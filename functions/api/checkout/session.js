// Starts a Stripe Checkout (embedded on our own /checkout page).
// POST {item: "course" | "barcelona" | "bali" | "calculator", extras: [...]} -> {clientSecret, publishableKey}
// Buyers see USD plus their local currency (Stripe Adaptive Pricing).
// "extras" are the city guides ticked as add-ons on the checkout page.
import { stripe, priceFor, json, SKUS } from '../../../src/lib.js';

export async function onRequestPost({ request, env }) {
  let b = {}; try { b = await request.json(); } catch {}
  const main = SKUS.includes(b.item) ? b.item : 'course';
  const skus = [main];
  // Add-ons: the city guides with any order; the calculator only with a guide (it is already in the course).
  const allowed = main === 'course' ? ['barcelona', 'bali'] : ['barcelona', 'bali', 'calculator'];
  for (const x of Array.isArray(b.extras) ? b.extras : []) if (allowed.includes(x) && !skus.includes(x)) skus.push(x);
  const prices = skus.map(s => priceFor(env, s));
  if (!env.STRIPE_SECRET_KEY || prices.some(p => !p)) return json({ error: 'Checkout is not set up yet.' }, 503);
  const origin = new URL(request.url).origin;
  const line_items = {};
  prices.forEach((price, i) => { line_items[i] = { price, quantity: 1 }; });
  // Adaptive Pricing on: buyers see USD and their local currency (EUR buyers get the fixed EUR prices set on each price).
  const base = {
      adaptive_pricing: { enabled: 'true' },
      mode: 'payment',
      line_items,
      customer_creation: 'always',
      payment_intent_data: { metadata: { skus: skus.join(',') } },
      metadata: { skus: skus.join(',') },
      allow_promotion_codes: 'true',
      return_url: `${origin}/checkout/thanks?session_id={CHECKOUT_SESSION_ID}`,
  };
  // Brand colours inside the Stripe form (needs API version 2025-09-30.clover or later).
  const branding = { background_color: '#FFFFFF', button_color: '#A05F50', border_style: 'rounded', display_name: '6-Figure Host' };
  // Link is hidden so the pay button uses our colour (Link always shows its own green button).
  const noLink = { link: { display: 'never' } };
  const attempts = [
    ['2025-09-30.clover', { ui_mode: 'embedded', branding_settings: branding, wallet_options: noLink, ...base }],
    ['2025-09-30.clover', { ui_mode: 'embedded', branding_settings: branding, ...base }],
    ['2025-09-30.clover', { ui_mode: 'embedded_page', branding_settings: branding, ...base }],
    [undefined, { ui_mode: 'embedded', ...base }],
  ];
  let last;
  for (const [version, params] of attempts) {
    try {
      const s = await stripe(env, 'POST', '/checkout/sessions', params, undefined, version);
      return json({ clientSecret: s.client_secret, publishableKey: env.STRIPE_PUBLISHABLE_KEY || '' });
    } catch (e) { last = e; if (e.status && e.status !== 400) break; }
  }
  return json({ error: last ? last.message : 'Checkout failed' }, 502);
}
