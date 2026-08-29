# -*- coding: utf-8 -*-
"""Макеты интерфейса: замер вылезаний и скриншоты по экранам.

Сначала меряем — низ каждого блока против рамки экрана, — и только потом
снимаем: макет, у которого нижняя панель обрезана рамкой, показывать
нельзя (ровно на этом обжёгся третий экран).
"""
import os, sys
from playwright.sync_api import sync_playwright

ПАПКА = os.path.dirname(os.path.abspath(__file__))
ИМЕНА = {
    "s1": "1-ролики", "s2": "2-материалы", "s3": "3-раскадровка",
    "s4": "4-сборка", "s5": "5-готово", "s6": "6-правила",
}

ЗАМЕР = """() => {
    const out = [];
    document.querySelectorAll('.screen').forEach(scr => {
        const r = scr.getBoundingClientRect();
        let вылез = 0, кто = '';
        scr.querySelectorAll('*').forEach(el => {
            const b = el.getBoundingClientRect();
            if (b.width === 0 && b.height === 0) return;
            const d = Math.max(b.bottom - r.bottom, r.top - b.top,
                               b.right - r.right, r.left - b.left);
            if (d > вылез) { вылез = d; кто = el.className || el.tagName; }
        });
        const внутри = [];
        scr.querySelectorAll('.content,.pane,.pane .b,.insp,.stage,.log').forEach(el => {
            const d = el.scrollHeight - el.clientHeight;
            if (d > 1) внутри.push((el.className || el.tagName) + ' +' + d);
        });
        out.push({id: scr.id, вылез: Math.round(вылез * 10) / 10, кто: кто,
                  внутри: внутри.join(', ')});
    });
    return out;
}"""


def главное():
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = br.new_page(viewport={"width": 1520, "height": 1000},
                         device_scale_factor=2)
        pg.goto("file://" + os.path.join(ПАПКА, "index.html"))
        pg.wait_for_timeout(2500)

        беда = 0
        for э in pg.evaluate(ЗАМЕР):
            метка = "ok " if э["вылез"] <= 0.5 else "ВЫЛЕЗ"
            print("%-4s %s %6.1f px  %s  | внутри: %s"
                  % (э["id"], метка, э["вылез"], э["кто"], э["внутри"] or "—"))
            if э["вылез"] > 0.5 or э["внутри"]:
                беда += 1

        if "--только-замер" in sys.argv:
            br.close()
            return 1 if беда else 0

        for ид, имя in ИМЕНА.items():
            pg.locator("#" + ид).screenshot(path=os.path.join(ПАПКА, имя + ".png"))
            print("снят", имя)
        br.close()
    return 1 if беда else 0


sys.exit(главное())
