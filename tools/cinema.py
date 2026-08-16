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
# Видеопанель 760×1000 (размер владельца, 2026-08-16) — ровно нативный
# портретный клип, без масштабирования: пиксель в пиксель, ничего не мылится.
VIDEO_W, VIDEO_H = 760, 1000
# По вертикали панель центрирована: (1080 − 1000) / 2.
VIDEO_X, VIDEO_Y = 0, (H - VIDEO_H) // 2
# Растворение правого края. 240px ≈ треть панели: короче — виден «обрыв»
# кадра, длиннее — человек уходит в фон вместе с плечом.
FADE = 240
# Колонка со слайдом начинается там, где кончается видеопанель: правый край
# панели к этому моменту уже полностью растворён в фоне.
PANE_X = VIDEO_W
PANE_W = W - PANE_X

# Кадрирование ИСХОДНИКА под панель. Для нативного портрета 760×1000 кроп не
# нужен (CROP = None); строка вида «w:h:x:y» нужна, только когда на входе
# другой формат — например запасной квадрат 720×720 из ветки media.
CROP = None
CROP_SQUARE = "600:720:30:0"

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
                   pane_stream=None, crop=None):
    """Фильтр ffmpeg: тёмная подложка + колонка слайда + видеопанель слева.

    pane_stream задаётся, когда колонка снята отдельным кадром (узкий
    вьюпорт); без него подложкой служит уже готовый кадр 1920×1080.
    crop — строка «w:h:x:y», если исходник не нативного размера панели.
    """
    parts = []
    base = "[%s]" % bg_stream
    if pane_stream:
        parts.append("%s[%s]overlay=%d:0[base]" % (base, pane_stream, PANE_X))
        base = "[base]"
    crop = crop if crop is not None else CROP
    head = "[%s]" % clip_stream
    if crop:
        head += "crop=%s," % crop
    # scale держим всегда: он же приводит клип к панели, если исходник
    # чуть другого размера, и стоит копейки, когда размеры совпали.
    parts.append("%sscale=%d:%d,setsar=1[hv]" % (head, VIDEO_W, VIDEO_H))
    parts.append("[hv][%s]alphamerge[pane]" % mask_stream)
    parts.append("%s[pane]overlay=%d:%d:format=auto[v]" % (base, VIDEO_X, VIDEO_Y))
    return ";".join(parts)


def crop_for(src_w, src_h):
    """Кроп «cover» под панель: None, если пропорции уже совпали.

    Нативный портрет 760×1000 проходит без кропа. Квадрат 720×720 из ветки
    media (запись под кружок) обрезается по бокам — с лёгким сдвигом влево,
    чтобы левая картина вошла целиком, а правая ушла под градиент.
    """
    if src_w <= 0 or src_h <= 0:
        return None
    want = VIDEO_W / float(VIDEO_H)
    have = src_w / float(src_h)
    if abs(have - want) < 0.01:
        return None
    if have > want:                                  # исходник шире — режем бока
        w = int(round(src_h * want)) // 2 * 2
        x = max(0, int(round((src_w - w) * 0.42)))   # 0.42, а не 0.5 — сдвиг влево
        return "%d:%d:%d:0" % (w, src_h, x)
    h = int(round(src_w / want)) // 2 * 2            # исходник уже — режем верх/низ
    y = max(0, (src_h - h) // 2)
    return "%d:%d:0:%d" % (src_w, h, y)


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
