// Starts a Stripe Checkout (embedded on our own /checkout page).
// POST {item: "course" | "barcelona" | "bali"}  -> {clientSecret, publishableKey}
import { stripe, priceFor, json, SKUS } from '../../../src/lib.js';

export async function onRequestPost({ request, env }) {
  let b = {}; try { b = await request.json(); } catch {}
  const sku = SKUS.includes(b.item) ? b.item : 'course';
  const price = priceFor(env, sku);
  if (!env.STRIPE_SECRET_KEY || !price) return json({ error: 'Checkout is not set up yet.' }, 503);
  const origin = new URL(request.url).origin;
  try {
    const s = await stripe(env, 'POST', '/checkout/sessions', {
      ui_mode: 'embedded',
      mode: 'payment',
      line_items: { 0: { price, quantity: 1 } },
      customer_creation: 'always',
      payment_intent_data: { setup_future_usage: 'off_session', metadata: { skus: sku } },
      metadata: { skus: sku },
      allow_promotion_codes: 'true',
      return_url: `${origin}/checkout/thanks?session_id={CHECKOUT_SESSION_ID}`,
    });
    return json({ clientSecret: s.client_secret, publishableKey: env.STRIPE_PUBLISHABLE_KEY || '' });
  } catch (e) {
    return json({ error: e.message }, 502);
  }
}
