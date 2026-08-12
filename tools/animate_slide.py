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

  // Слой для эмодзи — fixed, чтобы координаты совпадали с getBoundingClientRect
  var layer = document.createElement('div');
  layer.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:9999;overflow:hidden';
  document.body.appendChild(layer);

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

  function clamp(v){ return v < 0 ? 0 : v > 1 ? 1 : v; }
  function easeOut(p){ return 1 - Math.pow(1 - clamp(p), 3); }
  // 0 → 1 → 0: элемент вспыхивает и мягко возвращается в исходное состояние
  function bump(p){ return (p <= 0 || p >= 1) ? 0 : Math.sin(Math.PI * clamp(p)); }

  function apply(t){
    layer.innerHTML = '';
    for (var i = 0; i < CUES.length; i++){
      var cue = CUES[i], el = targets[i];
      if (!el) continue;
      el.setAttribute('style', bases[i]);
      var p = (t - cue.at) / (cue.dur || 2.5);
      if (p <= 0 || p >= 1) continue;
      var k = bump(p), color = cue.fx === 'glow-solar' ? SOLAR : VIOLET;

      if (cue.fx === 'pop'){
        el.style.transform = 'scale(' + (1 + 0.05 * k) + ')';
        el.style.filter = 'drop-shadow(0 0 ' + (26 * k) + 'px rgba(139,92,246,' + (0.8 * k) + '))';
      } else if (cue.fx === 'underline'){
        el.style.transform = 'scale(' + (1 + 0.04 * k) + ')';
        el.style.backgroundImage = 'linear-gradient(' + SOLAR + ',' + SOLAR + ')';
        el.style.backgroundRepeat = 'no-repeat';
        el.style.backgroundSize = (100 * easeOut(p * 2.2)) + '% 4px';
        el.style.backgroundPosition = '0 100%';
      } else {
        el.style.transform = 'scale(' + (1 + 0.06 * k) + ')';
        el.style.boxShadow = '0 0 ' + (60 * k) + 'px ' + (10 * k) + 'px rgba('
          + (color === SOLAR ? '249,115,22' : '139,92,246') + ',' + (0.55 * k) + ')';
        el.style.outline = (2.5 * k) + 'px solid ' + color;
        el.style.outlineOffset = (4 * k) + 'px';
        el.style.borderRadius = getComputedStyle(el).borderRadius;
      }
      el.style.transformOrigin = 'center center';

      if (cue.burst){
        var r = el.getBoundingClientRect(), n = cue.n || 10, tau = t - cue.at;
        for (var j = 0; j < n; j++){
          // Разлёт считается формулой от времени — значит кадр повторяем
          var ang = (Math.PI * (0.15 + 0.7 * (j / (n - 1)))) * -1;
          var sp = 260 + ((j * 37) % 120);
          var x = r.left + r.width / 2 + Math.cos(ang) * sp * tau;
          var y = r.top + r.height / 2 + Math.sin(ang) * sp * tau + 420 * tau * tau;
          var life = clamp(tau / (cue.dur * 0.75));
          if (life >= 1) continue;
          var s = document.createElement('span');
          s.textContent = cue.burst;
          s.style.cssText = 'position:absolute;left:' + x + 'px;top:' + y + 'px;'
            + 'font-size:' + (30 + (j % 3) * 10) + 'px;opacity:' + (1 - life)
            + ';transform:translate(-50%,-50%) rotate(' + (j * 47 * tau) + 'deg)';
          layer.appendChild(s);
        }
      }
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
        for i, w in enumerate(words):
            if i in used:
                continue
            if key in re.sub(r"[^\w\-]", "", w["w"]).lower():
                cue["at"] = w["s"]
                used.add(i)
                break
    return cues


def render(slide, cues, secs, out_dir, vendor, allow_fallback, preview=0):
    from playwright.sync_api import sync_playwright

    frames, srv = [], serve()
    total_frames = int(round(secs * FPS))
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                executable_path=os.environ.get("CHROMIUM_PATH") or None,
                args=["--no-sandbox", "--hide-scrollbars"])
            ctx = browser.new_context(viewport={"width": W, "height": H},
                                      device_scale_factor=1,
                                      reduced_motion="reduce")
            if vendor:
                ctx.route("**/*", vendor_route(vendor))
            page = ctx.new_page()
            page.goto("http://127.0.0.1:%d/automation/1/" % PORT,
                      wait_until="load", timeout=120000)
            page.wait_for_timeout(3000)
            page.add_style_tag(content=CHROME_OFF)
            page.evaluate("() => document.querySelectorAll("
                          "'#start-overlay,#intro-overlay').forEach(e => e.remove())")
            check_font(page, allow_fallback)
            for _ in range(slide):
                page.evaluate("() => window.nextSlide && window.nextSlide()")
                page.wait_for_timeout(160)
            page.wait_for_timeout(1200)

            page.evaluate(FX_JS.replace("__CUES__", json.dumps(cues, ensure_ascii=False)))
            missing = page.evaluate("() => window.__fx.missing")
            if missing:
                sys.exit("не нашёл на слайде элементы: %s\n"
                         "   Проверьте поле text в сценарии — оно должно совпадать\n"
                         "   с текстом элемента слайда дословно." % ", ".join(missing))

            step = max(1, total_frames // preview) if preview else 1
            for i in range(0, total_frames, step):
                page.evaluate("(t) => window.__fx.apply(t)", i / float(FPS))
                path = os.path.join(out_dir, "f-%05d.png" % i)
                page.screenshot(path=path)
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

    secs = (duration(ff, clip) if clip else None) or scen.get("clip_seconds", 30.0)

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

    print("2/3 · кадры (%.1f с × %d fps)" % (secs, FPS))
    render(idx, cues, secs, frames_dir, args.vendor,
           args.allow_fallback_fonts, preview=args.preview)
    if args.preview:
        print("\nконтрольные кадры: %s" % frames_dir)
        return

    print("3/3 · сборка")
    out = args.out or os.path.join(BUILD, tag + ".mp4")
    diameter = int(W * BUB_D) // 2 * 2
    margin = int(W * BUB_MARGIN)
    mask = os.path.join(BUILD, "circle-mask.png")
    circle_mask(mask, diameter)
    seq = os.path.join(frames_dir, "f-%05d.png")
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
