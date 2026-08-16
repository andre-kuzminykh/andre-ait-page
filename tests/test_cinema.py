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
    assert cinema.PANE_X >= cinema.VIDEO_X + cinema.VIDEO_W - cinema.FADE, \
        "колонка слайда начинается раньше, чем растворился край видео"
    assert cinema.PANE_W == cinema.W - cinema.PANE_X


def test_fade_is_narrower_than_the_pane():
    """Растворение шире панели съело бы человека целиком."""
    assert 0 < cinema.FADE < cinema.VIDEO_W


# ── Кроп исходника ────────────────────────────────────────────────────────

def test_native_portrait_needs_no_crop():
    """Клип ровно по размеру панели идёт пиксель в пиксель — без кропа."""
    assert cinema.crop_for(cinema.VIDEO_W, cinema.VIDEO_H) is None


def test_square_source_is_cropped_to_the_pane():
    """Квадрат 720×720 (запись под кружок) режется по бокам, а не растягивается:
    растяжение делает лицо шире, и это видно сразу."""
    crop = cinema.crop_for(720, 720)
    assert crop, "квадрат обязан кропаться"
    w, h, x, y = [int(v) for v in crop.split(":")]
    assert h == 720 and y == 0, "по высоте квадрат уже подходит"
    assert abs(w / float(h) - cinema.VIDEO_W / float(cinema.VIDEO_H)) < 0.02
    assert 0 <= x <= 720 - w


def test_crop_survives_a_taller_source():
    """Исходник уже панели — режем верх/низ, ширину не трогаем."""
    crop = cinema.crop_for(600, 1200)
    w, h, x, y = [int(v) for v in crop.split(":")]
    assert w == 600 and x == 0 and h <= 1200 and y >= 0


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
