import { brevo, json } from '../../src/lib.js';

// Contact form: sends the visitor's message to the inbox in CONTACT_TO (default sixfigurehost@gmail.com).
const TO = 'sixfigurehost@gmail.com';
const TOPICS = ['The online course', 'Add-ons (guides or calculator)', 'My access or a payment', 'Partnership or press', 'Something else'];
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export async function onRequestPost({ request, env }) {
  let b = {};
  try { b = await request.json(); } catch {}
  if (b.website) return json({ ok: true }); // honeypot: bots fill the hidden field
  if (Number(b.t || 0) && Date.now() - Number(b.t) < 2500) return json({ ok: true }); // sent faster than a person can type
  const name = String(b.name || '').trim().slice(0, 100);
  const email = String(b.email || '').trim().slice(0, 200);
  const topic = TOPICS.includes(b.topic) ? b.topic : 'Something else';
  const message = String(b.message || '').trim().slice(0, 5000);
  if (!name) return json({ error: 'Please add your name.' }, 400);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ error: 'Please check your email address. We need it to reply.' }, 400);
  if (message.length < 5) return json({ error: 'Please write your message.' }, 400);
  if (!env.BREVO_API_KEY) return json({ error: 'The form is not working right now. Please email contact@6figurehost.com.' }, 503);

  // Light per-IP limit: 5 messages an hour.
  const ip = request.headers.get('CF-Connecting-IP') || 'x';
  const key = `contact:${ip}:${new Date().toISOString().slice(0, 13)}`;
  try {
    const n = Number((await env.CODES.get(key)) || 0);
    if (n >= 5) return json({ error: 'You’ve sent several messages already. Please try again in an hour.' }, 429);
    await env.CODES.put(key, String(n + 1), { expirationTtl: 3600 });
  } catch {}

  const r = await brevo(env, '/smtp/email', {
    sender: { name: '6-Figure Host website', email: 'contact@6figurehost.com' },
    to: [{ email: env.CONTACT_TO || TO, name: 'Daniel & Farah' }],
    replyTo: { email, name },
    subject: `Website message: ${topic} (from ${name})`,
    htmlContent: `<p><b>Name:</b> ${esc(name)}<br><b>Email:</b> ${esc(email)}<br><b>Topic:</b> ${esc(topic)}</p><p style="white-space:pre-wrap">${esc(message)}</p><p style="color:#888">Reply to this email to answer ${esc(name)} directly.</p>`,
    textContent: `Name: ${name}\nEmail: ${email}\nTopic: ${topic}\n\n${message}`,
  });
  if (!r.ok) return json({ error: 'Your message didn’t go through. Please try again, or email contact@6figurehost.com.' }, 502);
  return json({ ok: true });
}
