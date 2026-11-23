// Black Friday for the course (same dates as public/assets/offer.js), Barcelona time:
// 27 Nov 2026 00:00 until the end of 30 Nov 2026. Before and after: regular price.
export const BF_START = Date.parse('2026-11-26T23:00:00Z');
export const BF_END = Date.parse('2026-11-30T23:00:00Z');
export function phase(now = Date.now()) { return now < BF_START ? 'pre' : now < BF_END ? 'bf' : 'after'; }
// Which Stripe price to charge for the course. Prices are set in EUR (USD amount = EUR at 1.156, as a currency option).
// Split pay = 3 monthly payments (cancelled after the 3rd).
const COURSE_PRICES = {
  one: 'price_1UerPhEuGEmbLNARLCfZSQJN',      // EUR 297 / USD 343
  oneBf: 'price_1UerPoEuGEmbLNARt8C2Ndfi',    // EUR 147 / USD 170
  split: 'price_1UerPpEuGEmbLNAREsE8Ke1k',    // 3 x EUR 99 / USD 114 per month
  splitBf: 'price_1UerPqEuGEmbLNARsFavffvc',  // 3 x EUR 49 / USD 57 per month
};
export function coursePrice(env, plan, now = Date.now()) {
  const bf = phase(now) === 'bf';
  if (plan === 'split') return bf ? COURSE_PRICES.splitBf : COURSE_PRICES.split;
  return bf ? COURSE_PRICES.oneBf : COURSE_PRICES.one;
}
export const SPLIT_MONTHS = 3;
