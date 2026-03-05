const nodemailer = require('nodemailer');
const config = require('../config');

function createTransporter() {
  return nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: config.gmail.user,
      pass: config.gmail.appPassword,
    },
  });
}

async function sendBookingConfirmation(recipientEmail, booking, leadName) {
  if (!recipientEmail) {
    console.log('No email address provided for lead — skipping email confirmation.');
    return null;
  }

  const transporter = createTransporter();
  const companyName = config.gmail.companyName;

  const mailOptions = {
    from: `"${companyName}" <${config.gmail.user}>`,
    to: recipientEmail,
    subject: `Appointment Confirmation — ${booking.date} at ${booking.time}`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Appointment Confirmed</h2>
        <p>Hi ${leadName || 'there'},</p>
        <p>Your appointment has been confirmed. Here are the details:</p>

        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;" role="presentation">
          <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Date</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">${booking.date}</td>
          </tr>
          <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Time</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">${booking.time}</td>
          </tr>
          <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Service</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">${booking.service}</td>
          </tr>
          <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Status</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">${booking.status}</td>
          </tr>
        </table>

        <h3 style="color: #2c3e50;">Important Reminders</h3>
        <ul>
          <li>Please arrive 5 minutes before your appointment</li>
          <li>Cancellations require at least 12 hours notice</li>
          <li>Rescheduling is free with 12 hours notice</li>
        </ul>

        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />

        <p style="color: #666; font-size: 14px;">
          <strong>${companyName}</strong><br />
          Email: ${config.gmail.companyEmail}<br />
          This is an automated confirmation. Please reply if you have any questions.
        </p>
      </div>
    `,
    text: `Appointment Confirmed

Hi ${leadName || 'there'},

Your appointment has been confirmed:
- Date: ${booking.date}
- Time: ${booking.time}
- Service: ${booking.service}
- Status: ${booking.status}

Reminders:
- Please arrive 5 minutes early
- Cancellations require 12 hours notice
- Rescheduling is free with 12 hours notice

${companyName}
Email: ${config.gmail.companyEmail}`,
  };

  const result = await transporter.sendMail(mailOptions);
  console.log(`Confirmation email sent to ${recipientEmail}: ${result.messageId}`);
  return result;
}

module.exports = { sendBookingConfirmation };
