# -*- coding: utf-8 -*-
"""Тесты сайта andre.technology (index.html). Без зависимостей — запускается
и как `python3 tests/test_site.py`, и через pytest.

FR-SITE1/24 — все кнопки диагностики («Free AI Diagnostic/Diagnosis») ведут
           на maturity.andre.technology (первый шаг воронки).
FR-SITE2 — роль/подпись «AI Consultant», а не «Chief AI Officer».
FR-SITE24 — меню из 8 разделов: About Me, AI Strategy, Neuronium, Landao,
            Antropolis, Academy, Dataist, My contacts.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _html():
    with open(os.path.join(_ROOT, "index.html"), encoding="utf-8") as f:
        return f.read()


# ── FR-SITE1 ──────────────────────────────────────────────────────────────

def test_diagnostic_buttons_link_to_maturity():
    html = _html()
    # каждая кнопка диагностики («Free AI Diagnostic» в шапке, «Free AI
    # Diagnosis» на контактах) — это ссылка <a> на maturity.andre.technology
    hits = [m.start() for m in re.finditer(r"Free AI Diagnos(?:tic|is)", html)]
    assert hits, "на сайте должны быть кнопки диагностики"
    for pos in hits:
        tag_start = html.rfind("<", 0, pos)
        el = html[tag_start:pos]
        if el.strip().startswith("<!--"):
            continue  # комментарий, не элемент
        assert el.lstrip().startswith("<a "), \
            "кнопка диагностики должна быть ссылкой <a>: " + el[:60]
        assert "https://maturity.andre.technology/" in el, \
            "диагностика должна вести на maturity.andre.technology: " + el[:80]


def test_no_free_diagnostic_button_with_contact():
    html = _html()
    # не должно быть <button ... data-action="contact" ...>Free AI Diagnostic
    bad = re.search(r'<button[^>]*data-action="contact"[^>]*>\s*Free AI Diagnostic', html)
    assert bad is None, "«Free AI Diagnostic» не должна быть кнопкой contact"


# ── FR-SITE2 ──────────────────────────────────────────────────────────────

def test_no_chief_ai_officer():
    assert "Chief AI Officer" not in _html(), "подпись «Chief AI Officer» должна быть убрана"


def test_role_and_subtitle_are_ai_consultant():
    html = _html()
    # бейдж-роль
    assert re.search(r'class="role"[^>]*>\s*AI Consultant\s*<', html), \
        "бейдж-роль должен быть «AI Consultant»"
    # анимированная подпись героя (CUES)
    assert re.search(r'text:\s*"your AI Consultant"', html), \
        "подпись героя должна быть «your AI Consultant»"


# ── FR-SITE3 ──────────────────────────────────────────────────────────────

def test_apply_expanded_toggles_list_open():
    html = _html()
    # applyExpanded помечает раскрытый список классом body.list-open
    body = html[html.find("function applyExpanded"):html.find("function toggleExpand")]
    assert "anyOpen" in body, "applyExpanded должен считать, открыт ли хоть один список"
    assert re.search(r"classList\.toggle\(\s*'list-open'\s*,\s*anyOpen\s*\)", body), \
        "applyExpanded должен тогглить body.list-open по anyOpen"


def test_list_open_scroll_is_full_viewport():
    html = _html()
    # правило full-viewport для раскрытого списка — внутри @media (min-width:1024px)
    assert "body.list-open .scroll" in html, "нужно правило body.list-open .scroll"
    rule = html.split("body.list-open .scroll {")[1].split("}")[0]
    # box-sizing:border-box обязателен — иначе бокс с padding вылезает за края экрана
    assert "box-sizing: border-box" in rule
    assert "max-height: 100dvh" in rule and "height: 100dvh" in rule
    # паддинги СИММЕТРИЧНЫ: auto-поля центрируют помещающийся список ровно
    # по центру вьюпорта (см. test_list_open_content_centered_when_fits)
    assert "padding-top: 6rem" in rule and "padding-bottom: 6rem" in rule
    assert "justify-content: flex-start" in rule
    # правило действует ТОЛЬКО на десктопе: ближайший @media перед ним — min-width:1024px
    before = html.split("body.list-open .scroll {")[0]
    nearest_media = before.rfind("@media (")
    assert "min-width:1024px" in before[nearest_media:nearest_media + 40], \
        "body.list-open .scroll должно быть в @media (min-width:1024px)"


def test_list_open_content_centered_when_fits():
    html = _html()
    # раскрытый список, помещающийся в экран, центрируется по вертикали
    # auto-полями активного экрана (приём .modal: margin auto = safe center);
    # при переполнении поля схлопываются в 0 и остаётся режим FR-SITE3
    assert re.search(
        r"body\.list-open \.scroll > \.screen\.active\s*\{\s*margin-top:\s*auto;\s*margin-bottom:\s*auto;",
        html), "нужно правило body.list-open .scroll > .screen.active { margin-top/bottom: auto }"
    # правило действует ТОЛЬКО на десктопе: ближайший @media перед ним — min-width:1024px
    before = html.split("body.list-open .scroll > .screen.active")[0]
    nearest_media = before.rfind("@media (")
    assert "min-width:1024px" in before[nearest_media:nearest_media + 40], \
        "центрирование list-open должно быть в @media (min-width:1024px)"


# ── FR-SITE4 ──────────────────────────────────────────────────────────────

def test_nav_font_readable():
    html = _html()
    # базовый размер пункта меню на десктопе — 14px, НЕ жирный (font-weight:500)
    assert re.search(r"\.nav-tab\s*\{\s*font-size:\s*14px;\s*font-weight:\s*500;", html), \
        "десктопный .nav-tab должен быть font-size:14px; font-weight:500 (не жирный)"
    assert "font-size: 12px; letter-spacing: 0.03em;" not in html, \
        "старый мелкий десктоп-размер 12px должен быть заменён"
    # НИКАКОГО transform:scale на .nav — он менял высоту и ронял шрифт до 8px
    for s in ("scale(0.66)", "scale(0.85)", "scale(0.86)", "scale(0.95)"):
        assert s not in html, "transform:scale на nav убран (%s), высота бара постоянна" % s
    # бар навигации и CTA — ОДНОЙ высоты (обе 2.85rem, box-sizing:border-box)
    assert re.search(r"\.nav\s*\{[^}]*height:\s*2\.85rem;[^}]*box-sizing:\s*border-box", html), \
        ".nav должен иметь фиксированную высоту 2.85rem и border-box"
    assert re.search(r"\.cta\s*\{\s*height:\s*2\.85rem;\s*box-sizing:\s*border-box;", html), \
        "десктопный .cta должен быть той же высоты 2.85rem"


def test_nav_dividers_never_hidden_on_desktop():
    html = _html()
    # разделители «·» видны на всех десктоп-ширинах: внутри мид-брейкпоинта
    # 1024–1319 НЕТ правила `.nav-divider { display: none }`
    mid = html.split("@media (min-width:1024px) and (max-width:1319px) {", 1)[1].split("}")[0]
    assert "display: none" not in mid, \
        "на узком десктопе разделители не должны пропадать (нет display:none)"


# ── FR-SITE7 ──────────────────────────────────────────────────────────────

def test_start_transformation_links_to_maturity():
    html = _html()
    # «Start AI Transformation» — ссылка на maturity. (первый шаг воронки), НЕ кнопка contact
    bad = re.search(r'<button[^>]*data-action="contact"[^>]*>\s*Start AI Transformation', html)
    assert bad is None, "«Start AI Transformation» не должна быть кнопкой contact (coming soon)"
    pos = html.find("Start AI Transformation")
    assert pos > 0, "на сайте должна быть кнопка «Start AI Transformation»"
    tag_start = html.rfind("<", 0, pos)
    el = html[tag_start:pos]
    assert el.lstrip().startswith("<a "), \
        "«Start AI Transformation» должна быть ссылкой <a>: " + el[:60]
    assert "https://maturity.andre.technology/" in el, \
        "«Start AI Transformation» должна вести на maturity.andre.technology"


def test_about_me_link():
    html = _html()
    # серая текстовая ссылка «About me» под hero-CTA → /about/
    m = re.search(r'<a class="about-link" href="https://andre\.technology/about/"[^>]*>About me</a>', html)
    assert m, "под «Start AI Transformation» должна быть ссылка «About me» на /about/"
    assert re.search(r"\.about-link\s*\{[^}]*color:\s*rgba\(255,255,255,0\.5\)", html), \
        "ссылка «About me» должна быть серой (rgba(255,255,255,0.5))"


# ── FR-SITE8 ──────────────────────────────────────────────────────────────

def test_get_ai_strategy_label():
    html = _html()
    assert "Get Your AI Strategy" in html, "кнопка стратегии должна называться «Get Your AI Strategy»"
    assert "Open AI Strategy" not in html, "старого названия «Open AI Strategy» быть не должно"


def test_product_buttons_link_out():
    """FR-SITE24/29: запущенные продукты — кнопки-ссылки; незапущенные (Neuronium,
    Landao, Antropolis) — кнопки Coming soon (попап сбора ранних заявок)."""
    html = _html()
    for label, host in (("Start AI Transformation", "https://maturity.andre.technology/"),
                        ("Get Your AI Strategy", "https://strategy.andre.technology/"),
                        ("Explore Courses", "https://academy.andre.technology/"),
                        ("Visit Dataist AI", "https://dataist.ai/"),
                        ("Free AI Diagnosis", "https://maturity.andre.technology/")):
        pos = html.find(label)
        assert pos > 0, "должна быть кнопка «%s»" % label
        el = html[html.rfind("<", 0, pos):pos]
        assert el.lstrip().startswith("<a "), "«%s» должна быть ссылкой <a>: %s" % (label, el[:80])
        assert host in el, "«%s» должна вести на %s: %s" % (label, host, el[:120])
    for label, source in (("Get Neuronium AI", "Neuronium AI"),
                          ("Meet Landao AI", "Landao AI"),
                          ("Enter Antropolis", "Antropolis")):
        pos = html.find(label)
        assert pos > 0, "должна быть кнопка «%s»" % label
        el = html[html.rfind("<", 0, pos):pos]
        assert el.lstrip().startswith("<button ") and 'data-action="lead-open"' in el, \
            "«%s» должна открывать попап Coming soon: %s" % (label, el[:120])
        assert 'data-source="%s"' % source in el, \
            "у «%s» должен быть data-source=«%s»" % (label, source)
    assert html.count('data-action="lead-open"') == 3, \
        "попап Coming soon открывают ровно три кнопки незапущенных продуктов"


def test_sec_links_under_buttons():
    """FR-SITE24: под кнопкой каждого экрана — серая текстовая ссылка."""
    html = _html()
    for label in ("AI Transformation Cases", "Learn More", "Project History",
                  "Manifesto", "Skill Map", "Top Stories"):
        m = re.search(r'<a class="sec-link"[^>]*>' + re.escape(label) + r'</a>', html)
        assert m, "нужна серая ссылка «%s» (class=sec-link)" % label
    assert re.search(r"\.sec-link\s*\{[^}]*color:\s*rgba\(255,255,255,0\.5\)", html), \
        "ссылки .sec-link должны быть серыми, как «About me»"


def test_nav_has_eight_sections():
    """FR-SITE24: меню = ровно 8 разделов в заданном порядке."""
    html = _html()
    targets = re.findall(r'<button class="nav-tab" data-action="tab" data-target="([a-z]+)"', html)
    assert targets == ["overview", "strategy", "neuronium", "landao",
                       "antropolis", "academy", "dataist", "contact"], targets
    for gone in ("platform", "employees", "products", "education"):
        assert 'data-screen="%s"' % gone not in html, "экран «%s» должен быть удалён" % gone


# ── FR-SITE9 ──────────────────────────────────────────────────────────────

def test_nav_label_my_contacts():
    html = _html()
    assert re.search(r'<span class="nav-label"[^>]*>My contacts</span>', html), \
        "пункт навигации должен называться «My contacts»"
    assert not re.search(r'<span class="nav-label"[^>]*>Contacts</span>', html), \
        "голого пункта «Contacts» быть не должно"


# ── FR-SITE10 ─────────────────────────────────────────────────────────────

def test_lang_switch_is_text_between_nav_and_cta():
    html = _html()
    # текстовый переключатель EN | RU: два «текстовых» пункта + разделитель
    assert '<button class="lang-opt active" data-action="lang" data-lang="en">EN</button>' in html
    assert '<button class="lang-opt" data-action="lang" data-lang="ru">RU</button>' in html
    # не кнопка: без фона и рамки
    assert re.search(r"\.lang-opt \{ background: none; border: 0;", html), \
        "пункты переключателя должны выглядеть текстом (без фона/рамки)"
    # позиция: в header-right ПЕРЕД CTA «Free AI Diagnostic» → визуально между меню и CTA
    i_hr = html.find('<div class="header-right">')
    i_ls = html.find('class="lang-switch"')
    i_cta = html.find('class="btn-white cta"')
    assert 0 < i_hr < i_ls < i_cta, "переключатель должен стоять в header-right перед CTA"


def test_lang_switch_positioning():
    """Переключатель сдвинут влево: на десктопе — в промежуток между пилюлей и
    CTA, на мобилке — к логотипу (auto-отступ), на ≤380px — компактный режим,
    иначе он наезжает на лого."""
    html = _html()
    assert re.search(r"@media \(min-width:1024px\) \{.*\.lang-switch \{ margin-right: 2rem; \}", html), \
        "на десктопе переключатель должен отступать от CTA на 2rem"
    assert re.search(r"\.header-right \{ flex: 1 0 auto; \}", html), \
        "на мобилке header-right должен растягиваться, иначе margin-right:auto не сработает"
    assert re.search(r"\.lang-switch \{ margin-left: clamp\([^)]+\); margin-right: auto; \}", html), \
        "на мобилке переключатель прижимается влево к логотипу"
    assert "@media (max-width:380px)" in html, \
        "нужен компактный режим ≤380px, иначе переключатель наезжает на логотип"
    # пилюля смещена левее центра, чтобы освободить место справа
    assert re.search(r"\.nav \{[^}]*left: calc\(50% - 3\.5rem\)", html), \
        ".nav должен быть смещён левее геометрического центра"


def test_lang_ru_dictionary_complete():
    html = _html()
    assert "var RU_TEXT" in html and "'ait_lang'" in html and "var CUES_RU" in html, \
        "нужны словарь RU_TEXT, ключ ait_lang и RU-подписи CUES_RU"
    # каждый размеченный ключ имеет перевод
    for k in set(re.findall(r'data-i18n(?:-ph)?="([^"]+)"', html)):
        assert ("'%s':" % k) in html, "нет перевода для ключа " + k


# ── FR-SITE11 ─────────────────────────────────────────────────────────────

LOGO_URL = "https://i.ibb.co/gn7SmgY/866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png"


def test_logo_url():
    html = _html()
    assert 'src="%s"' % LOGO_URL in html, "лого должно грузиться с рабочего адреса " + LOGO_URL
    assert "/assets/_ait_logo.png" not in html, \
        "путь с ведущим «_» Jekyll не публикует — лого отдаёт 404 (см. FR-SITE11)"


def test_no_underscore_asset_paths():
    """GitHub Pages собирает сайт Jekyll'ом, а он НЕ публикует файлы и папки,
    чьи имена начинаются с «_» → такой ресурс отдаёт 404 (см. FR-SITE11)."""
    html = _html()
    for m in re.finditer(r'(?:src|href)="(/[^"]*)"', html):
        parts = [p for p in m.group(1).split("/") if p]
        assert not any(p.startswith("_") for p in parts), \
            "ресурс с «_» в пути не будет опубликован Jekyll: " + m.group(1)


# ── FR-SITE12 ─────────────────────────────────────────────────────────────

_MOBILE_SCREENS = ("overview", "strategy", "neuronium", "landao",
                   "antropolis", "academy", "dataist")


def test_mobile_screens_share_one_offset():
    """На мобилке контент прижат к низу панели, поэтому ОДИН общий сдвиг для всех
    экранов = одинаковая нижняя линия (кнопки на одном уровне) и одинаковый
    воздух под плашкой «Andre AI»."""
    html = _html()
    m = re.search(r"@media \(max-width:1023px\) \{\s*(\[data-screen[^{]+)\{ transform: translateY\(1\.5rem\); \}", html)
    assert m, "нужно ОДНО общее правило translateY(1.5rem) для мобильных экранов"
    for s in _MOBILE_SCREENS:
        assert '[data-screen="%s"]' % s in m.group(1), \
            "экран «%s» должен быть в общем правиле сдвига" % s
    assert "translateY(-1.8rem)" not in html, \
        "старого подъёма первого экрана быть не должно — из-за него заголовок упирался в плашку"


def test_landscape_resets_mobile_offsets():
    """В ландшафте телефона сдвиги сбрасываются — иначе контент лезет на плашку."""
    html = _html()
    m = re.search(r"(\[data-screen[^{]+)\{ transform: none; \}", html)
    assert m, "в ландшафтном блоке должен быть сброс сдвигов"
    for s in _MOBILE_SCREENS:
        assert '[data-screen="%s"]' % s in m.group(1), \
            "экран «%s» должен сбрасывать сдвиг в ландшафте" % s


# ── FR-SITE17 ─────────────────────────────────────────────────────────────

def _mobile_shadow_stops():
    """Стопы мобильного градиента затемнения: [(альфа, позиция %)]."""
    html = _html()
    m = re.search(r"\.video-shadow \{[^}]*?background: linear-gradient\(to bottom,(.*?)\); \}", html, re.S)
    assert m, "не найден мобильный градиент .video-shadow"
    stops = []
    for a, p, solid in re.findall(r"rgba\(5,5,5,([\d.]+)\)\s+([\d.]+)%|#050505\s+([\d.]+)%", m.group(1)):
        stops.append((1.0, float(solid)) if solid else (float(a), float(p)))
    return stops


def test_video_shadow_has_vh_fallback():
    """Без vh-фолбэка браузеры без поддержки dvh получали height:auto → затемнение
    схлопывалось и переход «видео → чёрное» был резким."""
    html = _html()
    for sel in ("#hero-video", r"\.video-shadow"):
        assert re.search(sel + r" \{[^}]*height: 64vh; height: 64dvh;", html), \
            "%s должен объявлять height в vh ПЕРЕД dvh" % sel
    # ландшафт телефона — тот же приём
    assert re.search(r"#hero-video \{[^}]*height: 100vh; height: 100dvh;", html)
    assert re.search(r"\.video-shadow \{[^}]*height: 100vh; height: 100dvh;", html)


def test_portrait_video_mask_fades_the_video_itself():
    """В части мобильных браузеров (Samsung Internet) видео композитится отдельным
    слоем и оверлей затемнения под него не попадает. В портретной мобилке низ
    растворяет МАСКА на самом видео — её композитор обойти не может."""
    html = _html()
    assert "@media (max-width:1023px) and (orientation: portrait) {" in html, \
        "нужен портретный мобильный блок с маской видео"
    for prop in ("-webkit-mask-image", "mask-image"):
        assert re.search(re.escape(prop) + r": linear-gradient\(to bottom, rgba\(0,0,0,1\) 45%", html), \
            "нужна вертикальная маска %s, начинающаяся с непрозрачного 45%%" % prop
    assert html.count("rgba(0,0,0,0) 100%)") >= 2, \
        "маска должна доходить до полной прозрачности ровно на 100%"
    # оверлей гасим ТОЛЬКО там, где маски поддерживаются — иначе он остаётся рабочим
    assert re.search(
        r"@supports \(mask-image: linear-gradient\(#000, transparent\)\)[^{]*\{\s*\.video-shadow \{ background: none; \}",
        html), "гашение оверлея должно быть внутри @supports (иначе старые браузеры останутся без затемнения)"
    # JS не должен ставить mask:none на мобилке — это перебило бы CSS-маску
    fn = html[html.find("function applyVideoMask"):html.find("/* ---- captions")]
    assert ": '';" in fn and ": 'none';" not in fn, \
        "applyVideoMask на мобилке снимает инлайн-маску пустой строкой, а не ставит none"


def test_video_shadow_is_short_and_smooth():
    stops = _mobile_shadow_stops()
    assert len(stops) >= 12, "мало стопов (%d) — на слабых экранах будут полосы" % len(stops)
    # затемнение КОРОТКОЕ: до 40% высоты видео его нет (раньше начиналось с 6%)
    first_dark = next(p for a, p in stops if a > 0)
    assert first_dark >= 40, "затемнение начинается слишком высоко (%.0f%%) и темнит бороду" % first_dark
    # сплошной чёрный ровно на нижней кромке → бесшовный стык со страницей
    assert stops[-1] == (1.0, 100.0), "градиент должен доходить до #050505 ровно на 100%%, а не %s" % (stops[-1],)
    # монотонность и плавность
    alphas = [a for a, _ in stops]
    assert alphas == sorted(alphas), "альфа должна расти монотонно"
    steps = [round(b - a, 3) for a, b in zip(alphas, alphas[1:])]
    assert max(steps) <= 0.12, "слишком резкий скачок альфы: %.2f" % max(steps)


# ── FR-SITE18 ─────────────────────────────────────────────────────────────

def test_bottom_always_black():
    html = _html()
    assert re.search(r"html, body \{[^}]*overscroll-behavior: none;", html), \
        "overscroll-behavior: none гасит «оттяжку», из-за которой снизу светился фон браузера"
    assert re.search(r"body::after \{[^}]*position: fixed;[^}]*bottom: 0;", html), \
        "нужна фиксированная полоса, закрывающая зону системной панели"
    assert re.search(r"body::after \{[^}]*height: env\(safe-area-inset-bottom, 0px\);[^}]*background: #050505;", html), \
        "полоса должна быть высотой safe-area-inset-bottom и чёрной"


# ── FR-SITE19 ─────────────────────────────────────────────────────────────

def test_mic_pulses_on_mobile():
    html = _html()
    assert re.search(r"\.mic-wave \{[^}]*display: none;", html), \
        "по умолчанию кольцо скрыто"
    assert re.search(r"\.mic-wave\.on \{ display: block; \}", html), \
        "со звуком кольцо включается классом .on"
    assert re.search(r"@media \(max-width:1023px\) \{ \.mic-wave \{ display: block; \} \}", html), \
        "на мобилке кольцо должно пульсировать всегда"
    assert "micWave.classList.toggle('on', !m)" in html, \
        "видимостью управляет класс, а не инлайн-стиль (иначе media-правило не перебить)"
    assert not re.search(r'id="mic-wave"[^>]*style="display: none;"', html), \
        "инлайн-стиля display:none у #mic-wave быть не должно"
    assert re.search(r"\.mic-wave::before, \.mic-wave::after \{[^}]*border: 1px solid #8854F3;[^}]*animation: soundWave", html), \
        "кольцо — фиолетовое (#8854F3) с анимацией soundWave"


# ── FR-SITE26: правки по скринам нового меню ─────────────────────────────

def test_sec_link_gap_matches_hero():
    """Зазор «кнопка → серая ссылка» одинаковый на всех экранах (как у героя):
    1.1rem = gap секции + margin-top ссылки."""
    html = _html()
    # герой: gap 1.75rem − 0.65rem = 1.1rem
    assert re.search(r"\.about-link \{[^}]*margin-top: -0\.65rem;", html)
    # секции: моб gap 0.85rem + 0.25rem = 1.1rem; десктоп 1.35rem − 0.25rem = 1.1rem
    assert re.search(r"\.sec-link \{[^}]*margin-top: 0\.25rem;", html), \
        "на мобилке .sec-link добирает зазор до 1.1rem (+0.25rem)"
    assert re.search(r"@media \(min-width:1024px\) \{ \.sec-link \{ margin-top: -0\.25rem;", html), \
        "на десктопе .sec-link сокращает зазор до 1.1rem (−0.25rem)"


def test_landao_desc_mindful_living():
    html = _html()
    assert '>Your Personal AI Assistant <span class="nb">for Mindful Living</span><' in html, \
        "описание Landao: «Your Personal AI Assistant for Mindful Living» (хвост не разрывается)"
    assert 'Ваш персональный ИИ-ассистент <span class="nb">для осознанной жизни</span>' in html, \
        "RU-описание Landao должно упоминать осознанную жизнь"


def test_hero_sub_always_one_line():
    """Подзаголовок героя в одну строку на мобилке и вебе: nowrap + кегль от vw,
    отдельный для EN (44 зн.) и RU (53 зн.)."""
    html = _html()
    assert re.search(r'<p class="desc hero-sub" data-i18n="hero\.sub"', html), \
        "подзаголовку героя нужен класс hero-sub"
    assert re.search(r"\.desc\.hero-sub \{ white-space: nowrap; max-width: none;", html), \
        "hero-sub должен запрещать перенос"
    assert re.search(r'html\[lang="ru"\] \.desc\.hero-sub \{ font-size: clamp\(', html), \
        "у RU своя (меньшая) лестница кегля — строка длиннее"
    # и в десктопном, и в ландшафтном блоке есть свои клампы (перебивают .desc)
    assert html.count(".desc.hero-sub { font-size: clamp(") >= 4


def test_lang_switch_js_centres_between_pill_and_cta():
    """EN | RU стоит ПО СЕРЕДИНЕ между пилюлей меню и CTA: середина промежутка
    вычисляется в JS (ширина пилюли зависит от языка), CSS-отступ — фолбэк."""
    html = _html()
    assert "function placeLangSwitch()" in html
    assert "var navRight = nav.offsetLeft + nav.offsetWidth / 2;" in html, \
        "правый край пилюли: offsetLeft + width/2 (offsetLeft не знает про translateX(-50%))"
    assert "(navRight + headerCta.offsetLeft) / 2" in html, \
        "середина промежутка = (право пилюли + лево CTA) / 2"
    # пересчёт: на ресайзе, при смене языка и после загрузки веб-шрифта
    assert re.search(r"var onResize = function \(\) \{[^}]*placeLangSwitch\(\);", html)
    assert html.count("placeLangSwitch();") >= 3


def test_mobile_menu_brand_and_higher_items():
    html = _html()
    # бренд-шапка: тот же значок, что в хедере, + надпись
    m = re.search(r'<div class="nav-brand"[^>]*>\s*<img class="nav-brand-img" src="([^"]+)"', html)
    assert m and m.group(1) == LOGO_URL, "в меню сверху слева — тот же логотип, что на главной"
    assert re.search(r'<span class="nav-brand-name">Andre AI Technologies</span>', html)
    assert re.search(r"\.nav\.open \.nav-brand \{[^}]*position: absolute; top: 1\.1rem; left: 1\.1rem;", html)
    # пункты подтянуты выше: не центр, а от верха
    assert re.search(r"\.nav\.open \{[^}]*justify-content: flex-start;[^}]*padding: clamp\(", html), \
        "список меню прижат выше (flex-start), а не по центру экрана"


def test_strategy_h2_is_short():
    html = _html()
    assert re.search(r'data-i18n="strategy\.h2">AI Strategy</h2>', html), \
        "заголовок экрана стратегии — «AI Strategy» (без Transformation)"
    assert "AI Transformation Strategy</h2>" not in html
    assert "'strategy.h2': 'ИИ-стратегия'" in html


def test_ru_legal_links_fit_one_line():
    """«Политика конфиденциальности» и «Условия использования» на RU — каждая в
    одну строку: nowrap + уменьшенный кегль только для русского."""
    html = _html()
    assert re.search(r"\.nav-legal-link \{[^}]*white-space: nowrap;", html)
    assert re.search(r'html\[lang="ru"\] \.nav-legal-link \{ font-size: clamp\(', html), \
        "на RU кегль юр-ссылок меню меньше — иначе они не помещаются в строку"
    assert re.search(r'html\[lang="ru"\] \.legal-link \{ font-size: clamp\(', html), \
        "на RU кегль юр-ссылок футера контактов тоже уменьшается"
    assert re.search(r"\.legal-link \{[^}]*white-space: nowrap;", html)


def test_tiles_are_small_squares_without_bars():
    """FR-SITE27: плитки-иконки — квадратные, меньше и БЕЗ полосок-«подчёркиваний»;
    на мобилке дополнительно ужаты scale'ом, чтобы не вылезать на видео."""
    html = _html()
    assert 'class="bar"' not in html and ".tile .bar" not in html, \
        "цветных полосок под иконками (.bar) быть не должно"
    m = re.search(r"\.tile\.sm \{ width: ([\d.]+)rem; height: ([\d.]+)rem; \}", html)
    assert m and m.group(1) == m.group(2), "малая плитка должна быть квадратной"
    m = re.search(r"\.tile\.lg \{ width: ([\d.]+)rem; height: ([\d.]+)rem;", html)
    assert m and m.group(1) == m.group(2), "большая плитка должна быть квадратной"
    m = re.search(r"\.float-row \{[^}]*transform: scale\(([\d.]+)\);", html)
    assert m and float(m.group(1)) <= 0.72, \
        "на мобилке плитки дополнительно ужимаются (scale ≤ 0.72)"
    # размер иконок задаёт CSS, а не инлайн-стили (инлайн его не перебьёт)
    assert re.search(r"\.tile\.sm i \{ font-size: \d+px; \}", html)
    assert re.search(r"\.tile\.lg i \{ font-size: \d+px; \}", html)
    assert not re.search(r'\.tile[^<]*<i[^>]*style="font-size', html)


def test_desc_breaks_are_semantic():
    """FR-SITE27: двухстрочные подписи переносятся ПО СМЫСЛУ — хвостовая группа
    («для вашего бизнеса», «for Mindful Living»…) обёрнута в .nb и не рвётся."""
    html = _html()
    assert re.search(r"\.nb \{ white-space: nowrap; \}", html), "нужен класс .nb (nowrap)"
    for tail in ("AI Transformation Roadmap", "for Your Business", "for Mindful Living",
                 "for Human Good", "AI Can&rsquo;t Replace", "Insights &amp; Technologies",
                 "into an AI Company?",
                 "вашей ИИ-трансформации", "для вашего бизнеса", "для осознанной жизни",
                 "во благо человека", "которые ИИ не заменит", "и ИИ-технологии",
                 "в ИИ-компанию?"):
        assert '<span class="nb">%s</span>' % tail in html, \
            "хвост «%s» должен быть неразрывной группой .nb" % tail
    # подпись контакта: «…бизнес в ИИ-компанию?» вместо «…с помощью ИИ?»
    assert "с помощью ИИ?" not in html


def test_desktop_content_optically_centred():
    """Контент тёмной панели на десктопе сдвинут чуть вниз — в зрительную середину
    (шапка съедает верх). Экран контакта не сдвигается: у него футер у низа."""
    html = _html()
    assert re.search(r"@media \(min-width:1024px\) \{ \.scroll \{[^}]*transform: translateY\(1\.4rem\);", html)
    assert re.search(r"\.scroll:has\(\.contact-screen\.active\) \{[^}]*transform: none;", html)
    assert re.search(r"\.contact-hero \{[^}]*top: 1\.4rem;[^}]*\} \}", html) or \
        re.search(r"@media \(min-width:1024px\) \{ \.contact-hero \{[^}]*top: 1\.4rem;", html), \
        "герой контакта получает тот же сдвиг через top"


def test_desktop_typography_scaled_up():
    """Жалоба «на компе мелко»: клампы контентной колонки подняты и растут с окном."""
    html = _html()
    assert ".desc { font-size: clamp(15.5px, 1.3vw, 23px); max-width: 34rem; }" in html
    assert ".h2-size { font-size: clamp(2.2rem, 2.75vw, 3.7rem); }" in html
    assert ".hero-size { font-size: clamp(1.7rem, 3.3vw, 3rem); }" in html
    assert html.count("font-size: clamp(11.5px, 0.95vw, 16px)") == 6, \
        "кнопки шести секций должны использовать общий увеличенный кламп"


# ── FR-SITE30: русские названия продуктов ────────────────────────────────

def test_ru_product_names():
    """На русском продукты называются по-русски: заголовки экранов и пункты меню."""
    html = _html()
    for key, ru in (("'nav.neuronium'", "Нейроний"), ("'nav.landao'", "Ландао"),
                    ("'nav.antropolis'", "Антрополис"), ("'nav.dataist'", "Датаист"),
                    ("'neuronium.h2'", "Нейроний ИИ"), ("'landao.h2'", "Ландао ИИ"),
                    ("'antropolis.h2'", "Антрополис Сити"), ("'dataist.h2'", "Датаист Медиа")):
        assert re.search(key + r":\s*'" + ru + r"'", html), \
            "в RU_TEXT должен быть %s: «%s»" % (key, ru)
    # ключи привязаны к разметке (меню и заголовкам)
    for k in ("nav.neuronium", "nav.landao", "nav.antropolis", "nav.dataist",
              "neuronium.h2", "landao.h2", "antropolis.h2", "dataist.h2"):
        assert 'data-i18n="%s"' % k in html, "ключ %s должен стоять в разметке" % k
    # русские названия и в RU-кнопках
    assert "Познакомиться с Ландао ИИ" in html
    assert "Войти в Антрополис" in html
    assert "с Landao AI" not in html and "в Antropolis" not in html


# ── FR-SITE28: видео на языке интерфейса + постер-заглушка ───────────────

def test_video_per_language_with_poster():
    html = _html()
    m = re.search(r'<video id="hero-video" src="([^"]+)" poster="([^"]+)"[^>]*>', html)
    assert m, "нужен тег видео с src и poster"
    assert m.group(1) == "/assets/Andre_AIT_video_compressed.mp4", \
        "по умолчанию (EN) — новый ролик из assets этого репозитория"
    assert m.group(2) == "/andre_ai.jpg", \
        "постер-заглушка andre_ai.jpg — чёрного фона не бывает"
    assert "loop muted autoplay playsinline" in m.group(0)
    assert "'/assets/Andre_AIT_video_compressed_ru.mp4'" in html, \
        "у русского языка свой ролик"
    assert "function setVideoLang(" in html and "setVideoLang(lang);" in html, \
        "смена языка должна переключать ролик"
    assert "videoBlobs[lang] = URL.createObjectURL(b);" in html, \
        "каждый ролик кэшируется в blob (цикл без сети, FR-SITE25)"
    assert '<link rel="preload" as="image" href="/andre_ai.jpg" fetchpriority="high">' in html, \
        "постер грузится первым приоритетом"
    assert "hero-poster.jpg" not in html, "ссылок на старый постер быть не должно"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print("PASS", fn.__name__)
    print("\nВсе тесты сайта пройдены:", len(fns))
