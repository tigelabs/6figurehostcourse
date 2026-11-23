// Launch Room API: /api/team/login, /api/team/logout, /api/team/data, /api/team/write
import { json } from '../../../src/lib.js';
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
    return new Response(null, { status: 302, headers: { Location: '/launchroom/login', 'Set-Cookie': clearTeamCookie() } });
  }

  if (!(await isTeam(env, request))) return json({ error: 'Please log in again.' }, 401);

  if (action === 'data' && method === 'GET') return json(await readPlan(env));

  if (action === 'write' && method === 'POST') {
    let body = {};
    try { body = await request.json(); } catch {}
    try { return json({ ok: true, data: await writePlan(env, body) }); }
    catch (e) { return json({ error: String(e.message || e) }, 400); }
  }

  return json({ error: 'Not found' }, 404);
}
