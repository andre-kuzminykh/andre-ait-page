#!/bin/sh
# Сжатие mp4 для веба: файл должен открываться с мобильного интернета.
#
# Запуск (положить рядом с видео, хоть на Рабочий стол):
#   sh сжать.sh                 — все mp4/mov в этой папке
#   sh сжать.sh клип.mp4 …      — только названные
#
# Результаты кладутся в подпапку «сжатые/». Оригиналы НЕ трогаются.
#
# Насколько жать — первым словом:
#   sh сжать.sh                 — 720p, файлы легче МИНИМУМ в 10 раз (по умолчанию)
#   sh сжать.sh сильнее         — 540p, примерно в 20 раз
#   sh сжать.sh качество        — 1080p, в 6-8 раз, разрешение не тронуто
#   sh сжать.sh архив           — MOV → MP4 без заметной потери качества:
#                                 разрешение и частота кадров как были, звук
#                                 копируется как есть, если он уже aac
set -e
command -v ffmpeg  >/dev/null || { echo "Нет ffmpeg. macOS: brew install ffmpeg"; exit 1; }
command -v ffprobe >/dev/null || { echo "Нет ffprobe — он ставится вместе с ffmpeg"; exit 1; }

# ── режим ────────────────────────────────────────────────────────────────
# CRF — «постоянное качество»: чем больше число, тем меньше файл. Замерено на
# реальном ролике сайта (1920x1080, 6 c, 24 МБ) метрикой VMAF, где 100 —
# неотличимо от оригинала:
#   1080p crf 26 → 4.6 МБ, VMAF 97.7      720p crf 26 → 2.3 МБ, VMAF 94.6
#   1080p crf 30 → 2.6 МБ, VMAF 92.5      720p crf 28 → 1.7 МБ, VMAF 91.3
# Но одного CRF мало: он держит КАЧЕСТВО, а не размер, и на тяжёлом материале
# даёт всего 7-8 раз вместо десяти. Поэтому размер задаётся кратностью: потолок
# битрейта = битрейт исходника, делённый на RATIO. CRF при этом остаётся полом
# качества — на лёгком материале файл выйдет ещё меньше потолка.
SHORT=720; CRF=26; RATIO=12; MINK=700; MAXCAP=4000
ARCHIVE=0
SKIPK=1200      # ниже этого битрейта файл уже лёгкий, трогать его незачем
case "${1:-}" in
    сильнее|540)   SHORT=540;  CRF=28; RATIO=22; MINK=500; MAXCAP=2500; shift ;;
    качество|1080) SHORT=1080; CRF=26; RATIO=7;  MINK=1200; MAXCAP=8000; shift ;;
    обычно|720)    shift ;;
    # Архив: задача не «сделать лёгким для веба», а «переложить MOV в MP4,
    # чтобы глазом было не отличить». Поэтому кадр не уменьшается, потолка
    # битрейта нет вовсе (размер определяет только CRF 18 — это порог, где
    # разницу с оригиналом на глаз уже не видно), а лёгкие файлы не
    # пропускаются: их всё равно надо переложить в mp4.
    архив|mov|исходник)
        ARCHIVE=1; SHORT=100000; CRF=18; SKIPK=0; shift ;;
esac
OUTDIR="сжатые"
mkdir -p "$OUTDIR"

# Имена берём БЕЗ склейки в одну строку: «клип один.mov» разваливался по
# пробелу на «клип» и «один.mov», и такой файл молча пропускался. Список
# держим в аргументах — единственный способ в POSIX sh сохранить пробелы.
if [ $# -eq 0 ]; then
    set -- *.mp4 *.MP4 *.mov *.MOV *.m4v *.M4V *.mkv *.MKV *.avi *.AVI
fi
# Имя переменной латиницей: dash кириллические не принимает («not found»).
FOUND=0
for f in "$@"; do [ -f "$f" ] && FOUND=$((FOUND+1)); done
[ "$FOUND" -gt 0 ] || { echo "Рядом нет ни одного видеофайла (mp4, mov, m4v, mkv, avi)."; exit 1; }

# Тонемап нужен для съёмки с айфона в HDR: без него на обычном экране картинка
# выцветает. Фильтр есть не в каждой сборке, поэтому проверяем заранее.
HAVE_ZSCALE=$(ffmpeg -hide_banner -filters 2>/dev/null | grep -c " zscale " || true)

if [ "$ARCHIVE" = 1 ]; then
    echo "Режим: архив — разрешение и частота кадров как в исходнике, качество crf $CRF"
else
    echo "Режим: короткая сторона $SHORT, цель — в $RATIO раз легче (crf $CRF как пол качества)"
fi
echo

TOTAL_IN=0; TOTAL_OUT=0; DONE=0; SKIP=0

for f in "$@"; do
    [ -f "$f" ] || continue
    case "$f" in "$OUTDIR"/*) continue ;; esac

    NAME=$(basename "$f")
    OUT="$OUTDIR/${NAME%.*}.mp4"

    W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width  -of csv=p=0 "$f" 2>/dev/null || true)
    H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$f" 2>/dev/null || true)
    if [ -z "$W" ] || [ -z "$H" ]; then
        printf "  — %s: видеодорожки нет, пропускаю\n" "$NAME"
        continue
    fi
    ACODEC=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of csv=p=0 "$f" 2>/dev/null || true)
    CH=$(ffprobe -v error -select_streams a:0 -show_entries stream=channels -of csv=p=0 "$f" 2>/dev/null || true)
    ROT=$(ffprobe -v error -select_streams v:0 -show_entries stream_side_data=rotation -of csv=p=0 "$f" 2>/dev/null | head -1)
    TRC=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of csv=p=0 "$f" 2>/dev/null || true)
    : "${ROT:=0}"

    IN_SZ=$(wc -c < "$f" | tr -d ' ')
    DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null || echo 0)
    IN_KBPS=$(awk -v s="$IN_SZ" -v d="${DUR:-0}" 'BEGIN{ printf "%d", (d>0) ? s*8/d/1000 : 0 }')

    # Уже лёгкий файл жать бессмысленно: легче он почти не станет, а качество
    # упадёт. В режиме «архив» это правило выключено — там цель переложить
    # в mp4, а не выиграть мегабайты.
    if [ "$SKIPK" -gt 0 ] && [ "$IN_KBPS" -gt 0 ] && [ "$IN_KBPS" -lt "$SKIPK" ]; then
        printf "  = %s: уже лёгкий (%s кбит/с) — не трогаю\n" "$NAME" "$IN_KBPS"
        SKIP=$((SKIP+1))
        continue
    fi

    # Кадр с меткой поворота считаем в тех размерах, в каких он виден.
    case "$ROT" in
        90|-90|270|-270) DW=$H; DH=$W ;;
        *)               DW=$W; DH=$H ;;
    esac
    SMALL=$DW
    if [ "$DH" -lt "$DW" ]; then SMALL=$DH; fi

    if [ "$SMALL" -le "$SHORT" ]; then
        SCALE="iw:ih"                       # меньше, чем есть, не увеличиваем
    elif [ "$DW" -lt "$DH" ]; then
        SCALE="$SHORT:-2"                   # вертикаль: тянем ширину
    else
        SCALE="-2:$SHORT"                   # горизонт: тянем высоту
    fi

    VF="scale=$SCALE:flags=lanczos"
    case "$TRC" in
        smpte2084|arib-std-b67)
            if [ "$HAVE_ZSCALE" -gt 0 ]; then
                VF="$VF,zscale=t=linear:npl=100,tonemap=hable:desat=0,zscale=p=bt709:t=bt709:m=bt709:r=tv"
            else
                printf "\n    ⚠︎ %s снят в HDR, а тонемапа в вашей сборке ffmpeg нет — цвета выцветут\n    " "$NAME"
            fi
            ;;
    esac
    VF="$VF,format=yuv420p"

    if [ -z "$ACODEC" ]; then
        AOPT="-an"
    elif [ "$ARCHIVE" = 1 ]; then
        # Звук в архиве не трогаем: если он уже aac, кладём дорожку как есть
        # (бит-в-бит), иначе один раз пережимаем с запасом.
        if [ "$ACODEC" = "aac" ]; then AOPT="-c:a copy"; else AOPT="-c:a aac -b:a 256k"; fi
    elif [ "${CH:-2}" = "1" ]; then
        AOPT="-c:a aac -b:a 80k -ac 1"      # речь под микрофон по сути моно
    else
        AOPT="-c:a aac -b:a 96k"
    fi

    # Потолок под заказанную кратность, но в разумных рамках: на совсем тяжёлом
    # исходнике не опускаемся в кашу, на лёгком — не раздуваем зря.
    MAXK=$(awk -v b="$IN_KBPS" -v r="$RATIO" -v lo="$MINK" -v hi="$MAXCAP" \
        'BEGIN{ v=b/r; if(v<lo) v=lo; if(v>hi) v=hi; printf "%d", v }')
    # В архиве потолка нет: качество держит только CRF, иначе на сложных
    # кадрах (движение, зерно) появилась бы та самая «заметная потеря».
    CAP="-maxrate ${MAXK}k -bufsize $((MAXK*2))k"
    [ "$ARCHIVE" = 1 ] && CAP=""

    printf "  → %s (%s МБ, %s кбит/с)… " "$NAME" \
        "$(awk -v s="$IN_SZ" 'BEGIN{printf "%.1f", s/1048576}')" "$IN_KBPS"

    # -g 60 — ключевой кадр раз в 2 секунды: реже тормозит перемотка, чаще
    # файл толстеет ни за что. +faststart переносит оглавление в начало:
    # без него браузер ждёт закачки целиком, прежде чем показать первый кадр.
    # -map_metadata 0 сохраняет дату съёмки: без неё «Фото» и Finder ставят
    # файлам сегодняшний день и порядок в папке рассыпается.
    ffmpeg -y -loglevel error -nostdin -i "$f" \
        -vf "$VF" \
        -c:v libx264 -preset slow -crf "$CRF" \
        $CAP \
        -profile:v high -level 4.0 -g 60 -keyint_min 30 \
        $AOPT -map_metadata 0 -movflags +faststart "$OUT"

    ERR=$(ffmpeg -v error -i "$OUT" -f null - 2>&1 || true)
    if [ -n "$ERR" ]; then
        echo "ОШИБКА: $(echo "$ERR" | head -1)"
        exit 1
    fi

    OUT_SZ=$(wc -c < "$OUT" | tr -d ' ')
    awk -v a="$IN_SZ" -v b="$OUT_SZ" 'BEGIN{ printf "%.1f МБ, в %.1f раза легче\n", b/1048576, a/b }'
    TOTAL_IN=$((TOTAL_IN+IN_SZ)); TOTAL_OUT=$((TOTAL_OUT+OUT_SZ)); DONE=$((DONE+1))
done

echo
if [ "$DONE" = 0 ]; then
    echo "Сжимать было нечего: пропущено $SKIP файлов (все уже лёгкие)."
else
    awk -v a="$TOTAL_IN" -v b="$TOTAL_OUT" -v n="$DONE" -v s="$SKIP" 'BEGIN{
        printf "Готово: %d шт. — было %.0f МБ, стало %.0f МБ (в %.1f раза легче)\n", n, a/1048576, b/1048576, a/b
        if (s>0) printf "Пропущено как уже лёгкие: %d\n", s
    }'
    echo "Файлы в папке «$OUTDIR», оригиналы на месте."
fi
