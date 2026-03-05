const Anthropic = require('@anthropic-ai/sdk');
const config = require('../config');
const { getKnowledgeBasePrompt } = require('../config/knowledge-base');
const sheets = require('./sheets');
const scheduler = require('./scheduler');

const client = new Anthropic({ apiKey: config.anthropic.apiKey });

const TOOL_DEFINITIONS = [
  {
    name: 'check_availability',
    description: 'Check available appointment slots for a specific date.',
    input_schema: {
      type: 'object',
      properties: {
        date: {
          type: 'string',
          description: 'Date in YYYY-MM-DD format',
        },
      },
      required: ['date'],
    },
  },
  {
    name: 'book_appointment',
    description: 'Book an appointment for the lead.',
    input_schema: {
      type: 'object',
      properties: {
        date: {
          type: 'string',
          description: 'Appointment date in YYYY-MM-DD format',
        },
        time: {
          type: 'string',
          description: 'Appointment time in HH:MM format (24-hour)',
        },
        service: {
          type: 'string',
          description: 'Service type ID (e.g., initial-consultation, standard-appointment)',
        },
      },
      required: ['date', 'time', 'service'],
    },
  },
  {
    name: 'update_lead_name',
    description: "Update the lead's name when they provide it.",
    input_schema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: "The lead's name" },
      },
      required: ['name'],
    },
  },
  {
    name: 'update_lead_email',
    description: "Update the lead's email for confirmation emails.",
    input_schema: {
      type: 'object',
      properties: {
        email: { type: 'string', description: "The lead's email address" },
      },
      required: ['email'],
    },
  },
];

function buildSystemPrompt(lead, pastBookings) {
  const isReturning = lead.status !== 'New Lead';
  const leadContext = isReturning
    ? `This is a RETURNING lead. Name: ${lead.name || 'Unknown'}. Email: ${lead.email || 'Not provided'}. Status: ${lead.status}. They first contacted us on ${lead.createdAt}.`
    : 'This is a NEW lead contacting us for the first time. Warmly welcome them and try to learn their name.';

  const bookingsContext =
    pastBookings.length > 0
      ? `Past bookings:\n${pastBookings.map((b) => `- ${b.service} on ${b.date} at ${b.time} (${b.status})`).join('\n')}`
      : 'No past bookings.';

  return `You are a friendly, professional appointment booking assistant for ${config.gmail.companyName}. You communicate via WhatsApp.

## Your Role
- Answer questions about our services, hours, and policies
- Guide users toward booking an appointment
- Collect necessary information (name, preferred date/time, service type)
- Be conversational, warm, and helpful — but concise (WhatsApp messages should be short)
- Use the tools provided to check availability and book appointments
- When a user wants to book, ask for their preferred date and time, then use check_availability
- Only book after confirming the slot with the user
- If the user provides their name or email, use the update tools to save them
- For returning leads, acknowledge them by name and reference past interactions

## Lead Context
${leadContext}

## Booking History
${bookingsContext}

## Knowledge Base
${getKnowledgeBasePrompt()}

## Important Rules
- Always confirm details before booking
- Appointments must be at least 24 hours in advance
- Keep messages concise — this is WhatsApp, not email
- Use simple formatting: *bold* for emphasis, line breaks for readability
- Never fabricate availability — always use the check_availability tool
- If you don't know something, say so honestly`;
}

async function handleToolCall(toolName, toolInput, lead) {
  switch (toolName) {
    case 'check_availability': {
      const { date } = toolInput;
      if (!scheduler.isDateInFuture(date)) {
        return { error: 'That date is in the past. Please choose a future date.' };
      }
      const hours = scheduler.getWorkingHoursForDate(date);
      if (!hours) {
        return { error: 'We are closed on that day. Please choose another date.' };
      }
      const slots = await scheduler.getAvailableSlots(date);
      if (slots.length === 0) {
        return { available_slots: [], message: 'No available slots on that date.' };
      }
      return { available_slots: slots, date };
    }

    case 'book_appointment': {
      const { date, time, service } = toolInput;
      if (!scheduler.isAtLeast24HoursAhead(date, time)) {
        return { error: 'Appointments must be booked at least 24 hours in advance.' };
      }
      const available = await scheduler.isSlotAvailable(date, time);
      if (!available) {
        return { error: `The slot at ${time} on ${date} is no longer available.` };
      }
      const booking = await sheets.createBooking(lead.phone, service, date, time);
      if (lead.rowIndex) {
        await sheets.updateLeadStatus(lead, 'Booked');
      }
      return {
        success: true,
        booking,
        message: `Appointment booked for ${date} at ${time}.`,
      };
    }

    case 'update_lead_name': {
      if (lead.rowIndex) {
        await sheets.updateLeadName(lead, toolInput.name);
      }
      return { success: true, name: toolInput.name };
    }

    case 'update_lead_email': {
      if (lead.rowIndex) {
        await sheets.updateLeadEmail(lead, toolInput.email);
      }
      return { success: true, email: toolInput.email };
    }

    default:
      return { error: `Unknown tool: ${toolName}` };
  }
}

async function generateResponse(lead, userMessage) {
  const pastBookings = await sheets.getLeadBookings(lead.phone);
  const messageHistory = await sheets.getMessageHistory(lead.phone);
  const systemPrompt = buildSystemPrompt(lead, pastBookings);

  const messages = [
    ...messageHistory,
    { role: 'user', content: userMessage },
  ];

  let response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 500,
    system: systemPrompt,
    tools: TOOL_DEFINITIONS,
    messages,
  });

  // Process tool use in a loop until we get a final text response
  while (response.stop_reason === 'tool_use') {
    const toolUseBlocks = response.content.filter((b) => b.type === 'tool_use');
    const toolResults = [];

    for (const toolUse of toolUseBlocks) {
      const result = await handleToolCall(toolUse.name, toolUse.input, lead);
      toolResults.push({
        type: 'tool_result',
        tool_use_id: toolUse.id,
        content: JSON.stringify(result),
      });
    }

    messages.push({ role: 'assistant', content: response.content });
    messages.push({ role: 'user', content: toolResults });

    response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 500,
      system: systemPrompt,
      tools: TOOL_DEFINITIONS,
      messages,
    });
  }

  const textBlocks = response.content.filter((b) => b.type === 'text');
  const assistantMessage = textBlocks.map((b) => b.text).join('\n');

  // Check if a booking was made during this conversation turn
  let newBooking = null;
  for (const msg of messages) {
    if (msg.role === 'user' && Array.isArray(msg.content)) {
      for (const block of msg.content) {
        if (block.type === 'tool_result') {
          try {
            const result = JSON.parse(block.content);
            if (result.success && result.booking) {
              newBooking = result.booking;
            }
          } catch {
            // ignore parse errors
          }
        }
      }
    }
  }

  return { message: assistantMessage, booking: newBooking };
}

module.exports = { generateResponse };
