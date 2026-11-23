import { getCode, sendWelcome, json } from '../../src/lib.js';

// "Send my code again": emails a buyer their existing access code.
// Always answers the same way, so nobody can find out which emails bought the course.
export async function onRequestPost({ request, env }) {
  let b = {};
  try { b = await request.json(); } catch {}
  const email = String(b.email || '').trim().toLowerCase().slice(0, 200);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ error: 'Please check your email address.' }, 400);
  const done = json({ ok: true });

  const ip = request.headers.get('CF-Connecting-IP') || 'x';
  const hour = new Date().toISOString().slice(0, 13);
  try {
    const ipKey = `resend-ip:${ip}:${hour}`, mailKey = `resend-mail:${email}:${hour}`;
    const [n, m] = await Promise.all([env.CODES.get(ipKey), env.CODES.get(mailKey)]);
    if (Number(n || 0) >= 5) return json({ error: 'Too many requests. Please try again in an hour.' }, 429);
    await env.CODES.put(ipKey, String(Number(n || 0) + 1), { expirationTtl: 3600 });
    if (Number(m || 0) >= 2) return done; // this email already got it twice this hour
    await env.CODES.put(mailKey, String(Number(m || 0) + 1), { expirationTtl: 3600 });
  } catch {}

  const code = await env.CODES.get(`email:${email}`);
  if (!code) return done;
  const rec = await getCode(env, code);
  if (!rec || rec.active === false) return done;
  try { await sendWelcome(env, { ...rec, email: rec.email || email }); } catch {}
  return done;
}
