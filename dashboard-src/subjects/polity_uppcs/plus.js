(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); }, $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var KEY = 'polity-uppcs-plus', side = $('#side'), scrim = $('#scrim'), q = $('#q'), last = 'home', idx = null;
  var st = { known: {}, recall: false, rep: false, weak: false, focus: false, last: 'c1' };
  try { var s0 = JSON.parse(localStorage.getItem(KEY) || '{}'); if (s0 && typeof s0 === 'object' && !Array.isArray(s0)) { for (var k in st) if (k in s0) st[k] = s0[k]; if (!st.known || typeof st.known !== 'object' || Array.isArray(st.known)) st.known = {}; } } catch (e) {}
  function save() { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {} }
  var facts = $$('.f'), total = facts.length, chs = $$('.view.ch');

  // ---------- progress ----------
  function paintKnown() {
    facts.forEach(function (f) { f.classList.toggle('known', !!st.known[f.id]); });
    var all = 0;
    chs.forEach(function (c) {
      var n = $$('.f', c).length, kn = $$('.f.known', c).length; all += kn;
      var id = c.id.slice(1), txt = kn + '/' + n;
      $$('.ring[data-ch="' + id + '"]').forEach(function (r) { r.textContent = kn === n ? '✓ ' + txt : txt; r.classList.toggle('full', kn === n); });
      var a = $('.side a[data-v="' + c.id + '"]'); if (a) a.classList.toggle('full', kn === n);
    });
    $('#sKnown').textContent = all; $('#bar').style.width = (100 * all / total) + '%'; $('#tot').textContent = all + ' / ' + total + ' known';
    markEmpty();
  }
  function markEmpty() {
    $$('.topic').forEach(function (t) {
      t.classList.toggle('e-rep', !$('.f.h1,.f.h2,.f.h3', t));
      t.classList.toggle('e-weak', !$('.f:not(.known)', t));
    });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.tk'); if (!b) return;
    var f = b.closest('.f'); if (st.known[f.id]) delete st.known[f.id]; else st.known[f.id] = 1; save(); paintKnown();
  });

  // ---------- toggles ----------
  var T = { recall: $('#tRecall'), rep: $('#tRep'), weak: $('#tWeak'), focus: $('#tFocus') };
  function applyToggles() {
    for (var k in T) { T[k].checked = !!st[k]; document.body.classList.toggle(k, !!st[k]); }
    focusPaint();
  }
  Object.keys(T).forEach(function (k) { T[k].addEventListener('change', function () { st[k] = T[k].checked; save(); applyToggles(); }); });
  document.addEventListener('click', function (e) {
    var b = e.target.closest('b'); if (b && document.body.classList.contains('recall') && b.closest('.f,.tl,.topf')) b.classList.toggle('shown');
    var t = e.target.closest('.tlb'); if (t) { var tp = t.closest('.topic'), on = !tp.classList.contains('tlon'); tp.classList.toggle('tlon', on); $('.tl', tp).hidden = !on; t.setAttribute('aria-pressed', on ? 'true' : 'false'); }
  });

  // ---------- focus mode ----------
  var fbar = $('#fbar'), fcur = 0;
  function vis(t) { var b = document.body.classList; return !(b.contains('rep') && t.classList.contains('e-rep')) && !(b.contains('weak') && t.classList.contains('e-weak')); }
  function focusPaint() {
    var c = $('.view.ch.on'), on = st.focus && !!c; fbar.hidden = !on; $$('.topic.cur').forEach(function (t) { t.classList.remove('cur'); });
    if (!on) return;
    var ts = $$('.topic', c).filter(vis); if (!ts.length) { $('#fPos').textContent = 'Nothing to show'; return; }
    fcur = Math.max(0, Math.min(fcur, ts.length - 1)); ts[fcur].classList.add('cur'); $('#fPos').textContent = 'Topic ' + (fcur + 1) + ' of ' + ts.length;
  }
  $('#fPrev').onclick = function () { fcur--; focusPaint(); window.scrollTo(0, 0); };
  $('#fNext').onclick = function () {
    var c = $('.view.ch.on'), n = $$('.topic', c).filter(vis).length;
    if (fcur >= n - 1) { var nx = $('.pn .nx', c); if (nx) location.hash = nx.getAttribute('href'); return; }
    fcur++; focusPaint(); window.scrollTo(0, 0);
  };

  // ---------- routing ----------
  function drawer(o) { side.classList.toggle('open', o); scrim.classList.toggle('on', o); }
  function show(id) {
    $$('.view').forEach(function (v) { v.classList.toggle('on', v.id === id); }); $$('.side a').forEach(function (a) { a.classList.toggle('on', a.dataset.v === id); });
    if (id !== 'results') last = id; var v = $('#' + id); document.title = (v && v.dataset.title ? v.dataset.title + ' · ' : '') + 'Polity-UPPCS Plus';
    if (/^c\d+$/.test(id)) { st.last = id; save(); var c = $('#cont'); c.href = '#' + id; c.textContent = 'Continue: ' + v.dataset.title; }
    focusPaint();
  }
  function route() {
    var h = decodeURIComponent(location.hash.slice(1)) || 'home', el = document.getElementById(h); if (!el) { h = 'home'; el = document.getElementById(h); }
    var v = el.classList.contains('view') ? el : el.closest('.view'); q.value = ''; fcur = 0;
    if (el !== v && st.focus) { var ts = $$('.topic', v).filter(vis), tp = el.closest('.topic'); if (tp && ts.indexOf(tp) >= 0) fcur = ts.indexOf(tp); }
    show(v.id); drawer(false);
    if (el === v) window.scrollTo(0, 0); else { el.scrollIntoView({ block: 'center' }); el.classList.add('flash'); setTimeout(function () { el.classList.remove('flash'); }, 1900); }
  }
  function reveal(el) { // make sure a fact is visible before jumping to it
    var ch = false; if (st.rep && !/h[123]/.test(el.className)) { st.rep = false; ch = true; } if (st.weak && el.classList.contains('known')) { st.weak = false; ch = true; }
    if (ch) { save(); applyToggles(); }
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#f"],a[href^="#c"]'); if (!a) return; var el = document.getElementById(a.getAttribute('href').slice(1)); if (el && el.classList.contains('f')) reveal(el);
  }, true);

  // ---------- search ----------
  q.addEventListener('input', function () {
    var s = q.value.trim().toLowerCase(); if (s.length < 2) { show(last); return; }
    if (!idx) idx = facts.map(function (p) { var c = p.cloneNode(true); $$('.p,.tk', c).forEach(function (x) { x.remove(); }); var t = (p.tagName === 'TR' ? $$('td', c).map(function (d) { return d.textContent; }).filter(Boolean).join(' · ') : c.textContent).replace(/\s+/g, ' ').trim(); return { el: p, t: t, l: t.toLowerCase(), w: p.closest('.view').dataset.title, hot: /h[123]/.test(p.className) }; });
    var w = s.split(/\s+/), hits = idx.filter(function (x) { return w.every(function (k) { return x.l.indexOf(k) >= 0; }); }); hits.sort(function (a, b) { return (b.hot ? 1 : 0) - (a.hot ? 1 : 0); }); hits = hits.slice(0, 80);
    $('#rt').textContent = hits.length + (hits.length === 80 ? '+' : '') + ' results';
    $('#rl').innerHTML = hits.map(function (x) { return '<a href="#' + x.el.id + '">' + x.t.replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }) + '<small>' + x.w + '</small></a>'; }).join('') || '<p>Nothing found. Try one word.</p>';
    show('results'); window.scrollTo(0, 0);
  });

  // ---------- flashcards ----------
  var DECK = JSON.parse($('#deck').textContent), order = DECK.map(function (_, i) { return i; }), pos = 0, fc = $('#fc');
  function live() { return $('#fcWeak').checked ? order.filter(function (i) { return !st.known[DECK[i].i]; }) : order; }
  function card() {
    var L = live(); if (!L.length) { $('#fcFact').textContent = 'All repeated facts are marked known.'; $('#fcMeta').textContent = ''; $('#fcPos').textContent = ''; fc.classList.remove('hide'); return null; }
    pos = (pos % L.length + L.length) % L.length; var d = DECK[L[pos]];
    $('#fcMeta').textContent = 'Chapter ' + d.c + ' · asked in ' + d.n + ' UPPSC papers'; $('#fcFact').innerHTML = d.h; fc.classList.add('hide');
    $('#fcPos').textContent = (pos + 1) + ' of ' + L.length; $('#fcOpen').href = '#' + d.i; return d;
  }
  function flip() { fc.classList.toggle('hide'); }
  fc.onclick = flip; $('#fcShow').onclick = flip; fc.onkeydown = function (e) { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); flip(); } };
  $('#fcNext').onclick = function () { pos++; card(); }; $('#fcPrev').onclick = function () { pos--; card(); };
  $('#fcKnow').onclick = function () { var L = live(); if (!L.length) return; st.known[DECK[L[pos % L.length]].i] = 1; save(); paintKnown(); if (!$('#fcWeak').checked) pos++; card(); };
  $('#fcWeak').onchange = function () { pos = 0; card(); };
  $('#fcShuf').onclick = function () { for (var i = order.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = order[i]; order[i] = order[j]; order[j] = t; } pos = 0; card(); };

  // ---------- quiz ----------
  var QZ = JSON.parse($('#quizd').textContent), qzCh = $('#qzCh'), qzL = $('#qzList'), qd = 0, qr = 0, qset = [];
  function newQuiz() {
    var pool = (QZ[qzCh.value] || []).slice(); for (var i = pool.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = pool[i]; pool[i] = pool[j]; pool[j] = t; }
    qset = pool.slice(0, 10); qd = 0; qr = 0;
    qzL.innerHTML = qset.map(function (x, n) { return '<li data-n="' + n + '"><div class="qe">' + x.e + '</div><div class="qs">' + (n + 1) + '. ' + x.s + '</div><div class="qo">' + x.o.map(function (o, j) { return '<button type="button" data-j="' + j + '">(' + 'abcde'[j] + ') ' + o + '</button>'; }).join('') + '</div><div class="qf" hidden></div></li>'; }).join('');
    score();
  }
  function score() { $('#qzScore').textContent = 'Answered ' + qd + ' of ' + qset.length + ' · correct ' + qr; }
  qzL.addEventListener('click', function (e) {
    var b = e.target.closest('.qo button'); if (!b || b.disabled) return; var li = b.closest('li'), x = qset[+li.dataset.n], j = +b.dataset.j, ok = x.k.indexOf(j) >= 0;
    $$('.qo button', li).forEach(function (o, n) { o.disabled = true; if (x.k.indexOf(n) >= 0) o.classList.add('ok'); else if (n === j) o.classList.add('no'); });
    var f = $('.qf', li); f.hidden = false; f.innerHTML = '<b>' + (ok ? 'Correct.' : 'Not correct.') + '</b> ' + x.f + (x.t ? ' <a href="#' + x.t + '">Open topic →</a>' : ''); qd++; if (ok) qr++; score();
  });
  qzCh.onchange = newQuiz; $('#qzNew').onclick = newQuiz;
  document.addEventListener('click', function (e) { var a = e.target.closest('[data-quiz]'); if (a) { qzCh.value = a.getAttribute('data-quiz'); newQuiz(); } }, true);

  // ---------- start ----------
  $('#menu').onclick = function () { drawer(!side.classList.contains('open')); }; scrim.onclick = function () { drawer(false); };
  window.addEventListener('hashchange', route);
  var c0 = document.getElementById(st.last); if (c0) { $('#cont').href = '#' + st.last; $('#cont').textContent = 'Continue: ' + c0.dataset.title; }
  paintKnown(); applyToggles(); card(); newQuiz(); route();
})();
