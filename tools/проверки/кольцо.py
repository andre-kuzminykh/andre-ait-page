# -*- coding: utf-8 -*-
"""Кольцо цикла: ровный ли круг и ничего ли не залипает.

Владелец: «это должен быть не овал, а круг, но чтобы ничего не залипало».
Меряем в браузере: расстояние каждой точки до центра (должно быть одно
и то же) и зазоры между ВСЕМИ видимыми боксами кадра — кружками,
подписями и значком агента.
"""
import glob
import sys
from itertools import combinations
from playwright.sync_api import sync_playwright

def хром():
    """Путь к Chromium: версия в имени папки меняется, прибивать её нельзя."""
    из = sorted(glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome"))
    return из[-1] if из else "chromium"


ПОРТ = sys.argv[1] if len(sys.argv) > 1 else "8943"
МОМЕНТ = float(sys.argv[2]) if len(sys.argv) > 2 else 31.5
ЗАЗОР = 14          # меньше — уже «залипло»

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=хром(), args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg.goto("http://127.0.0.1:%s/index.html?rec=1&cover=0" % ПОРТ)
    pg.wait_for_function("typeof window.__renderAt === 'function'", timeout=20000)
    pg.wait_for_timeout(900)
    pg.evaluate("x=>window.__renderAt(x)", МОМЕНТ)
    pg.wait_for_timeout(700)
    боксы = pg.evaluate("""()=>{
        const s=document.querySelector('.cycle'), из=[];
        const буквы=(el)=>{let l=1e9,r=-1e9,t=1e9,b=-1e9;
            el.childNodes.forEach(n=>{
                if(n.nodeType!==3||!n.textContent.trim())return;
                const rg=document.createRange(); rg.selectNodeContents(n);
                [].slice.call(rg.getClientRects()).forEach(x=>{
                    if(x.width>1&&x.height>1){l=Math.min(l,x.left);r=Math.max(r,x.right);
                                              t=Math.min(t,x.top);b=Math.max(b,x.bottom);}});});
            return l>r?null:{l,r,t,b};};
        // у кружка и его СОБСТВЕННОЙ подписи зазор маленький по замыслу —
        // помечаем их одним «домом», такие пары не считаем залипшими.
        s.querySelectorAll('.pos').forEach((p,i)=>{
            const c=p.querySelector('.circle').getBoundingClientRect();
            из.push({имя:'кружок '+p.innerText.trim(),дом:i,l:c.left,r:c.right,t:c.top,b:c.bottom});
            const el=p.querySelector('.label'), б=буквы(el);
            if(б) из.push({имя:'подпись '+el.textContent.trim(),дом:i,l:б.l,r:б.r,t:б.t,b:б.b});});
        const a=s.querySelector('.agent');
        if(a){const r=a.getBoundingClientRect();
              из.push({имя:'агент',l:r.left,r:r.right,t:r.top,b:r.bottom});}
        return из;
    }""")
    точки = pg.evaluate("""()=>[].slice.call(document.querySelectorAll('.cycle .circle')).map(el=>{
        const r=el.getBoundingClientRect();
        return [Math.round(r.left+r.width/2), Math.round(r.top+r.height/2)];})""")
    b.close()

print("боксов в кадре:", len(боксы))
беды = 0

# 1. ровный круг: все точки на одном расстоянии от центра
if точки:
    cx = sum(x for x, _ in точки) / float(len(точки))
    cy = sum(y for _, y in точки) / float(len(точки))
    рад = [((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 for x, y in точки]
    print("центр (%.0f, %.0f), радиусы: %s" % (cx, cy, ["%.0f" % r for r in рад]))
    if max(рад) - min(рад) > 2:
        беды += 1
        print("  ← это не круг: радиусы разъехались на %.0fpx" % (max(рад) - min(рад)))

# 2. ничего не залипает
for a, c in combinations(боксы, 2):
    if a.get("дом") is not None and a.get("дом") == c.get("дом"):
        continue        # кружок и его собственная подпись
    dx = max(a["l"] - c["r"], c["l"] - a["r"])
    dy = max(a["t"] - c["b"], c["t"] - a["b"])
    зазор = max(dx, dy)
    if зазор < ЗАЗОР:
        беды += 1
        print("  ← «%s» и «%s» сходятся на %.0fpx" % (a["имя"], c["имя"], зазор))

# 3. зона
верх = min(x["t"] for x in боксы)
низ = max(x["b"] for x in боксы)
print("зона по кадру: %.0f…%.0f (можно 238…630)" % (верх, низ))
if верх < 238 or низ > 630:
    беды += 1
    print("  ← вышли из зоны")

print("бед:", беды)
sys.exit(1 if беды else 0)
