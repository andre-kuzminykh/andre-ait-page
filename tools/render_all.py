#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Рендер всей лекции: слайд за слайдом и одним файлом.

Каждый слайд считает `animate_slide.py` (кадры → mp4 с кружком головы и
звуком). Тут — очередь: клипы скачиваются заранее, слайды идут в несколько
потоков (у каждого свой порт локального сервера), кадры после сборки
удаляются — иначе 42 слайда съедают под двадцать гигабайт. В конце всё
склеивается в один файл без перекодирования.

    python3 tools/render_all.py --vendor <каталог>          # всё
    python3 tools/render_all.py --slides 5,6,7              # выборочно
    python3 tools/render_all.py --only-missing --jobs 3     # добить незаконченное
    python3 tools/render_all.py --join-only                 # только склейка
"""
import argparse
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from record_lecture import ROOT, ffmpeg_bin, head_clips, fetch, duration, timecode

BUILD = os.path.join(ROOT, "build")
FX_DIR = os.path.join(ROOT, "tools/fx")
TOOL = os.path.join(ROOT, "tools/animate_slide.py")


def have_scenario(lecture, n):
    return os.path.exists(os.path.join(
        FX_DIR, "lecture%d-slide%02d.json" % (lecture, n)))


def out_path(lecture, n):
    return os.path.join(BUILD, "lecture%d-slide%02d.mp4" % (lecture, n))


def prefetch(lecture, slides):
    """Клипы качаем заранее и по одному: параллельные рендеры иначе полезут
    за одним и тем же файлом и подерутся за .part."""
    clips = head_clips(lecture)
    os.makedirs(os.path.join(BUILD, "head-clips"), exist_ok=True)
    for n in slides:
        i = n - 1
        if i >= len(clips):
            continue
        name = urllib.parse.unquote(
            os.path.basename(urllib.parse.urlparse(clips[i]).path))
        dst = os.path.join(BUILD, "head-clips", "%03d-%s" % (i, name))
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            continue
        print("   клип слайда %d" % n, flush=True)
        try:
            fetch(clips[i], dst)
        except Exception as e:
            print("   ! клип слайда %d не скачался: %s" % (n, e))


def render(lecture, n, port, vendor, allow_fallback):
    env = dict(os.environ, LECTURE_PORT=str(port))
    cmd = [sys.executable, TOOL, "--lecture", str(lecture), "--slide", str(n),
           "--out", out_path(lecture, n)]
    if vendor:
        cmd += ["--vendor", vendor]
    if allow_fallback:
        cmd += ["--allow-fallback-fonts"]
    log = os.path.join(BUILD, "render-logs", "slide%02d.log" % n)
    os.makedirs(os.path.dirname(log), exist_ok=True)
    with open(log, "w", encoding="utf-8") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    frames = os.path.join(BUILD, "fxframes", "lecture%d-slide%02d" % (lecture, n))
    if r.returncode == 0 and os.path.isdir(frames):
        shutil.rmtree(frames, ignore_errors=True)   # кадры больше не нужны
    return r.returncode, log


def join(lecture, slides, out):
    """Склейка без перекодирования: у всех кусков одинаковые параметры."""
    ff = ffmpeg_bin()
    parts = [out_path(lecture, n) for n in slides
             if os.path.exists(out_path(lecture, n))]
    if not parts:
        sys.exit("склеивать нечего")
    lst = os.path.join(BUILD, "lecture%d-parts.txt" % lecture)
    with open(lst, "w", encoding="utf-8") as f:
        for p in parts:
            f.write("file '%s'\n" % p.replace("'", "'\\''"))
    subprocess.run([ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", "-movflags", "+faststart", out],
                   check=True)
    secs = duration(ff, out) or 0
    print("\nЛекция целиком: %s\n  %s · %.0f МБ · частей %d"
          % (out, timecode(secs), os.path.getsize(out) / 1024 / 1024, len(parts)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lecture", type=int, default=1)
    ap.add_argument("--slides", help="номера через запятую (по умолчанию все со сценарием)")
    ap.add_argument("--jobs", type=int, default=2, help="сколько слайдов одновременно")
    ap.add_argument("--vendor")
    ap.add_argument("--allow-fallback-fonts", action="store_true")
    ap.add_argument("--only-missing", action="store_true",
                    help="пропустить слайды, у которых mp4 уже собран")
    ap.add_argument("--join-only", action="store_true", help="только склейка")
    ap.add_argument("--no-join", action="store_true", help="без склейки")
    ap.add_argument("--out")
    args = ap.parse_args()

    total = len(head_clips(args.lecture)) or 42
    slides = ([int(x) for x in args.slides.split(",")] if args.slides
              else [n for n in range(1, total + 1)
                    if have_scenario(args.lecture, n)])
    if not slides:
        sys.exit("нет ни одного сценария в tools/fx — сначала заведите их")
    out = args.out or os.path.join(BUILD, "lecture%d-full.mp4" % args.lecture)

    if args.join_only:
        return join(args.lecture, slides, out)

    todo = [n for n in slides
            if not (args.only_missing and os.path.exists(out_path(args.lecture, n)))]
    print("слайдов к рендеру: %d (потоков %d)" % (len(todo), args.jobs))
    print("1/3 · клипы")
    prefetch(args.lecture, todo)

    print("2/3 · кадры и сборка по слайдам")
    q, fails, lock = queue.Queue(), [], threading.Lock()
    for n in todo:
        q.put(n)
    started = time.time()

    def worker(slot):
        while True:
            try:
                n = q.get_nowait()
            except queue.Empty:
                return
            t0 = time.time()
            code, log = render(args.lecture, n, 8400 + slot, args.vendor,
                               args.allow_fallback_fonts)
            with lock:
                if code:
                    fails.append(n)
                    print("   ✗ слайд %2d — см. %s"
                          % (n, os.path.relpath(log, ROOT)), flush=True)
                else:
                    print("   ✓ слайд %2d · %.0f с · осталось %d"
                          % (n, time.time() - t0, q.qsize()), flush=True)

    threads = [threading.Thread(target=worker, args=(i,), daemon=True)
               for i in range(max(1, args.jobs))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print("\nготово за %s, ошибок %d" % (timecode(time.time() - started), len(fails)))
    if fails:
        print("не собрались слайды: %s" % ", ".join(map(str, sorted(fails))))
    if not args.no_join:
        print("3/3 · склейка")
        join(args.lecture, slides, out)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
