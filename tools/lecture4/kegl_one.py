# -*- coding: utf-8 -*-
"""Быстрый замер кегля ОДНОГО слайда лекции 4 на телефоне.

    python3 build/l4/kegl_one.py 22            # один слайд
    python3 build/l4/kegl_one.py 22 23 24      # несколько

Собирает колоду из текущих build/l4/out/*.html в отдельный файл-пробник
(каждый запуск в свой, чтобы параллельные проверки не мешали друг другу),
открывает его в телефонной форме и печатает минимальный ЭФФЕКТИВНЫЙ кегль —
тот, что видит зритель: кегль × zoom × transform всей цепочки предков.

Норма — 10px. Ниже — слайд не принят: на телефоне текст нечитаем.

ВАЖНО: собранный CSS (assets/lecture-4.css) пересобирается отдельно. Пока
идёт разгрузка слайдов, НОВЫЕ классы Tailwind вводить нельзя — их нет в
собранном файле, и замер соврёт. Убирать и укорачивать — можно.

Запускать из корня репозитория.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import record_lecture as rl        # noqa: E402
import lecture_check as lc         # noqa: E402


STUB = ('    <div class="slide-container px-3 sm:px-6 md:px-12 opacity-0 pointer-events-none '
        'translate-y-8" id="slide-%d">\n        <div class="content-z max-w-5xl w-full">\n'
        '            <h2 class="text-xl sm:text-3xl md:text-5xl font-black mb-3 md:mb-5 '
        'text-center text-black">Заглушка <span class="text-solar">%d</span></h2>\n'
        '            <p class="text-center text-black/60 mb-4 md:mb-7 text-[10px] md:text-lg '
        'font-medium max-w-3xl mx-auto">Слайд ещё верстается</p>\n        </div>\n    </div>\n')


def build_probe(name):
    # Недостающие слайды подменяем заглушкой: подгонка считает каждый слайд
    # отдельно, поэтому на замер соседей это не влияет, а колода собирается.
    import shutil, tempfile
    src = os.path.join(ROOT, "build", "l4", "out")
    tmp = tempfile.mkdtemp(prefix="l4out-")
    have = set()
    for f in os.listdir(src):
        if f.endswith(".html"):
            shutil.copy(os.path.join(src, f), tmp)
            have.add(int(re.search(r"slide-(\d+)", f).group(1)))
    for i in range(43):
        if i not in have:
            io.open(os.path.join(tmp, "slide-%02d.html" % i), "w",
                    encoding="utf-8").write(STUB % (i, i))
    os.environ["L4_OUT"] = tmp
    os.environ["L4_DST"] = os.path.join(ROOT, "automation", "4", name)
    sys.path.insert(0, os.path.join(ROOT, "build", "l4"))
    import assemble
    import io as _io
    buf, old = _io.StringIO(), sys.stdout
    sys.stdout = buf
    try:
        assemble.main()
    finally:
        sys.stdout = old
    return os.environ["L4_DST"]


def main():
    lc.must_run_from_root()
    ids = [int(a) for a in sys.argv[1:]]
    if not ids:
        sys.exit(__doc__)
    name = "_kegl_%d.html" % os.getpid()
    path = build_probe(name)
    from playwright.sync_api import sync_playwright
    srv = rl.serve()
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(executable_path=lc.chromium_path(),
                                    args=["--no-sandbox", "--hide-scrollbars"])
            ctx = br.new_context(viewport=dict(lc.MOB), device_scale_factor=1,
                                 reduced_motion="reduce")
            v = lc.vendor_dir()
            if v:
                ctx.route("**/*", rl.vendor_route(v))
            page = ctx.new_page()
            page.goto("http://127.0.0.1:%d/automation/4/%s" % (rl.PORT, name),
                      wait_until="load", timeout=120000)
            page.wait_for_timeout(3500)
            page.evaluate("() => document.querySelectorAll('#start-overlay,#intro-overlay')"
                          ".forEach(e => e.remove())")
            rl.check_font(page, allow_fallback=False)
            worst = 99.0
            for i in ids:
                # updateSlides() аргументов не принимает — он показывает
                # currentSlide. Листаем до нужного стрелками, как зритель.
                page.evaluate("""(n) => {
                  const act = [...document.querySelectorAll('.slide-container')]
                    .findIndex(s => s.classList.contains('opacity-100'));
                  let d = n - (act < 0 ? 0 : act);
                  while (d > 0) { window.nextSlide(); d--; }
                  while (d < 0) { window.prevSlide(); d++; }
                }""", i)
                page.wait_for_timeout(1100)
                r = page.evaluate(lc._js(lc.JS_KEGL))
                worst = min(worst, r["min"] or 99)
                mark = "ХОРОШО" if (r["min"] or 0) >= 10 else "МАЛО"
                print("слайд %d: минимум %.2fpx — %s" % (i, r["min"] or 0, mark))
                for it in r["items"][:5]:
                    print("    %6.2fpx  %-18s %s" % (it["px"], it["tag"] + " " + it["cls"][:16],
                                                     it["text"][:58]))
            ctx.close(); br.close()
    finally:
        srv.shutdown()
        if os.path.exists(path):
            os.remove(path)
    return 0 if worst >= 10 else 1


if __name__ == "__main__":
    sys.exit(main())
