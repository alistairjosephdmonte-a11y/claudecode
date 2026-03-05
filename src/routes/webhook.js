const express = require('express');
const config = require('../config');
const whatsapp = require('../modules/whatsapp');
const sheets = require('../modules/sheets');
const conversation = require('../modules/conversation');
const email = require('../modules/email');

const router = express.Router();

// Webhook verification (GET) — required by WhatsApp Business API
router.get('/', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === config.whatsapp.verifyToken) {
    console.log('Webhook verified.');
    return res.status(200).send(challenge);
  }
  return res.sendStatus(403);
});

// Incoming message handler (POST)
router.post('/', async (req, res) => {
  // Respond immediately to avoid WhatsApp retry
  res.sendStatus(200);

  if (!whatsapp.isValidWebhook(req.body)) return;

  const incoming = whatsapp.extractMessage(req.body);
  if (!incoming || !incoming.text) return;

  const phone = incoming.from;
  const userMessage = incoming.text;

  try {
    // Step 1: Lead Memory — find or create the lead
    let lead = await sheets.findLead(phone);
    const isNewLead = !lead;

    if (isNewLead) {
      lead = await sheets.createLead(phone, userMessage);
      console.log(`New lead created: ${phone}`);
    } else {
      await sheets.logMessage(phone, 'user', userMessage);
      console.log(`Returning lead: ${phone} (${lead.name || 'unnamed'})`);
    }

    // If WhatsApp profile name is available and lead has no name, save it
    if (incoming.profileName && !lead.name && lead.rowIndex) {
      await sheets.updateLeadName(lead, incoming.profileName);
      lead.name = incoming.profileName;
    }

    // Steps 2-4: Knowledge Base + AI Conversation + Scheduling
    const response = await conversation.generateResponse(lead, userMessage);

    // Log assistant response
    await sheets.logMessage(phone, 'assistant', response.message);

    // Step 5: Send WhatsApp confirmation
    await whatsapp.sendMessage(phone, response.message);

    // Step 6: If a booking was made, send email confirmation
    if (response.booking) {
      const updatedLead = await sheets.findLead(phone);
      if (updatedLead?.email) {
        await email.sendBookingConfirmation(
          updatedLead.email,
          response.booking,
          updatedLead.name
        );
      }
    }
  } catch (err) {
    console.error(`Error processing message from ${phone}:`, err);
    try {
      await whatsapp.sendMessage(
        phone,
        "I'm sorry, I'm having a temporary issue. Please try again in a moment."
      );
    } catch (sendErr) {
      console.error('Failed to send error message:', sendErr);
    }
  }
});

module.exports = router;
