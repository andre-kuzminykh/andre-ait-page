#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Аудит сценариев подсветки: то, что не ловит fx_check.

fx_check отвечает на вопрос «сценарий вообще рабочий?» — есть ли элемент,
звучит ли слово. Здесь — вопрос «а это красиво?»: нет ли длинных провалов без
единой подсветки, не сливаются ли соседние реплики одним цветом, не горят ли
две подсветки одновременно на одном элементе, не заваливаем ли кадр эмодзи,
не целимся ли в карточку с классом scale-… (эффект переписывает transform, и
такая карточка в момент вспышки скачком «сдувается»).

    python3 tools/fx_audit.py            # все слайды
    python3 tools/fx_audit.py --slide 7
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from animate_slide import BUILD, FX_DIR, cue_times

MAX_GAP = 8.0          # с — дольше зритель смотрит на статичный кадр
MAX_BURST = 3          # всплесков эмодзи на слайд
SOLAR = {"glow-solar", "underline", "frame"}   # оранжевые эффекты
VIOLET = {"glow-violet", "pop", "rise"}        # фиолетовые


def tone(fx):
    return "оранж" if fx in SOLAR else "фиолет" if fx in VIOLET else "фиолет"


def audit(lecture, slide):
    tag = "lecture%d-slide%02d" % (lecture, slide)
    scen_p = os.path.join(FX_DIR, tag + ".json")
    inv_p = os.path.join(BUILD, "fx-inventory", tag + ".json")
    if not (os.path.exists(scen_p) and os.path.exists(inv_p)):
        return ["нет сценария или инвентаря"], {}
    scen, inv = json.load(open(scen_p, encoding="utf-8")), \
                json.load(open(inv_p, encoding="utf-8"))
    cues = cue_times(json.loads(json.dumps(scen["cues"])), inv.get("words", []))
    cues = sorted(cues, key=lambda c: c["at"])
    speech = inv["words"][-1]["e"] if inv.get("words") else 0
    cls = {i["text"]: (i.get("cls") or "") for i in inv["items"]}
    warn = []

    # 1. Провалы: до первой реплики, между гаснущей и следующей, после последней.
    if cues and cues[0]["at"] > MAX_GAP:
        warn.append("нет подсветки первые %.1f с" % cues[0]["at"])
    for a, b in zip(cues, cues[1:]):
        dark = b["at"] - (a["at"] + a.get("dur", 2.5))
        if dark > MAX_GAP:
            warn.append("провал %.1f с (%.1f→%.1f)"
                        % (dark, a["at"] + a.get("dur", 2.5), b["at"]))
    if cues:
        tail = speech - (cues[-1]["at"] + cues[-1].get("dur", 2.5))
        if tail > MAX_GAP:
            warn.append("хвост %.1f с без подсветки до конца речи" % tail)

    # 2. Цвет: две подряд одного тона сливаются в одно длинное пятно.
    for a, b in zip(cues, cues[1:]):
        if tone(a.get("fx")) == tone(b.get("fx")) \
                and b["at"] - (a["at"] + a.get("dur", 2.5)) < 1.5:
            warn.append("подряд один цвет (%s): %.1f и %.1f с"
                        % (tone(a.get("fx")), a["at"], b["at"]))

    # 3. Один элемент горит дважды внахлёст — выглядит как залипшая подсветка.
    for i, a in enumerate(cues):
        for b in cues[i + 1:]:
            if b["at"] >= a["at"] + a.get("dur", 2.5):
                break
            if b.get("text") == a.get("text") and b.get("up") == a.get("up"):
                warn.append("наложение на одном элементе: %.1f и %.1f с"
                            % (a["at"], b["at"]))

    # 4. Эмодзи: перебор превращает слайд в ярмарку.
    bursts = [c for c in cues if c.get("burst")]
    if len(bursts) > MAX_BURST:
        warn.append("всплесков эмодзи %d — больше %d" % (len(bursts), MAX_BURST))

    # 5. Карточки с scale-… дёргаются: эффект переписывает transform целиком.
    for c in cues:
        k = cls.get(c.get("text"), "")
        if "scale-" in k and (c.get("up") or 0) == 0:
            warn.append("цель со scale- в классах: %r" % c.get("text")[:32])

    # 6. Реплика после конца речи — подсветка в тишине.
    for c in cues:
        if speech and c["at"] > speech:
            warn.append("реплика на %.1f с — речь кончилась на %.1f"
                        % (c["at"], speech))

    stat = {"реплик": len(cues), "эмодзи": len(bursts),
            "речь": round(speech, 1),
            "покрытие": round(sum(c.get("dur", 2.5) for c in cues)
                              / speech * 100) if speech else 0}
    return warn, stat


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lecture", type=int, default=1)
    ap.add_argument("--slide", type=int)
    args = ap.parse_args()
    slides = [args.slide] if args.slide else sorted(
        int(f[-7:-5]) for f in os.listdir(FX_DIR)
        if f.startswith("lecture%d-slide" % args.lecture) and f.endswith(".json"))
    bad = 0
    for n in slides:
        warn, stat = audit(args.lecture, n)
        mark = "!" if warn else "·"
        print("%s слайд %2d — реплик %s, эмодзи %s, речь %s с, подсветка %s%%"
              % (mark, n, stat.get("реплик", "?"), stat.get("эмодзи", "?"),
                 stat.get("речь", "?"), stat.get("покрытие", "?")))
        for w in warn:
            print("    → %s" % w)
        bad += bool(warn)
    print("\nслайдов с замечаниями: %d из %d" % (bad, len(slides)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
