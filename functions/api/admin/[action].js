// Small admin tools, protected by the ADMIN_KEY secret.
// Use from a terminal or a browser tool like Hoppscotch, always with the header:  x-admin-key: <ADMIN_KEY>
//
// POST /api/admin/create      {email, name, send:true}  -> make a code by hand (gift, team, replacement)
// POST /api/admin/lookup      {code} or {email}         -> see a code, its status and devices
// POST /api/admin/reset       {code}                    -> forget all devices (the buyer logs in again)
// POST /api/admin/deactivate  {code}                    -> switch a code off
// POST /api/admin/activate    {code}                    -> switch a code back on
// POST /api/admin/setup       {}                        -> create the ACCESS_CODE attribute in Brevo (run once)
import { normalizeCode, getCode, putCode, createCode, sendWelcome, brevo, json, safeEqual, tooMany, countFail } from '../../../src/lib.js';

export async function onRequestPost({ request, env, params }) {
  if (await tooMany(env, request, 'admin', 10, 3600)) return json({ error: 'Too many attempts. Try again later.' }, 429);
  if (!env.ADMIN_KEY || !safeEqual(request.headers.get('x-admin-key') || '', env.ADMIN_KEY)) {
    await countFail(env, request, 'admin', 3600);
    return json({ error: 'unauthorized' }, 401);
  }
  let b = {};
  try { b = await request.json(); } catch {}
  const action = params.action;

  if (action === 'create') {
    const rec = await createCode(env, { email: (b.email || '').trim(), name: (b.name || '').trim(), source: 'admin' });
    const sent = b.send ? await sendWelcome(env, rec) : null;
    return json({ ok: true, record: rec, sent });
  }

  if (action === 'setup') {
    const r = await fetch('https://api.brevo.com/v3/contacts/attributes/normal/ACCESS_CODE', {
      method: 'POST', headers: { 'api-key': env.BREVO_API_KEY, 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'text' }),
    });
    return json({ status: r.status, body: await r.text() });
  }

  let code = normalizeCode(b.code);
  if (!code && b.email) code = await env.CODES.get(`email:${String(b.email).toLowerCase().trim()}`);
  if (!code) return json({ error: 'give a code or an email' }, 400);
  const rec = await getCode(env, code);
  if (!rec) return json({ error: 'code not found' }, 404);

  if (action === 'lookup') return json({ record: rec });
  if (action === 'reset') { rec.devices = []; await putCode(env, rec); return json({ ok: true, record: rec }); }
  if (action === 'deactivate') { rec.active = false; await putCode(env, rec); return json({ ok: true, record: rec }); }
  if (action === 'activate') { rec.active = true; await putCode(env, rec); return json({ ok: true, record: rec }); }
  return json({ error: 'unknown action' }, 400);
}
