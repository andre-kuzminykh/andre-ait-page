# -*- coding: utf-8 -*-
"""Каждое появление и каждое окно подсветки — внутри речи.

Графика, которая выходит в тишине, выглядит как своя жизнь поверх
ролика. Берём субтитры (это и есть речь по времени) и проверяем, что
каждое data-in попадает внутрь реплики, а окно data-cur пересекается с ней.
"""
import re
import sys

# Папку ролика передаём аргументом:
#   python3 tools/проверки/речь.py automation/1/<папка ролика>
ПАПКА = sys.argv[1] if len(sys.argv) > 1 else "."
СТРАНИЦА = ПАПКА + "/index.html"
СУБТИТРЫ = ПАПКА + "/субтитры.srt"
ЗАЗОР = 0.35          # столько тишины вокруг реплики считаем «ещё речью»


def реплики(путь):
    out = []
    for b in re.split(r"\n\n+", open(путь, encoding="utf-8-sig").read().replace("\r", "").strip()):
        m = re.search(r"(\d\d):(\d\d):(\d\d),(\d\d\d)\s*-->\s*(\d\d):(\d\d):(\d\d),(\d\d\d)", b)
        if not m:
            continue
        г = [int(x) for x in m.groups()]
        a = г[0] * 3600 + г[1] * 60 + г[2] + г[3] / 1000.0
        e = г[4] * 3600 + г[5] * 60 + г[6] + г[7] / 1000.0
        t = " ".join(l for l in b.split("\n") if "-->" not in l and not l.strip().isdigit())
        out.append((a, e, t.strip()))
    return out


реч = реплики(СУБТИТРЫ)


def в_речи(t):
    return any(a - ЗАЗОР <= t <= e + ЗАЗОР for a, e, _ in реч)


def слово(t):
    for a, e, тек in реч:
        if a - ЗАЗОР <= t <= e + ЗАЗОР:
            return тек
    return "—"


html = open(СТРАНИЦА, encoding="utf-8").read()
плохо = 0
for сцена in re.findall(r'<section class="scene" id="(s\d+)"[^>]*>(.*?)</section>', html, re.S):
    ид, тело = сцена
    for m in re.finditer(r'data-in="([\d.]+)"', тело):
        t = float(m.group(1))
        if not в_речи(t):
            плохо += 1
            print("%-4s появление %6.2f — в тишине" % (ид, t))
    for m in re.finditer(r'data-cur="([\d.]+) ([\d.]+)"', тело):
        a, e = float(m.group(1)), float(m.group(2))
        if not (в_речи(a) or в_речи(e)):
            плохо += 1
            print("%-4s окно %6.2f…%6.2f — в тишине" % (ид, a, e))
        if e <= a:
            плохо += 1
            print("%-4s окно %6.2f…%6.2f — вывернуто" % (ид, a, e))

# два кольца разом не горят
окна = []
for m in re.finditer(r'class="item el"[^>]*data-cur="([\d.]+) ([\d.]+)"', html):
    окна.append((float(m.group(1)), float(m.group(2))))
окна.sort()
for i in range(len(окна) - 1):
    if окна[i][1] > окна[i + 1][0] + 1e-6:
        плохо += 1
        print("два кольца разом: %.2f…%.2f и %.2f…%.2f" % (окна[i] + окна[i + 1]))

print("появлений:", len(re.findall(r'data-in="', html)),
      "окон:", len(re.findall(r'data-cur="', html)))
print("проблем:", плохо)
sys.exit(1 if плохо else 0)
