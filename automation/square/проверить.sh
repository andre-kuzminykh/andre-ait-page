#!/bin/sh
# Проверка готовых кусков: у каких начало или конец чёрные, а какие можно
# оставить как есть.
#
# Запуск:  sh проверить.sh                 — все mp4/mov рядом со скриптом
#          sh проверить.sh кусок-1.mp4 …   — только названные файлы
#
# Черноты бывает две, и находятся они по-разному:
#   1. ЧЁРНЫЕ КАДРЫ — приехали из исходника (дубль начинается или кончается
#      затемнением). Видны покадрово.
#   2. ДЫРА НА ШКАЛЕ — видеодорожка кончилась, а звук ещё идёт. Кадров там нет
#      вообще, покадрово её не найти: сверяем длину дорожки с длиной файла.
set -e
command -v ffmpeg  >/dev/null || { echo "Нет ffmpeg. macOS: brew install ffmpeg"; exit 1; }
command -v ffprobe >/dev/null || { echo "Нет ffprobe — он ставится вместе с ffmpeg"; exit 1; }

EDGE=1.5      # сколько секунд с краёв считать «началом» и «концом»
GAPMAX=0.15   # расхождение длин, ниже которого это просто округление кадров

if [ $# -gt 0 ]; then
    FILES="$*"
else
    FILES=$(ls *.mp4 *.MP4 *.mov *.MOV 2>/dev/null || true)
fi
[ -n "$FILES" ] || { echo "Рядом нет ни одного mp4/mov, и в аргументах пусто."; exit 1; }

BAD=0
for f in $FILES; do
    [ -f "$f" ] || continue
    CLEN=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
    VLEN=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "$f")
    BLACK=$(ffmpeg -hide_banner -i "$f" -vf "blackdetect=d=0.10:pic_th=0.98:pix_th=0.10" -f null - 2>&1 \
            | grep -o "black_start:[0-9.]* black_end:[0-9.]*" || true)

    HEAD=$(echo "$BLACK" | awk -v e="$EDGE" '{ for(i=1;i<=NF;i++) if($i ~ /^black_start:0(\.0*)?$/) { split($(i+1),b,":"); if(b[2]>0.3) print b[2] } }' | head -1)
    TAIL=$(echo "$BLACK" | awk -v c="${CLEN:-0}" -v e="$EDGE" '{ for(i=1;i<=NF;i++) if($i ~ /^black_end:/) { split($i,b,":"); split($(i-1),a,":"); if(c-b[2] < 0.2 && b[2]-a[2] > 0.3) print c-a[2] } }' | head -1)
    GAP=$(awk -v v="${VLEN:-0}" -v c="${CLEN:-0}" -v m="$GAPMAX" 'BEGIN{ d=(v>0)?c-v:0; printf "%.2f", (d>m)?d:0 }')

    MSG=""
    [ -n "$HEAD" ] && MSG="$MSG начало чёрное $(printf '%.1f' "$HEAD") c;"
    [ -n "$TAIL" ] && MSG="$MSG конец чёрный $(printf '%.1f' "$TAIL") c;"
    awk -v g="$GAP" 'BEGIN{ exit (g>0) ? 0 : 1 }' && MSG="$MSG звук идёт на $GAP c дольше картинки;"

    if [ -z "$MSG" ]; then
        printf "  ✓ %s — чисто, оставляем\n" "$f"
    else
        BAD=$((BAD+1))
        printf "  ✗ %s —%s\n" "$f" "$MSG"
    fi
done

echo
if [ "$BAD" = 0 ]; then
    echo "Все куски чистые: перерезать нечего."
else
    echo "Проблемных: $BAD."
    echo "Если это ДЫРА (звук дольше картинки) — перережьте новым нарезать.sh, он её убирает."
    echo "Если это ЧЁРНЫЕ КАДРЫ — они в самом исходнике: сдвиньте секунду реза"
    echo "или отрежьте затемнение, нарезка тут ни при чём."
fi
