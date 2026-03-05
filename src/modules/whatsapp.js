const config = require('../config');

const API_BASE = `${config.whatsapp.apiUrl}/${config.whatsapp.phoneNumberId}`;

async function sendMessage(to, text) {
  const response = await fetch(`${API_BASE}/messages`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${config.whatsapp.apiToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messaging_product: 'whatsapp',
      to,
      type: 'text',
      text: { body: text },
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`WhatsApp API error (${response.status}): ${error}`);
  }

  return response.json();
}

function extractMessage(webhookBody) {
  try {
    const entry = webhookBody.entry?.[0];
    const change = entry?.changes?.[0];
    const value = change?.value;
    const message = value?.messages?.[0];

    if (!message) return null;

    return {
      from: message.from,
      text: message.text?.body || '',
      messageId: message.id,
      timestamp: message.timestamp,
      profileName: value.contacts?.[0]?.profile?.name || '',
    };
  } catch {
    return null;
  }
}

function isValidWebhook(body) {
  return (
    body?.object === 'whatsapp_business_account' &&
    body?.entry?.[0]?.changes?.[0]?.value?.messages?.length > 0
  );
}

module.exports = { sendMessage, extractMessage, isValidWebhook };
