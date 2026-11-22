// One-click add-on after the purchase: charges the card the buyer just used.
// POST {session_id, item: "barcelona" | "bali"} -> {ok, products} or {fallback: "/checkout?item=..."}
import { stripe, grant, getCode, priceFor, productsOf, sendWelcome, json } from '../../../src/lib.js';

export async function onRequestPost({ request, env }) {
  let b = {}; try { b = await request.json(); } catch {}
  const sku = b.item;
  if (!['barcelona', 'bali'].includes(sku)) return json({ error: 'Unknown guide.' }, 400);
  const code = b.session_id ? await env.CODES.get(`cs:${b.session_id}`) : null;
  const rec = code ? await getCode(env, code) : null;
  if (!rec) return json({ error: 'Order not found.' }, 404);
  if (productsOf(rec).includes(sku)) return json({ ok: true, products: productsOf(rec) });
  // Offer is only for a fresh order (within 2 hours), so an old link can't be used to charge again.
  const s = await stripe(env, 'GET', `/checkout/sessions/${encodeURIComponent(b.session_id)}`);
  if (Date.now() / 1000 - s.created > 7200 || !rec.stripeCustomer || !rec.stripePaymentMethod) return json({ fallback: `/checkout?item=${sku}` });
  const price = await stripe(env, 'GET', `/prices/${priceFor(env, sku)}`);
  try {
    const pi = await stripe(env, 'POST', '/payment_intents', {
      amount: price.unit_amount, currency: price.currency,
      customer: rec.stripeCustomer, payment_method: rec.stripePaymentMethod,
      off_session: 'true', confirm: 'true',
      description: sku === 'bali' ? 'Bali Host Guide' : 'Barcelona Host Guide',
      metadata: { skus: sku, code: rec.code },
    }, `upsell-${b.session_id}-${sku}`);
    if (pi.status !== 'succeeded') return json({ fallback: `/checkout?item=${sku}` });
    const r = await grant(env, { email: rec.email, name: rec.name, skus: [sku], paymentId: pi.id });
    return json({ ok: true, products: productsOf(r.rec) });
  } catch (e) {
    return json({ fallback: `/checkout?item=${sku}`, error: e.message });
  }
}
