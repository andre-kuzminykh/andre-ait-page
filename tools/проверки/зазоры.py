# -*- coding: utf-8 -*-
"""Не слипаются ли соседние подписи в ряду.

fit_tr.py смотрит на общий бокс сцены и такое пропускает: «Поддерживающие»
и «Управленческие» стояли впритык, буква к букве, а зона при этом целая.
Здесь меряем сами буквы (range-боксы текстовых узлов) у соседних .label /
.role / .chip внутри одного ряда и требуем зазор не меньше 18px.
"""
import glob
import sys
from playwright.sync_api import sync_playwright

def хром():
    """Путь к Chromium: версия в имени папки меняется, прибивать её нельзя."""
    из = sorted(glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome"))
    return из[-1] if из else "chromium"


ПОРТ = sys.argv[1] if len(sys.argv) > 1 else "8942"
ЗАЗОР = 18

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=хром(), args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg.goto("http://127.0.0.1:%s/index.html?rec=1&cover=0" % ПОРТ)
    pg.wait_for_function("typeof window.__renderAt === 'function'", timeout=20000)
    pg.wait_for_timeout(900)
    сцены = pg.evaluate("""()=>[].slice.call(document.querySelectorAll('.scene')).map(s=>({
        id:s.id, out:+s.getAttribute('data-out')}))""")
    плохо = 0
    for c in sorted(сцены, key=lambda x: x["out"]):
        pg.evaluate("x=>window.__renderAt(x)", c["out"] - 0.25)
        pg.wait_for_timeout(600)
        ряды = pg.evaluate("""(id)=>{
            const s=document.getElementById(id), из=[];
            const буквы=(el)=>{let l=1e9,r=-1e9;el.childNodes.forEach(n=>{
                if(n.nodeType!==3||!n.textContent.trim())return;
                const rg=document.createRange();rg.selectNodeContents(n);
                [].slice.call(rg.getClientRects()).forEach(b=>{
                    if(b.width>1&&b.height>1){l=Math.min(l,b.left);r=Math.max(r,b.right);}});});
                return l>r?null:{l,r};};
            s.querySelectorAll('.row,.grid4,.trio,.chips').forEach(ряд=>{
                const шт=[];
                ряд.querySelectorAll('.label,.role,.chip,.sub').forEach(el=>{
                    const st=getComputedStyle(el);
                    if(st.opacity==='0'||st.visibility==='hidden'||st.display==='none')return;
                    const род=el.closest('.el');
                    if(род&&!род.classList.contains('on'))return;
                    const б=буквы(el); if(!б)return;
                    шт.push({t:el.textContent.trim(),l:б.l,r:б.r,y:el.getBoundingClientRect().top});
                });
                // в ряд попадают только те, что стоят на одной высоте
                const строки={};
                шт.forEach(x=>{const k=Math.round(x.y/8);(строки[k]=строки[k]||[]).push(x);});
                Object.keys(строки).forEach(k=>{
                    const л=строки[k].sort((a,b)=>a.l-b.l);
                    for(let i=1;i<л.length;i++) из.push({a:л[i-1].t,b:л[i].t,g:Math.round(л[i].l-л[i-1].r)});
                });
            });
            return из;
        }""", c["id"])
        for пара in ряды:
            if пара["g"] < ЗАЗОР:
                плохо += 1
                print("%-5s  «%s» ↔ «%s»  зазор %d" % (c["id"], пара["a"], пара["b"], пара["g"]))
    print("слипшихся пар:", плохо)
    b.close()
