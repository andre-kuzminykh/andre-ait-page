#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка сценариев подсветки ДО рендера (рендер слайда стоит ~4 минуты).

Сверяет каждую реплику с двумя источниками правды: инвентарём слайда
(`build/fx-inventory/`) — есть ли такой элемент дословно, и речью
(`build/timings/`) — звучит ли такое слово. Печатает итоговый тайминг: во
сколько реально загорится каждая реплика и сколько будет гореть.

    python3 tools/fx_check.py              # все сценарии
    python3 tools/fx_check.py --slide 5    # один
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from animate_slide import BUILD, FX_DIR, cue_times

FX = {"pop", "glow-violet", "glow-solar", "frame", "underline", "rise", "none",
      "zoom", "check", "fill"}


def load(path):
    return json.load(open(path, encoding="utf-8"))


def check(lecture, slide):
    tag = "lecture%d-slide%02d" % (lecture, slide)
    scen_p = os.path.join(FX_DIR, tag + ".json")
    inv_p = os.path.join(BUILD, "fx-inventory", tag + ".json")
    if not os.path.exists(scen_p):
        return ["нет сценария %s" % os.path.basename(scen_p)], []
    if not os.path.exists(inv_p):
        return ["нет инвентаря %s — сначала tools/fx_inventory.py" % inv_p], []

    scen, inv = load(scen_p), load(inv_p)
    texts = {i["text"] for i in inv["items"]}
    words = inv.get("words", [])
    errs, cues = [], scen.get("cues") or []
    if not cues:
        errs.append("пустой список cues")
    # Плотность, а не голое число: на минуту речи семь подсветок — редко,
    # а на пятнадцать секунд — уже рябь. Предел — примерно одна на четыре
    # секунды: перечисления в речи («восприятие — мышление — действие»)
    # идут плотнее среднего темпа, и запрещать их нельзя.
    speech = words[-1]["e"] if words else 0
    limit = max(7, int(speech / 4) + 1) if speech else 9
    if len(cues) > limit:
        errs.append("реплик %d на %.0f с речи — рябит, предел %d"
                    % (len(cues), speech, limit))

    for k, c in enumerate(cues, 1):
        where = "реплика %d (%s)" % (k, c.get("word") or c.get("text", "")[:20])
        if c.get("text") not in texts:
            errs.append("%s: элемента нет на слайде дословно: %r"
                        % (where, c.get("text")))
        if c.get("fx") and c["fx"] not in FX:
            errs.append("%s: неизвестный эффект %r" % (where, c["fx"]))
        if not isinstance(c.get("at"), (int, float)):
            errs.append("%s: нет ориентира at" % where)
        if c.get("burst") and not (4 <= (c.get("n") or 10) <= 16):
            errs.append("%s: n=%s вне 4..16" % (where, c.get("n")))

    # Привязка к речи — тем же кодом, что и рендер, чтобы проверка не врала.
    bound = cue_times(json.loads(json.dumps(cues)), words)
    rows, tail = [], (words[-1]["e"] if words else 0)
    for k, (c, b) in enumerate(zip(cues, bound), 1):
        if c.get("word") and words and not b.get("bound"):
            errs.append("реплика %d: слова %r нет в речи — время останется %.1f"
                        % (k, c["word"], c.get("at")))
        if b["at"] > tail + 0.5 and words:
            errs.append("реплика %d: %.1f с — уже после конца речи (%.1f с)"
                        % (k, b["at"], tail))
        rows.append((k, b["at"], b.get("dur", 2.5), c.get("fx", "glow"),
                     (c.get("text") or "")[:34], c.get("burst") or ""))
    order = [r[1] for r in rows]
    if order != sorted(order):
        errs.append("реплики идут не по времени речи — переставьте по порядку")
    return errs, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lecture", type=int, default=1)
    ap.add_argument("--slide", type=int)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    slides = ([args.slide] if args.slide else
              sorted(int(f[-7:-5]) for f in os.listdir(FX_DIR)
                     if f.startswith("lecture%d-slide" % args.lecture)
                     and f.endswith(".json")))
    bad = 0
    for n in slides:
        errs, rows = check(args.lecture, n)
        mark = "✗" if errs else "✓"
        print("%s слайд %d — реплик %d" % (mark, n, len(rows)))
        if not args.quiet:
            for k, at, dur, fx, text, burst in rows:
                print("   %d) %6.2f с · %4.1f с · %-12s %-34s %s"
                      % (k, at, dur, fx, text, burst))
        for e in errs:
            print("   ! %s" % e)
        bad += bool(errs)
    if bad:
        print("\nсценариев с проблемами: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
