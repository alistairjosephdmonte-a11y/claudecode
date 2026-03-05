const { describe, it } = require('node:test');
const assert = require('node:assert');
const { extractMessage, isValidWebhook } = require('../src/modules/whatsapp');

describe('whatsapp', () => {
  const validWebhookBody = {
    object: 'whatsapp_business_account',
    entry: [
      {
        changes: [
          {
            value: {
              messages: [
                {
                  from: '15551234567',
                  text: { body: 'Hello, I want to book an appointment' },
                  id: 'msg_123',
                  timestamp: '1709640000',
                },
              ],
              contacts: [
                {
                  profile: { name: 'John Doe' },
                },
              ],
            },
          },
        ],
      },
    ],
  };

  describe('isValidWebhook', () => {
    it('returns true for a valid webhook payload', () => {
      assert.strictEqual(isValidWebhook(validWebhookBody), true);
    });

    it('returns false for an empty object', () => {
      assert.strictEqual(isValidWebhook({}), false);
    });

    it('returns false for null', () => {
      assert.strictEqual(isValidWebhook(null), false);
    });

    it('returns false when messages array is empty', () => {
      const body = {
        object: 'whatsapp_business_account',
        entry: [{ changes: [{ value: { messages: [] } }] }],
      };
      assert.strictEqual(isValidWebhook(body), false);
    });
  });

  describe('extractMessage', () => {
    it('extracts message fields from a valid webhook', () => {
      const result = extractMessage(validWebhookBody);
      assert.strictEqual(result.from, '15551234567');
      assert.strictEqual(result.text, 'Hello, I want to book an appointment');
      assert.strictEqual(result.messageId, 'msg_123');
      assert.strictEqual(result.profileName, 'John Doe');
    });

    it('returns null for an invalid payload', () => {
      assert.strictEqual(extractMessage({}), null);
    });

    it('returns null for null input', () => {
      assert.strictEqual(extractMessage(null), null);
    });
  });
});
