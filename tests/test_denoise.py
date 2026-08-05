# -*- coding: utf-8 -*-
"""Тесты чистки шипения в звуке (FR-SITE31, SPEC-SITE.md).
Без зависимостей — запускается и как `python3 tests/test_denoise.py`, и через pytest.

Владелец: «что-то звук шипит». Замер показал, что сборка не виновата (после её
AAC 192k шумовой пол не поднимается), шипение — в самой дорожке. Скрипт чистит
звук, не трогая картинку. Проверяем то, что ломается молча: перекодирование
видео вместо копии, потерю метки поворота, немой отказ без afftdn.
"""
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SH = os.path.join(_ROOT, "automation", "compress", "шумодав.sh")


def _body():
    with open(_SH, encoding="utf-8") as f:
        return f.read()


def test_video_is_copied_not_reencoded():
    """Смысл скрипта — чистить звук БЕЗ потери картинки: видеодорожка копией.
    Проверено прогоном: md5 видеодорожки до и после совпадают байт-в-байт."""
    b = _body()
    assert "-c:v copy" in b, "видео перекодируется — потеря качества на ровном месте"
    assert "-map 0:v:0" in b and "-map 0:a:0" in b, \
        "дорожки не выбраны явно — при нескольких дорожках уедет не та"


def test_denoise_chain_is_sane():
    """highpass снимает гул ниже голоса, afftdn — шипение. Сила задаётся
    ступенями: замерено −11/−19/−26 дБ шумового пола при речи, тронутой
    меньше чем на дБ."""
    b = _body()
    assert "highpass=f=70" in b, "нет среза гула ниже голоса"
    assert "afftdn=nr=$NR" in b, "нет шумодава"
    assert "NR=12" in b and "NR=20" in b and "NR=30" in b, "нет трёх ступеней силы"
    assert "средне" in b and "сильно" in b, "ступени не названы по-русски"


def test_measures_floor_before_and_after():
    """Решение «чисто или ещё шипит» должно опираться на замер, а не на глаз:
    скрипт печатает шумовой пол до и после (RMS trough)."""
    b = _body()
    assert "RMS_trough" in b, "шумовой пол не меряется"
    assert "awk '{print $NF}'" in b, \
        "число берётся не последним полем — grep по строке лога ловил «0» из [Parsed_astats_0 @ 0x…]"
    assert "было" in b and "стало" in b, "замер не показывается человеку"


def test_fails_loud_not_silent():
    """Без afftdn в сборке ffmpeg скрипт обязан сказать об этом словами,
    а не почистить «вникуда»; результат проверяется декодированием."""
    b = _body()
    assert "grep -q afftdn" in b, "наличие шумодава не проверяется"
    assert "brew upgrade ffmpeg" in b, "не сказано, как получить afftdn"
    assert "-f null -" in b, "результат не проверяется декодированием"
    assert "нет звуковой дорожки" in b, "файл без звука не объясняется"


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
