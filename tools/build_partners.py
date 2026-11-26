# -*- coding: utf-8 -*-
"""FR-SITE137 — сборка страницы партнёров (partners/) из partners/partners.json.

Источник правды о партнёрах — partners/partners.json (массив публичных профилей,
схема — SPEC-SITE.md, раздел «Сайт партнёров»). Тот же файл сможет публиковать
будущий кабинет партнёра. Страница грузит его через fetch, а на случай file:// и
сбоя загрузки держит встроенную копию в partners/index.html — её вписывает этот
сборщик, руками она не правится (тест сверяет копию с файлом).

Что делает:
  * проверяет каждый профиль по схеме (обязательные поля, slug, LinkedIn,
    услуги, отрасли и языки с подписями на обоих языках, даты, отзывы);
  * вписывает в partners/index.html компактную копию JSON
    (<script type="application/json" id="partners-data">);
  * ставит в адреса partners.css и partners.js метку версии ?v=<sha1[:8]>
    содержимого — после правки посетитель не получит старый файл из кеша.

    python3 tools/build_partners.py           # проверить и собрать
    python3 tools/build_partners.py --check   # только сверить (exit 1, если сборка устарела)
    python3 tools/build_partners.py --og      # ещё и превью для соцсетей partners/og.png (нужен Playwright)

Добавить партнёра: дописать профиль в partners/partners.json → запустить сборку →
python3 tests/test_partners.py → коммит.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "partners")
INDEX = os.path.join(DIR, "index.html")
DATA = os.path.join(DIR, "partners.json")
CSS = os.path.join(DIR, "partners.css")
JS = os.path.join(DIR, "partners.js")

SERVICES = ("review", "bootcamp", "neuronium")
CERTIFIED = "andre-ai-certified"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINKEDIN_RE = re.compile(r"^https://(?:[a-z]{2,3}\.)?linkedin\.com/in/[A-Za-z0-9\-_%.]+/?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# FR-SITE147: промокод партнёра — необязательное поле; вид — как у кода партнёра в продукте (ценовая политика v3: 4–32 знака, латиница,
# цифры, «_» и «-», первый — буква или цифра). По нему «Пригласить клиента» собирает ссылку andre.technology/?promo=…&partner=…
PROMO_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{3,31}$")
INLINE_RE = re.compile(r'(<script type="application/json" id="partners-data">)(.*?)(</script>)', re.S)
VER_RE = re.compile(r'(partners\.(?:css|js))\?v=[0-9a-f]{8}')


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_i18n():
    """Словарь I18N из partners.js — он записан как JSON между пометками I18N:BEGIN / I18N:END."""
    js = _read(JS)
    m = re.search(r"/\* I18N:BEGIN.*?\*/\s*var I18N = (\{.*?\});\s*/\* I18N:END \*/", js, re.S)
    if not m:
        raise ValueError("partners.js: не найден блок I18N:BEGIN … I18N:END")
    return json.loads(m.group(1))


def load_partners():
    return json.loads(_read(DATA))


def _both(o):
    return isinstance(o, dict) and all(isinstance(o.get(k), str) and o.get(k).strip() for k in ("ru", "en"))


def _date(s):
    if not isinstance(s, str) or not DATE_RE.match(s):
        return False
    try:
        datetime.date.fromisoformat(s)
        return True
    except ValueError:
        return False


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _int(x):
    return isinstance(x, int) and not isinstance(x, bool) and x >= 0


def validate(partners, i18n=None):
    """Ошибки схемы — список строк; пустой список — всё верно. Правила — те же, что у страницы
    (partners.js: problem()), плюс то, что страница прощает молча: подписи отраслей и языков,
    одинаковое число навыков на двух языках, даты и оценки отзывов."""
    i18n = i18n or read_i18n()
    errs = []
    if not isinstance(partners, list):
        return ["partners.json: верхний уровень — массив профилей"]
    seen = set()
    for i, p in enumerate(partners):
        tag = "профиль #%d" % i
        if not isinstance(p, dict):
            errs.append(tag + ": не объект")
            continue
        slug = p.get("slug")
        tag = "%s (%s)" % (tag, slug)
        if not isinstance(slug, str) or not SLUG_RE.match(slug):
            errs.append(tag + ": slug — латиница в нижнем регистре, цифры и дефисы")
        elif slug in seen:
            errs.append(tag + ": slug повторяется")
        seen.add(slug)
        if "example" in p and not isinstance(p["example"], bool):
            errs.append(tag + ": example — true/false")
        if "promo_code" in p and (not isinstance(p["promo_code"], str) or not PROMO_RE.match(p["promo_code"])):
            errs.append(tag + ": promo_code — код партнёра: 4–32 знака, латиница, цифры, «_» и «-», первый — буква или цифра")
        for k in ("name", "headline", "about"):
            if not _both(p.get(k)):
                errs.append(tag + ": %s — {ru, en}, оба непустые" % k)
        if not _num(p.get("rating")) or not 0 <= p["rating"] <= 5:
            errs.append(tag + ": rating — число от 0 до 5")
        for k in ("reviews_count", "projects"):
            if not _int(p.get(k)):
                errs.append(tag + ": %s — целое ≥ 0" % k)
        if not _num(p.get("rate_usd")) or p["rate_usd"] < 50:
            errs.append(tag + ": rate_usd — ставка консультанта в $ за час, от 50 (ценовая политика §4)")
        sv = p.get("services")
        if not isinstance(sv, list) or not sv or any(s not in SERVICES for s in sv) or len(set(sv)) != len(sv):
            errs.append(tag + ": services — непустой список из %s без повторов" % (SERVICES,))
        for k, prefix in (("industries", "ind."), ("languages", "lng.")):
            v = p.get(k)
            if not isinstance(v, list) or not v or len(set(v)) != len(v):
                errs.append(tag + ": %s — непустой список без повторов" % k)
                continue
            for code in v:
                if not isinstance(code, str) or prefix + code not in i18n["ru"] or prefix + code not in i18n["en"]:
                    errs.append(tag + ": %s «%s» — нет подписи %s%s в I18N partners.js (ru и en)" % (k, code, prefix, code))
        for code in p.get("languages") or []:
            if isinstance(code, str) and not re.match(r"^[a-z]{2}$", code):
                errs.append(tag + ": язык «%s» — двухбуквенный код ISO 639-1" % code)
        loc = p.get("location")
        if not isinstance(loc, dict) or not _both(loc.get("city")) or not _both(loc.get("country")) \
                or not re.match(r"^[A-Z]{2}$", str(loc.get("country_code", ""))) or not isinstance(loc.get("remote"), bool):
            errs.append(tag + ": location — {city {ru,en}, country {ru,en}, country_code ISO 3166 (две заглавные), remote true/false}")
        if not isinstance(p.get("linkedin"), str) or not LINKEDIN_RE.match(p["linkedin"]):
            errs.append(tag + ": linkedin — https://www.linkedin.com/in/<профиль>")
        sk = p.get("skills")
        if not isinstance(sk, dict) or not all(isinstance(sk.get(k), list) and sk.get(k) and all(isinstance(x, str) and x for x in sk[k]) for k in ("ru", "en")):
            errs.append(tag + ": skills — {ru: [...], en: [...]}")
        elif len(sk["ru"]) != len(sk["en"]):
            errs.append(tag + ": skills — на двух языках одинаковое число навыков")
        certs = p.get("certificates")
        if not isinstance(certs, list):
            errs.append(tag + ": certificates — список")
        else:
            for c in certs:
                if not isinstance(c, dict) or not isinstance(c.get("id"), str) or not _both(c.get("title")) or not _int(c.get("year")):
                    errs.append(tag + ": сертификат — {id, year, title {ru, en}}")
            if not any(isinstance(c, dict) and c.get("id") == CERTIFIED for c in certs):
                errs.append(tag + ": в каталоге только сертифицированные — нужен сертификат id «%s»" % CERTIFIED)
        revs = p.get("reviews")
        if not isinstance(revs, list):
            errs.append(tag + ": reviews — список")
        else:
            for r in revs:
                ok = isinstance(r, dict) and _both(r.get("author")) and _both(r.get("text")) and _date(r.get("date")) \
                    and _num(r.get("rating")) and 1 <= r["rating"] <= 5 and ("company" not in r or _both(r.get("company")))
                if not ok:
                    errs.append(tag + ": отзыв — {author {ru,en}, company {ru,en}?, rating 1…5, date ГГГГ-ММ-ДД, text {ru,en}}")
            if isinstance(p.get("reviews_count"), int) and len(revs) > p["reviews_count"]:
                errs.append(tag + ": reviews_count меньше числа опубликованных отзывов")
        if not _date(p.get("joined")):
            errs.append(tag + ": joined — дата ГГГГ-ММ-ДД")
    return errs


def inline_json(partners):
    """Компактная копия для страницы; «</» экранирован, чтобы текст профиля не закрыл тег <script>."""
    return json.dumps(partners, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def version(path):
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


def render_index(html, partners):
    if not INLINE_RE.search(html):
        raise ValueError("partners/index.html: нет <script type=\"application/json\" id=\"partners-data\">")
    html = INLINE_RE.sub(lambda m: m.group(1) + inline_json(partners) + m.group(3), html, count=1)
    vers = {"partners.css": version(CSS), "partners.js": version(JS)}
    return VER_RE.sub(lambda m: "%s?v=%s" % (m.group(1), vers[m.group(1)]), html)


def build(check=False):
    partners = load_partners()
    errs = validate(partners)
    if errs:
        raise SystemExit("partners.json не прошёл проверку схемы:\n  " + "\n  ".join(errs))
    cur = _read(INDEX)
    new = render_index(cur, partners)
    if check:
        if new != cur:
            raise SystemExit("partners/index.html устарел: запустите python3 tools/build_partners.py")
        return False
    if new != cur:
        with open(INDEX, "w", encoding="utf-8") as f:
            f.write(new)
        return True
    return False


# ── превью для соцсетей ────────────────────────────────────────────────────

OG_HTML = r"""<!doctype html><html><head><meta charset="utf-8"><style>
  html, body { margin: 0; width: 1200px; height: 630px; overflow: hidden; background: #050505; }
  body { position: relative; font-family: 'JetBrains Mono', monospace; color: #E5E7EB;
    background: radial-gradient(60% 70% at 0% 0%, rgba(136,84,243,0.30), transparent 70%), radial-gradient(55% 65% at 100% 100%, rgba(249,115,22,0.22), transparent 70%), #050505; }
  .frame { position: absolute; inset: 0; border: 2px solid rgba(255,255,255,0.08); }
  .top { position: absolute; left: 78px; top: 78px; display: flex; align-items: center; gap: 30px; font-size: 34px; }
  .top img { width: 104px; height: 104px; object-fit: contain; margin: -20px 0; }
  .top b { color: #fff; font-weight: 700; } .top span { color: #94a3b8; }
  h1 { position: absolute; left: 76px; top: 232px; margin: 0; font-size: 74px; line-height: 1.16; font-weight: 800; letter-spacing: -0.02em; }
  h1 .p { color: #8854F3; } h1 .o { color: #F97316; }
  .sub { position: absolute; left: 78px; top: 448px; font-size: 27px; color: #cbd5e1; letter-spacing: 0.01em; }
  .pill { position: absolute; left: 70px; top: 538px; padding: 12px 24px; border: 2px solid #fff; border-radius: 999px; font-size: 24px; font-weight: 700; color: #fff; background: rgba(20,18,26,0.9); }
  .earn { position: absolute; right: 78px; top: 546px; font-size: 25px; font-weight: 700; color: #ff8a33; }
</style></head><body><div class="frame"></div>
  <div class="top"><img src="%LOGO%" alt=""><span><b>Andre AI</b> Partners</span></div>
  <h1><span class="p">Certified AI</span><br><span class="o">Consultants</span></h1>
  <p class="sub">map reviews · team bootcamps · Neuronium launches</p>
  <div class="pill">partners.andre.technology</div>
  <div class="earn">become a partner · $50–300/h</div>
</body></html>"""


def build_og(out=None):
    """partners/og.png 1200×630 — в стиле превью главной (assets/og/andre-ai-technologies.png).
    Логотип — локальная копия из корня репозитория, шрифт — JetBrains Mono из системы."""
    import base64
    from playwright.sync_api import sync_playwright
    out = out or os.path.join(DIR, "og.png")
    with open(os.path.join(ROOT, "866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png"), "rb") as f:
        logo = "data:image/png;base64," + base64.b64encode(f.read()).decode()
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or "/opt/pw-browsers/chromium", args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        pg.set_content(OG_HTML.replace("%LOGO%", logo), wait_until="load")
        pg.wait_for_timeout(300)
        pg.screenshot(path=out)
        b.close()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="только сверить, собрана ли страница из текущих файлов")
    ap.add_argument("--og", action="store_true", help="пересобрать partners/og.png (нужен Playwright и Chromium)")
    a = ap.parse_args()
    changed = build(check=a.check)
    if a.check:
        print("PARTNERS BUILD OK — страница собрана из текущих partners.json, partners.css, partners.js")
        return
    print("partners/index.html " + ("обновлён" if changed else "уже актуален"))
    if a.og:
        print("превью:", build_og())


if __name__ == "__main__":
    sys.exit(main())
