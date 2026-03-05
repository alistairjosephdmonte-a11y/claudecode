const { describe, it } = require('node:test');
const assert = require('node:assert');

// We test the pure logic functions from scheduler without needing Google Sheets
const {
  getWorkingHoursForDate,
  isDateInFuture,
  isAtLeast24HoursAhead,
} = require('../src/modules/scheduler');

describe('scheduler', () => {
  describe('getWorkingHoursForDate', () => {
    it('returns hours for a weekday', () => {
      // 2026-03-09 is a Monday
      const hours = getWorkingHoursForDate('2026-03-09');
      assert.deepStrictEqual(hours, { open: '09:00', close: '17:00' });
    });

    it('returns Saturday hours', () => {
      // 2026-03-07 is a Saturday
      const hours = getWorkingHoursForDate('2026-03-07');
      assert.deepStrictEqual(hours, { open: '10:00', close: '14:00' });
    });

    it('returns null for Sunday', () => {
      // 2026-03-08 is a Sunday
      const hours = getWorkingHoursForDate('2026-03-08');
      assert.strictEqual(hours, null);
    });
  });

  describe('isDateInFuture', () => {
    it('returns true for a far future date', () => {
      assert.strictEqual(isDateInFuture('2099-01-01'), true);
    });

    it('returns false for a past date', () => {
      assert.strictEqual(isDateInFuture('2020-01-01'), false);
    });
  });

  describe('isAtLeast24HoursAhead', () => {
    it('returns true for a date far in the future', () => {
      assert.strictEqual(isAtLeast24HoursAhead('2099-01-01', '10:00'), true);
    });

    it('returns false for a date in the past', () => {
      assert.strictEqual(isAtLeast24HoursAhead('2020-01-01', '10:00'), false);
    });
  });
});
