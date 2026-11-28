// Starts a Stripe Checkout (embedded on our own /checkout page).
// POST {item: "course" | "barcelona" | "bali" | "calculator", extras: [...]} -> {clientSecret, publishableKey}
// Buyers see USD plus their local currency (Stripe Adaptive Pricing).
// "extras" are the city guides ticked as add-ons on the checkout page.
import { stripe, priceFor, json, SKUS } from '../../../src/lib.js';
import { coursePrice, SPLIT_MONTHS, phase } from '../../../src/offer.js';

export async function onRequestPost({ request, env }) {
  let b = {}; try { b = await request.json(); } catch {}
  const main = SKUS.includes(b.item) ? b.item : 'course';
  // The new course launches on Black Friday (27 November): no course sales before that.
  if (main === 'course' && phase() === 'pre') return json({ error: 'The new 6-Figure Host Course launches on Black Friday, 27 November.' }, 403);
  const split = main === 'course' && b.plan === 'split';
  const skus = [main];
  // Add-ons: the calculator only with a guide (it is already in the course). City guides are "coming soon".
  const allowed = main === 'course' ? [] : ['barcelona', 'bali', 'calculator'].filter(x => x !== main);
  if (!split) for (const x of Array.isArray(b.extras) ? b.extras : []) if (allowed.includes(x) && !skus.includes(x)) skus.push(x);
  const prices = skus.map(s => s === 'course' ? coursePrice(env, split ? 'split' : 'one', Date.now(), b.offer === 'mc') : priceFor(env, s));
  if (!env.STRIPE_SECRET_KEY || prices.some(p => !p)) return json({ error: 'Checkout is not set up yet.' }, 503);
  const origin = new URL(request.url).origin;
  const line_items = {};
  prices.forEach((price, i) => { line_items[i] = { price, quantity: 1 }; });
  const meta = { skus: skus.join(','), ...(split ? { split: String(SPLIT_MONTHS) } : {}), ...(b.offer === 'mc' ? { offer: 'masterclass' } : {}) };
  const common = {
      line_items,
      metadata: meta,
      allow_promotion_codes: 'true',
      return_url: `${origin}/checkout/thanks?session_id={CHECKOUT_SESSION_ID}`,
  };
  const base = split
    ? { mode: 'subscription', subscription_data: { metadata: meta, description: `6-Figure Host Course, payment plan (${SPLIT_MONTHS} monthly payments)` }, ...common }
    : { mode: 'payment', customer_creation: 'always', payment_intent_data: { metadata: meta }, ...common };
  // EUR chosen on the page: charge in euros (fixed EUR prices). Otherwise USD, with the buyer's local currency shown by Stripe.
  if (b.currency === 'eur') base.currency = 'eur';
  const local = b.currency === 'eur' ? { adaptive_pricing: { enabled: 'false' } } : { adaptive_pricing: { enabled: 'true' } };
  // Brand colours inside the Stripe form (needs API version 2025-09-30.clover or later).
  const branding = { background_color: '#FFFFFF', button_color: '#A05F50', border_style: 'rounded', display_name: '6-Figure Host' };
  // Link is hidden so the pay button uses our colour (Link always shows its own green button).
  const noLink = { link: { display: 'never' } };
  const attempts = [
    ['2025-09-30.clover', { ui_mode: 'embedded', branding_settings: branding, wallet_options: noLink, ...local, ...base }],
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
