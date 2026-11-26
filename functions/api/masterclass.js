import { json } from '../../src/lib.js';

// Free masterclass signup: puts the person in the Brevo list that starts the masterclass emails.
// List ID comes from MC_LIST_ID (default 2, "signed up masterclass").
export async function onRequestPost({ request, env }) {
  let b = {};
  try { b = await request.json(); } catch {}
  if (b.website) return json({ ok: true }); // honeypot
  if (Number(b.t || 0) && Date.now() - Number(b.t) < 1500) return json({ ok: true });
  const email = String(b.email || '').trim().toLowerCase().slice(0, 200);
  const first = String(b.first || '').trim().slice(0, 80);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ error: 'Please check your email address.' }, 400);
  if (!first) return json({ error: 'Please add your first name.' }, 400);
  if (!env.BREVO_API_KEY) return json({ error: 'Signups are paused for a moment. Please try again later.' }, 503);

  const ip = request.headers.get('CF-Connecting-IP') || 'x';
  const key = `mc:${ip}:${new Date().toISOString().slice(0, 13)}`;
  try {
    const n = Number((await env.CODES.get(key)) || 0);
    if (n >= 8) return json({ error: 'Too many signups from this connection. Please try again in an hour.' }, 429);
    await env.CODES.put(key, String(n + 1), { expirationTtl: 3600 });
    // The same address can sign up at most twice a day, so nobody can flood someone else's inbox.
    const mk = `mc-mail:${email}:${new Date().toISOString().slice(0, 10)}`;
    const m = Number((await env.CODES.get(mk)) || 0);
    if (m >= 2) return json({ ok: true });
    await env.CODES.put(mk, String(m + 1), { expirationTtl: 86400 });
  } catch {}

  const list = Number(env.MC_LIST_ID || 2);
  const H = { 'api-key': env.BREVO_API_KEY, 'Content-Type': 'application/json', accept: 'application/json' };
  // Someone already on the list (for example moved over from Flodesk) is taken off first,
  // so being added again starts the emails.
  await fetch(`https://api.brevo.com/v3/contacts/lists/${list}/contacts/remove`, { method: 'POST', headers: H, body: JSON.stringify({ emails: [email] }) }).catch(() => {});
  const r = await fetch('https://api.brevo.com/v3/contacts', {
    method: 'POST', headers: H,
    body: JSON.stringify({ email, attributes: { FIRSTNAME: first }, listIds: [list], updateEnabled: true }),
  });
  if (!r.ok && r.status !== 204) return json({ error: 'That didn’t work. Please try again in a minute.' }, 502);
  // Email 1 (the access link) goes out right away as a transactional email, so it arrives even
  // while the automation is paused. The Brevo automation sends the two reminders after it.
  const tpl = Number(env.MC_TEMPLATE_ID || 7);
  await fetch('https://api.brevo.com/v3/smtp/email', {
    method: 'POST', headers: H,
    body: JSON.stringify({ templateId: tpl, to: [{ email, name: first }] }),
  }).catch(() => {});
  return json({ ok: true });
}
