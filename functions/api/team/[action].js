// Launch Room API: /api/team/login, /api/team/logout, /api/team/data, /api/team/write
import { json, productsOf } from '../../../src/lib.js';
import { checkPassword, makeTeamCookie, clearTeamCookie, isTeam, readPlan, writePlan } from '../../../src/team.js';

export async function onRequest({ request, env, params }) {
  const action = params.action;
  const method = request.method;

  if (action === 'login' && method === 'POST') {
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    const failKey = `team:fail:${ip}`;
    const fails = Number((await env.CODES.get(failKey)) || 0);
    if (fails >= 10) return json({ error: 'Too many attempts. Try again in 15 minutes.' }, 429);
    let body = {};
    try { body = await request.json(); } catch {}
    if (await checkPassword(env, String(body.password || ''))) {
      return json({ ok: true }, 200, { 'Set-Cookie': await makeTeamCookie(env) });
    }
    await env.CODES.put(failKey, String(fails + 1), { expirationTtl: 900 });
    return json({ error: 'That password is not right.' }, 401);
  }

  if (action === 'logout') {
    return new Response(null, { status: 302, headers: { Location: '/teamdashboard/login', 'Set-Cookie': clearTeamCookie() } });
  }

  if (!(await isTeam(env, request))) return json({ error: 'Please log in again.' }, 401);

  if (action === 'data' && method === 'GET') return json(await readPlan(env));

  // Students log: every access code with its buyer, logins and course progress.
  if (action === 'students' && method === 'GET') {
    const names = [];
    let cursor;
    do {
      const page = await env.CODES.list({ prefix: 'code:', cursor, limit: 1000 });
      names.push(...page.keys.map(k => k.name.slice(5)));
      cursor = page.list_complete ? null : page.cursor;
    } while (cursor);
    const rows = [];
    for (let i = 0; i < names.length; i += 40) {
      const part = await Promise.all(names.slice(i, i + 40).map(async c => {
        const [rec, prog] = await Promise.all([env.CODES.get(`code:${c}`, 'json'), env.CODES.get(`prog:${c}`, 'json')]);
        if (!rec) return null;
        return {
          code: rec.code, email: rec.email || '', name: rec.name || '', source: rec.source || '', products: productsOf(rec),
          active: rec.active !== false, createdAt: rec.createdAt || '', devices: (rec.devices || []).length,
          lastLogin: rec.lastLogin || '', loginCount: rec.loginCount || 0, logins: rec.logins || [],
          payments: (rec.payments || []).map(p => ({ skus: p.skus, at: p.at })), refunds: (rec.refunds || []).map(p => ({ skus: p.skus, at: p.at })),
          refundedAt: rec.refundedAt || '', progress: prog || null,
        };
      }));
      rows.push(...part.filter(Boolean));
    }
    return json({ students: rows, at: new Date().toISOString() });
  }

  if (action === 'write' && method === 'POST') {
    let body = {};
    try { body = await request.json(); } catch {}
    try { return json({ ok: true, data: await writePlan(env, body) }); }
    catch (e) { return json({ error: String(e.message || e) }, 400); }
  }

  return json({ error: 'Not found' }, 404);
}
