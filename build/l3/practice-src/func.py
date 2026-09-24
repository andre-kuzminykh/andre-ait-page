import os, sys, base64
sys.path.insert(0, '.')
from harness import start, chromium, route_ctx
import harness
from playwright.sync_api import sync_playwright
ROOT='/home/user/andre-ait-page'
srv, port = start()
URL = "http://127.0.0.1:%d/automation/3/practice/" % port
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chromium(), args=["--no-sandbox"])
    # 1) webm для проверки кружка: пишем 1.5с канваса MediaRecorder'ом
    ctx = b.new_context(); pg = ctx.new_page()
    pg.goto("about:blank")
    b64 = pg.evaluate("""async () => {
      const c = document.createElement('canvas'); c.width = 64; c.height = 64;
      const g = c.getContext('2d'); const st = c.captureStream(25);
      const rec = new MediaRecorder(st, {mimeType: 'video/webm;codecs=vp8'}); const parts = [];
      rec.ondataavailable = e => parts.push(e.data);
      let i = 0; const t = setInterval(() => { g.fillStyle = i++ % 2 ? '#8B5CF6' : '#F97316'; g.fillRect(0,0,64,64); }, 40);
      rec.start(); await new Promise(r => setTimeout(r, 1500)); rec.stop(); clearInterval(t);
      await new Promise(r => rec.onstop = r);
      const buf = await new Blob(parts).arrayBuffer();
      let s = ''; new Uint8Array(buf).forEach(x => s += String.fromCharCode(x)); return btoa(s);
    }""")
    webm = base64.b64decode(b64); ctx.close()
    print('webm bytes', len(webm))

    # 2) кружок появляется после loadeddata
    ctx = b.new_context(viewport={'width': 1440, 'height': 900})
    vendor_h = None
    def h(route):
        u = route.request.url
        if u.endswith('/assets/video_l3/practice.mp4'):
            return route.fulfill(status=200, body=webm, content_type='video/webm')
        if u.endswith('/assets/video_l3/practice.jpg'):
            return route.fulfill(status=200, body=open(ROOT + '/assets/video_sq/poster_practice_2.jpg','rb').read(), content_type='image/jpeg')
        return route.fallback()
    route_ctx(ctx)
    ctx.route('**/assets/video_l3/*', h)
    pg = ctx.new_page(); errs = []
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(2500)
    print('bubble with video:', pg.evaluate("() => [document.documentElement.classList.contains('bubble-ready'), getComputedStyle(document.getElementById('bubble')).display]"), 'errors:', errs)
    pg.screenshot(path=ROOT + '/build/l3/practice-shots/desk-dark-bubble-when-video.png')

    # 3) функции окна
    pg.wait_for_selector('#v-layer svg')
    # копирование с графом из окна
    ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
    pg.click('.v-tab[data-key="hr"]'); pg.wait_for_timeout(1200)
    pg.evaluate("() => document.querySelectorAll('details.src').forEach(d => d.open = true)")
    pg.click('.copy-code[data-copy="prompt-arch"]'); pg.wait_for_timeout(300)
    clip = pg.evaluate("() => navigator.clipboard.readText()")
    print('copy-with-graph: has graph', 'Извлечь данные резюме' in clip, '| placeholder gone', 'СЮДА ВСТАВЬТЕ КОД ГРАФА' not in clip)
    pg.click('.copy[data-copy="prompt-graph"]'); pg.wait_for_timeout(300)
    clip = pg.evaluate("() => navigator.clipboard.readText()")
    print('prompt 2 copied plain:', clip.startswith('Ты — архитектор ИИ-агентов'), '<b>' in clip, '-->' in clip)
    # case-nav
    pg.click('#info-hr .case-nav .next'); pg.wait_for_timeout(1500)
    print('case-nav next ->', pg.evaluate("() => [document.querySelector('.v-tab[aria-selected=true]').dataset.key, !document.getElementById('info-marketing').hidden, Math.round(document.getElementById('viewer').getBoundingClientRect().top)]"))
    # ошибка и промт на исправление
    pg.fill('#v-input', 'flowchart TD\n  A[Старт --> B{{')
    pg.wait_for_timeout(1500)
    e = pg.evaluate("() => [!document.getElementById('v-err').hidden, document.getElementById('v-err-text').textContent.slice(0,120), !!document.querySelector('#v-layer svg')]")
    print('broken code -> error shown:', e)
    pg.click('#v-fixprompt'); pg.wait_for_timeout(300)
    clip = pg.evaluate("() => navigator.clipboard.readText()")
    print('fix prompt has code+error:', 'Старт' in clip and 'Ошибка:' in clip)
    # своя схема переживает перезагрузку, вкладки сняты
    pg.fill('#v-input', 'flowchart TD\n  A(["Триггер"]) --> B["<b>Свой навык</b><br/>ИИ: генерация"]\n  classDef ai fill:#7C3AED,stroke:#A78BFA,color:#fff\n  class B ai')
    pg.wait_for_timeout(1500)
    pg.reload(); pg.wait_for_timeout(3000)
    print('draft restored:', pg.evaluate("() => [document.getElementById('v-input').value.includes('Свой навык'), !!document.querySelector('.v-tab[aria-selected=true]'), !!document.querySelector('#v-layer svg')]"))
    pg.click('.v-tab[data-key="consult"]'); pg.wait_for_timeout(1500)
    # тема переключается — граф перерисован
    pg.click('#lec-theme'); pg.wait_for_timeout(1500)
    print('theme toggle:', pg.evaluate("() => [document.documentElement.classList.contains('dark'), !!document.querySelector('#v-layer svg'), document.getElementById('v-err').hidden]"))
    # svg/png
    with pg.expect_download() as d1: pg.click('#v-svg')
    with pg.expect_download() as d2: pg.click('#v-png')
    print('downloads:', d1.value.suggested_filename, d2.value.suggested_filename, os.path.getsize(d2.value.path()))
    pg.click('#lec-theme'); pg.wait_for_timeout(800)
    print('errors total:', errs)
    ctx.close()

    # 4) mermaid не загрузился — карточки всё равно переключаются
    ctx = b.new_context(viewport={'width': 390, 'height': 844})
    route_ctx(ctx)
    ctx.route('**/assets/mermaid/**', lambda r: r.abort())
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(2500)
    pg.click('.v-tab[data-key="design"]'); pg.wait_for_timeout(300)
    print('no mermaid:', pg.evaluate("() => [!document.getElementById('v-err').hidden, document.getElementById('v-err-text').textContent.slice(0,60), !document.getElementById('info-design').hidden, document.getElementById('v-input').value.startsWith('flowchart')]"), errs)
    ctx.close()

    # 5) 1024x768 — прокрутки вбок нет
    for vw, vh in ((1024, 768), (320, 700)):
        ctx = b.new_context(viewport={'width': vw, 'height': vh}); route_ctx(ctx)
        pg = ctx.new_page(); pg.goto(URL); pg.wait_for_selector('#v-layer svg'); pg.wait_for_timeout(800)
        print(vw, 'scroll', pg.evaluate("() => [document.documentElement.scrollWidth, document.documentElement.clientWidth, document.getElementById('v-level').textContent]"))
        pg.screenshot(path=ROOT + '/build/l3/practice-shots/w%d-dark-top.png' % vw)
        ctx.close()
    b.close()
srv.shutdown()
