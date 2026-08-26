# -*- coding: utf-8 -*-
"""Тесты гайдбука роликов (FR-SITE43, SPEC-SITE.md).

Гайдбук — свод правил серии. Он бесполезен, если разошёлся с репозиторием:
названы инструменты, которых нет; забыт ролик; потеряно правило, за которое
уже платили переделкой. Тесты стерегут именно это, а не красоту текста.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_G = os.path.join(_ROOT, "automation", "1", "ГАЙДБУК.md")
_СЕРИЯ = os.path.join(_ROOT, "automation", "1")


def _текст():
    with open(_G, encoding="utf-8") as f:
        return f.read()


# ── гайдбук существует и покрывает всё, ради чего заведён ────────────────

def test_guidebook_exists():
    assert os.path.exists(_G), "гайдбука нет"
    assert len(_текст()) > 8000, "гайдбук слишком короткий, чтобы быть сводом"


def test_covers_every_area_of_the_work():
    """Правила накопились в семи областях. Пропущенная область — это ролик,
    сделанный по памяти."""
    t = _текст()
    for раздел in ("правил подачи", "Тайминг", "Геометрия", "Субтитры",
                   "Конвейер", "Чем проверять", "Грабли", "Дизайн-язык",
                   "Параметры в адресе", "новым роликом"):
        assert раздел in t, "в гайдбуке нет раздела про «%s»" % раздел


def test_every_video_of_the_series_is_listed():
    """Новый ролик делается из предыдущего — значит, список должен быть полон."""
    t = _текст()
    папки = sorted(d for d in os.listdir(_СЕРИЯ)
                   if d.startswith("overlay") and
                   os.path.isdir(os.path.join(_СЕРИЯ, d)))
    assert папки, "не нашлось ни одной папки ролика"
    for п in папки:
        assert п in t, "ролик «%s» в гайдбуке не упомянут" % п


def test_seven_permanent_rules_are_all_there():
    """Семь правил подачи — костяк всей серии, они повторены в каждом README."""
    t = _текст()
    for правило in ("прямоугольных блоков", "заголовков слайдов",
                    "минимум 24px", "в ряд", "не переносятся",
                    "картин на стене", "Текст белый"):
        assert правило in t, "потеряно постоянное правило: «%s»" % правило


def test_lessons_paid_for_by_rework_are_written_down():
    """Каждая из этих строк — оплаченная переделкой ошибка. Если она пропала
    из гайдбука, следующий ролик наступит на неё снова."""
    t = _текст()
    for урок in ("другого дубля",          # чужой SRT — вся графика ехала
                 "ПО СЛОВАМ",              # отсюда проверка по словам
                 "1.562",                  # кегль libass
                 "assert",                 # молчаливая подмена в сборщике
                 "tpad=stop=-1",           # шапка до конца дубля
                 "Phosphor",               # значки, а не эмодзи
                 "две строки"):            # субтитры «наслаивались»
        assert урок in t, "из гайдбука пропал урок про «%s»" % урок


# ── всё, что гайдбук называет, должно существовать ──────────────────────

def test_every_named_tool_exists():
    t = _текст()
    for путь in sorted(set(re.findall(r"tools/[\w./\-а-яё]+\.(?:py|sh)", t))):
        assert os.path.exists(os.path.join(_ROOT, путь)), \
            "гайдбук зовёт %s, а такого файла нет" % путь


def test_every_checker_is_described():
    """Обратная сторона: инструмент, который есть, но в гайдбуке не назван,
    для следующего ролика всё равно что не существует."""
    папка = os.path.join(_ROOT, "tools", "проверки")
    assert os.path.isdir(папка), "папки проверок нет"
    файлы = [f for f in os.listdir(папка) if f.endswith(".py")]
    assert len(файлы) >= 7, "проверок стало меньше семи"
    t = _текст()
    for f in файлы:
        assert f in t, "проверка %s нигде в гайдбуке не описана" % f


def test_checkers_are_not_nailed_to_one_video():
    """Проверки переехали из временной папки в репозиторий — значит, они не
    должны знать ни про конкретный ролик, ни про конкретную версию Chromium."""
    папка = os.path.join(_ROOT, "tools", "проверки")
    for f in sorted(os.listdir(папка)):
        if not f.endswith(".py"):
            continue
        with open(os.path.join(папка, f), encoding="utf-8") as fh:
            код = fh.read()
        assert "overlay-agentops" not in код, \
            "%s прибит к папке восьмой лекции" % f
        assert "chromium-1194" not in код, \
            "%s прибит к версии Chromium — она меняется" % f
        assert "scratchpad" not in код, \
            "%s всё ещё смотрит во временную папку сессии" % f


def test_numbers_match_the_real_page():
    """Числа гайдбука — не воспоминание, а то, что стоит на странице."""
    стр = os.path.join(_СЕРИЯ, "overlay-agentops", "index.html")
    with open(стр, encoding="utf-8") as f:
        html = f.read()
    t = _текст()
    assert "--zone-top:238px" in html and "--zone-h:392px" in html, \
        "зона на странице не 238…630 — гайдбук устарел"
    assert "238…630" in t, "в гайдбуке не та зона"
    assert "#F97316" in html and "#F97316" in t, "оранжевый акцент разошёлся"
    assert "--solar:#8B5CF6" in html and "#8B5CF6" in t, \
        "фиолетовый акцент разошёлся со страницей"
    assert "top:128px" in html and "128…224" in t, "шапка разошлась"


def test_pipeline_commands_are_runnable_as_written():
    """Команды конвейера пишутся так, чтобы их можно было скопировать."""
    t = _текст()
    for кусок in ("python3 tools/render_overlay.py",
                  "sh tools/слой.sh",
                  "sh собрать.sh",
                  "sh нарезать.sh"):
        assert кусок in t, "в конвейере нет шага «%s»" % кусок


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
