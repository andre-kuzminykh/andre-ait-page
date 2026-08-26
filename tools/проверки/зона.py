# -*- coding: utf-8 -*-
"""Влезает ли каждая сцена в отведённую зону 238…630.

Смотрим не на CSS, а на настоящие прямоугольники в браузере: берём
каждую сцену в момент, когда она полнее всего, и считаем общий бокс
видимых элементов. Выше 238 — графика лезет под шапку, ниже 630 — на
картины: и то и другое владелец уже ловил глазом.
"""
import glob
import sys
from playwright.sync_api import sync_playwright

def хром():
    """Путь к Chromium: версия в имени папки меняется, прибивать её нельзя."""
    из = sorted(glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome"))
    return из[-1] if из else "chromium"


ПОРТ = sys.argv[1] if len(sys.argv) > 1 else "8940"
ВЕРХ, НИЗ = 238, 630

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=хром(), args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg.goto("http://127.0.0.1:%s/index.html?rec=1&cover=0" % ПОРТ)
    pg.wait_for_function("typeof window.__renderAt === 'function'", timeout=20000)
    pg.wait_for_timeout(900)
    сцены = pg.evaluate("""()=>[].slice.call(document.querySelectorAll('.scene')).map(s=>({
        id:s.id, in:+s.getAttribute('data-in'), out:+s.getAttribute('data-out')}))""")
    моменты = []
    for c in сцены:                      # ближе к концу сцены она полнее всего
        моменты.append((c["id"], c["out"] - 0.25))
    моменты.sort(key=lambda x: x[1])
    плохо = 0
    for ид, t in моменты:
        pg.evaluate("x=>window.__renderAt(x)", t)
        pg.wait_for_timeout(650)
        r = pg.evaluate("""(id)=>{
            const s=document.getElementById(id);
            let top=1e9, bot=-1e9, left=1e9, right=-1e9, n=0;
            // считаем только то, что реально рисует: круги и текст.
            // Контейнеры (.row, .stage) растянуты во всю ширину и давали
            // ложную тревогу «узкие поля».
            s.querySelectorAll('.circle,.label,.role,.sub,.core,.foot,.ring,.title,.chip').forEach(el=>{
                const st0=getComputedStyle(el);
                if(el.closest('svg')) return;
                const st=st0;
                if(st.opacity==='0'||st.visibility==='hidden'||st.display==='none') return;
                const род=el.closest('.el');
                if(род&&!род.classList.contains('on')) return;
                // у текста меряем САМИ БУКВЫ: коробка абзаца шире строки
                // (в широкой раскладке она 400px) и давала ложную тревогу.
                let боксы=[el.getBoundingClientRect()];
                if(!el.classList.contains('circle')&&!el.classList.contains('ring')){
                    const rr=[];
                    el.childNodes.forEach(n=>{
                        if(n.nodeType!==3||!n.textContent.trim()) return;
                        const r=document.createRange(); r.selectNodeContents(n);
                        [].slice.call(r.getClientRects()).forEach(b=>{
                            if(b.width>1&&b.height>1) rr.push(b);
                        });
                    });
                    if(rr.length) боксы=rr;
                }
                боксы.forEach(b=>{
                    if(b.width<2||b.height<2) return;
                    top=Math.min(top,b.top); bot=Math.max(bot,b.bottom);
                    left=Math.min(left,b.left); right=Math.max(right,b.right); n++;
                });
            });
            return {top,bot,left,right,n};
        }""", ид)
        флаг = ""
        if r["n"] == 0:
            флаг = "  ПУСТО"
        else:
            if r["top"] < ВЕРХ - 1: флаг += "  ВЫШЕ ЗОНЫ на %d" % (ВЕРХ - r["top"])
            if r["bot"] > НИЗ + 1: флаг += "  НИЖЕ ЗОНЫ на %d" % (r["bot"] - НИЗ)
            if r["left"] < 60: флаг += "  УЗКИЕ ПОЛЯ слева %d" % r["left"]
            if r["right"] > 1020: флаг += "  УЗКИЕ ПОЛЯ справа %d" % (1080 - r["right"])
        if флаг: плохо += 1
        print("%-5s t=%6.1f  y %4d…%4d  x %4d…%4d  элементов %2d%s"
              % (ид, t, r["top"], r["bot"], r["left"], r["right"], r["n"], флаг))
    print("сцен с проблемами:", плохо)
    b.close()
