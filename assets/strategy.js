/* ============================================================
   FR-SITE41 — поведение лендинга AI Strategy.
   Листание экранами устроено так же, как в биографии: экраны сменяют друг
   друга анимацией, один жест = один экран, колесо не перехватывается внутри
   прокручиваемых лент. Все тексты — в разметке, скрипт общий на оба языка.
   ============================================================ */
(function () {
  "use strict";

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var mqDesk = window.matchMedia('(min-width: 1024px)');
  var lang = document.documentElement.lang === 'ru' ? 'ru' : 'en';
  try { localStorage.setItem('ait_lang', lang); } catch (e) {}

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var deck = $('#deck');
  var screens = $$('.screen');
  var navTabs = $$('.nav-tab');
  var nav = $('#nav');
  var menuIcon = $('#menu-icon');
  var head = $('#head');
  var video = $('#head-video');
  var dotsBox = $('#dots');

  /* ---------- точки-индикаторы ---------- */
  var dots = screens.map(function (s, i) {
    var b = document.createElement('button');
    b.className = 'dot';
    b.type = 'button';
    b.setAttribute('aria-label', String(i + 1));
    b.addEventListener('click', function () { go(i); });
    dotsBox.appendChild(b);
    return b;
  });

  /* ---------- заголовки в одну строку ----------
     h2.one-line и строки заголовка первого экрана набраны с nowrap. Кегль в
     vw их не спасает: ширина колонки зависит и от масштаба, и от языка, и на
     1280–1366px строка вылезала за экран. Подбираем кегль по факту. */
  function fitHeadings(root) {
    if (!root || !root.querySelectorAll) root = document;
    $$('h2.one-line, h1 .l', root).forEach(function (el) {
      el.style.fontSize = '';
      var box = el.closest('.wrap') || el.parentElement;
      var room = box.clientWidth - 2;
      if (room <= 0) return;
      var size = parseFloat(getComputedStyle(el).fontSize);
      var min = size * 0.55;
      while (size > min && el.scrollWidth > room) {
        size -= 0.5;
        el.style.fontSize = size + 'px';
      }
    });
  }
  fitHeadings();
  window.addEventListener('resize', fitHeadings);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitHeadings);

  /* ---------- лента артефактов: левая растушёвка только после прокрутки ---------- */
  $$('.rail-wrap').forEach(function (wrap) {
    var rail = $('.rail', wrap);
    if (!rail) return;
    function paintFade() {
      wrap.classList.toggle('scrolled', rail.scrollLeft > 4);
      wrap.classList.toggle('ended', rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 4);
    }
    rail.addEventListener('scroll', paintFade, { passive: true });
    window.addEventListener('resize', paintFade);
    paintFade();
  });

  /* ---------- перелёт оранжевых блоков между шагами 03 → 04 → 05 ----------
     Считаем позиции через offsetLeft/offsetTop: смещения не зависят от transform,
     которым экран въезжает, поэтому FLIP получается точным. Ключ data-flip="oN"
     нумерует оранжевые (человеческие) блоки по порядку внутри каждой сцены. */
  var FLIP_MS = 760;
  var FLIP_EASE = 'cubic-bezier(0.65, 0.02, 0.25, 1)';
  function offsetIn(el, root) {
    var x = 0, y = 0, n = el;
    while (n && n !== root) { x += n.offsetLeft; y += n.offsetTop; n = n.offsetParent; }
    return { x: x, y: y, w: el.offsetWidth, h: el.offsetHeight };
  }
  function captureFlip(screen) {
    if (!screen || !screen.classList.contains('step-screen')) return null;
    var map = null;
    $$('[data-flip]', screen).forEach(function (el) {
      (map = map || {})[el.getAttribute('data-flip')] = offsetIn(el, screen);
    });
    return map;
  }
  function playFlip(screen, from) {
    if (!from || !screen || !screen.classList.contains('step-screen')) return false;
    var moved = [];
    $$('[data-flip]', screen).forEach(function (el) {
      var was = from[el.getAttribute('data-flip')];
      if (!was) return;
      var now = offsetIn(el, screen);
      var dx = was.x - now.x, dy = was.y - now.y;
      var sx = now.w ? was.w / now.w : 1, sy = now.h ? was.h / now.h : 1;
      if (Math.abs(dx) < 2 && Math.abs(dy) < 2 && Math.abs(sx - 1) < 0.02 && Math.abs(sy - 1) < 0.02) return;
      el.style.transition = 'none';
      el.style.opacity = '1';
      el.style.transformOrigin = 'top left';
      el.style.transform = 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px) scale(' +
        sx.toFixed(3) + ',' + sy.toFixed(3) + ')';
      el.style.zIndex = '3';
      el.classList.add('flying');
      moved.push(el);
    });
    if (!moved.length) return false;
    deck.classList.add('morph');
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        moved.forEach(function (el) {
          el.style.transition = 'transform ' + FLIP_MS + 'ms ' + FLIP_EASE;
          el.style.transform = '';
        });
      });
    });
    clearTimeout(flipT);
    flipT = setTimeout(function () {
      deck.classList.remove('morph');
      moved.forEach(function (el) {
        el.classList.remove('flying');
        el.style.transition = el.style.transform = el.style.transformOrigin = '';
        el.style.opacity = el.style.zIndex = '';
      });
    }, FLIP_MS + 120);
    return true;
  }

  /* ---------- переключение экранов ---------- */
  var cur = 0, swapT, enterT, flipT, busy = false;
  function paint() {
    screens.forEach(function (s, i) { s.classList.toggle('active', i === cur); });
    var chapter = screens[cur].getAttribute('data-chapter');
    navTabs.forEach(function (t) { t.classList.toggle('active', t.getAttribute('data-go') === chapter); });
    dots.forEach(function (d, i) { d.classList.toggle('on', i === cur); });
    screens[cur].scrollTop = 0;
    fitHeadings(screens[cur]);
    countUpIn(screens[cur]);
  }
  function go(i) {
    if (i < 0 || i >= screens.length || i === cur || busy) return;
    closeMenu();
    busy = true;
    clearTimeout(swapT); clearTimeout(enterT);
    if (reduce) { cur = i; paint(); busy = false; return; }
    /* соседние шаги процесса связаны перелётом блоков, а не сменой экрана */
    var from = Math.abs(i - cur) === 1 && screens[i].classList.contains('step-screen')
      ? captureFlip(screens[cur]) : null;
    deck.classList.add('leaving');
    if (from) deck.classList.add('morph-out');
    swapT = setTimeout(function () {
      cur = i;
      paint();
      deck.classList.remove('leaving');
      deck.classList.remove('morph-out');
      if (!playFlip(screens[cur], from)) deck.classList.add('entering');
      enterT = setTimeout(function () { deck.classList.remove('entering'); busy = false; }, 520);
    }, 240);
  }
  function step(dir) { go(cur + dir); }
  function goChapter(key) {
    for (var i = 0; i < screens.length; i++) {
      if (screens[i].getAttribute('data-chapter') === key) { go(i); return; }
    }
  }

  /* цифры набегают один раз, когда экран показан */
  function countUpIn(screen) {
    if (reduce) return;
    $$('.num-val, .idx-val', screen).forEach(function (el) {
      if (el.dataset.done) return;
      var m = /^(\D*)([\d.]+)([\s\S]*)$/.exec(el.textContent.trim());
      if (!m) return;
      var pre = m[1], target = parseFloat(m[2]), post = m[3];
      var decimals = (m[2].split('.')[1] || '').length;
      if (!isFinite(target) || target < 2) return;
      el.dataset.done = '1';
      var t0 = 0, dur = 1100;
      requestAnimationFrame(function tick(ts) {
        if (!t0) t0 = ts;
        var p = Math.min(1, (ts - t0) / dur);
        el.textContent = pre + (target * (1 - Math.pow(1 - p, 3))).toFixed(decimals) + post;
        if (p < 1) requestAnimationFrame(tick);
      });
    });
  }

  /* ---------- колесо, свайп, клавиши ---------- */
  function innerScroll(node, horizontal) {
    while (node && node !== document.body) {
      if (node.nodeType === 1) {
        var span = horizontal ? (node.scrollWidth - node.clientWidth) : (node.scrollHeight - node.clientHeight);
        if (span > 4) {
          var ov = getComputedStyle(node)[horizontal ? 'overflowX' : 'overflowY'];
          if (ov === 'auto' || ov === 'scroll') return node;
        }
      }
      node = node.parentElement;
    }
    return null;
  }
  var lastWheel = 0;
  window.addEventListener('wheel', function (e) {
    if (nav.classList.contains('open')) return;
    var sc = innerScroll(e.target, false);
    if (sc) {
      var canDown = sc.scrollTop + sc.clientHeight < sc.scrollHeight - 2;
      var canUp = sc.scrollTop > 2;
      if ((e.deltaY > 0 && canDown) || (e.deltaY < 0 && canUp)) return;
    }
    if (Math.abs(e.deltaY) < 30) return;
    var now = Date.now();
    if (now - lastWheel < 900) return;    /* один жест = один экран */
    lastWheel = now;
    step(e.deltaY > 0 ? 1 : -1);
  }, { passive: true });

  var ty = null, tx = null, lastSwipe = 0;
  window.addEventListener('touchstart', function (e) {
    if (e.touches && e.touches[0]) { ty = e.touches[0].clientY; tx = e.touches[0].clientX; }
  }, { passive: true });
  window.addEventListener('touchend', function (e) {
    if (nav.classList.contains('open') || ty == null) return;
    var t = e.changedTouches && e.changedTouches[0];
    if (!t) return;
    var dy = t.clientY - ty, dx = t.clientX - tx;
    if (Math.abs(dy) < 45 || Math.abs(dx) > Math.abs(dy)) return;
    var sc = innerScroll(e.target, false);
    if (sc) {
      var canDown = sc.scrollTop + sc.clientHeight < sc.scrollHeight - 2;
      var canUp = sc.scrollTop > 2;
      if ((dy < 0 && canDown) || (dy > 0 && canUp)) return;
    }
    var now = Date.now();
    if (now - lastSwipe < 700) return;
    lastSwipe = now;
    step(dy < 0 ? 1 : -1);
  }, { passive: true });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closeMenu(); return; }
    if (nav.classList.contains('open')) return;
    if (e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === ' ') { e.preventDefault(); step(1); }
    else if (e.key === 'ArrowUp' || e.key === 'PageUp') { e.preventDefault(); step(-1); }
    else if (e.key === 'Home') { go(0); }
    else if (e.key === 'End') { go(screens.length - 1); }
  });

  /* ---------- меню ---------- */
  function openMenu() { nav.classList.add('open'); menuIcon.className = 'fa-solid fa-xmark'; }
  function closeMenu() { nav.classList.remove('open'); menuIcon.className = 'fa-solid fa-bars'; }
  $('#menu-btn').addEventListener('click', function () {
    nav.classList.contains('open') ? closeMenu() : openMenu();
  });
  var navClose = $('#nav-close');
  if (navClose) navClose.addEventListener('click', closeMenu);
  $$('[data-go]').forEach(function (el) {
    el.addEventListener('click', function () { goChapter(el.getAttribute('data-go')); });
  });

  /* «Назад» — обычная ссылка на главную, по овалу на каждом экране; скрипту
     тут делать нечего (правка владельца: стрелка всегда ведёт на главную) */

  /* ---------- лицо: звук по клику; на мобилке кружок ещё и перетаскивается ---------- */
  function setPlaying(on) {
    if (!video) return;
    video.muted = !on;
    head.classList.toggle('playing', on);
    var mic = $('#head-mic');
    if (mic) mic.className = on ? 'fa-solid fa-microphone-lines' : 'fa-solid fa-microphone-lines-slash';
    var p = video.play && video.play();
    if (p && p.catch) p.catch(function () {});
  }
  var POS_KEY = 'ait_strategy_head';
  var drag = null;
  function applyPos(p) {
    if (!p || mqDesk.matches) return;
    head.style.left = p.x + 'px';
    head.style.top = p.y + 'px';
    head.style.bottom = 'auto';
  }
  function savedPos() { try { return JSON.parse(localStorage.getItem(POS_KEY)); } catch (e) { return null; } }
  if (head) {
    head.addEventListener('pointerdown', function (e) {
      if (mqDesk.matches) return;
      var r = head.getBoundingClientRect();
      drag = { dx: e.clientX - r.left, dy: e.clientY - r.top, moved: 0, w: r.width, h: r.height };
      head.setPointerCapture(e.pointerId);
    });
    head.addEventListener('pointermove', function (e) {
      if (!drag) return;
      var x = Math.min(window.innerWidth - drag.w - 8, Math.max(8, e.clientX - drag.dx));
      var y = Math.min(window.innerHeight - drag.h - 8, Math.max(8, e.clientY - drag.dy));
      drag.moved += Math.abs(e.movementX) + Math.abs(e.movementY);
      applyPos({ x: x, y: y });
      drag.last = { x: x, y: y };
    });
    head.addEventListener('pointerup', function () {
      if (drag && drag.moved < 6) setPlaying(video.muted);
      else if (drag && drag.last) { try { localStorage.setItem(POS_KEY, JSON.stringify(drag.last)); } catch (err) {} }
      drag = null;
    });
    head.addEventListener('click', function () { if (mqDesk.matches) setPlaying(video.muted); });
    head.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setPlaying(video.muted); }
    });
  }
  setPlaying(false);
  if (!mqDesk.matches) applyPos(savedPos());

  paint();
})();
