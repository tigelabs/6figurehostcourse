/* Black Friday offer for the 6-Figure Host Course.
   Phases (Barcelona time): pre = until 27 Nov 00:00, bf = 27 Nov 00:00 to 1 Dec 23:59, after = from 2 Dec.
   The server (functions/api/checkout/session.js, src/offer.js) uses the same dates to pick the Stripe price.
   Preview a phase with ?phase=pre | bf | after (display only; the checkout always charges the real price). */
(function () {
  var START = Date.parse('2026-11-26T23:00:00Z'), END = Date.parse('2026-12-01T23:00:00Z');
  var q = (location.search.match(/[?&]phase=(pre|bf|after)/) || [])[1];
  var now = Date.now();
  var phase = q || (now < START ? 'pre' : now < END ? 'bf' : 'after');
  var P = {
    pre:   { one: 297, was: 0,   split: 109, splitWas: 0 },
    bf:    { one: 197, was: 297, split: 69,  splitWas: 109 },
    after: { one: 297, was: 0,   split: 109, splitWas: 0 }
  }[phase];
  var O = window.FH_OFFER = { phase: phase, start: START, end: END, one: P.one, was: P.was, split: P.split, splitWas: P.splitWas, months: 3 };

  function $$(sel) { return [].slice.call(document.querySelectorAll(sel)); }
  function set(name, html) { $$('[data-o="' + name + '"]').forEach(function (el) { el.innerHTML = html; }); }
  function show(name, on) { $$('[data-o="' + name + '"]').forEach(function (el) { el.hidden = !on; }); }

  function fill() {
    var bf = phase === 'bf';
    set('price', bf ? '<s>$297</s> $197' : '$297');
    set('price-plain', '$' + P.one);
    set('cta', 'Get instant access for $' + P.one);
    set('was1', bf ? '<s>$297</s>' : '');
    set('now1', '$' + P.one);
    set('save', bf ? 'Black Friday: you save $100' : 'Lifetime access, no subscription');
    set('was2', bf ? '<s>3 × $109</s>' : '');
    set('now2', '3 × $' + P.split);
    set('tot2', '$' + (P.split * 3) + ' total, paid monthly');
    if (phase === 'pre') {
      set('bar', '<b>Black Friday</b> opens 27 November: the course for $197 instead of $297. Starts in');
      set('headline', 'Black Friday opens 27 November: $197 for 5 days only');
    } else if (bf) {
      set('bar', '<b>Black Friday:</b> the course for $197 instead of $297, or 3 × $69. Ends 1 December at midnight.');
      set('headline', 'Black Friday price ends 1 December at midnight');
    } else {
      set('bar', 'The new interactive 6-Figure Host Course: one payment of $297, or 3 × $109.');
      set('headline', '');
    }
    show('countdown', phase !== 'after');
    show('headline', phase !== 'after');
    document.documentElement.setAttribute('data-phase', phase);
  }

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
