// Every request passes through here. The public site (home page, privacy, future sales pages)
// is open to everyone. Only /hostcourse/ (the course) needs a valid session cookie for an active code.
import { readSession, getCode, productsOf } from '../src/lib.js';

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
  // Pages and guide files check the code itself, so a refund locks them right away.
  const isPage = path.endsWith('/') || path.endsWith('.html');
  const guide = path.match(/^\/hostcourse\/guides\/(barcelona|bali)\b/);
  if (ok && (isPage || guide)) {
    const rec = await getCode(env, session.c);
    ok = !!(rec && rec.active && rec.devices.includes(session.d));
    if (ok) {
      const owned = productsOf(rec);
      const inGuides = path.startsWith('/hostcourse/guides/');
      if (guide && !owned.includes(guide[1])) {
        return isPage || path.endsWith('.pdf') ? Response.redirect(new URL('/hostcourse/guides/', url).toString(), 302) : new Response('Not found', { status: 404 });
      }
      // Bought only a guide: the course pages send them to their guides.
      if (isPage && !inGuides && !owned.includes('course')) return Response.redirect(new URL('/hostcourse/guides/', url).toString(), 302);
    }
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
