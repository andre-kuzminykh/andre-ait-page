# -*- coding: utf-8 -*-
"""Субтитры лекции: клипы говорящей головы → слова с таймингами → SRT.

Один прогон делает всё сразу для всех слайдов лекции:

  build/timings/lecture1-slideNN.json  — слова со start/end (их ест анимация)
  build/timings/lecture1-slideNN.srt   — субтитры слайда, по 2 слова на реплику
  build/timings/lecture1-full.srt      — субтитры ВСЕЙ лекции на сквозной шкале
  build/timings/lecture1-full.txt      — сплошной текст (в описание ролика)

Сквозная шкала важна: в итоговом ролике слайды идут подряд, поэтому реплики
каждого следующего клипа сдвигаются на сумму длительностей предыдущих. Без
этого субтитры совпали бы только с первым слайдом.

Движок распознавания:
  * openai (по умолчанию) — /v1/audio/transcriptions, модель whisper-1,
    обязательно response_format=verbose_json и timestamp_granularities[]=word:
    без них вернётся сплошной текст без пословных меток, и привязывать
    эффекты будет не к чему;
  * local — faster-whisper на своей машине, без сети наружу.

Ключ искать не нужно, инструмент ищет сам — по порядку:
  1. переменные OPENAI_API_KEY / LLM_API_KEY;
  2. .env рядом с проектом и в домашнем каталоге;
  3. окружение systemd-юнитов проекта (andre-ai-web, andre-ai-test, andre-ai-dev).
Сам ключ никуда не печатается — только откуда он взят.

    python3 tools/subtitles.py                    # вся лекция 1 через OpenAI
    python3 tools/subtitles.py --slides 5         # один слайд
    python3 tools/subtitles.py --engine local     # через faster-whisper
    python3 tools/subtitles.py --dry-run          # что будет сделано, без вызовов
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from record_lecture import ROOT, duration, head_clips, fetch

BUILD = os.path.join(ROOT, "build")
TIMINGS = os.path.join(BUILD, "timings")
UNITS = ("andre-ai-web", "andre-ai-test", "andre-ai-dev")
ENV_NAMES = ("OPENAI_API_KEY", "LLM_API_KEY")
ENV_FILES = ("/home/andre/andre-ai-maturity/.env", "/home/andre/andre-ai-test/.env",
             os.path.expanduser("~/.env"), os.path.join(ROOT, ".env"))


# ── ключ ──────────────────────────────────────────────────────────────────

def _from_env():
    for name in ENV_NAMES:
        val = os.environ.get(name)
        if val and val.strip():
            return val.strip(), "переменная окружения %s" % name
    return None, None


def _from_files():
    for path in ENV_FILES:
        if not os.path.isfile(path):
            continue
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for name in ENV_NAMES:
            m = re.search(r"^\s*(?:export\s+)?%s\s*=\s*[\"']?([^\"'\s#]+)" % name,
                          text, re.M)
            if m:
                return m.group(1), "%s → %s" % (path, name)
    return None, None


def _from_systemd():
    """Ключ живёт в окружении сервиса — достаём его же средствами systemd."""
    for unit in UNITS:
        try:
            out = subprocess.run(["systemctl", "show", unit, "-p", "Environment"],
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                 timeout=20).stdout.decode("utf-8", "ignore")
        except (OSError, subprocess.SubprocessError):
            continue
        for name in ENV_NAMES:
            m = re.search(r"%s=(\S+)" % name, out)
            if m:
                return m.group(1), "systemd-юнит %s → %s" % (unit, name)
    return None, None


def find_key():
    for probe in (_from_env, _from_files, _from_systemd):
        key, where = probe()
        if key:
            return key, where
    return None, None


# ── распознавание ─────────────────────────────────────────────────────────

def soft_ffmpeg():
    """ffmpeg тут не обязателен: он ускоряет загрузку (шлём звук вместо видео)
    и знает длительность. Нет его — длительность придёт из ответа API."""
    import shutil
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def audio_of(ff, clip, dst):
    """Отдельная звуковая дорожка: грузить на API 3 МБ видео вместо 0.5 МБ
    звука незачем. Не получилось — отдадим исходный файл, он тоже принимается."""
    if not ff:
        return clip
    try:
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", clip, "-vn",
                        "-ac", "1", "-ar", "16000", "-c:a", "aac", dst],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True)
        return dst if os.path.getsize(dst) > 1024 else clip
    except Exception:
        return clip


def via_openai(path, key, base):
    """POST multipart/form-data без сторонних библиотек — на VM может не быть
    ни requests, ни openai-sdk, а ставить их ради одного вызова не хочется."""
    fields = {"model": "whisper-1", "response_format": "verbose_json",
              "timestamp_granularities[]": "word", "language": "ru"}
    boundary = "----andre-ait-subtitles-boundary"
    body = b""
    for name, value in fields.items():
        body += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                 % (boundary, name, value)).encode("utf-8")
    body += ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n"
             "Content-Type: application/octet-stream\r\n\r\n"
             % (boundary, os.path.basename(path))).encode("utf-8")
    body += open(path, "rb").read() + b"\r\n"
    body += ("--%s--\r\n" % boundary).encode("utf-8")

    req = urllib.request.Request(
        base.rstrip("/") + "/audio/transcriptions", data=body,
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "multipart/form-data; boundary=" + boundary})
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.loads(r.read().decode("utf-8"))
    words = [{"w": w["word"].strip(), "s": round(w["start"], 3),
              "e": round(w["end"], 3)} for w in data.get("words", [])]
    return words, data.get("text", ""), data.get("duration")


def via_local(path):
    from faster_whisper import WhisperModel
    model = WhisperModel(os.environ.get("WHISPER_MODEL", "medium"),
                         device="cpu", compute_type="int8")
    segments, _ = model.transcribe(path, language="ru", word_timestamps=True,
                                   vad_filter=True)
    words, text = [], []
    for seg in segments:
        text.append(seg.text.strip())
        for w in (seg.words or []):
            words.append({"w": w.word.strip(), "s": round(w.start, 3),
                          "e": round(w.end, 3)})
    return words, " ".join(text), None


# ── SRT ───────────────────────────────────────────────────────────────────

def stamp(sec):
    ms = int(round(sec * 1000))
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60,
                                    ms // 1000 % 60, ms % 1000)


def srt(words, per=2, shift=0.0, start_no=1):
    """Реплики по `per` слов. Пустая реплика невозможна: пары режутся по
    факту, последняя может быть короче."""
    out, no = [], start_no
    for i in range(0, len(words), per):
        chunk = words[i:i + per]
        out.append("%d\n%s --> %s\n%s\n" % (
            no, stamp(chunk[0]["s"] + shift), stamp(chunk[-1]["e"] + shift),
            " ".join(c["w"] for c in chunk)))
        no += 1
    return out, no


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lecture", type=int, default=1)
    ap.add_argument("--slides", help="например 5 или 1-10 (по умолчанию все)")
    ap.add_argument("--engine", choices=("openai", "local"), default="openai")
    ap.add_argument("--per", type=int, default=2, help="слов в реплике субтитров")
    ap.add_argument("--dry-run", action="store_true",
                    help="показать план и найденный источник ключа, ничего не вызывая")
    args = ap.parse_args()

    ff = soft_ffmpeg()
    os.makedirs(TIMINGS, exist_ok=True)
    os.makedirs(os.path.join(BUILD, "head-clips"), exist_ok=True)

    clips = head_clips(args.lecture)
    if not clips:
        sys.exit("у лекции %d нет списка клипов" % args.lecture)
    idxs = list(range(len(clips)))
    if args.slides:
        if "-" in args.slides:
            a, b = args.slides.split("-")
            idxs = list(range(int(a) - 1, min(int(b), len(clips))))
        else:
            idxs = [int(args.slides) - 1]

    key = base = None
    if args.engine == "openai":
        key, where = find_key()
        if not key:
            sys.exit("ключ OpenAI не найден. Искал: %s; файлы %s; юниты %s.\n"
                     "   Задайте OPENAI_API_KEY=... перед командой либо "
                     "используйте --engine local."
                     % (", ".join(ENV_NAMES), ", ".join(ENV_FILES), ", ".join(UNITS)))
        base = (os.environ.get("OPENAI_BASE_URL") or os.environ.get("LLM_BASE_URL")
                or "https://api.openai.com/v1")
        print("ключ найден: %s · сервер %s" % (where, base))

    print("лекция %d: клипов %d, распознаём %d, движок %s"
          % (args.lecture, len(clips), len(idxs), args.engine))
    print("ffmpeg: %s" % (ff or "нет — длительность возьму из ответа API"))
    if args.dry_run:
        print("сухой прогон: сетевых вызовов не делаю")
        return

    full, no, clock, plain = [], 1, 0.0, []
    for n, i in enumerate(idxs, 1):
        name = urllib.parse.unquote(
            os.path.basename(urllib.parse.urlparse(clips[i]).path))
        clip = fetch(clips[i], os.path.join(BUILD, "head-clips", "%03d-%s" % (i, name)))
        tag = "lecture%d-slide%02d" % (args.lecture, i + 1)
        tj = os.path.join(TIMINGS, tag + ".json")

        if os.path.exists(tj):
            saved = json.load(open(tj, encoding="utf-8"))
            words, secs = saved["words"], saved.get("seconds")
            text = " ".join(w["w"] for w in words)
            print("  %d/%d · слайд %d — уже распознан" % (n, len(idxs), i + 1))
        else:
            src = audio_of(ff, clip, os.path.join(BUILD, "head-clips", tag + ".m4a"))
            words, text, secs = (via_openai(src, key, base) if args.engine == "openai"
                                 else via_local(src))
            json.dump({"words": words, "text": text, "seconds": secs},
                      open(tj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("  %d/%d · слайд %d — слов %d" % (n, len(idxs), i + 1, len(words)))

        lines, _ = srt(words, args.per)
        open(os.path.join(TIMINGS, tag + ".srt"), "w", encoding="utf-8").write(
            "\n".join(lines) + "\n")

        shifted, no = srt(words, args.per, shift=clock, start_no=no)
        full += shifted
        plain.append(text)
        # Сдвиг следующего слайда: длительность клипа. Порядок источников —
        # ffmpeg, ответ API, конец последнего слова (последнее приблизительно,
        # но лучше, чем ноль: иначе субтитры съедут на весь остаток лекции).
        clock += ((duration(ff, clip) if ff else None) or secs
                  or (words[-1]["e"] if words else 0.0))

    if len(idxs) > 1:
        stem = os.path.join(TIMINGS, "lecture%d-full" % args.lecture)
        open(stem + ".srt", "w", encoding="utf-8").write("\n".join(full) + "\n")
        open(stem + ".txt", "w", encoding="utf-8").write("\n\n".join(plain) + "\n")
        print("\nсквозные субтитры: %s.srt (%d реплик, %s)"
              % (stem, no - 1, stamp(clock).split(",")[0]))
    print("готово: %s" % os.path.relpath(TIMINGS, ROOT))


if __name__ == "__main__":
    main()
