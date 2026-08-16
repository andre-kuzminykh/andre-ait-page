# -*- coding: utf-8 -*-
"""Режим «кино»: видео слева, слайд справа, тёмный фон (эксперимент владельца).

Канон кадра (скрин владельца 2026-08-16): человек занимает левую часть кадра
живьём — не кружком в углу, — а инфографика уезжает в правую колонку на
тёмном фоне. Правый край видео НЕ обрезан линейкой: он растворяется в фоне
градиентом, поэтому шва между съёмкой и графикой не видно.

Как это устроено (и почему так, а не иначе):

  * Слайд снимается в УЗКОМ вьюпорте (ширина правой колонки). Портал-подгонка
    на странице считает раскладку от холста формы 1380×864 и сама вписывает
    её в любое окно — значит узкая колонка получается штатным механизмом, а
    не переопределением вёрстки. Ни один файл сайта для этого не меняется.
  * Тёмная палитра приезжает отдельным стилем на время съёмки (как CHROME_OFF
    прячет стрелки). Сайт остаётся светлым — эксперимент живёт в рендере.
  * Голову врезает ffmpeg тем же приёмом, что и кружок, только маска другая:
    вместо круга — прямоугольник с градиентом по правому краю (alphamerge).

Геометрия собрана в константах ниже — это единственное место, где её правят.
"""
import os

W, H = 1920, 1080

# ── Геометрия кадра ───────────────────────────────────────────────────────
# Видеопанель во всю высоту кадра (правка владельца 2026-08-16): 760×1000
# исходника, увеличенные до 820×1080, — те же пропорции 0.76, поэтому рост
# равномерный, лицо не растягивается.
# Ширина ЧЁТНАЯ намеренно. Точный пересчёт даёт 821, но у yuv420p цветовые
# плоскости вдвое меньше яркостной, и нечётная сторона валит фильтр pad
# («Padded dimensions cannot be smaller than input dimensions») — сборка
# падала на кодировании. 820 против 821 — это 0.09% пропорции, не видно.
VIDEO_W, VIDEO_H = 820, H
VIDEO_X, VIDEO_Y = 0, 0
# Растворение правого края. 240px ≈ треть панели: короче — виден «обрыв»
# кадра, длиннее — человек уходит в фон вместе с плечом.
FADE = 240
# Колонка со слайдом начинается там, где кончается видеопанель: правый край
# панели к этому моменту уже полностью растворён в фоне.
PANE_X = VIDEO_W
PANE_W = W - PANE_X

# КАНОН ВЛАДЕЛЬЦА: человек обязан входить в панель ЦЕЛИКОМ по ширине. Значит
# исходник подгоняем ПО ШИРИНЕ и никогда не режем бока — не хватило высоты,
# добираем фоном (он тот же, шва не видно); высоты слишком много — режем
# сверху/снизу, но со сдвигом к голове, чтобы не срезать макушку.
CROP_BIAS_TOP = 0.35
# Допуск притягивания к точной высоте панели (см. pane_graph).
SNAP = 6
# Радиус размытия подложки, которой добирается недостающая высота. Меньше —
# в фоне читается второй, «призрачный» человек; больше — каша из пятен.
BLUR = 30
# Растушёвка стыка резкого кадра с размытой подложкой, px по вертикали.
FEATHER = 90

# Фон кадра. Тот же цвет держит и слайд, и подложка ffmpeg — иначе на стыке
# колонки со слайдом и тёмного поля видна ступенька.
BG = "#0A0A0A"


# ── Тёмная палитра на время съёмки ────────────────────────────────────────
# Порядок правил важен: сначала гасим общий текст, потом возвращаем акценты
# (солнечный и фиолетовый) — иначе заголовок «операционное ядро» побелеет
# вместе с остальным.
CINEMA_CSS = """
html, body, .slide-container { background: %(bg)s !important; }
.slide-container { color: #fff !important; }

/* Карточки: белые плитки светлой темы → графитовые, без теней. */
.slide-container .bg-white,
.slide-container [class*="bg-grayBase"] {
  background: #141416 !important;
  box-shadow: none !important;
}
.slide-container [class*="border-grayBase"] { border-color: rgba(255,255,255,.12) !important; }
.slide-container [class*="shadow"] { box-shadow: none !important; }

/* Текст. Заголовки — чистый белый, проза — приглушённый.
   -webkit-text-fill-color обязателен рядом с каждым color: страница красит
   заголовки именно им (и с !important), а он перебивает color — без этой
   пары вся колонка оставалась чёрной по чёрному. */
.slide-container [class*="text-black"] {
  color: rgba(255,255,255,.68) !important;
  -webkit-text-fill-color: rgba(255,255,255,.68) !important;
}
.slide-container h1, .slide-container h2, .slide-container h3,
.slide-container h1 *, .slide-container h2 *, .slide-container h3 * {
  color: #fff !important;
  -webkit-text-fill-color: #fff !important;
}
/* …кроме градиентных акцентов в заголовках: там заливку рисует
   background-clip:text, и text-fill обязан остаться прозрачным. */
.slide-container h1 .text-solar, .slide-container h2 .text-solar {
  -webkit-text-fill-color: transparent !important;
  color: transparent !important;
}

/* Кружки под иконки внутри карточек — светлее самой карточки, иначе иконка
   тонет: на светлой теме их подложка была серая, а не белая. */
.slide-container .rounded-full[class*="bg-grayBase"],
.slide-container .rounded-full[class*="bg-white"] {
  background: rgba(255,255,255,.08) !important;
}
.slide-container .rounded-full i { color: #fff !important; }

/* Акценты возвращаем последними — они сильнее общего правила по тексту. */
.slide-container .text-solar, .slide-container .text-solar * {
  color: #F97316 !important;
  -webkit-text-fill-color: #F97316 !important;
}
.slide-container [class*="bg-solar"] { background: rgba(249,115,22,.22) !important; }
.slide-container [class*="bg-solar"] i { color: #F97316 !important; }
.slide-container .border-solar { border-color: #F97316 !important; }

/* Бейдж лекции: на тёмном обводка важнее заливки. */
.slide-container .rounded-full[class*="border-grayBase"] p { color: rgba(255,255,255,.75) !important; }
""" % {"bg": BG}


# ── Догон масштаба колонки ────────────────────────────────────────────────
# Раскладка слайда считается в координатах формы 1380×864 и вписывается в
# колонку целиком — а колонка почти квадратная (1099×1080). Из-за разницы
# пропорций контент занимал ~74% ширины и ~40% высоты: воздуха больше, чем
# самого слайда. Догоняем ФАКТИЧЕСКИМ замером: меряем чернила и растягиваем
# content-z transform-ом ровно настолько, чтобы упереться в потолок (ниже),
# но не вылезти. Именно transform, а не zoom: инлайновый zoom принадлежит
# подгонке страницы, перебивать его нельзя, а FX-слой берёт координаты
# через getBoundingClientRect и переживает масштаб без правок.
FILL_W = 0.94          # доля ширины колонки, дальше — впритык к краю
FILL_H = 0.88          # доля высоты кадра
GROW_CAP = 1.6         # выше — интерполяция начинает мылить шрифт
SHRINK_CAP = 0.55      # ниже — подписи в карточках нечитаемы

# Подгон ИТЕРАТИВНЫЙ и умеет уменьшать. Два урока живого прогона:
#   * одного замера мало — после масштаба фактические чернила оказывались
#     шире расчётных, и колонка вылезала за край (слайды 1 и 2 обрезались по
#     бокам на 60-70px). Замер после применения и поправка коэффициента
#     сходятся за 2-3 шага независимо от причины расхождения;
#   * уменьшать нужно не реже, чем увеличивать: слайд 3 («Четыре
#     промышленные революции») вылезал за колонку на 15% САМ, без всякого
#     догона — плотные слайды в узкой колонке не помещаются по построению.
GROW_JS = """
(cfg) => {
  const slide = document.querySelector('.slide-container.opacity-100');
  const c = slide && slide.querySelector('.content-z');
  if (!c) return null;
  const ink = () => {
    let x0 = 1e6, y0 = 1e6, x1 = -1e6, y1 = -1e6;
    c.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width < 1 || r.height < 1) return;
      const cs = getComputedStyle(el);
      if (cs.visibility === 'hidden' || cs.display === 'none') return;
      x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top);
      x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom);
    });
    return { w: x1 - x0, h: y1 - y0 };
  };
  c.style.transform = '';
  c.style.transformOrigin = 'center center';
  let k = 1, box = ink();
  if (!(box.w > 0 && box.h > 0)) return null;
  for (let i = 0; i < 5; i++) {
    box = ink();                                   // чернила КАК ЕСТЬ сейчас
    const need = Math.min(cfg.vw * cfg.fw / box.w, cfg.vh * cfg.fh / box.h);
    if (Math.abs(need - 1) < 0.005) break;         // сошлись
    k = Math.max(cfg.floor, Math.min(k * need, cfg.cap));
    c.style.transform = 'scale(' + k + ')';
  }
  box = ink();
  return { k: k, w: box.w, h: box.h };
}
"""


def grow_args():
    """Параметры для GROW_JS — держим рядом с геометрией, а не в вызове."""
    return {"vw": PANE_W, "vh": H, "fw": FILL_W, "fh": FILL_H,
            "cap": GROW_CAP, "floor": SHRINK_CAP}


def fade_mask(path, w=VIDEO_W, h=VIDEO_H, fade=FADE):
    """Альфа-маска видеопанели: слева непрозрачно, справа плавно в ноль.

    Кривая — smoothstep, а не прямая: у линейного градиента глаз ловит две
    границы (там, где растворение началось, и где кончилось), и панель
    читается как приклеенная полоса.
    """
    from PIL import Image
    solid = w - fade
    img = Image.new("L", (w, h), 255)
    px = img.load()
    for x in range(solid, w):
        t = (x - solid) / float(fade)          # 0 → 1 по ширине растворения
        a = 1.0 - (t * t * (3.0 - 2.0 * t))    # smoothstep, убывающий
        col = int(round(255 * a))
        for y in range(h):
            px[x, y] = col
    img.save(path)
    return path


def overlay_filter(bg_stream="0:v", clip_stream="1:v", mask_stream="2:v",
                   pane_stream=None, graph=None):
    """Фильтр ffmpeg: тёмная подложка + колонка слайда + видеопанель слева.

    pane_stream задаётся, когда колонка снята отдельным кадром (узкий
    вьюпорт); без него подложкой служит уже готовый кадр 1920×1080.
    graph — фрагмент от pane_graph(), отдающий метку [hv].
    """
    parts = []
    base = "[%s]" % bg_stream
    if pane_stream:
        parts.append("%s[%s]overlay=%d:0[base]" % (base, pane_stream, PANE_X))
        base = "[base]"
    parts.append(graph or ("[%s]scale=%d:%d,setsar=1[hv]"
                           % (clip_stream, VIDEO_W, VIDEO_H)))
    parts.append("[hv][%s]alphamerge[pane]" % mask_stream)
    parts.append("%s[pane]overlay=%d:%d:format=auto[v]" % (base, VIDEO_X, VIDEO_Y))
    return ";".join(parts)


def pane_fill_height(src_w, src_h):
    """Высота резкого кадра внутри панели — 0, если добор не нужен.

    Нужна вызывающему, чтобы заранее нарисовать маску растушёвки стыка ровно
    под этот размер.
    """
    if src_w <= 0 or src_h <= 0:
        return 0
    scaled_h = int(round(src_h * VIDEO_W / float(src_w))) // 2 * 2
    if abs(scaled_h - VIDEO_H) <= SNAP or scaled_h > VIDEO_H:
        return 0
    return scaled_h


def feather_mask(path, w, h, soft=FEATHER):
    """Маска резкого кадра: белая внутри, к верхнему и нижнему краю плавно
    уходит в ноль. Тот же smoothstep, что у бокового растворения."""
    from PIL import Image
    img = Image.new("L", (w, h), 255)
    px = img.load()
    soft = max(1, min(soft, h // 2))
    for y in range(soft):
        t = (y + 0.5) / soft
        a = int(round(255 * (t * t * (3.0 - 2.0 * t))))
        for x in range(w):
            px[x, y] = a
            px[x, h - 1 - y] = a
    img.save(path)
    return path


def pane_graph(src_w, src_h, src="1:v", out="hv", feather=None):
    """Граф ffmpeg: исходник → панель VIDEO_W×VIDEO_H, БЕЗ обрезки по ширине.

    Порядок жёсткий: сначала масштаб ПО ШИРИНЕ панели (человек входит в кадр
    целиком — канон владельца), потом добор по высоте:
      * ровно попали (нативный портрет 760×1000 → 820×1080) — один scale;
      * высоты в избытке → crop со сдвигом к голове (CROP_BIAS_TOP): срезать
        стол безопаснее, чем макушку;
      * высоты не хватило → под кадр подкладывается РАЗМЫТАЯ копия его же,
        растянутая «в край». Плоская заливка фоном давала чёрные полосы
        сверху и снизу — панель переставала читаться как кадр во всю высоту
        (замечание владельца по квадратной подложке). Размытие берёт цвет и
        свет той же комнаты, поэтому стык не читается, а сам человек не
        режется и не тянется.
    """
    if src_w <= 0 or src_h <= 0:                     # клип не опознан
        return "[%s]scale=%d:%d,setsar=1[%s]" % (src, VIDEO_W, VIDEO_H, out)
    scaled_h = int(round(src_h * VIDEO_W / float(src_w))) // 2 * 2
    # Притягивание к точной высоте панели: округление до чётного оставляет у
    # портрета 760×1000 ровно 1px полосы, а шов на ровном фоне заметнее, чем
    # искажение в 0.2%, которого глаз не видит.
    if abs(scaled_h - VIDEO_H) <= SNAP:
        return "[%s]scale=%d:%d,setsar=1[%s]" % (src, VIDEO_W, VIDEO_H, out)
    if scaled_h > VIDEO_H:
        y = int(round((scaled_h - VIDEO_H) * CROP_BIAS_TOP))
        return ("[%s]scale=%d:%d,crop=%d:%d:0:%d,setsar=1[%s]"
                % (src, VIDEO_W, scaled_h, VIDEO_W, VIDEO_H, y, out))
    y = (VIDEO_H - scaled_h) // 2
    # Растушёвка стыка: без неё резкий кадр лежит на размытом фоне ровным
    # прямоугольником, и граница читается как рамка. Маску подаём отдельным
    # входом (feather) — она дешевле, чем per-pixel geq на 1500 кадров.
    fg = "[{o}fgv]".format(o=out)
    if feather:
        soft = ("[{o}fgv][{f}]alphamerge[{o}fgs]").format(o=out, f=feather)
        fg = "[{o}fgs]".format(o=out)
    return (
        "[{src}]split=2[{o}bg][{o}fg];"
        "[{o}bg]scale={w}:{h}:force_original_aspect_ratio=increase,"
        "crop={w}:{h},boxblur={blur}:1,eq=brightness=-0.10:saturation=0.85[{o}bgv];"
        "[{o}fg]scale={w}:{sh}[{o}fgv];"
        "{soft}"
        "[{o}bgv]{fg}overlay=0:{y}:format=auto,setsar=1[{o}]"
    ).format(src=src, o=out, w=VIDEO_W, h=VIDEO_H, sh=scaled_h, y=y, blur=BLUR,
             soft=(soft + ";") if feather else "", fg=fg)


def probe_size(ff, path):
    """Размер кадра клипа. ffprobe рядом не всегда есть — читаем из ffmpeg."""
    import re
    import subprocess
    out = subprocess.run([ff, "-hide_banner", "-i", path],
                         capture_output=True, text=True).stderr
    m = re.search(r"Video:.*?,\s*(\d+)x(\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def dark_canvas(ff, path, secs=None):
    """Однотонная подложка кадра — на неё ложатся колонка и видеопанель."""
    from subprocess import run as _run
    _run([ff, "-y", "-loglevel", "error", "-f", "lavfi",
          "-i", "color=c=%s:s=%dx%d" % (BG.lstrip("#"), W, H),
          "-frames:v", "1", path], check=True)
    return path


def viewport():
    """Вьюпорт съёмки слайда — ровно правая колонка кадра."""
    return {"width": PANE_W, "height": H}


def geometry():
    """Сводка геометрии для отчёта в консоль."""
    return ("видео %dx%d с (%d,%d), растворение %dpx · "
            "колонка слайда %dx%d с x=%d · фон %s"
            % (VIDEO_W, VIDEO_H, VIDEO_X, VIDEO_Y, FADE, PANE_W, H, PANE_X, BG))
