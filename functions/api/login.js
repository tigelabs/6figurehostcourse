import { normalizeCode, getCode, putCode, makeSession, sessionCookie, json, MAX_DEVICES_DEFAULT } from '../../src/lib.js';
import { SEED_HASHES } from '../../src/seed.js';

async function sha256(t) {
  const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(t));
  return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('');
}

export async function onRequestPost({ request, env }) {
  let body = {};
  try { body = await request.json(); } catch {}
  const code = normalizeCode(body.code);
  const device = String(body.device || '').slice(0, 80);
  if (!code) return json({ error: 'That doesn’t look like a valid code. It looks like HOST-7K4M-Q2XP.' }, 400);
  if (!device) return json({ error: 'Your browser blocked the login. Please enable cookies and try again.' }, 400);

  let rec = await getCode(env, code);
  if (!rec && SEED_HASHES.has(await sha256(code))) {
    rec = { code, email: '', name: '', orderId: '', active: true, devices: [], createdAt: new Date().toISOString(), source: 'review' };
    await putCode(env, rec);
  }
  if (!rec) return json({ error: 'We couldn’t find this code. Please check it against your welcome email.' }, 401);
  if (!rec.active) return json({ error: 'This code is no longer active. If you think this is a mistake, email us at contact@6figurehost.com.' }, 403);

  const max = Number(env.MAX_DEVICES || MAX_DEVICES_DEFAULT);
  if (!rec.devices.includes(device)) {
    if (rec.devices.length >= max) {
      return json({ error: `This code is already in use on ${max} devices. Email us at contact@6figurehost.com and we’ll reset it for you.` }, 403);
    }
    rec.devices.push(device);
    rec.lastLogin = new Date().toISOString();
    await putCode(env, rec);
  }
  const token = await makeSession(env, code, device);
  return json({ ok: true }, 200, { 'Set-Cookie': sessionCookie(token) });
}

export async function onRequestGet({ request }) {
  return Response.redirect(new URL('/login', request.url).toString(), 302);
}
