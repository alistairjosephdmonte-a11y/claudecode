const { knowledgeBase } = require('../config/knowledge-base');

// Lazy-load sheets to allow pure functions to be tested without googleapis
let _sheets = null;
function getSheets() {
  if (!_sheets) _sheets = require('./sheets');
  return _sheets;
}

const DAY_NAMES = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];

function generateTimeSlots(openTime, closeTime, durationMinutes) {
  const slots = [];
  const [openH, openM] = openTime.split(':').map(Number);
  const [closeH, closeM] = closeTime.split(':').map(Number);
  const openTotal = openH * 60 + openM;
  const closeTotal = closeH * 60 + closeM;

  for (let t = openTotal; t + durationMinutes <= closeTotal; t += durationMinutes) {
    const h = Math.floor(t / 60);
    const m = t % 60;
    slots.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`);
  }
  return slots;
}

function getWorkingHoursForDate(dateStr) {
  const date = new Date(dateStr + 'T12:00:00');
  const dayName = DAY_NAMES[date.getDay()];
  return knowledgeBase.workingHours.days[dayName] || null;
}

async function getAvailableSlots(dateStr) {
  const hours = getWorkingHoursForDate(dateStr);
  if (!hours) return [];

  const allSlots = generateTimeSlots(
    hours.open,
    hours.close,
    knowledgeBase.workingHours.slotDurationMinutes
  );

  const existingBookings = await getSheets().getBookingsForDate(dateStr);
  const bookedTimes = new Set(existingBookings.map((b) => b.time));

  return allSlots.filter((slot) => !bookedTimes.has(slot));
}

async function isSlotAvailable(dateStr, timeStr) {
  const available = await getAvailableSlots(dateStr);
  return available.includes(timeStr);
}

function isDateInFuture(dateStr) {
  const now = new Date();
  const target = new Date(dateStr + 'T23:59:59');
  return target > now;
}

function isAtLeast24HoursAhead(dateStr, timeStr) {
  const now = new Date();
  const target = new Date(`${dateStr}T${timeStr}:00`);
  const diffMs = target.getTime() - now.getTime();
  return diffMs >= 24 * 60 * 60 * 1000;
}

module.exports = {
  getAvailableSlots,
  isSlotAvailable,
  isDateInFuture,
  isAtLeast24HoursAhead,
  getWorkingHoursForDate,
};
