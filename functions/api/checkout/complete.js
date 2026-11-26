// Called by the thank-you page. Checks the payment with Stripe, gives the buyer their code,
// logs this device in, and says which guides can still be offered.
// POST {session_id, device} -> {code, name, products, offers:[...]}
import { makeSession, sessionCookie, putCode, productsOf, json, MAX_DEVICES_DEFAULT, noteLogin } from '../../../src/lib.js';
import { fulfillSession } from '../../../src/fulfill.js';

export async function onRequestPost({ request, env }) {
  let b = {}; try { b = await request.json(); } catch {}
  if (!b.session_id || !/^cs_/.test(b.session_id)) return json({ error: 'Missing order.' }, 400);
  let out;
  try { out = await fulfillSession(env, b.session_id); } catch (e) { return json({ error: e.message }, 502); }
  if (out.pending) return json({ pending: true });
  const { rec, session } = out;
  // Only log in from a fresh order link (within 24 hours of the purchase).
  const fresh = Date.now() / 1000 - session.created < 86400;
  const headers = {};
  const device = String(b.device || '').slice(0, 80);
  if (fresh && device) {
    const max = Number(env.MAX_DEVICES || MAX_DEVICES_DEFAULT);
    if (!rec.devices.includes(device) && rec.devices.length < max) rec.devices.push(device);
    if (rec.devices.includes(device)) {
      if (!rec.lastLogin || Date.now() - Date.parse(rec.lastLogin) > 60e3) { noteLogin(rec, request, device, 'purchase'); await putCode(env, rec); }
      headers['Set-Cookie'] = sessionCookie(await makeSession(env, rec.code, device));
    }
  }
  const owned = productsOf(rec);
  // An old thank-you link no longer shows the code (it is in the welcome email).
  const recent = Date.now() / 1000 - session.created < 7 * 86400;
  return json({ code: recent ? rec.code : null, name: rec.name, email: recent ? rec.email : '', products: owned,
    offers: ['barcelona', 'bali'].filter(s => !owned.includes(s)), canOneClick: !!rec.stripePaymentMethod }, 200, headers);
}
