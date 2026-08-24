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


# ── FR-SITE29a: MOV → MP4 без заметной потери качества ───────────────────

def test_archive_mode_keeps_the_picture_as_it_was():
    """Владелец: «есть папка с видео в формате mov, надо сжать в mp4 без
    большой потери качества». Здесь задача не «сделать лёгким для веба»:
    кадр не уменьшается, частота кадров своя."""
    b = _body()
    assert "архив" in b, "нет режима «архив»"
    assert "ARCHIVE=1" in b, "режим не выставляет собственный флаг"
    assert "ARCHIVE=1; SHORT=100000" in b, \
        "в архиве кадр уменьшится: короткая сторона должна быть заведомо больше любой"
    assert "CRF=20" in b, "в архиве нужен CRF порога незаметности, а не веб-качество"


def test_archive_result_is_never_bigger_than_the_source():
    """Главный урок этого режима. Первая версия шла «CRF и никакого потолка» —
    и на уже сжатом исходнике писала БОЛЬШЕ бит, чем там было: 1080p h264
    3.0 МБ → 7.2 МБ, hevc 7.8 → 12.2 МБ. Владелец: «получилось еще больше по
    размеру»."""
    b = _body()
    assert '[ "$OUT_SZ" -ge "$IN_SZ" ]' in b, \
        "результат не сверяется с исходником — файл снова может вырасти"
    assert "БОЛЬШЕ исходника" in b, "рост файла не проговаривается человеку"
    assert '[ "$ARCHIVE" = 1 ] && [ "$COPYOK" = 1 ]' in b, \
        "«переложить как есть» должно работать только в архиве: в веб-режиме просили " \
        "720p, и вернуть вместо него исходные 4K — подмена"


def test_archive_ceiling_is_measured_in_bits_per_pixel():
    """Потолок «в N раз от исходника» здесь не работает: он тем выше, чем
    жирнее исходник, и на плотной съёмке разрешает написать больше, чем было.
    Считаем от кадра: ширина × высота × частота × бит на пиксель."""
    b = _body()
    assert "ARCBPP=" in b, "порог качества в битах на пиксель не задан"
    assert "w*h*f*b*m/1000" in b, "потолок в архиве считается не от кадра"
    assert 'case "$VCODEC" in hevc|av1|vp9) MULT=1.35' in b, \
        "h264 нужно больше бит, чем hevc: без поправки «без потери» станет потерей"


def test_archive_remuxes_what_is_already_dense():
    """Если исходник уже уложен плотнее порога, выигрывать нечем — дорожка
    перекладывается в mp4 как есть: качество 1:1 и мгновенно."""
    b = _body()
    assert "remux_copy" in b, "нет перекладывания без перекодирования"
    assert "-c:v copy" in b, "дорожка не копируется"
    assert '[ "$IN_KBPS" -le "$(( MAXK * 115 / 100 ))" ]' in b, \
        "нет порога «жать нечего» — плотный исходник пойдёт на перекодирование"
    assert 'case "$VCODEC" in h264|hevc|mpeg4) COPYOK=1' in b, \
        "prores и mjpeg в mp4 копировать нельзя — их надо перекодировать"
    assert '[ "$VCODEC" = "hevc" ] && TAG="-tag:v hvc1"' in b, \
        "без hvc1 переложенный hevc не откроется в QuickTime"


def test_frame_rate_is_read_as_average_not_declared():
    """Ловушка MOV: r_frame_rate там сплошь и рядом 600 — это шкала времени
    контейнера, а не съёмка. По ней потолок улетел бы в двадцать раз."""
    b = _body()
    assert "stream=avg_frame_rate" in b, "частота кадров берётся заявленной"
    assert "stream=r_frame_rate" in b, "нет запасного пути, если средней нет"
    assert "if (v<=0 || v>240) v=30" in b, "битая частота кадров не подстрахована"


def test_level_is_not_forced_on_full_size_frames():
    """`-level 4.0` — это потолок 1080p30. В архиве кадр родной, и на 4K или
    1080p60 такой уровень был бы нарушением."""
    b = _body()
    assert 'LEVELOPT="-level 4.0"' in b and '[ "$ARCHIVE" = 1 ] && LEVELOPT=""' in b, \
        "уровень профиля задаётся вслепую"


def test_archive_mode_does_not_skip_light_files():
    """«Уже лёгкий» — про веб. Лёгкий MOV всё равно надо переложить в mp4."""
    b = _body()
    assert "SKIPK=0" in b, "в архиве лёгкие файлы молча пропустятся и не переложатся"
    assert '[ "$SKIPK" -gt 0 ]' in b, "порог пропуска нельзя выключить"


def test_archive_keeps_the_sound_and_the_shooting_date():
    """Пережимать уже готовый aac второй раз — терять на ровном месте."""
    b = _body()
    assert '"$ACODEC" = "aac" ]; then AOPT="-c:a copy"' in b, \
        "готовый aac пережимается заново"
    assert "-c:a aac -b:a 256k" in b, "звук не-aac в архиве жмётся по-вебовски"
    assert "-map_metadata 0" in b, \
        "без даты съёмки «Фото» и Finder поставят файлам сегодняшний день"


def test_names_with_spaces_are_not_dropped():
    """«клип один.mov» разваливался по пробелу и молча пропускался: список
    файлов склеивался в строку. В POSIX sh пробелы держат только аргументы."""
    b = _body()
    assert "set -- *.mp4" in b, "список файлов собирается не в аргументы"
    assert "for f in $(ls" not in b and "for f in $FILES" not in b, \
        "имена со пробелами снова развалятся"
    assert 'for f in "$@"' in b, "аргументы перебираются без кавычек"
    assert "*.mov" in b and "*.MOV" in b, "mov не попадёт в список"


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


def test_no_stream_copy_in_the_web_modes():
    """Сжатие для веба копированием дорожки не делается — это всегда
    перекодирование. Копия живёт только в архиве, где жать уже нечего."""
    b = _body()
    assert "-c copy" not in b, "копированием дорожки ничего не сожмёшь"
    assert b.count("-c:v copy") == 1, "копия дорожки должна быть в одном месте — в remux_copy"
    assert "-c:v libx264 -preset slow" in b, "сжатие не перекодирует картинку"


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
