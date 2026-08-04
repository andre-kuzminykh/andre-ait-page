# -*- coding: utf-8 -*-
"""Сборка двух входных страниц курса из одного шаблона.

  /automation/     — английская (адрес без пометки)
  /automation_ru/  — русская (помечена суффиксом _ru)

Обе страницы устроены одинаково: одна и та же вёрстка, стили и скрипт, разные
только тексты и мета для веб-превью. Шаблон здесь — единственный источник
правды; `tests/test_course_entry.py` пересобирает страницы и сверяет байты,
поэтому руками их править нельзя — правим шаблон и запускаем:

    python3 tools/build_course_entry.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE = "https://andre.technology"
PATH_EN = "/automation/"
PATH_RU = "/automation_ru/"
URL_EN = SITE + PATH_EN
URL_RU = SITE + PATH_RU
COURSE = SITE + "/automation/main"

# Обложка курса для веб-превью (прислал заказчик). Меняется одной строкой на язык.
OG_IMAGE_EN = SITE + "/assets/cover_auto.jpg"
OG_IMAGE_RU = SITE + "/assets/cover_auto.jpg"
OG_W, OG_H = "960", "540"          # реальные размеры обложки

# ─────────────────────────────────────────────────────────────────────────────
# Тексты
# ─────────────────────────────────────────────────────────────────────────────

RU = {
    "lang": "ru",
    "url": URL_RU,
    "path": PATH_RU,
    "other_path": PATH_EN,
    "og_locale": "ru_RU",
    "og_image": OG_IMAGE_RU,
    "title": "Курс по автоматизации бизнес-процессов с помощью ИИ-агентов",
    "desc": (
        "Курс для будущих ИИ-консультантов, ИИ-инженеров по автоматизации и "
        "ИИ-основателей: находить процессы для автоматизации, собирать "
        "ИИ-агентов и получать измеримый экономический эффект."
    ),
    "og_image_alt": "Курс по автоматизации бизнес-процессов с помощью ИИ-агентов",
    "home_label": "На главную",
    "lang_group": "Язык",
    "theme_label": "Сменить фон (тёмный/светлый)",
    "consult": "Консультация",
    "consult_label": "Консультация",
    "blocks_label": "Блоки страницы",
    "start": "Начать обучение",
    "scroll": "Листайте вниз",
    "a_course": "О курсе",
    "a_roles": "Для кого этот курс",
    "a_skills": "Чему вы научитесь",
    "a_start": "Начать обучение",
    "hero": ('<span class="line">Добро пожаловать на курс</span>'
             '<span class="line">по автоматизации</span>'
             '<span class="line"><span class="plum">бизнес-процессов</span> '
             'с <span class="flame">ИИ-агентами</span></span>'),
    "hero_desc": ("Вы научитесь трансформировать бизнес в AI-First компанию: "
                  '<br class="lb">автоматизировать процессы с помощью ИИ-агентов, масштабироваться '
                  '<br class="lb">без роста штата и получать измеримый экономический эффект.'),
    "roles_h": 'Для кого <span class="plum">этот курс</span>',
    "roles": [
        ("p", "fa-compass", "ИИ-консультант",
         'Находит процессы для <span class="nb">ИИ-автоматизации</span>'),
        ("f", "fa-wrench", "ИИ-инженер по автоматизации",
         'Автоматизирует бизнес с <span class="nb">ИИ-агентами</span>'),
        ("p", "fa-rocket", "ИИ-основатель",
         'Строит бизнес с помощью <span class="nb">ИИ-агентов</span>'),
    ],
    "skills_h": 'Чему вы <span class="flame">научитесь</span>',
    "skills": [
        "Управлять компанией как потоком данных",
        "Находить процессы для автоматизации",
        "Описывать текущий AS-IS процесс",
        "Проектировать будущую TO-BE модель",
        "Определять роль ИИ-агента в процессе",
        "Создавать ИИ-агентов",
        "Понимать логику мультиагентных систем",
        "Проверять качество и безопасность ИИ",
        "Оценивать эффект от автоматизации",
        "Внедрить первого ИИ-агента в бизнес",
    ],
    "final_h": 'Готовы <span class="plum">начать</span>?',
    "final_lead": ("Пройдите курс шаг за шагом — от поиска процесса до работающего "
                   '<span class="nb">ИИ-агента</span> в вашем бизнесе.'),
}

EN = {
    "lang": "en",
    "url": URL_EN,
    "path": PATH_EN,
    "other_path": PATH_RU,
    "og_locale": "en_US",
    "og_image": OG_IMAGE_EN,
    "title": "Business process automation course with AI agents",
    "desc": ("A course for future AI consultants, AI automation engineers and AI "
             "founders: find the processes worth automating, build AI agents and "
             "deliver a measurable economic effect."),
    "og_image_alt": "Business process automation course with AI agents",
    "home_label": "Home",
    "lang_group": "Language",
    "theme_label": "Switch background (dark/light)",
    "consult": "Consultation",
    "consult_label": "Consultation",
    "blocks_label": "Page sections",
    "start": "Start learning",
    "scroll": "Scroll down",
    "a_course": "About the course",
    "a_roles": "Who this course is for",
    "a_skills": "What you will learn",
    "a_start": "Start learning",
    "hero": ('<span class="line">Welcome to the course on</span>'
             '<span class="line"><span class="plum">business process automation</span></span>'
             '<span class="line">with <span class="flame">AI agents</span></span>'),
    "hero_desc": ("You will learn to transform your business into an AI-First company: "
                  '<br class="lb">automate processes with AI agents, scale without growing headcount, '
                  '<br class="lb">and achieve a measurable economic effect.'),
    "roles_h": 'Who <span class="plum">this course</span> is for',
    "roles": [
        ("p", "fa-compass", "AI Consultant", "Finds processes ready for AI automation"),
        ("f", "fa-wrench", "AI Automation Engineer", "Automates business with AI agents"),
        ("p", "fa-rocket", "AI Founder", "Builds a business powered by AI agents"),
    ],
    "skills_h": 'What you will <span class="flame">learn</span>',
    "skills": [
        "Run a company as a flow of data",
        "Find processes worth automating",
        "Describe the current AS-IS process",
        "Design the future TO-BE model",
        "Define the AI agent's role in a process",
        "Build AI agents",
        "Understand multi-agent system logic",
        "Verify AI quality and safety",
        "Measure the effect of automation",
        "Deploy your first AI agent in a business",
    ],
    "final_h": 'Ready to <span class="plum">start</span>?',
    "final_lead": ("Take the course step by step — from finding a process to a working "
                   '<span class="nb">AI agent</span> in your business.'),
}

SKILL_ICONS = ("fa-brain", "fa-magnifying-glass", "fa-clipboard-list", "fa-pen-ruler",
               "fa-user-gear", "fa-robot", "fa-network-wired", "fa-shield-halved",
               "fa-arrow-trend-up", "fa-rocket")

# ─────────────────────────────────────────────────────────────────────────────
# Шаблон
# ─────────────────────────────────────────────────────────────────────────────

TEMPLATE = r"""<!DOCTYPE html>
<html lang="{{LANG}}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#050505">
<meta name="color-scheme" content="dark light">
<script>
/* Тема — до первой отрисовки, чтобы светлая не мигала чёрным. */
(function(){try{if(localStorage.getItem('welcome-theme')==='light')document.documentElement.classList.add('light');}catch(e){}})();
/* Язык: страница у каждого языка своя (адрес без пометки — английский,
   с суффиксом _ru — русский). Если посетитель уже выбирал язык на
   andre.technology, один раз за вкладку уводим его на нужную версию.
   Роботам и превью-скрейперам это не мешает: они JS не исполняют. */
(function(){
  try{
    if (sessionStorage.getItem('ait_lang_hop') === '1') return;
    var pref = localStorage.getItem('ait_lang');
    if ((pref === 'ru' || pref === 'en') && pref !== '{{LANG}}'){
      sessionStorage.setItem('ait_lang_hop', '1');
      location.replace('{{OTHER_PATH}}' + location.hash);
    }
  }catch(e){}
})();
</script>
<title>{{TITLE}}</title>
<meta name="description" content="{{DESC}}">

<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">

<link rel="canonical" href="{{URL}}">
<link rel="alternate" hreflang="en" href="{{URL_EN}}">
<link rel="alternate" hreflang="ru" href="{{URL_RU}}">
<link rel="alternate" hreflang="x-default" href="{{URL_EN}}">

<meta property="og:type" content="website">
<meta property="og:site_name" content="Andre AI Technologies">
<meta property="og:locale" content="{{OG_LOCALE}}">
<meta property="og:title" content="{{TITLE}}">
<meta property="og:description" content="{{DESC}}">
<meta property="og:url" content="{{URL}}">
<meta property="og:image" content="{{OG_IMAGE}}">
<meta property="og:image:width" content="{{OG_W}}">
<meta property="og:image:height" content="{{OG_H}}">
<meta property="og:image:alt" content="{{OG_IMAGE_ALT}}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{TITLE}}">
<meta name="twitter:description" content="{{DESC}}">
<meta name="twitter:image" content="{{OG_IMAGE}}">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<style>
  /* ============================================================
     Andre AIT — вход в курс. Один экран = один блок.
     Ни страница, ни сам блок не прокручиваются: колесо, свайп,
     стрелки и точки справа переключают блок целиком. Если блок
     не влезает в экран, скрипт ужимает его содержимое — резать
     нельзя, листать внутри блока тоже нельзя.
     ============================================================ */
  :root{
    --bg:#050505; --fg:#E5E7EB; --muted:rgba(255,255,255,.55);
    --card-bg:rgba(255,255,255,.04); --card-border:rgba(255,255,255,.10);
    --divider:rgba(255,255,255,.12); --navitem:rgba(255,255,255,.60);
    --btn-bg:#FAFAFA; --btn-fg:#050505;
    --ctrl-bg:rgba(255,255,255,.05); --ctrl-border:rgba(255,255,255,.10); --ctrl-fg:rgba(255,255,255,.80);
    --tile-bg:#15151b; --dot:rgba(255,255,255,.45);
  }
  html.light{
    --bg:#FAFAFA; --fg:#0A0A0A; --muted:rgba(10,10,10,.55);
    --card-bg:#fff; --card-border:rgba(0,0,0,.07);
    --divider:rgba(0,0,0,.10); --navitem:rgba(0,0,0,.55);
    --btn-bg:#0A0A0A; --btn-fg:#FAFAFA;
    --ctrl-bg:rgba(0,0,0,.03); --ctrl-border:rgba(0,0,0,.10); --ctrl-fg:rgba(0,0,0,.70);
    --tile-bg:#fff; --dot:rgba(0,0,0,.42);
  }
  /* На белом фоне фирменный оранжевый выцветает (2.7:1), а вторичный текст
     проваливается ниже 4.5:1 — в светлой теме берём те же цвета потемнее. */
  html.light{ --muted:rgba(10,10,10,.62); }
  html.light .flame, html.light .ico.f{ color:#D9520A; }
  html.light .learn li:hover{ border-color:rgba(217,82,10,.45) }

  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;overscroll-behavior:none}
  body{
    background:var(--bg); color:var(--fg);
    transition:background .25s ease,color .25s ease;
    font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,monospace;
    -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale;
    -webkit-tap-highlight-color:transparent;
  }
  h1,h2,h3{letter-spacing:-.02em;margin:0}
  ::selection{background:#8854F3;color:#fff}
  a{text-decoration:none;color:inherit}
  button{font-family:inherit;cursor:pointer}
  *:focus-visible{outline:2px solid #8854F3;outline-offset:2px}
  .plum{color:#8854F3}
  .flame{color:#F97316}

  /* Теней нет нигде (канон сайта) */
  *, *::before, *::after{ box-shadow:none !important; text-shadow:none !important; }
  [class*="drop-shadow"]{ filter:none !important; }
  img{ filter:none !important; }

  @keyframes gradientShimmer{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
  @keyframes floatY{0%{transform:translateY(0)}50%{transform:translateY(-9px)}100%{transform:translateY(0)}}
  @keyframes bounceDown{0%,100%{transform:translateY(0)}50%{transform:translateY(6px)}}
  @keyframes riseIn{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}

  /* ===== Grain (как на главном сайте) ===== */
  .grain{position:fixed;inset:0;z-index:4;pointer-events:none;opacity:.06;mix-blend-mode:screen;
    background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
    background-size:180px 180px}
  html.light .grain{mix-blend-mode:multiply;opacity:.04}

  /* ===== Шапка ===== */
  header{position:fixed;inset:0 0 auto 0;z-index:40}
  .row{display:grid;grid-template-columns:1fr auto;align-items:center;gap:.75rem;padding:1.1rem}
  @media(min-width:1024px){.row{padding:2rem}}

  .logo-btn{display:inline-flex;align-items:center;gap:.5rem;background:none;border:0;padding:0;justify-self:start;cursor:pointer}
  .logo-btn img{height:clamp(2.6rem,11vw,3.4rem);width:auto;object-fit:contain;transition:transform .2s ease}
  @media(min-width:1024px){.logo-btn img{height:3.4rem}}
  .logo-btn:hover img{transform:scale(1.05)}

  .right{display:flex;align-items:center;justify-self:end;gap:.45rem}
  @media(min-width:640px){.right{gap:.7rem}}

  /* Переключатель языка — как на главной: EN | RU, активный подсвечен.
     Здесь это ссылки: у каждого языка своя страница со своим веб-превью. */
  .lang-switch{display:flex;align-items:center;gap:.3rem;margin-right:.15rem;flex-shrink:0}
  @media(min-width:640px){.lang-switch{margin-right:.4rem}}
  .lang-opt{background:none;border:0;padding:.2rem .05rem;font-size:11px;font-weight:500;
    color:var(--navitem);letter-spacing:.06em;transition:color .2s ease;cursor:pointer}
  .lang-opt.active{color:var(--fg);font-weight:700}
  @media(hover:hover){.lang-opt:hover{color:var(--fg)}}
  .lang-sep{color:var(--divider);font-size:10px;user-select:none}
  @media(min-width:1024px){.lang-opt{font-size:12px}}

  .ctrl{display:inline-flex;align-items:center;justify-content:center;height:clamp(2.4rem,10vw,3.1rem);min-width:clamp(2.4rem,10vw,3.1rem);padding:0 .55rem;border-radius:999px;border:1px solid var(--ctrl-border);background:var(--ctrl-bg);color:var(--ctrl-fg);font-size:clamp(.95rem,3.2vw,1.15rem);line-height:1;flex-shrink:0;transition:background .2s ease}
  @media(min-width:1024px){.ctrl{height:2.85rem;min-width:2.85rem;font-size:1.05rem}}
  .ctrl:hover{background:rgba(136,84,243,.14)}

  /* ===== CTA-кнопки: белые, шиммер-градиент на ховере ===== */
  .btn-white{
    display:inline-flex;align-items:center;justify-content:center;gap:.55rem;border:0;
    border-radius:999px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;
    background:var(--btn-bg);color:var(--btn-fg);
    transition:all .3s ease;white-space:nowrap;
  }
  .btn-white:hover{
    background:linear-gradient(100deg,#8854F3 0%,#F97316 50%,#8854F3 100%);background-size:250% 250%;
    color:#fff;transform:translateY(-2px);
    animation:gradientShimmer 4.5s ease infinite;
  }
  .consult{height:clamp(2.4rem,10vw,3.1rem);padding:0 clamp(.9rem,2.2vw,1.5rem);font-size:clamp(9.5px,1.02vw,12px)}
  @media(min-width:1024px){.consult{height:2.85rem;padding:0 1.4rem;font-size:11.5px;letter-spacing:.15em}}
  @media(max-width:399px){.consult .txt{display:none}.consult{padding:0 .8rem}}

  /* Широкие экраны: масштабируем весь UI (как на главном сайте) */
  @media(min-width:1600px){body{zoom:1.15}}
  @media(min-width:1900px){body{zoom:1.3}}
  @media(min-width:2300px){body{zoom:1.5}}

  /* ===== Дек блоков ===== */
  .deck{position:fixed;inset:0;z-index:2}
  .panel{
    position:absolute;inset:0;display:flex;
    overflow:hidden;overscroll-behavior:none;
    padding:clamp(5.5rem,13vh,7.5rem) 1rem clamp(3rem,7vh,4.5rem);
    opacity:0;visibility:hidden;pointer-events:none;
    transition:opacity .34s ease,visibility 0s linear .34s;
  }
  @media(min-width:640px){.panel{padding-left:2rem;padding-right:2rem}}
  .panel.on{opacity:1;visibility:visible;pointer-events:auto;transition:opacity .34s ease,visibility 0s}
  /* margin:auto вместо align-items:center: если блок всё-таки выше экрана,
     скрипт ужмёт .wrap и сам посчитает отступ сверху. */
  .wrap{margin:auto;width:100%;max-width:62rem;text-align:center}

  /* Появление содержимого: каскад перезапускается при каждом показе блока */
  .panel.on .wrap > *{animation:riseIn .5s cubic-bezier(.22,1,.36,1) both}
  .panel.on .wrap > *:nth-child(2){animation-delay:.06s}
  .panel.on .wrap > *:nth-child(3){animation-delay:.12s}
  .panel.on .wrap > *:nth-child(4){animation-delay:.18s}
  .panel.on .wrap > *:nth-child(n+5){animation-delay:.24s}
  .panel.on .roles > *,.panel.on .learn > *{animation:riseIn .45s cubic-bezier(.22,1,.36,1) both}
  .panel.on .roles > *:nth-child(2){animation-delay:.08s}
  .panel.on .roles > *:nth-child(3){animation-delay:.14s}
  .panel.on .learn > *:nth-child(n+3){animation-delay:.06s}
  .panel.on .learn > *:nth-child(n+7){animation-delay:.12s}

  /* Точки-навигация по блокам */
  .dots{position:fixed;z-index:30;right:clamp(.7rem,1.6vw,1.5rem);top:50%;transform:translateY(-50%);
    display:flex;flex-direction:column;gap:.7rem}
  .dot{width:8px;height:8px;padding:0;border:0;border-radius:999px;background:var(--dot);
    transition:background .25s ease,transform .25s ease}
  .dot.on{background:#8854F3;transform:scale(1.35)}
  @media(hover:hover){.dot:hover{background:#F97316}}
  @media(max-width:520px){.dots{right:.45rem;gap:.55rem}.dot{width:7px;height:7px}}

  /* ===== Блок 1: о курсе ===== */
  /* zoom, а не transform: transform уменьшает только отрисовку, в потоке ряд
     продолжал занимать полную высоту — подгонка блока считала её и ужимала
     первый экран сильнее, чем требовалось. */
  .float-row{display:flex;justify-content:center;align-items:flex-end;gap:.85rem;zoom:.82;margin:0 0 .25rem}
  @media(min-width:640px){.float-row{zoom:1;margin-bottom:.85rem}}
  .tile{flex-shrink:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:var(--tile-bg);border:1px solid var(--card-border);border-radius:1rem;animation:floatY 4s ease-in-out infinite}
  .tile.sm{width:3.6rem;height:5.4rem;gap:.55rem}
  .tile.lg{width:4.5rem;height:6.6rem;gap:.6rem;border-radius:1.1rem}
  .tile .bar{height:3px;border-radius:2px}
  .tile.sm .bar{width:1.6rem}
  .tile.lg .bar{width:2rem}

  .hero{font-size:clamp(1.4rem,4.6vw,2.8rem);font-weight:800;text-transform:uppercase;line-height:1.12;letter-spacing:-.02em;padding-top:.5rem}
  .hero span.line{display:block}
  .hero .plum,.hero .flame{white-space:nowrap}
  .desc{color:var(--muted);max-width:min(62em,92vw);margin:1.35rem auto 0;font-size:clamp(14.5px,1.05vw,21px);line-height:1.6}
  .desc .lb{display:none}
  @media (min-width:680px){ .desc .lb{display:inline} }

  .scroll-hint{background:none;border:0;padding:0;margin-top:clamp(1.2rem,3.5vh,2rem);color:var(--muted);font-size:.72rem;letter-spacing:.15em;text-transform:uppercase;display:inline-flex;flex-direction:column;align-items:center;gap:.45rem}
  .scroll-hint i{animation:bounceDown 1.8s ease-in-out infinite;color:#8854F3}

  /* заголовки блоков */
  .h2{text-align:center;font-size:clamp(1.45rem,4vw,1.9rem);font-weight:800;text-transform:uppercase;letter-spacing:-.02em}
  @media(min-width:1024px){.h2{font-size:clamp(2.1rem,2.3vw,2.8rem)}}

  /* ===== Блок 2: для кого ===== */
  .roles{margin-top:1.8rem;display:grid;grid-template-columns:1fr;gap:1rem}
  @media(min-width:640px){.roles{grid-template-columns:repeat(3,1fr)}}
  .card{border:1px solid var(--card-border);background:var(--card-bg);border-radius:1rem;transition:transform .2s ease,border-color .2s ease}
  .card:hover{transform:translateY(-3px);border-color:rgba(136,84,243,.45)}
  .role{padding:1.5rem 1.3rem;text-align:center}
  .role .ico{margin:0 auto 1rem;display:inline-flex;align-items:center;justify-content:center;height:clamp(3.4rem,4.5vw,4.5rem);width:clamp(3.4rem,4.5vw,4.5rem);border-radius:1.1rem;font-size:clamp(1.45rem,2vw,2rem)}
  .ico.p{background:rgba(136,84,243,.15);color:#8854F3}
  .ico.f{background:rgba(249,115,22,.15);color:#F97316}
  .role h3{font-size:clamp(1rem,1.3vw,1.25rem);font-weight:700;text-transform:uppercase}
  /* Заголовок средней карточки занимает две строки — резерв даём всем трём,
     иначе описания в ряду начинаются с разной высоты. */
  @media(min-width:640px){.role h3{min-height:2.5em;display:flex;align-items:center;justify-content:center}}
  .role p{color:var(--muted);margin:.55rem 0 0;font-size:clamp(.78rem,1vw,.95rem);line-height:1.6}
  .nb{white-space:nowrap}   /* «ИИ-агентами» не разрывается по дефису */

  /* ===== Блок 3: чему научитесь ===== */
  .learn{margin:1.8rem auto 0;max-width:61rem;display:grid;grid-template-columns:repeat(2,1fr);gap:.55rem;list-style:none;padding:0;text-align:left;counter-reset:n}
  @media(max-width:639px){.learn{grid-template-columns:1fr}}
  .learn li{position:relative;display:flex;align-items:center;gap:.75rem;padding:.72rem 2rem .72rem .9rem;border-radius:1rem;border:1px solid var(--card-border);background:var(--card-bg);transition:transform .2s ease,border-color .2s ease}
  .learn li:hover{transform:translateY(-2px);border-color:rgba(249,115,22,.45)}
  .learn .ico{height:clamp(2.2rem,3vw,2.8rem);width:clamp(2.2rem,3vw,2.8rem);border-radius:.65rem;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;font-size:clamp(1rem,1.4vw,1.35rem)}
  .learn p{margin:0;font-size:clamp(.78rem,1.3vw,.98rem);line-height:1.4}
  .learn li::after{counter-increment:n;content:counter(n,decimal-leading-zero);position:absolute;top:.4rem;right:.7rem;font-size:.6rem;font-weight:700;letter-spacing:.08em;color:var(--muted);opacity:1}

  /* ===== CTA ===== */
  .cta-row{margin:1.9rem 0 0;display:flex;justify-content:center}
  .btn-start{padding:clamp(.95rem,1vw,1.5rem) clamp(1.9rem,2vw,3.2rem);font-size:clamp(12px,.85vw,17px);letter-spacing:.15em}
  .lead{color:var(--muted);max-width:40em;margin:1rem auto 0;font-size:clamp(.85rem,1.05vw,1.05rem);line-height:1.65}
  .divider{height:1px;max-width:16rem;margin:0 auto clamp(1.5rem,4vh,2.6rem);background:linear-gradient(90deg,transparent,#8854F3,#F97316,transparent);opacity:.6}

  /* Портрет и кнопка — один блок без просвета. Никакого градиента: снимок
     обрезан «в стык» и уходит ПОД кнопку до её середины, поэтому срез не виден
     и зазору взяться неоткуда. Кадр обрезан по силуэту в точке среза, так что
     выше кнопки плечи заведомо у́же неё и за края не заходят. Ширину и заход
     под кнопку считает скрипт — они зависят от фактического размера кнопки. */
  .cta-stack{margin:1.5rem 0 0;display:flex;flex-direction:column;align-items:center}
  .cta-photo{display:block;margin:0 auto;width:min(15rem,60vw);max-width:15rem;height:auto;pointer-events:none}
  .cta-stack .btn-start{position:relative;z-index:1}   /* кнопка поверх снимка */

  .site-link{display:inline-block;margin-top:clamp(1.3rem,4vh,2.1rem);color:var(--muted);font-size:.72rem;letter-spacing:.06em;border-bottom:1px solid var(--divider)}
  .site-link:hover{color:#8854F3;border-color:#8854F3}

  /* Телефон: ужимаем блоки так, чтобы каждый влезал в экран целиком —
     внутри блока прокрутки нет вовсе. */
  @media (max-width:639px){
    .panel{padding-top:clamp(4.9rem,11vh,6rem);padding-bottom:2rem;padding-left:1.4rem;padding-right:1.4rem}
    .desc{margin-top:1rem}
    .scroll-hint{margin-top:1.1rem}
    .cta-row{margin-top:1.15rem}
    .roles{margin-top:1.2rem;gap:.65rem}
    .role{padding:1.05rem 1rem}
    .role .ico{height:2.9rem;width:2.9rem;margin-bottom:.6rem;font-size:1.25rem;border-radius:.9rem}
    .role p{margin-top:.35rem;line-height:1.5}
    .learn{margin-top:1.15rem;gap:.4rem}
    .learn li{padding:.5rem .8rem;gap:.6rem;border-radius:.8rem}
    /* Номер пункта на телефоне съедал ширину строки и всё равно был
       нечитаем (9px, приглушённый) — на узком экране он не нужен. */
    .learn li::after{display:none}
    .learn .ico{height:2rem;width:2rem;font-size:.95rem;border-radius:.55rem}
    .learn p{font-size:.76rem;line-height:1.3}
    .lead{margin-top:.7rem}
    .cta-stack{margin-top:1.1rem}
    .site-link{margin-top:1.1rem}
  }
  /* Низкие экраны — ещё плотнее. Условие по высоте без ограничения ширины:
     в альбомной ориентации телефона ширина уже 844px, и правило с
     max-width:639px туда не доставало — блоки переставали влезать. */
  @media (max-height:700px){
    .float-row{zoom:.7;margin-bottom:0}
    .roles{margin-top:.9rem;gap:.5rem}
    .role{padding:.8rem .9rem}
    .role .ico{height:2.4rem;width:2.4rem;margin-bottom:.45rem;font-size:1.05rem}
    .learn{margin-top:.7rem;gap:.32rem}
    .learn li{padding:.42rem .7rem}
    .learn li::after{display:none}   /* резерв справа убран — номер убираем тоже */
    .learn .ico{height:1.8rem;width:1.8rem;font-size:.85rem}
    .cta-row{margin-top:.9rem}
    .panel{padding-top:clamp(4.2rem,14vh,5.2rem);padding-bottom:1.2rem}
    .desc{margin-top:.6rem}
    .scroll-hint{margin-top:.6rem}
    .cta-stack{margin-top:.6rem}
    .divider{margin-bottom:.8rem}
    .lead{margin-top:.5rem}
    .site-link{margin-top:.7rem}
  }

  /* На печать уходят все четыре блока подряд, а не только активный */
  @media print{
    html,body{height:auto;overflow:visible}
    .deck{position:static}
    .panel{position:static;opacity:1;visibility:visible;overflow:visible;page-break-after:always}
    .panel .wrap{transform:none !important;margin:0 auto !important}
    .dots,.scroll-hint,header{display:none}
  }

  @media (prefers-reduced-motion: reduce){
    .panel{transition:none}
    .panel.on .wrap > *,.panel.on .roles > *,.panel.on .learn > *{animation:none}
    .tile,.scroll-hint i{animation:none}
    .btn-white:hover{animation:none;transform:none}
  }
</style>
<noscript><style>
  /* Без скрипта дек не переключить — страница становится обычной,
     прокручиваемой, все четыре блока видны подряд. */
  html,body{height:auto;overflow:auto}
  .deck{position:static}
  .panel{position:static;opacity:1;visibility:visible;pointer-events:auto;min-height:100vh;overflow:visible}
  .dots,.scroll-hint,#theme{display:none}
</style></noscript>
</head>
<body>

  <div class="grain"></div>

  <!-- HEADER -->
  <header id="hdr">
    <div class="row">
      <button class="logo-btn" aria-label="{{HOME_LABEL}}" onclick="location.href='https://andre.technology'">
        <img src="https://i.ibb.co/gn7SmgY/866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png" alt="Andre AI">
      </button>
      <div class="right">
        <div class="lang-switch" role="group" aria-label="{{LANG_GROUP}}">
{{LANG_SWITCH}}
        </div>
        <button class="ctrl" id="theme" aria-label="{{THEME_LABEL}}"><i class="fa-solid fa-sun"></i></button>
        <button class="btn-white consult" onclick="window.open('https://t.me/andre_andreevich','_blank','noopener')" aria-label="{{CONSULT_LABEL}}">
          <span class="txt">{{CONSULT}}</span>
          <i class="fa-solid fa-arrow-right" style="font-size:.75rem"></i>
        </button>
      </div>
    </div>
  </header>

  <main class="deck" id="deck">

    <!-- ===== 1. О КУРСЕ ===== -->
    <section class="panel on" id="course" aria-label="{{A_COURSE}}">
      <div class="wrap">
        <div class="float-row" aria-hidden="true">
          <div class="tile sm" style="border-color:rgba(136,84,243,.3)"><i class="fa-solid fa-magnifying-glass-chart" style="font-size:26px;color:#8854F3"></i><div class="bar" style="background:rgba(136,84,243,.5)"></div></div>
          <div class="tile lg" style="border-color:rgba(249,115,22,.5);animation-delay:.2s"><i class="fa-solid fa-robot" style="font-size:38px;color:#F97316"></i><div class="bar" style="background:rgba(249,115,22,.5)"></div></div>
          <div class="tile sm" style="border-color:rgba(136,84,243,.3);animation-delay:.4s"><i class="fa-solid fa-gears" style="font-size:26px;color:#8854F3"></i><div class="bar" style="background:rgba(136,84,243,.5)"></div></div>
        </div>
        <h1 class="hero" id="hero-h">{{HERO}}</h1>
        <p class="desc" id="hero-d">{{HERO_DESC}}</p>
        <div class="cta-row">
          <a class="btn-white btn-start" href="{{COURSE}}">
            <span>{{START}}</span>
            <i class="fa-solid fa-arrow-right" style="font-size:1rem"></i>
          </a>
        </div>
        <button class="scroll-hint" type="button" data-go="next">
          <span>{{SCROLL}}</span>
          <i class="fa-solid fa-chevron-down"></i>
        </button>
      </div>
    </section>

    <!-- ===== 2. ДЛЯ КОГО ===== -->
    <section class="panel" id="roles" aria-label="{{A_ROLES}}">
      <div class="wrap">
        <h2 class="h2" id="roles-h">{{ROLES_H}}</h2>
        <div class="roles">
{{ROLE_CARDS}}
        </div>
        <div class="cta-row">
          <a class="btn-white btn-start" href="{{COURSE}}">
            <span>{{START}}</span>
            <i class="fa-solid fa-arrow-right" style="font-size:1rem"></i>
          </a>
        </div>
      </div>
    </section>

    <!-- ===== 3. ЧЕМУ НАУЧИТЕСЬ ===== -->
    <section class="panel" id="skills" aria-label="{{A_SKILLS}}">
      <div class="wrap">
        <h2 class="h2" id="skills-h">{{SKILLS_H}}</h2>
        <ol class="learn">
{{SKILL_ITEMS}}
        </ol>
        <div class="cta-row">
          <a class="btn-white btn-start" href="{{COURSE}}">
            <span>{{START}}</span>
            <i class="fa-solid fa-arrow-right" style="font-size:1rem"></i>
          </a>
        </div>
      </div>
    </section>

    <!-- ===== 4. НАЧАТЬ ===== -->
    <section class="panel" id="start" aria-label="{{A_START}}">
      <div class="wrap">
        <div class="divider"></div>
        <h2 class="h2" id="final-h">{{FINAL_H}}</h2>
        <p class="lead">{{FINAL_LEAD}}</p>
        <div class="cta-stack">
          <picture>
            <source srcset="/automation/andre-cta.webp" type="image/webp">
            <img class="cta-photo" id="cta-photo" src="/automation/andre-cta.png" alt="" width="600" height="454" decoding="async" onerror="this.style.display='none'">
          </picture>
          <a class="btn-white btn-start" id="final-cta" href="{{COURSE}}">
            <span>{{START}}</span>
            <i class="fa-solid fa-arrow-right" style="font-size:1rem"></i>
          </a>
        </div>
        <a class="site-link" href="https://andre.technology">andre.technology</a>
      </div>
    </section>

  </main>

  <nav class="dots" id="dots" aria-label="{{BLOCKS_LABEL}}"></nav>

  <script>
    function storeGet(k){ try { return localStorage.getItem(k); } catch (e) { return null; } }
    function storeSet(k, v){ try { localStorage.setItem(k, v); } catch (e) {} }

    /* ===== Язык: у каждого своя страница. Клик по EN|RU запоминает выбор и
       уводит на соседнюю версию; авто-переход при этом больше не срабатывает,
       иначе ручной выбор отскакивал бы обратно. ===== */
    (function(){
      var opts = document.querySelectorAll('.lang-opt'), i;
      for (i = 0; i < opts.length; i++){
        opts[i].addEventListener('click', function(){
          storeSet('ait_lang', this.getAttribute('data-lang'));
          try { sessionStorage.setItem('ait_lang_hop', '1'); } catch (e) {}
        });
      }
      // Осознанный выбор посетителя не перетираем — записываем язык только
      // если он вообще ещё не выбирался.
      if (storeGet('ait_lang') !== 'en' && storeGet('ait_lang') !== 'ru') storeSet('ait_lang', '{{LANG}}');
    })();

    /* ===== Тема: тёмная по умолчанию, .light по клику; ключ общий со
       страницами курса ('welcome-theme') ===== */
    (function(){
      var root = document.documentElement;
      var btn  = document.getElementById('theme');
      function sync(){
        var light = root.classList.contains('light');
        btn.innerHTML = '<i class="fa-solid fa-' + (light ? 'moon' : 'sun') + '"></i>';
        var tc = document.querySelector('meta[name="theme-color"]');
        if (tc) tc.setAttribute('content', light ? '#FAFAFA' : '#050505');
      }
      btn.addEventListener('click', function(){
        root.classList.toggle('light');
        storeSet('welcome-theme', root.classList.contains('light') ? 'light' : 'dark');
        sync();
        if (window.fitDeck) window.fitDeck();
      });
      sync();
    })();

    /* ===== Портрет ровно по ширине кнопки «Начать обучение» ===== */
    (function(){
      var photo = document.getElementById('cta-photo');
      var btn = document.getElementById('final-cta');
      if (!photo || !btn) return;
      window.sizePhoto = function(){
        var w = btn.offsetWidth, h = btn.offsetHeight;
        if (w > 40) {
          // Чуть у́же кнопки — чтобы плечи гарантированно не выходили за её края.
          var pw = Math.round(w * 0.92);
          photo.style.width = pw + 'px';
          photo.style.maxWidth = pw + 'px';
        }
        // Снимок заходит под кнопку до её середины: срез прячется, просвета нет.
        if (h > 20) photo.style.marginBottom = (-Math.round(h / 2)) + 'px';
      };
      window.sizePhoto();
    })();

    /* ===== Дек: один блок в фокусе ==========================================
       Ни страница, ни блок не прокручиваются. Колесо, свайп, стрелки и точки
       справа переключают блок целиком: гаснет один слой, зажигается другой,
       фон остаётся на месте. Блок, который не влезает в экран, ужимается
       целиком (fit) — резать содержимое и листать внутри блока нельзя. */
    (function(){
      var panels = [].slice.call(document.querySelectorAll('.panel'));
      var dotsBox = document.getElementById('dots');
      var idx = 0;
      var REDUCED = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      var SWITCH = REDUCED ? 120 : 380;      // сколько длится смена блока
      var busyUntil = 0, pending = -1, firedAt = 0;

      function now(){ return window.performance && performance.now ? performance.now() : Date.now(); }

      /* ---- Блок всегда помещается в экран целиком ----------------------------
         Считаем свободную высоту панели и, если содержимое выше, ужимаем .wrap
         масштабом (transform работает везде, в отличие от zoom) и сами ставим
         верхний отступ — margin:auto при переполнении уже не центрирует. */
      function fit(p){
        var w = p.querySelector('.wrap');
        if (!w) return;
        w.style.transform = '';
        w.style.transformOrigin = '';
        w.style.marginTop = '';
        w.style.marginBottom = '';
        var cs = window.getComputedStyle(p);
        var avail = p.clientHeight - parseFloat(cs.paddingTop || 0) - parseFloat(cs.paddingBottom || 0);
        var need = w.offsetHeight;
        if (!avail || !need || need <= avail + 1) return;
        // Ужимаем ровно настолько, насколько не хватает высоты. Пола нет
        // намеренно: любой пол означал бы обрезанный низ блока, а прокрутить
        // его нечем — колесо и свайп перехвачены декой.
        var k = avail / need;
        w.style.transformOrigin = 'top center';
        w.style.transform = 'scale(' + k + ')';
        w.style.marginTop = '0';
        w.style.marginBottom = '0';
      }
      var fitQueued = false;
      window.fitDeck = function(){
        if (fitQueued) return;
        fitQueued = true;
        (window.requestAnimationFrame || setTimeout)(function(){
          fitQueued = false;
          if (window.sizePhoto) window.sizePhoto();
          for (var i = 0; i < panels.length; i++) fit(panels[i]);
        }, 0);
      };

      var dots = panels.map(function(p, i){
        var b = document.createElement('button');
        b.className = 'dot';
        b.type = 'button';
        b.setAttribute('aria-label', p.getAttribute('aria-label') || ('' + (i + 1)));
        b.addEventListener('click', function(){ jump(i); });
        dotsBox.appendChild(b);
        return b;
      });

      function show(n){
        n = Math.max(0, Math.min(panels.length - 1, n));
        idx = n;
        panels.forEach(function(p, i){
          p.classList.toggle('on', i === idx);
          p.setAttribute('aria-hidden', i === idx ? 'false' : 'true');
        });
        dots.forEach(function(d, i){
          d.classList.toggle('on', i === idx);
          if (i === idx) d.setAttribute('aria-current', 'true'); else d.removeAttribute('aria-current');
        });
        // Якорь в адрес НЕ пишем: replaceState записей в историю не создаёт,
        // «назад» им всё равно не воспользуешься, а «#start» в адресной строке
        // выглядит мусором. Читать якорь при заходе продолжаем — ссылка вида
        // /automation/#skills откроет нужный блок.
      }

      /* Единственная точка входа для жестов: пока идёт смена блока, осознанное
         намерение не теряется, а откладывается до конца анимации. Хвост инерции
         сюда не доходит — его отсекает жестовый слой ниже. */
      function jump(n){
        var t = now();
        if (n < 0 || n > panels.length - 1) return;
        if (t < busyUntil){ if (n !== idx) pending = n; return; }
        if (n === idx) return;
        show(n);
        busyUntil = t + SWITCH;
        firedAt = t;
        disarmWheel();
        setTimeout(function(){
          var p = pending; pending = -1;
          if (p >= 0 && p !== idx) jump(p);
        }, SWITCH + 10);
      }
      function go(dir){ jump(idx + dir); }

      /* ---- Колесо и тачпад --------------------------------------------------
         Один осознанный жест = один блок. Инерция тачпада на macOS присылает
         десятки затухающих событий после взмаха: пока они затухают, ничего не
         делаем, а вот новый толчок (дельта перестала падать) снова взводит
         курок — иначе второй взмах подряд «проглатывался» и казалось, что
         страница дёрнулась и не переключилась. */
      var THRESH   = 42;     // накопленная прокрутка, дающая переключение
      var QUIET    = 170;    // пауза, после которой жест считается новым
      var REARM    = 260;    // раньше этого нового толчка не ищем — там ещё анимация
      var RISE_MIN = 12;     // дельта, ниже которой рост не считаем толчком
      var RISE_LEN = 3;      // столько СТРОГО растущих кадров подряд = новый взмах
      var COOL     = 500;    // жёсткий потолок: чаще этого колесо блок не меняет
      var accum = 0, lastT = 0, prevAbs = 0, armed = true, rise = 0, wheelAt = 0;

      function armWheel(){ armed = true; accum = 0; rise = 0; }
      // Любая смена блока — хоть колесом, хоть точкой, хоть клавишей — снимает
      // курок: иначе недоеденный хвост инерции доводил дек до следующего блока
      // уже ПОСЛЕ того, как зритель осознанно ткнул в нужную точку.
      function disarmWheel(){ armed = false; accum = 0; rise = 0; }

      window.addEventListener('wheel', function(e){
        if (e.ctrlKey) return;                    // ctrl+колесо — это зум браузера
        e.preventDefault();                       // ни страница, ни блок не едут
        var d = e.deltaY;
        if (e.deltaMode === 1) d *= 16;
        else if (e.deltaMode === 2) d *= window.innerHeight;
        var a = Math.abs(d);
        if (a < 1) return;
        if (Math.abs(e.deltaX) > a) return;       // горизонтальный жест — не наш
        var t = now(), gap = t - lastT;
        lastT = t;
        // Курок взводит либо пауза, либо НОВЫЙ ТОЛЧОК — три кадра подряд со
        // строго растущей дельтой. Нестрогое «не убывает» тут не годится:
        // инерция macOS приходит округлённой до целых, в хвосте появляются
        // плато (13,13,12,12), и на плато курок взводился сам — один мягкий
        // взмах уводил дек через два блока на третий. Взвода «по таймеру»
        // тоже быть не должно: хвост идёт кадрами по 16 мс, пауза не
        // набирается, и любой порог времени срабатывает на самом хвосте.
        if (gap > QUIET){ armWheel(); }
        else if (!armed && (t - firedAt) > REARM && a > prevAbs && a >= RISE_MIN){
          if (++rise >= RISE_LEN) armWheel();
        }
        else if (a <= prevAbs){ rise = 0; }
        prevAbs = a;
        if (!armed) return;
        accum += d;
        if (Math.abs(accum) >= THRESH){
          var dir = accum > 0 ? 1 : -1;   // направление СНАЧАЛА: disarm обнуляет accum
          disarmWheel();
          // Предохранитель поверх всей логики: сколько бы событий ни принёс
          // экзотический поток, чаще раза в COOL колесо блок не переключит.
          // Один взмах = один блок при любом раскладе.
          if (t - wheelAt < COOL) return;
          wheelAt = t;
          go(dir);
        }
      }, {passive:false});

      /* ---- Свайп ------------------------------------------------------------
         Срабатываем прямо во время движения пальца, как только он прошёл порог:
         ждать touchend — это те самые «полсекунды непонятно чего». */
      var tsX = null, tsY = null, tFired = false;
      window.addEventListener('touchstart', function(e){
        if (e.touches.length !== 1){ tsY = null; return; }
        tsX = e.touches[0].clientX;
        tsY = e.touches[0].clientY;
        tFired = false;
      }, {passive:true});
      window.addEventListener('touchmove', function(e){
        if (tsY === null || e.touches.length !== 1) return;
        e.preventDefault();                       // никакой «резинки» и оттяжки
        if (tFired) return;
        var dy = tsY - e.touches[0].clientY;
        var dx = tsX - e.touches[0].clientX;
        if (Math.abs(dx) > Math.abs(dy)) return;  // горизонтальный жест — не наш
        if (Math.abs(dy) < 48) return;
        tFired = true;
        go(dy > 0 ? 1 : -1);
      }, {passive:false});
      window.addEventListener('touchend', function(){ tsY = null; }, {passive:true});

      /* ---- Клавиатура ---------------------------------------------------- */
      document.addEventListener('keydown', function(e){
        if (e.metaKey || e.ctrlKey || e.altKey) return;   // системные сочетания — браузеру
        var k = e.key;
        // Пробел на кнопке или ссылке под фокусом — это нажатие, а не листание
        if (k === ' ' && e.target && e.target.closest && e.target.closest('button,a,input,textarea')) return;
        if (k === 'ArrowDown' || k === 'PageDown' || k === ' ') { e.preventDefault(); go(1); }
        else if (k === 'ArrowUp' || k === 'PageUp') { e.preventDefault(); go(-1); }
        else if (k === 'Home') { e.preventDefault(); jump(0); }
        else if (k === 'End') { e.preventDefault(); jump(panels.length - 1); }
      });

      var els = document.querySelectorAll('[data-go="next"]'), i;
      for (i = 0; i < els.length; i++) els[i].addEventListener('click', function(){ go(1); });

      window.addEventListener('resize', window.fitDeck);
      window.addEventListener('orientationchange', window.fitDeck);
      if (window.visualViewport) window.visualViewport.addEventListener('resize', window.fitDeck);
      window.addEventListener('load', window.fitDeck);
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(window.fitDeck);
      var photoEl = document.getElementById('cta-photo');
      if (photoEl) photoEl.addEventListener('load', window.fitDeck);

      var start = 0;
      if (location.hash){
        panels.forEach(function(p, i){ if ('#' + p.id === location.hash) start = i; });
      }
      show(start);
      window.fitDeck();
    })();
  </script>
</body>
</html>
"""

LANG_OPT = ('          <a class="lang-opt%(active)s" data-lang="%(code)s" href="%(href)s" '
            'hreflang="%(code)s"%(current)s>%(label)s</a>')
LANG_SEP = '          <span class="lang-sep" aria-hidden="true">|</span>'

ROLE_CARD = """          <article class="card role">
            <div class="ico %(tone)s"><i class="fa-solid %(icon)s"></i></div>
            <h3>%(title)s</h3>
            <p>%(text)s</p>
          </article>"""

SKILL_ITEM = ('          <li><span class="ico %(tone)s"><i class="fa-solid %(icon)s"></i></span>'
              '<p>%(text)s</p></li>')


def _lang_switch(cur):
    """EN | RU — активный язык помечен, соседний ведёт на свою страницу."""
    out = []
    for code in ("en", "ru"):
        active = code == cur["lang"]
        href = cur["path"] if active else cur["other_path"]
        out.append(LANG_OPT % {
            "active": " active" if active else "",
            "code": code,
            "href": href,
            "current": ' aria-current="true"' if active else "",
            "label": code.upper(),
        })
    return "\n".join([out[0], LANG_SEP, out[1]])


def render(cur):
    roles = "\n".join(
        ROLE_CARD % {"tone": tone, "icon": icon, "title": title, "text": text}
        for tone, icon, title, text in cur["roles"]
    )
    skills = "\n".join(
        SKILL_ITEM % {"tone": "p" if i % 2 == 0 else "f", "icon": SKILL_ICONS[i], "text": text}
        for i, text in enumerate(cur["skills"])
    )
    html = TEMPLATE
    subs = {
        "LANG": cur["lang"],
        "OTHER_PATH": cur["other_path"],
        "URL": cur["url"],
        "URL_EN": URL_EN,
        "URL_RU": URL_RU,
        "OG_LOCALE": cur["og_locale"],
        "OG_IMAGE": cur["og_image"],
        "OG_W": OG_W,
        "OG_H": OG_H,
        "OG_IMAGE_ALT": cur["og_image_alt"],
        "TITLE": cur["title"],
        "DESC": cur["desc"],
        "COURSE": COURSE,
        "HOME_LABEL": cur["home_label"],
        "LANG_GROUP": cur["lang_group"],
        "THEME_LABEL": cur["theme_label"],
        "CONSULT": cur["consult"],
        "CONSULT_LABEL": cur["consult_label"],
        "BLOCKS_LABEL": cur["blocks_label"],
        "START": cur["start"],
        "SCROLL": cur["scroll"],
        "A_COURSE": cur["a_course"],
        "A_ROLES": cur["a_roles"],
        "A_SKILLS": cur["a_skills"],
        "A_START": cur["a_start"],
        "HERO": cur["hero"],
        "HERO_DESC": cur["hero_desc"],
        "ROLES_H": cur["roles_h"],
        "SKILLS_H": cur["skills_h"],
        "FINAL_H": cur["final_h"],
        "FINAL_LEAD": cur["final_lead"],
        "LANG_SWITCH": _lang_switch(cur),
        "ROLE_CARDS": roles,
        "SKILL_ITEMS": skills,
    }
    for key, value in subs.items():
        html = html.replace("{{%s}}" % key, value)
    assert "{{" not in html, "в шаблоне остался незаполненный токен"
    return html


PAGES = (("automation/index.html", EN), ("automation_ru/index.html", RU))


def build():
    """Возвращает {путь: html} — файлы на диск не пишет."""
    return dict((rel, render(cur)) for rel, cur in PAGES)


def main():
    for rel, html in build().items():
        path = os.path.join(ROOT, rel)
        directory = os.path.dirname(path)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("собрано:", rel, len(html), "байт")


if __name__ == "__main__":
    main()
