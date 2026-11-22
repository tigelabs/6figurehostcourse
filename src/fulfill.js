// Turns a paid Stripe Checkout Session into access (used by the thank-you page and the webhook).
import { stripe, grant, sendWelcome } from './lib.js';

export async function fulfillSession(env, sessionId) {
  const s = await stripe(env, 'GET', `/checkout/sessions/${encodeURIComponent(sessionId)}`, { expand: { 0: 'payment_intent' } });
  if (s.payment_status !== 'paid') return { pending: true };
  const pi = s.payment_intent || {};
  const skus = String(s.metadata?.skus || 'course').split(',').filter(Boolean);
  const r = await grant(env, {
    email: s.customer_details?.email, name: (s.customer_details?.name || '').split(' ')[0],
    skus, paymentId: pi.id || s.id, customerId: s.customer, paymentMethodId: pi.payment_method,
  });
  await env.CODES.put(`cs:${s.id}`, r.rec.code);
  if (r.first) await sendWelcome(env, r.rec);
  return { rec: r.rec, session: s };
}
