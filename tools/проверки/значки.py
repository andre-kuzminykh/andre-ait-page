# -*- coding: utf-8 -*-
"""Куда реально прилетают значки.

fit_tr.py их не видит: он меряет текст и круги, а значки — отдельный
слой. Считаем конечную точку каждого значка (точка старта плюс --dx/--dy
из разметки) и требуем поля 24px от краёв кадра и верх не выше 238.
"""
import glob
import sys
from playwright.sync_api import sync_playwright

def хром():
    """Путь к Chromium: версия в имени папки меняется, прибивать её нельзя."""
    из = sorted(glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome"))
    return из[-1] if из else "chromium"


ПОРТ = sys.argv[1] if len(sys.argv) > 1 else "8942"
ПОЛЕ, ВЕРХ = 24, 238

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=хром(), args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg.goto("http://127.0.0.1:%s/index.html?rec=1&cover=0" % ПОРТ)
    pg.wait_for_function("typeof window.__renderAt === 'function'", timeout=20000)
    pg.wait_for_timeout(900)
    сцены = pg.evaluate("""()=>[].slice.call(document.querySelectorAll('.scene')).map(s=>({
        id:s.id, in:+s.getAttribute('data-in'), out:+s.getAttribute('data-out')}))""")
    плохо = 0
    for c in сцены:
        t = min(c["in"] + 2.0, c["out"] - 0.2)
        pg.evaluate("x=>window.__renderAt(x)", t)
        pg.wait_for_timeout(500)
        r = pg.evaluate("""(id)=>{
            const s=document.getElementById(id), из=[];
            s.querySelectorAll('.fly').forEach(f=>{
                const б=f.getBoundingClientRect();
                f.querySelectorAll('i').forEach(i=>{
                    const dx=parseFloat(i.style.getPropertyValue('--dx'))||0;
                    const dy=parseFloat(i.style.getPropertyValue('--dy'))||0;
                    // i стоит left:-20 top:-20 от точки .fly, размер 40
                    из.push({l:б.left-20+dx, r:б.left+20+dx, t:б.top-20+dy, b:б.top+20+dy});
                });
            });
            if(!из.length) return null;
            return {l:Math.min.apply(null,из.map(x=>x.l)), r:Math.max.apply(null,из.map(x=>x.r)),
                    t:Math.min.apply(null,из.map(x=>x.t)), b:Math.max.apply(null,из.map(x=>x.b)),
                    n:из.length};
        }""", c["id"])
        if not r:
            continue
        флаг = ""
        if r["l"] < ПОЛЕ: флаг += "  ЗА КРАЙ слева %d" % r["l"]
        if r["r"] > 1080 - ПОЛЕ: флаг += "  ЗА КРАЙ справа %d" % (1080 - r["r"])
        if r["t"] < ВЕРХ: флаг += "  ВЫШЕ ЗОНЫ на %d" % (ВЕРХ - r["t"])
        if флаг: плохо += 1
        print("%-5s значков %2d  x %4d…%4d  y %4d…%4d%s"
              % (c["id"], r["n"], r["l"], r["r"], r["t"], r["b"], флаг))
    print("сцен с улетевшими значками:", плохо)
    b.close()
