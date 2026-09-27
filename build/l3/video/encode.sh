#!/bin/bash
# Нарезка роликов лекции 3 из исходников владельца (FR-SITE71).
#
#   build/l3/video/encode.sh <папка с IMG_1727.MOV … IMG_1771.MOV> [ffmpeg]
#
# Исходники — 43 вертикальных ролика с телефона (1080×1920 HEVC). По алфавиту
# они идут 0…42: ролик k → assets/video_l3/<k+1>.mp4 (кружок слайда k),
# ролик 42 → practice.mp4, его первый кадр → practice.jpg.
#
# Кадр один на все ролики: камера за съёмку не двигалась (верх рамок картин на
# 776–783 px во всех файлах). Вся ширина 1080×1080 с верхом на 728 px — над
# картинами остаётся около 48 px, как в кадре лекции 2. Формат как у лекции 2:
# H.264 514×514, 30 fps, AAC 96 кбит/с, faststart.
#
# Поправки по приёмке — без них пересборка из исходников их потеряет:
#   1.mp4  (IMG_1727) звук +4.0 dB  — был на 4 LU тише остальных;
#   2.mp4  (IMG_1728) звук +2.7 dB;
#   19–21.mp4 (IMG_1745…1747) цвет rr 1.10, gg 0.90, bb 0.875 — сняты с
#   холодным балансом, цвет прыгал при листании 17→21.
#
# Для проверки: L3_VIDEO_DST — другая папка вывода, L3_VIDEO_ONLY — номера
# роликов через пробел (1…42, 43 = практика), остальные пропускаются.
set -e
SRC=${1:?папка с исходниками}
FF=${2:-ffmpeg}
DST=${L3_VIDEO_DST:-$(cd "$(dirname "$0")/../../.." && pwd)/assets/video_l3}
mkdir -p "$DST"
CROP="crop=1080:1080:0:728"
SCALE="scale=514:514:flags=lanczos,format=yuv420p"
X264="-c:v libx264 -preset slow -crf 26 -profile:v high -r 30"
AAC="-c:a aac -b:a 96k -ac 2 -ar 44100"
i=0
for f in $(ls "$SRC"/*.MOV | sort); do
  n=$((i + 1)); out="$DST/$n.mp4"
  if [ -n "$L3_VIDEO_ONLY" ] && ! [[ " $L3_VIDEO_ONLY " == *" $n "* ]]; then i=$n; continue; fi
  [ $i -eq 42 ] && out="$DST/practice.mp4"
  vf="$CROP,$SCALE"; af="anull"
  case $n in
    19|20|21) [ $i -ne 42 ] && vf="$CROP,colorchannelmixer=rr=1.10:gg=0.90:bb=0.875,$SCALE" ;;
  esac
  [ $i -eq 0 ] && af="volume=4.0dB"
  [ $i -eq 1 ] && af="volume=2.7dB"
  "$FF" -hide_banner -loglevel error -y -i "$f" -vf "$vf" -af "$af" $X264 $AAC \
        -movflags +faststart -map_metadata -1 "$out"
  echo "$(basename "$f") → $(basename "$out")"
  i=$((i + 1))
done
[ -f "$DST/practice.mp4" ] && \
  "$FF" -hide_banner -loglevel error -y -i "$DST/practice.mp4" -frames:v 1 -q:v 3 "$DST/practice.jpg"
echo "готово: $i роликов и practice.jpg в $DST"
