// Stripe webhook. We never trust the request body: we read the event back from Stripe by its id.
//  checkout.session.completed -> give the buyer access (in case they closed the page before the thank-you page)
//  charge.refunded (full)     -> take away what that payment unlocked
import { stripe, getCode, putCode, json } from '../../../src/lib.js';
import { fulfillSession } from '../../../src/fulfill.js';

export async function onRequestPost({ request, env }) {
  let body = {}; try { body = await request.json(); } catch {}
  if (!body.id || !/^evt_/.test(body.id)) return json({ error: 'bad event' }, 400);
  const ev = await stripe(env, 'GET', `/events/${body.id}`);
  const obj = ev.data.object;

  if (ev.type === 'checkout.session.completed' || ev.type === 'checkout.session.async_payment_succeeded') {
    const r = await fulfillSession(env, obj.id);
    return json({ ok: true, code: r.rec?.code || null });
  }

  if (ev.type === 'charge.refunded' && obj.refunded && obj.payment_intent) {
    const code = await env.CODES.get(`pay:${obj.payment_intent}`);
    const rec = code ? await getCode(env, code) : null;
    if (rec) {
      const pay = (rec.payments || []).find(p => p.id === obj.payment_intent);
      const lost = pay ? pay.skus : [];
      rec.products = (rec.products || []).filter(s => !lost.includes(s));
      if (!rec.products.length) rec.active = false;
      rec.refunds = [...(rec.refunds || []), { id: obj.payment_intent, skus: lost, at: new Date().toISOString() }];
      await putCode(env, rec);
    }
    return json({ ok: true, refunded: code || null });
  }
  return json({ ignored: ev.type });
}
