// The course sends a short progress summary here (never the student's notes):
// which lessons are marked done, how many tasks are ticked, the last page and the language.
// Stored as prog:<code>. Only written when something changed, or every 30 minutes as "last active".
import { readSession, getCode, json } from '../../src/lib.js';

const LESSONS = ['start', 'story', 'roadmap', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10', 'ch11', 'ch12', 'ch13'];

export async function onRequestPost({ request, env }) {
  const s = await readSession(env, request);
  const rec = s ? await getCode(env, s.c) : null;
  if (!rec || !rec.active || !rec.devices.includes(s.d)) return json({ error: 'not logged in' }, 401);
  let b = {}; try { b = await request.json(); } catch {}
  const done = Array.isArray(b.done) ? LESSONS.filter(l => b.done.includes(l)) : [];
  const tasks = Math.max(0, Math.min(5000, Math.floor(Number(b.tasks) || 0)));
  const last = String(b.last || '').replace(/[^A-Za-z0-9_-]/g, '').slice(0, 40);
  const lang = ['en', 'nl', 'es', 'pt'].includes(b.lang) ? b.lang : 'en';
  const key = `prog:${rec.code}`;
  const old = (await env.CODES.get(key, 'json')) || {};
  const same = JSON.stringify([old.done, old.tasks, old.last, old.lang]) === JSON.stringify([done, tasks, last, lang]);
  const now = Date.now();
  if (same && old.at && now - Date.parse(old.at) < 30 * 60e3) return json({ ok: true, skipped: true });
  const out = { done, tasks, last, lang, at: new Date(now).toISOString(), device: rec.devices.indexOf(s.d) + 1, first: old.first || new Date(now).toISOString() };
  await env.CODES.put(key, JSON.stringify(out));
  return json({ ok: true });
}
