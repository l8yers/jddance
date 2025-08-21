// /api/contact.js
import { Resend } from "resend";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { name, email, message } = req.body || {};
  if (!name || !email || !message) {
    return res.status(400).json({ error: "Missing fields" });
  }

  const resend = new Resend(process.env.RESEND_API_KEY);

  try {
    await resend.emails.send({
      from: process.env.EMAIL_FROM,    // verified sender (your Gmail)
      to: process.env.EMAIL_TO,        // where submissions should go (same Gmail is fine)
      reply_to: email,                 // so replies go back to the site visitor
      subject: `New contact form from ${name}`,
      text: `Name: ${name}\nEmail: ${email}\n\n${message}`,
    });

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: "Failed to send" });
  }
}
