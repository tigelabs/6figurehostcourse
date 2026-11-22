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
  // Split pay: stop the subscription after the 3rd monthly payment.
  if (s.mode === 'subscription' && s.subscription) {
    try {
      const subId = typeof s.subscription === 'string' ? s.subscription : s.subscription.id;
      const sub = await stripe(env, 'GET', `/subscriptions/${subId}`);
      if (!sub.cancel_at) {
        const months = Number(s.metadata?.split || 3);
        const d = new Date(sub.start_date * 1000); d.setUTCMonth(d.getUTCMonth() + months - 1); d.setUTCDate(d.getUTCDate() + 5);
        await stripe(env, 'POST', `/subscriptions/${subId}`, { cancel_at: String(Math.floor(d / 1000)), proration_behavior: 'none' });
      }
    } catch (e) { console.log('split cancel_at failed', e.message); }
  }
  if (r.first) await sendWelcome(env, r.rec);
  return { rec: r.rec, session: s };
}
