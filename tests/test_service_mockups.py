# -*- coding: utf-8 -*-
"""Тесты предложения и макетов сервиса «Ролики» (FR-SITE45, SPEC-SITE.md).

Макет полезен ровно до тех пор, пока он не врёт. Врать он может двумя
способами: показывать выдуманные данные (тогда не видно, что подпись не
влезает) и показывать экран, у которого низ срезан рамкой (ровно это и
случилось на третьем экране). Тесты стерегут оба.

Запускается и как `python3 tests/test_service_mockups.py`, и через pytest.
"""
import os
import re
import struct

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_UX = os.path.join(_ROOT, "СЕРВИС-UX.md")
_ПАПКА = os.path.join(_ROOT, "сервис-макеты")
_СТРАНИЦА = os.path.join(_ПАПКА, "index.html")
_СКРИПТ = os.path.join(_ПАПКА, "снять.py")
_РОЛИК = os.path.join(_ROOT, "automation", "1", "overlay-roles")

_ЭКРАНЫ = ["1-ролики", "2-материалы", "3-раскадровка",
           "4-сборка", "5-готово", "6-правила"]


def _текст(путь):
    with open(путь, encoding="utf-8") as f:
        return f.read()


def _размер_png(путь):
    with open(путь, "rb") as f:
        голова = f.read(24)
    assert голова[:8] == b"\x89PNG\r\n\x1a\n", путь + " — не PNG"
    return struct.unpack(">II", голова[16:24])


# ── предложение и макеты ─────────────────────────────────────────────────

def test_proposal_and_mockups_exist():
    assert os.path.exists(_UX), "предложения по сервису нет"
    assert os.path.exists(_СТРАНИЦА), "страницы макетов нет"
    assert os.path.exists(os.path.join(_ПАПКА, "README.md")), "README макетов нет"
    ux = _текст(_UX)
    assert len(ux) > 6000, "предложение выродилось в заметку"
    assert "сервис-макеты/" in ux, "предложение не ведёт к макетам"
    assert "СЕРВИС-UX.md" in _текст(os.path.join(_ПАПКА, "README.md")), \
        "макеты не ведут обратно к предложению"


def test_six_screens_and_six_shots():
    html = _текст(_СТРАНИЦА)
    ид = re.findall(r'<div class="screen" id="(s\d)"', html)
    assert ид == ["s1", "s2", "s3", "s4", "s5", "s6"], \
        "экранов должно быть шесть по порядку, а найдено: %s" % ид
    for имя in _ЭКРАНЫ:
        путь = os.path.join(_ПАПКА, имя + ".png")
        assert os.path.exists(путь), "нет скриншота " + имя
        assert os.path.getsize(путь) > 50000, имя + " — подозрительно пустой кадр"


def test_shots_are_taken_at_double_resolution():
    """Экран 1440×900, снимок — вдвое: на глаз читаются мелкие подписи."""
    for имя in _ЭКРАНЫ:
        ш, в = _размер_png(os.path.join(_ПАПКА, имя + ".png"))
        assert (ш, в) == (2880, 1800), \
            "%s снят как %d×%d, а нужно 2880×1800" % (имя, ш, в)


# ── то, из-за чего низ третьего экрана уезжал под срез ───────────────────

def test_frame_never_clips_the_bottom_panels():
    """`.main` — элемент грида: без min-height:0 он растёт по min-content,
    ряд становится выше 900px, и overflow:hidden съедает нижние панели."""
    css = _текст(_СТРАНИЦА)
    main = re.search(r"\.main\{([^}]*)\}", css)
    assert main, "правила .main нет"
    assert "min-height:0" in main.group(1), \
        "у .main нет min-height:0 — низ экрана снова срежет рамкой"
    экран = re.search(r"\.screen\{([^}]*)\}", css)
    assert экран and "height:900px" in экран.group(1), "экран должен быть 900px"


def test_script_measures_before_it_shoots():
    код = _текст(_СКРИПТ)
    assert os.path.exists(_СКРИПТ), "скрипта съёмки нет"
    assert "getBoundingClientRect" in код, "скрипт не меряет геометрию"
    assert "scrollHeight" in код, "скрипт не видит переполнения внутренних областей"
    assert "--только-замер" in код, "нет режима «померить и не снимать»"
    assert 'os.path.join(ПАПКА, "index.html")' in код, \
        "скрипт снимает не ту страницу, что лежит рядом"
    for имя in _ЭКРАНЫ:
        assert имя in код, "скрипт не знает про экран " + имя


# ── макеты стоят на настоящих данных ─────────────────────────────────────

def test_mockups_stand_on_real_data():
    for обложка in ("cover1.jpg", "cover2.jpg"):
        своя = open(os.path.join(_ПАПКА, "img", обложка), "rb").read()
        ролика = open(os.path.join(_РОЛИК, обложка), "rb").read()
        assert своя == ролика, обложка + " разошлась с обложкой девятого ролика"
    html = _текст(_СТРАНИЦА)
    for число in ("41.9", "101.8", "16"):
        assert число in html, "в макетах нет реального числа " + число
    assert "Мыслить как архитектор" in html, \
        "на макете нет настоящего замечания, ради которого экран и нужен"
    assert "49px при пороге 60" in html, "замечание без замера — выдумка"


def test_page_opens_from_the_repository():
    """Картинки лежат рядом, снаружи — только шрифты: страница должна
    открываться из репозитория, а не из папки сессии."""
    html = _текст(_СТРАНИЦА)
    чужое = [u for u in re.findall(r'(?:src|href)="([^"]+)"', html)
             if "://" in u and not u.startswith("https://fonts.googleapis.com")]
    assert not чужое, "макеты тянут наружу: %s" % чужое
    for путь in re.findall(r'<img src="([^"]+)"', html):
        assert os.path.exists(os.path.join(_ПАПКА, путь)), "нет картинки " + путь


if __name__ == "__main__":
    сбой = 0
    for имя, ф in sorted(globals().items()):
        if имя.startswith("test_") and callable(ф):
            try:
                ф()
                print("ok   " + имя)
            except AssertionError as e:
                сбой += 1
                print("СБОЙ " + имя + ": " + str(e))
    print("провалено: %d" % сбой)
    raise SystemExit(1 if сбой else 0)
