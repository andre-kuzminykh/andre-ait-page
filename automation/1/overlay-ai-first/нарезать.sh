#!/bin/sh
# Режет готовый ролик на части по числам и каждой части приклеивает спереди
# обложку из этой же папки, подписав её «Часть 1», «Часть 2» и так далее.
#
# Сколько чисел — столько резов, частей на одну больше:
#   sh нарезать.sh "ролик-готовый.mp4" 62 128         → 3 части
#   sh нарезать.sh "ролик-готовый.mp4" 45 90 135      → 4 части
#   sh нарезать.sh "ролик-готовый.mp4" 1:02 2:08      → те же 3, но в мм:сс
#
# ОБЛОЖКИ берутся из папки рядом со скриптом:
#   cover1.png, cover2.png, cover3.png, cover4.png — своя на каждую часть;
#   нет их — берётся общая cover.png на все;
#   нет и её — берётся первый кадр самой части.
# Годятся .png, .jpg, .jpeg, .webp — расширение искать не нужно.
#
# ПОДПИСЬ «Часть N» ставится на обложку под тайтлом, кеглем меньше тайтла.
# Двигается и настраивается — всё через необязательные пары ключ=значение,
# их можно писать в любом месте команды:
#   низ=760        насколько ниже верха кадра стоит строка (пикселей)
#   кегль=64       размер шрифта подписи
#   подпись=нет    вообще без подписи
#   подпись="Серия"  другое слово вместо «Часть»
#   обложка=0.3    длина обложки в секундах (по умолчанию 0.2)
#   заставка=0     в исходнике заставки НЕТ, не искать
# Например:  sh нарезать.sh видео.mp4 45 90 135 низ=820 кегль=72
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

VIDEO=""; CUTS=""; SEC=0.2; OLD=""; CAPY=""; CAPSIZE=""; CAPWORD="Часть"; PREVIEW=0
# Разбор аргументов: первый не-ключ — файл, дальше числа реза, а пары
# ключ=значение можно ставить где угодно.
for a in "$@"; do
  case "$a" in
    низ=*|y=*)             CAPY="${a#*=}" ;;
    кегль=*|size=*)        CAPSIZE="${a#*=}" ;;
    подпись=*|caption=*)   CAPWORD="${a#*=}" ;;
    обложка=*|cover=*)     SEC="${a#*=}" ;;
    заставка=*|intro=*)    OLD="${a#*=}" ;;
    превью|превью=*|preview|preview=*) PREVIEW=1 ;;
    *) if [ -z "$VIDEO" ]; then VIDEO="$a"; else CUTS="$CUTS $a"; fi ;;
  esac
done
[ -n "$VIDEO" ] || { echo "Как запускать: sh нарезать.sh \"ролик-готовый.mp4\" 62 128"; exit 1; }
[ -f "$VIDEO" ] || { echo "Не найден файл: $VIDEO"; exit 1; }
[ -n "$CUTS" ] || { echo "Нужны числа реза: sh нарезать.sh \"$VIDEO\" 62 128 (два числа — три части)"; exit 1; }

# «1:02» → 62. Секунды можно писать и просто числом. Числа сортируются:
# «128 62» иначе дало бы кусок отрицательной длины и пустой файл — ffmpeg
# на это не жалуется вовсе.
sec() { echo "$1" | awk -F: '{ s=0; for(i=1;i<=NF;i++) s=s*60+$i; printf "%.3f\n", s }'; }
PTS=""
for c in $CUTS; do PTS="$PTS $(sec "$c")"; done
PTS=$(printf "%s\n" $PTS | sort -n | tr "\n" " ")

p()  { "$FP" -v error -select_streams "$1" -show_entries stream="$2" -of csv=p=0 "$VIDEO"; }
pf() { "$FP" -v error -show_entries format="$1" -of csv=p=0 "$VIDEO"; }
W=$(p v:0 width); H=$(p v:0 height)
FPS=$(p v:0 r_frame_rate); PIX=$(p v:0 pix_fmt)
VCODEC=$(p v:0 codec_name); ACODEC=$(p a:0 codec_name); BR=$(pf bit_rate)
DUR=$(pf duration)
ROT=$("$FP" -v error -select_streams v:0 -show_entries stream_side_data=rotation -of csv=p=0 "$VIDEO" 2>/dev/null | head -1)
: "${ROT:=0}"
case "$ROT" in 90|-90|270|-270) DW=$H; DH=$W ;; *) DW=$W; DH=$H ;; esac
N=$(( $(echo $PTS | wc -w) + 1 ))
echo "Ролик: $VCODEC ${DW}x${DH}, ${DUR}с, звук ${ACODEC:-нет} → частей: $N"

LAST=$(echo $PTS | awk '{print $NF}')
awk -v b="$LAST" -v d="$DUR" 'BEGIN{ exit (b < d-0.05) ? 0 : 1 }' \
  || { echo "Последнее число ($LAST с) не внутри ролика ($DUR с) — последняя часть вышла бы пустой"; exit 1; }

# Заставка в начале исходника. Ролик из собрать.sh начинается с 0.2 с
# СТОП-КАДРА, и если просто приклеить обложку, зритель увидит заставку
# вдвое дольше. Ищем стоп-кадр фильтром freezedetect: он меряет разницу
# между соседними кадрами, а сверять их хэши бесполезно — картинка
# кодируется с потерями, и два кадра ОДНОЙ картинки декодируются
# по-разному. Порог 0.001 — заводской: на живом дубле (шум матрицы,
# дыхание, свет) он не срабатывает ни разу, проверено на исходнике.
if [ -n "$OLD" ]; then
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
# Имя рабочей папки латиницей и без пробелов: путь к шрифту уходит ВНУТРЬ
# фильтра drawtext, где двоеточия, пробелы и запятые пришлось бы
# экранировать, а папка ролика вполне может называться «Эволюция ИИ».
TMP=".cut-build"; rm -rf "$TMP"; mkdir -p "$TMP"

# Подпись «Часть N» на обложке: тем же шрифтом, что и субтитры, кеглем
# заметно меньше тайтла, белым с тонкой тёмной обводкой — как весь текст
# в этих роликах. Без ttf рядом подпись не ставится: по имени семейства
# libass и drawtext молча уходят в системный шрифт.
# Отдельным case, а не цепочкой [ … ] && CAP=0: при set -e ложная цепочка
# сама по себе роняет скрипт — команда вернула бы ненулевой код.
CAP=1
case "$CAPWORD" in нет|no|off|"") CAP=0 ;; esac
# Шрифт ищем по списку: сначала фирменный рядом со скриптом, потом
# системные. Скрипт часто кладут ОДИН, рядом с видео, — без запасного
# варианта подпись в таком случае молча не появлялась бы.
# Найденный файл копируется в рабочую папку под именем f.ttf: путь уходит
# внутрь фильтра, где пробелы и двоеточия пришлось бы экранировать, а
# «/System/Library/Fonts/Supplemental/Arial Bold.ttf» — с пробелом.
FONTNAME=""
if [ "$CAP" = 1 ]; then
  mkdir -p "$TMP/fonts"
  for f in \
      "$DIR/fonts/Montserrat-Black.ttf" \
      "$HOME/Library/Fonts/Montserrat-Black.ttf" \
      "/Library/Fonts/Montserrat-Black.ttf" \
      "/System/Library/Fonts/Supplemental/Arial Bold.ttf" \
      "/System/Library/Fonts/Supplemental/Arial Unicode.ttf" \
      "/Library/Fonts/Arial Bold.ttf" \
      "/System/Library/Fonts/Helvetica.ttc" \
      "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" ; do
    if [ -f "$f" ]; then cp "$f" "$TMP/fonts/f.ttf"; FONTNAME="$f"; break; fi
  done
  if [ -z "$FONTNAME" ]; then
    echo "⚠︎ ПОДПИСИ «$CAPWORD N» НЕ БУДЕТ: не нашёл ни одного шрифта."
    echo "  Положите скрипт в папку ролика (там лежит fonts/Montserrat-Black.ttf)."
    CAP=0
  else
    case "$FONTNAME" in
      *Montserrat-Black.ttf) : ;;
      *) echo "⚠︎ Фирменного fonts/Montserrat-Black.ttf рядом нет — подпись будет шрифтом $(basename "$FONTNAME")."
         echo "  Чтобы вышло как надо, запускайте скрипт из папки ролика." ;;
    esac
  fi
fi
# Чем рисовать подпись. drawtext проще, но он есть не в каждой сборке
# (нужен libfreetype), а subtitles — не в каждой другой (нужен libass).
# Умеем обоими: что нашлось, тем и рисуем.
CAPMODE=none
if [ "$CAP" = 1 ]; then
  FILTERS=$("$FF" -hide_banner -filters 2>/dev/null)
  case "$FILTERS" in
    *" drawtext "*)  CAPMODE=draw ;;
    *" subtitles "*) CAPMODE=ass ;;
    *) CAP=0; echo "Подпись «$CAPWORD N» не ставлю: в этой сборке ffmpeg нет ни drawtext, ни subtitles" ;;
  esac
fi
: "${CAPSIZE:=$(awk -v h="$DH" 'BEGIN{ printf "%d", h*0.036 }')}"
# 0.35 высоты = 672 при 1920. На обложках этой серии тайтл кончается около
# y636, между его строками 42px — подпись садится на 36px ниже тайтла, то
# есть читается как часть того же блока, а не отдельной строкой в пустоте.
: "${CAPY:=$(awk -v h="$DH" 'BEGIN{ printf "%d", h*0.35 }')}"
BORD=$(awk -v s="$CAPSIZE" 'BEGIN{ v=int(s/16); if(v<3) v=3; printf "%d", v }')
if [ "$CAP" = 1 ]; then echo "Подпись: «$CAPWORD N», кегль $CAPSIZE, от верха кадра $CAPY"; fi

# Обложка части: своя cover1/2/3…, общая cover, иначе первый кадр части.
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

# Части: [OLD…первое число], … , [последнее число…конец].
STARTS="$OLD $PTS"
ENDS="$PTS"        # на один короче STARTS: пусто = до конца ролика

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

  # Подпись рисуется ПОВЕРХ обложки, до склейки: сам ролик она не трогает.
  # Белым с тонкой тёмной обводкой — как весь текст в этих роликах.
  DRAW=""
  if [ "$CAPMODE" = draw ]; then
    DRAW=",drawtext=fontfile=$TMP/fonts/f.ttf:text='$CAPWORD $i':fontcolor=white:fontsize=$CAPSIZE:borderw=$BORD:bordercolor=black@0.55:x=(w-text_w)/2:y=$CAPY"
  elif [ "$CAPMODE" = ass ]; then
    # Выравнивание 8 — по центру сверху, тогда MarginV считается от верха
    # кадра, как y у drawtext. Имя шрифта ПОЛНОЕ («Montserrat Black»,
    # это name ID 1 в ttf): по семейному libass молча уходит в системный.
    { echo "[Script Info]"
      echo "ScriptType: v4.00+"
      echo "PlayResX: $DW"
      echo "PlayResY: $DH"
      echo "[V4+ Styles]"
      echo "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
      echo "Style: Cap,Montserrat Black,$CAPSIZE,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,$BORD,0,8,40,40,$CAPY,1"
      echo "[Events]"
      echo "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
      echo "Dialogue: 0,0:00:00.00,0:00:30.00,Cap,,0,0,0,,$CAPWORD $i"
    } > "$TMP/cap$i.ass"
    DRAW=",subtitles=filename=$TMP/cap$i.ass:fontsdir=$TMP/fonts"
  fi
  # Превью: та же обложка с той же подписью, но картинкой — посмотреть
  # глазами, не гоняя кодировщик и не ловя в плеере 0.2 секунды.
  if [ "$PREVIEW" = 1 ]; then
    PNG="$BASE-обложка$i.png"
    "$FF" -y -v error -i "$PIC" -vf "scale=$DW:$DH:flags=lanczos$DRAW" -frames:v 1 "$PNG"
    echo "  превью обложки → $PNG"
    continue
  fi
  # [0] обложка · [1] картинка части · [2] та же часть, но из неё берётся
  # ТОЛЬКО звук, со сдвигом на длину обложки. Звук копией — без пережима.
  # -framerate у обложки обязателен: картинка по умолчанию идёт 25 к/с, и
  # на 30-кадровом ролике заставка выходила бы 5 кадров вместо 6.
  # -r на выходе обязателен: после concat частота теряется.
  VF="[0:v]scale=$DW:$DH:flags=lanczos$DRAW,format=$PIX,setsar=1,fps=$FPS[c];[1:v]setpts=PTS-STARTPTS,scale=$DW:$DH:flags=lanczos,format=$PIX,setsar=1[m];[c][m]concat=n=2:v=1[v]"
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
if [ "$PREVIEW" = 1 ]; then
  echo "Превью готовы: $i шт. Ролики НЕ резались — уберите слово «превью», чтобы нарезать."
else
  echo "Готово: $i шт., $BASE-часть1.mp4 … $BASE-часть$i.mp4"
fi
