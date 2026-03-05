const knowledgeBase = {
  company: {
    name: process.env.COMPANY_NAME || 'Our Company',
    phone: process.env.COMPANY_PHONE || '+1-555-000-0000',
    email: process.env.COMPANY_EMAIL || 'info@example.com',
    address: process.env.COMPANY_ADDRESS || '123 Main Street, Suite 100',
  },

  services: [
    {
      id: 'initial-consultation',
      name: 'Initial Consultation',
      duration: 30,
      price: 'Free',
      description: 'A complimentary 30-minute session to discuss your needs and how we can help.',
    },
    {
      id: 'standard-appointment',
      name: 'Standard Appointment',
      duration: 60,
      price: '$75',
      description: 'A full 60-minute session for ongoing clients.',
    },
    {
      id: 'extended-session',
      name: 'Extended Session',
      duration: 90,
      price: '$110',
      description: 'A 90-minute deep-dive session for complex matters.',
    },
    {
      id: 'follow-up',
      name: 'Follow-Up',
      duration: 30,
      price: '$40',
      description: 'A 30-minute follow-up to review progress.',
    },
  ],

  workingHours: {
    timezone: 'America/New_York',
    days: {
      monday: { open: '09:00', close: '17:00' },
      tuesday: { open: '09:00', close: '17:00' },
      wednesday: { open: '09:00', close: '17:00' },
      thursday: { open: '09:00', close: '17:00' },
      friday: { open: '09:00', close: '16:00' },
      saturday: { open: '10:00', close: '14:00' },
      sunday: null,
    },
    slotDurationMinutes: 30,
  },

  bookingPolicies: [
    'Appointments must be booked at least 24 hours in advance.',
    'Cancellations require at least 12 hours notice to avoid a cancellation fee.',
    'Late arrivals exceeding 15 minutes may result in a shortened session.',
    'Rescheduling is free if done at least 12 hours before the appointment.',
  ],

  faqs: [
    {
      question: 'How do I book an appointment?',
      answer: 'Simply tell me your preferred date and time, and I will check availability for you.',
    },
    {
      question: 'Can I reschedule?',
      answer: 'Yes, you can reschedule for free as long as you notify us at least 12 hours before your appointment.',
    },
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept credit/debit cards, bank transfers, and cash payments at the office.',
    },
    {
      question: 'Is the initial consultation really free?',
      answer: 'Yes, your first 30-minute consultation is completely free with no obligation.',
    },
  ],
};

function getKnowledgeBasePrompt() {
  const servicesText = knowledgeBase.services
    .map((s) => `- ${s.name} (${s.duration} min, ${s.price}): ${s.description}`)
    .join('\n');

  const hoursText = Object.entries(knowledgeBase.workingHours.days)
    .map(([day, hours]) => {
      if (!hours) return `- ${day}: Closed`;
      return `- ${day}: ${hours.open} - ${hours.close}`;
    })
    .join('\n');

  const policiesText = knowledgeBase.bookingPolicies.map((p) => `- ${p}`).join('\n');

  const faqsText = knowledgeBase.faqs.map((f) => `Q: ${f.question}\nA: ${f.answer}`).join('\n\n');

  return `
## Company Information
Name: ${knowledgeBase.company.name}
Phone: ${knowledgeBase.company.phone}
Email: ${knowledgeBase.company.email}
Address: ${knowledgeBase.company.address}

## Services Offered
${servicesText}

## Working Hours (${knowledgeBase.workingHours.timezone})
${hoursText}
Appointment slots are ${knowledgeBase.workingHours.slotDurationMinutes} minutes each.

## Booking Policies
${policiesText}

## Frequently Asked Questions
${faqsText}
`.trim();
}

module.exports = { knowledgeBase, getKnowledgeBasePrompt };
