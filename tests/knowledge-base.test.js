const { describe, it } = require('node:test');
const assert = require('node:assert');
const { knowledgeBase, getKnowledgeBasePrompt } = require('../src/config/knowledge-base');

describe('knowledge-base', () => {
  it('has services defined', () => {
    assert.ok(knowledgeBase.services.length > 0);
    for (const service of knowledgeBase.services) {
      assert.ok(service.id);
      assert.ok(service.name);
      assert.ok(service.duration > 0);
    }
  });

  it('has working hours for weekdays', () => {
    const { days } = knowledgeBase.workingHours;
    assert.ok(days.monday);
    assert.ok(days.tuesday);
    assert.ok(days.friday);
    assert.strictEqual(days.sunday, null);
  });

  it('has FAQs', () => {
    assert.ok(knowledgeBase.faqs.length > 0);
    for (const faq of knowledgeBase.faqs) {
      assert.ok(faq.question);
      assert.ok(faq.answer);
    }
  });

  it('generates a knowledge base prompt string', () => {
    const prompt = getKnowledgeBasePrompt();
    assert.ok(prompt.includes('Services Offered'));
    assert.ok(prompt.includes('Working Hours'));
    assert.ok(prompt.includes('Booking Policies'));
    assert.ok(prompt.includes('Frequently Asked Questions'));
  });
});
