# -*- coding: utf-8 -*-
"""Тесты движка реплик-эффектов (FX_JS в tools/animate_slide.py).

Движок — большой кусок JavaScript внутри питоновской строки: его не проверяет
ни один линтер и не импортирует ни один модуль, поэтому сторожим его здесь —
синтаксисом и текстом. Запускается и как `python3 tests/test_slide_fx.py`,
и через pytest.
"""
import os
import shutil
import subprocess
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "tools", "animate_slide.py")


def _source():
    return open(_SRC, encoding="utf-8").read()


def _fx_js():
    """Готовый к исполнению JS: подставляем плейсхолдеры, как это делает render()."""
    body = _source().split('FX_JS = r"""')[1].split('"""')[0]
    return body.replace("__CUES__", "[]").replace("__SPREAD__", "1.8")


def _underline_branch():
    js = _fx_js()
    head = js.index("cue.fx === 'underline'")
    return js[head:js.index("cue.fx === 'rise'", head)]


def test_fx_js_is_valid_javascript():
    """Синтаксическая ошибка в FX_JS всплывает только на рендере — через
    десять минут съёмки и с пустым кадром на выходе. Ловим сразу."""
    node = shutil.which("node")
    if not node:                                   # pragma: no cover
        print("SKIP: node не найден")
        return
    tmp = os.path.join(tempfile.mkdtemp(prefix="fxjs_"), "fx.js")
    open(tmp, "w", encoding="utf-8").write(_fx_js())
    r = subprocess.run([node, "--check", tmp], capture_output=True, text=True)
    assert r.returncode == 0, "FX_JS не парсится:\n%s" % r.stderr


def test_underline_never_repaints_gradient_text():
    """Заголовки лекции красят БУКВЫ фоном (background-clip:text). Реплика
    underline раньше писала им background-size: N% 4px — и заливка букв
    становилась четырёхпиксельной полоской, фраза пропадала целиком
    («операционное ядро бизнеса» на слайде 1). Ветка обязана сперва спросить
    paintsTextViaBackground и для таких элементов фон не трогать."""
    branch = _underline_branch()
    assert "paintsTextViaBackground(el)" in branch, \
        "underline не проверяет, не занят ли фон буквами:\n%s" % branch
    guard = branch.index("paintsTextViaBackground(el)")
    for prop in ("backgroundSize", "backgroundImage", "backgroundPosition"):
        if prop in branch:
            assert branch.index(prop) > guard, \
                "%s пишется ДО проверки — градиентный заголовок пропадёт" % prop


def test_underline_fallback_draws_a_real_bar():
    """Фолбэк должен именно РИСОВАТЬ подчёркивание, а не тихо ничего не делать:
    иначе реплика пропадает из кадра и слайд выглядит «мёртвым»."""
    branch = _underline_branch()
    assert "bars.appendChild" in branch, "фолбэк ничего не добавляет в слой"
    assert "background:' + SOLAR" in branch, "полоска не оранжевая"
    assert "grown" in branch, "полоска не расползается — нет анимации ширины"


def test_overlay_layer_is_reset_every_frame():
    """Рендер покадровый: apply(t) обязан быть чистой функцией времени. Слой
    подчёркиваний живёт вне слайда, значит его чистка — отдельной строкой,
    иначе полоски копятся кадр за кадром."""
    js = _fx_js()
    body = js[js.index("function apply(t)"):]
    assert "bars.innerHTML = ''" in body[:400], \
        "слой подчёркиваний не сбрасывается в начале apply()"
    assert "layer.innerHTML = ''" in body[:400], \
        "слой эмодзи не сбрасывается в начале apply()"


def test_overlay_layer_sits_above_the_slide():
    """Полоска рисуется поверх страницы и в оконных координатах: position:fixed
    не наследует transform от .content-z, а боксы приходят из
    getBoundingClientRect. Внутри слайда (z-index:-1, как слой эмодзи) её
    закрыла бы карточка."""
    js = _fx_js()
    decl = js[js.index("var bars ="):js.index("document.body.appendChild(bars)")]
    assert "position:fixed" in decl
    assert "z-index:2" in decl, "полоска должна быть выше содержимого слайда"
    assert "pointer-events:none" in decl


def test_gradient_detection_reads_background_clip():
    """Признак «фон = буквы» — именно background-clip:text (с вебкитным
    префиксом у Chromium), а не прозрачный цвет: у обычного текста заливка
    тоже бывает прозрачной на кадрах анимации."""
    js = _fx_js()
    fn = js[js.index("function paintsTextViaBackground"):]
    fn = fn[:fn.index("\n  }")]
    assert "webkitBackgroundClip" in fn and "backgroundClip" in fn
    assert "'text'" in fn


# ── Канон сценариев ───────────────────────────────────────────────────────

# Слайды, доведённые до канона «карточки не растут». Правило проверяется по
# факту: у каждой реплики карточки grow:0, а zoom (эффект, у которого рост —
# единственное содержание) не используется вовсе. Список растёт по мере
# рендера остальных слайдов — вслепую его расширять нельзя, надо знать, какая
# цель карточка, а какая заголовок.
CANON_SLIDES = (1, 2)


def _scenarios():
    import glob
    return sorted(glob.glob(os.path.join(_ROOT, "tools", "fx", "*.json")))


def test_emoji_burst_happens_once_per_slide():
    """Канон владельца: «только один раз эмодзи вылетают — больше не надо».
    Всплеск — акцент, а не фон; семь штук за слайд превращали его в шум."""
    import json
    for p in _scenarios():
        d = json.load(open(p, encoding="utf-8"))
        n = sum(1 for c in d["cues"] if c.get("burst"))
        assert n <= 1, "%s: всплесков %d, а канон — один" % (os.path.basename(p), n)


def test_canon_slides_never_enlarge_cards():
    """«Не надо текст в карточках увеличивать»: подсветка остаётся (ореол,
    обводка, подъём), рост убран. zoom здесь запрещён — у него, кроме роста,
    ничего нет, и с grow:0 реплика просто пропала бы из кадра."""
    import json
    for n in CANON_SLIDES:
        p = os.path.join(_ROOT, "tools", "fx", "lecture1-slide%02d.json" % n)
        d = json.load(open(p, encoding="utf-8"))
        for c in d["cues"]:
            assert c.get("fx") != "zoom", \
                "слайд %d: реплика на %s осталась zoom — это чистый рост" % (n, c["at"])
            if "grow" in c:
                assert c["grow"] == 0, \
                    "слайд %d: реплика на %s растит цель на %s" % (n, c["at"], c["grow"])


# Заголовки и подписи, живущие ВНУТРИ карточек. Их нельзя брать целью
# подсветки: вокруг слова рисуется прямоугольник, и слайд превращается в
# набор рамок (правка владельца: «не надо выделять прямоугольником отдельные
# тайтлы в словах, просто не трогай слова в карточках»). Подсвечиваем карточку
# целиком либо не трогаем вовсе.
CARD_WORDS = {
    1: ("От инструмента к агенту", "AI‑First компании", "Новая роль человека"),
    2: ("Лидеры", "Их клиенты", "AI‑First компании"),
}
# Эффекты, которые рисуют вокруг цели рамку или ореол.
BOXING_FX = ("glow-violet", "glow-solar", "frame", "zoom", "pop")


def test_words_inside_cards_are_left_alone():
    import json
    for n, words in CARD_WORDS.items():
        p = os.path.join(_ROOT, "tools", "fx", "lecture1-slide%02d.json" % n)
        d = json.load(open(p, encoding="utf-8"))
        for c in d["cues"]:
            if c["text"].strip() in words:
                assert c["fx"] not in BOXING_FX, (
                    "слайд %d: реплика на %s обводит %r — это заголовок внутри "
                    "карточки" % (n, c["at"], c["text"]))


def test_frame_honours_zero_grow():
    """`cue.grow || 0.01` возвращал честный ноль обратно в процент, и запрет
    «не увеличивать» молча не работал для рамки."""
    js = _fx_js()
    branch = js[js.index("cue.fx === 'frame'"):]
    branch = branch[:branch.index("cue.fx === 'underline'")]
    # комментарии выкидываем: в них та самая формула разобрана как ошибка
    code = "\n".join(l for l in branch.splitlines()
                     if not l.lstrip().startswith("//"))
    assert "cue.grow ||" not in code, "рамка снова растит цель при grow:0"
    assert "typeof cue.grow === 'number'" in code


if __name__ == "__main__":
    ok = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("PASS %s" % name)
            ok += 1
    print("\nВсе тесты движка реплик пройдены: %d" % ok)
