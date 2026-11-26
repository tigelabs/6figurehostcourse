// Every request passes through here. The public site (home page, privacy, future sales pages)
// is open to everyone. Only /hostcourse/ (the course) needs a valid session cookie for an active code.
import { readSession, getCode, productsOf } from '../src/lib.js';
import { isTeam } from '../src/team.js';

const TEAM = '/teamdashboard';
const TEAM_PUBLIC = new Set(['/teamdashboard/login', '/teamdashboard/login.html']);

const COURSE = '/hostcourse';
const COURSE_PUBLIC = new Set([
  '/hostcourse/login', '/hostcourse/login.html', '/hostcourse/img/cover.webp', '/hostcourse/img/login-cover.webp',
]);

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  // Encoded slashes or backslashes (/hostcourse%2Findex.html) would slip past the path checks below
  // while the file server still decodes them, so they are refused outright.
  if (/%2f|%5c|\\/i.test(url.pathname)) return new Response('Not found', { status: 404 });
  let path;
  try { path = decodeURIComponent(url.pathname).replace(/\/{2,}/g, '/'); } catch { return new Response('Not found', { status: 404 }); }
  const lower = path.toLowerCase();

  // Old course address: send people to the new one.
  if (path === '/login' || path === '/login.html') {
    return Response.redirect(new URL('/hostcourse/login' + url.search, url).toString(), 301);
  }

  // Old Launch Room address: it now lives inside the team dashboard.
  if (lower === '/launchroom' || lower.startsWith('/launchroom/')) {
    return Response.redirect(new URL('/teamdashboard/launchroom/', url).toString(), 301);
  }

  // Private team dashboard (Farah & Daniel only): Launch Room, Students log.
  if (lower === TEAM || lower.startsWith(TEAM + '/')) {
    if (path === TEAM) return Response.redirect(new URL(TEAM + '/', url).toString(), 301);
    if (TEAM_PUBLIC.has(path)) {
      const r = await next(), out = new Response(r.body, r);
      out.headers.set('X-Robots-Tag', 'noindex, nofollow');
      return out;
    }
    if (!(await isTeam(env, request))) {
      if (path.endsWith('/') || path.endsWith('.html')) { const to = new URL(TEAM + '/login', url); if (path !== TEAM + '/') to.searchParams.set('next', path); return Response.redirect(to.toString(), 302); }
      return new Response('Not found', { status: 404 });
    }
    const r = await next(), out = new Response(r.body, r);
    out.headers.set('Cache-Control', 'private, no-store');
    out.headers.set('X-Robots-Tag', 'noindex, nofollow');
    return out;
  }

  if (lower !== COURSE && !lower.startsWith(COURSE + '/')) return next();
  if (path === COURSE) return Response.redirect(new URL(COURSE + '/', url).toString(), 301);
  if (COURSE_PUBLIC.has(path)) return next();

  const session = await readSession(env, request);
  let ok = !!session;
  // Pages and guide files check the code itself, so a refund locks them right away.
  const isPage = path.endsWith('/') || path.endsWith('.html');
  const guide = path.match(/^\/hostcourse\/guides\/(barcelona|bali)\b/);
  const calc = path.startsWith('/hostcourse/calculator/');
  const isFile = /\.(pdf|docx?|xlsx?|zip)$/i.test(path);
  if (ok && (isPage || guide || calc || isFile)) {
    const rec = await getCode(env, session.c);
    ok = !!(rec && rec.active && rec.devices.includes(session.d));
    if (ok) {
      const owned = productsOf(rec);
      const inGuides = path.startsWith('/hostcourse/guides/') || calc;
      if (calc && !owned.includes('calculator') && !owned.includes('course')) return Response.redirect(new URL('/hostcourse/guides/', url).toString(), 302);
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
