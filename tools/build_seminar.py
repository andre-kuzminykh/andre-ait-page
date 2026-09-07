# -*- coding: utf-8 -*-
"""Сборка семинара к лекции 1: automation/1/seminar/index.html.

Зачем отдельный сборщик. Семинар — это 13 слайдов по 10 плиток, к каждой
плитке своя карточка-схема: 130 однотипных блоков. Руками такую страницу
не поддержать: одна правка вёрстки превратилась бы в 130 одинаковых правок.
Поэтому содержимое лежит данными (tools/seminar/data-*.json и speech-*.json),
а вёрстка — одним шаблоном здесь.

Канон лекций соблюдён (LECTURE-GUIDE.md, §2):
  · форм ровно две — 1380x864 и 376x844, граница 768px и только по ширине;
  · внутри формы раскладка не зависит от окна: окно меняет ОДИН масштаб
    --view-scale (transform), состав картинки не меняется никогда;
  · не прокручивается ни страница, ни слайд;
  · теней нет нигде;
  · термины по-русски;
  · Montserrat, фиолетовый #8B5CF6 + оранжевый #F97316.

Значки Phosphor вшиты SVG-спрайтом (tools/seminar/icons.json): с внешнего
CDN они пропадают при плохой сети — этим уже обжигались страницы практики.

    python3 tools/build_seminar.py            # собрать страницу
    python3 tools/build_seminar.py --icons DIR  # обновить icons.json из
                                                # @phosphor-icons/core (assets/fill)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "tools", "seminar")
OUT = os.path.join(ROOT, "automation", "1", "seminar", "index.html")

# Порядок слайдов колоды. Первый — карта направлений, дальше десять
# направлений по десять сотрудников, потом сборка компании и финал.
DOMAIN_ORDER = ["management", "hr", "marketing", "smm", "sales", "support",
                "analytics", "design", "development", "engineering"]
DECK_ORDER = ["map"] + DOMAIN_ORDER + ["assembly", "finale"]

TITLE = "Семинар — 100 ИИ-сотрудников | Модуль 1"
DESC = ("Семинар к лекции 1: сто ИИ-сотрудников в десяти направлениях. "
        "Что каждый берёт на вход, что делает, что оставляет после себя "
        "и где в его работу включается человек.")

AUTONOMY = [
    "Читает и разбирает",
    "Готовит черновик",
    "Действует после подтверждения",
    "Действует сам в рамках правил",
    "Наблюдает и зовёт человека",
]
RISK = [
    "Только чтение",
    "Внутренний черновик",
    "Меняет внутренние записи",
    "Обратимое внешнее действие",
    "Необратимое действие",
]


def read_json(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ── Спрайт значков ────────────────────────────────────────────────────────
# В HTML попадают только те значки, которые реально используются: сотня
# карточек тянула бы за собой весь набор Phosphor (полтора мегабайта).

def refresh_icons(src_dir):
    """Пересобрать tools/seminar/icons.json из @phosphor-icons/core."""
    used = set()
    for key in DECK_ORDER:
        if key == "map":
            continue
        d = read_json("data-%s.json" % key)
        used.add(d.get("icon", "circle"))
        for t in d["tiles"]:
            used.add(t.get("icon", "circle"))
    used |= set(UI_ICONS)
    out = {}
    missing = []
    for name in sorted(used):
        path = os.path.join(src_dir, "%s-fill.svg" % name)
        if not os.path.exists(path):
            missing.append(name)
            continue
        body = open(path, encoding="utf-8").read()
        m = re.search(r"<svg[^>]*>(.*)</svg>", body, re.S)
        out[name] = re.sub(r"\s+", " ", m.group(1)).strip()
    if missing:
        sys.exit("нет значков: " + ", ".join(missing))
    with open(os.path.join(DATA_DIR, "icons.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=0, sort_keys=True)
    print("icons.json: %d значков" % len(out))


# Значки самой страницы (шапка, стрелки, разделы карточки)
UI_ICONS = [
    "moon", "sun", "book-open-text", "chalkboard-teacher", "arrow-left",
    "arrow-right", "x", "sign-in", "gear-fine", "package", "user-focus",
    "gauge", "shield-warning", "arrow-fat-line-right", "wrench", "target",
    "caret-right", "squares-four",
]


def sprite(icons):
    parts = ['<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>']
    for name in sorted(icons):
        body = ICONS.get(name)
        if body is None:
            continue
        parts.append('<symbol id="i-%s" viewBox="0 0 256 256">%s</symbol>' % (name, body))
    parts.append("</defs></svg>")
    return "".join(parts)


def ic(name, cls="ic"):
    return '<svg class="%s" aria-hidden="true"><use href="#i-%s"></use></svg>' % (cls, name)


ICONS = {}


# ── Стили ─────────────────────────────────────────────────────────────────
# Раскладка считается ТОЛЬКО в пикселях формы (1380x864 / 376x844). Окно
# получает готовый холст, умноженный на один transform: scale. Поэтому
# внутри формы нет ни одного правила, которое зависело бы от размера окна,
# и единственный контентный брейкпоинт — граница форм, 768px.

CSS = r"""
:root{
  --ink:#0A0A0A; --bg:#FFFFFF; --card:#FFFFFF; --bd:#E9E9E9;
  --muted:rgba(0,0,0,.58); --soft:rgba(0,0,0,.035); --soft-bd:rgba(0,0,0,.08);
  --pur:#8B5CF6; --org:#F97316;
  /* Акцент слайда — готовым набором, без color-mix: там, где его нет,
     подложка молча становится прозрачной и плитка теряет фон. */
  --ac:#8B5CF6; --ac-s:rgba(139,92,246,.13); --ac-m:rgba(139,92,246,.09);
  --ac-b:rgba(139,92,246,.26); --ac-l:rgba(139,92,246,.34);
  --scrim:rgba(10,10,10,.62);
  --view-scale:1;
  --form-w:1380px; --form-h:864px;
}
@media (max-width:767px){ :root{ --form-w:376px; --form-h:844px; } }
html.dark{
  --ink:#FAFAFA; --bg:#0A0A0A; --card:#141414; --bd:rgba(255,255,255,.13);
  --muted:rgba(250,250,250,.62); --soft:rgba(255,255,255,.05); --soft-bd:rgba(255,255,255,.10);
  --scrim:rgba(0,0,0,.74);
}
.acc-warm{ --ac:#F97316; --ac-s:rgba(249,115,22,.14); --ac-m:rgba(249,115,22,.10);
  --ac-b:rgba(249,115,22,.28); --ac-l:rgba(249,115,22,.36); }
*{margin:0;padding:0;box-sizing:border-box}
/* Теней нет нигде — общее требование по всем страницам курса */
*,*::before,*::after{box-shadow:none!important;text-shadow:none!important;filter:none!important}
html,body{height:100%;overflow:hidden;overflow:clip;-webkit-tap-highlight-color:transparent}
html{background:var(--bg)}
body{
  font-family:'Montserrat',sans-serif; background:var(--bg); color:var(--ink);
  -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale;
  transition:background .3s ease,color .3s ease;
}
a{color:inherit;text-decoration:none}
button{font-family:inherit;color:inherit;cursor:pointer;background:none;border:none}
::selection{background:var(--pur);color:#fff}
*:focus{outline:none}
*:focus-visible{outline:2px solid var(--pur);outline-offset:3px}
.ic{width:1em;height:1em;fill:currentColor;flex-shrink:0;display:block}

/* ── Шапка: геометрия один в один с шапкой лекции ─────────────────────── */
#lecture-header{
  position:fixed; top:0; left:0; right:0; z-index:9000; display:flex;
  align-items:center; justify-content:space-between; gap:.5rem;
  padding:1.1rem; pointer-events:none; zoom:var(--view-scale,1);
}
@media (min-width:768px){ #lecture-header{ padding:2rem; } }
#lecture-header>*{pointer-events:auto}
.lec-logo{display:inline-flex;align-items:center;flex-shrink:0}
.lec-logo img{width:2.9rem;height:2.9rem;object-fit:contain;display:block}
@media (min-width:768px){ .lec-logo img{width:3.6rem;height:3.6rem} }
.lec-right{display:flex;align-items:center;gap:.4rem;flex-shrink:0}
.lec-ctrl{
  display:inline-flex;align-items:center;justify-content:center;height:2.7rem;width:2.7rem;
  border-radius:999px;border:1px solid var(--soft-bd);background:var(--card);color:var(--ink);
  font-size:1.05rem;line-height:1;transition:background .2s ease,color .2s ease,border-color .2s ease;
}
@media (min-width:768px){ .lec-ctrl{height:2.85rem;width:2.85rem;font-size:1.3rem} }
.lec-ctrl:hover{background:var(--soft);border-color:var(--pur)}
.lec-lbl{width:auto;padding:0 1.15rem;gap:.45rem;font-weight:800;text-transform:uppercase;letter-spacing:.07em;font-size:12px}
.lec-lbl .ic{font-size:1.2rem}
@media (max-width:767px){
  .lec-lbl{width:2.7rem;padding:0}
  .lec-lbl span{display:none}
  .lec-lbl .ic{font-size:1.05rem}
}
.lec-consult{
  display:inline-flex;align-items:center;justify-content:center;gap:.4rem;padding:.62rem .85rem;
  border-radius:999px;background:var(--pur);color:#fff;font-weight:800;text-transform:uppercase;
  letter-spacing:.06em;font-size:10.5px;white-space:nowrap;transition:background .2s ease;
}
@media (min-width:768px){ .lec-consult{height:2.85rem;box-sizing:border-box;padding:0 1.4rem;font-size:11.5px;letter-spacing:.15em;gap:.55rem} }
.lec-consult:hover{background:#7C3AED}

/* ── Сцена и холст ─────────────────────────────────────────────────────── */
/* Холст равен ФОРМЕ и центрируется; окно меняет только --view-scale. */
#stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;overflow:hidden}
#deck{
  position:relative; width:var(--form-w); height:var(--form-h); flex:0 0 auto;
  transform:translateX(var(--deck-shift,0px)) scale(var(--view-scale));
  transform-origin:center center;
}
body:not(.fit-ready) #deck{opacity:0}
.slide{
  position:absolute; inset:0; display:flex; flex-direction:column;
  padding:128px 40px 88px; opacity:0; visibility:hidden; pointer-events:none;
  transition:opacity .34s ease;
}
.slide.is-on{opacity:1;visibility:visible;pointer-events:auto}
@media (max-width:767px){ .slide{padding:88px 14px 96px} }

/* ── Заголовок слайда ──────────────────────────────────────────────────── */
.s-head{flex:0 0 auto;margin-bottom:14px}
.s-kicker{
  display:inline-flex;align-items:center;gap:.45em;font-size:11px;font-weight:800;
  letter-spacing:.18em;text-transform:uppercase;color:var(--ac);margin-bottom:8px;
}
.s-kicker .ic{font-size:14px}
.s-title{
  font-size:44px;line-height:1.06;font-weight:900;letter-spacing:-.015em;
  background-image:linear-gradient(90deg,var(--pur) 0%,var(--org) 100%);
  -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent;
}
.s-sub{margin-top:9px;font-size:15px;line-height:1.45;font-weight:500;color:var(--muted);max-width:1000px}
.s-sub.mob{display:none}
@media (max-width:767px){
  .s-head{margin-bottom:10px}
  .s-kicker{font-size:9px;letter-spacing:.14em;margin-bottom:5px}
  .s-kicker .ic{font-size:11px}
  .s-title{font-size:23px;line-height:1.1}
  .s-sub{margin-top:6px;font-size:11.5px;line-height:1.38}
  .s-sub.pc{display:none}
  .s-sub.mob{display:block}
}

/* ── Сетка плиток: 5x2 на компьютере, 2x5 на телефоне ──────────────────── */
.grid{
  flex:1 1 auto; display:grid; grid-template-columns:repeat(5,1fr);
  grid-auto-rows:1fr; gap:16px; min-height:0;
}
@media (max-width:767px){ .grid{grid-template-columns:repeat(2,1fr);gap:9px} }

.tile{
  position:relative; display:flex; flex-direction:column; align-items:flex-start;
  text-align:left; padding:15px 15px 13px; border-radius:18px;
  background:var(--card); border:1px solid var(--bd); overflow:hidden;
  transition:border-color .18s ease,background .18s ease;
}
.tile::after{
  content:''; position:absolute; left:0; right:0; bottom:0; height:3px;
  background:var(--ac); opacity:.16; transition:opacity .18s ease;
}
.tile:hover,.tile:focus-visible{border-color:var(--ac);background:var(--soft)}
.tile:hover::after,.tile:focus-visible::after{opacity:1}
.t-no{
  position:absolute; top:13px; right:14px; font-size:11px; font-weight:800;
  letter-spacing:.06em; color:var(--muted); opacity:.65;
}
.t-ic{
  display:flex; align-items:center; justify-content:center; width:44px; height:44px;
  border-radius:14px; background:var(--ac-s);
  color:var(--ac); font-size:24px; margin-bottom:11px; flex:0 0 auto;
}
.t-name{font-size:15.5px;line-height:1.2;font-weight:800;letter-spacing:-.005em;overflow-wrap:break-word;hyphens:none}
.t-lead{margin-top:7px;font-size:11.5px;line-height:1.38;font-weight:500;color:var(--muted);overflow-wrap:break-word}
.t-do{margin-top:10px;display:grid;gap:4px;width:100%}
.t-do i{display:flex;align-items:flex-start;gap:.45em;font-size:10.5px;line-height:1.3;font-style:normal;font-weight:600;color:var(--muted)}
.t-do i::before{content:'';flex:0 0 auto;width:4px;height:4px;border-radius:50%;background:var(--ac);margin-top:.44em;opacity:.75}
.t-foot{margin-top:auto;padding-top:10px;display:flex;align-items:center;gap:7px;width:100%}
.t-dots{display:flex;gap:3px}
.t-dots i{width:11px;height:4px;border-radius:2px;background:var(--soft-bd);display:block}
.t-dots i.on{background:var(--ac)}
.t-cnt{font-size:10px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--ac);white-space:nowrap}
.t-trig{font-size:9.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);white-space:nowrap}
@media (max-width:767px){
  .tile{padding:9px 9px 8px;border-radius:13px}
  .t-no{top:7px;right:8px;font-size:8.5px}
  .t-ic{width:27px;height:27px;border-radius:9px;font-size:15px;margin-bottom:6px}
  .t-name{font-size:11px;line-height:1.16}
  .t-lead{display:none}
  .t-do{display:none}
  .t-foot{padding-top:6px;gap:5px}
  .t-dots i{width:7px;height:3px}
  .t-trig{display:none}
  .t-cnt{font-size:8.5px;letter-spacing:.04em}
}

/* ── Стрелки, счётчик и полоса прогресса ───────────────────────────────── */
/* Всё это живёт в НИЖНЕЙ ПОЛОСЕ формы (88px на компьютере, 124px на
   телефоне) и масштабируется тем же множителем, что и холст. Поэтому
   стрелка не может налезть на плитку ни при каком окне: полоса пуста
   по построению, а панель стрелок ниже неё или ровно в ней.
   Размеры считаются в calc(), а не zoom: zoom у растянутого на всю
   ширину блока ломает центрирование. */
#deck-nav{
  position:fixed; left:0; right:0; bottom:0; z-index:8000; pointer-events:none;
  display:flex; align-items:center; justify-content:center;
  gap:calc(14px * var(--view-scale,1));
  height:calc(88px * var(--view-scale,1)); padding-bottom:3px;
}
@media (max-width:767px){ #deck-nav{ height:calc(96px * var(--view-scale,1)); } }
#deck-nav>*{pointer-events:auto}
.nav-arrow{
  width:calc(48px * var(--view-scale,1)); height:calc(48px * var(--view-scale,1));
  border-radius:999px; display:flex; align-items:center; justify-content:center;
  font-size:calc(20px * var(--view-scale,1));
  background:var(--card); border:1px solid var(--soft-bd); color:var(--ink);
  transition:background .2s ease,border-color .2s ease,color .2s ease;
}
.nav-arrow:hover{background:var(--pur);border-color:var(--pur);color:#fff}
#counter{
  font-size:calc(12px * var(--view-scale,1)); font-weight:800; letter-spacing:.12em;
  color:var(--muted); min-width:calc(64px * var(--view-scale,1)); text-align:center;
}
#progress{position:fixed;left:0;right:0;bottom:0;height:3px;background:var(--soft-bd);z-index:8000}
#progress-bar{height:100%;width:0;background:linear-gradient(90deg,var(--pur) 0%,var(--org) 100%);transition:width .34s ease}
"""

CSS += r"""
/* ── Карточка сотрудника ───────────────────────────────────────────────── */
/* Карточка — оконный слой, а не содержимое слайда: она не масштабируется
   вместе с холстом и прокручивается внутри себя. Слайд под ней остаётся
   неподвижным, поэтому правило «ничего не листается» не нарушено. */
#pop{position:fixed;inset:0;z-index:9600;display:flex;align-items:center;justify-content:center;padding:18px}
#pop[hidden]{display:none!important}
.pop-card:focus,.pop-card:focus-visible{outline:none}
.pop-scrim{position:absolute;inset:0;background:var(--scrim);opacity:0;transition:opacity .22s ease}
#pop.on .pop-scrim{opacity:1}
.pop-card{
  position:relative; width:min(760px,100%); max-height:min(88dvh,860px); overflow-y:auto;
  overscroll-behavior:contain; background:var(--card); border:1px solid var(--bd);
  border-radius:24px; padding:26px 26px 28px; opacity:0; transform:translateY(14px);
  transition:opacity .22s ease,transform .22s cubic-bezier(.22,1,.36,1);
  scrollbar-width:thin; scrollbar-color:var(--ac) transparent;
}
#pop.on .pop-card{opacity:1;transform:none}
.pop-card::-webkit-scrollbar{width:9px}
.pop-card::-webkit-scrollbar-thumb{background:linear-gradient(180deg,var(--pur),var(--org));border-radius:999px;border:2px solid transparent;background-clip:padding-box}
.pop-x{
  position:absolute;top:14px;right:14px;width:34px;height:34px;border-radius:999px;
  display:flex;align-items:center;justify-content:center;font-size:17px;color:var(--muted);
  border:1px solid transparent;transition:color .2s ease,border-color .2s ease;
}
.pop-x:hover{color:var(--ac);border-color:var(--soft-bd)}
.pop-head{display:flex;align-items:flex-start;gap:16px;padding-right:38px}
.pop-ic{
  flex:0 0 auto;display:flex;align-items:center;justify-content:center;width:62px;height:62px;
  border-radius:19px;font-size:33px;color:#fff;
  background:linear-gradient(135deg,var(--pur) 0%,var(--org) 100%);
}
.pop-id{min-width:0}
.chips-top{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:7px}
.chip{
  display:inline-flex;align-items:center;gap:.35em;padding:4px 9px;border-radius:999px;
  font-size:10px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;
  background:var(--soft);border:1px solid var(--soft-bd);color:var(--muted);white-space:nowrap;
}
.chip-ac{background:var(--ac-s);border-color:var(--ac-l);color:var(--ac)}
.pop-name{font-size:26px;line-height:1.14;font-weight:900;letter-spacing:-.015em;overflow-wrap:break-word}
.pop-en{margin-top:4px;font-size:11.5px;font-weight:600;letter-spacing:.06em;color:var(--muted);opacity:.75}
.pop-mission{margin-top:15px;font-size:14.5px;line-height:1.6;font-weight:500;color:var(--ink);opacity:.86}

.sect{margin-top:20px}
.sect-h{
  display:flex;align-items:center;gap:.55em;font-size:10.5px;font-weight:800;
  letter-spacing:.15em;text-transform:uppercase;color:var(--ac);margin-bottom:9px;
}
.sect-h .ic{font-size:13px}
.sect-h::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,var(--ac-l),transparent)}

/* Конвейер: что входит → что делает → что остаётся */
.flow{display:grid;grid-template-columns:1fr 22px 1fr 22px 1fr;align-items:stretch;gap:0}
.flow-col{padding:13px 13px 12px;border-radius:16px;background:var(--soft);border:1px solid var(--soft-bd);min-width:0}
.flow-col.mid{background:var(--ac-m);border-color:var(--ac-b)}
.flow-h{display:flex;align-items:center;gap:.4em;font-size:9.5px;font-weight:800;letter-spacing:.11em;text-transform:uppercase;color:var(--muted);margin-bottom:9px}
.flow-h .ic{font-size:12px;color:var(--ac)}
.flow-col ul{list-style:none;display:grid;gap:6px}
.flow-col li{
  display:flex;align-items:flex-start;gap:.5em;font-size:12px;line-height:1.34;
  font-weight:600;color:var(--ink);opacity:.85;overflow-wrap:break-word;
}
.flow-col li::before{content:'';flex:0 0 auto;width:5px;height:5px;border-radius:50%;background:var(--ac);margin-top:.42em;opacity:.75}
.flow-ar{display:flex;align-items:center;justify-content:center;color:var(--ac);font-size:15px;opacity:.6}

/* Две шкалы: самостоятельность и класс действия */
.meters{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.meter{padding:12px 13px;border-radius:16px;background:var(--soft);border:1px solid var(--soft-bd)}
.meter-h{font-size:9.5px;font-weight:800;letter-spacing:.11em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.meter-seg{display:flex;gap:4px;margin-bottom:8px}
.meter-seg i{flex:1;height:7px;border-radius:3px;background:var(--soft-bd);display:block}
.meter-seg i.on{background:var(--ac)}
.meter-seg.warm i.on{background:var(--org)}
.meter-v{font-size:12.5px;font-weight:800;line-height:1.3;overflow-wrap:break-word}

/* Строки-акценты: участие человека и ограничение */
.row{display:flex;align-items:flex-start;gap:11px;padding:12px 14px;border-radius:16px;margin-top:12px}
.row .ic{font-size:19px;flex:0 0 auto;margin-top:1px}
.row-t{font-size:9.5px;font-weight:800;letter-spacing:.11em;text-transform:uppercase;margin-bottom:4px;opacity:.72}
.row-v{font-size:12.8px;line-height:1.45;font-weight:600}
.row-human{background:rgba(139,92,246,.10);border:1px solid rgba(139,92,246,.26);color:var(--ink)}
.row-human .ic{color:var(--pur)}
.row-guard{background:rgba(249,115,22,.11);border:1px solid rgba(249,115,22,.30);color:var(--ink)}
.row-guard .ic{color:var(--org)}

.chips-wrap{display:flex;flex-wrap:wrap;gap:7px}
.chip-lg{
  display:inline-flex;align-items:center;gap:.4em;padding:7px 12px;border-radius:999px;
  font-size:12px;font-weight:700;background:var(--soft);border:1px solid var(--soft-bd);
  color:var(--ink);opacity:.9;letter-spacing:0;text-transform:none;
}
.chip-lg .ic{font-size:13px;color:var(--ac);opacity:.85}
.chip-next{background:var(--ac-m);border-color:var(--ac-b)}

.roles{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:7px}
.roles li{display:flex;align-items:center;gap:.6em;padding:9px 12px;border-radius:12px;background:var(--soft);border:1px solid var(--soft-bd);font-size:12.5px;font-weight:700;line-height:1.25;overflow-wrap:break-word}
.roles .r-n{flex:0 0 auto;font-size:10px;font-weight:800;letter-spacing:.06em;color:var(--ac);opacity:.8}
@media (max-width:767px){ .roles{grid-template-columns:1fr} }

.pop-nav{display:flex;align-items:center;justify-content:center;gap:14px;margin-top:22px;padding-top:16px;border-top:1px solid var(--soft-bd)}
.pop-nav button{display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:999px;border:1px solid var(--soft-bd);background:var(--soft);color:var(--ink);font-size:15px;transition:background .2s ease,border-color .2s ease,color .2s ease}
.pop-nav button:hover{background:var(--ac);border-color:var(--ac);color:#fff}
.pop-nav span{font-size:11px;font-weight:800;letter-spacing:.12em;color:var(--muted)}

@media (max-width:767px){
  #pop{padding:10px}
  .pop-card{width:100%;max-height:92dvh;padding:20px 16px 22px;border-radius:20px}
  .pop-head{gap:12px;padding-right:34px}
  .pop-ic{width:50px;height:50px;border-radius:16px;font-size:27px}
  .pop-name{font-size:20px}
  .pop-mission{font-size:13px;margin-top:13px}
  .flow{grid-template-columns:1fr;gap:0}
  .flow-ar{height:20px;transform:rotate(90deg)}
  .meters{grid-template-columns:1fr}
  .sect{margin-top:17px}
}

/* ── Панель «Текст к слайду»: дикторский текст семинара ────────────────── */
:root{--notes-w:clamp(340px,33vw,560px)}
#notes-panel{
  position:fixed;top:0;left:0;height:100dvh;width:var(--notes-w);z-index:9500;
  display:flex;flex-direction:column;background:var(--card);color:var(--ink);
  border-right:1px solid var(--bd);transform:translateX(-101%);visibility:hidden;
  transition:transform .38s cubic-bezier(.22,1,.36,1),visibility 0s linear .38s;
}
body.notes-open #notes-panel{transform:none;visibility:visible;transition:transform .38s cubic-bezier(.22,1,.36,1),visibility 0s}
@media (prefers-reduced-motion:reduce){#notes-panel{transition:none}}
.notes-head{
  flex:0 0 auto;display:flex;align-items:flex-start;justify-content:space-between;gap:.75rem;
  padding:calc((clamp(2.3rem,9vw,3.2rem) + clamp(1.5rem,5vw,2.3rem)) * var(--view-scale,1)) clamp(1rem,2.6vw,1.6rem) .85rem;
  border-bottom:1px solid var(--soft-bd);
  background:linear-gradient(180deg,rgba(139,92,246,.08),transparent);
}
#notes-close{flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;width:2rem;height:2rem;font-size:1.25rem;color:var(--muted);transition:color .2s ease}
#notes-close:hover{color:var(--pur)}
.notes-meta{min-width:0;padding-top:.15rem}
.notes-counter{display:inline-block;font-size:10.5px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--pur);margin-bottom:.3rem}
.notes-title{font-size:1.12rem;font-weight:800;line-height:1.28;overflow-wrap:break-word}
.notes-body{
  flex:1 1 auto;min-height:0;overflow-y:auto;overscroll-behavior:contain;
  padding:1.2rem clamp(1rem,2.6vw,1.6rem) 3rem;
  scrollbar-width:thin;scrollbar-color:var(--pur) transparent;
}
.notes-body::-webkit-scrollbar{width:9px}
.notes-body::-webkit-scrollbar-thumb{background:linear-gradient(180deg,var(--pur),var(--org));border-radius:999px;border:2px solid transparent;background-clip:padding-box}
.notes-body p{margin:0 0 .95em;font-size:.94rem;line-height:1.72;color:var(--ink);opacity:.85;overflow-wrap:break-word}
.n-h{margin:1.5em 0 .7em;font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--pur);display:flex;align-items:center;gap:.6rem}
.n-h::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(139,92,246,.35),transparent)}
.notes-body>*:first-child{margin-top:0}
.n-item{margin:0 0 .7rem;padding:.8rem .95rem;border-radius:.9rem;background:var(--soft);border:1px solid var(--soft-bd)}
.n-item .n-name{display:block;font-size:.8rem;font-weight:800;letter-spacing:.02em;color:var(--pur);margin-bottom:.35rem}
.n-item.alt{background:rgba(249,115,22,.08);border-color:rgba(249,115,22,.22)}
.n-item.alt .n-name{color:var(--org)}
.n-item p{margin:0;font-size:.9rem}
.n-lead{margin:0 0 1.1em;padding:.85rem 1rem;border-left:3px solid var(--org);border-radius:0 .7rem .7rem 0;background:rgba(249,115,22,.09)}
.n-lead p{margin:0}
@media (max-width:767px){
  #notes-panel{width:100%;border-right:none}
  .notes-body p{font-size:.88rem}
}
body.notes-open .nav-arrow{opacity:.35}
@media (max-width:767px){ body.notes-open .nav-arrow{display:none} }
"""


# ── Скрипты страницы ──────────────────────────────────────────────────────

JS_THEME = r"""
(function(){
  function apply(dark){ document.documentElement.classList.toggle('dark', !!dark); }
  var urlT = null;
  try { urlT = new URLSearchParams(location.search).get('theme'); } catch (e) {}
  if (urlT === 'dark' || urlT === 'light') { apply(urlT === 'dark'); }
  else {
    // Общий ключ всего клиентского пути: семинар открывается в том же тоне,
    // в каком человек оставил лекцию. По умолчанию путь тёмный.
    var saved = null; try { saved = localStorage.getItem('welcome-theme'); } catch (e) {}
    apply(saved !== 'light');
  }
})();
"""

JS_MAIN = r"""
(function(){
  var root = document.documentElement, body = document.body;

  // ══ ДВЕ ФОРМЫ (канон лекций) ═══════════════════════════════════════════
  // Размер холста задаёт CSS: 1380x864 от 768px и 376x844 до неё. JS считает
  // ОДИН множитель --view-scale по той же границе, поэтому смена формы
  // происходит в одном кадре и промежуточных раскладок не существует.
  // Внутри формы ничего не пересобирается: меняется только transform.
  var REF = { pc: { w:1380, h:864 }, mob: { w:376, h:844 } };
  var GAP_X = 24, GAP_Y = 16;   // «чуть-чуть по бокам зазоры» — минимум 12px
  function form(){ return window.innerWidth < 768 ? 'mob' : 'pc'; }

  function fit(){
    var g = REF[form()];
    var panel = document.getElementById('notes-panel');
    var dock = (body.classList.contains('notes-open') && form() === 'pc' && panel)
      ? panel.offsetWidth : 0;
    var availW = Math.max(160, window.innerWidth - dock - GAP_X);
    var availH = Math.max(160, window.innerHeight - GAP_Y);
    root.style.setProperty('--view-scale', String(Math.min(availW / g.w, availH / g.h)));
    root.style.setProperty('--deck-shift', (dock / 2) + 'px');
  }
  // Без дебаунса: при ресайзе меняется одна transform-величина, пересобирать
  // нечего — иначе картинка «дышит» секунду после каждого движения окна.
  window.addEventListener('resize', fit, { passive:true });
  window.addEventListener('orientationchange', fit, { passive:true });
  fit();

  // ══ Колода ═════════════════════════════════════════════════════════════
  var slides = [].slice.call(document.querySelectorAll('.slide'));
  var total = slides.length;
  var cur = 0;
  var bar = document.getElementById('progress-bar');
  var counter = document.getElementById('counter');

  function updateSlides(){
    slides.forEach(function(s, i){ s.classList.toggle('is-on', i === cur); });
    if (bar) bar.style.width = ((cur + 1) / total * 100) + '%';
    if (counter) counter.textContent = (cur + 1) + ' / ' + total;
    try {
      if (('#s' + (cur + 1)) !== location.hash)
        history.replaceState(null, '', '#s' + (cur + 1));
    } catch (e) {}
  }
  function go(i){
    var n = Math.max(0, Math.min(total - 1, i));
    if (n === cur) return;
    cur = n; updateSlides();
    if (window.__notesRender) window.__notesRender(cur);
  }
  window.updateSlides = updateSlides;
  window.nextSlide = function(){ go(cur + 1); };
  window.prevSlide = function(){ go(cur - 1); };
  window.gotoSlide = go;
  window.currentSlide = function(){ return cur; };

  var m = /^#s(\d+)$/.exec(location.hash || '');
  if (m) cur = Math.max(0, Math.min(total - 1, parseInt(m[1], 10) - 1));
  updateSlides();

  document.getElementById('nav-prev').addEventListener('click', window.prevSlide);
  document.getElementById('nav-next').addEventListener('click', window.nextSlide);

  document.addEventListener('keydown', function(e){
    if (window.__popOpen && window.__popOpen()) return;      // карточка сама ловит стрелки
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === ' ')
      { e.preventDefault(); window.nextSlide(); }
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp')
      { e.preventDefault(); window.prevSlide(); }
    else if (e.key === 'Home'){ e.preventDefault(); go(0); }
    else if (e.key === 'End'){ e.preventDefault(); go(total - 1); }
  });

  // Свайп: длинный жест листает, короткий — это нажатие на плитку.
  (function(){
    var sx = 0, sy = 0, st = 0, tracking = false;
    var THRESH = 45, SLOPE = 1.25;
    function excluded(t){
      if (!t || !t.closest) return false;
      return !!(t.closest('#pop') || t.closest('#notes-panel') || t.closest('.nav-arrow'));
    }
    document.addEventListener('touchstart', function(e){
      if (e.touches.length !== 1 || excluded(e.target)) { tracking = false; return; }
      tracking = true; sx = e.touches[0].clientX; sy = e.touches[0].clientY; st = Date.now();
    }, { passive:true });
    document.addEventListener('touchend', function(e){
      if (!tracking) return; tracking = false;
      var t = e.changedTouches && e.changedTouches[0];
      if (!t || (Date.now() - st) > 800) return;
      var dx = t.clientX - sx, dy = t.clientY - sy;
      var adx = Math.abs(dx), ady = Math.abs(dy);
      if (adx < THRESH && ady < THRESH) return;
      if (adx >= ady * SLOPE) { if (dx < 0) window.nextSlide(); else window.prevSlide(); }
      else if (ady >= adx * SLOPE) { if (dy < 0) window.nextSlide(); else window.prevSlide(); }
    }, { passive:true });
  })();

  // Показываем колоду только когда шрифты доехали и масштаб посчитан:
  // иначе виден кадр с чужой метрикой шрифта и другой раскладкой строк.
  function reveal(){ fit(); body.classList.add('fit-ready'); }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(reveal).catch(reveal);
  else reveal();
  window.addEventListener('load', reveal);
  setTimeout(reveal, 1200);
})();
"""

JS_POP = r"""
(function(){
  var dataEl = document.getElementById('seminar-data');
  if(!dataEl) return;
  var DECK = {};
  try { DECK = JSON.parse(dataEl.textContent || '{}'); } catch(e){ return; }

  var AUTO = DECK.autonomy || [], RISK = DECK.risk || [];
  var pop = document.getElementById('pop');
  var card = document.getElementById('pop-card');
  var opener = null, seq = [], seqIdx = 0;

  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){
    return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c]; }); }
  function ic(name, cls){ return '<svg class="' + (cls || 'ic') + '" aria-hidden="true"><use href="#i-' + esc(name) + '"></use></svg>'; }
  function chips(list, cls, icon){
    return '<div class="chips-wrap">' + (list || []).map(function(v){
      return '<span class="chip-lg ' + (cls || '') + '">' + (icon ? ic(icon) : '') + esc(v) + '</span>';
    }).join('') + '</div>';
  }
  function seg(level, count, warm){
    var out = '<div class="meter-seg' + (warm ? ' warm' : '') + '">';
    for (var i = 0; i < count; i++) out += '<i class="' + (i <= level ? 'on' : '') + '"></i>';
    return out + '</div>';
  }
  function col(head, icon, items, mid){
    return '<div class="flow-col' + (mid ? ' mid' : '') + '">' +
      '<div class="flow-h">' + ic(icon) + esc(head) + '</div><ul>' +
      (items || []).map(function(v){ return '<li>' + esc(v) + '</li>'; }).join('') + '</ul></div>';
  }

  function rolesBlock(list){
    return '<ol class="roles">' + (list || []).map(function(v, k){
      return '<li><span class="r-n">' + (k < 9 ? '0' : '') + (k + 1) + '</span>' + esc(v) + '</li>';
    }).join('') + '</ol>';
  }

  function render(t){
    var isDom = !!(t.roles && t.roles.length);
    var a = Math.max(0, Math.min(4, t.autonomy | 0));
    var r = Math.max(0, Math.min(4, t.risk | 0));
    var nav = seq.length > 1
      ? '<div class="pop-nav"><button type="button" id="pop-prev" aria-label="Предыдущая карточка">' + ic('arrow-left') + '</button>' +
        '<span>' + (seqIdx + 1) + ' / ' + seq.length + '</span>' +
        '<button type="button" id="pop-next" aria-label="Следующая карточка">' + ic('arrow-right') + '</button></div>'
      : '';
    var head =
      '<button class="pop-x" type="button" data-close aria-label="Закрыть">' + ic('x') + '</button>' +
      '<div class="pop-head"><span class="pop-ic">' + ic(t.icon || 'circle') + '</span>' +
        '<div class="pop-id"><div class="chips-top">' +
          '<span class="chip chip-ac">' + esc(t.dom || '') + '</span>' +
          (t.no ? '<span class="chip">' + esc(t.no) + '</span>' : '') +
          (t.trigger ? '<span class="chip">' + esc(t.trigger) + '</span>' : '') +
        '</div><h3 class="pop-name" id="pop-name">' + esc(t.ru) + '</h3>' +
        (t.en ? '<div class="pop-en">' + esc(t.en) + '</div>' : '') + '</div></div>' +
      '<p class="pop-mission">' + esc(t.mission) + '</p>';

    var middle;
    if (isDom){
      middle =
        '<div class="sect"><div class="sect-h">' + ic('squares-four') + 'Десять ролей направления</div>' +
          rolesBlock(t.roles) + '</div>';
    } else {
      middle =
        '<div class="sect"><div class="sect-h">' + ic('arrow-fat-line-right') + 'Как устроена работа</div>' +
          flowBlock(t) + '</div>' +
        '<div class="sect"><div class="sect-h">' + ic('gauge') + 'Самостоятельность и цена ошибки</div>' +
          '<div class="meters">' +
            '<div class="meter"><div class="meter-h">Насколько действует сам</div>' + seg(a, 5, false) +
              '<div class="meter-v">' + esc(AUTO[a] || '') + '</div></div>' +
            '<div class="meter"><div class="meter-h">Что меняет в мире</div>' + seg(r, 5, true) +
              '<div class="meter-v">' + esc(RISK[r] || '') + '</div></div>' +
          '</div>' +
          '<div class="row row-human">' + ic('user-focus') +
            '<div><div class="row-t">Где включается человек</div><div class="row-v">' + esc(t.human) + '</div></div></div>' +
          '<div class="row row-guard">' + ic('shield-warning') +
            '<div><div class="row-t">Чего делать нельзя</div><div class="row-v">' + esc(t.guard) + '</div></div></div>' +
        '</div>' +
        '<div class="sect"><div class="sect-h">' + ic('target') + 'Чем меряют пользу</div>' + chips(t.metrics, '', 'target') + '</div>' +
        '<div class="sect"><div class="sect-h">' + ic('wrench') + 'С чем работает</div>' + chips(t.tools, '', 'wrench') + '</div>';
    }

    card.innerHTML = head + middle +
      '<div class="sect"><div class="sect-h">' + ic('arrow-right') +
        (isDom ? 'С чего начинается направление' : 'Передаёт дальше') + '</div>' +
        chips(t.handoffs, 'chip-next', 'caret-right') + '</div>' + nav;
    card.scrollTop = 0;
    var p = document.getElementById('pop-prev'), n = document.getElementById('pop-next');
    if (p) p.addEventListener('click', function(){ step(-1); });
    if (n) n.addEventListener('click', function(){ step(1); });
  }

  // Конвейер: три колонки «что приходит → что делает → что остаётся».
  function flowBlock(t){
    return '<div class="flow">' +
      col('Что приходит', 'sign-in', t['in'], false) +
      '<div class="flow-ar">' + ic('caret-right') + '</div>' +
      col('Что делает', 'gear-fine', t['do'], true) +
      '<div class="flow-ar">' + ic('caret-right') + '</div>' +
      col('Что остаётся', 'package', t.out, false) + '</div>';
  }

  function step(d){
    if (!seq.length) return;
    seqIdx = (seqIdx + d + seq.length) % seq.length;
    render(seq[seqIdx]);
  }

  function open(slideIdx, tileIdx, el){
    var s = (DECK.slides || [])[slideIdx];
    if (!s) return;
    seq = s.tiles || []; seqIdx = tileIdx; opener = el || null;
    pop.classList.toggle('acc-warm', slideIdx % 2 === 1);
    render(seq[seqIdx]);
    pop.hidden = false;
    requestAnimationFrame(function(){ pop.classList.add('on'); });
    card.focus();
  }
  function close(){
    pop.classList.remove('on');
    setTimeout(function(){ pop.hidden = true; card.innerHTML = ''; seq = []; }, 200);
    if (opener && opener.focus) opener.focus();
    opener = null;
  }
  window.__popOpen = function(){ return !pop.hidden; };

  document.addEventListener('click', function(e){
    var t = e.target.closest ? e.target.closest('.tile') : null;
    if (t){ open(+t.getAttribute('data-s'), +t.getAttribute('data-t'), t); return; }
    if (!pop.hidden && e.target.closest && (e.target.closest('[data-close]') || e.target.closest('.pop-scrim'))) close();
  });
  document.addEventListener('keydown', function(e){
    if (pop.hidden) return;
    if (e.key === 'Escape'){ e.preventDefault(); close(); }
    else if (e.key === 'ArrowRight'){ e.preventDefault(); step(1); }
    else if (e.key === 'ArrowLeft'){ e.preventDefault(); step(-1); }
  });
})();
"""

JS_NOTES = r"""
(function(){
  var panel = document.getElementById('notes-panel');
  var toggle = document.getElementById('notes-toggle');
  var closeB = document.getElementById('notes-close');
  var bodyEl = document.getElementById('notes-body');
  var titleEl = document.getElementById('notes-title');
  var cntEl = document.getElementById('notes-counter');
  var dataEl = document.getElementById('slide-notes');
  if (!panel || !toggle || !dataEl) return;

  var NOTES = [];
  try { NOTES = JSON.parse(dataEl.textContent || '[]'); } catch(e){ NOTES = []; }
  if (!NOTES.length){ toggle.style.display = 'none'; return; }

  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){
    return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c]; }); }

  function render(i){
    var n = NOTES[i] || {};
    cntEl.textContent = 'Слайд ' + (i + 1) + ' / ' + NOTES.length;
    titleEl.textContent = n.title || '';
    var html = '';
    if (n.lead) html += '<div class="n-lead"><p>' + esc(n.lead) + '</p></div>';
    (n.paras || []).forEach(function(t){ html += '<p>' + esc(t) + '</p>'; });
    if ((n.items || []).length){
      html += '<div class="n-h">Текст по плиткам</div>';
      html += (n.items || []).map(function(it, k){
        return '<div class="n-item' + (k % 2 ? ' alt' : '') + '">' +
          '<span class="n-name">' + esc(it.ru) + '</span><p>' + esc(it.text) + '</p></div>';
      }).join('');
    }
    if ((n.outro || []).length){
      html += '<div class="n-h">В заключение</div>';
      (n.outro || []).forEach(function(t){ html += '<p>' + esc(t) + '</p>'; });
    }
    bodyEl.innerHTML = html || '<p style="opacity:.55">К этому слайду текста нет.</p>';
    bodyEl.scrollTop = 0;
  }
  window.__notesRender = function(i){
    if (document.body.classList.contains('notes-open')) render(i);
  };

  function setOpen(open){
    document.body.classList.toggle('notes-open', open);
    panel.setAttribute('aria-hidden', open ? 'false' : 'true');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) render(window.currentSlide ? window.currentSlide() : 0);
    // Ширина сцены изменилась — пересчитать масштаб холста в том же кадре
    // и ещё раз после анимации панели.
    window.dispatchEvent(new Event('resize'));
    setTimeout(function(){ window.dispatchEvent(new Event('resize')); }, 400);
  }
  toggle.addEventListener('click', function(){ setOpen(!document.body.classList.contains('notes-open')); });
  closeB.addEventListener('click', function(){ setOpen(false); });
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape' && document.body.classList.contains('notes-open') && window.__popOpen && !window.__popOpen())
      setOpen(false);
  });
  ['touchstart','touchmove','touchend'].forEach(function(ev){
    panel.addEventListener(ev, function(e){ e.stopPropagation(); }, { passive:true });
  });
})();
"""


# ── Сборка страницы ───────────────────────────────────────────────────────

SLIDE_META = {
    "map": dict(
        kicker="Семинар к лекции 1", icon="squares-four",
        title="Сто ИИ-сотрудников",
        sub=("Десять направлений по десять ролей. Это процессы, построенные вокруг ИИ "
             "с самого начала: из них собирается компания, которая ставит запуск продуктов "
             "на поток. Нажмите на плитку — откроется состав направления."),
        sub_mob="Нажмите на плитку — откроется состав направления.",
    ),
    "assembly": dict(
        kicker="Сборка", icon="puzzle-piece",
        title="Из ста ролей — компания",
        sub=None,
    ),
    "finale": dict(
        kicker="Что дальше", icon="rocket-launch",
        title="Ваш агент",
        sub=None,
    ),
}


def dots(level, count=5):
    return "".join('<i class="%s"></i>' % ("on" if i <= level else "") for i in range(count))


def tile_html(s_idx, t_idx, t, show_lead=True):
    lead = ('<span class="t-lead">%s</span>' % esc(t["lead"])) if (show_lead and t.get("lead")) else ""
    steps = (t.get("do") or [])[:3]
    do = ('<span class="t-do">%s</span>' % "".join("<i>%s</i>" % esc(x) for x in steps)) if steps else ""
    trig = ('<span class="t-trig">%s</span>' % esc(t["trigger"])) if t.get("trigger") else ""
    if t.get("roles"):
        # У плитки направления шкалы самостоятельности нет: это не сотрудник,
        # а группа из десяти. В подвале — сколько ролей внутри.
        foot = '<span class="t-cnt">%d ролей внутри</span>' % len(t["roles"])
    else:
        level = max(0, min(4, int(t.get("autonomy", 0))))
        foot = '<span class="t-dots">%s</span>%s' % (dots(level), trig)
    return (
        '<button class="tile" type="button" data-s="%d" data-t="%d" aria-label="%s — открыть карточку">'
        '<span class="t-no">%02d</span>'
        '<span class="t-ic">%s</span>'
        '<span class="t-name">%s</span>%s%s'
        '<span class="t-foot">%s</span>'
        "</button>"
    ) % (s_idx, t_idx, esc(t["ru"]), t_idx + 1, ic(t.get("icon", "circle")),
         esc(t["ru"]), lead, do, foot)


def slide_html(idx, meta, tiles):
    # Соседние слайды чередуют фиолетовый и оранжевый акцент: иначе
    # тринадцать одинаковых сеток сливаются в одну.
    warm = " acc-warm" if idx % 2 else ""
    sub = ""
    if meta.get("sub"):
        sub += '<p class="s-sub pc">%s</p>' % esc(meta["sub"])
    if meta.get("sub_mob"):
        sub += '<p class="s-sub mob">%s</p>' % esc(meta["sub_mob"])
    body = "".join(tile_html(idx, i, t) for i, t in enumerate(tiles))
    return (
        '<section class="slide%s" data-i="%d">'
        '<div class="s-head"><div class="s-kicker">%s%s</div>'
        '<h2 class="s-title" data-slide-title>%s</h2>%s</div>'
        '<div class="grid">%s</div></section>'
    ) % (warm, idx, ic(meta.get("icon", "circle")), esc(meta["kicker"]),
         esc(meta["title"]), sub, body)


def paragraphs(text, per=3):
    """Длинный монолог режем на абзацы по несколько предложений: сплошная
    простыня в панели не читается, а диктору нужны точки для дыхания."""
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    out, buf = [], []
    for p in parts:
        buf.append(p)
        if len(buf) >= per:
            out.append(" ".join(buf))
            buf = []
    if buf:
        out.append(" ".join(buf))
    return out


def build():
    global ICONS
    ICONS = read_json("icons.json")

    data = {k: read_json("data-%s.json" % k) for k in DECK_ORDER if k != "map"}
    speech = {k: read_json("speech-%s.json" % k) for k in DECK_ORDER if k != "map"}
    speech["intro"] = read_json("speech-intro.json")

    # Плитки карты — сами направления: у них не конвейер, а состав из десяти ролей.
    map_tiles = []
    for i, key in enumerate(DOMAIN_ORDER):
        d = data[key]
        map_tiles.append({
            "ru": d["ru"], "en": d["en"], "icon": d["icon"], "lead": d["line"],
            "mission": d["blurb"], "roles": [t["ru"] for t in d["tiles"]],
            # На плитке направления показываем три роли из десяти — чтобы
            # карта читалась и без открытия карточки.
            "do": [t["ru"] for t in d["tiles"][:3]],
            "handoffs": [t["ru"] for t in d["tiles"][:3]],
            "dom": "Направление %d из 10" % (i + 1), "no": "10 ролей",
            "autonomy": 2, "trigger": "",
        })

    slides, deck_tiles, notes = [], [], []

    # ── Слайд 1: карта направлений ───────────────────────────────────────
    slides.append(slide_html(0, SLIDE_META["map"], map_tiles))
    deck_tiles.append({"key": "map", "tiles": map_tiles})
    intro = speech["intro"]["intro"]
    notes.append({
        "title": "Вступление: карта из ста ролей",
        "lead": "Слайд открывает семинар. Дальше — десять направлений по десять ролей.",
        "paras": paragraphs(intro, 3),
        "items": [],
    })

    # ── Слайды 2-11: направления ─────────────────────────────────────────
    for i, key in enumerate(DOMAIN_ORDER):
        d, sp = data[key], speech[key]
        idx = i + 1
        tiles = []
        for t in d["tiles"]:
            t = dict(t)
            t["dom"] = d["ru"]
            t["no"] = "№ %d из 100" % (i * 10 + int(t["n"]))
            tiles.append(t)
        meta = dict(kicker="Направление %d из 10" % idx, icon=d["icon"],
                    title=d["ru"], sub=d["blurb"], sub_mob=d["line"])
        slides.append(slide_html(idx, meta, tiles))
        deck_tiles.append({"key": key, "tiles": tiles})
        notes.append({
            "title": d["ru"],
            "lead": sp["intro"],
            "items": [{"ru": it["ru"], "text": it["text"]} for it in sp["items"]],
        })

    # ── Слайды 12-13: сборка компании и финал ────────────────────────────
    for key in ("assembly", "finale"):
        d, sp = data[key], speech[key]
        idx = len(slides)
        tiles = []
        for t in d["tiles"]:
            t = dict(t)
            t["dom"] = d["ru"]
            t["no"] = ""
            tiles.append(t)
        meta = dict(SLIDE_META[key])
        meta["sub"] = d["blurb"]
        meta["sub_mob"] = d["line"]
        slides.append(slide_html(idx, meta, tiles))
        deck_tiles.append({"key": key, "tiles": tiles})
        note = {
            "title": meta["title"],
            "lead": sp["intro"],
            "items": [{"ru": it["ru"], "text": it["text"]} for it in sp["items"]],
        }
        if sp.get("outro"):
            note["outro"] = paragraphs(sp["outro"], 3)
        notes.append(note)

    used = set(UI_ICONS)
    for s in deck_tiles:
        for t in s["tiles"]:
            used.add(t.get("icon", "circle"))
    missing = sorted(n for n in used if n not in ICONS)
    if missing:
        sys.exit("значков нет в icons.json: %s (обнови: --icons DIR)" % ", ".join(missing))

    deck_data = {
        "autonomy": AUTONOMY, "risk": RISK,
        "slides": [{"key": s["key"], "tiles": s["tiles"]} for s in deck_tiles],
    }

    html = PAGE.replace("__SPRITE__", sprite(used))
    html = html.replace("__CSS__", CSS)
    html = html.replace("__JS_THEME__", JS_THEME)
    html = html.replace("__JS_MAIN__", JS_MAIN)
    html = html.replace("__JS_POP__", JS_POP)
    html = html.replace("__JS_NOTES__", JS_NOTES)
    html = html.replace("__SLIDES__", "\n".join(slides))
    html = html.replace("__DECK_DATA__", json.dumps(deck_data, ensure_ascii=False, separators=(",", ":")))
    html = html.replace("__NOTES_DATA__", json.dumps(notes, ensure_ascii=False, separators=(",", ":")))
    html = html.replace("__ICON_MOON__", ic("moon"))
    html = html.replace("__ICON_BOOK__", ic("book-open-text"))
    html = html.replace("__ICON_LECT__", ic("chalkboard-teacher"))
    html = html.replace("__ICON_PREV__", ic("arrow-left"))
    html = html.replace("__ICON_NEXT__", ic("arrow-right"))
    html = html.replace("__ICON_X__", ic("x"))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("собрано: %s — %d слайдов, %d плиток, %.0f КБ"
          % (os.path.relpath(OUT, ROOT), len(slides),
             sum(len(s["tiles"]) for s in deck_tiles), len(html) / 1024))


WPM = 135.0   # спокойный темп дикторской начитки по-русски


def _mmss(words):
    sec = int(round(words / WPM * 60))
    return "%d:%02d" % (sec // 60, sec % 60)


def speech_md():
    """Собрать дикторский текст семинара одним файлом для озвучки."""
    data = {k: read_json("data-%s.json" % k) for k in DECK_ORDER if k != "map"}
    speech = {k: read_json("speech-%s.json" % k) for k in DECK_ORDER if k != "map"}
    speech["intro"] = read_json("speech-intro.json")

    out = ["# Семинар к лекции 1 — «Сто ИИ-сотрудников»",
           "", "Текст для озвучки. Хронометраж считан по темпу %d слов в минуту." % int(WPM),
           "", "---", ""]
    total = 0

    def block(title, text):
        nonlocal total
        w = len(text.split())
        total += w
        out.append("### %s" % title)
        out.append("")
        out.append("*%s · %d слов*" % (_mmss(w), w))
        out.append("")
        out.append(text)
        out.append("")

    out.append("## Слайд 1 — карта из ста ролей")
    out.append("")
    block("Вступление", speech["intro"]["intro"])

    for i, key in enumerate(DOMAIN_ORDER):
        d, sp = data[key], speech[key]
        out.append("## Слайд %d — %s" % (i + 2, d["ru"]))
        out.append("")
        block("Подводка к слайду", sp["intro"])
        for it in sp["items"]:
            block("%d. %s" % (it["n"], it["ru"]), it["text"])

    for n, key in ((12, "assembly"), (13, "finale")):
        d, sp = data[key], speech[key]
        out.append("## Слайд %d — %s" % (n, d["ru"]))
        out.append("")
        block("Подводка к слайду", sp["intro"])
        for it in sp["items"]:
            block("%d. %s" % (it["n"], it["ru"]), it["text"])
        if sp.get("outro"):
            block("Заключительное слово", sp["outro"])

    out.insert(4, "**Итого: %s (%d слов).**" % (_mmss(total), total))
    out.insert(5, "")
    path = os.path.join(DATA_DIR, "speech.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out).rstrip() + "\n")
    print("речь: %s — %s, %d слов" % (os.path.relpath(path, ROOT), _mmss(total), total))


def main():
    if "--icons" in sys.argv:
        refresh_icons(sys.argv[sys.argv.index("--icons") + 1])
        return
    if "--speech" in sys.argv:
        speech_md()
        return
    build()


PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>__TITLE__</title>
    <link rel="icon" href="/favicon.ico" sizes="any">
    <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
    <link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">
<meta name="description" content="__DESC__">
<meta name="theme-color" content="#8B5CF6">
<meta name="color-scheme" content="dark light">
<meta property="og:type" content="website">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<meta property="og:image" content="https://andre.technology/automation/1/1_lecture.jpg">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="Andre AIT">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="__TITLE__">
<meta name="twitter:description" content="__DESC__">
<meta name="twitter:image" content="https://andre.technology/automation/1/1_lecture.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>__CSS__</style>
<script>__JS_THEME__</script>
</head>
<body>
__SPRITE__

<header id="lecture-header">
  <a class="lec-logo" href="https://andre.technology" aria-label="На главную">
    <img src="/866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png" alt="AIT">
  </a>
  <div class="lec-right">
    <button id="notes-toggle" class="lec-ctrl lec-lbl" type="button" aria-label="Текст к слайду" aria-expanded="false">__ICON_BOOK__<span>Текст</span></button>
    <a class="lec-ctrl lec-lbl" href="/automation/1/" aria-label="Вернуться к лекции" title="Вернуться к лекции">__ICON_LECT__<span>Лекция</span></a>
    <button id="lec-theme" class="lec-ctrl" type="button" aria-label="Сменить тему (тёмная/светлая)">__ICON_MOON__</button>
    <a class="lec-consult" href="/automation/bootcamp/">Буткемп</a>
  </div>
</header>

<div id="stage">
  <div id="deck">
__SLIDES__
  </div>
</div>

<div id="deck-nav">
  <button id="nav-prev" class="nav-arrow" type="button" aria-label="Предыдущий слайд">__ICON_PREV__</button>
  <div id="counter" aria-hidden="true"></div>
  <button id="nav-next" class="nav-arrow" type="button" aria-label="Следующий слайд">__ICON_NEXT__</button>
</div>
<div id="progress"><div id="progress-bar"></div></div>

<aside id="notes-panel" aria-hidden="true" aria-label="Текст к слайду">
  <div class="notes-head">
    <div class="notes-meta">
      <span class="notes-counter" id="notes-counter"></span>
      <div class="notes-title" id="notes-title"></div>
    </div>
    <button id="notes-close" type="button" aria-label="Закрыть текст">__ICON_X__</button>
  </div>
  <div class="notes-body" id="notes-body"></div>
</aside>

<div id="pop" hidden>
  <div class="pop-scrim" data-close></div>
  <div class="pop-card" id="pop-card" tabindex="-1" role="dialog" aria-modal="true" aria-labelledby="pop-name"></div>
</div>

<script id="seminar-data" type="application/json">__DECK_DATA__</script>
<script id="slide-notes" type="application/json">__NOTES_DATA__</script>
<script>__JS_MAIN__</script>
<script>__JS_POP__</script>
<script>__JS_NOTES__</script>
<script>
(function(){
  // Тумблер темы: тот же ключ, что у лекции и дорожной карты — путь курса
  // не должен «перекрашиваться» при переходе между страницами.
  var btn = document.getElementById('lec-theme');
  if (!btn) return;
  function sync(){
    var dark = document.documentElement.classList.contains('dark');
    btn.innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-' + (dark ? 'sun' : 'moon') + '"></use></svg>';
  }
  btn.addEventListener('click', function(){
    var dark = document.documentElement.classList.toggle('dark');
    try { localStorage.setItem('welcome-theme', dark ? 'dark' : 'light'); } catch (e) {}
    sync();
  });
  sync();
})();
</script>
</body>
</html>
"""

PAGE = PAGE.replace("__TITLE__", TITLE).replace("__DESC__", DESC)


if __name__ == "__main__":
    main()
