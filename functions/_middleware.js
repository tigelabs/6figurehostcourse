// Every request passes through here. Only the login page (and what it needs) is public;
// everything else requires a valid session cookie for an active code.
import { readSession, getCode } from '../src/lib.js';

const PUBLIC = new Set(['/login', '/login.html', '/api/login', '/api/thrivecart', '/img/cover.webp', '/favicon.ico', '/robots.txt']);

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const path = url.pathname;

  if (PUBLIC.has(path) || path.startsWith('/api/admin/')) return next();

  const session = await readSession(env, request);
  let ok = !!session;
  // Check the code is still active on page loads (so a refund locks the course right away).
  const isPage = path === '/' || path.endsWith('.html');
  if (ok && isPage) {
    const rec = await getCode(env, session.c);
    ok = !!(rec && rec.active && rec.devices.includes(session.d));
  }
  if (ok) {
    const res = await next();
    if (isPage) {
      const r = new Response(res.body, res);
      r.headers.set('Cache-Control', 'private, no-store');
      r.headers.set('X-Robots-Tag', 'noindex');
      return r;
    }
    return res;
  }

  if (isPage) {
    const to = new URL('/login', url);
    if (path !== '/' ) to.searchParams.set('next', path);
    return Response.redirect(to.toString(), 302);
  }
  return new Response('Not found', { status: 404 });
}
