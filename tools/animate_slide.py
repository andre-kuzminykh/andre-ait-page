# -*- coding: utf-8 -*-
"""Анимация слайда под голос: подсветки, увеличение, эмодзи-всплески.

Идея: слайд перестаёт быть неподвижной картинкой. Когда в озвучке звучит
«Восприятие», карточка «Восприятие» подсвечивается и чуть подрастает; на
«автономность» под словом прочерчивается линия; где просится — вылетает
горсть эмодзи. Всё это привязано к СЛОВАМ, а не к секундам на глаз.

Конвейер:

  1. Тайминг слов. `--transcribe` прогоняет клип слайда через faster-whisper
     с пословными метками и кладёт рядом два файла:
       build/timings/lecture1-slide05.json  — слова со start/end
       build/timings/lecture1-slide05.srt   — субтитры по 2 слова на реплику
     (Модель качается с huggingface, поэтому шаг требует интернета.)

  2. Сценарий — tools/fx/lecture<N>-slide<MM>.json: список реплик вида
     «слово `восприятие` → элемент с текстом `Восприятие` → эффект glow-violet
     + всплеск 👁». Время каждой реплики берётся из тайминга по полю word;
     если тайминга нет, действует запасное поле at (секунды).

  3. Рендер. Кадры снимаются ДЕТЕРМИНИРОВАННО: страница не проигрывает
     анимацию сама по себе — сцена умеет показать состояние на любой момент
     времени, и рендерер просит её показать t = 0, 1/30, 2/30… Поэтому
     тайминг точен до кадра и повторяем: два прогона дают побайтово равные
     кадры (в отличие от записи экрана, где кадры теряются).

  4. Сборка. Кадры + звук клипа + кружок с головой → mp4 1920×1080.

    python3 tools/animate_slide.py --slide 5 --transcribe   # с распознаванием
    python3 tools/animate_slide.py --slide 5                # тайминг уже есть
    python3 tools/animate_slide.py --slide 5 --preview 8    # 8 контрольных кадров
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cinema as cinema_fx
from record_lecture import (ROOT, W, H, FPS, BUB_D, BUB_MARGIN, CHROME_OFF,
                            PORT, ffmpeg_bin, run, duration, head_clips, fetch,
                            serve, vendor_route, check_font, circle_mask,
                            timecode)

FX_DIR = os.path.join(ROOT, "tools/fx")
BUILD = os.path.join(ROOT, "build")

# Сцена целиком живёт функцией от времени: никаких CSS-переходов и
# requestAnimationFrame. Рендерер задаёт t, сцена рисует состояние — это и
# делает покадровую съёмку точной и воспроизводимой.
FX_JS = r"""
window.__fx = (function(){
  var CUES = __CUES__;
  var SOLAR = '#F97316', VIOLET = '#8B5CF6';
  // Размах разлёта эмодзи. В режиме «кино» кадр снимается на всю ширину
  // и ложится ПОВЕРХ видео, поэтому всплески должны долетать до человека
  // (правка владельца: «эмодзи могут вылетать за чёрное — прям на само
  // видео»). При штатной съёмке множитель 1 — поведение не меняется.
  var SPREAD = __SPREAD__;

  // Эмодзи вылетают ИЗ-ЗА карточек (правка владельца), а не поверх. Слой для
  // этого живёт ВНУТРИ слайда с z-index:-1: отрицательный слой рисуется после
  // фона слайда, но до карточек с их текстом. За body его класть нельзя —
  // непрозрачный фон слайда накрывает весь экран и эмодзи не видно вовсе.
  var slide = document.querySelector('.slide-container.opacity-100');
  var layer = document.createElement('div');
  layer.style.cssText = 'position:absolute;inset:0;pointer-events:none;z-index:-1;overflow:hidden';
  slide.insertBefore(layer, slide.firstChild);
  if (getComputedStyle(slide).position === 'static') slide.style.position = 'relative';
  // Координаты элементов приходят в системе окна — переводим в систему слоя
  function originOf(){ var r = layer.getBoundingClientRect(); return { x: r.left, y: r.top }; }

  function findTarget(cue){
    var all = document.querySelectorAll('.slide-container.opacity-100 *');
    var best = null;
    for (var i = 0; i < all.length; i++){
      var el = all[i];
      var txt = (el.textContent || '').replace(/\s+/g, ' ').trim();
      if (txt !== cue.text) continue;
      if (!best || el.children.length < best.children.length) best = el;
    }
    if (!best) return null;
    for (var u = 0; u < (cue.up || 0); u++) best = best.parentElement || best;
    return best;
  }

  var targets = CUES.map(findTarget);
  var bases = targets.map(function(el){ return el ? el.getAttribute('style') || '' : ''; });
  // Собственный transform элемента (у карточек это md:scale-105 из вёрстки).
  // Эффекты дописывают свой scale ПОВЕРХ него, иначе карточка в момент вспышки
  // скачком «сдувается» к масштабу 1 — раньше из-за этого такие карточки
  // приходилось обходить стороной.
  var baseTf = targets.map(function(el){
    if (!el) return '';
    var t = getComputedStyle(el).transform;
    return (!t || t === 'none') ? '' : t + ' ';
  });
  // Галочка внутри пункта списка — её «ставит» эффект check.
  var marks = targets.map(function(el){
    return el ? el.querySelector('i, svg, span') : null;
  });
  var markBases = marks.map(function(el){ return el ? el.getAttribute('style') || '' : ''; });

  function clamp(v){ return v < 0 ? 0 : v > 1 ? 1 : v; }
  function easeOut(p){ return 1 - Math.pow(1 - clamp(p), 3); }
  // 0 → 1 → 0: элемент вспыхивает и мягко возвращается в исходное состояние
  function bump(p){ return (p <= 0 || p >= 1) ? 0 : Math.sin(Math.PI * clamp(p)); }

  // Полёт эмодзи живёт СВОИМ временем, а не длительностью подсветки. Реплики
  // «восприятие — мышление — действие» в живой речи идут через ~1.1 с, и пока
  // разлёт был привязан к cue.dur, монетки исчезали через полсекунды после
  // вылета. Теперь длительность полёта задаёт burst_dur (по умолчанию BDUR),
  // а подсветка карточки по-прежнему гаснет к следующей реплике.
  var BDUR = 1.8;
  function burst(cue, r, tau){
    var n = cue.n || 10, dur = cue.burst_dur || BDUR, o = originOf();
    for (var j = 0; j < n; j++){
      // Разлёт считается формулой от времени — значит кадр повторяем
      var lag = (j % 4) * 0.05;            // вылетают не строем, а россыпью
      var a = tau - lag;
      if (a <= 0) continue;
      var q = a / dur;
      if (q >= 1) continue;
      var ang = (Math.PI * (0.15 + 0.7 * (j / (n - 1)))) * -1;
      var sp = (260 + ((j * 37) % 120)) * SPREAD;
      // Путь замедляется к концу (1-(1-q)^2): эмодзи выстреливает и зависает,
      // а не улетает за край кадра равномерной пулей.
      var dist = sp * dur * 0.42 * (1 - Math.pow(1 - q, 2));
      // Стартуют у самой кромки карточки (0.42 от её размера — чуть внутри):
      // первые кадры эмодзи ещё спрятано за карточкой и сразу выходит из-за
      // края. С прежними 0.34/0.30 разлёт полсекунды полз внутри плашки.
      var x = r.left - o.x + r.width / 2 + Math.cos(ang) * (r.width * 0.42 + dist);
      var y = r.top - o.y + r.height / 2 + Math.sin(ang) * (r.height * 0.42 + dist)
              + 120 * dur * q * q;         // мягкая гравитация к концу полёта
      var born = clamp(a / 0.18);          // рождение: 0.4 → 1 за 0.18 с
      var fade = q < 0.62 ? 1 : 1 - (q - 0.62) / 0.38;
      var s = document.createElement('span');
      // burst может быть списком: тогда вылетает не один значок, а набор
      // (цифры для «цифровой революции» и т. п.).
      s.textContent = (cue.burst instanceof Array)
        ? cue.burst[j % cue.burst.length] : cue.burst;
      // Шрифт эмодзи задаём явно. Без него Chromium берёт текстовое начертание
      // из шрифта лекции: 👁 и ⚡ выходят чёрно-белыми контурами вместо цветных.
      s.style.cssText = 'position:absolute;left:' + x + 'px;top:' + y + 'px;'
        + 'font-family:"Noto Color Emoji","Apple Color Emoji","Segoe UI Emoji",sans-serif;'
        + 'font-size:' + (34 + (j % 3) * 10) + 'px;opacity:' + fade
        + ';transform:translate(-50%,-50%) scale(' + (0.4 + 0.6 * born)
        + ') rotate(' + ((j % 5 - 2) * 60 * q) + 'deg)';
      layer.appendChild(s);
    }
  }

  function apply(t){
    layer.innerHTML = '';
    // Сброс — ОТДЕЛЬНЫМ проходом по всем целям, до наложения подсветок. Пока
    // сброс жил в одном цикле с наложением, две реплики на один и тот же узел
    // (обычное дело: карточка берётся то напрямую, то через `up` от строки
    // внутри неё) гасили друг друга — поздняя стирала стиль ранней, и ранняя
    // вспышка не появлялась в кадре вообще.
    for (var r = 0; r < CUES.length; r++){
      if (targets[r]) targets[r].setAttribute('style', bases[r]);
      if (marks[r]) marks[r].setAttribute('style', markBases[r]);
    }
    // Геометрию снимаем на погашенном кадре: масштаб соседней подсветки не
    // должен смещать точку рождения эмодзи, иначе разлёт «дышит».
    var rects = targets.map(function(el){
      return el ? el.getBoundingClientRect() : null;
    });
    for (var i = 0; i < CUES.length; i++){
      var cue = CUES[i], el = targets[i];
      if (!el) continue;
      var tau = t - cue.at;
      if (cue.burst && tau > 0) burst(cue, rects[i], tau);
      var p = tau / (cue.dur || 2.5);
      if (p <= 0 || p >= 1) continue;
      var k = bump(p), color = cue.fx === 'glow-solar' ? SOLAR : VIOLET;
      var bt = baseTf[i];   // собственный масштаб карточки — эффект пишет поверх
      // Насколько подрастает элемент. Для слова внутри строки нужен почти
      // нулевой рост (правка владельца: «выделил, но не расширяй сильно») —
      // иначе оно наезжает на соседние слова. Задаётся полем grow в сценарии.
      var grow = (typeof cue.grow === 'number') ? cue.grow : 0.06;

      if (cue.fx === 'pop'){
        el.style.transform = bt + 'scale(' + (1 + (grow === 0.06 ? 0.05 : grow) * k) + ')';
        el.style.setProperty('filter', 'drop-shadow(0 0 ' + (26 * k)
          + 'px rgba(139,92,246,' + (0.8 * k) + '))', 'important');
      } else if (cue.fx === 'frame'){
        // Просто рамка: только оранжевый контур, без ореола и без всплеска
        // (правка владельца по «Ключевое отличие — автономность»). Рост почти
        // нулевой — плашка стоит в потоке, дёргать её незачем.
        el.style.transform = bt + 'scale(' + (1 + (cue.grow || 0.01) * k) + ')';
        el.style.outline = (3 * k) + 'px solid ' + SOLAR;
        el.style.outlineOffset = (3 * k) + 'px';
        el.style.borderRadius = getComputedStyle(el).borderRadius;
      } else if (cue.fx === 'underline'){
        el.style.transform = bt + 'scale(' + (1 + 0.04 * k) + ')';
        el.style.backgroundImage = 'linear-gradient(' + SOLAR + ',' + SOLAR + ')';
        el.style.backgroundRepeat = 'no-repeat';
        el.style.backgroundSize = (100 * easeOut(p * 2.2)) + '% 4px';
        el.style.backgroundPosition = '0 100%';
      } else if (cue.fx === 'rise'){
        // Всплытие: карточка приподнимается и подсвечивается снизу. Для рядов
        // одинаковых плиток читается лучше обводки — глаз ловит движение.
        el.style.transform = bt + 'translateY(' + (-14 * k) + 'px) scale('
          + (1 + grow * k) + ')';
        el.style.setProperty('box-shadow', '0 ' + (18 * k) + 'px ' + (44 * k)
          + 'px -' + (10 * k) + 'px rgba('
          + (color === SOLAR ? '249,115,22' : '139,92,246') + ','
          + (0.75 * k) + ')', 'important');
      } else if (cue.fx === 'zoom'){
        // Просто увеличение, без рамки и свечения (правка владельца: слова и
        // карточки, вокруг которых рамка не нужна, — «просто увеличить»).
        el.style.transform = bt + 'scale('
          + (1 + (typeof cue.grow === 'number' ? cue.grow : 0.09) * k) + ')';
      } else if (cue.fx === 'check'){
        // «Ставим галочку»: значок в пункте списка прорисовывается слева
        // направо, подрастает и вспыхивает оранжевым. Сам пункт чуть подаётся
        // вправо — как будто его только что отметили.
        var mark = marks[i];
        if (mark){
          mark.style.setProperty('clip-path',
            'inset(0 ' + (100 - 100 * easeOut(clamp(p / 0.45))) + '% 0 0)', 'important');
          mark.style.setProperty('transform', 'scale(' + (1 + 0.6 * k) + ')', 'important');
          mark.style.setProperty('color', SOLAR, 'important');
          mark.style.setProperty('filter', 'drop-shadow(0 0 ' + (16 * k)
            + 'px rgba(249,115,22,' + (0.9 * k) + '))', 'important');
        }
        el.style.transform = bt + 'translateX(' + (7 * k) + 'px)';
      } else if (cue.fx === 'fill'){
        // Заливка карточки снизу вверх: фиолетовое поле, на его фронте —
        // оранжевая полоска (правка владельца вместо эмодзи снизу).
        var h = 100 * easeOut(clamp(p / 0.6));
        var a = p < 0.72 ? 1 : 1 - (p - 0.72) / 0.28;
        var edge = h > 1.4 ? h - 1.4 : 0;
        el.style.setProperty('background-image',
          'linear-gradient(to top, rgba(139,92,246,' + (0.34 * a) + ') 0%,'
          + 'rgba(139,92,246,' + (0.34 * a) + ') ' + edge + '%,'
          + 'rgba(249,115,22,' + a + ') ' + edge + '%,'
          + 'rgba(249,115,22,' + a + ') ' + h + '%,'
          + 'rgba(0,0,0,0) ' + h + '%)', 'important');
        el.style.setProperty('background-repeat', 'no-repeat', 'important');
        el.style.setProperty('background-size', '100% 100%', 'important');
      } else if (cue.fx === 'none'){
        // Только всплеск эмодзи, элемент не трогаем (он служит якорем).
      } else {
        el.style.transform = bt + 'scale(' + (1 + grow * k) + ')';
        // ВАЖНО: в лекции живёт глобальное `*{box-shadow:none!important}`
        // (канон «теней нет нигде»). Без явного important свечение молча не
        // рисуется — в кадре остаётся одна обводка.
        el.style.setProperty('box-shadow', '0 0 ' + (60 * k) + 'px ' + (10 * k)
          + 'px rgba(' + (color === SOLAR ? '249,115,22' : '139,92,246') + ','
          + (0.55 * k) + ')', 'important');
        el.style.outline = (2.5 * k) + 'px solid ' + color;
        el.style.outlineOffset = ((cue.tight ? 1 : 4) * k) + 'px';
        el.style.borderRadius = getComputedStyle(el).borderRadius;
      }
      el.style.transformOrigin = 'center center';
    }
  }

  return { apply: apply,
           missing: CUES.filter(function(c, i){ return !targets[i]; }).map(function(c){ return c.text; }) };
})();
"""


def transcribe(clip, out_json, out_srt):
    """Клип → слова с таймингами + субтитры по 2 слова на реплику."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("нужен faster-whisper: pip install faster-whisper")
    model = WhisperModel(os.environ.get("WHISPER_MODEL", "medium"),
                         device="cpu", compute_type="int8")
    segments, _ = model.transcribe(clip, language="ru", word_timestamps=True,
                                   vad_filter=True)
    words = []
    for seg in segments:
        for w in (seg.words or []):
            words.append({"w": w.word.strip(), "s": round(w.start, 3),
                          "e": round(w.end, 3)})
    json.dump({"words": words}, open(out_json, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    def stamp(sec):
        ms = int(round(sec * 1000))
        return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60,
                                        ms // 1000 % 60, ms % 1000)

    with open(out_srt, "w", encoding="utf-8") as f:
        for n, i in enumerate(range(0, len(words), 2), 1):
            pair = words[i:i + 2]
            f.write("%d\n%s --> %s\n%s\n\n" % (
                n, stamp(pair[0]["s"]), stamp(pair[-1]["e"]),
                " ".join(p["w"] for p in pair)))
    print("  слов: %d · субтитров: %d" % (len(words), (len(words) + 1) // 2))
    return words


def cue_times(cues, words):
    """Время реплики = момент, когда прозвучало её слово. Нет тайминга или
    слово не нашлось — остаётся запасное `at` из сценария."""
    used = set()
    for cue in cues:
        key = (cue.get("word") or "").lower()
        if not key or not words:
            continue
        hint, hits = cue.get("at", 0.0), []
        for i, w in enumerate(words):
            if i in used:
                continue
            plain = re.sub(r"[^\w\-]", "", w["w"]).lower()
            # Точное слово принимаем любой длины, по корню — только от пяти
            # букв (в речи «агента», в сценарии «агент»: падежи не должны
            # ломать привязку). Короткий префикс брать нельзя: тире
            # схлопывается в пустую строку, а односимвольное «В» — префикс
            # чего угодно, и «восприятие» уезжало на «В» в середине фразы.
            n = min(len(key), len(plain))
            if plain == key or (n >= 5 and plain[:n] == key[:n]):
                hits.append((abs(w["s"] - hint), i, w["s"]))
        if hits:
            # Слово в речи может повторяться: берём то вхождение, что ближе
            # к ориентиру `at` из сценария, а не первое попавшееся.
            _, i, sec = min(hits)
            cue["at"] = sec
            cue["bound"] = True     # слово нашлось в речи (нужно проверке)
            used.add(i)
    # Эффект живёт до СЛЕДУЮЩЕЙ реплики, а не фиксированные секунды. На живой
    # речи «восприятие — мышление — действие» идут через 0.9 с: с жёсткими
    # тремя секундами все три горели бы разом и перечисление читалось бы кашей.
    order = sorted(cues, key=lambda c: c["at"])
    for i, cue in enumerate(order):
        gap = (order[i + 1]["at"] - cue["at"]) if i + 1 < len(order) else None
        if gap and gap > 0:
            cue["dur"] = max(0.8, min(cue.get("dur", 2.5), gap * 1.25))
    return cues


def render(slide, cues, secs, out_dir, vendor, allow_fallback, preview=0, at=None,
           cinema=False):
    from playwright.sync_api import sync_playwright

    frames, srv = [], serve()
    total_frames = int(round(secs * FPS))
    try:
        with sync_playwright() as pw:
            # Путь к браузеру задаём ЯВНО: у Playwright свой номер сборки, и
            # после его обновления автопоиск уходит в несуществующий каталог
            # (chromium_headless_shell-NNNN) — рендер молча падал на запуске,
            # а рядом лежал готовый /opt/pw-browsers/chromium.
            browser = pw.chromium.launch(
                executable_path=(os.environ.get("CHROMIUM_PATH")
                                 or "/opt/pw-browsers/chromium"),
                args=["--no-sandbox", "--hide-scrollbars"])
            # В режиме «кино» слайд снимается в узком вьюпорте — ровно в
            # ширину правой колонки. Портал-подгонка страницы сама вписывает
            # холст формы в это окно, поэтому колонка получается штатным
            # механизмом, без переопределения вёрстки слайдов.
            ctx = browser.new_context(
                viewport=(cinema_fx.viewport() if cinema
                          else {"width": W, "height": H}),
                device_scale_factor=1,
                reduced_motion="reduce")
            if vendor:
                ctx.route("**/*", vendor_route(vendor))
            page = ctx.new_page()
            page.goto("http://127.0.0.1:%d/automation/1/" % PORT,
                      wait_until="load", timeout=120000)
            page.wait_for_timeout(3000)
            page.add_style_tag(content=CHROME_OFF)
            if cinema:
                page.add_style_tag(content=cinema_fx.css())
            page.evaluate("() => document.querySelectorAll("
                          "'#start-overlay,#intro-overlay').forEach(e => e.remove())")
            check_font(page, allow_fallback)
            for _ in range(slide):
                page.evaluate("() => window.nextSlide && window.nextSlide()")
                page.wait_for_timeout(160)
            page.wait_for_timeout(1200)
            if cinema:
                # Догон масштаба — ПОСЛЕ подгонки страницы и ДО FX: движок
                # эффектов запоминает цели по тексту, а координаты берёт в
                # момент кадра, поэтому масштаб ему безразличен.
                grown = page.evaluate(cinema_fx.GROW_JS, cinema_fx.grow_args())
                if grown:
                    print("   колонка: ×%.2f → %.0f×%.0f из %d×%d"
                          % (grown["k"], grown["w"], grown["h"],
                             cinema_fx.PANE_W, H))

            page.evaluate(FX_JS.replace("__CUES__", json.dumps(cues, ensure_ascii=False))
                              .replace("__SPREAD__",
                                       str(cinema_fx.SPREAD) if cinema else "1"))
            missing = page.evaluate("() => window.__fx.missing")
            if missing:
                sys.exit("не нашёл на слайде элементы: %s\n"
                         "   Проверьте поле text в сценарии — оно должно совпадать\n"
                         "   с текстом элемента слайда дословно." % ", ".join(missing))

            if at:
                # Точечная проверка: кадр ровно на такой-то секунде речи. Нужна,
                # чтобы глазами убедиться, что конкретная реплика реально горит,
                # а не «должна гореть по сценарию».
                for sec in at:
                    page.evaluate("(t) => window.__fx.apply(t)", float(sec))
                    path = os.path.join(out_dir, "at-%06.2f.png" % float(sec))
                    page.screenshot(path=path, omit_background=cinema)
                    frames.append(path)
                    print("   кадр на %.2f с" % float(sec))
                ctx.close()
                browser.close()
                return frames

            step = max(1, total_frames // preview) if preview else 1
            for i in range(0, total_frames, step):
                page.evaluate("(t) => window.__fx.apply(t)", i / float(FPS))
                path = os.path.join(out_dir, "f-%05d.png" % i)
                page.screenshot(path=path, omit_background=cinema)
                frames.append(path)
                if i % (FPS * 5) == 0:
                    print("   кадр %d/%d" % (i, total_frames))
            ctx.close()
            browser.close()
    finally:
        srv.shutdown()
    return frames


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lecture", type=int, default=1)
    ap.add_argument("--slide", type=int, default=5, help="номер слайда, с 1")
    ap.add_argument("--transcribe", action="store_true",
                    help="сначала распознать речь клипа (нужен интернет)")
    ap.add_argument("--preview", type=int, default=0,
                    help="снять N контрольных кадров вместо видео")
    ap.add_argument("--at", help="секунды через запятую: снять кадры ровно на "
                                 "этих отметках (проверка конкретных реплик)")
    ap.add_argument("--clip", help="взять свой файл головы вместо клипа из "
                                   "лекции (проверка раскладки на другом "
                                   "исходнике)")
    ap.add_argument("--seconds", type=float,
                    help="ограничить длительность (по умолчанию — clip_seconds "
                         "сценария, если задан --clip, иначе длина клипа)")
    ap.add_argument("--cinema", action="store_true",
                    help="видео слева живьём, слайд справа, тёмный фон "
                         "(вместо кружка в углу) — см. tools/cinema.py")
    ap.add_argument("--reuse-frames", action="store_true",
                    help="не снимать кадры заново, собрать видео из уже "
                         "готовых build/fxframes/<тег> — правка сборки "
                         "(маски, порядок слоёв, длительность) не стоит "
                         "четверти часа съёмки")
    ap.add_argument("--vendor")
    ap.add_argument("--allow-fallback-fonts", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()

    idx = args.slide - 1
    tag = "lecture%d-slide%02d" % (args.lecture, args.slide)
    ff = ffmpeg_bin()
    for d in ("timings", "fxframes", "head-clips"):
        os.makedirs(os.path.join(BUILD, d), exist_ok=True)
    frames_dir = os.path.join(BUILD, "fxframes", tag)
    os.makedirs(frames_dir, exist_ok=True)
    if args.reuse_frames:
        have = len([f for f in os.listdir(frames_dir) if f.endswith(".png")])
        if not have:
            sys.exit("--reuse-frames: в %s нет кадров" % frames_dir)
        print("кадры не снимаю — беру готовые (%d шт.)" % have)
    else:
        for old in os.listdir(frames_dir):
            os.remove(os.path.join(frames_dir, old))

    scen_path = os.path.join(FX_DIR, tag + ".json")
    if not os.path.exists(scen_path):
        sys.exit("нет сценария %s — заведите его по образцу lecture1-slide05.json" % scen_path)
    scen = json.load(open(scen_path, encoding="utf-8"))
    cues = [c for c in scen["cues"]]

    clips = head_clips(args.lecture)
    clip = None
    if idx < len(clips):
        name = urllib.parse.unquote(os.path.basename(urllib.parse.urlparse(clips[idx]).path))
        dst = os.path.join(BUILD, "head-clips", "%03d-%s" % (idx, name))
        try:
            clip = fetch(clips[idx], dst)
        except Exception as e:
            print("клип не скачался (%s) — видео будет без звука и головы" % e)

    if args.clip:
        clip = args.clip
    if args.cinema and clip:
        # Геометрию панели считаем ДО съёмки кадров: от ширины панели зависит
        # ширина колонки, а значит и вьюпорт, в котором снимается слайд.
        sw, sh = cinema_fx.probe_size(ff, clip)
        print("клип %dx%d · %s" % (sw, sh, cinema_fx.configure(sw, sh)))

    secs = (duration(ff, clip) if clip else None) or scen.get("clip_seconds", 30.0)
    if args.clip:
        # Свой файл — это обычно целый сегмент записи, а не нарезка под слайд.
        # Длительность берём из сценария, иначе рендер уходит на все 2:45
        # исходника, а реплики FX кончаются на 50-й секунде.
        secs = float(args.seconds or scen.get("clip_seconds", secs))
    elif args.seconds:
        secs = float(args.seconds)

    tj = os.path.join(BUILD, "timings", tag + ".json")
    if args.transcribe and clip:
        print("1/3 · распознаю речь")
        words = transcribe(clip, tj, os.path.join(BUILD, "timings", tag + ".srt"))
    elif os.path.exists(tj):
        words = json.load(open(tj, encoding="utf-8"))["words"]
        print("1/3 · тайминг слов взят из %s" % os.path.relpath(tj, ROOT))
    else:
        words = []
        print("1/3 · тайминга слов нет — реплики идут по полю at из сценария")
    cues = cue_times(cues, words)

    at = [float(x) for x in args.at.split(",")] if args.at else None
    if args.reuse_frames:
        print("2/3 · кадры готовы (%.1f с × %d fps)" % (secs, FPS))
    else:
        print("2/3 · кадры (%.1f с × %d fps)" % (secs, FPS))
        render(idx, cues, secs, frames_dir, args.vendor,
               args.allow_fallback_fonts, preview=args.preview, at=at,
               cinema=args.cinema)
        if args.preview or at:
            print("\nконтрольные кадры: %s" % frames_dir)
            return

    print("3/3 · сборка")
    out = args.out or os.path.join(BUILD, tag + ".mp4")
    seq = os.path.join(frames_dir, "f-%05d.png")

    if args.cinema:
        # Кино: подложка + колонка слайда справа + живое видео слева, правый
        # край которого растворяется маской-градиентом.
        if not clip:
            sys.exit("режим «кино» без клипа бессмыслен — левая панель пуста")
        mask = os.path.join(BUILD, "cinema-mask.png")
        cinema_fx.fade_mask(mask)
        bg = os.path.join(BUILD, "cinema-bg.png")
        cinema_fx.dark_canvas(ff, bg)
        sw, sh = cinema_fx.probe_size(ff, clip)
        # Исходник ниже панели — добираем высоту размытой копией кадра, а стык
        # растушёвываем отдельной маской (её размер знает pane_fill_height).
        fill_h = cinema_fx.pane_fill_height(sw, sh)
        extra, feather = [], None
        if fill_h:
            soft = os.path.join(BUILD, "cinema-feather.png")
            cinema_fx.feather_mask(soft, cinema_fx.VIDEO_W, fill_h)
            extra = ["-i", soft]
            feather = "4:v"
        graph = cinema_fx.pane_graph(sw, sh, src="2:v", feather=feather)
        print("   исходник %dx%d · панель %dx%d%s"
              % (sw, sh, cinema_fx.VIDEO_W, cinema_fx.VIDEO_H,
                 " (высоту добираем размытым фоном)" if fill_h else ""))
        vf = cinema_fx.overlay_filter(bg_stream="0:v", clip_stream="2:v",
                                      mask_stream="3:v", pane_stream="1:v",
                                      graph=graph)
        run([ff, "-y", "-loglevel", "error",
             "-loop", "1", "-framerate", str(FPS), "-i", bg,
             "-framerate", str(FPS), "-i", seq,
             "-i", clip, "-i", mask] + extra + ["-filter_complex", vf,
             "-map", "[v]", "-map", "2:a?",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             # -t обязателен: подложка идёт «-loop 1», то есть бесконечна, и
             # -shortest меряет длину по звуку клипа. С полным сегментом записи
             # (2:45) файл выходил втрое длиннее слайда: картинка замирала на
             # последнем кадре, а речь всё шла.
             "-t", "%.3f" % secs,
             "-shortest", "-movflags", "+faststart", out])
        print("\nГотово (кино): %s\n  %s · %.0f МБ\n  %s"
              % (out, timecode(secs), os.path.getsize(out) / 1024 / 1024,
                 cinema_fx.geometry()))
        return

    diameter = int(W * BUB_D) // 2 * 2
    margin = int(W * BUB_MARGIN)
    mask = os.path.join(BUILD, "circle-mask.png")
    circle_mask(mask, diameter)
    if clip:
        vf = ("[1:v]scale=%d:%d,setsar=1[hv];[hv][2:v]alphamerge[circ];"
              "[0:v][circ]overlay=W-w-%d:H-h-%d:format=auto[v]"
              % (diameter, diameter, margin, margin))
        run([ff, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", seq,
             "-i", clip, "-i", mask, "-filter_complex", vf,
             "-map", "[v]", "-map", "1:a?",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             "-shortest", "-movflags", "+faststart", out])
    else:
        run([ff, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", seq,
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", out])
    print("\nГотово: %s\n  %s · %.0f МБ"
          % (out, timecode(secs), os.path.getsize(out) / 1024 / 1024))


if __name__ == "__main__":
    main()
