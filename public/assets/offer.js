/* Black Friday offer for the 6-Figure Host Course.
   Phases (Barcelona time): pre = until 27 Nov 00:00, bf = 27 Nov 00:00 to 30 Nov 23:59, after = from 1 Dec.
   Currency: EUR or USD (same numbers), chosen with the toggle; remembered on this device and passed to the checkout as ?cur=eur.
   The server (functions/api/checkout/session.js, src/offer.js) uses the same dates to pick the Stripe price.
   Preview a phase with ?phase=pre | bf | after (display only; the checkout always charges the real price). */
(function () {
  var START = Date.parse('2026-11-26T23:00:00Z'), END = Date.parse('2026-11-30T23:00:00Z');
  var q = (location.search.match(/[?&]phase=(pre|bf|after)/) || [])[1];
  var now = Date.now();
  var phase = q || (now < START ? 'pre' : now < END ? 'bf' : 'after');
  var P = {
    pre:   { one: 297, was: 0,   split: 79, splitWas: 0 },
    bf:    { one: 197, was: 297, split: 54, splitWas: 79 },
    after: { one: 297, was: 0,   split: 79, splitWas: 0 }
  }[phase];
  var O = window.FH_OFFER = { phase: phase, start: START, end: END, one: P.one, was: P.was, split: P.split, splitWas: P.splitWas, months: 4 };
  var cur = 'usd';
  try { var qc = (location.search.match(/[?&]cur=(eur|usd)/) || [])[1]; var sv = localStorage.getItem('fh_cur'); cur = qc || (sv === 'eur' || sv === 'usd' ? sv : (/^Europe\//.test(Intl.DateTimeFormat().resolvedOptions().timeZone || '') ? 'eur' : 'usd')); } catch (e) {}
  O.cur = cur;
  function m(n) { return (O.cur === 'eur' ? '€' : '$') + n; }
  O.money = m;

  function $$(sel) { return [].slice.call(document.querySelectorAll(sel)); }
  function set(name, html) { $$('[data-o="' + name + '"]').forEach(function (el) { el.innerHTML = html; }); }
  function show(name, on) { $$('[data-o="' + name + '"]').forEach(function (el) { el.hidden = !on; }); }

  function fill() {
    var bf = phase === 'bf', n = O.months;
    set('price', bf ? '<s>' + m(297) + '</s> ' + m(197) : m(297));
    set('price-plain', m(P.one));
    set('cta', 'Get instant access for ' + m(P.one));
    set('was1', bf ? '<s>' + m(297) + '</s>' : '');
    set('now1', m(P.one));
    set('save', bf ? 'Black Friday: you save ' + m(100) : 'Lifetime access, no subscription');
    set('was2', bf ? '<s>' + n + ' × ' + m(P.splitWas) + '</s>' : '');
    set('now2', n + ' × ' + m(P.split));
    set('tot2', m(P.split * n) + ' total, paid monthly');
    set('split-note', 'Start today, pay in ' + n + ' months');
    $$('[data-o="vs"]').forEach(function (el) { el.textContent = m(el.getAttribute('data-v')); });
    if (phase === 'pre') {
      set('bar', '<b>Black Friday</b> opens 27 November: the course for ' + m(197) + ' instead of ' + m(297) + '. Starts in');
      set('headline', 'Black Friday opens 27 November: ' + m(197) + ' for 4 days only');
    } else if (bf) {
      set('bar', '<b>Black Friday:</b> the course for ' + m(197) + ' instead of ' + m(297) + ', or ' + n + ' × ' + m(P.split) + '. Ends 30 November at midnight.');
      set('headline', 'Black Friday price ends 30 November at midnight');
    } else {
      set('bar', 'The new interactive 6-Figure Host Course: one payment of ' + m(297) + ', or ' + n + ' × ' + m(P.split) + '.');
      set('headline', '');
    }
    set('mc-note', '*In the video we talk about our old guide and its price. That guide is now the full 6-Figure Host Course' + (phase === 'after' ? ': <b>' + m(297) + '</b>.' : (bf ? '. Black Friday price: <b><s>' + m(297) + '</s> ' + m(197) + '</b>, until 30 November.' : '. On Black Friday (27 to 30 November): <b><s>' + m(297) + '</s> ' + m(197) + '</b>.')));
    show('countdown', phase !== 'after');
    show('headline', phase !== 'after');
    $$('[data-o="cur"] button').forEach(function (b) { b.setAttribute('aria-checked', b.getAttribute('data-cur') === O.cur ? 'true' : 'false'); });
    $$('a[href*="/checkout"]').forEach(function (a) {
      var h = a.getAttribute('href').replace(/([?&])cur=(eur|usd)&?/, '$1').replace(/[?&]$/, '');
      if (O.cur === 'eur') h += (h.indexOf('?') < 0 ? '?' : '&') + 'cur=eur';
      a.setAttribute('href', h);
    });
    document.documentElement.setAttribute('data-phase', phase);
  }
  O.setCur = function (c) { O.cur = c; try { localStorage.setItem('fh_cur', c); } catch (e) {} fill(); if (O.onchange) O.onchange(); };
  document.addEventListener('click', function (e) { var b = e.target.closest && e.target.closest('[data-o="cur"] button'); if (b) O.setCur(b.getAttribute('data-cur')); });

  function tick() {
    var target = phase === 'pre' ? START : END;
    var left = Math.max(0, target - (q ? (phase === 'pre' ? START - 4.4 * 864e5 : END - 1.6 * 864e5) + (Date.now() - now) : Date.now()));
    var d = Math.floor(left / 864e5), h = Math.floor(left / 36e5) % 24, m = Math.floor(left / 6e4) % 60, s = Math.floor(left / 1e3) % 60;
    var html = [[d, 'Days'], [h, 'Hours'], [m, 'Min'], [s, 'Sec']].map(function (x) {
      return '<span class="cd-u"><b>' + (x[0] < 10 ? '0' : '') + x[0] + '</b><i>' + x[1] + '</i></span>';
    }).join('');
    set('countdown', html);
    if (!q && left === 0) { location.reload(); }
  }

  function init() { fill(); if (phase !== 'after') { tick(); setInterval(tick, 1000); } }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
