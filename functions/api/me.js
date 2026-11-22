// Who is logged in on this device, and what their code unlocks. Used by the guides page.
import { readSession, getCode, productsOf, json } from '../../src/lib.js';

export async function onRequestGet({ request, env }) {
  const s = await readSession(env, request);
  const rec = s ? await getCode(env, s.c) : null;
  if (!rec || !rec.active || !rec.devices.includes(s.d)) return json({ loggedIn: false }, 401);
  return json({ loggedIn: true, name: rec.name || '', products: productsOf(rec) });
}
