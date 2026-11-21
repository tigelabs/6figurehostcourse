// ThriveCart webhook (Settings > API & Webhooks > Webhooks & notifications).
// order.success  -> create a code, add the buyer to Brevo and send the welcome email
// order.refund   -> deactivate that order's code
import { createCode, getCode, putCode, sendWelcome, json } from '../../src/lib.js';

async function readForm(request) {
  const type = request.headers.get('Content-Type') || '';
  if (type.includes('application/json')) return flatten(await request.json());
  const fd = await request.formData();
  const o = {};
  for (const [k, v] of fd.entries()) o[k] = v;
  return o;
}
function flatten(obj, pre = '', out = {}) {
  for (const [k, v] of Object.entries(obj || {})) {
    const key = pre ? `${pre}[${k}]` : k;
    if (v && typeof v === 'object') flatten(v, key, out); else out[key] = v;
  }
  return out;
}

// ThriveCart checks the URL with a HEAD/GET request when you save it.
export async function onRequestHead() { return new Response(null, { status: 200 }); }
export async function onRequestGet() { return new Response('OK', { status: 200 }); }

export async function onRequestPost({ request, env }) {
  const p = await readForm(request);
  if (!env.THRIVECART_SECRET || p.thrivecart_secret !== env.THRIVECART_SECRET) return json({ error: 'bad secret' }, 401);

  const event = p.event || '';
  const orderId = p.order_id || p['order[id]'] || '';
  const email = (p['customer[email]'] || p.customer_email || '').trim();
  const name = (p['customer[first_name]'] || p['customer[name]'] || '').trim();

  // Optional: only react to the course product(s). PRODUCT_IDS = "12,34"
  if (env.PRODUCT_IDS) {
    const ids = env.PRODUCT_IDS.split(',').map(s => s.trim());
    if (p.base_product && !ids.includes(String(p.base_product))) return json({ ignored: 'other product' });
  }

  if (event === 'order.success') {
    if (orderId) {
      const existing = await env.CODES.get(`order:${orderId}`);
      if (existing) return json({ ok: true, code: existing, duplicate: true });
    }
    const rec = await createCode(env, { email, name, orderId, source: p.mode === 'test' ? 'thrivecart-test' : 'thrivecart' });
    const brevo = await sendWelcome(env, rec);
    return json({ ok: true, code: rec.code, brevo });
  }

  if (event === 'order.refund') {
    const code = orderId ? await env.CODES.get(`order:${orderId}`) : null;
    if (code) {
      const rec = await getCode(env, code);
      if (rec) { rec.active = false; rec.refundedAt = new Date().toISOString(); await putCode(env, rec); }
    }
    return json({ ok: true, deactivated: code || null });
  }

  return json({ ignored: event });
}
