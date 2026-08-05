# -*- coding: utf-8 -*-
"""Тесты сжатия видео для веба (FR-SITE29, SPEC-SITE.md).
Без зависимостей — запускается и как `python3 tests/test_compress.py`, и через pytest.

Скрипт должен делать файлы минимум в 10 раз легче и при этом не портить то, что
уже лёгкое. Проверяем то, что ломается молча: способ задания размера, защиты и
флаги, без которых ролик на сайте стартует медленно.
"""
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SH = os.path.join(_ROOT, "automation", "compress", "сжать.sh")


def _body():
    with open(_SH, encoding="utf-8") as f:
        return f.read()


# ── FR-SITE29: размер задаётся кратностью, а не только качеством ─────────

def test_size_is_driven_by_ratio_not_crf_alone():
    """Владелец просил «сжать более чем в 10 раз». Один CRF этого не даёт: он
    держит качество, а не размер, и на тяжёлом материале выходило 7-8 раз.
    Потолок битрейта считается от битрейта исходника."""
    b = _body()
    assert "RATIO=" in b, "кратность сжатия не задана"
    assert "-v b=\"$IN_KBPS\" -v r=\"$RATIO\"" in b, \
        "потолок не считается от битрейта исходника — кратность не гарантирована"
    assert "-maxrate" in b and "-bufsize" in b, "потолок битрейта не выставляется"
    assert "-crf" in b, "нет пола качества: лёгкий материал раздуется до потолка"
    assert "if(v<lo) v=lo; if(v>hi) v=hi" in b, \
        "потолок не ограничен снизу и сверху — на краях выйдет каша или раздутый файл"


def test_three_modes_differ():
    b = _body()
    for word in ("сильнее", "качество"):
        assert word in b, "нет режима «%s»" % word
    assert "SHORT=540" in b and "SHORT=720" in b and "SHORT=1080" in b, \
        "режимы не отличаются разрешением"


# ── FR-SITE29: не сделать хуже ───────────────────────────────────────────

def test_light_files_are_left_alone():
    """Сжимать то, что уже лёгкое, — только терять качество: размер не изменится."""
    b = _body()
    assert "SKIPK=" in b, "нет порога «уже лёгкий»"
    assert "уже лёгкий" in b, "пропуск не объясняется человеку"


def test_originals_are_never_overwritten():
    b = _body()
    assert 'OUTDIR="сжатые"' in b, "результаты не отделены от оригиналов"
    assert 'case "$f" in "$OUTDIR"/*) continue ;; esac' in b, \
        "скрипт сожмёт собственные результаты на втором запуске"


def test_result_is_verified_by_decoding():
    """Тот же урок, что в сборке и нарезке: файл нужного размера может не играть."""
    b = _body()
    assert "-f null" in b, "результат не проверяется декодированием"
    assert "command -v ffmpeg" in b, "скрипт должен сам сообщать о зависимостях"


# ── FR-SITE29: быстро открывается с мобильного ───────────────────────────

def test_flags_for_fast_start_on_mobile():
    """Ради этого всё и затевалось: ролик должен начинать играть сразу."""
    b = _body()
    assert "+faststart" in b, \
        "без faststart браузер ждёт закачки целиком до первого кадра"
    assert "-g 60" in b, "не задан интервал ключевых кадров — перемотка задумается"
    assert "-pix_fmt yuv420p" in b or "format=yuv420p" in b, \
        "без yuv420p часть устройств не покажет видео"
    assert "-profile:v high" in b, "профиль не задан"


def test_phone_footage_quirks_are_handled():
    """Съёмка с телефона: метка поворота и HDR."""
    b = _body()
    assert "$ROT" in b and "90|-90|270|-270" in b, "поворот кадра не учитывается"
    assert "tonemap" in b, "HDR не приводится к обычному цвету — картинка выцветет"
    assert "HAVE_ZSCALE" in b, \
        "тонемап применяется вслепую: в сборке без zscale команда упадёт"


def test_no_stream_copy():
    """Сжатие копированием дорожки не делается — это всегда перекодирование."""
    b = _body()
    assert "-c copy" not in b, "копированием дорожки ничего не сожмёшь"


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
