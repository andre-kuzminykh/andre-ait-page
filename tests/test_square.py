# -*- coding: utf-8 -*-
"""Тесты квадратной нарезки роликов (FR-SITE24, SPEC-SITE.md).
Без зависимостей — запускается и как `python3 tests/test_square.py`, и через pytest.

Инструмент режет вертикальный студийный кадр на квадратные куски 1080×1080.
Проверяем то, что ломается молча: кадрирование (сверху картины, снизу край
стола), разбор секунд и то, что скрипт вообще способен сделать обрезку.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PAGE = os.path.join(_ROOT, "automation", "square", "index.html")

# Ориентиры студийного кадра 1080×1920, снятые с реального дубля.
_FRAME_W, _FRAME_H = 1080, 1920
_PICTURES_TOP = 638        # верх рамок картин на стене
_TABLE_EDGE = 1652         # передний край стола


def _html():
    with open(_PAGE, encoding="utf-8") as f:
        return f.read()


def _script():
    """Тело генератора шелл-скрипта из страницы."""
    html = _html()
    return html[html.index("function script()"):html.index("mkBtn.addEventListener")]


# ── FR-SITE24: страница ни от чего не зависит ────────────────────────────

def test_page_is_self_contained():
    html = _html()
    external = re.findall(r'(?:src|href)="(https?:)?//[^"]+"', html)
    assert not external, "страница тянет внешние ресурсы: %r" % external
    assert os.path.exists(os.path.join(os.path.dirname(_PAGE), "Запустить.command")), \
        "нет лаунчера локального сервера: из file:// браузер не отдаст превью"


# ── FR-SITE24: кадрирование ──────────────────────────────────────────────

def test_default_crop_keeps_pictures_and_table():
    """Владелец про это сказал прямо: «внимательно видишь где стол и картины».
    Квадрат по умолчанию обязан захватывать и верх картин, и край стола."""
    html = _html()
    default = int(re.search(r'id="pos" min="0" max="1000" value="(\d+)"', html).group(1))
    top = default / 1000.0 * _FRAME_H
    side = _FRAME_W                       # квадрат во всю ширину вертикали
    bottom = top + side

    assert top < _PICTURES_TOP, \
        "квадрат начинается ниже верха картин (%d): они срежутся" % _PICTURES_TOP
    assert bottom > _TABLE_EDGE, \
        "квадрат кончается выше края стола (%d): стола не будет в кадре" % _TABLE_EDGE
    # И при этом картины не должны висеть посреди кадра — они у самой кромки.
    assert _PICTURES_TOP - top < 80, \
        "картины слишком далеко от верхней кромки (%.0fpx)" % (_PICTURES_TOP - top)


def test_crop_position_is_adjustable():
    """Дубли разные, поэтому положение квадрата — ползунок, а не константа,
    и его значение уезжает в скрипт."""
    html = _html()
    assert 'id="pos"' in html, "нет ползунка положения квадрата"
    assert "(frac()).toFixed(4)" in html, "положение не попадает в скрипт"
    assert "if(y<0)y=0; if(y>m)y=m" in html, \
        "положение не ограничено высотой кадра — вылезет за пределы"


# ── FR-SITE24: разбор секунд ─────────────────────────────────────────────

def test_cut_points_are_parsed_and_split():
    html = _html()
    assert "cuts.value.split(';')" in html, "секунды должны разделяться точкой с запятой"
    assert "raw.split(':')" in html, "формат мм:сс должен пониматься"
    # N точек реза → N+1 кусков: последний идёт до конца ролика.
    assert "edges.push(dur || Infinity)" in html, \
        "последний кусок пропадает, пока не приехала длительность"
    assert "sort(function (a, b) { return a - b; })" in html, \
        "точки реза должны сортироваться — иначе куски выйдут отрицательной длины"


# ── FR-SITE24: скрипт нарезки ────────────────────────────────────────────

def test_script_crops_and_reencodes():
    """Обрезку кадра нельзя сделать копированием дорожки — только пересборкой."""
    body = _script()
    assert "crop=$SIDE:$SIDE:$X:$Y" in body, "нет обрезки в квадрат"
    assert "scale=1080:1080" in body, "куски должны приводиться к 1080×1080"
    assert "-c copy" not in body, "обрезку копированием дорожки не сделать"
    assert "videotoolbox" in body, "на маке нарезка должна идти аппаратно"
    assert "$ROT" in body, "поворот кадра не учитывается"
    assert "SIDE=$DW; [ \"$DH\" -lt \"$DW\" ] && SIDE=$DH" in body, \
        "сторона квадрата должна браться по меньшей стороне кадра"


def test_script_checks_every_piece():
    """Каждый кусок проверяется декодированием: битый файл наружу не уходит."""
    body = _script()
    assert "-f null" in body, "куски не проверяются декодированием"
    assert "ОШИБКА в куске" in body, "нет разбора ошибки по куску"
    assert "command -v ffmpeg" in body, "скрипт должен сам сообщать о зависимостях"


def test_script_handles_open_ended_last_piece():
    """У последнего куска конца нет — он идёт до конца ролика."""
    body = _script()
    assert "пусто = до конца ролика" in body, "не объяснено, что пустой конец значит"
    assert 'if [ -n "$B" ]; then' in body, "пустой конец не обрабатывается"


def test_script_leaves_no_black_at_the_ends():
    """Владелец видел это своими глазами: у части роликов кусок начинался и
    кончался чёрным квадратом. Причина не в резе, а в исходнике: видеодорожка
    начинается позже звука (edit list в MOV с телефона) или кончается раньше
    него. Дырка на шкале — не кадр, покадровые проверки её не ловят, поэтому
    дорожки прижимаются к нулю, обрываются по короткой и сверяются по длине."""
    body = _script()
    assert "setpts=PTS-STARTPTS" in body, "видеодорожка куска не прижата к нулю"
    assert "asetpts=PTS-STARTPTS" in body, "звук куска не прижат к нулю"
    assert "aresample=async=1:first_pts=0" in body, "звук не выравнивается по нулю"
    assert "-shortest" in body, "кусок не обрывается по короткой дорожке — будет чернота в конце"
    # И проверка, которая ловит остаток: видеодорожка короче самого куска.
    assert "stream=duration" in body and "format=duration" in body, \
        "длины дорожки и куска не сверяются"
    assert "в плеере будет чернота" in body, "дыра не объясняется человеку"


def test_script_takes_seconds_as_an_argument():
    """Перерезать тот же клип по другим секундам можно без страницы: секунды
    и положение квадрата — аргументы, а не только вшитые значения."""
    body = _script()
    assert "CUTS=\"${2:-" in body, "секунды нельзя передать аргументом"
    assert "TOP=\"${3:-" in body, "положение квадрата нельзя передать аргументом"
    # Разбор секунд в самом скрипте: мм:сс и сортировка.
    assert "awk -F:" in body, "формат мм:сс в скрипте не разбирается"
    assert "sort -n" in body, \
        "точки реза не сортируются в скрипте — «45;12» дало бы кусок отрицательной длины"
    assert 'IFS=";"' in body, "разделитель точка с запятой в скрипте не задан"
    assert "IFS=$OLD" in body, "IFS не возвращается — дальше поломается разбор списков"


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   %s" % name)
            except Exception as e:  # AssertionError и любые сбои разбора
                failed += 1
                print("FAIL %s: %s: %s" % (name, type(e).__name__, e))
    raise SystemExit(1 if failed else 0)
