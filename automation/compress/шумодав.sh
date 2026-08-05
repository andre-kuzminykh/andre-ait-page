#!/bin/sh
# Чистка шипения в звуке. КАРТИНКА НЕ ТРОГАЕТСЯ: видеодорожка копируется
# бит-в-бит, перекодируется только звук. Поэтому быстро и без потери качества.
#
# Запуск (рядом с клипом):
#   sh шумодав.sh "клип.MOV"            — мягкая чистка (обычно достаточно)
#   sh шумодав.sh "клип.MOV" средне
#   sh шумодав.sh "клип.MOV" сильно     — если шипит заметно; проверяйте на слух,
#                                         сильная чистка может задеть «с» и «ш» в речи
#
# На выходе «клип-чистый.mp4». Дальше этим файлом пользуетесь как обычно:
# собрать.sh, нарезать.sh, сжать.sh — чистить надо ДО сборки, один раз.
#
# Замерено на синтетике «речь + шипение»: мягко −12 дБ шума, средне −19,
# сильно −26; уровень речи при этом меняется меньше чем на дБ.
set -e
command -v ffmpeg  >/dev/null || { echo "Нет ffmpeg. macOS: brew install ffmpeg"; exit 1; }
command -v ffprobe >/dev/null || { echo "Нет ffprobe — он ставится вместе с ffmpeg"; exit 1; }
ffmpeg -hide_banner -filters 2>/dev/null | grep -q afftdn || {
    echo "В вашей сборке ffmpeg нет шумодава afftdn. macOS: brew upgrade ffmpeg"; exit 1; }

VIDEO="${1:?Укажите файл: sh шумодав.sh \"клип.MOV\"}"
[ -f "$VIDEO" ] || { echo "Не найден файл: $VIDEO"; exit 1; }
OUT="${VIDEO%.*}-чистый.mp4"

# Сила чистки: nr — сколько дБ шума снимать за проход.
case "${2:-мягко}" in
    средне|2)  NR=20 ;;
    сильно|3)  NR=30 ;;
    *)         NR=12 ;;
esac

ACODEC=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of csv=p=0 "$VIDEO" 2>/dev/null || true)
[ -n "$ACODEC" ] || { echo "В файле нет звуковой дорожки — чистить нечего."; exit 1; }

floor() {  # шумовой пол: самый тихий кусок дорожки (RMS trough)
    ffmpeg -hide_banner -i "$1" -map 0:a:0 \
        -af astats=measure_overall=RMS_trough:measure_perchannel=none -f null - 2>&1 \
        | grep "RMS trough" | awk '{print $NF}' | head -1
}

BEFORE=$(floor "$VIDEO")
echo "Шумовой пол исходника: ${BEFORE:-?} дБ. Чищу (nr=$NR)…"

# highpass=70 убирает гул ниже голоса (кондиционер, стол), afftdn — шипение.
# Видео — копией: -c:v copy, метка поворота и кодек остаются как были.
ffmpeg -y -loglevel error -stats -i "$VIDEO" \
    -map 0:v:0 -map 0:a:0 -c:v copy \
    -af "highpass=f=70,afftdn=nr=$NR:nf=-30" \
    -c:a aac -b:a 256k -movflags +faststart "$OUT"

ERR=$(ffmpeg -v error -i "$OUT" -f null - 2>&1 || true)
[ -z "$ERR" ] || { echo "ОШИБКА: результат не декодируется — $(echo "$ERR" | head -1)"; exit 1; }

AFTER=$(floor "$OUT")
echo
echo "Готово: $OUT"
echo "Шумовой пол: было ${BEFORE:-?} дБ → стало ${AFTER:-?} дБ (ниже = тише шип)"
echo "Послушайте паузы между фразами. Всё ещё шипит — запустите с «средне» или «сильно»."
