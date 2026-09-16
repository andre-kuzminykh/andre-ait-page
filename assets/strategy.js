/* ============================================================
   FR-SITE41 — поведение лендинга Andre AI Strategy.
   Один скрипт на обе языковые версии: все тексты лежат в разметке,
   язык страницы приходит из <html lang> (им же синхронизируем ait_lang).

   Правило спеки: НИКАКОГО перехвата прокрутки. Всё, что «играет»,
   привязано к обычному скроллу: листаешь быстрее — анимация идёт быстрее.
   ============================================================ */
(function () {
  "use strict";

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var mqDesk = window.matchMedia('(min-width: 1024px)');
  var lang = document.documentElement.lang === 'ru' ? 'ru' : 'en';
  try { localStorage.setItem('ait_lang', lang); } catch (e) {}

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------- шапка: фон появляется, когда ушли с первого экрана ---------- */
  var header = $('header');
  var head = $('#head');
  var progress = $('#progress');

  /* ---------- появление блоков каскадом (как на /about/) ---------- */
  function countUp(el, delay) {
    if (!el || reduce) return;
    var m = /^(\D*)(\d+)([\s\S]*)$/.exec(el.textContent.trim());
    if (!m) return;
    var pre = m[1], target = parseInt(m[2], 10), post = m[3];
    if (!isFinite(target) || target < 2) return;
    var t0 = 0, dur = 1200;
    setTimeout(function () {
      requestAnimationFrame(function step(ts) {
        if (!t0) t0 = ts;
        var p = Math.min(1, (ts - t0) / dur);
        el.textContent = pre + Math.round(target * (1 - Math.pow(1 - p, 3))) + post;
        if (p < 1) requestAnimationFrame(step);
      });
    }, delay + 140);
  }

  function reveal(el, delay) {
    if (delay) el.style.setProperty('--d', delay + 'ms');
    el.classList.add('in');
    var num = el.querySelector('.num-val');
    if (num) countUp(num, delay);
    setTimeout(function () { el.style.removeProperty('--d'); el.classList.add('done'); }, 760 + delay);
  }

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.filter(function (e) { return e.isIntersecting; })
        .sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; })
        .forEach(function (e, i) {
          io.unobserve(e.target);
          reveal(e.target, reduce ? 0 : Math.min(i, 5) * 60);
        });
    }, { rootMargin: '0px 0px -4% 0px', threshold: 0.01 });
    $$('.reveal').forEach(function (el) { io.observe(el); });
  } else {
    $$('.reveal').forEach(function (el) { el.classList.add('in', 'done'); });
  }

  /* ---------- HERO: фразы, которые «звучат» рядом с Андре ---------- */
  var phrases = $$('.phrase');
  if (phrases.length && !reduce) {
    var pi = -1;
    var cycle = function () {
      if (document.body.classList.contains('mini-head')) { setTimeout(cycle, 1200); return; }
      if (pi >= 0) phrases[pi].classList.remove('on');
      pi = (pi + 1) % phrases.length;
      phrases[pi].classList.add('on');
      /* на ответе задерживаемся дольше: это вывод всей сцены */
      setTimeout(cycle, phrases[pi].classList.contains('answer') ? 3200 : 2000);
    };
    setTimeout(cycle, 900);
  } else {
    phrases.forEach(function (p, i) { if (i === phrases.length - 1) p.classList.add('on'); });
  }

  /* ---------- Голова: колонка → кружок, звук по клику ---------- */
  var video = $('#head-video');
  function setPlaying(on) {
    if (!video) return;
    video.muted = !on;
    head.classList.toggle('playing', on);
    var mic = $('#head-mic');
    if (mic) mic.className = on ? 'fa-solid fa-microphone-lines' : 'fa-solid fa-microphone-lines-slash';
    var p = video.play && video.play();
    if (p && p.catch) p.catch(function () {});
  }
  /* Кружок перетаскивается (как на страницах лекций): он неизбежно накрывает
     часть текста, и правило владельца — «пусть двигают куда хотят».
     Место запоминаем; клик от перетаскивания отличаем по пройденному пути. */
  var POS_KEY = 'ait_strategy_head';
  var drag = null;
  function applyPos(p) {
    if (!p || !head.classList.contains('mini')) return;
    head.style.left = p.x + 'px';
    head.style.top = p.y + 'px';
    head.style.bottom = 'auto';
  }
  function savedPos() { try { return JSON.parse(localStorage.getItem(POS_KEY)); } catch (e) { return null; } }
  if (head) {
    head.addEventListener('pointerdown', function (e) {
      if (!head.classList.contains('mini')) return;
      var r = head.getBoundingClientRect();
      drag = { dx: e.clientX - r.left, dy: e.clientY - r.top, moved: 0, w: r.width, h: r.height };
      head.setPointerCapture(e.pointerId);
      head.style.transition = 'none';
    });
    head.addEventListener('pointermove', function (e) {
      if (!drag) return;
      var x = Math.min(window.innerWidth - drag.w - 8, Math.max(8, e.clientX - drag.dx));
      var y = Math.min(window.innerHeight - drag.h - 8, Math.max(8, e.clientY - drag.dy));
      drag.moved += Math.abs(e.movementX) + Math.abs(e.movementY);
      applyPos({ x: x, y: y });
      drag.last = { x: x, y: y };
    });
    head.addEventListener('pointerup', function (e) {
      head.style.transition = '';
      if (drag && drag.moved < 6) setPlaying(video.muted);          /* это был клик */
      else if (drag && drag.last) { try { localStorage.setItem(POS_KEY, JSON.stringify(drag.last)); } catch (err) {} }
      drag = null;
    });
    head.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setPlaying(video.muted); }
    });
  }

  /* ---------- Секция вопросов: кадр выбирается положением скролла ---------- */
  var qs = $('#questions');
  var qItems = $$('.q-item');
  var qDots = $$('.qs-dot');
  var qFinal = $('.qs-final');
  var qHead = $('.qs-head');
  function tickQuestions() {
    if (!qs || !qItems.length) return;
    var r = qs.getBoundingClientRect();
    var span = r.height - window.innerHeight;
    var p = span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 0;
    /* первые 12% — заголовок, последние 22% — итоговая строка */
    var qZone = (p - 0.12) / 0.66;
    var idx = Math.floor(qZone * qItems.length);
    var showFinal = p > 0.80;
    qItems.forEach(function (el, i) {
      el.classList.toggle('on', !showFinal && i === idx && qZone >= 0 && qZone < 1);
      el.classList.toggle('gone', !showFinal && i < idx);
    });
    qDots.forEach(function (d, i) { d.classList.toggle('on', showFinal || i <= idx); });
    if (qFinal) qFinal.classList.toggle('on', showFinal);
    if (qHead) {
      var fade = showFinal || qZone > 0.1;
      qHead.style.opacity = fade ? 0 : 1;
      qHead.style.transform = fade ? 'translateY(-18px)' : 'none';
    }
  }

  /* ---------- Обещание: понятия появляются и схлопываются в один узел ---------- */
  var orbit = $('#orbit');
  var chips = $$('.orbit-chip');
  if (orbit && chips.length) {
    /* раскладываем по кругу один раз: в разметке только тексты */
    chips.forEach(function (c, i) {
      var a = (-Math.PI / 2) + (i / chips.length) * Math.PI * 2;
      c.style.left = (50 + Math.cos(a) * 36) + '%';
      c.style.top = (50 + Math.sin(a) * 38) + '%';
    });
  }
  function tickOrbit() {
    if (!orbit) return;
    var r = orbit.getBoundingClientRect();
    var vh = window.innerHeight;
    var p = 1 - (r.top - vh * 0.25) / (vh * 0.7);
    chips.forEach(function (c, i) { c.classList.toggle('on', p > 0.12 + i * 0.07); });
    orbit.classList.toggle('collapsed', p > 0.95);
  }

  /* ---------- 10 шагов: сцена меняется, номер подсвечивается ---------- */
  var steps = $$('.story-step');
  var stages = $$('.stage-card');
  var railNs = $$('.rail-n');
  var activeStep = 0;
  function setStep(n) {
    if (n === activeStep) return;
    activeStep = n;
    /* на мобилке сцены стоят в потоке и включаются своим наблюдателем —
       иначе этот перебор гасил бы все, кроме текущей */
    if (mqDesk.matches) stages.forEach(function (s) { s.classList.toggle('on', +s.getAttribute('data-step') === n); });
    railNs.forEach(function (b) { b.classList.toggle('on', +b.getAttribute('data-step') === n); });
    var stage = stages.filter(function (s) { return +s.getAttribute('data-step') === n; })[0];
    if (stage && mqDesk.matches) playStage(stage);
  }
  /* внутри сцены есть свои маленькие «включения» (AS-IS → TO-BE и т.п.) */
  function playStage(stage) {
    if (reduce) { stage.classList.add('played'); return; }
    stage.classList.remove('played');
    var seq = $$('[data-seq]', stage);
    seq.forEach(function (el, i) {
      el.style.transitionDelay = (i * 110) + 'ms';
      el.style.animationDelay = (i * 110) + 'ms';
    });
    var morph = stage.querySelector('[data-transform]');
    if (morph) {
      clearTimeout(stage._t);
      morph.classList.remove('to-be');
      stage._t = setTimeout(function () { morph.classList.add('to-be'); }, 1500);
    }
  }
  function tickSteps() {
    if (!steps.length) return;
    var mid = window.innerHeight * (mqDesk.matches ? 0.5 : 0.35);
    var cur = 1;
    steps.forEach(function (s) {
      var r = s.getBoundingClientRect();
      if (r.top <= mid) cur = +s.getAttribute('data-step');
    });
    setStep(cur);
  }
  /* на мобилке сцены идут в потоке между шагами — включаем по входу в экран */
  if (!mqDesk.matches && 'IntersectionObserver' in window) {
    var sio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('on');
        playStage(e.target);
        sio.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.15 });
    stages.forEach(function (s) { sio.observe(s); });
  }

  railNs.forEach(function (b) {
    b.addEventListener('click', function () {
      var t = steps.filter(function (s) { return s.getAttribute('data-step') === b.getAttribute('data-step'); })[0];
      if (t) t.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
    });
  });

  /* ---------- Финальный экран: строки выходят по очереди ---------- */
  var finalSec = $('#start');
  var finalLines = $$('.final-line');
  var flowItems = $$('.flow span');
  function tickFinal() {
    if (!finalSec) return;
    var r = finalSec.getBoundingClientRect();
    var p = 1 - (r.top - window.innerHeight * 0.1) / (window.innerHeight * 0.75);
    finalLines.forEach(function (l, i) { l.classList.toggle('on', p > 0.1 + i * 0.16); });
    flowItems.forEach(function (f, i) { f.classList.toggle('on', p > 0.55 + i * 0.05); });
  }

  /* ---------- активный пункт меню ---------- */
  var navTabs = $$('.nav-tab');
  var sections = navTabs.map(function (t) { return document.getElementById(t.getAttribute('data-go')); });
  function tickNav() {
    var best = 0, bestTop = -Infinity;
    sections.forEach(function (s, i) {
      if (!s) return;
      var top = s.getBoundingClientRect().top - window.innerHeight * 0.3;
      if (top <= 0 && top > bestTop) { bestTop = top; best = i; }
    });
    navTabs.forEach(function (t, i) { t.classList.toggle('active', i === best); });
  }

  /* ---------- общий тик прокрутки ---------- */
  var pending = false;
  function onScroll() {
    pending = false;
    var doc = document.documentElement;
    var max = doc.scrollHeight - window.innerHeight;
    var y = window.pageYOffset || doc.scrollTop;
    if (progress) progress.style.width = (max > 0 ? Math.min(100, (y / max) * 100) : 0) + '%';
    if (header) header.classList.toggle('solid', y > window.innerHeight * 0.75);
    var mini = y > window.innerHeight * 0.72;
    document.body.classList.toggle('mini-head', mini);
    if (head && head.classList.contains('mini') !== mini) {
      head.classList.toggle('mini', mini);
      if (mini) applyPos(savedPos());
      else { head.style.left = ''; head.style.top = ''; head.style.bottom = ''; }
    }
    tickQuestions();
    tickOrbit();
    tickSteps();
    tickFinal();
    tickNav();
  }
  function queue() { if (!pending) { pending = true; requestAnimationFrame(onScroll); } }
  window.addEventListener('scroll', queue, { passive: true });
  window.addEventListener('resize', queue);

  /* ---------- меню, «назад», аккордеон, магнитные кнопки ---------- */
  var nav = $('#nav');
  var menuIcon = $('#menu-icon');
  function closeMenu() { nav.classList.remove('open'); menuIcon.className = 'fa-solid fa-bars'; document.body.style.overflow = ''; }
  $('#menu-btn').addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    menuIcon.className = open ? 'fa-solid fa-xmark' : 'fa-solid fa-bars';
    document.body.style.overflow = open ? 'hidden' : '';
  });
  var navClose = $('#nav-close');
  if (navClose) navClose.addEventListener('click', closeMenu);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });
  navTabs.forEach(function (t) {
    t.addEventListener('click', function () {
      var el = document.getElementById(t.getAttribute('data-go'));
      closeMenu();
      if (el) el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    });
  });
  $$('[data-go-hero]').forEach(function (b) {
    b.addEventListener('click', function () {
      var el = document.getElementById(b.getAttribute('data-go-hero'));
      if (el) el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    });
  });

  var back = $('#back-btn');
  if (back) back.addEventListener('click', function () {
    if (document.referrer && history.length > 1) history.back(); else location.href = '/';
  });
  $$('.acc-btn').forEach(function (b) {
    b.addEventListener('click', function () { b.parentElement.classList.toggle('open'); });
  });
  /* лёгкая «магнитность» кнопок — только на вебе и только с мышью */
  if (mqDesk.matches && !reduce && matchMedia('(hover:hover)').matches) {
    $$('.btn-primary').forEach(function (b) {
      b.addEventListener('mousemove', function (e) {
        var r = b.getBoundingClientRect();
        b.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * 0.12).toFixed(1) + 'px,' +
                            ((e.clientY - r.top - r.height / 2) * 0.18).toFixed(1) + 'px)';
      });
      b.addEventListener('mouseleave', function () { b.style.transform = ''; });
    });
  }

  onScroll();
  setStep(1);
})();
