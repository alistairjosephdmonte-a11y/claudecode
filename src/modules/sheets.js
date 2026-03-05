const { google } = require('googleapis');
const config = require('../config');

const LEADS_SHEET = 'Leads';
const BOOKINGS_SHEET = 'Bookings';
const MESSAGES_SHEET = 'Messages';

let sheetsClient = null;

function getAuth() {
  return new google.auth.JWT(
    config.google.serviceAccountEmail,
    null,
    config.google.privateKey,
    ['https://www.googleapis.com/auth/spreadsheets']
  );
}

function getSheets() {
  if (!sheetsClient) {
    sheetsClient = google.sheets({ version: 'v4', auth: getAuth() });
  }
  return sheetsClient;
}

async function getSheetData(range) {
  const sheets = getSheets();
  const response = await sheets.spreadsheets.values.get({
    spreadsheetId: config.google.spreadsheetId,
    range,
  });
  return response.data.values || [];
}

async function appendRow(sheetName, values) {
  const sheets = getSheets();
  await sheets.spreadsheets.values.append({
    spreadsheetId: config.google.spreadsheetId,
    range: `${sheetName}!A:Z`,
    valueInputOption: 'USER_ENTERED',
    requestBody: { values: [values] },
  });
}

async function updateCell(sheetName, row, col, value) {
  const sheets = getSheets();
  const colLetter = String.fromCharCode(65 + col);
  await sheets.spreadsheets.values.update({
    spreadsheetId: config.google.spreadsheetId,
    range: `${sheetName}!${colLetter}${row}`,
    valueInputOption: 'USER_ENTERED',
    requestBody: { values: [[value]] },
  });
}

// --- Lead Management ---
// Leads sheet columns: A=phone, B=name, C=email, D=status, E=createdAt, F=updatedAt

async function findLead(phone) {
  const rows = await getSheetData(`${LEADS_SHEET}!A:F`);
  if (rows.length <= 1) return null; // header only

  for (let i = 1; i < rows.length; i++) {
    if (rows[i][0] === phone) {
      return {
        rowIndex: i + 1, // 1-based sheet row
        phone: rows[i][0],
        name: rows[i][1] || '',
        email: rows[i][2] || '',
        status: rows[i][3] || 'New Lead',
        createdAt: rows[i][4] || '',
        updatedAt: rows[i][5] || '',
      };
    }
  }
  return null;
}

async function createLead(phone, initialMessage) {
  const now = new Date().toISOString();
  await appendRow(LEADS_SHEET, [phone, '', '', 'New Lead', now, now]);
  await logMessage(phone, 'user', initialMessage);
  return {
    phone,
    name: '',
    email: '',
    status: 'New Lead',
    createdAt: now,
    updatedAt: now,
  };
}

async function updateLeadName(lead, name) {
  await updateCell(LEADS_SHEET, lead.rowIndex, 1, name);
  await updateCell(LEADS_SHEET, lead.rowIndex, 5, new Date().toISOString());
}

async function updateLeadStatus(lead, status) {
  await updateCell(LEADS_SHEET, lead.rowIndex, 3, status);
  await updateCell(LEADS_SHEET, lead.rowIndex, 5, new Date().toISOString());
}

async function updateLeadEmail(lead, email) {
  await updateCell(LEADS_SHEET, lead.rowIndex, 2, email);
  await updateCell(LEADS_SHEET, lead.rowIndex, 5, new Date().toISOString());
}

// --- Message History ---
// Messages sheet columns: A=phone, B=role, C=content, D=timestamp

async function logMessage(phone, role, content) {
  const now = new Date().toISOString();
  await appendRow(MESSAGES_SHEET, [phone, role, content, now]);
}

async function getMessageHistory(phone, limit = 20) {
  const rows = await getSheetData(`${MESSAGES_SHEET}!A:D`);
  if (rows.length <= 1) return [];

  const messages = [];
  for (let i = 1; i < rows.length; i++) {
    if (rows[i][0] === phone) {
      messages.push({
        role: rows[i][1] === 'user' ? 'user' : 'assistant',
        content: rows[i][2] || '',
      });
    }
  }
  return messages.slice(-limit);
}

// --- Booking Management ---
// Bookings sheet columns: A=phone, B=service, C=date, D=time, E=status, F=createdAt

async function getBookingsForDate(date) {
  const rows = await getSheetData(`${BOOKINGS_SHEET}!A:F`);
  if (rows.length <= 1) return [];

  const bookings = [];
  for (let i = 1; i < rows.length; i++) {
    if (rows[i][2] === date && rows[i][4] !== 'Cancelled') {
      bookings.push({
        phone: rows[i][0],
        service: rows[i][1],
        date: rows[i][2],
        time: rows[i][3],
        status: rows[i][4],
      });
    }
  }
  return bookings;
}

async function createBooking(phone, service, date, time) {
  const now = new Date().toISOString();
  await appendRow(BOOKINGS_SHEET, [phone, service, date, time, 'Confirmed', now]);
  return { phone, service, date, time, status: 'Confirmed', createdAt: now };
}

async function getLeadBookings(phone) {
  const rows = await getSheetData(`${BOOKINGS_SHEET}!A:F`);
  if (rows.length <= 1) return [];

  const bookings = [];
  for (let i = 1; i < rows.length; i++) {
    if (rows[i][0] === phone) {
      bookings.push({
        service: rows[i][1],
        date: rows[i][2],
        time: rows[i][3],
        status: rows[i][4],
        createdAt: rows[i][5],
      });
    }
  }
  return bookings;
}

module.exports = {
  findLead,
  createLead,
  updateLeadName,
  updateLeadStatus,
  updateLeadEmail,
  logMessage,
  getMessageHistory,
  getBookingsForDate,
  createBooking,
  getLeadBookings,
};
