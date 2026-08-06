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
    "start": "Начать обучение",
    "a_course": "О курсе",
    "a_roles": "Для кого этот курс",
    "a_skills": "Чему вы научитесь",
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
         'Находит процессы<br>для <span class="nb">ИИ-автоматизации</span>'),
        ("f", "fa-wrench", "ИИ-инженер по автоматизации",
         'Автоматизирует бизнес<br>с <span class="nb">ИИ-агентами</span>'),
        ("p", "fa-rocket", "ИИ-основатель",
         'Строит бизнес<br>с помощью <span class="nb">ИИ-агентов</span>'),
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
    "start": "Start learning",
    "a_course": "About the course",
    "a_roles": "Who this course is for",
    "a_skills": "What you will learn",
    "hero": ('<span class="line">Welcome to the course on</span>'
             '<span class="line"><span class="plum">business process automation</span></span>'
             '<span class="line">with <span class="flame">AI agents</span></span>'),
    "hero_desc": ("You will learn to transform your business into an AI-First company: "
                  '<br class="lb">automate processes with AI agents, scale without growing headcount, '
                  '<br class="lb">and achieve a measurable economic effect.'),
    "roles_h": 'Who <span class="plum">this course</span> is for',
    "roles": [
        ("p", "fa-compass", "AI Consultant", 'Finds processes<br>ready for <span class="nb">AI automation</span>'),
        ("f", "fa-wrench", "AI Automation Engineer", 'Automates business<br>with <span class="nb">AI agents</span>'),
        ("p", "fa-rocket", "AI Founder", 'Builds a business<br>powered by <span class="nb">AI agents</span>'),
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
    --tile-bg:#15151b;
  }
  html.light{
    --bg:#FAFAFA; --fg:#0A0A0A; --muted:rgba(10,10,10,.55);
    --card-bg:#fff; --card-border:rgba(0,0,0,.07);
    --divider:rgba(0,0,0,.10); --navitem:rgba(0,0,0,.55);
    --btn-bg:#0A0A0A; --btn-fg:#FAFAFA;
    --ctrl-bg:rgba(0,0,0,.03); --ctrl-border:rgba(0,0,0,.10); --ctrl-fg:rgba(0,0,0,.70);
    --tile-bg:#fff;
  }
  /* На белом фоне фирменный оранжевый выцветает (2.7:1), а вторичный текст
     проваливается ниже 4.5:1 — в светлой теме берём те же цвета потемнее. */
  html.light{ --muted:rgba(10,10,10,.62); }
  html.light .flame, html.light .ico.f{ color:#D9520A; }
  html.light .learn li:hover{ border-color:rgba(217,82,10,.45) }

  *{box-sizing:border-box}
  /* Обычная прокручиваемая страница: от «листания по блокам» отказались
     (правка заказчика). Блоки просто идут друг за другом, прокрутка плавная. */
  html{scroll-behavior:smooth}
  html,body{margin:0}
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

  /* ===== Шапка =============================================================
     Геометрия один в один с главной andre.technology: те же отступы шапки,
     тот же размер логотипа, тот же переключатель языка и та же правая кнопка.
     Роль бургера (круглая кнопка между языком и CTA) здесь играет переключатель
     темы — размеры у него бургерные, поэтому ряд собирается точно так же. */
  header{position:fixed;top:0;left:0;right:0;z-index:40;pointer-events:none;padding:1.1rem}
  @media(min-width:1024px){header{padding:2rem}}
  .header-row{position:relative;display:flex;align-items:center;justify-content:space-between;gap:.5rem}
  .header-left{pointer-events:auto;display:flex;align-items:center;gap:.5rem;min-width:0}
  .header-right{pointer-events:auto;display:flex;align-items:center;gap:.4rem;flex-shrink:0}

  .logo-btn{display:inline-flex;align-items:center;background:none;border:0;padding:0;cursor:pointer;flex-shrink:0}
  .logo-img{width:clamp(2.85rem,12vw,3.7rem);height:clamp(2.85rem,12vw,3.7rem);object-fit:contain;transition:transform .2s ease}
  @media(min-width:1024px){.logo-img{width:3.6rem;height:3.6rem}}
  .logo-btn:hover .logo-img{transform:scale(1.05)}

  /* Переключатель языка — как на главной: EN | RU, активный подсвечен.
     Здесь это ссылки: у каждого языка своя страница со своим веб-превью.
     На мобилке свободное место в шапке слева, поэтому переключатель уезжает
     туда (margin-right:auto), а круглая кнопка и CTA остаются прижаты вправо. */
  .lang-switch{display:flex;align-items:center;gap:.3rem;margin-right:clamp(.5rem,3.5vw,1.4rem);flex-shrink:0}
  @media(max-width:1023px){
    .header-right{flex:1 0 auto}
    .lang-switch{margin-left:clamp(.5rem,2.2vw,1.5rem);margin-right:auto}
  }
  .lang-opt{background:none;border:0;padding:.2rem .05rem;font-size:11px;font-weight:500;
    color:var(--navitem);letter-spacing:.08em;transition:color .2s ease;cursor:pointer}
  .lang-opt.active{color:var(--fg);font-weight:700}
  @media(hover:hover){.lang-opt:hover{color:var(--fg)}}
  .lang-sep{color:var(--divider);font-size:10px;user-select:none}
  @media(min-width:1024px){.lang-opt{font-size:12px}.lang-switch{margin-right:2rem}}
  @media(min-width:1024px) and (max-width:1319px){.lang-switch{gap:.12rem;margin-right:1rem}.lang-opt{font-size:11px;letter-spacing:0}}

  .ctrl{display:flex;align-items:center;justify-content:center;width:clamp(2.5rem,11vw,3.3rem);height:clamp(2.5rem,11vw,3.3rem);border-radius:999px;border:1px solid var(--ctrl-border);background:var(--ctrl-bg);color:var(--ctrl-fg);font-size:clamp(.95rem,3.2vw,1.15rem);line-height:1;flex-shrink:0;transition:background .2s ease}
  @media(min-width:1024px){.ctrl{width:2.85rem;height:2.85rem;font-size:1.05rem}}
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
  /* Правая кнопка шапки — те же размеры, что «Free AI Diagnostic» на главной */
  /* Кнопка шапки. Класс исторический (раньше вела на буткемп) — теперь это
     тот же вход в курс, что и кнопка внизу: призыв к действию на странице один. */
  .consult{padding:clamp(.7rem,2.4vw,1.05rem) clamp(1rem,3.6vw,1.6rem);font-size:clamp(11px,3.1vw,15px);letter-spacing:clamp(.06em,.4vw,.1em);gap:clamp(.4rem,1.2vw,.6rem)}
  @media(min-width:1024px){.consult{height:2.85rem;box-sizing:border-box;padding:0 1.6rem;font-size:14px;letter-spacing:.13em;gap:.55rem}}
  @media(min-width:1024px) and (max-width:1319px){.consult{padding:0 1.1rem;font-size:12px;letter-spacing:.08em;gap:.4rem}}
  @media(min-width:1320px) and (max-width:1479px){.consult{padding:0 1.35rem;font-size:13px;letter-spacing:.12em;gap:.5rem}}
  /* ≤380px — компактная шапка, как на главной: четыре элемента в строку иначе не влезают */
  @media(max-width:380px){
    header{padding:.85rem .6rem}
    .header-right{flex:0 0 auto;gap:.3rem}
    .lang-switch{margin-left:0;margin-right:.25rem;gap:.12rem}
    .lang-opt{font-size:10px;letter-spacing:.03em}
    .logo-img{width:2.5rem;height:2.5rem}
    .ctrl{width:2.3rem;height:2.3rem}
    .consult{padding:.62rem .7rem;font-size:10px;letter-spacing:.02em}
  }

  /* Широкие экраны: масштабируем весь UI (как на главном сайте) */
  @media(min-width:1600px){body{zoom:1.15}}
  @media(min-width:1900px){body{zoom:1.3}}
  @media(min-width:2300px){body{zoom:1.5}}

  /* ===== Блоки страницы =====
     Ритм страницы, а не «экран на блок»: min-height:100svh раздувал каждый
     блок до полной высоты окна и оставлял между ними провалы в 300-450px.
     Отступы такие же, как на странице буткемпа — блоки идут плотно и
     читаются подряд, обычной прокруткой. */
  .deck{position:relative;z-index:2}
  .panel{
    position:relative;display:flex;
    padding:clamp(1.8rem,4.5vh,2.8rem) 1rem;
  }
  .panel:first-child{padding-top:clamp(6.5rem,17vh,9rem)}
  .panel:last-child{padding-bottom:clamp(3.5rem,9vh,5.5rem)}
  @media(min-width:640px){.panel{padding-left:2rem;padding-right:2rem}}
  .wrap{margin:auto;width:100%;max-width:68rem;text-align:center}

  /* Появление содержимого — когда блок доехал до экрана (IntersectionObserver
     ставит класс .in). Пока блок не показывался, его содержимое приспущено. */
  .panel .wrap > *{opacity:0;transform:translateY(16px)}
  .panel.in .wrap > *{animation:riseIn .55s cubic-bezier(.22,1,.36,1) forwards}
  .panel.in .wrap > *:nth-child(2){animation-delay:.06s}
  .panel.in .wrap > *:nth-child(3){animation-delay:.12s}
  .panel.in .wrap > *:nth-child(4){animation-delay:.18s}
  .panel.in .wrap > *:nth-child(n+5){animation-delay:.24s}

  /* ===== Блок 1: о курсе ===== */
  /* zoom, а не transform: transform уменьшает только отрисовку, в потоке ряд
     продолжал занимать полную высоту — подгонка блока считала её и ужимала
     первый экран сильнее, чем требовалось. */
  .float-row{display:flex;justify-content:center;align-items:flex-end;gap:.85rem;zoom:.82;margin:0 0 .25rem}
  @media(min-width:640px){.float-row{zoom:1;margin-bottom:.85rem}}
  .tile{flex-shrink:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:var(--tile-bg);border:1px solid var(--card-border);border-radius:1rem;animation:floatY 4s ease-in-out infinite}
  .tile.sm{width:4rem;height:6rem;gap:.6rem}
  .tile.lg{width:5rem;height:7.3rem;gap:.65rem;border-radius:1.1rem}
  .tile .bar{height:3px;border-radius:2px}
  .tile.sm .bar{width:1.8rem}
  .tile.lg .bar{width:2.25rem}

  .hero{font-size:clamp(1.55rem,5vw,3.3rem);font-weight:800;text-transform:uppercase;line-height:1.12;letter-spacing:-.02em;padding-top:.5rem}
  .hero span.line{display:block}
  .hero .plum,.hero .flame{white-space:nowrap}
  .desc{color:var(--muted);max-width:min(62em,92vw);margin:1.35rem auto 0;font-size:clamp(15.5px,1.18vw,24px);line-height:1.6}
  .desc .lb{display:none}
  @media (min-width:680px){ .desc .lb{display:inline} }


  /* заголовки блоков */
  .h2{text-align:center;font-size:clamp(1.6rem,4.4vw,2.2rem);font-weight:800;text-transform:uppercase;letter-spacing:-.02em}
  @media(min-width:1024px){.h2{font-size:clamp(2.4rem,2.6vw,3.2rem)}}

  /* ===== Блок 2: для кого ===== */
  .roles{margin-top:1.8rem;display:grid;grid-template-columns:1fr;gap:1rem}
  @media(min-width:640px){.roles{grid-template-columns:repeat(3,1fr)}}
  .card{border:1px solid var(--card-border);background:var(--card-bg);border-radius:1rem;transition:transform .2s ease,border-color .2s ease}
  .card:hover{transform:translateY(-3px);border-color:rgba(136,84,243,.45)}
  .role{padding:1.7rem 1.45rem;text-align:center}
  .role .ico{margin:0 auto 1rem;display:inline-flex;align-items:center;justify-content:center;height:clamp(3.7rem,5vw,5rem);width:clamp(3.7rem,5vw,5rem);border-radius:1.1rem;font-size:clamp(1.6rem,2.2vw,2.2rem)}
  .ico.p{background:rgba(136,84,243,.15);color:#8854F3}
  .ico.f{background:rgba(249,115,22,.15);color:#F97316}
  .role h3{font-size:clamp(1.08rem,1.45vw,1.4rem);font-weight:700;text-transform:uppercase}
  /* Заголовок средней карточки занимает две строки — резерв даём всем трём,
     иначе описания в ряду начинаются с разной высоты. */
  @media(min-width:640px){.role h3{min-height:2.5em;display:flex;align-items:center;justify-content:center}}
  .role p{color:var(--muted);margin:.55rem 0 0;font-size:clamp(.85rem,1.1vw,1.05rem);line-height:1.6}
  .nb{white-space:nowrap}   /* «ИИ-агентами» не разрывается по дефису */

  /* ===== Блок 3: чему научитесь ===== */
  /* Номеров у пунктов нет: они ничего не сообщали, а резерв справа перекашивал
     строку. Отступы поэтому симметричные. */
  .learn{margin:1.8rem auto 0;max-width:67rem;display:grid;grid-template-columns:repeat(2,1fr);gap:.65rem;list-style:none;padding:0;text-align:left}
  @media(max-width:639px){.learn{grid-template-columns:1fr}}
  .learn li{position:relative;display:flex;align-items:center;gap:.8rem;padding:.8rem 1rem;border-radius:1rem;border:1px solid var(--card-border);background:var(--card-bg);transition:transform .2s ease,border-color .2s ease}
  .learn li:hover{transform:translateY(-2px);border-color:rgba(249,115,22,.45)}
  .learn .ico{height:clamp(2.4rem,3.3vw,3.1rem);width:clamp(2.4rem,3.3vw,3.1rem);border-radius:.65rem;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;font-size:clamp(1.1rem,1.55vw,1.5rem)}
  .learn p{margin:0;font-size:clamp(.85rem,1.45vw,1.1rem);line-height:1.4}

  /* ===== CTA ===== */
  .cta-row{margin:1.9rem 0 0;display:flex;justify-content:center}
  /* Кнопка на странице одна — она и есть главный акцент, поэтому крупнее
     прежних трёх одинаковых. */
  .btn-start{padding:clamp(1.3rem,1.45vw,2.1rem) clamp(2.7rem,3vw,4.6rem);font-size:clamp(15px,1.15vw,23px);letter-spacing:.15em}



  /* Телефон: тот же ритм, только плотнее и с узкими полями. */
  @media (max-width:639px){
    .panel{padding:clamp(1.4rem,4vh,2.2rem) 1.4rem}
    .panel:first-child{padding-top:clamp(5.2rem,13vh,6.4rem)}
    .panel:last-child{padding-bottom:clamp(2.6rem,7vh,3.6rem)}
    .desc{margin-top:1rem}
    .cta-row{margin-top:1.15rem}
    .roles{margin-top:1.2rem;gap:.65rem}
    .role{padding:1.05rem 1rem}
    .role .ico{height:2.9rem;width:2.9rem;margin-bottom:.6rem;font-size:1.25rem;border-radius:.9rem}
    .role p{margin-top:.35rem;line-height:1.5}
    .learn{margin-top:1.15rem;gap:.4rem}
    .learn li{padding:.55rem .8rem;gap:.65rem;border-radius:.8rem}
    .learn .ico{height:2.15rem;width:2.15rem;font-size:1rem;border-radius:.55rem}
    .learn p{font-size:.82rem;line-height:1.3}
  }
  /* Низкие окна отдельным правилом больше не ужимаем: блоки не обязаны
     влезать в экран, страница прокручивается обычным образом. */

  @media print{
    .panel{page-break-after:always}
    .panel .wrap > *{opacity:1;transform:none}
    header{display:none}
  }

  @media (prefers-reduced-motion: reduce){
    .panel .wrap > *{opacity:1;transform:none;animation:none}
    .tile{animation:none}
    .btn-white:hover{animation:none;transform:none}
  }
</style>
<noscript><style>
  /* Без скрипта появление блоков не запустится — показываем сразу. */
  .panel .wrap > *{opacity:1;transform:none}
  #theme{display:none}
</style></noscript>
</head>
<body>

  <div class="grain"></div>

  <!-- HEADER -->
  <header id="hdr">
    <div class="header-row">
      <div class="header-left">
        <button class="logo-btn" aria-label="{{HOME_LABEL}}" onclick="location.href='https://andre.technology'">
          <img class="logo-img" src="https://i.ibb.co/gn7SmgY/866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png" alt="Andre AI">
        </button>
      </div>
      <div class="header-right">
        <div class="lang-switch" role="group" aria-label="{{LANG_GROUP}}">
{{LANG_SWITCH}}
        </div>
        <button class="ctrl" id="theme" aria-label="{{THEME_LABEL}}"><i class="fa-solid fa-sun"></i></button>
        <button class="btn-white consult" onclick="location.href='{{COURSE}}'" aria-label="{{START}}">
          <span class="txt">{{START}}</span>
          <i class="fa-solid fa-arrow-right" style="font-size:.75rem"></i>
        </button>
      </div>
    </div>
  </header>

  <main class="deck" id="deck">

    <!-- ===== 1. О КУРСЕ ===== -->
    <section class="panel" id="course" aria-label="{{A_COURSE}}">
      <div class="wrap">
        <div class="float-row" aria-hidden="true">
          <div class="tile sm" style="border-color:rgba(136,84,243,.3)"><i class="fa-solid fa-magnifying-glass-chart" style="font-size:26px;color:#8854F3"></i><div class="bar" style="background:rgba(136,84,243,.5)"></div></div>
          <div class="tile lg" style="border-color:rgba(249,115,22,.5);animation-delay:.2s"><i class="fa-solid fa-robot" style="font-size:38px;color:#F97316"></i><div class="bar" style="background:rgba(249,115,22,.5)"></div></div>
          <div class="tile sm" style="border-color:rgba(136,84,243,.3);animation-delay:.4s"><i class="fa-solid fa-gears" style="font-size:26px;color:#8854F3"></i><div class="bar" style="background:rgba(136,84,243,.5)"></div></div>
        </div>
        <h1 class="hero" id="hero-h">{{HERO}}</h1>
        <p class="desc" id="hero-d">{{HERO_DESC}}</p>
      </div>
    </section>

    <!-- ===== 2. ДЛЯ КОГО ===== -->
    <section class="panel" id="roles" aria-label="{{A_ROLES}}">
      <div class="wrap">
        <h2 class="h2" id="roles-h">{{ROLES_H}}</h2>
        <div class="roles">
{{ROLE_CARDS}}
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

  </main>


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


    /* ===== Плавное появление блоков при прокрутке ======================
       Никакого перехвата колеса и свайпа: страница прокручивается как
       обычная. Наблюдатель включает каскад появления, когда блок доехал до
       экрана. */
    (function(){
      var panels = [].slice.call(document.querySelectorAll('.panel'));
      var REDUCED = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      if (!window.IntersectionObserver || REDUCED){
        panels.forEach(function(p){ p.classList.add('in'); });
      } else {
        var io = new IntersectionObserver(function(entries){
          entries.forEach(function(e){
            if (e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }
          });
        }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });
        panels.forEach(function(p){ io.observe(p); });
        // Первый экран показываем сразу, не дожидаясь события наблюдателя.
        if (panels[0]) panels[0].classList.add('in');
      }

      function goNext(from){
        var i = panels.indexOf(from);
        var next = panels[i + 1] || panels[panels.length - 1];
        if (next) next.scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth', block: 'start' });
      }
      var els = document.querySelectorAll('[data-go="next"]'), i;
      for (i = 0; i < els.length; i++){
        els[i].addEventListener('click', function(){
          var p = this.closest ? this.closest('.panel') : null;
          goNext(p || panels[0]);
        });
      }
    })();
  </script>

<!-- ГОВОРЯЩАЯ ГОЛОВА (кружок): та же механика и размер, что на /automation/main.
     Ролик — заглушка, заказчик заменит. Без звука не играет: стоит на кнопке
     ▶; если звук включали раньше на пути (welcome-audio) — стартует сам. -->
<style>
/* ===== Video bubble (talking head): tap = sound / play-pause, draggable — same as welcome ===== */
  .bubble{position:fixed;left:clamp(1.5rem,5vw,4rem);bottom:clamp(1.5rem,5vh,3rem);z-index:40;width:clamp(150px,13.6vw,196px);height:clamp(150px,13.6vw,196px);touch-action:none;user-select:none;-webkit-user-select:none}
  @media(max-width:768px){.bubble{left:15px;bottom:15px;width:120px;height:120px}}
  .bubble .inner{position:relative;height:100%;width:100%;border-radius:999px;overflow:hidden;box-shadow:0 30px 80px -20px rgba(0,0,0,.6);outline:1px solid rgba(255,255,255,.2);cursor:grab}
  .bubble.dragging .inner{cursor:grabbing}
  .bubble .grad{position:absolute;inset:0;z-index:0;background:linear-gradient(135deg,#8854F3 0%,#F97316 100%)}
  .bubble video{position:absolute;inset:0;z-index:1;width:100%;height:100%;object-fit:cover;transition:filter .25s ease,transform .25s ease}
  /* Пока ролик не играет — кадр стоит РАЗМЫТЫМ под кнопкой play (правка
     заказчика); scale прячет светлую кайму, которую blur тянет с краёв */
  .bubble.paused video{filter:blur(5px);transform:scale(1.08)}
  .bubble-sound{position:absolute;z-index:3;left:50%;bottom:8%;transform:translateX(-50%);display:inline-flex;align-items:center;justify-content:center;height:1.5rem;min-width:1.5rem;padding:0 .4rem;border-radius:999px;background:rgba(0,0,0,.45);color:#fff;font-size:.72rem;pointer-events:none;-webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px);transition:opacity .2s ease}
  .bubble.paused .bubble-sound{opacity:0}
  .bubble-play{position:absolute;inset:0;z-index:4;display:flex;align-items:center;justify-content:center;color:#fff;font-size:1.9rem;background:rgba(0,0,0,.28);-webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px);opacity:0;transition:opacity .2s ease;pointer-events:none}
  .bubble.paused .bubble-play{opacity:1}
/* Кружок справа, размеры как в лекциях */
.bubble{ left:auto; right:20px; /* БЕЗ !important: перетаскивание пишет инлайновый style.left, важность из CSS его глушила — кружок ходил только по вертикали */
  width:clamp(150px,13.6vw,196px) !important; height:clamp(150px,13.6vw,196px) !important; }
@media(max-width:768px){
  .bubble{ left:auto; right:12px; width:120px !important; height:120px !important; }
}
</style>
<div class="bubble muted" id="bubble" title="Перетащите кружок · клик — звук, затем пауза/воспроизведение">
    <div class="inner">
      <div class="grad"></div>
      <!-- Ролик входа в курс лежит в репозитории: внешний CDN отдавал 404 и
           кружок оставался пустым градиентом. Обложка стоит и постером, и
           фоном — дыры на месте кружка нет никогда. -->
      <video id="bubble-video" src="https://raw.githubusercontent.com/andre-kuzminykh/andre-ait-page/refs/heads/media/assets/video_sq/auto_welcome-sq.mp4" muted playsinline preload="auto"
             poster="/assets/video_sq/poster_welcome.jpg"
             style="background:#0A0A0A url(/assets/video_sq/poster_welcome.jpg) center/cover no-repeat"></video>
      <div class="bubble-sound" id="bubble-sound" aria-hidden="true"><svg viewBox="0 0 24 24" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M3 10v4h4l5 5V5L7 10H3z"/><path d="M15.6 8.6 14.2 10l2 2-2 2 1.4 1.4 2-2 2 2L21 14l-2-2 2-2-1.4-1.4-2 2z"/></svg></div>
      <div class="bubble-play" aria-hidden="true"><svg viewBox="0 0 24 24" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg></div>
    </div>
  </div>
<script>
(function(){
// ===== Video bubble: tap = sound, then play/pause; drag to move (same as welcome) =====
    (function(){
      var bubble = document.getElementById('bubble');
      var video  = document.getElementById('bubble-video');
      var sound  = document.getElementById('bubble-sound');
      if (!bubble || !video) return;

      // ONE journey-wide audio memory (same flag as welcome/roles/skills): if the user enabled
      // sound earlier in the path, the roadmap video starts WITH sound too (best-effort; falls back
      // to muted if the browser blocks unmuted autoplay — one tap re-enables).
      var WANT_SOUND = false;
      try { WANT_SOUND = localStorage.getItem('welcome-audio') === '1'; } catch (e) {}
      function rememberSound(){ try { localStorage.setItem('welcome-audio', '1'); } catch (e) {} }
      // Дорожная карта — конечная страница пути: голова договаривает своё и
      // замолкает, дальше выбирает пользователь. Зацикливать нельзя: на шагах
      // мастера ролик по окончании ведёт на следующий шаг, а здесь вести некуда,
      // и повтор превращался в бесконечно говорящую голову поверх списка модулей.
      video.loop = false; video.muted = !WANT_SOUND;
      // БЕЗ ЗВУКА НЕ ИГРАЕМ (правка заказчика): молчаливый ролик выглядел как
      // сломанный. Если звук включали на предыдущем шаге пути — пробуем
      // стартовать сразу СО ЗВУКОМ; если браузер запретил (NotAllowedError на
      // свежей странице) или флага нет — стоим на кнопке ▶, клик всё включит.
      function tryPlay(){
        if (video.muted){ bubble.classList.add('paused'); return; }
        var p = video.play && video.play();
        if (p && p.catch) p.catch(function(err){
          if (err && err.name === 'NotAllowedError'){ video.muted = true; video.pause(); bubble.classList.add('paused'); }
        });
      }
      tryPlay();
      video.addEventListener('loadedmetadata', tryPlay);
      video.addEventListener('loadeddata', tryPlay);
      video.addEventListener('canplay', tryPlay);
      function syncSound(){
        bubble.classList.toggle('muted', video.muted);
        if (sound) sound.innerHTML = video.muted ? '<svg viewBox="0 0 24 24" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M3 10v4h4l5 5V5L7 10H3z"/><path d="M15.6 8.6 14.2 10l2 2-2 2 1.4 1.4 2-2 2 2L21 14l-2-2 2-2-1.4-1.4-2 2z"/></svg>' : '<svg viewBox="0 0 24 24" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M3 10v4h4l5 5V5L7 10H3z"/><path d="M14.5 12c0-1.8-1-3.3-2.5-4v8c1.5-.7 2.5-2.2 2.5-4z"/><path d="M12 3.2v2.1c2.9.9 5 3.6 5 6.7s-2.1 5.8-5 6.7v2.1c4-.9 7-4.5 7-8.8s-3-7.9-7-8.8z"/></svg>';
      }
      video.addEventListener('play',  function(){ bubble.classList.remove('paused'); });
      video.addEventListener('pause', function(){ bubble.classList.add('paused'); });
      // Договорил — показываем ▶, чтобы кружок не выглядел зависшим и ролик
      // можно было пересмотреть. Отдельно от 'pause': по спецификации порядок
      // событий в конце воспроизведения зависит от браузера.
      video.addEventListener('ended', function(){ try { video.currentTime = 0; } catch (e) {} bubble.classList.add('paused'); });
      video.addEventListener('volumechange', syncSound);
      syncSound();
      // safety net: show ▶ only if playback genuinely never started (rare with the muted fallback)
      setTimeout(function(){ if (video.paused && video.currentTime < 0.1) bubble.classList.add('paused'); }, 2500);

      // tap: first turn the SOUND on (unmute — allowed inside the user gesture); then toggle play/pause
      function onTap(){
        if (video.muted){ video.muted = false; rememberSound(); try { video.currentTime = 0; } catch (e) {} var q = video.play(); if (q && q.catch) q.catch(function(){}); } // включили звук → видео с начала
        else if (video.paused){ var p2 = video.play(); if (p2 && p2.catch) p2.catch(function(){}); }
        else video.pause();
      }

      // body{zoom} on big screens scales fixed elements: clientX / getBoundingClientRect are in
      // RENDERED px while style.left is in LAYOUT px — reconcile via the measured zoom factor.
      function zoomF(){ var r=bubble.getBoundingClientRect(); return (r.width && bubble.offsetWidth) ? r.width/bubble.offsetWidth : 1; }
      // pointer drag; a tap (no real movement) triggers onTap (sound / play-pause)
      var down=false, moved=false, sx=0, sy=0, ox=0, oy=0, TH=6;
      bubble.addEventListener('pointerdown', function(e){
        down=true; moved=false; sx=e.clientX; sy=e.clientY;
        var r=bubble.getBoundingClientRect(), z=zoomF(); ox=r.left; oy=r.top;
        bubble.style.left=(r.left/z)+'px'; bubble.style.top=(r.top/z)+'px';
        bubble.style.right='auto'; bubble.style.bottom='auto';
        if (bubble.setPointerCapture){ try { bubble.setPointerCapture(e.pointerId); } catch (err) {} }
      });
      bubble.addEventListener('pointermove', function(e){
        if (!down) return;
        var dx=e.clientX-sx, dy=e.clientY-sy;
        if (!moved && (Math.abs(dx)>TH || Math.abs(dy)>TH)){ moved=true; bubble.classList.add('dragging'); }
        if (moved){
          var z=zoomF(), rw=bubble.offsetWidth*z, rh=bubble.offsetHeight*z;
          var nx=Math.min(Math.max(0, ox+dx), window.innerWidth  - rw);
          var ny=Math.min(Math.max(0, oy+dy), window.innerHeight - rh);
          bubble.style.left=(nx/z)+'px'; bubble.style.top=(ny/z)+'px';
        }
      });
      function endDrag(){ if (!down) return; down=false; bubble.classList.remove('dragging'); if (!moved) onTap(); }
      bubble.addEventListener('pointerup', endDrag);
      bubble.addEventListener('pointercancel', endDrag);

      window.addEventListener('resize', function(){
        if (!bubble.style.left) return;
        var z=zoomF(), rw=bubble.offsetWidth*z, rh=bubble.offsetHeight*z;
        var lx=Math.max(0,Math.min(parseFloat(bubble.style.left)*z, window.innerWidth  - rw));
        var ly=Math.max(0,Math.min(parseFloat(bubble.style.top)*z,  window.innerHeight - rh));
        bubble.style.left=(lx/z)+'px'; bubble.style.top=(ly/z)+'px';
      });
    })();
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
        "START": cur["start"],
        "A_COURSE": cur["a_course"],
        "A_ROLES": cur["a_roles"],
        "A_SKILLS": cur["a_skills"],
        "HERO": cur["hero"],
        "HERO_DESC": cur["hero_desc"],
        "ROLES_H": cur["roles_h"],
        "SKILLS_H": cur["skills_h"],
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
