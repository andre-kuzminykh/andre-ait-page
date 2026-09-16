# -*- coding: utf-8 -*-
"""Собирает лендинг Andre AI Strategy на двух языках из одного шаблона.

    python3 tools/build_strategy.py        # пишет strategy/index.html и strategy/ru/index.html

Почему генератор, а не два рукописных файла: страница огромная (15 разделов,
10 сцен продукта), и держать две копии вручную — гарантированно развести их.
Вёрстка в assets/strategy.css, поведение в assets/strategy.js; здесь только
структура и тексты. Точек в конце строк нет — правило владельца.
"""
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Навигация: восемь разделов продукта + иконки для мобильного меню ──────
NAV = [
    ("questions",   "fa-circle-question"),
    ("businesses",  "fa-city"),
    ("deliverables", "fa-box-open"),
    ("process",     "fa-diagram-project"),
    ("model",       "fa-sitemap"),
    ("learning",    "fa-graduation-cap"),
    ("pricing",     "fa-tag"),
    ("start",       "fa-rocket"),
]

BIZ_ICONS = ["fa-briefcase", "fa-user-tie", "fa-bullhorn", "fa-pen-nib",
             "fa-headset", "fa-life-ring", "fa-palette", "fa-code"]

OUT_ICONS = ["fa-gauge-high", "fa-diagram-project", "fa-map", "fa-lightbulb",
             "fa-people-arrows", "fa-wand-magic-sparkles", "fa-id-card", "fa-route"]


def radar_points(values, cx=100, cy=98, r=74):
    """Семиугольник зрелости: значения 0..1 по семи осям."""
    pts = []
    for i, v in enumerate(values):
        a = -math.pi / 2 + i * 2 * math.pi / len(values)
        pts.append("%.1f,%.1f" % (cx + math.cos(a) * r * v, cy + math.sin(a) * r * v))
    return " ".join(pts)


def radar_axes(n=7, cx=100, cy=98, r=74):
    out = []
    for i in range(n):
        a = -math.pi / 2 + i * 2 * math.pi / n
        out.append('<line class="axis" x1="%d" y1="%d" x2="%.1f" y2="%.1f"/>'
                   % (cx, cy, cx + math.cos(a) * r, cy + math.sin(a) * r))
    return "".join(out)


def radar_ring(k, n=7, cx=100, cy=98, r=74):
    pts = []
    for i in range(n):
        a = -math.pi / 2 + i * 2 * math.pi / n
        pts.append("%.1f,%.1f" % (cx + math.cos(a) * r * k, cy + math.sin(a) * r * k))
    return '<polygon class="grid-l" points="%s"/>' % " ".join(pts)


def stages(t):
    """Десять сцен: упрощённый, но настоящий интерфейс продукта."""
    s = t["stage"]
    out = []

    # 01 — диагностика зрелости
    dims = s["dims"]
    vals = [0.62, 0.38, 0.55, 0.44, 0.28, 0.5, 0.46]
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot p"></span><span class="ui-dot o"></span>{bar}</div>
        <div class="ui-body" style="display:grid; gap:1.2rem; grid-template-columns:minmax(0,1fr) minmax(0,1fr); align-items:center;">
          <div>
            <svg class="radar" viewBox="0 0 200 200" role="img" aria-label="{bar}">
              {rings}{axes}
              <polygon class="shape" points="{pts}"/>
              <circle class="weak" cx="{wx}" cy="{wy}" r="4"/>
            </svg>
          </div>
          <div>
            <div class="rows">{rows}</div>
            <div class="idx"><b>2.4</b><span>/ 5 &middot; {index}</span></div>
            <p class="muted" style="margin-top:.7rem">{weak}</p>
          </div>
        </div>
      </div>""".format(
        bar=s["s1_bar"], index=s["s1_index"], weak=s["s1_weak"],
        rings="".join(radar_ring(k) for k in (0.33, 0.66, 1.0)),
        axes=radar_axes(), pts=radar_points(vals),
        wx=100 + math.cos(-math.pi / 2 + 4 * 2 * math.pi / 7) * 74 * vals[4],
        wy=98 + math.sin(-math.pi / 2 + 4 * 2 * math.pi / 7) * 74 * vals[4],
        rows="".join(
            '<div class="row"><b>%s</b><div class="meter" style="--v:%d%%; flex:1; max-width:7rem"><i></i></div></div>'
            % (d, int(v * 100)) for d, v in zip(dims, vals))))

    # 02 — «просто расскажите»
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot p"></span>{bar}</div>
        <div class="ui-body">
          <div class="wave">{bars}</div>
          <p class="typing" style="margin:1rem 0 1.2rem">{quote}<span class="caret"></span></p>
          <div style="display:grid; gap:.5rem; grid-template-columns:repeat(3,1fr)">
            {cards}
          </div>
        </div>
      </div>""".format(
        bar=s["s2_bar"], quote=s["s2_quote"],
        bars="".join('<span style="animation-delay:%.2fs"></span>' % (i * 0.08) for i in range(16)),
        cards="".join('<div class="node ai" data-seq style="justify-content:center"><i class="fa-solid fa-diagram-project"></i>%s</div>' % c
                      for c in s["s2_cards"])))

    # 03 — процессы найдены
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot p"></span>{bar}</div>
        <div class="ui-body">
          <div style="display:grid; gap:.5rem; grid-template-columns:repeat(2,1fr)">{cards}</div>
          <div class="legend" style="margin-top:1rem">
            <span><i class="fa-solid fa-pen"></i> {rename}</span>
            <span><i class="fa-solid fa-plus"></i> {add}</span>
            <span><i class="fa-solid fa-trash"></i> {delete}</span>
            <span><i class="fa-solid fa-grip-vertical"></i> {drag}</span>
          </div>
        </div>
      </div>""".format(
        bar=s["s3_bar"], rename=s["s3_rename"], add=s["s3_add"], delete=s["s3_delete"], drag=s["s3_drag"],
        cards="".join('<div class="node" data-seq><i class="fa-solid fa-grip-vertical"></i>%s</div>' % c
                      for c in s["s3_cards"])))

    # 04 — процесс раскрыт в операции
    ops = s["s4_ops"]
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot o"></span>{bar}</div>
        <div class="ui-body" style="display:grid; gap:1rem; grid-template-columns:minmax(0,.95fr) minmax(0,1.05fr)">
          <div class="chain">{chain}</div>
          <div style="border-left:1px solid rgba(255,255,255,.08); padding-left:1rem">
            <p class="muted" style="margin-bottom:.6rem; letter-spacing:.14em; text-transform:uppercase">{panel}</p>
            <div class="rows">{rows}</div>
          </div>
        </div>
      </div>""".format(
        bar=s["s4_bar"], panel=s["s4_panel"],
        chain="".join(
            ('<div class="node%s" data-seq><i class="fa-solid fa-circle-dot"></i>%s</div>' % (" glow" if i == 1 else "", o))
            + ('<div class="arrow">&darr;</div>' if i < len(ops) - 1 else "")
            for i, o in enumerate(ops)),
        rows="".join('<div class="row"><b>%s</b><span>%s</span></div>' % (k, v) for k, v in s["s4_fields"])))

    # 05 — когнитивная разведка
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot p"></span>{bar}</div>
        <div class="ui-body">
          <div class="node human glow" style="justify-content:center; margin-bottom:1rem"><i class="fa-solid fa-user"></i>{node}</div>
          <div style="display:grid; gap:.45rem">{qs}</div>
          <div class="arrow" style="text-align:center; margin:.7rem 0; color:rgba(255,255,255,.3)">&darr;</div>
          <div class="node ai" data-seq style="justify-content:center"><i class="fa-solid fa-brain"></i>{logic}</div>
        </div>
      </div>""".format(
        bar=s["s5_bar"], node=s["s5_node"], logic=s["s5_logic"],
        qs="".join('<div class="chip" data-seq style="width:100%%; justify-content:flex-start"><i class="fa-solid fa-circle-question"></i>%s</div>' % q
                   for q in s["s5_qs"])))

    # 06 — карта AS-IS
    def map_nodes(items, extra=""):
        return "".join('<div class="node %s" data-seq%s><i class="fa-solid %s"></i>%s</div>' % (kind, extra, ic, label)
                       for kind, ic, label in items)

    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot"></span>{bar}</div>
        <div class="ui-body">
          <div class="map">{nodes}</div>
          <div class="legend">
            <span><i style="background:#cbd5e1"></i>{human}</span>
            <span><i style="background:var(--o)"></i>{system}</span>
            <span><i style="background:rgba(255,255,255,.35)"></i>{doc}</span>
            <span><i style="background:var(--p)"></i>{bottleneck}</span>
          </div>
        </div>
      </div>""".format(bar=s["s6_bar"], human=s["l_human"], system=s["l_system"], doc=s["l_doc"],
                       bottleneck=s["l_bottleneck"], nodes=map_nodes(s["s6_nodes"])))

    # 07 — возможности ИИ
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot p"></span>{bar}</div>
        <div class="ui-body">
          <div class="map">{nodes}</div>
          <div style="display:flex; flex-wrap:wrap; gap:.4rem; margin-top:1rem">
            <span class="chip p"><i class="fa-solid fa-bolt"></i>{impact}</span>
            <span class="chip o"><i class="fa-solid fa-layer-group"></i>{complexity}</span>
            <span class="chip p" style="margin-left:auto"><i class="fa-solid fa-wand-magic-sparkles"></i>{automate}</span>
          </div>
        </div>
      </div>""".format(bar=s["s7_bar"], impact=s["s7_impact"], complexity=s["s7_complexity"],
                       automate=s["s7_automate"], nodes=map_nodes(s["s7_nodes"])))

    # 08 — роль человека
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot p"></span><span class="ui-dot o"></span>{bar}</div>
        <div class="ui-body">
          <div class="node ai" style="justify-content:center; margin-bottom:.9rem"><i class="fa-solid fa-robot"></i>{op}</div>
          <div style="display:grid; gap:.45rem; grid-template-columns:repeat(2,1fr)">{roles}</div>
          <div class="chain" style="margin-top:1rem">
            <div class="node ai" data-seq><i class="fa-solid fa-robot"></i>{flow1}</div>
            <div class="arrow">&darr;</div>
            <div class="node doc" data-seq><i class="fa-solid fa-file-lines"></i>{flow2}</div>
            <div class="arrow">&darr;</div>
            <div class="node human glow" data-seq><i class="fa-solid fa-user-check"></i>{flow3}</div>
          </div>
        </div>
      </div>""".format(bar=s["s8_bar"], op=s["s8_op"], flow1=s["s8_flow"][0], flow2=s["s8_flow"][1], flow3=s["s8_flow"][2],
                       roles="".join('<div class="chip%s" data-seq style="width:100%%; justify-content:center">%s</div>'
                                     % (" p" if i == 1 else "", r) for i, r in enumerate(s["s8_roles"]))))

    # 09 — AS-IS → TO-BE (сцена сама переключается)
    out.append("""
      <div class="ui" data-transform>
        <div class="ui-bar">
          <span class="ui-dot p"></span>
          <span class="tag-asis">{asis}</span><span style="color:rgba(255,255,255,.3)">&rarr;</span><span class="tag-tobe">{tobe}</span>
        </div>
        <div class="ui-body">
          <div class="map">{nodes}</div>
          <p class="muted" style="margin-top:1rem">{caption}</p>
        </div>
      </div>""".format(
        bar="", asis=s["s9_asis"], tobe=s["s9_tobe"], caption=s["s9_caption"],
        nodes="".join('<div class="node %s %s"><i class="fa-solid %s"></i>%s</div>' % (kind, state, ic, label)
                      for kind, state, ic, label in s["s9_nodes"])))

    # 10 — паспорт агента
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot p"></span>{bar}</div>
        <div class="ui-body">
          <h3 style="margin-bottom:.9rem">{name}</h3>
          {rows}
        </div>
      </div>""".format(bar=s["s10_bar"], name=s["s10_name"],
                       rows="".join('<div class="passport-row" data-seq><b>%s</b><span>%s</span></div>' % (k, v)
                                    for k, v in s["s10_fields"])))
    return out


def page(t, lang):
    other = "ru" if lang == "en" else "en"
    other_href = "/strategy/ru/" if lang == "en" else "/strategy/"
    self_href = "/strategy/" if lang == "en" else "/strategy/ru/"
    video = "/assets/Andre_AIT_video_compressed%s.mp4" % ("" if lang == "en" else "_ru")

    nav_html = "".join(
        '<button class="nav-tab" data-go="{id}" style="--ic:{c}"><span class="nav-ic"><i class="fa-solid {ic}"></i></span>'
        '<span class="nav-label">{label}</span><span class="nav-go"><i class="fa-solid fa-arrow-right"></i></span></button>'.format(
            id=sec, ic=icon, label=t["nav"][i], c="#8854F3" if i % 2 == 0 else "#F97316")
        for i, (sec, icon) in enumerate(NAV))

    phrases = "".join('<div class="phrase{cls}">{txt}</div>'.format(
        cls=" answer" if i == len(t["hero_phrases"]) - 1 else "", txt=p) for i, p in enumerate(t["hero_phrases"]))

    questions = "".join('<div class="q-item">%s</div>' % q for q in t["questions"])
    dots = "".join('<span class="qs-dot"></span>' for _ in t["questions"])

    nums = "".join(
        '<div class="num-card reveal"><span class="num-val">{v}</span><p>{p}</p></div>'.format(v=v, p=p)
        for v, p in t["numbers"])

    chips = "".join('<span class="orbit-chip">%s</span>' % c for c in t["promise_chips"])

    biz = "".join("""
        <article class="biz reveal">
          <div class="biz-ic"><i class="fa-solid {ic}"></i></div>
          <h3>{name}</h3>
          <div><p class="biz-label">{ops_l}</p><p class="biz-ops">{ops}</p></div>
          <div><p class="biz-label">{met_l}</p><div class="biz-metrics">{metrics}</div></div>
          <span class="biz-go">{explore} <i class="fa-solid fa-arrow-right"></i></span>
        </article>""".format(
        ic=BIZ_ICONS[i], name=b[0], ops=b[1], metrics="".join("<span>%s</span>" % m for m in b[2]),
        ops_l=t["biz_ops_label"], met_l=t["biz_metrics_label"], explore=t["biz_explore"])
        for i, b in enumerate(t["businesses"]))

    outs = "".join("""
        <article class="out">
          <span class="out-n">{n:02d}</span>
          <h3><i class="fa-solid {ic}" style="margin-right:.5rem; color:var(--p-l)"></i>{name}</h3>
          <p>{desc}</p>
        </article>""".format(n=i + 1, ic=OUT_ICONS[i], name=o[0], desc=o[1])
        for i, o in enumerate(t["deliverables"]))

    stage_html = stages(t)
    steps = "".join("""
        <article class="story-step reveal" data-step="{n}" style="--n:{n}">
          <p class="step-n">{n:02d} &mdash; {tag}</p>
          <h2>{title}</h2>
          <p>{body}</p>
          {note}
        </article>""".format(n=i + 1, tag=st[0], title=st[1], body=st[2],
                             note='<p class="step-note">%s</p>' % st[3] if st[3] else "")
        for i, st in enumerate(t["steps"]))
    stage_cards = "".join('<div class="stage-card" data-step="{n}" style="--n:{n}">{html}</div>'.format(n=i + 1, html=h)
                          for i, h in enumerate(stage_html))
    rail = "".join('<button class="rail-n" data-step="%d">%02d</button>' % (i + 1, i + 1) for i in range(len(t["steps"])))

    model = "".join('<div class="node %s reveal"><i class="fa-solid %s"></i>%s</div>'
                    % (k, ic, n) for k, ic, n in t["model_nodes"])

    learn = "".join('<div class="learn-step reveal"><span>%s</span><b>%s</b><p class="muted">%s</p></div>'
                    % (a, b, c) for a, b, c in t["learn_steps"])

    costs = "".join('<div class="cost-col{win} reveal"><h3>{h}</h3><span class="cost-val">{v}</span><p>{p}</p></div>'.format(
        win=" win" if i == 2 else "", h=c[0], v=c[1], p=c[2]) for i, c in enumerate(t["cost_cols"]))

    plans = "".join("""
        <article class="plan{best} reveal">
          {badge}
          <h3>{name}</h3>
          <div class="plan-price">{price}</div>
          <div class="plan-scope">{scope}</div>
          <p>{desc}</p>
          <a class="btn btn-{style} btn-sm" href="{cta_href}">{cta}</a>
          {hint}
        </article>""".format(
        best=" best" if p[0] == "best" else "", name=p[1], price=p[2], scope=p[3], desc=p[4],
        badge='<span class="plan-badge">%s</span>' % t["best_value"] if p[0] == "best" else "",
        hint='<span class="plan-hint">%s</span>' % t["best_hint"] if p[0] == "best" else "",
        style="primary" if p[0] == "best" else "ghost", cta=p[5], cta_href=t["cta_href"])
        for p in t["plans"])

    flow = "".join('<span>%s</span>%s' % (f, '<i class="fa-solid fa-arrow-right"></i>' if i < len(t["final_flow"]) - 1 else "")
                   for i, f in enumerate(t["final_flow"]))

    final_list = "".join('<div><i class="fa-solid fa-circle"></i><span>%s</span></div>' % f for f in t["final_list"])

    return """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#050505">
<meta name="color-scheme" content="dark">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://andre.technology{self_href}">
<link rel="alternate" hreflang="en" href="https://andre.technology/strategy/">
<link rel="alternate" hreflang="ru" href="https://andre.technology/strategy/ru/">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:url" content="https://andre.technology{self_href}">
<meta property="og:site_name" content="Andre AI Technologies">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://andre.technology/assets/og/andre-ai-technologies.png">
<meta name="twitter:card" content="summary_large_image">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet" media="print" onload="this.media='all';this.onload=null">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" media="print" onload="this.media='all';this.onload=null">
<noscript>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</noscript>
<link rel="stylesheet" href="/assets/strategy.css">
</head>
<body>

<div class="progress" id="progress" aria-hidden="true"></div>

<!-- ===== Говорящая голова: колонка на вебе, кружок ниже и на мобилке ===== -->
<div class="head" id="head" role="button" tabindex="0" aria-label="{video_aria}">
  <video id="head-video" src="{video}" poster="/andre_ai.jpg" loop muted autoplay playsinline preload="auto"></video>
  <div class="head-shade" aria-hidden="true"></div>
  <div class="head-play" aria-hidden="true"><i class="fa-solid fa-circle-play"></i></div>
</div>
<div class="head-badge"><b>Andre AI</b><span>{role}</span><i><i class="fa-solid fa-microphone-lines-slash" id="head-mic"></i></i></div>
<div class="phrases" aria-hidden="true">{phrases}</div>

<!-- ===== Шапка ===== -->
<header>
  <div class="header-row">
    <div class="header-left">
      <button class="back" id="back-btn" type="button" aria-label="{back}"><i class="fa-solid fa-arrow-left"></i></button>
      <a class="logo-btn" href="/" aria-label="Andre AI Technologies">
        <img class="logo-img" src="https://i.ibb.co/gn7SmgY/866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png" alt="AIT">
        <span class="prod-name">Andre <span>AI Strategy</span></span>
      </a>
    </div>

    <nav class="nav" id="nav" aria-label="{sections}">
      <button class="nav-close" id="nav-close" aria-label="{close}"><i class="fa-solid fa-xmark"></i></button>
      <div class="nav-brand" aria-hidden="true">
        <img src="https://i.ibb.co/gn7SmgY/866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png" alt="">
        <span>Andre AI Strategy</span>
      </div>
      {nav_html}
    </nav>

    <div class="header-right">
      <div class="lang-switch" role="group" aria-label="Language">
        {lang_switch}
      </div>
      <button class="menu-btn" id="menu-btn" aria-label="{menu}"><i id="menu-icon" class="fa-solid fa-bars"></i></button>
      <a class="btn btn-primary cta-head" href="{cta_href}" rel="noopener">{cta_top}</a>
    </div>
  </div>
</header>

<main>

<!-- ===== 1. HERO ===== -->
<section class="hero" id="top">
  <div class="wrap">
    <p class="eyebrow">Andre AI Strategy</p>
    <h1>{h1}</h1>
    <p class="lead">{hero_lead}</p>
    <p>{hero_body}</p>
    <div class="hero-cta">
      <a class="btn btn-primary" href="{cta_href}" rel="noopener">{cta_main} <i class="fa-solid fa-arrow-right"></i></a>
      <button class="btn btn-ghost" data-go-hero="process" type="button">{cta_how}</button>
    </div>
    <div class="hero-note">{hero_notes}</div>
  </div>
</section>

<!-- ===== 2. Вопросы ===== -->
<section class="qs" id="questions">
  <div class="qs-stage">
    <div class="qs-head"><h2>{q_head}</h2></div>
    <div class="qs-list">{questions}</div>
    <div class="qs-final"><h2>{q_final}</h2></div>
    <div class="qs-dots">{dots}</div>
  </div>
</section>

<!-- ===== 3. Цифры рынка ===== -->
<section class="sec" id="numbers">
  <div class="wrap">
    <p class="eyebrow o reveal">{n_eyebrow}</p>
    <h2 class="reveal">{n_head}</h2>
    <div class="nums">{nums}</div>
    <div class="nums-foot reveal"><p>{n_foot}</p></div>
    <div class="verdict reveal"><h2>{n_verdict}</h2></div>
    <p class="foot-note reveal">{n_note}</p>
  </div>
</section>

<!-- ===== 4. Простое обещание ===== -->
<section class="sec center" id="promise">
  <div class="wrap">
    <h2 class="reveal">{p_head}</h2>
    <p class="lead reveal" style="max-width:38rem; margin:1.2rem auto 0">{p_sub}</p>
    <div class="promise-orbit" id="orbit">
      {chips}
      <div class="orbit-core"><b>{p_core}</b></div>
    </div>
  </div>
</section>

<!-- ===== 5. Под ваш бизнес ===== -->
<section class="sec" id="businesses">
  <div class="wrap">
    <p class="eyebrow reveal">{b_eyebrow}</p>
    <h2 class="reveal">{b_head}</h2>
    <p class="lead reveal" style="max-width:40rem; margin-top:1rem">{b_sub}</p>
    <div class="biz-grid">{biz}</div>
    <div class="biz-more reveal">
      <a class="btn btn-ghost" href="{cta_href}">{b_all} <i class="fa-solid fa-arrow-right"></i></a>
      <p class="biz-arch">{b_arch}</p>
      <p class="muted" style="max-width:40rem">{b_metrics_note}</p>
    </div>
  </div>
</section>

<!-- ===== 6. Что вы получаете ===== -->
<section class="sec" id="deliverables">
  <div class="wrap">
    <p class="eyebrow o reveal">{d_eyebrow}</p>
    <h2 class="reveal">{d_head}</h2>
    <p class="lead reveal" style="max-width:40rem; margin-top:1rem">{d_sub}</p>
    <div class="rail">{outs}</div>
    <p class="rail-hint reveal"><i class="fa-solid fa-arrows-left-right"></i> {d_hint}</p>
  </div>
</section>

<!-- ===== 7. Как это работает: десять шагов ===== -->
<section class="sec" id="process">
  <div class="wrap">
    <p class="eyebrow reveal">{s_eyebrow}</p>
    <h2 class="reveal">{s_head}</h2>
    <p class="lead reveal" style="max-width:40rem; margin-top:1rem">{s_sub}</p>
  </div>
  <div class="wrap story">
    <div class="story-inner">
      <aside class="story-rail" aria-hidden="true">{rail}</aside>
      <div class="story-steps">{steps}</div>
      <div class="story-stage">{stage_cards}</div>
    </div>
  </div>
</section>

<!-- ===== 8. Модель компании ===== -->
<section class="sec" id="model">
  <div class="wrap center">
    <p class="eyebrow reveal">{m_eyebrow}</p>
    <h2 class="reveal">{m_head}</h2>
    <p class="lead reveal" style="max-width:40rem; margin:1rem auto 0">{m_sub}</p>
    <div class="model-map">{model}</div>
  </div>
</section>

<!-- ===== 9. Команда ===== -->
<section class="sec" id="team">
  <div class="wrap">
    <p class="eyebrow o reveal">{t_eyebrow}</p>
    <h2 class="reveal">{t_head}</h2>
    <div class="team-split">
      <div class="team-col p reveal from-l"><h3><i class="fa-solid fa-user-tie" style="margin-right:.5rem"></i>{t_l_head}</h3><p>{t_l_body}</p></div>
      <div class="team-join reveal"><i class="fa-solid fa-arrows-left-right"></i></div>
      <div class="team-col o reveal from-r"><h3><i class="fa-solid fa-users" style="margin-right:.5rem"></i>{t_r_head}</h3><p>{t_r_body}</p></div>
    </div>
    <p class="lead reveal" style="margin-top:1.6rem">{t_foot}</p>
  </div>
</section>

<!-- ===== 10. Обучение ===== -->
<section class="sec" id="learning">
  <div class="wrap">
    <p class="eyebrow reveal">{l_eyebrow}</p>
    <h2 class="reveal">{l_head}</h2>
    <p class="lead reveal" style="max-width:42rem; margin-top:1rem">{l_sub}</p>
    <div class="learn-chain">{learn}</div>
    <p class="reveal" style="margin-top:1.6rem; max-width:42rem">{l_foot}</p>
  </div>
</section>

<!-- ===== 11. Сколько стоит консалтинг ===== -->
<section class="sec cost" id="cost">
  <div class="wrap">
    <p class="eyebrow o reveal">{c_eyebrow}</p>
    <h2 class="reveal" style="max-width:44rem">{c_head}</h2>
    <div class="cost-cols">{costs}</div>
    <p class="foot-note reveal">{c_note}</p>
  </div>
</section>

<!-- ===== 12. Тарифы ===== -->
<section class="sec" id="pricing">
  <div class="wrap">
    <p class="eyebrow reveal">{pr_eyebrow}</p>
    <h2 class="reveal">{pr_head}</h2>
    <div class="plans">{plans}</div>
    <div class="pay-once reveal">
      <h3>{pr_once}</h3>
      <p class="lead">{pr_once_sub}</p>
      <div class="acc">
        <button class="acc-btn" type="button">{pr_what} <i class="fa-solid fa-plus"></i></button>
        <div class="acc-body"><div class="acc-in"><div>
          <div class="op-chain">{op_chain}</div>
          <p class="muted">{pr_ops_note}</p>
        </div></div></div>
      </div>
    </div>
  </div>
</section>

<!-- ===== 13. Финал ===== -->
<section class="final" id="start">
  <div class="wrap">
    <div class="final-lines">
      <h2 class="final-line">{f_1}</h2>
      <p class="final-line quiet">{f_2}</p>
      <h2 class="final-line hl-p">{f_3}</h2>
    </div>
    <div class="flow">{flow}</div>
    <div class="final-list">{final_list}</div>
    <a class="btn btn-primary" href="{cta_href}" rel="noopener">{f_cta} <i class="fa-solid fa-arrow-right"></i></a>
  </div>
</section>

</main>

<footer>
  <div class="wrap foot-row">
    <div class="socials">
      <a href="https://t.me/andre_dataist" target="_blank" rel="noopener" aria-label="Telegram" style="--brand:#2AABEE"><i class="fa-brands fa-telegram"></i></a>
      <a href="https://dataist.ai/" target="_blank" rel="noopener" aria-label="Website" style="--brand:#8854F3"><i class="fa-solid fa-globe"></i></a>
      <a href="https://www.youtube.com/@andre_dataist" target="_blank" rel="noopener" aria-label="YouTube" style="--brand:#FF0000"><i class="fa-brands fa-youtube"></i></a>
      <a href="https://www.linkedin.com/in/andre-kuzminykh/" target="_blank" rel="noopener" aria-label="LinkedIn" style="--brand:#0a66c2"><i class="fa-brands fa-linkedin"></i></a>
      <a href="mailto:admin@andre.technology" aria-label="Email" style="--brand:#F97316"><i class="fa-solid fa-envelope"></i></a>
    </div>
    <a class="copy" href="/">2026 &copy; Andre AI Technologies LTD</a>
  </div>
</footer>

<script src="/assets/strategy.js"></script>
</body>
</html>
""".format(
        lang=lang, title=t["title"], desc=t["meta_desc"], self_href=self_href, video=video,
        video_aria=t["video_aria"], role=t["role"], phrases=phrases, back=t["back"], sections=t["sections"],
        close=t["close"], menu=t["menu"], nav_html=nav_html, cta_href=t["cta_href"], cta_top=t["cta_top"],
        lang_switch=('<span class="lang-opt active">EN</span><span class="lang-sep">|</span>'
                     '<a class="lang-opt" href="%s">RU</a>' % other_href) if lang == "en" else
                    ('<a class="lang-opt" href="%s">EN</a><span class="lang-sep">|</span>'
                     '<span class="lang-opt active">RU</span>' % other_href),
        h1=t["h1"], hero_lead=t["hero_lead"], hero_body=t["hero_body"], cta_main=t["cta_main"], cta_how=t["cta_how"],
        hero_notes="".join('<span><i class="fa-solid fa-circle"></i>%s</span>' % n for n in t["hero_notes"]),
        q_head=t["q_head"], questions=questions, q_final=t["q_final"], dots=dots,
        n_eyebrow=t["n_eyebrow"], n_head=t["n_head"], nums=nums, n_foot=t["n_foot"], n_verdict=t["n_verdict"], n_note=t["n_note"],
        p_head=t["p_head"], p_sub=t["p_sub"], chips=chips, p_core=t["p_core"],
        b_eyebrow=t["b_eyebrow"], b_head=t["b_head"], b_sub=t["b_sub"], biz=biz, b_all=t["b_all"],
        b_arch=t["b_arch"], b_metrics_note=t["b_metrics_note"],
        d_eyebrow=t["d_eyebrow"], d_head=t["d_head"], d_sub=t["d_sub"], outs=outs, d_hint=t["d_hint"],
        s_eyebrow=t["s_eyebrow"], s_head=t["s_head"], s_sub=t["s_sub"], rail=rail, steps=steps, stage_cards=stage_cards,
        m_eyebrow=t["m_eyebrow"], m_head=t["m_head"], m_sub=t["m_sub"], model=model,
        t_eyebrow=t["t_eyebrow"], t_head=t["t_head"], t_l_head=t["t_l_head"], t_l_body=t["t_l_body"],
        t_r_head=t["t_r_head"], t_r_body=t["t_r_body"], t_foot=t["t_foot"],
        l_eyebrow=t["l_eyebrow"], l_head=t["l_head"], l_sub=t["l_sub"], learn=learn, l_foot=t["l_foot"],
        c_eyebrow=t["c_eyebrow"], c_head=t["c_head"], costs=costs, c_note=t["c_note"],
        pr_eyebrow=t["pr_eyebrow"], pr_head=t["pr_head"], plans=plans, pr_once=t["pr_once"], pr_once_sub=t["pr_once_sub"],
        pr_what=t["pr_what"], pr_ops_note=t["pr_ops_note"],
        op_chain="".join('<span>%s</span>%s' % (o, '<i class="fa-solid fa-arrow-right"></i>' if i < len(t["op_chain"]) - 1 else "")
                         for i, o in enumerate(t["op_chain"])),
        f_1=t["f_1"], f_2=t["f_2"], f_3=t["f_3"], flow=flow, final_list=final_list, f_cta=t["f_cta"],
    )


def build():
    from strategy_copy import EN, RU  # тексты вынесены в соседний файл
    out = [("strategy/index.html", page(EN, "en")), ("strategy/ru/index.html", page(RU, "ru"))]
    for rel, html in out:
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("written", rel, len(html), "bytes")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    build()
