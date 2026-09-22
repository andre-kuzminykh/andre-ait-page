# -*- coding: utf-8 -*-
"""Замер общего кегля заголовков колоды (__FLOOR) — LECTURE-GUIDE §10, п.3.

    python3 tools/measure_floor.py 4            # напечатает числа
    python3 tools/measure_floor.py 4 --write    # ещё и впишет их в lecture-floor

Зачем константа. Общий кегль заголовков — свойство КОЛОДЫ, а не окна: он
считается один раз на форму. Если его не зашить числом, первый заход в форму
показывает слайд с целевым кеглем, а через секунду ужимает до общего — это и
есть «слайд дышит». Если тексты слайдов изменились, константа протухает, и
её надо переснять.

Как меряем: временная копия страницы с обнулённым __FLOOR, самокалибровка
подгонщика отрабатывает сама, и мы читаем то, к чему она сошлась — ровно по
формуле подгонщика (инлайновый кегль заголовка × zoom его content-z).

*** Запускать из корня репозитория *** — иначе не найдётся vendor/ со
шрифтом, страница уедет на системный и замер соврёт.
"""
import argparse, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import record_lecture as rl          # noqa: E402
import lecture_check as lc           # noqa: E402

# Размеры из §10: кегль зависит только от формы, поэтому 1440x900 и 1920x1080
# обязаны дать одно и то же число, а 390x844 и 376x667 — своё.
PC = {"width": 1440, "height": 900}
MOB = {"width": 390, "height": 844}

# Мерим ВЫЧИСЛЕННЫЙ кегль заголовка, умноженный на zoom его холста, — то есть
# размер в пикселях ФОРМЫ, в которых и живёт константа.
#
# Инлайновый кегль, который ставит sizeTitles, брать нельзя: на каждом проходе
# сразу за apply(z) идёт textFit, а он первым делом сбрасывает инлайновые
# кегли ВСЕХ текстовых элементов холста, включая заголовок. К концу подгонки
# инлайнового размера у заголовка нет — есть только классовый. Проверено на
# лекции 3: min(computed x zoom) = 34.20 при зашитой константе 34.2851, то
# есть число в lecture-floor описывает ровно эту величину.
JS_MIN = """
() => {
  const out = [];
  document.querySelectorAll('.slide-container').forEach((s, i) => {
    const c = s.querySelector('.content-z');
    if (!c) return;
    const t = c.querySelector('[data-slide-title]') || c.querySelector('h1, h2');
    if (!t) return;
    const z = parseFloat(getComputedStyle(c).zoom) || 1;
    const px = parseFloat(getComputedStyle(t).fontSize);
    if (px) out.push([i, px * z]);
  });
  return out;
}
"""


def measure(lecture, probe_rel, viewport):
    from playwright.sync_api import sync_playwright
    srv = rl.serve()
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(executable_path=lc.chromium_path(),
                                    args=["--no-sandbox", "--hide-scrollbars"])
            ctx = br.new_context(viewport=dict(viewport), device_scale_factor=1,
                                 reduced_motion="reduce")
            vend = lc.vendor_dir()
            if vend:
                ctx.route("**/*", rl.vendor_route(vend))
            page = ctx.new_page()
            page.goto("http://127.0.0.1:%d/%s" % (rl.PORT, probe_rel),
                      wait_until="load", timeout=120000)
            page.wait_for_timeout(4000)
            page.evaluate("() => document.querySelectorAll('#start-overlay,#intro-overlay')"
                          ".forEach(e => e.remove())")
            # Самокалибровка идёт после того, как очередь подгонки опустеет,
            # и может запустить ВТОРОЙ проход по всей колоде. Ждём его.
            page.wait_for_timeout(5000)
            rl.check_font(page, allow_fallback=False)
            vals = page.evaluate(JS_MIN)
            ctx.close(); br.close()
    finally:
        srv.shutdown()
    if not vals:
        sys.exit("ни одного заголовка не замерено — подгонка не отработала")
    worst = min(vals, key=lambda v: v[1])
    return worst, vals


def main():
    ap = argparse.ArgumentParser(description="Замер __FLOOR колоды.")
    ap.add_argument("lecture", type=int)
    ap.add_argument("--write", action="store_true", help="вписать в lecture-floor")
    # У лекции может быть вторая колода (automation/5/v2) — у неё свой общий
    # кегль, и мерить его надо по её странице, а не по прод-версии.
    ap.add_argument("--page", help="страница колоды вместо automation/<N>/index.html")
    ap.add_argument("--json", help="куда положить floor.json")
    a = ap.parse_args()
    lc.must_run_from_root()

    src = os.path.join(ROOT, a.page) if a.page else \
        os.path.join(ROOT, "automation", str(a.lecture), "index.html")
    html = io.open(src, encoding="utf-8").read()
    probe = os.path.join(os.path.dirname(src), "_floor_probe.html")
    io.open(probe, "w", encoding="utf-8").write(
        re.sub(r"window\.__FLOOR = \{[^}]*\};", "window.__FLOOR = {pc:0,mob:0};", html, count=1))
    rel = os.path.relpath(probe, ROOT)
    try:
        got = {}
        for name, vp in (("pc", PC), ("mob", MOB)):
            worst, vals = measure(a.lecture, rel, vp)
            got[name] = round(worst[1], 4)
            print("%s: %.4f  (самый узкий слайд — %d; всего замерено %d)"
                  % (name, worst[1], worst[0], len(vals)))
            # Общий кегль тянет вниз ОДИН перегруженный слайд, поэтому важно
            # видеть не только худший, а хвост: разгружать надо их все.
            for i, v in sorted(vals, key=lambda v: v[1])[:6]:
                print("    слайд %2d: %.4f" % (i, v))
    finally:
        os.remove(probe)

    print("window.__FLOOR = {pc:%s,mob:%s};" % (got["pc"], got["mob"]))
    if a.write:
        html = io.open(src, encoding="utf-8").read()
        html = re.sub(r"window\.__FLOOR = \{[^}]*\};",
                      "window.__FLOOR = {pc:%s,mob:%s};" % (got["pc"], got["mob"]),
                      html, count=1)
        io.open(src, "w", encoding="utf-8").write(html)
        json.dump(got, io.open(os.path.join(ROOT, a.json) if a.json else
                               os.path.join(ROOT, "build", "l4", "floor.json"), "w",
                               encoding="utf-8"))
        print("вписано в %s" % src)
    return 0


if __name__ == "__main__":
    sys.exit(main())
