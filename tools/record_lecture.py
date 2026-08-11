# -*- coding: utf-8 -*-
"""Экспорт лекции в видео Full HD (1920×1080) для YouTube.

Собирает готовый mp4 из того же, что уже лежит на сайте, — второй раз ничего
записывать руками не нужно:

  * кадр каждого слайда снимает headless-Chromium в 1920×1080 и «чисто»: без
    стрелок листания, шапки, полосы прогресса и стартового оверлея — на кадре
    остаются только контент слайда и кружок с говорящей головой;
  * сам кружок дорисовывает ffmpeg из тех же клипов, что играют на странице
    (по клипу на слайд, ветка media). В браузере его снимать нельзя: headless
    Chromium без проприетарных кодеков показал бы вместо головы постер;
  * длительность слайда = длительность его клипа, звук берётся оттуда же, так
    что картинка идёт ровно за озвучкой, без ручной подгонки тайминга;
  * рядом кладётся chapters.txt с тайм-кодами и заголовками слайдов —
    вставляется в описание ролика и YouTube делает главы.

Требуется playwright (chromium) и ffmpeg. Если ffmpeg не стоит в системе,
берётся тот, что приезжает с пакетом imageio-ffmpeg.

    python3 tools/record_lecture.py                      # вся лекция 1
    python3 tools/record_lecture.py --slides 1-5         # только часть
    python3 tools/record_lecture.py --lecture 2          # другая лекция
    python3 tools/record_lecture.py --no-head            # без кружка и звука
    python3 tools/record_lecture.py --out ~/lection1.mp4

Кэш клипов лежит в build/head-clips — второй прогон уже ничего не качает.
"""
import argparse
import functools
import http.server
import json
import os
import re
import shutil
import socketserver
import subprocess
import sys
import threading
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8321
W, H = 1920, 1080
FPS = 30

# Кружок с головой: диаметр и отступы от правого нижнего угла кадра. Проценты
# от ширины кадра, а не пиксели, — чтобы при смене разрешения ничего не поехало.
BUB_D = 0.148          # 284px при 1920 — как кружок на самой странице
BUB_MARGIN = 0.021     # 40px

CHROME_OFF = """
/* Экспорт в видео: на кадре только контент слайда (правка владельца —
   «чтобы стрелочек не было, чисто кружок и текст»). Кружок дорисовывает
   ffmpeg настоящим клипом, поэтому и он тут скрыт. */
#lecture-header, .nav-arrow, #progress-container, #start-overlay,
#intro-overlay, #video-bubble, #notes-panel { display: none !important; }
html, body { overflow: hidden !important; }
"""


# ── ffmpeg ────────────────────────────────────────────────────────────────

def ffmpeg_bin():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit("нужен ffmpeg: поставьте его или `pip install imageio-ffmpeg`")


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode:
        sys.stdout.write(p.stdout.decode("utf-8", "ignore")[-4000:])
        sys.exit("ffmpeg вернул %d" % p.returncode)
    return p.stdout.decode("utf-8", "ignore")


def duration(ff, path):
    """Длительность файла — по выводу самого ffmpeg, чтобы не тянуть ffprobe."""
    out = subprocess.run([ff, "-hide_banner", "-i", path],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                         ).stdout.decode("utf-8", "ignore")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    if not m:
        return None
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


# ── исходники ─────────────────────────────────────────────────────────────

def head_clips(lecture):
    """Ссылки на клипы говорящей головы — читаем из самой лекции, чтобы список
    не разъезжался с сайтом."""
    path = os.path.join(ROOT, "automation/%d/index.html" % lecture)
    if not os.path.exists(path):
        sys.exit("лекции %d нет в репозитории (модуль закрыт?)" % lecture)
    html = open(path, encoding="utf-8").read()
    m = re.search(r"const videoIds = \[(.*?)\];", html, re.S)
    return re.findall(r"'([^']+)'", m.group(1)) if m else []


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return dest
    tmp = dest + ".part"
    with urllib.request.urlopen(url, timeout=180) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f)
    os.replace(tmp, dest)
    return dest


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)

    class Quiet(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

        def handle_error(self, *a):
            pass

    srv = Quiet(("127.0.0.1", PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


# ── съёмка слайдов ────────────────────────────────────────────────────────

def shoot(lecture, indexes, out_dir, vendor=None, scale=1):
    from playwright.sync_api import sync_playwright

    titles, srv = {}, serve()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                executable_path=os.environ.get("CHROMIUM_PATH") or None,
                args=["--no-sandbox", "--force-device-scale-factor=1",
                      "--hide-scrollbars"])
            ctx = browser.new_context(
                viewport={"width": W // scale, "height": H // scale},
                device_scale_factor=scale, reduced_motion="reduce")
            if vendor:
                ctx.route("**/*", vendor_route(vendor))
            page = ctx.new_page()
            page.goto("http://127.0.0.1:%d/automation/%d/" % (PORT, lecture),
                      wait_until="load", timeout=120000)
            page.wait_for_timeout(3000)
            page.add_style_tag(content=CHROME_OFF)
            page.evaluate("() => document.querySelectorAll("
                          "'#start-overlay,#intro-overlay').forEach(e => e.remove())")
            page.wait_for_timeout(500)

            total = page.evaluate(
                "() => document.querySelectorAll('.slide-container').length")
            for i in range(total):
                if i in indexes:
                    page.wait_for_timeout(900)      # даём доиграть каскаду появления
                    titles[i] = page.evaluate("""() => {
                        const s = document.querySelector('.slide-container.opacity-100');
                        const h = s && s.querySelector('h1,h2,h3');
                        return h ? h.innerText.replace(/\\s+/g, ' ').trim() : '';
                    }""")
                    page.screenshot(path=os.path.join(out_dir, "slide-%03d.png" % i))
                    print("  кадр %d/%d — %s" % (i + 1, total, titles[i][:48]))
                if i < total - 1:
                    page.evaluate("() => window.nextSlide && window.nextSlide()")
                    page.wait_for_timeout(160)
            ctx.close()
            browser.close()
    finally:
        srv.shutdown()
    return titles


def vendor_route(vendor):
    """Офлайн-прогон: внешние CDN подменяются файлами из каталога --vendor.
    На машине с интернетом флаг не нужен — страница возьмёт всё сама."""
    types = {".css": "text/css", ".js": "application/javascript",
             ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf",
             ".svg": "image/svg+xml", ".png": "image/png"}

    def handler(route):
        url = route.request.url
        for host, subs in (("unpkg.com/@phosphor-icons/web@2.1.1/",
                            ("phosphor", "phosphor-icons-web-2.1.1")),
                           ("font-awesome/6.4.0/", ("fa",))):
            if host in url:
                rel = url.split(host, 1)[1].split("?")[0]
                for sub in subs:                       # каталог зовут по-разному
                    path = os.path.join(vendor, sub, rel)
                    if os.path.isfile(path):
                        return route.fulfill(
                            status=200, body=open(path, "rb").read(),
                            content_type=types.get(os.path.splitext(path)[1],
                                                   "application/octet-stream"))
                return route.fulfill(status=404, body=b"")
        if url.split("/")[2] in ("unpkg.com", "cdnjs.cloudflare.com",
                                 "i.ibb.co", "cdn.jsdelivr.net"):
            return route.abort()
        return route.continue_()

    return handler


# ── сборка ────────────────────────────────────────────────────────────────

def circle_mask(path, size):
    """Альфа-маска кружка: ffmpeg вырежет ею голову из квадратного клипа."""
    from PIL import Image, ImageDraw
    img = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(img).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    img.resize((size, size), Image.LANCZOS).save(path)


def segment(ff, png, clip, mask, dst, secs, diameter, margin):
    """Один слайд: неподвижный кадр + кружок с головой + её звук."""
    if clip:
        vf = ("[1:v]scale=%d:%d,setsar=1[hv];"
              "[hv][2:v]alphamerge[circ];"
              "[0:v][circ]overlay=W-w-%d:H-h-%d:format=auto[v]"
              % (diameter, diameter, margin, margin))
        run([ff, "-y", "-loglevel", "error",
             "-loop", "1", "-framerate", str(FPS), "-t", "%.3f" % secs, "-i", png,
             "-i", clip, "-i", mask,
             "-filter_complex", vf, "-map", "[v]", "-map", "1:a?",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             "-shortest", "-movflags", "+faststart", dst])
    else:
        run([ff, "-y", "-loglevel", "error",
             "-loop", "1", "-framerate", str(FPS), "-t", "%.3f" % secs, "-i", png,
             "-f", "lavfi", "-t", "%.3f" % secs,
             "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", dst])


def timecode(sec):
    return "%d:%02d:%02d" % (int(sec) // 3600, int(sec) // 60 % 60, int(sec) % 60)


def parse_slides(spec, total):
    if not spec:
        return list(range(total))
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a) - 1, int(b)))
        else:
            out.append(int(part) - 1)
    return [i for i in out if 0 <= i < total]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lecture", type=int, default=1, help="номер лекции")
    ap.add_argument("--slides", help="какие слайды: 1-5 или 1,4,7 (по умолчанию все)")
    ap.add_argument("--out", default=os.path.join(ROOT, "build/lecture-1-fullhd.mp4"))
    ap.add_argument("--no-head", action="store_true",
                    help="без кружка с головой и без звука")
    ap.add_argument("--sec", type=float, default=8.0,
                    help="секунд на слайд, когда звука нет (--no-head)")
    ap.add_argument("--vendor", help="каталог с офлайн-копиями CDN (для прогона без интернета)")
    ap.add_argument("--supersample", type=int, default=1, choices=(1, 2),
                    help="2 — снимать в двойном разрешении (чётче мелкий текст)")
    args = ap.parse_args()

    ff = ffmpeg_bin()
    build = os.path.join(ROOT, "build")
    frames, clips_dir, segs = (os.path.join(build, d)
                               for d in ("frames", "head-clips", "segments"))
    for d in (build, frames, clips_dir, segs):
        os.makedirs(d, exist_ok=True)

    clips = [] if args.no_head else head_clips(args.lecture)
    total = 42
    path = os.path.join(ROOT, "automation/%d/index.html" % args.lecture)
    total = open(path, encoding="utf-8").read().count('class="slide-container')
    indexes = parse_slides(args.slides, total)
    print("Лекция %d: слайдов %d, снимаем %d" % (args.lecture, total, len(indexes)))

    print("1/4 · кадры слайдов %dx%d" % (W, H))
    titles = shoot(args.lecture, set(indexes), frames,
                   vendor=args.vendor, scale=args.supersample)

    print("2/4 · клипы говорящей головы")
    local, secs = {}, {}
    for i in indexes:
        if i < len(clips):
            name = os.path.basename(urllib.parse.urlparse(clips[i]).path)
            name = urllib.parse.unquote(name)
            dst = os.path.join(clips_dir, "%03d-%s" % (i, name))
            try:
                fetch(clips[i], dst)
                local[i] = dst
                secs[i] = duration(ff, dst) or args.sec
            except Exception as e:                     # нет сети — слайд молча идёт без головы
                print("   слайд %d: клип не скачался (%s)" % (i + 1, e))
                secs[i] = args.sec
        else:
            secs[i] = args.sec

    diameter = int(W * BUB_D) // 2 * 2
    margin = int(W * BUB_MARGIN)
    mask = os.path.join(build, "circle-mask.png")
    circle_mask(mask, diameter)

    print("3/4 · сборка сегментов")
    listing, chapters, clock = os.path.join(build, "segments.txt"), [], 0.0
    with open(listing, "w", encoding="utf-8") as lst:
        for n, i in enumerate(indexes, 1):
            png = os.path.join(frames, "slide-%03d.png" % i)
            dst = os.path.join(segs, "seg-%03d.mp4" % i)
            segment(ff, png, local.get(i), mask, dst, secs[i], diameter, margin)
            lst.write("file '%s'\n" % dst.replace("'", r"'\''"))
            chapters.append("%s %s" % (timecode(clock),
                                       titles.get(i) or "Слайд %d" % (i + 1)))
            clock += secs[i]
            print("  %d/%d · %.1f с" % (n, len(indexes), secs[i]))

    print("4/4 · склейка")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    run([ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", listing, "-c", "copy", "-movflags", "+faststart", args.out])

    chap_path = os.path.splitext(args.out)[0] + ".chapters.txt"
    with open(chap_path, "w", encoding="utf-8") as f:
        f.write("\n".join(chapters) + "\n")

    size = os.path.getsize(args.out) / 1024 / 1024
    print("\nГотово: %s\n  %s · %.0f МБ · %dx%d · %d fps"
          % (args.out, timecode(clock), size, W, H, FPS))
    print("  главы для описания на YouTube: %s" % chap_path)


if __name__ == "__main__":
    main()
