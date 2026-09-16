# -*- coding: utf-8 -*-
"""FR-SITE41 — лендинг AI Strategy (/strategy/ и /strategy/ru/).

Страница листается экранами, как биография и главная. Без зависимостей:
`python3 tests/test_strategy.py` или через pytest.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _en():
    return _read("strategy/index.html")


def _ru():
    return _read("strategy/ru/index.html")


def _pages():
    return (("en", _en()), ("ru", _ru()))


# ── страницы, общая вёрстка, языки ────────────────────────────────────────

def test_pages_and_shared_assets_exist():
    for rel in ("strategy/index.html", "strategy/ru/index.html",
                "assets/strategy.css", "assets/strategy.js",
                "tools/build_strategy.py", "tools/strategy_copy.py"):
        assert os.path.exists(os.path.join(_ROOT, rel)), "нет файла " + rel


def test_pages_share_css_and_js():
    for lang, html in _pages():
        assert '<link rel="stylesheet" href="/assets/strategy.css">' in html, lang
        assert '<script src="/assets/strategy.js"></script>' in html, lang


def test_html_lang_and_cross_links():
    en, ru = _en(), _ru()
    assert '<html lang="en">' in en and '<html lang="ru">' in ru
    assert '<a class="lang-opt" href="/strategy/ru/">RU</a>' in en
    assert '<a class="lang-opt" href="/strategy/">EN</a>' in ru
    assert '<span class="lang-opt active">EN</span>' in en
    assert '<span class="lang-opt active">RU</span>' in ru


def test_each_page_uses_its_own_video():
    assert 'src="/assets/Andre_AIT_video_compressed.mp4"' in _en()
    assert 'src="/assets/Andre_AIT_video_compressed_ru.mp4"' in _ru()


def test_language_is_stored_for_the_main_site():
    assert "localStorage.setItem('ait_lang', lang)" in _read("assets/strategy.js")


def test_pages_are_generated_not_hand_written():
    """Править strategy/*.html руками нельзя — сборка перезапишет."""
    for lang, html in _pages():
        assert "tools/build_strategy.py" in html, lang + ": в шапке файла нет отметки о сборке"


# ── FR-SITE41: лицо слева на полэкрана, кружок только на мобилке ──────────

def test_face_is_always_half_the_screen_on_web():
    css = _read("assets/strategy.css")
    assert "--head-w: 50%;" in css, "лицо занимает половину экрана"
    assert "50vw" not in css, "рамку страницы нельзя мерить в vw: body{zoom} их умножает"
    assert ".head.mini" not in css, "на вебе голова не сжимается в кружок"
    mob = [b for b in re.findall(r"@media \(max-width:1023px\) \{.*?\n\}", css, re.S) if ".head {" in b]
    assert mob and "border-radius: 50%" in mob[0], "на мобилке голова — кружок"


def test_head_is_draggable_on_mobile_and_clickable():
    js = _read("assets/strategy.js")
    assert "pointerdown" in js and "pointermove" in js, "кружок на мобилке должен перетаскиваться"
    assert "if (mqDesk.matches) return;" in js, "на вебе лицо — колонка, двигать нечего"
    assert "ait_strategy_head" in js, "место кружка запоминается"


# ── лендинг листается экранами, как биография ─────────────────────────────

SCREEN_IDS = ["top", "numbers", "usecases", "solution",
              "learning", "pricing", "start"]


def test_landing_is_a_deck_of_screens():
    """Не простыня и не scroll-snap: экраны сменяют друг друга анимацией."""
    css = _read("assets/strategy.css")
    assert "scroll-snap-type: y" not in css, "вертикальной прокрутки страницы нет — только смена экранов"
    assert "scroll-snap-type: x mandatory" in css, "горизонтальная лента артефактов прилипает по-прежнему"
    assert re.search(r"html, body \{.*?overflow: hidden", css, re.S), "страница сама не прокручивается"
    assert ".screen.active { display: flex; }" in css
    assert ".deck.leaving .screen.active" in css and ".deck.entering .screen.active" in css
    assert "@keyframes slideInScreen" in css
    for lang, html in _pages():
        assert html.count('<section class="screen') == 13, lang + ": тринадцать экранов"
        for sid in SCREEN_IDS:
            assert 'id="%s"' % sid in html, "%s: нет экрана %s" % (lang, sid)


def test_screens_switch_by_wheel_swipe_and_keys():
    js = _read("assets/strategy.js")
    for handler in ("'wheel'", "'touchstart'", "'touchend'", "'keydown'"):
        assert js.count(handler), "нет обработчика " + handler
    assert "innerScroll" in js, "внутри прокручиваемых лент колесо не перехватывается"
    assert re.search(r"now - lastWheel < \d+", js), "один жест = один экран"


def test_menu_lists_six_product_chapters():
    """Экран с вопросами удалён, первый пункт теперь «Solution» (правка владельца)."""
    nav = ["solution", "usecases", "process", "learning", "pricing", "start"]
    for lang, html in _pages():
        header = html[html.index("<header>"):html.index("</header>")]
        for key in nav:
            assert 'data-go="%s"' % key in header, "%s: в меню нет раздела %s" % (lang, key)
        assert header.count('class="nav-tab') == len(nav), lang + ": в меню шесть разделов"
    assert ">Use Cases<" in _en(), "раздел называется Use Cases, а не Businesses"
    assert ">Problem<" not in _en(), "пункта «Problem» в меню быть не должно"
    assert ">Solution<" in _en(), "первый раздел называется Solution"


def test_home_icon_replaces_the_back_button():
    """Правка владельца: «вместо кнопки BACK иконку домой рядом с меню»."""
    css = _read("assets/strategy.css")
    assert ".back {" not in css, "овала «назад» на странице больше нет"
    home = re.search(r"\.nav-home \{(.*?)\}", css, re.S)
    assert home, "нет стиля иконки дома"
    for lang, html in _pages():
        header = html[html.index("<header>"):html.index("</header>")]
        assert header.count('class="nav-home" href="/"') == 1, lang + ": одна иконка дома в шапке"
        assert header.index('class="nav-home"') < header.index('class="nav-tab'), \
            lang + ": иконка дома стоит ПЕРЕД пунктами меню"
        assert 'class="back"' not in html, lang + ": кнопок «назад» на экранах больше нет"
        assert 'class="prod-name"' not in html, lang + ": у лого не пишем название продукта"
    assert "location.href = '/'" not in _read("assets/strategy.js"), \
        "иконка дома — обычная ссылка, скрипт тут не нужен"


def test_header_matches_the_main_site():
    """Кнопки сверху — того же размера и на тех же местах, что на главной."""
    css = _read("assets/strategy.css")
    site = _read("index.html")
    for rule in ("width: clamp(2.85rem, 12vw, 3.7rem)",     # лого
                 "height: 2.85rem",                          # пилюля меню и кнопка
                 "font-size: 14px; font-weight: 500",        # пункты меню
                 "padding: 0 1.4rem; font-size: 11.5px"):    # кнопка действия
        assert rule in css, "в шапке лендинга нет правила «%s» с главной" % rule
        assert rule in site or rule.replace("; ", ";\n") in site, "правило «%s» изменилось на главной" % rule
    assert "location.href = '/'" not in _read("assets/strategy.js"), \
        "«назад» — обычная ссылка на главную, скрипт тут не нужен"


def test_page_scales_like_the_main_site():
    """Масштабирование body zoom — как на главной, чтобы вид совпадал."""
    css = _read("assets/strategy.css")
    site = _read("index.html")
    for w in ("1600px", "1900px", "2300px"):
        assert re.search(r"min-width: ?%s" % w, css), "нет ступени масштаба " + w
        assert re.search(r"min-width: ?%s" % w, site), "ступень %s пропала на главной" % w
    assert css.count("zoom:") >= 3, "масштаб задаётся через zoom, как на главной"


# ── первый экран ──────────────────────────────────────────────────────────

def test_hero_headline_is_two_lines_with_orange_business():
    for lang, html in _pages():
        h1 = re.search(r"<h1>(.*?)</h1>", html, re.S).group(1)
        assert h1.count('<span class="l">') == 2, lang + ": заголовок ровно в две строки"
        assert 'class="hl-o">' in h1, lang + ": «бизнес» — оранжевым"
    assert "AI Strategy shows how to transform your business with AI" in _en()
    assert 'class="hl-o">business<' in _en()
    assert 'class="hl-o">бизнес' in _ru()


def test_hero_has_two_buttons_of_equal_size():
    css = _read("assets/strategy.css")
    hero = re.search(r"\.hero-cta \.btn \{([^}]*)\}", css).group(1)
    assert "width: 13.5rem" in hero and "flex: 0 0 13.5rem" in hero, \
        "две кнопки первого экрана — ровно одного размера"
    for lang, html in _pages():
        hero = html[html.index('id="top"'):html.index("</section>", html.index('id="top"'))]
        assert hero.count('class="btn btn-') == 2, lang + ": на первом экране ровно две кнопки"


def test_buttons_do_not_move_on_hover():
    """Правка владельца: кнопка не должна ездить под курсором."""
    css, js = _read("assets/strategy.css"), _read("assets/strategy.js")
    assert "magnetic" not in css and "magnetic" not in js, "магнитных кнопок быть не должно"
    for m in re.finditer(r"\.btn[^{]*:hover \{([^}]*)\}", css):
        assert "translate" not in m.group(1), "кнопка не смещается при наведении: " + m.group(1)


# ── экран «Problem» и цифры рынка ─────────────────────────────────────────

def test_questions_screen_is_gone():
    """Владелец убрал экран «The problem is no longer access to AI» целиком."""
    for lang, html in _pages():
        assert 'class="q-item"' not in html, lang + ": экран с вопросами должен быть удалён"
        for mark in ("The problem is no longer", "Проблема больше не в доступе",
                     "That is exactly what AI Strategy", "Именно на эти вопросы"):
            assert mark not in html, "%s: остался текст «%s»" % (lang, mark)
    assert ".q-item" not in _read("assets/strategy.css"), "правила удалённого экрана убраны"


def test_process_intro_screen_is_gone():
    """«От „нам нужен ИИ“…» убран — сразу к зрелости."""
    for lang, html in _pages():
        for mark in ("here’s what to build", "вот что мы строим"):
            assert mark not in html, "%s: вводный экран шагов должен быть удалён" % lang
        first_step = html.index('data-step="1"')
        assert html.index('id="usecases"') < first_step, lang + ": шаги идут после кейсов"


def test_market_numbers_are_four_squares_without_hover_jump():
    css = _read("assets/strategy.css")
    for m in re.finditer(r"\.num-card:hover \{([^}]*)\}", css):
        assert "translate" not in m.group(1), "квадраты не прыгают при наведении"
    for lang, html in _pages():
        assert html.count('class="num-card"') == 4, lang + ": четыре квадрата рынка"
        assert html.count('class="num-val"') == 4, lang + ": четыре цифры"
        for v in ("76", "14", "81", "73"):
            assert ">%s" % v in html, "%s: нет цифры %s" % (lang, v)
        assert 'class="nums-foot"' in html, lang + ": оранжевая строка про конкурентов"
    assert "Don’t let your competitors get ahead with AI" in _en()
    assert "Anthropic" not in _en(), "сноску про Anthropic владелец просил убрать"


# ── Use Cases ─────────────────────────────────────────────────────────────

def test_use_cases_fit_one_screen_with_one_metric_each():
    for lang, html in _pages():
        assert html.count('class="biz"') == 8, lang + ": восемь карточек"
        assert html.count('class="biz-metric"') == 8, lang + ": по одной метрике на карточку"
        assert html.count('class="biz-ic"') == 8, lang + ": иконка слева от названия"
        assert html.count('class="biz-go"') == 8, lang + ": «Explore» справа"
        assert 'class="biz-all"' in html, lang + ": простая ссылка на все типы бизнеса"
    css = _read("assets/strategy.css")
    assert re.search(r"\.biz-grid \{[^}]*minmax\(0, ?1fr\)", css), "карточки не вылезают за экран"
    assert ".rail-wrap::before" in css and ".rail-wrap::after" in css, \
        "края ленты уходят в тёмный градиент"


# ── Solution: восемь артефактов с новыми названиями ───────────────────────

DELIVERABLES_EN = ["AI Maturity Index", "Process Map", "Cognitive Map", "AI Opportunities",
                   "Human + AI", "AI-First Model", "AI Agents", "Roadmap"]


def test_solution_cards_use_the_agreed_names():
    en = _en()
    assert en.count('class="out"') == 8, "восемь артефактов"
    for name in DELIVERABLES_EN:
        assert ">%s<" % name in en, "нет карточки «%s»" % name
    for lang, html in _pages():
        assert html.count('class="out"') == 8, lang + ": восемь артефактов"


# ── How it works: шесть шагов и перелёт оранжевых блоков ──────────────────

def test_six_steps_each_on_its_own_screen():
    for lang, html in _pages():
        assert html.count('class="screen step-screen"') == 6, lang + ": шесть шагов"
        assert html.count('<div class="stage-card"') == 6, lang + ": шесть сцен продукта"
        for n in range(1, 7):
            assert 'data-step="%d"' % n in html, "%s: нет шага %d" % (lang, n)
        assert 'data-step="7"' not in html, lang + ": шагов должно быть шесть, не больше"


def test_orange_blocks_fly_from_process_to_opportunities_to_ai_first():
    """Правка владельца: оранжевые блоки перелетают AS-IS → AI Opportunity → AI-First."""
    for lang, html in _pages():
        keys = re.findall(r'data-flip="([a-zа-яё0-9-]+)"', html)
        trio = [k for k in set(keys) if keys.count(k) == 3]
        assert len(trio) == 3, \
            "%s: три блока должны проходить все три сцены, нашлось %s" % (lang, sorted(trio))
        for cls in ("pnode human", "opnode", "fnode human"):
            assert re.search(r'class="%s" data-seq data-flip="[a-zа-яё0-9-]+"' % cls, html), \
                "%s: нет связанного блока на сцене «%s»" % (lang, cls)
        # то, что забрал ИИ, пары не находит и просто гаснет
        solo = [k for k in set(keys) if keys.count(k) == 1]
        assert solo, lang + ": операции, ушедшие к ИИ, не должны иметь пары"
    js = _read("assets/strategy.js")
    assert "captureFlip" in js and "playFlip" in js, "перелёт блоков должен быть реализован"
    assert "offsetIn" in js, "позиции считаются через offset, чтобы transform не мешал"
    css = _read("assets/strategy.css")
    assert ".deck.morph .screen.active .stage-card" in css, \
        "во время перелёта карточка не въезжает заново"
    assert ".deck.leaving.morph-out .screen.active { transform: none; }" in css, \
        "уходящий экран при перелёте только гаснет"


def test_people_are_orange_and_agents_are_purple():
    css = _read("assets/strategy.css")
    ORANGE, PURPLE = "249,115,22", "136,84,243"
    assert re.search(r"\.pnode\.human \{[^}]*" + ORANGE, css), "люди в процессах — оранжевые"
    assert re.search(r"\.fnode\.human \{[^}]*" + ORANGE, css), "люди в AI-First — оранжевые"
    assert re.search(r"\.fnode\.ai \{[^}]*" + PURPLE, css), "агенты — фиолетовые"


def test_maturity_scene_shows_score_above_the_radar():
    for lang, html in _pages():
        card = html[html.index('data-step="1"'):html.index('data-step="2"')]
        assert card.index('class="score"') < card.index('class="radar"'), \
            lang + ": оценка стоит над паутиной"
    en = _en()
    for dim in ("Strategy", "People", "Infrastructure", "Data", "Models", "Implementation", "R&D"):
        assert ">%s<" % dim in en, "нет оси зрелости «%s»" % dim


def test_agent_passport_fields_sit_around_the_agent():
    """Иконка агента — в центре, поля вокруг (координаты считает сборщик)."""
    for lang, html in _pages():
        spokes = re.findall(r'<span class="spoke" data-seq style="left:([\d.]+)%; top:([\d.]+)%"', html)
        assert len(spokes) == 8, lang + ": восемь полей паспорта агента"
        assert len(set(spokes)) == 8, lang + ": поля не должны слипаться в центре"
        assert 'class="hub-core"' in html, lang + ": агент в центре"


def test_company_model_and_team_blocks_are_gone():
    """Владелец просил убрать блоки модели компании и команды."""
    for lang, html in _pages():
        assert 'id="model"' not in html, lang + ": блок модели компании удалён"
        assert 'id="team"' not in html, lang + ": блок команды удалён"


# ── Learning ──────────────────────────────────────────────────────────────

def test_learning_has_an_endless_roles_ticker():
    css = _read("assets/strategy.css")
    assert "@keyframes tick" in css and "translateX(-50%)" in css, "лента ролей крутится без конца"
    for lang, html in _pages():
        assert html.count('class="role"') == 24, lang + ": 12 ролей, продублированных для бесшовной ленты"
        roles = html[html.index('class="ticker"'):]
        assert roles.count("fa-solid") >= 24, lang + ": у каждой роли своя иконка"


# ── Pricing ───────────────────────────────────────────────────────────────

def test_pricing_is_one_block_with_strikethrough_comparison():
    for lang, html in _pages():
        assert html.count('<article class="plan') == 4, lang + ": четыре тарифа"
        assert html.count('class="cmp old"') >= 1, lang + ": сравнение зачёркнуто"
        assert "$0" in html and "$59" in html and "$199" in html and "$499" in html, lang
        assert "What is an operation?" not in html and "Что такое операция?" not in html, \
            lang + ": пояснение про операции владелец просил убрать"
    css = _read("assets/strategy.css")
    assert "text-decoration: line-through" in css, "старая цена зачёркнута"
    assert re.search(r"\.plans \{[^}]*minmax\(0, ?1fr\)", css), "тарифы не вылезают за экран"


# ── финал и подвал ────────────────────────────────────────────────────────

def test_final_screen_carries_the_footer():
    for lang, html in _pages():
        final = html[html.index('id="start"'):]
        assert "<footer" in final, lang + ": подвал живёт на последнем экране"
        assert 'class="company"' in final, lang + ": название компании внизу"
        assert "2026" in final, lang + ": копирайт внизу"
        assert final.count("fa-") >= 3, lang + ": иконки соцсетей внизу"


def test_cta_targets_the_product():
    for lang, html in _pages():
        hrefs = re.findall(r'class="btn btn-[a-z]+[^"]*" href="([^"]+)"', html)
        assert hrefs, lang + ": на странице должны быть кнопки"
        for h in hrefs:
            assert h == "https://strategy.andre.technology/", lang + ": кнопка ведёт мимо продукта: " + h


# ── общие правила спеки и владельца ───────────────────────────────────────

def test_reduced_motion_is_respected():
    css, js = _read("assets/strategy.css"), _read("assets/strategy.js")
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert "prefers-reduced-motion: reduce" in js, "скрипт тоже должен уважать настройку"


def test_headings_have_no_trailing_dots():
    for lang, html in _pages():
        for tag in ("h1", "h2", "h3"):
            for m in re.finditer(r"<%s[^>]*>(.*?)</%s>" % (tag, tag), html, re.S):
                text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                assert not text.endswith("."), "%s: точка в конце <%s>: %s" % (lang, tag, text[-40:])


def test_copy_makes_no_guarantees():
    for lang, html in _pages():
        assert "replace McKinsey" not in html and "заменяем McKinsey" not in html, lang


def test_agent_passport_is_purple_orange():
    """Правка владельца: «где агент давай фиолетово-оранжевый»."""
    css = _read("assets/strategy.css")
    core = re.search(r"\.hub-core \{(.*?)\}", css, re.S).group(1)
    assert "rgba(136,84,243" in core and "rgba(249,115,22" in core, \
        "карточка агента должна быть фиолетово-оранжевой"
    edge = re.search(r"\.hub-core::before \{(.*?)\}", css, re.S).group(1)
    assert "var(--p)" in edge and "var(--o)" in edge, "рамка агента — градиент из двух цветов"
    assert ".spoke:nth-of-type(even) { border-color: rgba(249,115,22" in css, \
        "поля вокруг агента чередуются фиолетовым и оранжевым"


def test_process_chain_has_no_dangling_connectors():
    """Цепочка идёт рядами по три со стрелкой переноса — без висящих чёрточек."""
    css = _read("assets/strategy.css")
    assert ".pnode.linked::after" not in css, "псевдо-соединители убраны"
    assert ".prow {" in css and ".pwrap {" in css, "цепочка рисуется рядами"
    for lang, html in _pages():
        assert html.count('class="prow"') == 2, lang + ": два ряда процессов"
        assert html.count('class="pwrap"') == 1, lang + ": одна стрелка переноса"
        assert html.count('class="frow"') == 2, lang + ": AI-First тоже рядами"


def test_one_line_headings_are_fitted_by_script():
    """clamp в vw не спасал: на 1280–1366px строка вылезала за колонку."""
    js = _read("assets/strategy.js")
    assert "function fitHeadings" in js, "нет подбора кегля"
    assert "fitHeadings(screens[cur])" in js, \
        "подбор обязан работать на показанном экране: у скрытого clientWidth = 0"
    assert "!root.querySelectorAll" in js, \
        "resize передаёт событие — его нельзя принимать за узел"


def test_rail_left_fade_only_after_scrolling():
    """Растушёвка слева гасила первую карточку в покое."""
    css = _read("assets/strategy.css")
    assert ".rail-wrap.scrolled::before { opacity: 1; }" in css
    assert re.search(r"\.rail-wrap::before \{[^}]*opacity: 0", css, re.S), \
        "в покое левой растушёвки нет"
    assert "classList.toggle('scrolled'" in _read("assets/strategy.js")


def test_explore_label_survives_on_mobile():
    """Владелец просил подпись «Explore →», а не голую стрелку."""
    css = _read("assets/strategy.css")
    assert ".biz-go span { display: none; }" not in css, \
        "на мобилке подпись «Explore» не прячем"


def test_final_screen_content_is_centred():
    """На финальном экране между кнопкой и подвалом зияла половина экрана."""
    css = _read("assets/strategy.css")
    wrap = re.search(r"\.final \.wrap \{(.*?)\}", css, re.S).group(1)
    assert "justify-content: center" in wrap, "призыв — по центру экрана"
    assert "flex: 1 1 auto" in wrap, "блок занимает высоту до подвала"
    assert ".final footer { margin-top: auto;" in css, "подвал прижат к низу"


def test_screens_never_clip_their_top_when_content_is_tall():
    """Верх длинного экрана обязан оставаться доступным: на лендинге это
    `safe center`, в биографии — жёсткая привязка к верху (правка владельца:
    заголовок главы не должен прыгать от слайда к слайду)."""
    assert "justify-content: safe center" in _read("assets/strategy.css"), \
        "на лендинге нет safe-центрирования"
    about = _read("assets/about.css")
    assert "justify-content: flex-start" in about, \
        "в биографии экран прижат к постоянному верху"
    assert "justify-content: safe center" not in about, \
        "вертикального центрирования в биографии больше нет — оно двигало заголовок"


def test_process_blocks_are_the_same_size_on_every_scene():
    """Правка владельца «элементы покрупнее» самонейтрализовалась: в правилах
    .node и .opnode было ПО ДВА объявления font-size, и меньшее побеждало."""
    css = _read("assets/strategy.css")
    for sel in (".node {", ".opnode {"):
        i = css.index(sel)
        body = css[i:css.index("}", i)]
        assert body.count("font-size:") <= 1, \
            "в правиле «%s» два объявления font-size — крупное перебивается мелким" % sel
    assert ".node, .pnode, .opnode, .fnode { font-size: 12px;" in css, \
        "один и тот же шаг обязан быть одного кегля на всех сценах"


def test_step_panel_geometry_is_fixed():
    """Шесть шагов обязаны стоять на одном месте: фиксируем и шапку, и рамку."""
    css = _read("assets/strategy.css")
    assert ".step-copy { height:" in css, "высота шапки шага фиксирована"
    assert re.search(r"\.stage-card \{[^}]*height: min\(", css, re.S), "высота панели фиксирована"
    assert ".stage-card > .ui { width: 100%; height: 100%;" in css, \
        "рамка тянется на всю панель, иначе она скакала со 152 до 414px"
    assert "grid-template-columns: minmax(0, 1fr); grid-template-rows" in css, \
        "неявная колонка грида равна max-content и растягивала шаг за экран"


def test_market_squares_are_equal_height_without_aspect_ratio():
    """aspect-ratio вместе с align-self:stretch считал ШИРИНУ от высоты и
    выбрасывал карточки из ячеек на 86px."""
    css = _read("assets/strategy.css")
    assert "aspect-ratio: 1 / 0.46" not in css, "пропорции у квадратов рынка быть не должно"
    assert ".num-card { align-self: stretch; }" in css, "карточки тянутся на высоту ряда"
    assert re.search(r"\.num-card \{[^}]*min-height:", css, re.S), "высота задана min-height"


def test_grids_never_widen_past_their_column():
    """У 1fr минимум равен min-content: блок в одну строку раздвигал сетку."""
    css = _read("assets/strategy.css")
    assert "repeat(4, 1fr)" not in css and "repeat(2, 1fr)" not in css, \
        "во всех сетках нужен minmax(0, 1fr)"


def test_mobile_hero_headline_is_bigger_than_section_headings():
    """Правка владельца «побольше надо»: на мобилке nowrap зажимал заголовок
    первого экрана до размера обычных заголовков разделов."""
    css = _read("assets/strategy.css")
    blocks = [b for b in re.findall(r"@media \(max-width:1023px\) \{(.*?)\n\}", css, re.S)
              if re.search(r"\bh1 \{", b)]
    assert blocks, "нет мобильного правила для заголовка первого экрана"
    assert any("8.4vw" in b for b in blocks), \
        "кегль заголовка на мобилке считается от ширины окна"
    assert "h1 .l { white-space: normal; }" in css, "на мобилке строки переносятся"
    assert "if (!mqDesk.matches)" in _read("assets/strategy.js"), \
        "подбор кегля не должен трогать мобильный заголовок"


if __name__ == "__main__":
    import sys
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   " + name)
            except AssertionError as e:
                fails += 1
                print("FAIL " + name + ": " + str(e))
            except Exception as e:
                fails += 1
                print("ERR  " + name + ": " + type(e).__name__ + ": " + str(e))
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ" if not fails else "ПРОВАЛЕНО: %d" % fails)
    sys.exit(1 if fails else 0)
