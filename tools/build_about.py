# -*- coding: utf-8 -*-
"""Собирает биографию на двух языках из одного шаблона.

    python3 tools/build_about.py     # пишет about/index.html и about/ru/index.html

Страница листается ЭКРАНАМИ, как лендинг /ai-strategy/ и главная: внутри
экрана НИЧЕГО не прокручивается, поэтому длинная глава разрезана на несколько
коротких экранов. Меню глав при этом осталось из шести пунктов: экраны одной
главы помечены одинаковым data-chapter, и пункт меню ведёт на первый из них.

Вёрстка — assets/about.css, тексты — tools/about_copy.py.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://andre.technology"
PATH_EN = "/about/"
PATH_RU = "/about/ru/"

LOGO = ("https://i.ibb.co/gn7SmgY/"
        "866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png")

PURPLE = "#8854F3"
ORANGE = "#F97316"

# Главы: ключ, иконка меню, цвет. Порядок = порядок экранов.
CHAPTERS = [
    ("childhood", "fa-paw",            ORANGE),
    ("education", "fa-graduation-cap", PURPLE),
    ("career",    "fa-coins",          ORANGE),
    ("startups",  "fa-rocket",         PURPLE),
    ("ecosystem", "fa-microchip",      ORANGE),
    ("mission",   "fa-star",           PURPLE),
]
CH_COLOR = dict((k, c) for k, _i, c in CHAPTERS)

SOCIALS = [
    ("https://t.me/andre_dataist", "Telegram", "fa-brands fa-telegram", "#2AABEE"),
    ("https://dataist.ai/", "Website", "fa-solid fa-globe", PURPLE),
    ("https://www.youtube.com/@andre_dataist", "YouTube", "fa-brands fa-youtube", "#FF0000"),
    ("https://www.linkedin.com/in/andre-kuzminykh/", "LinkedIn", "fa-brands fa-linkedin", "#0a66c2"),
    ("mailto:admin@andre.technology", "Email", "fa-solid fa-envelope", ORANGE),
]

# ── Экраны ───────────────────────────────────────────────────────────────
# Каждый экран: глава, знак главы на фоне (иконка + наклон), иконка заголовка
# и список блоков. Ключи блоков — из tools/about_copy.py.
# Правило владельца: внутри экрана не листать, поэтому блоков мало и они
# короткие. Одна глава — несколько экранов подряд.
SCREENS = [
    # ── детство ──
    dict(ch="childhood", wm=("tiger", "-7deg"), blocks=[
        ("eyebrow", "eyebrow"), ("h1", "h1"), ("lead", "c1_lead"), ("p", "c1_p1")]),
    dict(ch="childhood", wm=("fa-chess-knight", "8deg"), ic="fa-chess-knight", blocks=[
        ("h2", "c2_head"), ("p", "c2_p1"), ("p", "c2_p2"), ("quote", "c2_quote")]),
    dict(ch="childhood", wm=("fa-helmet-safety", "-5deg"), ic="fa-road", blocks=[
        ("h2", "c3_head"), ("p", "c3_p1"), ("facts", "c3_facts")]),
    # ── образование ──
    dict(ch="education", wm=("fa-graduation-cap", "8deg"), ic="fa-graduation-cap", blocks=[
        ("h2", "e1_head"), ("lead", "e1_lead"), ("facts", "e1_facts")]),
    dict(ch="education", wm=("fa-microscope", "-6deg"), ic="fa-microscope", blocks=[
        ("h2", "e2_head"), ("p", "e2_p1"), ("p", "e2_p2"), ("note-o", "e2_note")]),
    # ── карьера ──
    dict(ch="career", wm=("fa-coins", "6deg"), ic="fa-chart-line", blocks=[
        ("h2", "k1_head"), ("p", "k1_p1"), ("p", "k1_p2")]),
    dict(ch="career", wm=("fa-building-columns", "-6deg"), ic="fa-building-columns", blocks=[
        ("h2", "k2_head"), ("p", "k2_p1"), ("stat", "k2_stat")]),
    dict(ch="career", wm=("fa-door-open", "7deg"), ic="fa-door-open", blocks=[
        ("h2", "k3_head"), ("p", "k3_p1"), ("p", "k3_p2"), ("p", "k3_p3"), ("quote", "k3_quote")]),
    # ── стартапы ──
    dict(ch="startups", wm=("fa-rocket", "12deg"), ic="fa-rocket", blocks=[
        ("h2", "s1_head"), ("p", "s1_p1"), ("p", "s1_p2")]),
    dict(ch="startups", wm=("fa-flask", "-8deg"), ic="fa-flask", blocks=[
        ("h2", "s2_head"), ("facts", "s2_facts"), ("stat", "s2_stat")]),
    dict(ch="startups", wm=("fa-user-gear", "6deg"), ic="fa-user-gear", blocks=[
        ("h2", "s3_head"), ("p", "s3_p1"), ("p", "s3_p2"), ("p", "s3_p3")]),
    dict(ch="startups", wm=("fa-lightbulb", "-10deg"), ic="fa-lightbulb", blocks=[
        ("h2", "s4_head"), ("note", "s4_note"), ("p", "s4_p1")]),
    # ── экосистема ──
    dict(ch="ecosystem", wm=("fa-microchip", "-9deg"), ic="fa-microchip", blocks=[
        ("h2", "x1_head"), ("p", "x1_p1"), ("p", "x1_p2"), ("cards", "x1_cards")]),
    dict(ch="ecosystem", wm=("fa-scale-balanced", "7deg"), ic="fa-scale-balanced", blocks=[
        ("h2", "x2_head"), ("note-o", "x2_note"), ("p", "x2_p1"), ("stat", "x2_stat")]),
    dict(ch="ecosystem", wm=("fa-diagram-project", "-7deg"), ic="fa-diagram-project", blocks=[
        ("h2", "x3_head"), ("p", "x3_p1"), ("p", "x3_p2"), ("note", "x3_note")]),
    dict(ch="ecosystem", wm=("fa-robot", "8deg"), ic="fa-robot", blocks=[
        ("h2", "x4_head"), ("p", "x4_p1"), ("facts-grid", "x4_facts")]),
    # ── миссия ──
    dict(ch="mission", wm=("fa-people-group", "-6deg"), ic="fa-people-group", blocks=[
        ("h2", "m1_head"), ("p", "m1_p1"), ("p", "m1_p2")]),
    dict(ch="mission", wm=("fa-star", "9deg"), ic="fa-star", blocks=[
        ("h2", "m2_head"), ("p", "m2_p1"), ("p", "m2_p2"), ("p", "m2_p3")]),
    dict(ch="mission", wm=("fa-flag-checkered", "-8deg"), cls=" final", blocks=[
        ("finale", "finale"), ("foot", None)]),
]


def socials(cls="nav-social"):
    out = ['<div class="%s">' % cls]
    for href, label, icon, brand in SOCIALS:
        ext = "" if href.startswith("mailto:") else ' target="_blank" rel="noopener"'
        out.append('<a class="social" href="%s"%s aria-label="%s" style="--brand:%s;">'
                   '<i class="%s"></i></a>' % (href, ext, label, brand, icon))
    out.append('</div>')
    return "\n          ".join(out)


def block_html(kind, key, c, screen):
    """Один блок экрана. Всё, кроме первого экрана, выезжает по .reveal."""
    color = CH_COLOR[screen["ch"]]
    if kind == "eyebrow":
        return '<p class="eyebrow hero-rise">%s</p>' % c[key]
    if kind == "h1":
        return '<h1 class="hero-rise">%s</h1>' % c[key]
    if kind == "h2":
        return ('<h2 class="reveal" style="--ic:%s;"><i class="fa-solid %s"></i>%s</h2>'
                % (color, screen["ic"], c[key]))
    if kind == "lead":
        return '<p class="lead reveal">%s</p>' % c[key]
    if kind == "p":
        return '<p class="reveal">%s</p>' % c[key]
    if kind == "quote":
        return '<div class="quote reveal"><p>%s</p></div>' % c[key]
    if kind in ("note", "note-o"):
        cls = "note o" if kind == "note-o" else "note"
        return '<div class="%s reveal"><p>%s</p></div>' % (cls, c[key])
    if kind == "stat":
        num, text = c[key]
        return ('<div class="stat reveal"><span class="stat-num">%s</span><p>%s</p></div>'
                % (num, text))
    if kind in ("facts", "facts-grid"):
        cls = "facts grid" if kind == "facts-grid" else "facts"
        items = "\n        ".join(
            '<li><i class="fa-solid %s"></i><span>%s</span></li>' % (ic, text)
            for ic, text in c[key])
        return '<ul class="%s reveal">\n        %s\n      </ul>' % (cls, items)
    if kind == "cards":
        items = []
        for ic, head, text, mod in c[key]:
            items.append('<div class="card%s">\n          <h3><i class="fa-solid %s"></i>%s</h3>'
                         '\n          <p>%s</p>\n        </div>'
                         % ((" " + mod) if mod else "", ic, head, text))
        return '<div class="cards reveal">\n        %s\n      </div>' % "\n        ".join(items)
    if kind == "finale":
        return ('<div class="finale reveal">\n        <p>%s</p>\n        '
                '<a class="btn-white" href="https://maturity.andre.technology/" rel="noopener">'
                '%s <i class="fa-solid fa-arrow-right"></i></a>\n      </div>'
                % (c["finale"], c["finale_btn"]))
    if kind == "foot":
        return ('<div class="foot">\n          %s\n          '
                '<p class="nav-copy">2026 &copy; Andre AI Technologies LTD</p>\n        </div>'
                % socials())
    raise ValueError("неизвестный блок: " + kind)


def screen_html(i, s, c):
    icon, rot = s["wm"]
    if icon == "tiger":
        mark = '<svg><use href="#ic-tiger"></use></svg>'
    else:
        mark = '<i class="fa-solid %s"></i>' % icon
    parts = ['<div class="wm" style="--rot: %s;" aria-hidden="true">%s</div>' % (rot, mark)]
    for kind, key in s["blocks"]:
        parts.append(block_html(kind, key, c, s))
    return ('      <section class="screen%s%s" data-i="%d" data-chapter="%s"%s>\n        %s\n'
            '      </section>'
            % (" active" if i == 0 else "", s.get("cls", ""), i, s["ch"],
               ' id="top"' if i == 0 else "",
               "\n        ".join(parts)))


def nav_html(c):
    out = ['<a class="nav-home" href="/" aria-label="%s" data-label="%s">'
           '<i class="fa-solid fa-house"></i></a>' % (c["home"], c["home"])]
    for n, (key, icon, color) in enumerate(CHAPTERS):
        if n:
            out.append('<span class="nav-divider" aria-hidden="true">|</span>')
        out.append('<button class="nav-tab%s" data-chapter="%s" style="--ul:%s; --hover:%s; --ic:%s;">'
                   '<span class="nav-ic"><i class="fa-solid %s"></i></span>'
                   '<span class="nav-label">%s</span>'
                   '<span class="nav-go"><i class="fa-solid fa-arrow-right"></i></span></button>'
                   % (" active" if n == 0 else "", key, color, color, color, icon, c["nav"][key]))
    return "\n        ".join(out)


JS = r"""
(function () {
  "use strict";
  var LANG_KEY = 'ait_lang';
  var LANG = document.documentElement.lang === 'ru' ? 'ru' : 'en';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var mqDesktop = window.matchMedia('(min-width: 1024px)');
  var article = document.querySelector('.article');
  var screens = Array.prototype.slice.call(document.querySelectorAll('.screen'));
  var navTabs = Array.prototype.slice.call(document.querySelectorAll('.nav-tab'));
  var nav = document.getElementById('nav');
  var menuIcon = document.getElementById('menu-icon');
  var media = document.getElementById('media');
  var video = document.getElementById('hero-video');
  var micIcon = document.getElementById('mic-icon');
  var micWave = document.getElementById('mic-wave');
  var dotsBox = document.getElementById('dots');

  /* язык страницы синхронизирован с главной: вернувшись на «/», посетитель
     увидит сайт на том же языке */
  try { localStorage.setItem(LANG_KEY, LANG); } catch (err) {}

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

  /* ---------- заголовки: перенос авторский, подгоняем только кегль ----------
     На вебе строка заголовка не переносится: если она чуть шире колонки,
     уменьшаем кегль, а не ломаем строку. На телефоне подгонка выключена —
     там свой крупный масштаб и переносы по месту (как на лендинге). */
  function fitHeadings(root) {
    var wide = mqDesktop.matches;
    if (!root || !root.querySelectorAll) root = document;
    Array.prototype.slice.call(root.querySelectorAll('h1 .l, h2')).forEach(function (el) {
      el.style.fontSize = '';
      el.style.whiteSpace = '';
      if (!wide) return;
      el.style.whiteSpace = 'nowrap';
      var max = parseFloat(getComputedStyle(el).fontSize);
      var size = max, min = max * 0.55;
      while (size > min && el.scrollWidth > el.clientWidth + 1) {
        size -= 0.5;
        el.style.fontSize = size + 'px';
      }
      /* если даже минимальный кегль не спасает — пусть лучше перенесётся,
         чем текст уедет за край */
      if (el.scrollWidth > el.clientWidth + 1) { el.style.whiteSpace = ''; el.style.fontSize = ''; }
    });
  }
  fitHeadings();
  window.addEventListener('resize', fitHeadings);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitHeadings);

  /* ---------- переключение экранов (как на главной) ---------- */
  var cur = 0, swapT, enterT, busy = false;
  function paint() {
    screens.forEach(function (s, i) { s.classList.toggle('active', i === cur); });
    var chapter = screens[cur].getAttribute('data-chapter');
    navTabs.forEach(function (t) { t.classList.toggle('active', t.getAttribute('data-chapter') === chapter); });
    dots.forEach(function (d, i) { d.classList.toggle('on', i === cur); });
    fitHeadings(screens[cur]);
    revealIn(screens[cur]);
    countUpIn(screens[cur]);
  }
  function go(i) {
    if (i < 0 || i >= screens.length || i === cur || busy) return;
    closeMenu();
    busy = true;
    clearTimeout(swapT); clearTimeout(enterT);
    if (reduce) { cur = i; paint(); busy = false; return; }
    article.classList.add('leaving');
    swapT = setTimeout(function () {
      cur = i;
      paint();
      article.classList.remove('leaving');
      article.classList.add('entering');
      enterT = setTimeout(function () { article.classList.remove('entering'); busy = false; }, 520);
    }, 240);
  }
  function step(dir) { go(cur + dir); }

  /* блоки экрана выходят каскадом: задержку держит --d, как на лендинге */
  function revealIn(screen) {
    var items = Array.prototype.slice.call(screen.querySelectorAll('.reveal'));
    items.forEach(function (el, i) {
      if (el.classList.contains('in')) return;
      var d = reduce ? 0 : Math.min(i, 5) * 70;
      if (d) el.style.setProperty('--d', d + 'ms');
      el.classList.add('in');
      setTimeout(function () { el.style.removeProperty('--d'); el.classList.add('done'); }, 760 + d);
    });
  }

  /* цифры в карточках набегают один раз, когда экран показан */
  function countUpIn(screen) {
    if (reduce) return;
    Array.prototype.forEach.call(screen.querySelectorAll('.stat-num'), function (el) {
      if (el.dataset.done) return;
      var m = /^(\D*)(\d+)([\s\S]*)$/.exec(el.textContent.trim());
      if (!m) return;
      var pre = m[1], target = parseInt(m[2], 10), post = m[3];
      if (!isFinite(target) || target < 2) return;
      el.dataset.done = '1';
      var t0 = 0, dur = 1100;
      requestAnimationFrame(function tick(ts) {
        if (!t0) t0 = ts;
        var p = Math.min(1, (ts - t0) / dur);
        el.textContent = pre + Math.round(target * (1 - Math.pow(1 - p, 3))) + post;
        if (p < 1) requestAnimationFrame(tick);
      });
    });
  }

  /* ---------- колесо, свайп, клавиши ----------
     Внутри экрана прокрутки нет вовсе (правка владельца «только по блокам»),
     поэтому любой жест сразу листает экран. */
  var lastWheel = 0;
  window.addEventListener('wheel', function (e) {
    if (nav.classList.contains('open')) return;
    if (Math.abs(e.deltaY) < 30) return;
    var now = Date.now();
    if (now - lastWheel < 900) return;   /* один жест = один экран */
    lastWheel = now;
    step(e.deltaY > 0 ? 1 : -1);
  }, { passive: true });

  var ty = null, lastSwipe = 0;
  window.addEventListener('touchstart', function (e) {
    if (e.touches && e.touches[0]) ty = e.touches[0].clientY;
  }, { passive: true });
  window.addEventListener('touchend', function (e) {
    if (nav.classList.contains('open') || ty == null) return;
    var t = e.changedTouches && e.changedTouches[0];
    if (!t) return;
    var dy = t.clientY - ty;
    if (Math.abs(dy) < 45) return;
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

  /* ---------- меню глав ---------- */
  function openMenu() { nav.classList.add('open'); menuIcon.className = 'fa-solid fa-xmark'; }
  function closeMenu() { nav.classList.remove('open'); menuIcon.className = 'fa-solid fa-bars'; }
  document.getElementById('menu-btn').addEventListener('click', function () {
    nav.classList.contains('open') ? closeMenu() : openMenu();
  });
  var navClose = document.getElementById('nav-close');
  if (navClose) navClose.addEventListener('click', closeMenu);
  /* пункт меню ведёт на ПЕРВЫЙ экран своей главы */
  navTabs.forEach(function (t) {
    t.addEventListener('click', function () {
      var key = t.getAttribute('data-chapter');
      for (var i = 0; i < screens.length; i++) {
        if (screens[i].getAttribute('data-chapter') === key) { go(i); return; }
      }
    });
  });

  /* ---------- звук: клик по видео (и по кружку на мобилке) ---------- */
  function setMuted(m) {
    video.muted = m;
    media.classList.toggle('is-playing', !m);
    micIcon.className = m ? 'fa-solid fa-microphone-lines-slash' : 'fa-solid fa-microphone-lines';
    micIcon.style.color = m ? 'rgba(255,255,255,0.5)' : '#ffffff';
    micWave.style.display = m ? 'none' : 'block';
  }
  setMuted(true);
  function toggle() { setMuted(!video.muted); var p = video.play && video.play(); if (p && p.catch) p.catch(function () {}); }
  document.getElementById('mic-btn').addEventListener('click', function (e) { e.stopPropagation(); toggle(); });

  /* Кружок с роликом можно ТАСКАТЬ — как на лендинге (правка владельца).
     Точка хранится как отступы от ЛЕВОГО-НИЖНЕГО угла, а не как `top`: у
     мобильного браузера при показе адресной строки видимая область и
     координаты position:fixed расходятся, и сохранённый `top` выбрасывал
     кружок на середину экрана. Любая точка прижимается к окну. */
  var POS_KEY = 'ait_about_head';
  var drag = null;
  function clampPos(p) {
    if (!p || typeof p.l !== 'number' || typeof p.b !== 'number') return null;
    var w = media.offsetWidth || 120, h = media.offsetHeight || 120;
    return { l: Math.min(Math.max(8, window.innerWidth - w - 8), Math.max(8, p.l)),
             b: Math.min(Math.max(8, window.innerHeight - h - 8), Math.max(8, p.b)) };
  }
  function applyPos(p) {
    if (mqDesktop.matches) { media.style.left = ''; media.style.bottom = ''; media.style.top = ''; return; }
    p = clampPos(p);
    if (!p) return;
    media.style.left = p.l + 'px';
    media.style.bottom = p.b + 'px';
    media.style.top = 'auto';
  }
  function savedPos() { try { return JSON.parse(localStorage.getItem(POS_KEY)); } catch (e) { return null; } }
  media.addEventListener('pointerdown', function (e) {
    if (mqDesktop.matches) return;
    var r = media.getBoundingClientRect();
    drag = { dx: e.clientX - r.left, dy: r.bottom - e.clientY, moved: 0 };
    media.setPointerCapture(e.pointerId);
  });
  media.addEventListener('pointermove', function (e) {
    if (!drag) return;
    drag.moved += Math.abs(e.movementX) + Math.abs(e.movementY);
    if (drag.moved < 8) return;
    drag.last = { l: e.clientX - drag.dx, b: window.innerHeight - e.clientY - drag.dy };
    applyPos(drag.last);
  });
  media.addEventListener('pointerup', function () {
    if (drag && drag.moved < 8) toggle();
    else if (drag && drag.last) { try { localStorage.setItem(POS_KEY, JSON.stringify(clampPos(drag.last))); } catch (err) {} }
    drag = null;
  });
  media.addEventListener('click', function (e) { if (mqDesktop.matches) toggle(); });
  if (!mqDesktop.matches) applyPos(savedPos());
  window.addEventListener('resize', function () { applyPos(savedPos()); });

  paint();
})();
"""


TEMPLATE = """<!DOCTYPE html>
<!-- Собрано tools/build_about.py из tools/about_copy.py — правьте их, не этот файл -->
<html lang="@@LANG@@">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#050505">
<meta name="color-scheme" content="dark">
<title>@@TITLE@@</title>
<meta name="description" content="@@DESC@@">
<link rel="canonical" href="@@SITE@@@@PATH@@">
<link rel="alternate" hreflang="en" href="@@SITE@@/about/">
<link rel="alternate" hreflang="ru" href="@@SITE@@/about/ru/">
<meta name="robots" content="index, follow, max-image-preview:large">

<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">

<meta property="og:type" content="profile">
<meta property="og:url" content="@@SITE@@@@PATH@@">
<meta property="og:site_name" content="Andre AI Technologies">
<meta property="og:title" content="@@TITLE@@">
<meta property="og:description" content="@@OGDESC@@">
<meta property="og:image" content="@@SITE@@/assets/og/andre-ai-technologies.png">
<meta name="twitter:card" content="summary_large_image">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
<!-- как на главной: шрифт и иконки НЕ блокируют первую отрисовку -->
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet" media="print" onload="this.media='all';this.onload=null">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" media="print" onload="this.media='all';this.onload=null">
<noscript>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</noscript>

<link rel="stylesheet" href="/assets/about.css">
</head>
<body>

<div class="grain" aria-hidden="true"></div>
<div class="top-fade" aria-hidden="true"></div>
<div class="bottom-fade" aria-hidden="true"></div>

<!-- Тигр (детство на Дальнем Востоке) — в Font Awesome его нет, рисуем линиями -->
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="ic-tiger" viewBox="0 0 200 200">
    <g fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M100 176c-38 0-66-28-66-66 0-16 3-30 9-42l-9-38 35 22c9-4 19-6 31-6s22 2 31 6l35-22-9 38c6 12 9 26 9 42 0 38-28 66-66 66z"/>
      <path d="M86 56v16M100 50v20M114 56v16"/>
      <path d="M36 92h18M32 112h20M164 92h-18M168 112h-20"/>
      <ellipse cx="76" cy="102" rx="9" ry="7"/>
      <ellipse cx="124" cy="102" rx="9" ry="7"/>
      <path d="M90 128h20l-10 12z"/>
      <path d="M100 140v10M100 150c-7 11-22 10-26 1M100 150c7 11 22 10 26 1"/>
      <path d="M66 132H40M66 142l-24 9M134 132h26M134 142l24 9"/>
    </g>
  </symbol>
</svg>

<!-- ===== Видео: колонка слева (десктоп) / кружок (мобилка) ===== -->
<div class="media" id="media">
  <video id="hero-video" src="@@VIDEO@@" poster="/andre_ai.jpg" loop muted autoplay playsinline preload="auto"></video>
  <div class="media-shadow" aria-hidden="true"></div>
  <div class="bubble-play" aria-hidden="true"><i class="fa-solid fa-circle-play"></i></div>
  <div class="speaker">
    <div style="display: flex; align-items: center; gap: 0.5rem;">
      <span class="speaker-emoji" aria-hidden="true">🤖</span>
      <h3>Andre AI</h3>
      <span class="sep">|</span>
      <p class="role">@@ROLE@@</p>
    </div>
    <button class="mic-btn" id="mic-btn" aria-label="Toggle voice">
      <i id="mic-icon" class="fa-solid fa-microphone-lines-slash" style="font-size: 11px; color: rgba(255,255,255,0.5);"></i>
      <span id="mic-wave" class="mic-wave"></span>
    </button>
  </div>
</div>

<!-- ===== Header ===== -->
<header>
  <div class="header-row">
    <div class="header-left">
      <a class="logo-btn" href="/" aria-label="Home">
        <img class="logo-img" src="@@LOGO@@" alt="AIT">
      </a>
    </div>

    <nav class="nav" id="nav" aria-label="Sections">
      <button class="nav-close" id="nav-close" aria-label="Close menu"><i class="fa-solid fa-xmark" style="font-size: 26px;"></i></button>
      <div class="nav-brand" aria-hidden="true">
        <img class="nav-brand-img" src="@@LOGO@@" alt="">
        <span class="nav-brand-name">Andre AI Technologies</span>
      </div>
        @@NAV@@
      <div class="nav-foot">
        @@SOCIALS@@
        <div class="nav-legal">
          <a class="nav-legal-link" href="/">@@PRIVACY@@</a>
          <span class="nav-legal-sep" aria-hidden="true">&middot;</span>
          <a class="nav-legal-link" href="/">@@TERMS@@</a>
        </div>
        <p class="nav-copy">2026 &copy; Andre AI Technologies LTD</p>
      </div>
    </nav>

    <div class="header-right">
      <div class="lang-switch" role="group" aria-label="Language">
        @@LANGSWITCH@@
      </div>
      <button class="menu-btn" id="menu-btn" aria-label="Menu"><i id="menu-icon" class="fa-solid fa-bars" style="font-size: clamp(14px, 4vw, 18px);"></i></button>
      <a class="btn-white cta" href="https://maturity.andre.technology/" rel="noopener">@@CTA@@ <i class="fa-solid fa-arrow-right"></i></a>
    </div>
  </div>
</header>

<!-- ===== Колонка чтения ===== -->
<div class="dots" id="dots" aria-hidden="true"></div>
<main class="read" id="read">
  <article class="article">

@@SCREENS@@

    </article>
</main>

<script>@@JS@@</script>
</body>
</html>
"""

LANG_EN = ('<span class="lang-opt active">EN</span>\n'
           '        <span class="lang-sep" aria-hidden="true">|</span>\n'
           '        <a class="lang-opt" href="/about/ru/">RU</a>')
LANG_RU = ('<a class="lang-opt" href="/about/">EN</a>\n'
           '        <span class="lang-sep" aria-hidden="true">|</span>\n'
           '        <span class="lang-opt active">RU</span>')


def page(c):
    body = "\n\n".join(screen_html(i, s, c) for i, s in enumerate(SCREENS))
    html = TEMPLATE
    for token, value in [
        ("@@LANG@@", c["lang"]),
        ("@@TITLE@@", c["title"]),
        ("@@DESC@@", c["desc"]),
        ("@@OGDESC@@", c["og_desc"]),
        ("@@SITE@@", SITE),
        ("@@PATH@@", PATH_RU if c["lang"] == "ru" else PATH_EN),
        ("@@LOGO@@", LOGO),
        ("@@VIDEO@@", "/assets/Andre_AIT_video_compressed_ru.mp4"
                      if c["lang"] == "ru" else "/assets/Andre_AIT_video_compressed.mp4"),
        ("@@ROLE@@", c["role"]),
        ("@@NAV@@", nav_html(c)),
        ("@@SOCIALS@@", socials()),
        ("@@PRIVACY@@", c["privacy"]),
        ("@@TERMS@@", c["terms"]),
        ("@@LANGSWITCH@@", LANG_RU if c["lang"] == "ru" else LANG_EN),
        ("@@CTA@@", c["cta"]),
        ("@@SCREENS@@", body),
        ("@@JS@@", JS),
    ]:
        assert token in html, token
        html = html.replace(token, value)
    assert "@@" not in html, "в шаблоне остались незаполненные метки"
    return html


def build():
    from about_copy import EN, RU
    pages = (("about/index.html", page(EN)), ("about/ru/index.html", page(RU)))
    for rel, html in pages:
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("written", rel, len(html), "bytes,", len(SCREENS), "screens")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    build()
