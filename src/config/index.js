const config = {
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',

  whatsapp: {
    apiToken: process.env.WHATSAPP_API_TOKEN,
    phoneNumberId: process.env.WHATSAPP_PHONE_NUMBER_ID,
    verifyToken: process.env.WHATSAPP_VERIFY_TOKEN,
    apiUrl: 'https://graph.facebook.com/v21.0',
  },

  anthropic: {
    apiKey: process.env.ANTHROPIC_API_KEY,
  },

  google: {
    serviceAccountEmail: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
    privateKey: (process.env.GOOGLE_PRIVATE_KEY || '').replace(/\\n/g, '\n'),
    spreadsheetId: process.env.GOOGLE_SPREADSHEET_ID,
  },

  gmail: {
    user: process.env.GMAIL_USER,
    appPassword: process.env.GMAIL_APP_PASSWORD,
    companyEmail: process.env.COMPANY_EMAIL,
    companyName: process.env.COMPANY_NAME || 'Our Company',
  },
};

module.exports = config;
