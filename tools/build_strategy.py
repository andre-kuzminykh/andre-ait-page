# -*- coding: utf-8 -*-
"""Собирает лендинг AI Strategy на двух языках из одного шаблона.

    python3 tools/build_strategy.py      # пишет strategy/index.html и strategy/ru/index.html

Страница листается ЭКРАНАМИ, как биография и главная: экраны сменяют друг
друга анимацией, а не прокруткой. Вёрстка — assets/strategy.css, поведение —
assets/strategy.js, тексты — tools/strategy_copy.py. Точек в конце строк нет.
"""
import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Разделы меню: id экрана + иконка для мобильного меню
NAV = [
    ("solution",   "fa-cubes",           "#8854F3"),
    ("usecases",   "fa-city",            "#F97316"),
    ("process",    "fa-diagram-project", "#8854F3"),
    ("learning",   "fa-graduation-cap",  "#F97316"),
    ("pricing",    "fa-tag",             "#8854F3"),
    ("start",      "fa-rocket",          "#F97316"),
]

BIZ_ICONS = ["fa-briefcase", "fa-user-tie", "fa-bullhorn", "fa-pen-nib",
             "fa-headset", "fa-life-ring", "fa-palette", "fa-code"]
OUT_ICONS = ["fa-gauge-high", "fa-diagram-project", "fa-brain", "fa-lightbulb",
             "fa-people-arrows", "fa-wand-magic-sparkles", "fa-robot", "fa-route"]


def flip_key(name):
    """Ключ перелёта — по НАЗВАНИЮ блока, а не по номеру: так «Meeting» летит
    именно в «Meeting», а операция, которую забрал ИИ, пары не находит и
    просто гаснет. Индексы такой смысловой связи не давали."""
    key = re.sub(r"[^0-9a-zа-яё]+", "-", name.lower(), flags=re.U).strip("-")
    return ' data-flip="%s"' % key


def radar(values, dims):
    """Паутина зрелости: семь осей, оценка живёт НАД схемой."""
    cx = cy = 100
    r = 68
    def pts(k, vals=None):
        out = []
        for i in range(len(dims)):
            a = -math.pi / 2 + i * 2 * math.pi / len(dims)
            v = k if vals is None else vals[i]
            out.append("%.1f,%.1f" % (cx + math.cos(a) * r * v, cy + math.sin(a) * r * v))
        return " ".join(out)
    rings = "".join('<polygon class="grid-l" points="%s"/>' % pts(k) for k in (0.34, 0.67, 1.0))
    axes = "".join('<line class="axis" x1="%d" y1="%d" x2="%.1f" y2="%.1f"/>'
                   % (cx, cy, cx + math.cos(-math.pi / 2 + i * 2 * math.pi / len(dims)) * r,
                      cy + math.sin(-math.pi / 2 + i * 2 * math.pi / len(dims)) * r)
                   for i in range(len(dims)))
    labels = []
    for i, d in enumerate(dims):
        a = -math.pi / 2 + i * 2 * math.pi / len(dims)
        x, y = cx + math.cos(a) * (r + 17), cy + math.sin(a) * (r + 17)
        anchor = "middle" if abs(math.cos(a)) < 0.3 else ("start" if math.cos(a) > 0 else "end")
        labels.append('<text x="%.1f" y="%.1f" text-anchor="%s">%s</text>' % (x, y + 3, anchor, d))
    return rings + axes + '<polygon class="shape" points="%s"/>' % pts(None, values) + "".join(labels)


def stages(t):
    """Шесть сцен продукта — по одной на шаг."""
    s = t["stage"]
    out = []

    # 01 — индекс зрелости: оценка над паутиной
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot p"></span>{bar}</div>
        <div class="ui-body">
          <div class="score"><b class="idx-val">2.4</b><span>/ 5 &middot; {score}</span></div>
          <svg class="radar" viewBox="0 0 200 200" role="img" aria-label="{bar}">{svg}</svg>
        </div>
      </div>""".format(bar=s["s1_bar"], score=s["s1_score"],
                       svg=radar([0.62, 0.3, 0.55, 0.48, 0.42, 0.35, 0.5], s["dims"])))

    # 02 — голос превращается в процессы
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot p"></span>{bar}</div>
        <div class="ui-body">
          <div class="wave">{bars}</div>
          <p class="typing">{quote}<span class="caret"></span></p>
          <div class="flow-row">{cards}</div>
        </div>
      </div>""".format(
        bar=s["s2_bar"], quote=s["s2_quote"],
        bars="".join('<span style="animation-delay:%.2fs"></span>' % (i * 0.08) for i in range(18)),
        cards="".join('<div class="node ai" data-seq><i class="fa-solid fa-diagram-project"></i>%s</div>' % c
                      for c in s["s2_cards"])))

    # 03 — процессы связаны между собой, где люди — оранжевые
    proc = s["s3_cards"]
    nodes = []
    for name, kind in proc:
        icon = "fa-user" if kind == "human" else "fa-database"
        flip = flip_key(name) if kind == "human" else ""
        nodes.append('<div class="pnode %s" data-seq%s><i class="fa-solid %s"></i><span>%s</span></div>'
                     % ("human" if kind == "human" else "sys", flip, icon, name))
    # рядами по три: в одну строку шесть блоков не влезают, а сетка оставляла
    # висящую чёрточку в конце ряда и рвала связь между рядами
    PARROW = '<span class="parrow" aria-hidden="true"><i class="fa-solid fa-arrow-right"></i></span>'
    PDOWN = '<span class="pwrap" aria-hidden="true"><i class="fa-solid fa-arrow-turn-down"></i></span>'
    rows = [nodes[i:i + 3] for i in range(0, len(nodes), 3)]
    chain = []
    for r, row in enumerate(rows):
        chain.append('<div class="prow">' + PARROW.join(row) + "</div>")
        if r < len(rows) - 1:
            chain.append(PDOWN)
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot o"></span>{bar}</div>
        <div class="ui-body"><div class="pchain">{chain}</div></div>
      </div>""".format(bar=s["s3_bar"], chain="".join(chain)))

    # 04 — что может забрать ИИ
    ops_html = []
    for name, can in s["s4_ops"]:
        flip = "" if can else flip_key(name)
        ops_html.append('<div class="opnode%s" data-seq%s><i class="fa-solid %s"></i><span>%s</span></div>'
                        % (" can" if can else "", flip, "fa-wand-magic-sparkles" if can else "fa-user", name))
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot p"></span>{bar}</div>
        <div class="ui-body">
          <div class="opgrid">{ops}</div>
          <div class="chips"><span class="chip p"><i class="fa-solid fa-bolt"></i>{impact}</span>
            <span class="chip o"><i class="fa-solid fa-layer-group"></i>{complexity}</span></div>
        </div>
      </div>""".format(
        bar=s["s4_bar"], impact=s["s4_impact"], complexity=s["s4_complexity"],
        ops="".join(ops_html)))

    # 05 — AI-First модель: люди оранжевые, агенты фиолетовые
    # цепочка идёт рядами по три: в одну строку шесть блоков не помещаются,
    # а перенос флексом оставлял «висящую» стрелку в конце ряда
    items = []
    for name, kind in s["s5_flow"]:
        icon = "fa-user" if kind == "human" else "fa-robot"
        flip = flip_key(name) if kind == "human" else ""
        items.append('<div class="fnode %s" data-seq%s><i class="fa-solid %s"></i><span>%s</span></div>'
                     % (kind, flip, icon, name))
    ARROW = '<span class="farrow" aria-hidden="true"><i class="fa-solid fa-arrow-right"></i></span>'
    DOWN = '<span class="fwrap" aria-hidden="true"><i class="fa-solid fa-arrow-turn-down"></i></span>'
    flow, rows = [], [items[i:i + 3] for i in range(0, len(items), 3)]
    for r, row in enumerate(rows):
        flow.append('<div class="frow">' + ARROW.join(row) + "</div>")
        if r < len(rows) - 1:
            flow.append(DOWN)
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot p"></span><span class="ui-dot o"></span>{bar}</div>
        <div class="ui-body">
          <div class="fflow">{flow}</div>
          <div class="legend">
            <span><i style="background:var(--o)"></i>{lh}</span>
            <span><i style="background:var(--p)"></i>{la}</span>
          </div>
        </div>
      </div>""".format(bar=s["s5_bar"], flow="".join(flow), lh=s["s5_legend_h"], la=s["s5_legend_a"]))

    # 06 — паспорт агента: агент в центре, поля вокруг
    n = len(s["s6_spokes"])
    spokes = []
    for i, sp in enumerate(s["s6_spokes"]):
        a = -math.pi / 2 + i * 2 * math.pi / n
        x = 50 + math.cos(a) * 40
        y = 50 + math.sin(a) * 40
        spokes.append('<span class="spoke" data-seq style="left:%.1f%%; top:%.1f%%">%s</span>' % (x, y, sp))
    spokes = "".join(spokes)
    out.append("""
      <div class="ui">
        <div class="ui-bar"><span class="ui-dot p"></span>{bar}</div>
        <div class="ui-body">
          <div class="hub">
            <div class="hub-core" aria-label="{name}"><i class="fa-solid fa-robot"></i></div>
            {spokes}
          </div>
        </div>
      </div>""".format(bar=s["s6_bar"], name=s["s6_name"], spokes=spokes))
    return out


def page(t, lang):
    other_href = "/strategy/ru/" if lang == "en" else "/strategy/"
    self_href = "/strategy/" if lang == "en" else "/strategy/ru/"
    video = "/assets/Andre_AIT_video_compressed%s.mp4" % ("" if lang == "en" else "_ru")

    nav_html = "".join(
        '<button class="nav-tab{act}" data-go="{id}" style="--ul:{c}; --hover:{c}; --ic:{c};">'
        '<span class="nav-ic"><i class="fa-solid {ic}"></i></span>'
        '<span class="nav-label">{label}</span>'
        '<span class="nav-go"><i class="fa-solid fa-arrow-right"></i></span></button>'.format(
            id=sec, ic=icon, c=color, label=t["nav"][i], act=" active" if i == 0 else "")
        for i, (sec, icon, color) in enumerate(NAV))

    # правка владельца: вместо кнопки «назад» — иконка дома рядом с меню
    home = ('<a class="nav-home" href="/" aria-label="{label}" data-label="{label}">'
            '<i class="fa-solid fa-house"></i></a>').format(label=t["home"])

    nums = "".join('<div class="num-card"><span class="num-val">{v}</span><p>{p}</p></div>'.format(v=v, p=p)
                   for v, p in t["numbers"])

    biz = "".join("""
          <article class="biz">
            <span class="biz-ic"><i class="fa-solid {ic}"></i></span>
            <div class="biz-body">
              <h3>{name}</h3>
              <p class="biz-metric"><b>{val}</b><span>{label}</span></p>
            </div>
            <span class="biz-go"><span>{explore}</span> <i class="fa-solid fa-arrow-right"></i></span>
          </article>""".format(ic=BIZ_ICONS[i], name=b[0], val=b[1], label=b[2], explore=t["biz_explore"])
        for i, b in enumerate(t["businesses"]))

    outs = "".join("""
          <article class="out">
            <span class="out-n">{n:02d}</span>
            <h3><i class="fa-solid {ic}"></i>{name}</h3>
            <p>{desc}</p>
          </article>""".format(n=i + 1, ic=OUT_ICONS[i], name=o[0], desc=o[1])
        for i, o in enumerate(t["deliverables"]))

    stage_html = stages(t)
    steps = "".join("""
      <section class="screen step-screen" data-chapter="process" data-step="{n}">
        <div class="wrap step-wrap">
          <article class="step-copy">
            <p class="step-n">{n:02d} &mdash; {chapter} &mdash; {tag}</p>
            <h2>{title}</h2>
            <p>{body}</p>
          </article>
          <div class="stage-card">{stage}</div>
        </div>
      </section>""".format(n=i + 1, chapter=t["s_eyebrow"], tag=st[0], title=st[1], body=st[2], stage=stage_html[i])
        for i, st in enumerate(t["steps"]))

    roles = "".join('<span class="role"><i class="fa-solid %s"></i>%s</span>' % (ic, name) for name, ic in t["roles"])

    plans = "".join("""
          <article class="plan{best}">
            {badge}
            <h3>{name}</h3>
            <div class="plan-price">{price}</div>
            <div class="plan-scope">{scope}</div>
            <a class="btn btn-{style} btn-sm" href="{href}" rel="noopener">{cta} <i class="fa-solid fa-arrow-right"></i></a>
          </article>""".format(
        best=" best" if p[0] == "best" else "", name=p[1], price=p[2], scope=p[3], cta=p[4],
        badge='<span class="plan-badge">%s</span>' % t["best_value"] if p[0] == "best" else "",
        style="primary" if p[0] == "best" else "ghost", href=t["cta_href"])
        for p in t["plans"])

    compare = "".join(
        '<span class="cmp%s">%s</span>%s' % (" old" if old else " now", txt,
                                             '<i class="fa-solid fa-circle"></i>' if i < len(t["compare"]) - 1 else "")
        for i, (txt, old) in enumerate(t["compare"]))

    return """<!DOCTYPE html>
<!-- Собрано tools/build_strategy.py — править этот файл руками нельзя, сборка перезапишет -->
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

<!-- ===== Лицо: слева на полэкрана (веб), кружок внизу слева (мобилка) ===== -->
<div class="head" id="head" role="button" tabindex="0" aria-label="{video_aria}">
  <video id="head-video" src="{video}" poster="/andre_ai.jpg" loop muted autoplay playsinline preload="auto"></video>
  <div class="head-shade" aria-hidden="true"></div>
  <div class="head-play" aria-hidden="true"><i class="fa-solid fa-circle-play"></i></div>
</div>
<div class="head-badge"><b>Andre AI</b><span>{role}</span><i><i class="fa-solid fa-microphone-lines-slash" id="head-mic"></i></i></div>

<!-- ===== Шапка: как на главной ===== -->
<header>
  <div class="header-row">
    <div class="header-left">
      <a class="logo-btn" href="/" aria-label="Andre AI Technologies">
        <img class="logo-img" src="https://i.ibb.co/gn7SmgY/866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png" alt="AIT">
      </a>
    </div>

    <nav class="nav" id="nav" aria-label="{sections}">
      <button class="nav-close" id="nav-close" aria-label="{close}"><i class="fa-solid fa-xmark"></i></button>
      <div class="nav-brand" aria-hidden="true">
        <img src="https://i.ibb.co/gn7SmgY/866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png" alt="">
        <span>AI Strategy</span>
      </div>
      {home}{nav_html}
    </nav>

    <div class="header-right">
      <div class="lang-switch" role="group" aria-label="Language">
        {lang_switch}
      </div>
      <button class="menu-btn" id="menu-btn" aria-label="{menu}"><i id="menu-icon" class="fa-solid fa-bars"></i></button>
      <a class="btn btn-primary cta-head" href="{cta_href}" rel="noopener">{cta_top} <i class="fa-solid fa-arrow-right"></i></a>
    </div>
  </div>
</header>

<div class="dots" id="dots" aria-hidden="true"></div>

<main class="deck" id="deck">

  <!-- 1. Первый экран -->
  <section class="screen active" data-chapter="top" id="top">
    <div class="wrap">
      <p class="eyebrow">AI Strategy</p>
      <h1>{h1}</h1>
      <p class="lead">{hero_lead}</p>
      <div class="hero-cta">
        <a class="btn btn-primary" href="{cta_href}" rel="noopener">{cta_main} <i class="fa-solid fa-arrow-right"></i></a>
        <button class="btn btn-ghost" data-go="process" type="button">{cta_how}</button>
      </div>
    </div>
  </section>

  <!-- 3. Рынок -->
  <section class="screen" data-chapter="solution" id="numbers">
    <div class="wrap center">
      <p class="eyebrow o">{n_eyebrow}</p>
      <h2 class="one-line">{n_head}</h2>
      <div class="nums">{nums}</div>
      <p class="nums-foot">{n_foot}</p>
    </div>
  </section>

  <!-- 4. Кейсы -->
  <section class="screen" data-chapter="usecases" id="usecases">
    <div class="wrap">
      <p class="eyebrow">{b_eyebrow}</p>
      <h2>{b_head}</h2>
      <div class="biz-grid">{biz}</div>
      <a class="biz-all" href="{cta_href}" rel="noopener">{b_all} <i class="fa-solid fa-arrow-right"></i></a>
    </div>
  </section>

  <!-- 5. Решение -->
  <section class="screen" data-chapter="solution" id="solution">
    <div class="wrap">
      <p class="eyebrow o">{d_eyebrow}</p>
      <h2>{d_head}</h2>
      <p class="lead">{d_sub}</p>
      <div class="rail-wrap">
        <div class="rail">{outs}</div>
      </div>
      <p class="rail-hint"><i class="fa-solid fa-arrows-left-right"></i> {d_hint}</p>
    </div>
  </section>

{steps}

  <!-- 7. Обучение -->
  <section class="screen" data-chapter="learning" id="learning">
    <div class="wrap center">
      <p class="eyebrow o">{l_eyebrow}</p>
      <h2>{l_head}</h2>
      <p class="lead">{l_sub}</p>
      <p class="l-note"><i class="fa-solid fa-circle-nodes"></i>{l_note}</p>
    </div>
    <div class="ticker" aria-hidden="true">
      <div class="ticker-row">{roles}{roles}</div>
    </div>
  </section>

  <!-- 8. Тарифы -->
  <section class="screen" data-chapter="pricing" id="pricing">
    <div class="wrap">
      <p class="eyebrow">{pr_eyebrow}</p>
      <h2>{pr_head}</h2>
      <p class="lead">{pr_sub}</p>
      <div class="plans">{plans}</div>
      <p class="compare">{compare}</p>
    </div>
  </section>

  <!-- 9. Финал -->
  <section class="screen final" data-chapter="start" id="start">
    <div class="wrap center">
      <h2 class="final-1">{f_1}</h2>
      <p class="final-2">{f_2}</p>
      <h2 class="final-3">{f_3}</h2>
      <a class="btn btn-primary final-cta" href="{cta_href}" rel="noopener">{f_cta} <i class="fa-solid fa-arrow-right"></i></a>
    </div>
    <footer>
      <p class="company">{company}</p>
      <div class="socials">
        <a href="https://t.me/andre_dataist" target="_blank" rel="noopener" aria-label="Telegram" style="--brand:#2AABEE"><i class="fa-brands fa-telegram"></i></a>
        <a href="https://dataist.ai/" target="_blank" rel="noopener" aria-label="Website" style="--brand:#8854F3"><i class="fa-solid fa-globe"></i></a>
        <a href="https://www.youtube.com/@andre_dataist" target="_blank" rel="noopener" aria-label="YouTube" style="--brand:#FF0000"><i class="fa-brands fa-youtube"></i></a>
        <a href="https://www.linkedin.com/in/andre-kuzminykh/" target="_blank" rel="noopener" aria-label="LinkedIn" style="--brand:#0a66c2"><i class="fa-brands fa-linkedin"></i></a>
        <a href="mailto:admin@andre.technology" aria-label="Email" style="--brand:#F97316"><i class="fa-solid fa-envelope"></i></a>
      </div>
      <p class="legal"><a href="/">{legal0}</a><span>&middot;</span><a href="/">{legal1}</a></p>
      <p class="copy">2026 &copy; Andre AI Technologies LTD</p>
    </footer>
  </section>

</main>

<script src="/assets/strategy.js"></script>
</body>
</html>
""".format(
        lang=lang, title=t["title"], desc=t["meta_desc"], self_href=self_href, video=video,
        video_aria=t["video_aria"], role=t["role"], sections=t["sections"], close=t["close"], menu=t["menu"],
        nav_html=nav_html, cta_href=t["cta_href"], cta_top=t["cta_top"], home=home,
        lang_switch=('<span class="lang-opt active">EN</span><span class="lang-sep">|</span>'
                     '<a class="lang-opt" href="%s">RU</a>' % other_href) if lang == "en" else
                    ('<a class="lang-opt" href="%s">EN</a><span class="lang-sep">|</span>'
                     '<span class="lang-opt active">RU</span>' % other_href),
        h1=t["h1"], hero_lead=t["hero_lead"], cta_main=t["cta_main"], cta_how=t["cta_how"],
        n_eyebrow=t["n_eyebrow"], n_head=t["n_head"], nums=nums, n_foot=t["n_foot"],
        b_eyebrow=t["b_eyebrow"], b_head=t["b_head"], biz=biz, b_all=t["b_all"],
        d_eyebrow=t["d_eyebrow"], d_head=t["d_head"], d_sub=t["d_sub"], outs=outs, d_hint=t["d_hint"],
        steps=steps,
        l_eyebrow=t["l_eyebrow"], l_head=t["l_head"], l_sub=t["l_sub"], l_note=t["l_note"], roles=roles,
        pr_eyebrow=t["pr_eyebrow"], pr_head=t["pr_head"], pr_sub=t["pr_sub"], plans=plans, compare=compare,
        f_1=t["f_1"], f_2=t["f_2"], f_3=t["f_3"], f_cta=t["f_cta"],
        company=t["company"], legal0=t["legal"][0], legal1=t["legal"][1],
    )


def build():
    from strategy_copy import EN, RU
    for rel, html in (("strategy/index.html", page(EN, "en")), ("strategy/ru/index.html", page(RU, "ru"))):
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("written", rel, len(html), "bytes")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    build()
