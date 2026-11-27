/* Black Friday offer for the 6-Figure Host Course.
   Phases (Barcelona time): pre = until 27 Nov 00:00, bf = 27 Nov 00:00 to 30 Nov 23:59, after = from 1 Dec.
   Currency: EUR or USD (prices set in EUR, USD converted at a fixed rate), chosen with the toggle; remembered on this device and passed to the checkout as ?cur=eur.
   The server (functions/api/checkout/session.js, src/offer.js) uses the same dates to pick the Stripe price.
   Preview a phase with ?phase=pre | bf | after (display only; the checkout always charges the real price). */
(function () {
  var START = Date.parse('2026-11-26T23:00:00Z'), END = Date.parse('2026-11-30T23:00:00Z');
  var q = (location.search.match(/[?&]phase=(pre|bf|after)/) || [])[1];
  var now = Date.now();
  var phase = q || (now < START ? 'pre' : now < END ? 'bf' : 'after');
  // Course prices: set in EUR; USD = EUR at 1.156 (23 Nov 2026), the same amounts as the Stripe prices.
  // Split pay = 3 monthly payments.
  var RATE = 1.156;
  var TABLE = {
    eur: { reg: 297, bf: 147, split: 99, splitBf: 49 },
    usd: { reg: 343, bf: 170, split: 114, splitBf: 57 }
  };
  var O = window.FH_OFFER = { phase: phase, start: START, end: END, months: 3, rate: RATE };
  var P = {};
  function setPrices() {
    var t = TABLE[O.cur] || TABLE.usd, bf = phase === 'bf';
    P.one = bf ? t.bf : t.reg; P.was = bf ? t.reg : 0; P.split = bf ? t.splitBf : t.split; P.splitWas = bf ? t.split : 0;
    O.one = P.one; O.was = P.was; O.split = P.split; O.splitWas = P.splitWas; O.reg = t.reg; O.bfOne = t.bf; O.regSplit = t.split;
  }
  var cur = 'usd';
  try { var qc = (location.search.match(/[?&]cur=(eur|usd)/) || [])[1]; var sv = localStorage.getItem('fh_cur'); cur = qc || (sv === 'eur' || sv === 'usd' ? sv : (/^Europe\//.test(Intl.DateTimeFormat().resolvedOptions().timeZone || '') ? 'eur' : 'usd')); } catch (e) {}
  O.cur = cur;
  setPrices();
  function m(n) { return (O.cur === 'eur' ? '€' : '$') + n; }
  O.money = m;

  function $$(sel) { return [].slice.call(document.querySelectorAll(sel)); }
  function set(name, html) { $$('[data-o="' + name + '"]').forEach(function (el) { el.innerHTML = html; }); }
  function show(name, on) { $$('[data-o="' + name + '"]').forEach(function (el) { el.hidden = !on; }); }

  function fill() {
    var bf = phase === 'bf', n = O.months;
    set('price', bf ? '<s>' + m(O.reg) + '</s> ' + m(O.bfOne) : m(O.reg));
    set('price-plain', m(P.one));
    set('cta', phase === 'pre' ? 'Coming soon on Black Friday' : 'Get instant access for ' + m(P.one));
    set('was1', bf ? '<s>' + m(O.reg) + '</s>' : '');
    set('now1', m(P.one));
    set('save', bf ? 'Black Friday: you save ' + m(O.reg - O.bfOne) : 'Lifetime access, no subscription');
    set('was2', bf ? '<s>' + n + ' × ' + m(P.splitWas) + '</s>' : '');
    set('now2', n + ' × ' + m(P.split));
    set('tot2', m(P.split * n) + ' total, paid monthly');
    set('split-note', 'Start today, pay in ' + n + ' months');
    $$('[data-o="vs"]').forEach(function (el) { var v = Number(el.getAttribute('data-v')); el.textContent = m(O.cur === 'usd' ? Math.round(v * RATE) : v); });
    if (phase === 'pre') {
      set('bar', '<b>Black Friday</b> opens 27 November: the course for ' + m(O.bfOne) + ' instead of ' + m(O.reg) + '. Starts in');
      set('headline', 'Black Friday opens 27 November: ' + m(O.bfOne) + ' for 4 days only');
    } else if (bf) {
      set('bar', '<b>Black Friday:</b> the course for ' + m(O.bfOne) + ' instead of ' + m(O.reg) + ', or ' + n + ' × ' + m(P.split) + '. Ends 30 November at midnight.');
      set('headline', 'Black Friday price ends 30 November at midnight');
    } else {
      set('bar', 'The new interactive 6-Figure Host Course: one payment of ' + m(O.reg) + ', or ' + n + ' × ' + m(P.split) + '.');
      set('headline', '');
    }
    set('mc-note', phase === 'pre'
      ? '*In the video we mention our old guide and its price. We’re turning that guide into a bigger, better course, so the old guide is no longer available. The new 6-Figure Host Course launches on <b>Black Friday, 27 November</b>, at <b><s>' + m(O.reg) + '</s> ' + m(O.bfOne) + '</b>.'
      : bf ? '*In the video we mention our old guide and its price. That guide is now the full 6-Figure Host Course: <b><s>' + m(O.reg) + '</s> ' + m(O.bfOne) + '</b>.'
      : '*In the video we mention our old guide and its price. That guide is now the full 6-Figure Host Course: <b>' + m(O.reg) + '</b>.');
    // Before Black Friday the course is not on sale yet: buy buttons say "Coming soon".
    $$('a[data-buy]').forEach(function (a) { var pre = phase === 'pre'; a.textContent = pre ? 'Coming soon on Black Friday' : a.getAttribute('data-buy'); a.classList.toggle('is-soon', pre); if (pre) a.setAttribute('aria-disabled', 'true'); else a.removeAttribute('aria-disabled'); });
    $$('a[href*="/checkout"]').forEach(function (a) { var h = a.getAttribute('href'); var course = !/item=(calculator|barcelona|bali)/.test(h); if (course && phase === 'pre') { a.classList.add('is-soon'); a.setAttribute('aria-disabled', 'true'); } });
    // During Black Friday: a small line under each course buy button with the price after Black Friday.
    $$('a.cta[href*="/checkout"]').forEach(function (a) {
      if (/item=(calculator|barcelona|bali)/.test(a.getAttribute('href'))) return;
      var nx = a.nextElementSibling, el = nx && nx.classList.contains('upnote') ? nx : null;
      if (!el) { el = document.createElement('small'); el.className = 'upnote'; a.parentNode.insertBefore(el, a.nextSibling); }
      var split = /plan=split/.test(a.getAttribute('href'));
      el.textContent = split ? 'Goes up to ' + O.months + ' × ' + m(O.regSplit) + ' when Black Friday ends (30 Nov)' : 'Price goes up to ' + m(O.reg) + ' when Black Friday ends (30 Nov)';
      el.hidden = phase !== 'bf';
    });
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
  O.setCur = function (c) { O.cur = c; setPrices(); try { localStorage.setItem('fh_cur', c); } catch (e) {} fill(); if (O.onchange) O.onchange(); };
  document.addEventListener('click', function (e) { var soon = e.target.closest && e.target.closest('a.is-soon'); if (soon) { e.preventDefault(); return; } var b = e.target.closest && e.target.closest('[data-o="cur"] button'); if (b) O.setCur(b.getAttribute('data-cur')); });

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
