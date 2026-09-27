# -*- coding: utf-8 -*-
"""Сканеры приёмки лекции: П1-П9 живым рендером, а не строковым тестом.

«Строка есть в CSS» проходит, а страница при этом может быть чёрной или
рассыпанной. Поэтому каждый пункт приёмки из §11.1 LECTURE-GUIDE.md здесь
меряется в настоящем Chromium на настоящей странице.

    python3 tools/lecture_check.py kegl 3        # П5: мин. кегль телефона, >= 10px
    python3 tools/lecture_check.py kraya 3       # П3: заступы за края, должно быть 0
    python3 tools/lecture_check.py parnost 3     # П1: текст ПК -> телефон, 0 потерь
    python3 tools/lecture_check.py perenos 3     # аварийные переносы, 0
    python3 tools/lecture_check.py ikonki 3      # ложные иконки, 0
    python3 tools/lecture_check.py transform 3   # анимация стёрла transform, 0
    python3 tools/lecture_check.py perehod 3     # движение при смене слайда, 0
    python3 tools/lecture_check.py kadry 3 ДО    # кадры до правки
    python3 tools/lecture_check.py kadry 3 ПОСЛЕ # кадры после правки
    python3 tools/lecture_check.py sverka ДО ПОСЛЕ   # П8, должно быть 0
    python3 tools/lecture_check.py vse 3         # все сканеры подряд

*** ЗАПУСКАТЬ ТОЛЬКО ИЗ КОРНЯ РЕПОЗИТОРИЯ ***

Каталог кэша CDN ищется по ОТНОСИТЕЛЬНОМУ пути vendor/ (так же, как это
делает record_lecture.py). Из чужого каталога шрифт молча не подгрузится,
страница уедет на системный, метрики текста станут другими — и все замеры
соврут В БОЛЬШУЮ сторону. Это уже один раз испортило приёмку: сканер
показывал минимум 10.54px там, где на самом деле 9.71px. Поэтому здесь
запуск не из корня — это ошибка с выходом, а не предупреждение, и шрифт
проверяется пробой перед каждым замером.

Если vendor/ нет, а интернет есть — страница возьмёт шрифт и иконки сама;
проба всё равно отработает и не даст мерить по системному шрифту. Собрать
кэш можно так (нужен npm и доступ к fonts.googleapis.com):

    python3 tools/lecture_check.py vendor
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import record_lecture as rl  # noqa: E402  локальный сервер + vendor_route + проба шрифта

# Формы владельца. Между ними ничего нет, граница — 768px по ширине.
PC = {"width": 1380, "height": 864}
MOB = {"width": 376, "height": 844}
# Ширины для сканера краёв (§11.2). 1380 — компьютерная форма, остальные —
# телефонная, включая 767 (последний пиксель перед сменой формы).
KRAYA_SIZES = [(320, 844), (376, 844), (414, 844), (767, 844), (1380, 864)]

KEGL_MIN = 10.0        # П5
GUTTER_MIN = 12.0      # §2.1 п.6 — «чуть-чуть по бокам зазоры»
FRAMES = os.path.join(ROOT, "build", "lecture-frames")

# Панель «Текст» и хром — не контент слайда. Кружок головы контенту заезжать
# разрешено (канон §2.3 п.17), поэтому он в замерах тоже не участвует.
CHROME_SEL = "#lecture-header, #notes-panel, #video-bubble, .nav-arrow, #progress-container"


# ── стенд ────────────────────────────────────────────────────────────────

def must_run_from_root():
    if os.path.abspath(os.getcwd()) != ROOT:
        sys.exit("СТОП: запускать только из корня репозитория (%s).\n"
                 "   Сейчас: %s\n"
                 "   Из чужого каталога не найдётся vendor/ и все замеры соврут."
                 % (ROOT, os.getcwd()))


def vendor_dir():
    """Каталог кэша CDN — ровно тот относительный путь, что у record_lecture."""
    path = os.path.join(ROOT, "vendor")
    return path if os.path.isdir(path) else None


def chromium_path():
    """Playwright ставит свою ревизию, а в образе лежит своя. Берём из
    CHROMIUM_PATH, иначе ищем то, что реально есть на диске."""
    env = os.environ.get("CHROMIUM_PATH")
    if env and os.path.exists(env):
        return env
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    for name in sorted(os.listdir(base) if os.path.isdir(base) else [], reverse=True):
        if name.startswith("chromium-"):
            exe = os.path.join(base, name, "chrome-linux", "chrome")
            if os.path.exists(exe):
                return exe
    return None


class Stand:
    """Открытая лекция в нужной форме: сервер, браузер, подгруженный шрифт."""

    def __init__(self, lecture, viewport, vendor=None, motion=False):
        self.lecture, self.viewport = lecture, viewport
        self.vendor = vendor if vendor is not None else vendor_dir()
        # Кадры для П8 снимаются с ЗАГЛУШЕННОЙ анимацией — на этом держится
        # их детерминизм. Но тогда стенд слеп к дефектам, которые живут
        # ИМЕННО в анимации (см. cmd_transform), поэтому она включаема.
        self.motion = motion

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        # Порт занимают параллельные прогоны (сканеры гоняем пачками). Берём
        # свободный, иначе второй процесс падает на «address already in use».
        if not os.environ.get("LECTURE_PORT"):
            import socket
            s = socket.socket()
            s.bind(("127.0.0.1", 0))
            rl.PORT = s.getsockname()[1]
            s.close()
        self.srv = rl.serve()
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(
            executable_path=chromium_path(),
            args=["--no-sandbox", "--hide-scrollbars"])
        self.ctx = self.browser.new_context(
            viewport=dict(self.viewport), device_scale_factor=1,
            reduced_motion="no-preference" if self.motion else "reduce")
        if self.vendor:
            self.ctx.route("**/*", rl.vendor_route(self.vendor))
        self.page = self.ctx.new_page()
        # LECTURE_PATH — адрес колоды вместо /automation/<N>/. Нужен, когда у
        # лекции есть вторая версия (/automation/5/v2/): сканеры должны уметь
        # ходить по ней, иначе её никто не проверяет.
        path = os.environ.get("LECTURE_PATH") or "/automation/%d/" % self.lecture
        self.page.goto("http://127.0.0.1:%d%s" % (rl.PORT, path),
                       wait_until="load", timeout=120000)
        self.page.wait_for_timeout(3500)
        # Стартовый оверлей перекрывает слайд целиком — снимаем, иначе меряем чёрный экран.
        self.page.evaluate("() => document.querySelectorAll("
                           "'#start-overlay,#intro-overlay').forEach(e => e.remove())")
        self.page.wait_for_timeout(600)
        # Шрифт — до единого замера. Молчаливая подмена системным даёт
        # другие метрики текста и завышает кегль.
        rl.check_font(self.page, allow_fallback=False)
        self.check_scale()
        self.total = self.page.evaluate(
            "() => document.querySelectorAll('.slide-container').length")
        return self

    def check_scale(self):
        """Цепочка множителей посчитана верно — сверка с эталоном.

        Стоит ровно на той ошибке, которая уже испортила приёмку: .content-z
        несёт И zoom, И transform: scale (0.82935 * 0.970839 на слайде 24
        телефонной формы). Кто взял только zoom, получил кегль на 3% больше
        настоящего — и «ниже порога» вышло 2 слайда вместо 11.

        Проверяем честно: одну и ту же строку рисуем внутри холста и вне его
        и смотрим, совпадает ли отношение ширин с тем, что даёт effScale."""
        gap = self.page.evaluate(_js(JS_SCALE + r"""
        (() => {
          const cz = document.querySelector('.slide-container.opacity-100 .content-z')
                  || document.querySelector('.content-z');
          if (!cz) return 0;
          const mk = (parent) => {
            const e = document.createElement('span');
            e.textContent = 'Шжаб';
            e.style.cssText = 'font-family:Montserrat,sans-serif;font-weight:700;'
                            + 'font-size:100px;line-height:1;white-space:nowrap;'
                            + 'position:absolute;left:-9999px;top:0;visibility:hidden';
            parent.appendChild(e);
            const w = e.getBoundingClientRect().width;
            e.remove();
            return w;
          };
          const truth = mk(cz) / mk(document.body);
          return Math.abs(truth - effScale(cz)) / (truth || 1);
        })()
        """))
        if gap > 0.005:
            sys.exit("СТОП: множитель подгонки посчитан неверно — расхождение с "
                     "эталоном %.2f%%.\n   Замеры кегля доверять нельзя: в цепочке "
                     "появился множитель, которого effScale не видит." % (gap * 100))

    def __exit__(self, *exc):
        try:
            self.ctx.close()
            self.browser.close()
        finally:
            self._pw.stop()
            self.srv.shutdown()

    def each_slide(self, settle=520):
        """Проходит колоду слайд за слайдом (листаем, как зритель: подгонщик
        обязан дать один и тот же результат на любом пути)."""
        for i in range(self.total):
            self.page.wait_for_timeout(settle)
            yield i
            if i < self.total - 1:
                self.page.evaluate("() => window.nextSlide && window.nextSlide()")

    def resize(self, viewport):
        """Смена формы — синхронно, как в каноне; потом даём очереди подгонки
        разобрать колоду."""
        self.page.set_viewport_size(dict(viewport))
        self.page.wait_for_timeout(1200)


# ── общий кусок JS: эффективный кегль ────────────────────────────────────
#
# Кегль на экране — это НЕ то, что отдаёт getComputedStyle: тот возвращает
# кегль ДО подгонки (у элемента с text-[10px] это 12px — столько ему даёт
# slide-polish на телефоне). Между ним и зрителем стоит вся цепочка:
# zoom z на холсте, --view-scale и --fill-boost как transform.
#
# Считать множитель как rect.width/offsetWidth НЕЛЬЗЯ: offsetWidth округлён
# до целого пикселя, и на узких подписях ошибка доходит до 3%. На слайде 24
# это давало 9.60px вместо настоящих 9.95px — то есть сканер сам придумывал
# нарушение там, где его нет. Поэтому цепочку множителей собираем честно:
# zoom каждого предка и масштаб из его матрицы transform.

JS_SCALE = r"""
const effScale = (el) => {
  let f = 1;
  for (let node = el; node; node = node.parentElement) {
    const st = getComputedStyle(node);
    const z = parseFloat(st.zoom);
    if (z && Math.abs(z - 1) > 1e-6) f *= z;
    const tr = st.transform;
    if (tr && tr !== 'none') {
      try {
        const m = new DOMMatrixReadOnly(tr);
        const det = Math.abs(m.a * m.d - m.b * m.c);
        if (det > 1e-9) f *= Math.sqrt(det);
      } catch (e) { /* нечитаемая матрица — множитель не трогаем */ }
    }
  }
  return f;
};
const ownText = (el) => {
  let s = '';
  for (const n of el.childNodes) if (n.nodeType === 3) s += n.nodeValue;
  return s.replace(/­/g, '').replace(/\s+/g, ' ').trim();
};
const seen = (el) => {
  const st = getComputedStyle(el);
  if (st.visibility === 'hidden' || st.display === 'none') return false;
  if (parseFloat(st.opacity) < 0.05) return false;
  const r = el.getBoundingClientRect();
  return r.width > 0.5 && r.height > 0.5;
};
"""

JS_KEGL = JS_SCALE + r"""
(() => {
  const slide = document.querySelector('.slide-container.opacity-100')
             || document.querySelector('.slide-container');
  if (!slide) return {min: null, items: []};
  const out = [];
  for (const el of slide.querySelectorAll('*')) {
    if (el.closest(CHROME)) continue;
    const t = ownText(el);
    if (!t) continue;
    if (!seen(el)) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize) || 0;
    const eff = fs * effScale(el);
    if (eff > 0.5) out.push({px: Math.round(eff * 100) / 100,
                             tag: el.tagName.toLowerCase(),
                             cls: (el.className || '').toString().slice(0, 90),
                             text: t.slice(0, 70)});
  }
  out.sort((a, b) => a.px - b.px);
  return {min: out.length ? out[0].px : null, items: out.slice(0, 6)};
})()
"""


def _js(body):
    return body.replace("CHROME", json.dumps(CHROME_SEL))


# ── П5: минимальный эффективный кегль ────────────────────────────────────

def cmd_kegl(lecture):
    print("П5 — минимальный эффективный кегль на телефоне (норма >= %.0fpx)" % KEGL_MIN)
    bad = []
    with Stand(lecture, MOB) as st:
        print("   форма %dx%d, слайдов %d" % (MOB["width"], MOB["height"], st.total))
        rows = []
        for i in st.each_slide():
            r = st.page.evaluate(_js(JS_KEGL))
            rows.append((i, r))
            if r["min"] is not None and r["min"] < KEGL_MIN:
                bad.append((i, r))
    worst = sorted([r for r in rows if r[1]["min"] is not None],
                   key=lambda r: r[1]["min"])[:8]
    print("\n   самые мелкие слайды:")
    for i, r in worst:
        print("     слайд %-3d %6.2fpx   %s" % (i, r["min"], r["items"][0]["text"][:52]))
    if bad:
        print("\n   НИЖЕ ПОРОГА — %d слайд(ов):" % len(bad))
        for i, r in bad:
            print("     слайд %d — %.2fpx" % (i, r["min"]))
            for it in r["items"]:
                if it["px"] < KEGL_MIN:
                    print("        %6.2fpx  <%s class=\"%s\">  %s"
                          % (it["px"], it["tag"], it["cls"], it["text"]))
    else:
        print("\n   ВСЁ ЧИСТО: ни один слайд не ниже %.0fpx" % KEGL_MIN)
    return len(bad)


# ── П3: заступы за края экрана и карточек ────────────────────────────────

JS_KRAYA = JS_SCALE + r"""
(() => {
  const slide = document.querySelector('.slide-container.opacity-100')
             || document.querySelector('.slide-container');
  if (!slide) return [];
  const out = [], vw = innerWidth, vh = innerHeight, EPS = 1.0;
  // Подписи радиальных схем шире своих кружков ПО ЗАМЫСЛУ (§4.2) — не дефект.
  const exempt = (el) => !!el.closest('.rf-label') || el.classList.contains('rf-label');

  for (const el of slide.querySelectorAll('*')) {
    if (el.closest(CHROME)) continue;
    if (!ownText(el) || !seen(el) || exempt(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.left < -EPS || r.top < -EPS || r.right > vw + EPS || r.bottom > vh + EPS) {
      out.push({kind: 'экран', text: ownText(el).slice(0, 60),
                cls: (el.className || '').toString().slice(0, 80),
                out: Math.round(Math.max(-r.left, -r.top, r.right - vw, r.bottom - vh) * 10) / 10});
      continue;
    }
    // Плашка-ярлык (position:absolute с отрицательным смещением) СИДИТ на
    // рамке карточки по замыслу — «СРЕДА ИСПОЛНЕНИЯ» на слайде 7, например.
    // Для неё правило «текст не выходит за карточку» не писалось: это не
    // текст в потоке, а элемент, положенный на борт руками. Под неё в
    // slide-polish есть отдельные правила :has(> [class*="-top-2"]).
    const pos = getComputedStyle(el).position;
    if (pos === 'absolute' || pos === 'fixed') continue;
    // Рамка — КОНТЕНТ-БОКС карточки: паддинг принадлежит карточке, не тексту (§2.2 п.8).
    const card = el.parentElement && el.parentElement.closest(
      '[class*="rounded"],[class*="border"],[class*="bg-"]');
    if (!card || card === el || card.closest(CHROME)) continue;
    const cs = getComputedStyle(card), cr = card.getBoundingClientRect();
    const k = effScale(card);
    const box = {l: cr.left + parseFloat(cs.paddingLeft) * k,
                 t: cr.top + parseFloat(cs.paddingTop) * k,
                 r: cr.right - parseFloat(cs.paddingRight) * k,
                 b: cr.bottom - parseFloat(cs.paddingBottom) * k};
    const over = Math.max(box.l - r.left, box.t - r.top, r.right - box.r, r.bottom - box.b);
    if (over > EPS) out.push({kind: 'карточка', text: ownText(el).slice(0, 60),
                              cls: (el.className || '').toString().slice(0, 80),
                              out: Math.round(over * 10) / 10});
  }
  return out;
})()
"""

# Зазор меряем по тому, что зритель ВИДИТ: по тексту и по крашеным боксам.
# Сам холст .content-z — прозрачная коробка без фона: она шире картинки и
# давала «зазор 5.1px» там, где глазами его 14px.

JS_GUTTER = r"""
(() => {
  const slide = document.querySelector('.slide-container.opacity-100')
             || document.querySelector('.slide-container');
  if (!slide) return null;
  const paints = (el, st) => {
    for (const n of el.childNodes) if (n.nodeType === 3 && n.nodeValue.trim()) return true;
    const bg = st.backgroundColor;
    if (bg && bg !== 'transparent' && !/rgba\(\s*0,\s*0,\s*0,\s*0\s*\)/.test(bg)) return true;
    if (st.backgroundImage && st.backgroundImage !== 'none') return true;
    for (const s of ['Top', 'Right', 'Bottom', 'Left'])
      if (parseFloat(st['border' + s + 'Width']) > 0.4
          && st['border' + s + 'Style'] !== 'none') return true;
    return el.tagName === 'IMG' || el.tagName === 'SVG' || el.tagName === 'I';
  };
  let l = Infinity, r = -Infinity;
  for (const el of slide.querySelectorAll('*')) {
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none') continue;
    if (parseFloat(st.opacity) < 0.05) continue;
    const b = el.getBoundingClientRect();
    if (b.width < 0.5 || b.height < 0.5) continue;
    if (!paints(el, st)) continue;
    l = Math.min(l, b.left); r = Math.max(r, b.right);
  }
  if (!isFinite(l)) return null;
  return Math.round(Math.min(l, innerWidth - r) * 10) / 10;
})()
"""


def cmd_kraya(lecture):
    print("П3 — заступы за края экрана и карточек (норма 0)")
    total_bad = 0
    for w, h in KRAYA_SIZES:
        with Stand(lecture, {"width": w, "height": h}) as st:
            hits, gutters = [], []
            for i in st.each_slide():
                for e in st.page.evaluate(_js(JS_KRAYA)):
                    hits.append((i, e))
                g = st.page.evaluate(JS_GUTTER)
                if g is not None:
                    gutters.append((i, g))
        narrow = [(i, g) for i, g in gutters if g < GUTTER_MIN]
        total_bad += len(hits)
        print("   %4dx%-4d  заступов %-3d  мин. боковой зазор %5.1fpx%s"
              % (w, h, len(hits), min((g for _, g in gutters), default=0),
                 "  ЗАЗОР МАЛ на слайдах %s" % [i for i, _ in narrow][:6] if narrow else ""))
        for i, e in hits[:12]:
            print("        слайд %-3d %-9s +%.1fpx  %s" % (i, e["kind"], e["out"], e["text"]))
        if len(hits) > 12:
            print("        ... ещё %d" % (len(hits) - 12))
    print("   ИТОГО заступов: %d" % total_bad)
    return total_bad


# ── П1: текст компьютера = текст телефона ────────────────────────────────

JS_TEXT = r"""
(() => {
  const slide = document.querySelector('.slide-container.opacity-100')
             || document.querySelector('.slide-container');
  if (!slide) return [];
  const out = [];
  const walk = document.createTreeWalker(slide, NodeFilter.SHOW_TEXT);
  for (let n = walk.nextNode(); n; n = walk.nextNode()) {
    const el = n.parentElement;
    if (!el || el.closest(CHROME)) continue;
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none') continue;
    if (parseFloat(st.opacity) < 0.05) continue;
    // Видимость — по рамкам самого текста, а не родителя: у обёртки
    // display:contents рамок нет по определению, и её текст считался
    // потерянным на телефоне, хотя виден (слайд 8 лекции 2). Текст внутри
    // скрытого предка рамок не даёт и по-прежнему не считается.
    const rg = document.createRange(); rg.selectNodeContents(n);
    if (!rg.getClientRects().length) continue;
    const t = n.nodeValue.replace(/­/g, '').replace(/\s+/g, ' ').trim();
    if (t) out.push(t);
  }
  return out;
})()
"""


def _norm(s):
    # Мягкие переносы, неразрывные пробелы и дефис U+2011 не считаются
    # расхождением: это оформление, а не информация.
    s = s.replace("­", "").replace(" ", " ").replace("‑", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def cmd_parnost(lecture):
    print("П1 — информация на телефоне = информация на компьютере (норма 0 потерь)")
    pc, mob = {}, {}
    with Stand(lecture, PC) as st:
        for i in st.each_slide():
            pc[i] = st.page.evaluate(_js(JS_TEXT))
    with Stand(lecture, MOB) as st:
        for i in st.each_slide():
            mob[i] = st.page.evaluate(_js(JS_TEXT))
    lost_total = 0
    for i in sorted(pc):
        a = [_norm(x) for x in pc[i] if _norm(x)]
        b = " ".join(_norm(x) for x in mob.get(i, []))
        lost = [x for x in a if x and x not in b]
        if lost:
            lost_total += len(lost)
            print("   слайд %-3d потеряно %d:" % (i, len(lost)))
            for x in lost[:6]:
                print("        «%s»" % x[:72])
    print("   ИТОГО потерь: %d" % lost_total)
    return lost_total


# ── аварийные переносы ───────────────────────────────────────────────────

JS_PERENOS = JS_SCALE + r"""
(() => {
  const slide = document.querySelector('.slide-container.opacity-100')
             || document.querySelector('.slide-container');
  if (!slide) return [];
  const out = [];
  for (const el of slide.querySelectorAll('*')) {
    if (el.closest(CHROME)) continue;
    const t = ownText(el);
    if (!t || !seen(el)) continue;
    // Подгонщик, не уместив подпись, пишет overflow-wrap:anywhere ПРЯМО НА
    // элемент — и слово рвётся посреди: «СОСТОЯН/ИЕ» (§4.3, грабля 3).
    const inline = (el.getAttribute('style') || '');
    const st = getComputedStyle(el);
    const anywhere = /overflow-wrap\s*:\s*anywhere/i.test(inline)
                  || st.overflowWrap === 'anywhere' || st.wordBreak === 'break-all';
    if (!anywhere) continue;
    // Рвётся ли НА САМОМ ДЕЛЕ: слово длиннее строки, значит перенос внутри
    // слова. НО перенос по мягкому переносу (&shy;) — это НЕ авария: слово
    // ломается по слогу и с дефисом, ровно как задумал автор. Аварией
    // считается разрыв в случайном месте («СОСТОЯН/ИЕ»), поэтому смотрим,
    // какой символ стоит перед переходом на новую строку.
    const r = document.createRange();
    let torn = false;
    for (const n of el.childNodes) {
      if (n.nodeType !== 3) continue;
      const txt = n.nodeValue;
      if (/\s/.test(txt.trim())) continue;          // это не одно слово
      r.selectNodeContents(n);
      if (r.getClientRects().length < 2) continue;   // умещается в строку
      // Ищем ПЕРВЫЙ символ, который уехал на следующую строку.
      let top0 = null;
      for (let i = 0; i < txt.length; i++) {
        r.setStart(n, i); r.setEnd(n, i + 1);
        const rect = r.getBoundingClientRect();
        if (!rect.width && !rect.height) continue;
        if (top0 === null) { top0 = rect.top; continue; }
        if (rect.top > top0 + 1) {
          // перед переносом обязан стоять мягкий перенос
          if (txt.charCodeAt(i - 1) !== 0x00AD) torn = true;
          break;
        }
      }
      r.selectNodeContents(n);
    }
    out.push({text: t.slice(0, 60), torn: torn,
              cls: (el.className || '').toString().slice(0, 80)});
  }
  return out;
})()
"""


def cmd_perenos(lecture):
    print("Аварийные переносы посреди слова (норма 0)")
    bad = 0
    for name, vp in (("телефон", MOB), ("компьютер", PC)):
        with Stand(lecture, vp) as st:
            hits = []
            for i in st.each_slide():
                for e in st.page.evaluate(_js(JS_PERENOS)):
                    hits.append((i, e))
        torn = [h for h in hits if h[1]["torn"]]
        bad += len(torn)
        print("   %-9s подгонщик поставил anywhere: %-3d  из них реально рвётся: %d"
              % (name, len(hits), len(torn)))
        for i, e in torn[:10]:
            print("        слайд %-3d «%s»" % (i, e["text"]))
    print("   ИТОГО разорванных слов: %d" % bad)
    return bad


# ── ложные иконки ────────────────────────────────────────────────────────

JS_IKONKI = r"""
(() => {
  const out = [];
  for (const el of document.querySelectorAll('i[class*="ph-"]')) {
    const names = (el.className || '').toString().split(/\s+/)
                    .filter(c => /^ph-/.test(c) && !/^ph-(fill|bold|duotone|thin|light)$/.test(c));
    const st = getComputedStyle(el, '::before');
    const content = st.content;
    const r = el.getBoundingClientRect();
    out.push({names: names, content: content,
              w: Math.round(r.width * 10) / 10, h: Math.round(r.height * 10) / 10,
              fam: st.fontFamily});
  }
  return out;
})()
"""



# ── движение при смене слайда ────────────────────────────────────────────
#
# markActive() перещёлкивает .is-active при КАЖДОЙ смене слайда — это
# перезапускает каскад появления (FR-LECTURE-14). Если в каскаде остались
# анимации, меняющие геометрию (deckRise поднимал блок на 14px, iconPop
# масштабировал иконку с 0.72), зритель видит, как содержимое «встаёт на
# место» после каждого переключения. Кадры П8 снимаются без анимации и
# этого не видят вовсе.
#
# Проверка честная: щёлкаем слайд и дважды снимаем геометрию — сразу после
# переключения и когда движение заведомо доиграло. Позиции обязаны совпасть.

JS_GEOM = r"""
(() => {
  const s = document.querySelector('.slide-container.opacity-100');
  if (!s) return [];
  // Бесконечные анимации (вращение кольца, бегущий пунктир, дыхание узла)
  // двигаются ВСЕГДА и по замыслу — они не «встают на место». Такие элементы
  // и всё, что внутри них, из проверки исключаем, иначе она всегда красная.
  const forever = (el) => {
    for (let n = el; n && n !== s.parentElement; n = n.parentElement) {
      if (/infinite/.test(getComputedStyle(n).animationIterationCount || '')) return true;
    }
    return false;
  };
  const out = [];
  for (const el of s.querySelectorAll('*')) {
    if (forever(el)) { out.push(null); continue; }
    const r = el.getBoundingClientRect();
    out.push([Math.round(r.left * 10) / 10, Math.round(r.top * 10) / 10,
              Math.round(r.width * 10) / 10, Math.round(r.height * 10) / 10]);
  }
  return out;
})()
"""

JS_LABEL = r"""
(i) => {
  const s = document.querySelector('.slide-container.opacity-100');
  const el = s ? s.querySelectorAll('*')[i] : null;
  if (!el) return '';
  const t = (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 34);
  return t || ('<' + el.tagName.toLowerCase() + ' class="'
               + (el.className || '').toString().slice(0, 44) + '">');
}
"""

MOVE_EPS = 0.5      # меньше — это округление подпикселей, а не движение


def cmd_perehod(lecture):
    """При переключении слайда содержимое не имеет права двигаться."""
    print("Движение содержимого при смене слайда (норма 0)")
    bad = []
    with Stand(lecture, PC, motion=True) as st:
        st.page.wait_for_timeout(900)
        for i in range(st.total - 1):
            st.page.evaluate("() => window.nextSlide && window.nextSlide()")
            st.page.wait_for_timeout(40)          # каскад только начался
            a = st.page.evaluate(JS_GEOM)
            st.page.wait_for_timeout(900)         # заведомо доиграл
            b = st.page.evaluate(JS_GEOM)
            if len(a) != len(b):
                bad.append((i + 1, "состав слайда изменился", 0))
                continue
            worst, worst_i = 0.0, -1
            for k in range(len(a)):
                if a[k] is None or b[k] is None:
                    continue                      # вечное движение — не наш случай
                d = max(abs(a[k][j] - b[k][j]) for j in range(4))
                if d > worst:
                    worst, worst_i = d, k
            if worst > MOVE_EPS:
                label = st.page.evaluate(JS_LABEL, worst_i)
                bad.append((i + 1, label, worst))
    if bad:
        print("   ДВИГАЕТСЯ на %d переходах:" % len(bad))
        for i, label, d in bad[:12]:
            print("     слайд %-3d сдвиг %5.1fpx  %s" % (i, d, label))
        if len(bad) > 12:
            print("     ... ещё %d" % (len(bad) - 12))
        print("   Лечение: убрать из каскада появления всё, что меняет геометрию"
              " —\n   оставить только прозрачность. Каскад играет заново на КАЖДОЙ"
              " смене слайда.")
    else:
        print("   ВСЁ ЧИСТО: на %d переходах геометрия не шелохнулась" % (st.total - 1))
    return len(bad)


# ── затирание статических трансформов анимацией ──────────────────────────
#
# Кадры для П8 снимаются с заглушённой анимацией — иначе попиксельная сверка
# развалится. Но из-за этого стенд СЛЕП к дефектам, которые живут именно в
# анимации, и один такой уже доехал до прода: keyframes, заканчивающиеся
# кадром transform:none при animation-fill-mode:both, НАВСЕГДА перебивают
# собственный transform элемента. У карточек радиальной схемы это стирало
# -translate-x-1/2 -translate-y-1/2, и они висели углом на точке кольца
# вместо центра. В кадрах сканера дефекта не было — там анимация не шла.
#
# Поэтому здесь стенд поднимается С анимацией и меряет то, что реально
# осталось от трансформа, когда движение доиграло.

JS_TRANSFORM = r"""
(() => {
  // 1. Какие анимации вообще трогают transform в КОНЕЧНОМ кадре.
  const risky = new Set();
  // Рекурсия обязательна: @keyframes внутри @media первая версия проверки
  // пропускала, и iconPop — с тем же transform:none в конечном кадре —
  // не попал в список рискованных.
  const walk = (rules) => {
    if (!rules) return;
    for (const r of rules) {
      if (r.type === CSSRule.KEYFRAMES_RULE) {
        for (const kf of r.cssRules) {
          const key = (kf.keyText || '').replace(/\s/g, '');
          if (key !== '100%' && key !== 'to') continue;
          if (kf.style && kf.style.transform) risky.add(r.name);
        }
      } else if (r.cssRules) {
        walk(r.cssRules);                 // @media, @supports, @layer
      }
    }
  };
  for (const sheet of document.styleSheets) {
    try { walk(sheet.cssRules); } catch (e) { continue; }      // чужой источник
  }
  // 2. Элементы, у которых КЛАСС объявляет transform, а в браузере его нет.
  const TW = /(^|\s)-?(translate-x-|translate-y-|translate-|rotate-|scale-|skew-)/;
  const IDENT = /^(none|matrix\(1,\s*0,\s*0,\s*1,\s*0,\s*0\))$/;
  const out = [];
  const slide = document.querySelector('.slide-container.opacity-100');
  if (!slide) return {risky: [...risky], hits: out};
  for (const el of slide.querySelectorAll('*')) {
    const cls = (el.className || '').toString();
    if (!TW.test(cls)) continue;
    const st = getComputedStyle(el);
    if (!IDENT.test(st.transform)) continue;        // трансформ на месте — всё хорошо
    const names = (st.animationName || '').split(',').map(x => x.trim());
    const hit = names.filter(n => risky.has(n));
    if (!hit.length) continue;                      // обнулил не анимация — не наш случай
    out.push({anim: hit.join(','), fill: st.animationFillMode,
              cls: cls.slice(0, 80),
              text: (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 34)});
  }
  return {risky: [...risky], hits: out};
})()
"""


def cmd_transform(lecture):
    """Анимация не имеет права стирать собственный transform элемента."""
    print("Затирание статических трансформов анимацией (норма 0)")
    bad, risky = [], []
    with Stand(lecture, PC, motion=True) as st:
        for i in st.each_slide(settle=1100):     # даём движению доиграть
            r = st.page.evaluate(JS_TRANSFORM)
            if not risky:
                risky = r["risky"]
            for e in r["hits"]:
                bad.append((i, e))
    print("   анимаций, задающих transform в конечном кадре: %d%s"
          % (len(risky), (" — " + ", ".join(sorted(risky))) if risky else ""))
    if bad:
        print("   СТЁРТЫХ ТРАНСФОРМОВ: %d" % len(bad))
        for i, e in bad[:12]:
            print("     слайд %-3d %-10s fill:%-9s %s" % (i, e["anim"], e["fill"], e["text"]))
            print("            class=\"%s\"" % e["cls"])
        if len(bad) > 12:
            print("     ... ещё %d" % (len(bad) - 12))
        print("   Лечение: в keyframes использовать независимые свойства"
              " scale/translate/rotate\n"
              "   вместо transform — они композируются с трансформом элемента,"
              " а не заменяют его.")
    else:
        print("   ВСЁ ЧИСТО: ни один элемент не потерял свой transform")
    return len(bad)


def cmd_ikonki(lecture):
    print("Ложные имена иконок Phosphor (норма 0)")
    with Stand(lecture, PC) as st:
        seen_names, bad = {}, {}
        for i in st.each_slide():
            for e in st.page.evaluate(JS_IKONKI):
                for n in e["names"]:
                    seen_names.setdefault(n, set()).add(i)
                    # Несуществующее имя: правило ::before не нашлось,
                    # content пустой или none — глиф не рисуется вовсе.
                    if e["content"] in ("none", '""', "''", "normal", ""):
                        bad.setdefault(n, set()).add(i)
    print("   всего имён ph-*: %d, уникальных: %d"
          % (sum(len(v) for v in seen_names.values()), len(seen_names)))
    if bad:
        print("   НЕ РИСУЮТСЯ — %d имён:" % len(bad))
        for n in sorted(bad):
            print("     %-28s слайды %s" % (n, sorted(bad[n])[:10]))
    else:
        print("   ВСЁ ЧИСТО: каждое имя ph-* даёт настоящий глиф")
    return len(bad)


# ── П8: кадры и попиксельная сверка ──────────────────────────────────────

def cmd_kadry(lecture, tag):
    """Кадры ОБЕИХ форм. П8 сверяет компьютерные, телефонные — чтобы глазами."""
    made = 0
    for name, vp in (("pc", PC), ("mob", MOB)):
        out = os.path.join(FRAMES, tag, name)
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out, exist_ok=True)
        with Stand(lecture, vp) as st:
            for i in st.each_slide():
                st.page.screenshot(path=os.path.join(out, "slide-%03d.png" % i))
                made += 1
        print("   %s: %d кадров -> %s" % (name, st.total, out))
    print("   метка «%s», всего кадров %d" % (tag, made))
    return 0


def cmd_sverka(tag_a, tag_b):
    """П8 — попиксельная сверка компьютерных кадров. Меняться должно только то,
    о чём просил владелец; всё остальное — правка, вылезшая из медиазапроса."""
    print("П8 — попиксельная сверка компьютерной формы «%s» -> «%s» (норма 0)"
          % (tag_a, tag_b))
    a_dir = os.path.join(FRAMES, tag_a, "pc")
    b_dir = os.path.join(FRAMES, tag_b, "pc")
    for d in (a_dir, b_dir):
        if not os.path.isdir(d):
            sys.exit("нет кадров: %s (сними их: lecture_check.py kadry N МЕТКА)" % d)
    names = sorted(set(os.listdir(a_dir)) | set(os.listdir(b_dir)))
    changed = []
    for n in names:
        pa, pb = os.path.join(a_dir, n), os.path.join(b_dir, n)
        if not os.path.exists(pa) or not os.path.exists(pb):
            changed.append((n, "нет пары"))
            continue
        ba, bb = open(pa, "rb").read(), open(pb, "rb").read()
        if ba == bb:
            continue
        changed.append((n, _pixel_diff(pa, pb)))
    if changed:
        print("   ИЗМЕНИЛОСЬ %d кадров из %d:" % (len(changed), len(names)))
        for n, how in changed:
            print("     %s — %s" % (n, how))
    else:
        print("   ВСЁ ЧИСТО: %d кадров ПК не изменились ни на пиксель" % len(names))
    return len(changed)


def _pixel_diff(pa, pb):
    """Сколько пикселей разошлось. Без Pillow — считаем через сам Chromium,
    чтобы не тащить зависимость ради одной сверки."""
    try:
        from PIL import Image, ImageChops
    except ImportError:
        return "байты различаются (поставьте Pillow для счёта пикселей)"
    ia, ib = Image.open(pa).convert("RGB"), Image.open(pb).convert("RGB")
    if ia.size != ib.size:
        return "разный размер %s vs %s" % (ia.size, ib.size)
    bbox = ImageChops.difference(ia, ib).getbbox()
    if not bbox:
        return "0 пикселей (различие только в сжатии PNG)"
    n = sum(1 for p in ImageChops.difference(ia, ib).getdata() if p != (0, 0, 0))
    return "%d пикселей, область %s" % (n, bbox)


# ── сборка кэша CDN ──────────────────────────────────────────────────────

def cmd_vendor():
    """vendor/ лежит в .gitignore — в свежем контейнере его нет. Собираем."""
    ua = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/141.0.0.0 Safari/537.36")
    fonts = os.path.join(ROOT, "vendor", "fonts", "files")
    os.makedirs(fonts, exist_ok=True)
    url = ("https://fonts.googleapis.com/css2?family=Montserrat:"
           "wght@300;400;500;600;700;800;900&display=swap")
    css = urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": ua}), timeout=30
    ).read().decode("utf-8")
    # Ссылки на gstatic в css2.css остаются КАК ЕСТЬ. Переписать их на
    # относительные «files/...» нельзя: база у этого css — googleapis, и
    # запрос уйдёт на fonts.googleapis.com/files/..., мимо подменяющей ветки
    # vendor_route, которая ловит только fonts.gstatic.com. Шрифт тогда молча
    # не подгрузится, страница уедет на системный и все замеры соврут.
    for u in sorted(set(re.findall(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", css))):
        dest = os.path.join(fonts, u.rsplit("/", 1)[1].split("?")[0])
        if not os.path.exists(dest):
            open(dest, "wb").write(urllib.request.urlopen(
                urllib.request.Request(u, headers={"User-Agent": ua}), timeout=60).read())
    open(os.path.join(ROOT, "vendor", "fonts", "css2.css"), "w", encoding="utf-8").write(css)
    print("   шрифт: %d файлов" % len(os.listdir(fonts)))

    # Иконки. unpkg и jsdelivr закрыты корпоративным прокси, npm — открыт.
    phos = os.path.join(ROOT, "vendor", "phosphor")
    if not os.path.isdir(os.path.join(phos, "src", "regular")):
        tmp = os.path.join(ROOT, "build", "phos")
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp, exist_ok=True)
        subprocess.run(["npm", "pack", "@phosphor-icons/web@2.1.1"],
                       cwd=tmp, check=True, stdout=subprocess.DEVNULL)
        tgz = [f for f in os.listdir(tmp) if f.endswith(".tgz")][0]
        subprocess.run(["tar", "xzf", tgz], cwd=tmp, check=True)
        os.makedirs(phos, exist_ok=True)
        shutil.copytree(os.path.join(tmp, "package", "src"),
                        os.path.join(phos, "src"), dirs_exist_ok=True)
        shutil.rmtree(tmp, ignore_errors=True)
    print("   иконки: %s" % os.path.join(phos, "src"))
    return 0


# ── точка входа ──────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Сканеры приёмки лекции (П1-П9). Запускать из корня репозитория.")
    ap.add_argument("cmd", choices=["kegl", "kraya", "parnost", "perenos",
                                    "ikonki", "transform", "perehod", "kadry", "sverka",
                                    "vse", "vendor"])
    ap.add_argument("a", nargs="?", help="номер лекции (или метка ДО для sverka)")
    ap.add_argument("b", nargs="?", help="метка кадров")
    args = ap.parse_args()

    if args.cmd == "vendor":
        must_run_from_root()
        return cmd_vendor()

    must_run_from_root()
    if args.cmd == "sverka":
        if not args.a or not args.b:
            sys.exit("нужны две метки: lecture_check.py sverka ДО ПОСЛЕ")
        return cmd_sverka(args.a, args.b)

    if not args.a:
        sys.exit("нужен номер лекции: lecture_check.py %s 3" % args.cmd)
    n = int(args.a)
    if args.cmd == "kadry":
        if not args.b:
            sys.exit("нужна метка: lecture_check.py kadry %d ДО" % n)
        return cmd_kadry(n, args.b)
    if args.cmd == "vse":
        bad = 0
        for fn in (cmd_kegl, cmd_kraya, cmd_parnost, cmd_perenos,
                   cmd_ikonki, cmd_transform, cmd_perehod):
            bad += fn(n)
            print()
        print("ИТОГО нарушений: %d" % bad)
        return bad
    return {"kegl": cmd_kegl, "kraya": cmd_kraya, "parnost": cmd_parnost,
            "perenos": cmd_perenos, "ikonki": cmd_ikonki,
            "transform": cmd_transform,
            "perehod": cmd_perehod}[args.cmd](n)


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
