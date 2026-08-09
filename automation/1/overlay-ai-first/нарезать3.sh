#!/bin/sh
# Режет готовый ролик на ТРИ части по двум числам и каждой части приклеивает
# спереди обложку из этой же папки.
#
# Запуск:  sh нарезать3.sh "ролик-готовый.mp4" 62 128
#          числа — секунды реза, можно в виде мм:сс («1:02 2:08»).
#
#   часть 1 — с начала до первого числа
#   часть 2 — между числами
#   часть 3 — от второго числа до конца
#
# ОБЛОЖКИ берутся из папки рядом со скриптом:
#   cover1.png / cover2.png / cover3.png — своя на каждую часть;
#   нет их — берётся общая cover.png на все три;
#   нет и её — берётся первый кадр самой части.
# Годятся и .jpg/.jpeg/.webp — расширение искать не нужно, скрипт сам найдёт.
#
# Необязательные аргументы:
#   sh нарезать3.sh видео.mp4 62 128 0.3      → обложка 0.3 с вместо 0.2
#   sh нарезать3.sh видео.mp4 62 128 0.2 0    → в исходнике заставки НЕТ
#
# Что важно знать про звук и кадры:
#   • звук идёт КОПИЕЙ, без пережима — как в собрать.sh;
#   • частота кадров держится явным -r: после concat она теряется, и
#     ffmpeg молча пишет 25 к/с, выбрасывая каждый шестой кадр;
#   • ролик, собранный собрать.sh, уже начинается с заставки 0.2 с —
#     скрипт это видит сам и заменяет её обложкой первой части, а не
#     кладёт вторую поверх первой. Числа реза при этом те, что вы видите
#     на шкале готового ролика.
set -e
FF=""
for c in ffmpeg /opt/homebrew/bin/ffmpeg /usr/local/bin/ffmpeg; do
  command -v "$c" >/dev/null 2>&1 && { FF="$c"; break; }
done
[ -n "$FF" ] || { echo "Нет ffmpeg. macOS: brew install ffmpeg"; exit 1; }
FP="$(dirname "$FF")/ffprobe"; [ -x "$FP" ] || FP=ffprobe
command -v "$FP" >/dev/null || { echo "Рядом с $FF нет ffprobe"; exit 1; }
DIR=$(cd "$(dirname "$0")" && pwd)

VIDEO="${1:-}"
[ -n "$VIDEO" ] || { echo "Как запускать: sh нарезать3.sh \"ролик-готовый.mp4\" 62 128"; exit 1; }
[ -f "$VIDEO" ] || { echo "Не найден файл: $VIDEO"; exit 1; }
[ -n "${2:-}" ] && [ -n "${3:-}" ] || { echo "Нужны ДВА числа реза: sh нарезать3.sh \"$VIDEO\" 62 128"; exit 1; }
SEC="${4:-0.2}"          # сколько секунд держится обложка каждой части

# «1:02» → 62. Секунды можно писать и просто числом.
sec() { echo "$1" | awk -F: '{ s=0; for(i=1;i<=NF;i++) s=s*60+$i; printf "%.3f", s }'; }
C1=$(sec "$2"); C2=$(sec "$3")
# Числа могли прийти в обратном порядке — «128 62» дало бы кусок
# отрицательной длины, и ffmpeg вернул бы пустой файл без единой жалобы.
if awk -v a="$C1" -v b="$C2" 'BEGIN{ exit (a>b) ? 0 : 1 }'; then T=$C1; C1=$C2; C2=$T; fi

p()  { "$FP" -v error -select_streams "$1" -show_entries stream="$2" -of csv=p=0 "$VIDEO"; }
pf() { "$FP" -v error -show_entries format="$1" -of csv=p=0 "$VIDEO"; }
W=$(p v:0 width); H=$(p v:0 height)
FPS=$(p v:0 r_frame_rate); PIX=$(p v:0 pix_fmt)
VCODEC=$(p v:0 codec_name); ACODEC=$(p a:0 codec_name); BR=$(pf bit_rate)
DUR=$(pf duration)
ROT=$("$FP" -v error -select_streams v:0 -show_entries stream_side_data=rotation -of csv=p=0 "$VIDEO" 2>/dev/null | head -1)
: "${ROT:=0}"
case "$ROT" in 90|-90|270|-270) DW=$H; DH=$W ;; *) DW=$W; DH=$H ;; esac
echo "Ролик: $VCODEC ${DW}x${DH}, ${DUR}с, звук ${ACODEC:-нет}"

awk -v b="$C2" -v d="$DUR" 'BEGIN{ exit (b < d-0.05) ? 0 : 1 }' \
  || { echo "Второе число ($C2 с) не внутри ролика ($DUR с) — третья часть вышла бы пустой"; exit 1; }

# Заставка в начале исходника. Ролик из собрать.sh начинается с 0.2 с
# СТОП-КАДРА, и если просто приклеить обложку, зритель увидит заставку
# вдвое дольше. Ищем стоп-кадр фильтром freezedetect: он меряет разницу
# между соседними кадрами, а сверять их хэши бесполезно — картинка
# кодируется с потерями, и два кадра ОДНОЙ картинки декодируются
# по-разному. Порог 0.001 — заводской: на живом дубле (шум матрицы,
# дыхание, свет) он не срабатывает ни разу, проверено на исходнике.
if [ -n "${5:-}" ]; then
  OLD="$5"
  echo "Заставка в исходнике: $OLD с (указана вручную)"
else
  OLD=$("$FF" -v info -t 1.5 -i "$VIDEO" -an -vf "freezedetect=n=0.001:d=0.08" -f null - 2>&1 \
        | awk -F": " '/freeze_start/ { if (got) next; s=$2 }
                      /freeze_end/   { if (got) next;
                                       if (s+0 < 0.05 && $2+0 <= 1.0) { printf "%.3f", $2; got=1 } }')
  : "${OLD:=0}"
  if [ "$OLD" = "0" ]; then
    echo "Заставка в исходнике: нет — просто приклею обложку"
  else
    echo "Заставка в исходнике: нашёл стоп-кадр $OLD с — заменю его обложкой первой части"
  fi
fi

# Битрейт и кодировщик — как в собрать.sh: перекодируется только картинка,
# и раздувать файл незачем. На маке идёт аппаратно, через VideoToolbox.
TARGET=$(awk -v b="${BR:-0}" 'BEGIN{ if(b<1) b=12000000; if(b<10000000) b=10000000; printf "%d", b }')
HW=$("$FF" -hide_banner -encoders 2>/dev/null | grep -o "hevc_videotoolbox\|h264_videotoolbox" | tr "\n" " ")
case "$VCODEC:$HW" in
  hevc:*hevc_videotoolbox*) VE="hevc_videotoolbox -b:v $TARGET -tag:v hvc1" ;;
  *:*h264_videotoolbox*)    VE="h264_videotoolbox -b:v $TARGET" ;;
  hevc:*)                   VE="libx265 -preset medium -crf 18 -tag:v hvc1 -x265-params log-level=none" ;;
  *)                        VE="libx264 -preset medium -crf 17" ;;
esac
echo "Кодировщик: $VE"
AENC=aac; "$FF" -hide_banner -encoders 2>/dev/null | grep -q aac_at && AENC=aac_at

BASE="${VIDEO%.*}"
BASE="${BASE%-готовый}"     # «ролик-готовый.mp4» → «ролик-часть1.mp4»
TMP=".cut3-build"; rm -rf "$TMP"; mkdir -p "$TMP"

# Обложка части: своя cover1/2/3, общая cover, иначе первый кадр части.
pickcover() {   # <номер части> <секунда начала части>
  for e in png jpg jpeg webp; do
    [ -f "$DIR/cover$1.$e" ] && { echo "$DIR/cover$1.$e"; return; }
  done
  for e in png jpg jpeg webp; do
    [ -f "$DIR/cover.$e" ] && { echo "$DIR/cover.$e"; return; }
  done
  "$FF" -y -v error -ss "$2" -i "$VIDEO" -frames:v 1 -vf "scale=$DW:$DH" "$TMP/cover$1.png"
  echo "$TMP/cover$1.png"
}

# Части: [OLD…C1], [C1…C2], [C2…конец]. Начало первой берётся ПОСЛЕ старой
# заставки, поэтому числа реза остаются теми, что видно на шкале.
STARTS="$OLD $C1 $C2"
ENDS="$C1 $C2"

i=0
for A in $STARTS; do
  i=$((i+1))
  B=$(echo "$ENDS" | awk -v i="$i" '{print $i}')
  OUT="$BASE-часть$i.mp4"
  if [ -n "$B" ]; then
    LEN=$(awk -v a="$A" -v b="$B" 'BEGIN{ printf "%.3f", b-a }')
    TOPT="-t $LEN"
  else
    LEN=$(awk -v a="$A" -v d="$DUR" 'BEGIN{ printf "%.3f", d-a }')
    TOPT=""
  fi
  PIC=$(pickcover "$i" "$A")
  case "$PIC" in "$TMP"/*) WHAT="первый кадр части" ;; *) WHAT="$(basename "$PIC")" ;; esac
  echo "Часть $i: с $A с, длина $LEN с, обложка ${SEC}с — $WHAT → $OUT"

  # [0] обложка · [1] картинка части · [2] та же часть, но из неё берётся
  # ТОЛЬКО звук, со сдвигом на длину обложки. Звук копией — без пережима.
  # -framerate у обложки обязателен: картинка по умолчанию идёт 25 к/с, и
  # на 30-кадровом ролике заставка выходила бы 5 кадров вместо 6.
  # -r на выходе обязателен: после concat частота теряется.
  VF="[0:v]scale=$DW:$DH:flags=lanczos,format=$PIX,setsar=1,fps=$FPS[c];[1:v]setpts=PTS-STARTPTS,scale=$DW:$DH:flags=lanczos,format=$PIX,setsar=1[m];[c][m]concat=n=2:v=1[v]"
  if [ -z "$ACODEC" ]; then
    "$FF" -y -loglevel error -stats -loop 1 -framerate "$FPS" -t "$SEC" -i "$PIC" \
      -ss "$A" $TOPT -i "$VIDEO" \
      -filter_complex "$VF" \
      -map "[v]" -r "$FPS" -c:v $VE -pix_fmt "$PIX" -an -movflags +faststart "$OUT"
  else
    [ "$ACODEC" = "aac" ] && AOPT="-c:a copy" || AOPT="-c:a $AENC -b:a 256k"
    "$FF" -y -loglevel error -stats -loop 1 -framerate "$FPS" -t "$SEC" -i "$PIC" \
      -ss "$A" $TOPT -i "$VIDEO" \
      -itsoffset "$SEC" -ss "$A" $TOPT -i "$VIDEO" \
      -filter_complex "$VF" \
      -map "[v]" -map 2:a:0 -r "$FPS" -c:v $VE -pix_fmt "$PIX" $AOPT -movflags +faststart "$OUT"
  fi

  # Проверка декодированием: файл нужного размера и длины может не играть.
  ERR=$("$FF" -v error -i "$OUT" -f null - 2>&1 || true)
  [ -z "$ERR" ] || { echo "ОШИБКА в части $i: $(echo "$ERR" | head -1)"; exit 1; }
  # Длина куска и длина звука должны сойтись: если видеодорожка короче,
  # в плеере под звук пойдёт чернота.
  CLEN=$("$FP" -v error -show_entries format=duration -of csv=p=0 "$OUT")
  VLEN=$("$FP" -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "$OUT")
  awk -v c="${CLEN:-0}" -v v="${VLEN:-0}" -v w="$(awk -v l="$LEN" -v s="$SEC" 'BEGIN{printf "%.3f", l+s}')" -v n="$i" 'BEGIN{
    if (w-c > 0.15 || c-w > 0.15) printf "  ⚠︎ часть %s: вышло %.2f с вместо %.2f\n", n, c, w;
    if (v > 0 && c-v > 0.15)      printf "  ⚠︎ часть %s: видеодорожка на %.2f с короче — будет чернота\n", n, c-v }'
done
rm -rf "$TMP"
echo "Готово: $BASE-часть1.mp4, $BASE-часть2.mp4, $BASE-часть3.mp4"
