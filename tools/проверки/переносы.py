# -*- coding: utf-8 -*-
"""Ни одна подпись не переносится на две строки (правило владельца №5).

Считаем строчные боксы диапазона текста: две коробки = перенос. Явный
<br> тоже даёт две — такие подписи перечислены в РАЗРЕШЕНО.
"""
import glob
import io
import sys
from playwright.sync_api import sync_playwright

def хром():
    """Путь к Chromium: версия в имени папки меняется, прибивать её нельзя."""
    из = sorted(glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome"))
    return из[-1] if из else "chromium"


ПОРТ = sys.argv[1] if len(sys.argv) > 1 else "8940"
# Разрешённые переносы лежат РЯДОМ С РОЛИКОМ, а не в проверке: список у
# каждого ролика свой (владелец разрешал перенос точечно — «можно в две
# строчки»), а зашитый в инструмент он молча разрешал бы чужие.
#   python3 tools/проверки/переносы.py <порт> [папка ролика]
ПАПКА = sys.argv[2] if len(sys.argv) > 2 else "."
РАЗРЕШЕНО = set()
try:
    for строка in io.open(ПАПКА + "/переносы-исключения.txt", encoding="utf-8"):
        строка = строка.split("#")[0].strip()
        if строка:
            РАЗРЕШЕНО.add(строка)
except IOError:
    pass

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=хром(), args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg.goto("http://127.0.0.1:%s/index.html?rec=1&cover=0" % ПОРТ)
    pg.wait_for_function("typeof window.__renderAt === 'function'", timeout=20000)
    pg.wait_for_timeout(900)
    # показываем ВСЁ разом: ширина подписи от времени не зависит
    pg.evaluate("""()=>{document.querySelectorAll('.scene').forEach(s=>s.classList.add('on'));
                     document.querySelectorAll('.el').forEach(e=>e.classList.add('on'));}""")
    pg.wait_for_timeout(300)
    плохие = pg.evaluate("""()=>{
        const out=[];
        document.querySelectorAll('.scene .label,.scene .core,.scene .sub,.scene .foot,.scene .role')
          .forEach(el=>{
            const t=(el.textContent||'').trim(); if(!t) return;
            // Меряем ТОЛЬКО текстовые узлы: сияние внутри абзаца — это
            // абсолютный спан, и его прямоугольник считался лишней строкой.
            const верхи=new Set();
            el.childNodes.forEach(n=>{
                if(n.nodeType!==3||!n.textContent.trim()) return;
                const r=document.createRange(); r.selectNodeContents(n);
                [].slice.call(r.getClientRects()).forEach(b=>{
                    if(b.width>1) верхи.add(Math.round(b.top));
                });
            });
            const строк=верхи.size;
            const b=el.getBoundingClientRect();
            out.push({сцена:el.closest('.scene').id, текст:t, строк:строк,
                      ширина:Math.round(b.width), лево:Math.round(b.left), право:Math.round(b.right)});
        });
        return out;
    }""")
    b.close()

плохо = 0
for э in плохие:
    беда = []
    if э["строк"] > 1 and э["текст"] not in РАЗРЕШЕНО:
        беда.append("перенос на %d строки" % э["строк"])
    if э["лево"] < 40:
        беда.append("уходит за левый край (%d)" % э["лево"])
    if э["право"] > 1040:
        беда.append("уходит за правый край (%d)" % э["право"])
    if беда:
        плохо += 1
        print("%-5s «%s» — %s" % (э["сцена"], э["текст"], ", ".join(беда)))
print("подписей проверено: %d, с бедой: %d" % (len(плохие), плохо))
