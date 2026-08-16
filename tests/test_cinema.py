# -*- coding: utf-8 -*-
"""Тесты режима «кино» (tools/cinema.py): видео слева, слайд справа.

Запускается и как `python3 tests/test_cinema.py`, и через pytest. Сайт эти
тесты не трогают — режим живёт только в конвейере рендера видео.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import cinema  # noqa: E402


# ── Геометрия кадра ───────────────────────────────────────────────────────

def test_pane_fits_the_frame():
    """Панель и колонка обязаны целиком помещаться в кадр 1920×1080 и не
    перекрывать друг друга: иначе слайд заезжает на человека."""
    assert cinema.VIDEO_X + cinema.VIDEO_W <= cinema.W
    assert cinema.VIDEO_Y + cinema.VIDEO_H <= cinema.H
    assert cinema.VIDEO_Y >= 0, "панель не должна вылезать за верх кадра"
    assert cinema.VIDEO_H == cinema.H, "панель идёт во всю высоту кадра"
    assert cinema.PANE_X >= cinema.VIDEO_X + cinema.VIDEO_W - cinema.FADE, \
        "колонка слайда начинается раньше, чем растворился край видео"
    assert cinema.PANE_W == cinema.W - cinema.PANE_X


def test_fade_is_narrower_than_the_pane():
    """Растворение шире панели съело бы человека целиком."""
    assert 0 < cinema.FADE < cinema.VIDEO_W


def test_pane_sides_are_even():
    """Все стороны панели и колонки — ЧЁТНЫЕ. У yuv420p цветовые плоскости
    вдвое меньше яркостной, и нечётная сторона валит сборку: на ширине 821
    фильтр pad падал с «Padded dimensions cannot be smaller than input
    dimensions», ffmpeg не открывал кодек, файл выходил пустым."""
    for name in ("VIDEO_W", "VIDEO_H", "PANE_W", "VIDEO_X", "VIDEO_Y", "W", "H"):
        val = getattr(cinema, name)
        assert val % 2 == 0, "%s = %d — нечётное, сборка упадёт" % (name, val)


# ── Подгонка исходника: человек не режется по ширине ──────────────────────

_FORMATS = ((720, 720), (760, 1000), (1080, 1920), (1920, 1080), (900, 1600))

# Дефолт модуля = панель под портрет 760×1000. configure() правит глобальную
# геометрию, поэтому каждый тест, который её трогает, возвращает дефолт.
_DEFAULT_SRC = (760, 1000)


def _restore():
    cinema.configure(*_DEFAULT_SRC)


# ── configure(): панель под конкретный клип ───────────────────────────────

def test_configure_fits_by_height_without_cropping():
    """КАНОН владельца: «обрезать ничего не надо — берём по всей высоте».
    Вертикаль 9:16 (720×1280) обязана дать панель во всю высоту кадра одним
    масштабом: ни кропа, ни добора, ни растяжения."""
    try:
        cinema.configure(720, 1280)
        assert (cinema.VIDEO_W, cinema.VIDEO_H) == (608, 1080)
        assert cinema.pane_fill_height(720, 1280) == 0, "добор не нужен"
        g = cinema.pane_graph(720, 1280, src="1:v")
        assert g == "[1:v]scale=608:1080,setsar=1[hv]", g
        # пропорции исходника сохранены — лицо не тянется
        assert abs(608 / 1080.0 - 720 / 1280.0) < 0.005
    finally:
        _restore()


def test_configure_leaves_room_for_the_slide():
    """Панель не имеет права съесть кадр: у самого широкого исходника она
    упирается в потолок, и колонке остаётся место."""
    try:
        cinema.configure(1920, 1080)
        assert cinema.VIDEO_W <= cinema.PANE_MAX
        assert cinema.PANE_W >= cinema.W - cinema.PANE_MAX > 0
        assert cinema.PANE_X + cinema.PANE_W == cinema.W
    finally:
        _restore()


def test_masks_follow_configure():
    """Маски рисуются ПОД ТЕКУЩУЮ панель. Ловушка Python: значения по
    умолчанию в сигнатуре вычисляются при определении функции — маска
    оставалась прежнего размера после configure(), alphamerge падал на
    несовпадении сторон, и сборка не открывала кодек (файл выходил пустым)."""
    try:
        from PIL import Image
    except ImportError:                       # pragma: no cover
        print("PIL нет — пропускаю проверку масок")
        return
    import tempfile
    d = tempfile.mkdtemp()
    try:
        cinema.configure(720, 1280)
        path = os.path.join(d, "fade.png")
        cinema.fade_mask(path)
        assert Image.open(path).size == (cinema.VIDEO_W, cinema.VIDEO_H), \
            "маска растворения не следует за configure()"
        assert Image.open(path).size == (608, 1080)
    finally:
        _restore()


def test_fade_scales_with_the_pane():
    """Растворение — доля ширины панели. Фиксированные 240px на узкой панели
    608px съели бы человека вместе с плечом."""
    try:
        cinema.configure(720, 1280)
        narrow = cinema.FADE
        assert 0 < narrow < cinema.VIDEO_W / 2.0
        cinema.configure(1920, 1080)
        assert cinema.FADE > narrow, "на широкой панели растворение шире"
    finally:
        _restore()


def test_native_portrait_scales_to_the_pane_exactly():
    """760×1000 → 820×1080: те же пропорции, только масштаб. Ни добора, ни
    кропа — иначе кадр либо режется, либо получает лишние поля."""
    g = cinema.pane_graph(760, 1000, src="1:v")
    assert g == "[1:v]scale=%d:%d,setsar=1[hv]" % (cinema.VIDEO_W, cinema.VIDEO_H), g


def test_width_is_never_cropped():
    """КАНОН: человек входит в панель целиком по ширине. Кроп по ширине
    запрещён на любом исходнике — единственный crop, который допустим,
    режет ТОЛЬКО высоту (и ещё один кроп — у размытой подложки, она не
    человек, ей можно)."""
    for src in _FORMATS:
        g = cinema.pane_graph(*src, src="1:v")
        fg = g.split(";")[-2] if "boxblur" in g else g   # ветка самого кадра
        for step in fg.split(","):
            if step.startswith("crop="):
                cw = int(step[len("crop="):].split(":")[0])
                assert cw == cinema.VIDEO_W, \
                    "%s: crop режет ширину (%d) — человек обрежется: %s" % (src, cw, g)
            if step.startswith("scale="):
                sw = int(step[len("scale="):].split(":")[0])
                assert sw == cinema.VIDEO_W, \
                    "%s: масштаб не по ширине панели: %s" % (src, g)


def test_pane_always_covers_full_height():
    """Панель обязана доходить до верхнего и нижнего края кадра при ЛЮБОМ
    исходнике (замечание владельца: «видео не от края идёт»). Значит в графе
    всегда есть ступень ровно в высоту панели — либо scale, либо crop, либо
    подложка-cover под кадром."""
    for src in _FORMATS:
        g = cinema.pane_graph(*src, src="1:v")
        full = ["%d:%d" % (cinema.VIDEO_W, cinema.VIDEO_H) in step
                for step in g.replace(";", ",").split(",")]
        assert any(full), "%s: нет ступени во всю высоту панели: %s" % (src, g)


def test_short_source_is_filled_with_blur_not_bars():
    """Квадрат 720×720 ниже панели: недостающую высоту добираем РАЗМЫТОЙ
    копией кадра. Плоская заливка давала чёрные полосы сверху и снизу —
    панель переставала читаться как кадр во всю высоту."""
    g = cinema.pane_graph(720, 720, src="1:v")
    assert "boxblur" in g, "добор без размытия — вернутся полосы: %s" % g
    assert "split=2" in g, "подложка обязана быть копией того же кадра"
    assert "force_original_aspect_ratio=increase" in g, "подложка не в край"
    assert g.rstrip().endswith("[hv]"), "граф обязан отдавать метку hv: %s" % g


def test_fill_height_is_reported_only_when_filling():
    """Вызывающий должен знать высоту резкого кадра — под неё рисуется маска
    растушёвки. Когда добор не нужен, высота 0 и маска не создаётся."""
    assert cinema.pane_fill_height(760, 1000) == 0, "точное попадание"
    assert cinema.pane_fill_height(1080, 1920) == 0, "тут кроп, а не добор"
    h = cinema.pane_fill_height(720, 720)
    assert 0 < h < cinema.VIDEO_H and h % 2 == 0, h


def test_feather_mask_softens_both_edges():
    """Маска стыка: непрозрачная в середине, к верхнему и нижнему краю плавно
    в ноль. Без неё резкий кадр лежит на размытом фоне рамкой."""
    try:
        from PIL import Image
    except ImportError:                       # pragma: no cover
        print("PIL нет — пропускаю проверку маски стыка")
        return
    import tempfile
    path = os.path.join(tempfile.mkdtemp(), "feather.png")
    cinema.feather_mask(path, 40, 200, soft=50)
    px = Image.open(path).load()
    assert px[20, 100] == 255, "середина обязана быть непрозрачной"
    assert px[20, 0] <= 6 and px[20, 199] <= 6, "края обязаны уйти в ноль"
    assert px[20, 10] < px[20, 40] < px[20, 100], "спад сверху не монотонный"
    assert px[20, 189] < px[20, 159] < px[20, 100], "спад снизу не монотонный"


def test_feather_is_wired_into_the_graph():
    """Растушёвка подключается отдельным входом — и только там, где идёт
    добор: у точного попадания её нет и быть не должно."""
    g = cinema.pane_graph(720, 720, src="1:v", feather="4:v")
    assert "[4:v]alphamerge" in g, g
    assert "[4:v]" not in cinema.pane_graph(760, 1000, src="1:v", feather="4:v")


def test_tall_source_is_cropped_towards_the_head():
    """Исходник выше панели — режем по высоте со сдвигом вверх: срезать стол
    безопаснее, чем макушку."""
    g = cinema.pane_graph(1080, 1920, src="1:v")
    crop = [s for s in g.split(",") if s.startswith("crop=")][0]
    w, h, x, y = [int(v) for v in crop[len("crop="):].split(":")]
    assert (w, h, x) == (cinema.VIDEO_W, cinema.VIDEO_H, 0)
    scaled_h = int(round(1920 * cinema.VIDEO_W / 1080.0)) // 2 * 2
    assert y < (scaled_h - cinema.VIDEO_H) / 2.0, "сдвиг обязан быть к голове"


# ── Тёмная палитра ────────────────────────────────────────────────────────

def test_every_color_rule_also_sets_text_fill():
    """Страница красит заголовки `-webkit-text-fill-color` с !important, и он
    перебивает `color`. Без парного правила вся колонка остаётся чёрной по
    чёрному — ровно этот дефект и был в первом прогоне."""
    css = cinema.css()
    blocks = [b for b in css.split("}") if "color:" in b]
    for b in blocks:
        if "background" in b and "color:" not in b.replace("background-color:", ""):
            continue
        has_color = any(line.strip().startswith("color:")
                        for line in b.split(";"))
        if has_color:
            assert "-webkit-text-fill-color" in b, \
                "правило красит color без text-fill:\n%s" % b.strip()


def test_gradient_headings_keep_transparent_fill():
    """Акцент в заголовке рисуется градиентом через background-clip:text —
    заливка обязана остаться прозрачной, иначе градиент закрашивается."""
    assert "-webkit-text-fill-color: transparent" in cinema.css()


def test_slide_frame_is_transparent():
    """Кадр слайда снимается ПРОЗРАЧНЫМ и кладётся поверх видео — только так
    эмодзи FX вылетают из колонки на человека (правка владельца). Любая
    заливка в этом стиле закрыла бы видео целиком; фон рисует ffmpeg."""
    css = cinema.css()
    assert "background: transparent" in css, css[:400]
    assert cinema.BG not in css, "заливка фона вернулась — видео закроется"
    assert cinema.BG.startswith("#") and len(cinema.BG) == 7


def test_slide_frame_goes_over_the_video():
    """Порядок сборки: подложка → видео → кадр слайда. Если поменять местами,
    видео снова перекроет эмодзи."""
    f = cinema.overlay_filter(bg_stream="0:v", clip_stream="2:v",
                              mask_stream="3:v", pane_stream="1:v")
    steps = f.split(";")
    video_at = next(i for i, s in enumerate(steps) if "[pane]overlay" in s)
    slide_at = next(i for i, s in enumerate(steps) if "[1:v]overlay" in s)
    assert video_at < slide_at, "кадр слайда обязан ложиться ПОВЕРХ видео: %s" % f
    assert steps[slide_at].startswith("[base][1:v]overlay=0:0"), \
        "кадр слайда кладётся на весь кадр, а не в колонку: %s" % f


def test_column_offset_follows_the_pane():
    """Отступ колонки в стиле считается из текущей панели: зашитый на импорте
    увёл бы контент не туда после configure()."""
    try:
        cinema.configure(720, 1280)
        assert "padding-left: %dpx" % cinema.PANE_X in cinema.css()
        assert "padding-left: 608px" in cinema.css()
    finally:
        _restore()


# ── Маска растворения ─────────────────────────────────────────────────────

def test_fade_mask_goes_from_opaque_to_clear():
    """Маска: слева непрозрачно, справа ноль, между ними монотонный спад."""
    try:
        from PIL import Image
    except ImportError:                       # pragma: no cover
        print("PIL нет — пропускаю проверку маски")
        return
    import tempfile
    path = os.path.join(tempfile.mkdtemp(), "mask.png")
    cinema.fade_mask(path, w=200, h=10, fade=80)
    px = Image.open(path).load()
    assert px[0, 5] == 255, "левый край обязан быть непрозрачным"
    assert px[199, 5] <= 2, "правый край обязан раствориться в ноль"
    prev = 255
    for x in range(200):
        assert px[x, 5] <= prev, "спад маски не монотонный на x=%d" % x
        prev = px[x, 5]


def test_viewport_covers_the_whole_frame():
    """Вьюпорт съёмки — ВЕСЬ кадр, а не колонка: эмодзи FX должны иметь право
    вылететь из колонки на видео, а нарисовать их можно только внутри снятой
    области. В колонку контент ставит GROW_JS."""
    vp = cinema.viewport()
    assert (vp["width"], vp["height"]) == (cinema.W, cinema.H)
    assert vp["width"] > cinema.PANE_W, "иначе эмодзи упрутся в край колонки"


def test_emoji_reach_lands_on_the_video_but_stays_in_frame():
    """Разлёт эмодзи (burst() в animate_slide.py) считается формулой, поэтому
    дальность вылета проверяема без браузера. Держим её в вилке: короче
    растворения — значок гаснет, не долетев до человека; длиннее ширины видео
    — улетает за левый край кадра."""
    src = open(os.path.join(_ROOT, "tools", "animate_slide.py"),
               encoding="utf-8").read()
    bdur = float(src.split("var BDUR = ")[1].split(";")[0])
    # sp = (260 + (j*37)%120) * SPREAD  →  максимум базы 379
    # dist = sp * dur * 0.42 при q → 1;  по горизонтали cos(0.15π) = 0.891
    reach = 0.891 * (260 + 119) * cinema.SPREAD * bdur * 0.42
    assert reach > cinema.FADE, \
        "разлёт %.0f px не выходит за растворение %d px — эмодзи не долетают " \
        "до видео" % (reach, cinema.FADE)
    assert reach < cinema.VIDEO_W, \
        "разлёт %.0f px шире панели %d px — значки уходят за край кадра" \
        % (reach, cinema.VIDEO_W)


# ── Сборка ────────────────────────────────────────────────────────────────

def _cinema_compose_source():
    """Кусок animate_slide.main() со сборкой «кино» — от `if args.cinema:` до
    `return`. Сама команда строится инлайном, импортировать нечего, поэтому
    сторожим её текстом."""
    src = open(os.path.join(_ROOT, "tools", "animate_slide.py"),
               encoding="utf-8").read()
    head = src.index("    if args.cinema:\n")
    return src[head:src.index("\n        return\n", head)]


def test_cinema_output_is_capped_by_the_slide_length():
    """Подложка идёт «-loop 1» (бесконечна), поэтому -shortest меряет длину по
    звуку клипа. Без явного -t слайд на 49 с превращался в 2:45 замершей
    картинки под продолжающуюся речь."""
    body = _cinema_compose_source()
    assert '"-t", "%.3f" % secs' in body, \
        "в сборке «кино» нет ограничения длительности:\n%s" % body
    assert body.index('"-t", "%.3f" % secs') < body.index('"-shortest"'), \
        "-t обязан идти как опция ВЫХОДА, до -shortest"


def test_head_stub_replaces_the_picture_but_not_the_sound():
    """Заглушка головы — это ТОЛЬКО картинка панели. Звук, длительность и
    тайминги слов обязаны остаться от родного клипа слайда: реплики FX
    расставлены по его словам, и чужая дорожка рассинхронит весь слайд."""
    src = open(os.path.join(_ROOT, "tools", "animate_slide.py"),
               encoding="utf-8").read()
    assert "--head-stub" in src
    # звук всегда со входа 2 — это клип слайда, его порядковый номер не плавает
    body = _cinema_compose_source()
    assert '["-i", clip],' in body, "клип слайда должен быть входом №2"
    assert body.index('["-i", clip],') < body.index('["-i", mask]'), \
        "клип обязан идти до маски, иначе -map 2:a? возьмёт не ту дорожку"
    assert '"-map", "2:a?"' in body, "звук берётся не с клипа слайда"
    # а картинку панели рисуем из pic, который при заглушке смотрит на неё
    assert 'if args.head_stub:' in body and 'ins.append(["-i", args.head_stub])' in body
    assert "src=pic" in body and "clip_stream=pic" in body, \
        "панель по-прежнему собирается из клипа, а не из заглушки"


def test_head_stub_drives_the_geometry():
    """Ширину панели считаем по тому, что РЕАЛЬНО видно: при заглушке — по
    её сторонам. Иначе колонка слайда встанет под размер чужого файла."""
    src = open(os.path.join(_ROOT, "tools", "animate_slide.py"),
               encoding="utf-8").read()
    assert "head_pic = args.head_stub or clip" in src
    assert "cinema_fx.probe_size(ff, head_pic)" in src
    assert "cinema_fx.probe_size(ff, clip)" not in src, \
        "где-то геометрия всё ещё считается по клипу, а не по картинке панели"


def test_cinema_inputs_are_numbered_by_the_list():
    """Входы ffmpeg нумеруются позицией. Маска растушёвки и заглушка
    появляются по обстоятельствам, поэтому индексы обязаны считаться от
    длины списка — руками написанный «4:v» молча склеит не те потоки."""
    body = _cinema_compose_source()
    assert '"%d:v" % (len(ins) - 1)' in body, "индексы входов зашиты числом"
    assert '= "4:v"' not in body


def test_reuse_frames_does_not_wipe_the_frames():
    """--reuse-frames существует ради правок сборки без четверти часа съёмки.
    Если чистка каталога останется безусловной, флаг сотрёт то, что переиспользует."""
    src = open(os.path.join(_ROOT, "tools", "animate_slide.py"),
               encoding="utf-8").read()
    wipe = src.index("os.remove(os.path.join(frames_dir, old))")
    guard = src.index("if args.reuse_frames:")
    assert guard < wipe, "чистка кадров не под флагом"
    assert "--reuse-frames" in src


if __name__ == "__main__":
    ok = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("PASS %s" % name)
            ok += 1
    print("\nВсе тесты режима «кино» пройдены: %d" % ok)
