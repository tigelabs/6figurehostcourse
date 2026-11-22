// Every request passes through here. The public site (home page, privacy, future sales pages)
// is open to everyone. Only /hostcourse/ (the course) needs a valid session cookie for an active code.
import { readSession, getCode } from '../src/lib.js';

const COURSE = '/hostcourse';
const COURSE_PUBLIC = new Set([
  '/hostcourse/login', '/hostcourse/login.html', '/hostcourse/img/cover.webp',
]);

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const path = url.pathname;

  // Old course address: send people to the new one.
  if (path === '/login' || path === '/login.html') {
    return Response.redirect(new URL('/hostcourse/login' + url.search, url).toString(), 301);
  }

  if (path !== COURSE && !path.startsWith(COURSE + '/')) return next();
  if (path === COURSE) return Response.redirect(new URL(COURSE + '/', url).toString(), 301);
  if (COURSE_PUBLIC.has(path)) return next();

  const session = await readSession(env, request);
  let ok = !!session;
  // Check the code is still active on page loads (so a refund locks the course right away).
  const isPage = path.endsWith('/') || path.endsWith('.html');
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
    const to = new URL(COURSE + '/login', url);
    if (path !== COURSE + '/') to.searchParams.set('next', path);
    return Response.redirect(to.toString(), 302);
  }
  return new Response('Not found', { status: 404 });
}
