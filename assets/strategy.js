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
  function shrinkToFit(els) {
    /* сравнивать надо scrollWidth с clientWidth САМОГО элемента: у блочного
       элемента scrollWidth никогда не меньше его ширины, поэтому проверка
       против ширины колонки срабатывала всегда и кегль падал до минимума */
    els.forEach(function (el) { el.style.fontSize = ''; });
    var live = els.filter(function (el) { return el.clientWidth > 0; });
    if (!live.length) return;                   /* экран ещё скрыт */
    var size = parseFloat(getComputedStyle(live[0]).fontSize);
    /* нижний предел в 9px: без него подпись метрики на узкой карточке ужималась
       до 5.5px и читать её было нельзя */
    var min = Math.max(size * 0.4, 9);
    function overflows() {
      return live.some(function (el) { return el.scrollWidth > el.clientWidth; });
    }
    while (size > min && overflows()) {
      size = Math.max(min, size - 0.5);
      live.forEach(function (el) { el.style.fontSize = size + 'px'; });
      if (size <= min) break;
    }
  }
  function fitHeadings(root) {
    if (!root || !root.querySelectorAll) root = document;
    /* МОБИЛКА — отдельная вёрстка, а не ужатая настольная: подгонка кегля
       здесь не работает вовсе. Она существует, чтобы строка влезла в одну
       строку на широком экране; на телефоне тот же расчёт зажимал заголовки,
       блоки процессов и подписи кейсов до 8–10px, и всё выглядело мелким.
       На телефоне строки просто переносятся, а размеры задаёт CSS. */
    if (!mqDesk.matches) {
      $$('h1, h1 .l, h2, .biz h3, .biz-metric, .opnode, .pnode, .fnode, .node', root)
        .forEach(function (el) { el.style.fontSize = ''; });
      return;
    }
    /* строки одного заголовка ужимаются ВМЕСТЕ — иначе вторая строка выходит
       заметно мельче первой */
    $$('h1', root).forEach(function (h) {
      var lines = $$('.l', h);
      /* на мобилке строка заголовка переносится и кегль задаёт CSS: подгонка
         под nowrap в узкой колонке зажимала его до размера обычных заголовков */
      if (!mqDesk.matches) {
        lines.forEach(function (el) { el.style.fontSize = ''; });
        h.style.fontSize = '';
        return;
      }
      shrinkToFit(lines.length ? lines : [h]);
    });
    $$('h2.one-line', root).forEach(function (h) { shrinkToFit([h]); });
    /* названия кейсов и подписи метрик держим в одну строку и ОДНОГО кегля:
       иначе длинные русские подписи обрезались многоточием */
    var titles = $$('.biz h3', root);
    if (titles.length) shrinkToFit(titles);
    var metrics = $$('.biz-metric', root);
    if (metrics.length) shrinkToFit(metrics);
    /* блоки возможностей стоят такими же рядами, как цепочки на соседних
       сценах, поэтому и кегль им подбирается вместе с ними — с проверкой
       ширины всего ряда, а не каждого блока по отдельности */
    var chain = $$('.pnode, .fnode, .node, .opnode', root);
    if (chain.length) {
      shrinkToFit(chain);
      /* ряд целиком тоже не должен вылезать за колонку: у блоков nowrap, и
         переполнение видно только на самом ряду */
      var box = $('.stage-card .ui-body', root) || $('.stage-card', root);
      var rows = $$('.frow, .prow', root).filter(function (r) { return r.clientWidth > 0; });
      /* флекс-ряд не «прокручивается», поэтому переполнение ловим сравнением
         рамок ряда и панели, а не scrollWidth */
      /* Считаем по СОДЕРЖИМОМУ панели и оставляем ещё воздух по краям:
         сравнение с внешней рамкой разрешало ряду встать вплотную к ней и
         даже залезть в её падинг — цепочка почти упиралась в края (жалоба
         владельца «почти за края выходит»). */
      var AIR = 14;
      function tooWide() {
        if (!box) return false;
        var lim = box.getBoundingClientRect(), cs = getComputedStyle(box);
        var padL = parseFloat(cs.paddingLeft) || 0, padR = parseFloat(cs.paddingRight) || 0;
        var left = lim.left + padL + AIR, right = lim.right - padR - AIR;
        return rows.some(function (r) {
          var rr = r.getBoundingClientRect();
          return rr.width > right - left || rr.right > right || rr.left < left;
        });
      }
      var size = chain[0] ? parseFloat(getComputedStyle(chain[0]).fontSize) : 0;
      var min = Math.max(size * 0.6, 9);
      while (size > min && tooWide()) {
        size -= 0.5;
        chain.forEach(function (el) { el.style.fontSize = size + 'px'; });
      }
    }
  }
  fitHeadings();
  window.addEventListener('resize', fitHeadings);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitHeadings);

  /* ---------- запуск анимаций сцены ----------
     Переход НЕ стартует для элемента, который в этом же кадре был display:none —
     браузеру не от чего анимировать, и он сразу ставит конечное значение.
     Поэтому конечное состояние повешено на класс .lit, а класс ставится через
     два кадра после показа экрана. */
  function sceneIn(screen) {
    if (!screen || !screen.classList) return;
    screen.classList.remove('lit');
    if (reduce) { screen.classList.add('lit'); return; }
    void screen.offsetWidth;
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { screen.classList.add('lit'); });
    });
  }

  /* ---------- цитата печатается, когда экран показан ----------
     Владелец просил, чтобы фраза «We get most leads through the website…»
     именно набиралась, а не появлялась целиком. Печатаем один раз на экран;
     при prefers-reduced-motion текст ставится сразу. */
  var typeT;
  function typeIn(root) {
    if (!root || !root.querySelectorAll) return;
    $$('.typing[data-type]', root).forEach(function (el) {
      var out = $('.typed', el);
      if (!out) return;
      var text = el.getAttribute('data-type');
      if (reduce) { out.textContent = text; return; }
      if (el.dataset.typed === '1') return;
      el.dataset.typed = '1';
      out.textContent = '';
      var i = 0;
      clearInterval(typeT);
      typeT = setInterval(function () {
        out.textContent = text.slice(0, ++i);
        if (i >= text.length) clearInterval(typeT);
      }, 22);
    });
  }

  /* ---------- лента артефактов: растушёвка по краям ----------
     Считать её можно только на ПОКАЗАННОМ экране: у скрытого clientWidth и
     scrollWidth равны нулю, и «доскроллено до конца» срабатывало сразу — правая
     растушёвка гасла, а карточка обрезалась голым краем. */
  function paintFades(root) {
    if (!root || !root.querySelectorAll) root = document;
    $$('.rail-wrap', root).forEach(function (wrap) {
      var rail = $('.rail', wrap);
      if (!rail || !rail.clientWidth) return;
      wrap.classList.toggle('scrolled', rail.scrollLeft > 4);
      wrap.classList.toggle('ended', rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 4);
    });
  }
  $$('.rail').forEach(function (rail) {
    rail.addEventListener('scroll', function () { paintFades(rail.closest('.screen')); }, { passive: true });
  });
  window.addEventListener('resize', function () { paintFades(screens[cur]); });

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
      /* только перенос, без масштаба: блоки на всех сценах одного размера, а
         scale() визуально «раздувал» их в полёте (жалоба владельца) */
      if (Math.abs(dx) < 2 && Math.abs(dy) < 2) return;
      el.style.transition = 'none';
      el.style.opacity = '1';
      el.style.transformOrigin = 'top left';
      el.style.transform = 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px)';
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
    paintFades(screens[cur]);
    sceneIn(screens[cur]);
    typeIn(screens[cur]);
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
