#!/bin/sh
# Кадры PNG → слой графики: цвет и маска прозрачности отдельными mp4.
#
#   sh tools/слой.sh <папка кадров> <папка ролика> [overlay|subs]
#
# Пример:
#   python3 tools/render_overlay.py 173.4 8943 /tmp/кадры "&subs=0"
#   sh tools/слой.sh /tmp/кадры automation/1/overlay-agentops overlay
#
# Почему два файла, а не один: прозрачности в mp4 нет, webm с альфой
# собирается не везде, а две видеодорожки в одном mp4 не пережили ремукс —
# файл переставал декодироваться. `alphamerge` в собрать.sh сшивает их обратно.
#
# Имена переменных латиницей: dash кириллические не принимает («not found»).
set -e
FRAMES=$1
DST=$2
NAME=${3:-overlay}

[ -n "$FRAMES" ] && [ -n "$DST" ] || {
    echo "Как звать: sh tools/слой.sh <папка кадров> <папка ролика> [overlay|subs]"; exit 1; }
[ -d "$FRAMES" ] || { echo "Нет папки кадров: $FRAMES"; exit 1; }
[ -d "$DST" ] || { echo "Нет папки ролика: $DST"; exit 1; }
ls "$FRAMES"/f00000.png >/dev/null 2>&1 || {
    echo "В $FRAMES нет кадров f00000.png… — сначала render_overlay.py"; exit 1; }

# -crf 18 и preset slow: слой кодируется один раз, а поверх него ещё раз
# кодируется готовый ролик — на слое экономить нельзя, потери сложатся.
# -g 60 (ключевой кадр раз в 2 c) и -r 30 держат синхронность с дорожкой.
ffmpeg -y -hide_banner -loglevel error -framerate 30 -i "$FRAMES/f%05d.png" \
    -vf "format=rgba,format=yuv420p" \
    -c:v libx264 -crf 18 -preset slow -g 60 -r 30 \
    -movflags +faststart "$DST/${NAME}_c.mp4"
echo "  ${NAME}_c.mp4 — цвет готов"

ffmpeg -y -hide_banner -loglevel error -framerate 30 -i "$FRAMES/f%05d.png" \
    -vf "format=rgba,alphaextract,format=gray,format=yuv420p" \
    -c:v libx264 -crf 18 -preset slow -g 60 -r 30 \
    -movflags +faststart "$DST/${NAME}_a.mp4"
echo "  ${NAME}_a.mp4 — маска прозрачности готова"

for f in "$DST/${NAME}_c.mp4" "$DST/${NAME}_a.mp4"; do
    ERR=$(ffmpeg -v error -i "$f" -f null - 2>&1 || true)
    [ -z "$ERR" ] || { echo "ОШИБКА в $f: $(echo "$ERR" | head -1)"; exit 1; }
done
echo "Слой «$NAME» собран и проверен декодированием."
