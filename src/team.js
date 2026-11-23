// Private Launch Room for Farah & Daniel (/launchroom/).
// Storage (KV binding "CODES"):
//   team:pw          -> {salt, hash, iter}  PBKDF2-SHA256 of the team password (never stored in plain text)
//   team:launchroom  -> {items:{}, checks:{}, days:{}, meta:{}}  the whole planner
//   team:fail:<ip>   -> failed login count (expires after 15 minutes)
const enc = new TextEncoder();
export const TEAM_COOKIE = 'fh_team';
const MAX_AGE_DAYS = 30;
const COLLECTIONS = ['items', 'checks', 'days', 'meta'];

function b64url(buf) {
  return btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
async function hmac(secret, data) {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return b64url(await crypto.subtle.sign('HMAC', key, enc.encode('team|' + data)));
}
function hexToBytes(h) { return new Uint8Array(h.match(/../g).map(x => parseInt(x, 16))); }
function toHex(buf) { return [...new Uint8Array(buf)].map(x => x.toString(16).padStart(2, '0')).join(''); }
function same(a, b) { if (a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; }

export async function checkPassword(env, pw) {
  const rec = await env.CODES.get('team:pw', 'json');
  if (!rec || !pw) return false;
  const key = await crypto.subtle.importKey('raw', enc.encode(pw), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt: hexToBytes(rec.salt), iterations: rec.iter }, key, 256);
  return same(toHex(bits), rec.hash);
}

export async function makeTeamCookie(env) {
  const exp = String(Date.now() + MAX_AGE_DAYS * 864e5);
  return `${TEAM_COOKIE}=${exp}.${await hmac(env.SESSION_SECRET, exp)}; Path=/; Max-Age=${MAX_AGE_DAYS * 86400}; HttpOnly; Secure; SameSite=Lax`;
}
export const clearTeamCookie = () => `${TEAM_COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`;

export async function isTeam(env, request) {
  const m = (request.headers.get('Cookie') || '').match(new RegExp(`(?:^|;\\s*)${TEAM_COOKIE}=([^;]+)`));
  if (!m) return false;
  const [exp, sig] = m[1].split('.');
  if (!exp || !sig || Number(exp) < Date.now()) return false;
  return same(await hmac(env.SESSION_SECRET, exp), sig);
}

export async function readPlan(env) {
  const d = (await env.CODES.get('team:launchroom', 'json')) || {};
  for (const c of COLLECTIONS) if (!d[c] || typeof d[c] !== 'object') d[c] = {};
  return d;
}

// One change: {col, id, data} (data null = delete).
export async function writePlan(env, { col, id, data }) {
  if (!COLLECTIONS.includes(col)) throw new Error('bad collection');
  if (typeof id !== 'string' || !/^[A-Za-z0-9_.~:@+-]{1,80}$/.test(id)) throw new Error('bad id');
  if (data !== null && (typeof data !== 'object' || Array.isArray(data))) throw new Error('bad data');
  if (data && JSON.stringify(data).length > 50000) throw new Error('too large');
  const d = await readPlan(env);
  if (data === null) delete d[col][id]; else d[col][id] = data;
  await env.CODES.put('team:launchroom', JSON.stringify(d));
  return d;
}
