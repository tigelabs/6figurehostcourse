// Starts a Stripe Checkout (embedded on our own /checkout page).
// POST {item: "course" | "barcelona" | "bali", extras: ["barcelona", "bali"]} -> {clientSecret, publishableKey}
// "extras" are the city guides ticked as add-ons on the checkout page.
import { stripe, priceFor, json, SKUS } from '../../../src/lib.js';

export async function onRequestPost({ request, env }) {
  let b = {}; try { b = await request.json(); } catch {}
  const main = SKUS.includes(b.item) ? b.item : 'course';
  const skus = [main];
  for (const x of Array.isArray(b.extras) ? b.extras : []) if (['barcelona', 'bali'].includes(x) && !skus.includes(x)) skus.push(x);
  const prices = skus.map(s => priceFor(env, s));
  if (!env.STRIPE_SECRET_KEY || prices.some(p => !p)) return json({ error: 'Checkout is not set up yet.' }, 503);
  const origin = new URL(request.url).origin;
  const line_items = {};
  prices.forEach((price, i) => { line_items[i] = { price, quantity: 1 }; });
  try {
    const s = await stripe(env, 'POST', '/checkout/sessions', {
      ui_mode: 'embedded',
      mode: 'payment',
      line_items,
      customer_creation: 'always',
      payment_intent_data: { metadata: { skus: skus.join(',') } },
      metadata: { skus: skus.join(',') },
      allow_promotion_codes: 'true',
      return_url: `${origin}/checkout/thanks?session_id={CHECKOUT_SESSION_ID}`,
    });
    return json({ clientSecret: s.client_secret, publishableKey: env.STRIPE_PUBLISHABLE_KEY || '' });
  } catch (e) {
    return json({ error: e.message }, 502);
  }
}
