// Shared helpers for the 6-Figure Host course gate.
// Storage (Cloudflare KV, binding "CODES"):
//   code:HOST-XXXX-XXXX  -> {code, email, name, orderId, active, devices:[...], createdAt, source}
//   order:<orderId>      -> "HOST-XXXX-XXXX"   (so a repeated webhook never creates a second code)
//   email:<email>        -> "HOST-XXXX-XXXX"   (handy for support: find a buyer's code)

export const COOKIE = 'fh_session';
export const MAX_DEVICES_DEFAULT = 5;
const ALPHABET = '23456789ABCDEFGHJKMNPQRSTUVWXYZ'; // no 0/O, 1/I/L

export function normalizeCode(input) {
  let v = String(input || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (v.startsWith('HOST')) v = v.slice(4);
  if (v.length !== 8) return null;
  return `HOST-${v.slice(0, 4)}-${v.slice(4)}`;
}

export function newCode() {
  const bytes = new Uint8Array(8);
  crypto.getRandomValues(bytes);
  let s = '';
  for (const b of bytes) s += ALPHABET[b % ALPHABET.length];
  return `HOST-${s.slice(0, 4)}-${s.slice(4)}`;
}

export async function getCode(env, code) {
  return env.CODES.get(`code:${code}`, 'json');
}

export async function putCode(env, rec) {
  await env.CODES.put(`code:${rec.code}`, JSON.stringify(rec));
}

// Create a code that doesn't exist yet.
export async function createCode(env, { email = '', name = '', orderId = '', source = 'manual' }) {
  for (let i = 0; i < 8; i++) {
    const code = newCode();
    if (!(await getCode(env, code))) {
      const rec = { code, email, name, orderId: String(orderId || ''), active: true, devices: [], createdAt: new Date().toISOString(), source };
      await putCode(env, rec);
      if (orderId) await env.CODES.put(`order:${orderId}`, code);
      if (email) await env.CODES.put(`email:${email.toLowerCase()}`, code);
      return rec;
    }
  }
  throw new Error('Could not create a unique code');
}

// ---- signed session cookie -------------------------------------------------
const enc = new TextEncoder();
function b64url(buf) {
  let s = btoa(String.fromCharCode(...new Uint8Array(buf)));
  return s.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
function b64urlText(t) { return b64url(enc.encode(t)); }
function fromB64url(s) {
  s = s.replace(/-/g, '+').replace(/_/g, '/');
  while (s.length % 4) s += '=';
  return atob(s);
}
async function hmac(secret, data) {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return b64url(await crypto.subtle.sign('HMAC', key, enc.encode(data)));
}

export async function makeSession(env, code, device) {
  const payload = b64urlText(JSON.stringify({ c: code, d: device, t: Date.now() }));
  return `${payload}.${await hmac(env.SESSION_SECRET, payload)}`;
}

export async function readSession(env, request) {
  const cookie = request.headers.get('Cookie') || '';
  const m = cookie.match(new RegExp(`(?:^|;\\s*)${COOKIE}=([^;]+)`));
  if (!m) return null;
  const [payload, sig] = m[1].split('.');
  if (!payload || !sig) return null;
  if ((await hmac(env.SESSION_SECRET, payload)) !== sig) return null;
  try { return JSON.parse(fromB64url(payload)); } catch { return null; }
}

export function sessionCookie(value, maxAgeDays = 400) {
  return `${COOKIE}=${value}; Path=/; Max-Age=${maxAgeDays * 86400}; HttpOnly; Secure; SameSite=Lax`;
}

export function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...headers } });
}

// ---- Brevo -----------------------------------------------------------------
export async function brevo(env, path, body) {
  const r = await fetch(`https://api.brevo.com/v3${path}`, {
    method: 'POST',
    headers: { 'api-key': env.BREVO_API_KEY, 'Content-Type': 'application/json', accept: 'application/json' },
    body: JSON.stringify(body),
  });
  const text = await r.text();
  return { ok: r.ok, status: r.status, text };
}

export async function sendWelcome(env, rec) {
  // Called after every purchase: new buyers get their code, returning buyers get a reminder of it.
  const out = {};
  if (!env.BREVO_API_KEY) return { skipped: 'no BREVO_API_KEY' };
  if (rec.email) {
    const contact = { email: rec.email, attributes: { FIRSTNAME: rec.name || '', ACCESS_CODE: rec.code }, updateEnabled: true };
    if (env.BREVO_LIST_ID) contact.listIds = [Number(env.BREVO_LIST_ID)];
    out.contact = await brevo(env, '/contacts', contact);
    // First sale ever: the ACCESS_CODE field may not exist in Brevo yet. Create it and try again.
    if (!out.contact.ok && /attribute/i.test(out.contact.text)) {
      await fetch('https://api.brevo.com/v3/contacts/attributes/normal/ACCESS_CODE', {
        method: 'POST', headers: { 'api-key': env.BREVO_API_KEY, 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'text' }),
      });
      out.contact = await brevo(env, '/contacts', contact);
    }
    if (env.BREVO_TEMPLATE_ID) {
      out.email = await brevo(env, '/smtp/email', {
        templateId: Number(env.BREVO_TEMPLATE_ID),
        to: [{ email: rec.email, name: rec.name || rec.email }],
        params: { CODE: rec.code, FIRSTNAME: rec.name || 'there', COURSE_URL: productsOf(rec).includes('course') ? (env.COURSE_URL || '') : (env.COURSE_URL || '').replace(/\/?$/, '/').replace(/hostcourse\/$/, 'hostcourse/guides/') },
      });
    }
  }
  return out;
}

// ---- products ----------------------------------------------------------------
// What each code unlocks. Older codes (review codes, ThriveCart buyers) have no list and get the course.
export const SKUS = ['course', 'barcelona', 'bali', 'calculator'];
export function productsOf(rec) { return Array.isArray(rec?.products) ? rec.products : ['course']; }

// ---- Stripe ------------------------------------------------------------------
const STRIPE_VERSION = '2025-03-31.basil';
function formEncode(obj, pre = '', out = []) {
  for (const [k, v] of Object.entries(obj)) {
    if (v === undefined || v === null) continue;
    const key = pre ? `${pre}[${k}]` : k;
    if (typeof v === 'object') formEncode(v, key, out);
    else out.push(`${encodeURIComponent(key)}=${encodeURIComponent(v)}`);
  }
  return out;
}
export async function stripe(env, method, path, params, idempotencyKey, version) {
  const headers = { Authorization: `Bearer ${env.STRIPE_SECRET_KEY}`, 'Stripe-Version': version || STRIPE_VERSION };
  let url = `https://api.stripe.com/v1${path}`, body;
  const qs = params ? formEncode(params).join('&') : '';
  if (method === 'GET') { if (qs) url += `?${qs}`; }
  else { body = qs; headers['Content-Type'] = 'application/x-www-form-urlencoded'; }
  if (idempotencyKey) headers['Idempotency-Key'] = idempotencyKey;
  const r = await fetch(url, { method, headers, body });
  const data = await r.json();
  if (!r.ok) { const e = new Error(data?.error?.message || `Stripe ${r.status}`); e.stripe = data?.error; e.status = r.status; throw e; }
  return data;
}

// Price for each product, set in Cloudflare (PRICE_COURSE, PRICE_BARCELONA, PRICE_BALI).
export function priceFor(env, sku) { return env[`PRICE_${sku.toUpperCase()}`]; }

// Give a buyer what they paid for. Safe to call many times for the same payment.
// Finds the buyer's existing code by email, or makes a new one, and adds the products.
export async function grant(env, { email, name, skus, paymentId, customerId, paymentMethodId, source = 'stripe' }) {
  const done = await env.CODES.get(`pay:${paymentId}`);
  if (done) return { rec: await getCode(env, done), fresh: false, first: false };
  email = (email || '').trim().toLowerCase();
  let rec = null;
  const existing = email ? await env.CODES.get(`email:${email}`) : null;
  if (existing) rec = await getCode(env, existing);
  let fresh = false;
  if (!rec) { rec = await createCode(env, { email, name, orderId: paymentId, source }); rec.products = []; fresh = true; }
  if (!Array.isArray(rec.products)) rec.products = productsOf(rec);
  for (const s of skus) if (!rec.products.includes(s)) rec.products.push(s);
  if (customerId) rec.stripeCustomer = customerId;
  if (paymentMethodId) rec.stripePaymentMethod = paymentMethodId;
  rec.payments = [...(rec.payments || []), { id: paymentId, skus, at: new Date().toISOString() }];
  rec.active = true;
  await putCode(env, rec);
  await env.CODES.put(`pay:${paymentId}`, rec.code);
  return { rec, fresh, first: true };
}
