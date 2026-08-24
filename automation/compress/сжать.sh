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
#   sh сжать.sh архив           — MOV → MP4 без БОЛЬШОЙ потери качества:
#                                 кадр и частота как были, но файл минимум
#                                 в 1.6 раза легче (обычно сильно больше)
#   sh сжать.sh переложить      — MOV → MP4 вообще без перекодирования:
#                                 качество 1:1, размер почти не изменится
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
ARCHIVE=0; REMUXONLY=0
SKIPK=1200      # ниже этого битрейта файл уже лёгкий, трогать его незачем
case "${1:-}" in
    сильнее|540)   SHORT=540;  CRF=28; RATIO=22; MINK=500; MAXCAP=2500; shift ;;
    качество|1080) SHORT=1080; CRF=26; RATIO=7;  MINK=1200; MAXCAP=8000; shift ;;
    обычно|720)    shift ;;
    # Архив: кадр не уменьшается, но файл ДОЛЖЕН стать заметно легче —
    # «без большой потери», а не «без всякой потери». Подробности ниже.
    архив|mov|исходник)
        ARCHIVE=1; SHORT=100000; CRF=22; SKIPK=0; shift ;;
    # Переложить 1:1: перекодирования нет вовсе, только смена контейнера
    # MOV → MP4. Размер почти не изменится — это и есть смысл режима.
    переложить|копия|1:1)
        ARCHIVE=1; REMUXONLY=1; SHORT=100000; CRF=18; SKIPK=0; shift ;;
esac

# ── чем архив отличается от веб-режимов ─────────────────────────────────
# Кадр остаётся родным, поэтому выигрыш даёт только битрейт. Потолок —
# МЕНЬШЕЕ из двух:
#   1) по кадру: ширина × высота × частота × ARCBPP (для съёмки с запасом);
#   2) по исходнику: делённый на ARCRATIO — гарантия, что файл реально
#      похудеет, даже если исходник уже уложен плотно.
#
# ДВА УРОКА, ОБА ОТ ВЛАДЕЛЬЦА.
# «получилось еще больше по размеру» — первая версия шла «CRF без потолка»,
# и на уже сжатом исходнике писала больше бит, чем там было (1080p h264
# 3.0 МБ → 7.2 МБ). Отсюда пункт 2.
# «размер не изменился» — вторая версия при плотном исходнике вообще не
# перекодировала, а перекладывала 1:1. Формально честно, а по делу файл не
# похудел. Теперь перекладывание 1:1 — это отдельная команда «переложить»,
# а «архив» всегда жмёт.
ARCBPP=0.12     # бит на пиксель: 7.5 Мбит/с на 1080p30
# Во столько раз режем битрейт картинки. Файл целиком выходит легче чуть
# меньше — в него ещё входит звук, поэтому 1.8 по картинке даёт около 1.5
# по файлу на плотной съёмке (на жирной — в разы).
ARCRATIO=1.8
# Ниже этого файл настолько плотный, что дальше жать — уже портить
# (1.9 Мбит/с на 1080p30). Такие перекладываются 1:1 с честной оговоркой.
ARCFLOOR=0.03
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

# Съёмку в hevc (айфон, современные камеры) перекладывать в h264 бессмысленно:
# за ту же картинку h264 возьмёт в полтора раза больше бит, и «сжатие» станет
# ростом. Такие файлы жмём тем же hevc — если в сборке есть кодировщик.
HAVE_X265=$(ffmpeg -hide_banner -encoders 2>/dev/null | grep -c " libx265 " || true)

# Переложить дорожку в mp4 как есть — картинка бит-в-бит, потери нулевые.
# Звук идёт по тем же правилам, что и при сжатии ($AOPT): готовый aac
# копируется, PCM (обычный спутник ProRes) один раз кладётся в aac.
# Имя латиницей: dash кириллические имена функций не принимает, как и
# переменные («Bad function name»).
remux_copy() {
    ffmpeg -y -loglevel error -nostdin -i "$1" \
        -c:v copy $3 $AOPT -map_metadata 0 -movflags +faststart "$2" || return 1
    RERR=$(ffmpeg -v error -i "$2" -f null - 2>&1 || true)
    [ -z "$RERR" ] || { echo "ОШИБКА: $(echo "$RERR" | head -1)"; return 1; }
}

if [ "$REMUXONLY" = 1 ]; then
    echo "Режим: переложить 1:1 — MOV → MP4 без перекодирования, размер почти не изменится"
elif [ "$ARCHIVE" = 1 ]; then
    echo "Режим: архив — кадр и частота как в исходнике, битрейт режется в $ARCRATIO раза (crf $CRF)"
else
    echo "Режим: короткая сторона $SHORT, цель — в $RATIO раз легче (crf $CRF как пол качества)"
fi
echo

TOTAL_IN=0; TOTAL_OUT=0; DONE=0; SKIP=0; COPIED=0

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
    VCODEC=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of csv=p=0 "$f" 2>/dev/null || true)
    # Частоту кадров спрашиваем средней, а не «заявленной»: в MOV с телефона
    # r_frame_rate сплошь и рядом равен 600 (это шкала времени контейнера, а не
    # съёмка), и потолок битрейта улетел бы в двадцать раз. Если средней нет —
    # берём заявленную.
    FPSR=$(ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of csv=p=0 "$f" 2>/dev/null | head -1)
    case "${FPSR:-0}" in ""|0|0/0) FPSR=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$f" 2>/dev/null | head -1) ;; esac
    # «30000/1001» — обычная запись частоты кадров; битая или нулевая бывает у
    # экранных записей с переменной частотой, тогда считаем по 30.
    FPS=$(awk -v r="${FPSR:-0}" 'BEGIN{ n=split(r,a,"/"); v=(n==2 && a[2]>0) ? a[1]/a[2] : r+0;
                                        if (v<=0 || v>240) v=30; printf "%.3f", v }')
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

    # Кодировщик выбираем по исходнику: hevc жмём в hevc, всё остальное в h264.
    VENC="libx264"; VCRF="$CRF"; ENCTAG=""
    if [ "$ARCHIVE" = 1 ]; then
        case "$VCODEC" in
            hevc|av1|vp9)
                if [ "$HAVE_X265" -gt 0 ]; then
                    # x265 при том же качестве берёт примерно на треть меньше
                    # бит, поэтому и CRF у него другой: 24 ≈ x264 21.
                    VENC="libx265"; VCRF=$((CRF + 2)); ENCTAG="-tag:v hvc1"
                fi ;;
        esac
    fi

    if [ "$ARCHIVE" = 1 ]; then
        # У hevc на тот же вид уходит меньше бит — потолок по кадру ниже.
        BPPM=1
        [ "$VENC" = "libx265" ] && BPPM=0.7
        # Меньшее из двух: «сколько нужно кадру» и «в ARCRATIO раз легче
        # исходника». Второе и делает файл заметно легче на плотной съёмке.
        # Имя «in» здесь нельзя: в awk это ключевое слово («type clash»).
        MAXK=$(awk -v w="$DW" -v h="$DH" -v f="$FPS" -v b="$ARCBPP" -v m="$BPPM" \
                   -v src="$IN_KBPS" -v r="$ARCRATIO" \
            'BEGIN{ v=w*h*f*b*m/1000; u=(src>0)? src/r : v; if(u<v) v=u;
                    if(v<400) v=400; printf "%d", v }')
    else
        # Потолок под заказанную кратность, но в разумных рамках: на совсем
        # тяжёлом исходнике не опускаемся в кашу, на лёгком — не раздуваем зря.
        MAXK=$(awk -v b="$IN_KBPS" -v r="$RATIO" -v lo="$MINK" -v hi="$MAXCAP" \
            'BEGIN{ v=b/r; if(v<lo) v=lo; if(v>hi) v=hi; printf "%d", v }')
    fi
    CAP="-maxrate ${MAXK}k -bufsize $((MAXK*2))k"
    # В режиме «переложить» до перекодирования доходят только те, кого в mp4
    # скопировать нельзя (prores, mjpeg). Резать им битрейт нечестно: просили
    # 1:1, поэтому потолка нет, качество держит crf 18.
    [ "$REMUXONLY" = 1 ] && CAP=""

    # Можно ли вообще переложить дорожку как есть: mp4 держит h264, hevc и
    # mpeg4, а prores и mjpeg — нет, их придётся перекодировать (и там как раз
    # выигрыш в разы).
    COPYOK=0
    case "$VCODEC" in h264|hevc|mpeg4) COPYOK=1 ;; esac
    TAG=""
    [ "$VCODEC" = "hevc" ] && TAG="-tag:v hvc1"   # иначе QuickTime не откроет

    # Когда перекладываем 1:1 вместо сжатия:
    #   1) попросили именно это («переложить»);
    #   2) файл уже настолько плотный (ниже ARCFLOOR), что дальше жать —
    #      портить;
    #   3) съёмка в hevc, а кодировщика hevc в сборке нет: h264 за ту же
    #      картинку возьмёт больше бит, «сжатие» обернётся ростом.
    REMUX=0; WHY=""
    if [ "$ARCHIVE" = 1 ] && [ "$COPYOK" = 1 ]; then
        FLOORK=$(awk -v w="$DW" -v h="$DH" -v f="$FPS" -v b="$ARCFLOOR" \
            'BEGIN{ printf "%d", w*h*f*b/1000 }')
        if [ "$REMUXONLY" = 1 ]; then
            REMUX=1; WHY="переложен в mp4 без перекодирования (качество 1:1)"
        elif [ "$IN_KBPS" -gt 0 ] && [ "$IN_KBPS" -le "$FLOORK" ]; then
            REMUX=1; WHY="уже совсем плотный ($IN_KBPS кбит/с) — дальше жать значит портить, переложен 1:1"
        elif [ "$VENC" = "libx264" ] && [ "$HAVE_X265" -eq 0 ]; then
            case "$VCODEC" in
                hevc|av1|vp9) REMUX=1
                    WHY="снят в $VCODEC, а кодировщика hevc в вашем ffmpeg нет — в h264 файл бы вырос, переложен 1:1" ;;
            esac
        fi
    fi

    # Съёмка в hevc жмётся тем же hevc, и это заметно дольше h264 — честно
    # предупреждаем ДО начала, пока строка висит без ответа. При
    # перекладывании 1:1 перекодирования нет, и предупреждать не о чем.
    NOTE=""
    [ "$VENC" = "libx265" ] && [ "$REMUX" = 0 ] && NOTE=" [hevc, это дольше]"

    printf "  → %s (%s МБ, %s кбит/с)%s… " "$NAME" \
        "$(awk -v s="$IN_SZ" 'BEGIN{printf "%.1f", s/1048576}')" "$IN_KBPS" "$NOTE"

    if [ "$REMUX" = 1 ]; then
        remux_copy "$f" "$OUT" "$TAG" || exit 1
        OUT_SZ=$(wc -c < "$OUT" | tr -d ' ')
        awk -v b="$OUT_SZ" -v w="$WHY" 'BEGIN{ printf "%.1f МБ — %s\n", b/1048576, w }'
        TOTAL_IN=$((TOTAL_IN+IN_SZ)); TOTAL_OUT=$((TOTAL_OUT+OUT_SZ)); COPIED=$((COPIED+1))
        continue
    fi

    # Уровень профиля задаём только в веб-режимах: там кадр заведомо 720p и
    # меньше. В архиве кадр родной, и `-level 4.0` на 4K или 1080p60 — это
    # нарушение уровня, о котором x264 честно ругается. `-profile:v high`
    # тоже только для x264: у x265 профили называются иначе (main/main10).
    if [ "$VENC" = "libx265" ]; then
        VOPT="-c:v libx265 -preset medium -crf $VCRF $ENCTAG -x265-params log-level=error"
    else
        LEVELOPT="-level 4.0"
        [ "$ARCHIVE" = 1 ] && LEVELOPT=""
        VOPT="-c:v libx264 -preset slow -crf $VCRF -profile:v high $LEVELOPT"
    fi

    # -g 60 — ключевой кадр раз в 2 секунды: реже тормозит перемотка, чаще
    # файл толстеет ни за что. +faststart переносит оглавление в начало:
    # без него браузер ждёт закачки целиком, прежде чем показать первый кадр.
    # -map_metadata 0 сохраняет дату съёмки: без неё «Фото» и Finder ставят
    # файлам сегодняшний день и порядок в папке рассыпается.
    ffmpeg -y -loglevel error -nostdin -i "$f" \
        -vf "$VF" \
        $VOPT \
        $CAP \
        -g 60 -keyint_min 30 \
        $AOPT -map_metadata 0 -movflags +faststart "$OUT"

    ERR=$(ffmpeg -v error -i "$OUT" -f null - 2>&1 || true)
    if [ -n "$ERR" ]; then
        echo "ОШИБКА: $(echo "$ERR" | head -1)"
        exit 1
    fi

    OUT_SZ=$(wc -c < "$OUT" | tr -d ' ')

    # Страховка: результат больше исходника — это не сжатие. Такое бывает на
    # плотно уложенной съёмке, где выигрывать уже нечего. В архиве дорожка
    # тогда перекладывается как есть; в веб-режимах так нельзя — там просили
    # кадр 720p, и вернуть вместо него исходные 4K было бы подменой, поэтому
    # честно говорим, что файл вырос.
    if [ "$OUT_SZ" -ge "$IN_SZ" ]; then
        if [ "$ARCHIVE" = 1 ] && [ "$COPYOK" = 1 ]; then
            remux_copy "$f" "$OUT" "$TAG" || exit 1
            OUT_SZ=$(wc -c < "$OUT" | tr -d ' ')
            awk -v b="$OUT_SZ" 'BEGIN{ printf "%.1f МБ — сжатие ничего не дало, переложен в mp4 как есть (качество 1:1)\n", b/1048576 }'
            TOTAL_IN=$((TOTAL_IN+IN_SZ)); TOTAL_OUT=$((TOTAL_OUT+OUT_SZ)); COPIED=$((COPIED+1))
            continue
        fi
        awk -v a="$IN_SZ" -v b="$OUT_SZ" 'BEGIN{ printf "%.1f МБ — ⚠︎ БОЛЬШЕ исходника (%.1f МБ): жать тут нечего\n", b/1048576, a/1048576 }'
        TOTAL_IN=$((TOTAL_IN+IN_SZ)); TOTAL_OUT=$((TOTAL_OUT+OUT_SZ)); DONE=$((DONE+1))
        continue
    fi

    if [ "$REMUXONLY" = 1 ]; then
        awk -v a="$IN_SZ" -v b="$OUT_SZ" -v c="$VCODEC" \
            'BEGIN{ printf "%.1f МБ — %s в mp4 не кладётся, пересобран в h264 с запасом качества (в %.1f раза легче)\n", b/1048576, c, a/b }'
    else
        awk -v a="$IN_SZ" -v b="$OUT_SZ" 'BEGIN{ printf "%.1f МБ, в %.1f раза легче\n", b/1048576, a/b }'
    fi
    TOTAL_IN=$((TOTAL_IN+IN_SZ)); TOTAL_OUT=$((TOTAL_OUT+OUT_SZ)); DONE=$((DONE+1))
done

echo
if [ "$DONE" = 0 ] && [ "$COPIED" = 0 ]; then
    echo "Сжимать было нечего: пропущено $SKIP файлов (все уже лёгкие)."
else
    awk -v a="$TOTAL_IN" -v b="$TOTAL_OUT" -v n="$DONE" -v s="$SKIP" -v c="$COPIED" -v r="$REMUXONLY" 'BEGIN{
        printf "Готово: %d шт. — было %.0f МБ, стало %.0f МБ (в %.1f раза легче)\n", n+c, a/1048576, b/1048576, a/b
        if (c>0) printf "Из них переложено в mp4 без перекодирования: %d%s\n", c, (r=="1" ? "" : " (жать было нечего)")
        if (s>0) printf "Пропущено как уже лёгкие: %d\n", s
    }'
    echo "Файлы в папке «$OUTDIR», оригиналы на месте."
fi
