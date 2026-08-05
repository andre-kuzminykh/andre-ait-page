# -*- coding: utf-8 -*-
"""Тесты графики поверх видео-приветствия курса (FR-SITE30, SPEC-SITE.md).
Без зависимостей — запускается и как `python3 tests/test_welcome.py`, и через pytest.

Второй ролик по тем же постоянным правилам, что и лекция 1 (FR-SITE27), но с
одним новым свойством: слова субтитров лежат отдельным файлом и правятся без
перерендера слоя. Проверяем то, что ломается молча: внешние зависимости,
расхождение подписей с деком, рассинхрон таймингов и разрыв связи
«страница — субтитры.srt — собрать.sh».
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIR = os.path.join(_ROOT, "automation_ru", "overlay")
_PAGE = os.path.join(_DIR, "index.html")
_DECK = os.path.join(_ROOT, "automation_ru", "index.html")
_SRT = os.path.join(_DIR, "субтитры.srt")
_DURATION = 59.1           # 00:59 — длина ролика
_WORDS = 121               # столько слов в сценарии владельца
_POSTERS_TOP = 638         # верх рамок картин на стене


def _html(path=_PAGE):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _scenes():
    """[(id, in, out, [времена элементов])] по разметке сцен."""
    html, out = _html(), []
    for m in re.finditer(
            r'<section class="scene" id="(\w+)" data-in="([\d.]+)" data-out="([\d.]+)">',
            html):
        end = html.index("</section>", m.end())
        cues = [float(c) for c in re.findall(r'data-in="([\d.]+)"', html[m.end():end])]
        out.append((m.group(1), float(m.group(2)), float(m.group(3)), cues))
    return out


def _labels():
    """Подписи элементов, как их видит зритель (<br> — это пробел)."""
    html = _html()
    body = html[html.index('<div id="layer">'):html.index('<div id="cover">')]
    out = []
    for raw in re.findall(r'<p class="label">(.*?)</p>', body, re.S):
        txt = re.sub(r"<br\s*/?>", " ", raw)
        out.append(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", txt)).strip())
    return out


def _cues():
    """[(начало, конец, текст)] из субтитры.srt."""
    with open(_SRT, encoding="utf-8") as f:
        text = f.read().replace("\r", "")
    out = []
    for block in re.split(r"\n\n+", text):
        m = re.search(r"(\d\d):(\d\d):(\d\d),(\d\d\d)\s*-->\s*(\d\d):(\d\d):(\d\d),(\d\d\d)", block)
        if not m:
            continue
        lines = block.split("\n")
        body = " ".join(lines[lines.index(m.group(0)) + 1:]).strip() if m.group(0) in lines \
            else " ".join(l for l in lines if "-->" not in l and not l.strip().isdigit()).strip()
        a = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1000.0
        b = int(m.group(5)) * 3600 + int(m.group(6)) * 60 + int(m.group(7)) + int(m.group(8)) / 1000.0
        out.append((a, b, body))
    return out


# ── FR-SITE30: страница самодостаточна ───────────────────────────────────

def test_page_is_self_contained():
    """В записи и офлайн страница обязана выглядеть так же, как на сайте."""
    html = _html()
    external = re.findall(r'(?:src|href)="(https?:)?//[^"]+"', html)
    assert not external, "страница тянет внешние ресурсы: %r" % external
    assert "fonts.googleapis" not in html and "cdnjs" not in html, "остался внешний шрифт или CDN иконок"
    for f in re.findall(r"url\((fonts/[^)]+\.woff2)\)", html):
        assert os.path.exists(os.path.join(_DIR, f)), "нет файла шрифта: %s" % f
    assert os.path.exists(os.path.join(_DIR, "icons.js")), "нет набора иконок"


def test_font_matches_the_deck():
    """Дек курса набран JetBrains Mono — графика поверх видео обязана совпадать
    с ним, иначе кадр и страница курса выглядят как из разных проектов."""
    assert "JetBrains+Mono" in _html(_DECK), "дек больше не на JetBrains Mono — проверьте пару"
    assert "'JetBrains Mono'" in _html(), "страница набрана не тем шрифтом, что дек"


def test_icons_come_from_the_deck_set():
    """Иконки берутся из того же набора и той же версии, что в деке: в FA 7
    часть глифов перерисована, и кадр разошёлся бы с картинкой курса."""
    icons = _html(os.path.join(_DIR, "icons.js"))
    assert "6.4.0" in icons, "версия Font Awesome не зафиксирована"
    used = set(re.findall(r'data-icon="([\w-]+)"', _html()))
    assert used, "в разметке нет ни одной иконки"
    for name in used:
        assert ("'%s'" % name) in icons or re.search(r"\b%s\s*:" % re.escape(name), icons), \
            "иконки нет в наборе: %s" % name


# ── FR-SITE30: тайминги ──────────────────────────────────────────────────

def test_scenes_do_not_overlap():
    scenes = _scenes()
    assert len(scenes) >= 5, "сцен подозрительно мало: %d" % len(scenes)
    prev = 0.0
    for sid, tin, tout, _ in scenes:
        assert tin < tout, "%s: окно вывернуто" % sid
        assert tin >= prev, "%s начинается раньше, чем кончилась предыдущая сцена" % sid
        prev = tout
    assert prev <= _DURATION, "последняя сцена выходит за длину ролика"


def test_cues_are_within_scenes():
    for sid, tin, tout, cues in _scenes():
        for c in cues:
            assert tin <= c <= tout, "%s: элемент на %.1f вне окна сцены %.1f–%.1f" % (sid, c, tin, tout)


# ── FR-SITE30: тексты из дека, своего не досочиняем ──────────────────────

# Слова, продиктованные владельцем при пересборке раскладки («Сначала так…»):
# «Управление изменениями», «ИИ-агент в реальном бизнес-процессе», «Рутина»,
# «Создание будущего», «Новая экономика», «AI-First процессах». В деке их нет,
# но это прямые формулировки владельца — как «Цифровизация» в лекции 1.
_OWNER_WORDING = {
    "управление", "изменениями", "реальном", "рутина",
    "создание", "новая", "экономика", "процессах",
    # «будущего» — это дековское «проектировать будущую», просто падеж меняет
    # больше двух последних букв, и грубый стем его не ловит.
    "будущего",
}


def test_labels_come_from_the_deck():
    """Подписи сокращены до сути; каждое значимое слово — из дека или из
    прямой формулировки владельца. Всё остальное — досочинённое обещание,
    которого нет на странице курса."""
    deck = re.sub(r"\s+", " ", _html(_DECK).replace("&nbsp;", " ").replace("&shy;", "")).lower()
    skip = {"и", "в", "по", "как", "первого", "с"}     # служебные слова
    for label in _labels():
        for word in re.findall(r"[\w-]+", label):
            if word.lower() in skip or len(word) < 3 or word.lower() in _OWNER_WORDING:
                continue
            stem = (word[:-2] if len(word) > 6 else word).lower()   # падежи не считаем
            assert stem in deck, "слова нет в деке, значит подпись досочинена: %r (из %r)" % (word, label)
    assert len(_labels()) >= 12, "проверено подозрительно мало подписей (%d)" % len(_labels())


def test_finale_animations_are_in_place():
    """Владелец просил три особых финала: дизлайк «выходит» у «Рутины», лайк —
    у «Создания будущего», за «Новой экономикой» дышит фиолетовое сияние."""
    html = _html()
    assert "@keyframes thumbDown" in html, "нет анимации дизлайка"
    assert "@keyframes thumbUp" in html, "нет анимации лайка"
    assert 'data-icon="thumbs-down"' in html and 'data-icon="thumbs-up"' in html, \
        "нет пальцев у «Рутины» и «Создания будущего»"
    assert "glowPulse" in html and "infinite" in html[html.index("glowPulse"):], \
        "сияние за «Новой экономикой» не дышит"
    assert "136,84,243" in html, "сияние не фирменным фиолетовым (#8854F3)"


def test_no_headings_in_frame():
    """Правило 2: заголовки экранов в кадр не идут."""
    html = _html()
    layer = html[html.index('<div id="layer">'):html.index('<div id="cover">')]
    layer = re.sub(r"<!--.*?-->", " ", layer, flags=re.S)   # комментарии в кадр не попадают
    assert "<h1" not in layer and "<h2" not in layer and "<h3" not in layer, "в кадре заголовок"
    for heading in ("Для кого", "Чему вы", "Добро пожаловать на курс"):
        assert heading not in layer, "заголовок дека попал в кадр: %r" % heading


def test_no_rectangular_blocks():
    """Правило 1: круг — единственная допустимая оправа."""
    html = _html()
    css = html[html.index("<style>"):html.index("</style>")]
    scene_css = css[css.index("/* ── Ряды."):css.index("/* ── Обложка")]
    for radius in re.findall(r"border-radius:([^;}]+)", scene_css):
        assert "50%" in radius, "в сценах не круглая оправа: border-radius:%s" % radius


def test_no_small_print():
    """Правило 3: только крупный текст. 24px при ширине кадра 1080 — это ~9px
    на телефоне, меньше нельзя."""
    css = _html()
    css = css[css.index("/* ── Ряды."):css.index("/* ── Обложка")]
    sizes = [float(x) for x in re.findall(r"\.label\{font-size:([\d.]+)px", css)]
    sizes += [float(x) for x in re.findall(r"#s\d \.label\{font-size:([\d.]+)px", css)]
    assert sizes, "не нашёл ни одного кегля подписей"
    assert min(sizes) >= 24, "подпись мельче 24px: %s" % sorted(sizes)[:3]


def test_no_hyphenation_at_all():
    """Правило 5: слова не переносятся."""
    html = _html()
    assert "&shy;" not in html, "остался мягкий перенос"
    flat = html.replace(" ", "")
    assert "overflow-wrap:anywhere" not in flat, "anywhere рвёт слово посреди слога"
    assert "hyphens:auto" not in flat, "автоперенос запрещён"


def test_zone_stays_above_the_posters():
    """Правило 6: графика не доходит до картин на стене."""
    html = _html()
    top = int(re.search(r"--zone-top:(\d+)px", html).group(1))
    height = int(re.search(r"--zone-h:(\d+)px", html).group(1))
    assert top + height <= _POSTERS_TOP, \
        "зона графики (%d..%d) заходит на картины (y%d)" % (top, top + height, _POSTERS_TOP)


# ── FR-SITE30: субтитры правятся без перерендера ─────────────────────────

def test_subtitles_live_in_one_editable_file():
    """Владелец просил «чтобы можно было какие-то слова поправить». Значит
    слова лежат в ОДНОМ файле, и его же читают и превью, и сборка. Копия
    внутри страницы означала бы, что правка расходится с тем, что видно."""
    assert os.path.exists(_SRT), "нет файла субтитров"
    html = _html()
    assert "субтитры.srt" in html, "страница не читает файл субтитров"
    assert "var SUBS = [];" in html, "в странице осталась своя копия слов — она разойдётся с файлом"
    script = html[html.index("function joinScript()"):html.index("var joinBtn")]
    assert "субтитры.srt" in script, "сборка вжигает не тот файл, который правит владелец"


def test_layer_has_no_subtitles_in_it():
    """Субтитров в слое нет намеренно: иначе правка слова требовала бы
    перерендера всех 1773 кадров."""
    html = _html()
    script = html[html.index("function joinScript()"):html.index("var joinBtn")]
    assert "subtitles=" in script, "субтитры не вжигаются при сборке"
    assert "fontsdir" in script, "libass не найдёт шрифт: субтитры выйдут системным"
    # Имя обязано быть ПОЛНЫМ: по семейному «JetBrains Mono» libass шрифт не
    # находит и молча уходит в системный — кадр с ним побайтово совпал с кадром,
    # где указан заведомо несуществующий шрифт.
    assert "JetBrains Mono ExtraBold" in script, \
        "в стиле не полное имя шрифта — субтитры выйдут системным, и молча"
    assert os.path.exists(os.path.join(_DIR, "fonts", "JetBrainsMono-ExtraBold.ttf")), \
        "нет ttf для вжигания: woff2 libass не понимает"


def test_style_is_applied_through_ass_not_force_style():
    """force_style здесь не работает: запятые внутри стиля ffmpeg считает
    своими разделителями, и субтитр молча не рисуется — кадр остаётся чистым,
    без единой ошибки в логе. Поэтому SRT переводится в ASS и правится стиль."""
    html = _html()
    script = html[html.index("function joinScript()"):html.index("var joinBtn")]
    assert "force_style=" not in script, "через force_style субтитры молча не отрисуются"
    assert "raw.ass" in script and "subs.ass" in script, "нет перевода SRT в ASS"
    assert "subtitles=filename=" in script, \
        "ffmpeg 8 (brew на маке) не разбирает короткую форму subtitles=файл — нужен явный ключ"
    assert "PlayResX" in script and "PlayResY" in script, \
        "ffmpeg пишет ASS в координатах 384x288 — без подмены кегль и отступ будут не те"


def test_subs_follow_the_transcript():
    cues = _cues()
    assert len(cues) >= 30, "реплик подозрительно мало: %d" % len(cues)
    prev_end = 0.0
    words = 0
    for a, b, text in cues:
        assert a < b, "вывернутая реплика: %r" % text
        assert a >= prev_end - 0.001, "реплики наезжают друг на друга: %r" % text
        assert b <= _DURATION + 0.1, "реплика выходит за длину ролика: %r" % text
        assert "[" not in text and "]" not in text, "ремарка в квадратных скобках в кадре: %r" % text
        assert "TurboScribe" not in text, "водяной знак распознавалки в кадре"
        n = len(text.split())
        assert 1 <= n <= 4, "в реплике %d слов (можно 2–4): %r" % (n, text)
        words += n
        prev_end = b
    assert words == _WORDS, "слов в субтитрах %d, а в сценарии %d" % (words, _WORDS)


def test_subs_are_white_outlined_and_boxless():
    """Правило 7 и вид субтитров: белые, тонкая чёрная обводка, без подложки."""
    html = _html()
    css = html[html.index("#sub{"):html.index("}", html.index("#sub{"))]
    assert "color:#fff" in css.replace(" ", ""), "субтитры не белые"
    assert "-webkit-text-stroke" in html, "нет обводки"
    assert "paint-order:stroke fill" in html.replace("  ", " "), \
        "без paint-order обводка съедает половину буквы изнутри"


# ── FR-SITE30: слой и сборка ─────────────────────────────────────────────

def test_rendered_layer_is_present_and_split():
    for name in ("overlay_c.mp4", "overlay_a.mp4"):
        path = os.path.join(_DIR, name)
        assert os.path.exists(path), "нет слоя: %s" % name
        assert os.path.getsize(path) > 100000, "слой подозрительно пустой: %s" % name


def test_page_can_be_rendered_frame_by_frame():
    html = _html()
    assert "window.__renderAt" in html, "нет покадрового рендера — слой нечем собрать"
    assert "an.currentTime" in html, "время анимаций не выставляется явно — появления размажутся"
    assert "documentElement.style.background = 'transparent'" in html, \
        "фон <html> не снят: снимки выйдут непрозрачными"


def test_script_burns_the_layer_into_the_frame():
    html = _html()
    script = html[html.index("function joinScript()"):html.index("var joinBtn")]
    assert "alphamerge" in script, "слой не сшивается из цвета и маски"
    assert "eof_action=pass" in script, "слой обязан отпускать картинку, а не резать её"
    assert "$ROT" in script, "поворот кадра не учитывается"
    assert "videotoolbox" in script, "на маке пересборка должна идти аппаратно"
    assert "-f null" in script, "результат не проверяется декодированием"
    assert "setpts=PTS-STARTPTS" in script, "дорожки ролика не прижаты к нулю — будет чёрный кадр"


def test_brand_chrome_is_in_place():
    """Владелец: «сверху слева AIT и АКАДЕМИЯ ДАТАИСТА, а чуть ниже уже все
    эти иконки». Геометрия — 1:1 с хромом рилсов Академии: шапка top 128 /
    высота 96, лого 92px при left 56, тег 26px/700 с разрядкой .3em.
    Зона графики обязана начинаться НИЖЕ шапки (224), иначе иконки лезут
    под лого."""
    html = _html()
    assert 'id="chrome"' in html, "нет фирменной шапки"
    assert "АКАДЕМИЯ ДАТАИСТА" in html, "нет тега «АКАДЕМИЯ ДАТАИСТА»"
    assert 'src="logo.png"' in html, "лого не подключено"
    assert os.path.exists(os.path.join(_DIR, "logo.png")), "нет файла logo.png рядом со страницей"
    chrome = html[html.index("#chrome{"):html.index("#chrome .tag")]
    assert "top:128px" in chrome and "height:96px" in chrome and "left:56px" in chrome, \
        "геометрия шапки разошлась с хромом рилсов (top 128 / height 96 / left 56)"
    assert "height:92px" in html[html.index("#chrome img"):html.index("#chrome .tag")], \
        "лого не 92px"
    tag = html[html.index("#chrome .tag"):html.index("}", html.index("#chrome .tag"))]
    assert "font-size:26px" in tag and ".3em" in tag and "uppercase" in tag, \
        "тег разошёлся со стилем рилсов (26px / .3em / капс)"
    zone_top = int(re.search(r"--zone-top:(\d+)px", html).group(1))
    assert zone_top >= 224 + 20, "зона графики залезает под шапку (top %d)" % zone_top
    assert "body.on-cover #chrome" in html, "на обложке шапка обязана прятаться"


def test_layer_end_does_not_cut_the_clip():
    """Со shortest=1 ролик ДЛИННЕЕ слоя обрезался по слою: замер — 70-секундный
    дубль выходил 59.12 с видео при 70 с звука, то есть 11 секунд черноты под
    звук. eof_action=pass: слой кончился — картинка идёт дальше."""
    html = _html()
    script = html[html.index("function joinScript()"):html.index("var joinBtn")]
    assert "eof_action=pass" in script, "слой обрежет ролик, который длиннее его"
    assert "overlay=0:0:format=auto:shortest=1" not in script, \
        "в самом фильтре остался shortest=1 — он режет дубль длиннее слоя"


def test_audio_is_copied_when_it_can_be():
    """Владелец: «звук шипит… в оригинале всё ок». Дорожка НИКОГДА не
    пережимается (кроме не-AAC — их в mp4 копией не положить): идёт копией
    отдельным входом, а смещение дорожек исходника (edit list в MOV)
    воспроизводится контейнером — itsoffset при положительном сдвиге, срез
    начала при отрицательном. Синхрон проверен корреляцией: 0 мс."""
    html = _html()
    script = html[html.index("function joinScript()"):html.index("var joinBtn")]
    assert '-c:a copy' in script, "звук всегда пережимается — это и слышно"
    assert "-map 3:a:0" in script, "звук берётся не отдельным входом со сдвигом"
    assert "stream=start_time" in script, "смещение дорожек не замеряется"
    assert '-itsoffset' in script and '-ss ${OFF#-}' in script, \
        "смещение не воспроизводится контейнером (itsoffset / срез начала)"
    assert "aresample=async" not in script, \
        "звук растягивается под склейку — это и слышалось как искажение"
    assert "aac_at" in script, "для не-AAC дорожек не взят лучший кодировщик"
    assert "-b:a 192k" not in script, "остался пережим 192k"


def test_script_picks_a_capable_ffmpeg():
    """У владельца в терминале активна conda, и её урезанный ffmpeg затеняет
    brew-шный: «No such filter: 'subtitles'». Команда ffmpeg не берётся на
    веру — скрипт перебирает кандидатов (PATH, /opt/homebrew, /usr/local) и
    берёт первого, у кого реально есть фильтр subtitles; иначе говорит
    словами, что поставить."""
    html = _html()
    script = html[html.index("function joinScript()"):html.index("var joinBtn")]
    assert '/opt/homebrew/bin/ffmpeg' in script, "brew-путь не пробуется мимо PATH"
    assert 'grep -q " subtitles "' in script, "кандидат не проверяется на фильтр subtitles"
    assert 'brew install ffmpeg' in script, "нет понятного отказа без libass"
    assert re.search(r"'p\(\)  \{ \"\$FP\"", script) or '"$FP" -v error' in script, \
        "пробы идут не через выбранный ffprobe"
    assert "ffmpeg -y -loglevel" not in script, "остался вызов ffmpeg мимо селектора"


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   %s" % name)
            except Exception as e:
                failed += 1
                print("FAIL %s: %s: %s" % (name, type(e).__name__, e))
    raise SystemExit(1 if failed else 0)
