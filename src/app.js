const express = require('express');
const config = require('./config');
const webhookRouter = require('./routes/webhook');

const app = express();

app.use(express.json());

// Health check
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// WhatsApp webhook
app.use('/webhook', webhookRouter);

app.listen(config.port, () => {
  console.log(`WhatsApp Booking Assistant running on port ${config.port}`);
  console.log(`Webhook URL: http://localhost:${config.port}/webhook`);
});

module.exports = app;
