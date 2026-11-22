// Black Friday for the course (same dates as public/assets/offer.js), Barcelona time:
// 27 Nov 2026 00:00 until the end of 30 Nov 2026. Before and after: regular price.
export const BF_START = Date.parse('2026-11-26T23:00:00Z');
export const BF_END = Date.parse('2026-11-30T23:00:00Z');
export function phase(now = Date.now()) { return now < BF_START ? 'pre' : now < BF_END ? 'bf' : 'after'; }
// Which Stripe price to charge for the course. Split pay = 3 monthly payments (cancelled after the 4th).
export function coursePrice(env, plan, now = Date.now()) {
  const bf = phase(now) === 'bf';
  if (plan === 'split') return bf ? env.PRICE_COURSE_SPLIT_BF : env.PRICE_COURSE_SPLIT;
  return bf ? env.PRICE_COURSE_BF : env.PRICE_COURSE;
}
export const SPLIT_MONTHS = 4;
