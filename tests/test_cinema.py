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

def _scale_w(fit):
    """Ширина первого scale в цепочке — она обязана равняться ширине панели."""
    head = fit.split(",")[0]
    assert head.startswith("scale="), fit
    return int(head[len("scale="):].split(":")[0])


def test_native_portrait_scales_to_the_pane_exactly():
    """760×1000 → 821×1080: те же пропорции, только масштаб. Ни pad, ни crop —
    иначе кадр либо режется, либо получает лишние поля."""
    fit = cinema.pane_filter(760, 1000)
    assert fit == "scale=%d:%d" % (cinema.VIDEO_W, cinema.VIDEO_H), fit


def test_width_is_never_cropped():
    """КАНОН: человек входит в панель целиком по ширине. Любой исходник
    масштабируется ИМЕННО по ширине панели, боковой crop запрещён."""
    for src in ((720, 720), (760, 1000), (1080, 1920), (1920, 1080), (900, 1600)):
        fit = cinema.pane_filter(*src)
        assert _scale_w(fit) == cinema.VIDEO_W, "%s: масштаб не по ширине: %s" % (src, fit)
        for step in fit.split(","):
            if step.startswith("crop="):
                cw = int(step[len("crop="):].split(":")[0])
                assert cw == cinema.VIDEO_W, \
                    "%s: crop режет ширину (%d) — человек обрежется: %s" % (src, cw, fit)


def test_short_source_is_padded_not_stretched():
    """Квадрат 720×720 ниже панели: добираем фоном сверху/снизу, а не тянем —
    растяжение сразу видно по лицу."""
    fit = cinema.pane_filter(720, 720)
    assert "pad=" in fit and "crop=" not in fit, fit
    pad = [s for s in fit.split(",") if s.startswith("pad=")][0]
    w, h = pad[len("pad="):].split(":")[:2]
    assert (int(w), int(h)) == (cinema.VIDEO_W, cinema.VIDEO_H)
    assert cinema.BG.lstrip("#").lower() in fit.lower(), "добор не цветом фона"


def test_tall_source_is_cropped_towards_the_head():
    """Исходник выше панели — режем по высоте со сдвигом вверх: срезать стол
    безопаснее, чем макушку."""
    fit = cinema.pane_filter(1080, 1920)
    crop = [s for s in fit.split(",") if s.startswith("crop=")][0]
    w, h, x, y = [int(v) for v in crop[len("crop="):].split(":")]
    assert (w, h, x) == (cinema.VIDEO_W, cinema.VIDEO_H, 0)
    scaled_h = int(round(1920 * cinema.VIDEO_W / 1080.0)) // 2 * 2
    assert y < (scaled_h - cinema.VIDEO_H) / 2.0, "сдвиг обязан быть к голове"


# ── Тёмная палитра ────────────────────────────────────────────────────────

def test_every_color_rule_also_sets_text_fill():
    """Страница красит заголовки `-webkit-text-fill-color` с !important, и он
    перебивает `color`. Без парного правила вся колонка остаётся чёрной по
    чёрному — ровно этот дефект и был в первом прогоне."""
    css = cinema.CINEMA_CSS
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
    assert "-webkit-text-fill-color: transparent" in cinema.CINEMA_CSS


def test_background_is_one_tone_everywhere():
    """Фон подложки ffmpeg и фон слайда — один цвет: иначе на стыке колонки
    с тёмным полем видна ступенька."""
    assert cinema.BG.startswith("#") and len(cinema.BG) == 7
    assert cinema.BG in cinema.CINEMA_CSS


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


def test_viewport_matches_the_slide_column():
    """Вьюпорт съёмки = ровно колонка: иначе кадр придётся масштабировать,
    и текст поплывёт."""
    vp = cinema.viewport()
    assert vp["width"] == cinema.PANE_W and vp["height"] == cinema.H


if __name__ == "__main__":
    ok = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("PASS %s" % name)
            ok += 1
    print("\nВсе тесты режима «кино» пройдены: %d" % ok)
