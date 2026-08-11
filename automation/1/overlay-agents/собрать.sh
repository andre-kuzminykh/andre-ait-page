#!/bin/sh
# Обложка 0.2 с + ролик + графика + субтитры, вжжённые в кадр.
#
# Графику и субтитры нельзя доложить копированием дорожки — их надо
# нарисовать поверх КАЖДОГО кадра. Значит одна пересборка, с битрейтом
# исходника: второй проход на 10+ Мбит/с на глаз неотличим, а раздувать
# файл незачем.
#
# СЛОВА СУБТИТРОВ ЖИВУТ В ФАЙЛЕ «субтитры.srt» РЯДОМ. Поправили слово —
# просто запустите скрипт заново: перерендеривать графику не нужно,
# субтитров в слое нет, они вжигаются из этого файла.
#
# Запуск:  sh собрать.sh "ваше видео.MOV"   (кавычки — если в имени пробелы)
set -e
# ffmpeg-ов в системе бывает несколько: conda затеняет brew, а её сборка
# урезана — без libass, то есть без фильтра subtitles («No such filter»).
# Поэтому команда ffmpeg не берётся на веру: перебираем кандидатов и
# берём первого, кто реально умеет вжигать субтитры.
FF=""; FULL=0
for c in ffmpeg /opt/homebrew/bin/ffmpeg /usr/local/bin/ffmpeg; do
  command -v "$c" >/dev/null 2>&1 || continue
  if "$c" -hide_banner -filters 2>/dev/null | grep -q " subtitles "; then FF="$c"; FULL=1; break; fi
  [ -n "$FF" ] || FF="$c"
done
[ -n "$FF" ] || { echo "Нет ffmpeg вообще. macOS: brew install ffmpeg"; exit 1; }
FP="$(dirname "$FF")/ffprobe"; [ -x "$FP" ] || FP=ffprobe
command -v "$FP" >/dev/null || { echo "Рядом с $FF нет ffprobe"; exit 1; }
echo "ffmpeg: $FF"
DIR=$(cd "$(dirname "$0")" && pwd)
for f in cover.png overlay_c.mp4 overlay_a.mp4 субтитры.srt fonts/Montserrat-Black.ttf; do
  [ -f "$DIR/$f" ] || { echo "Рядом со скриптом нет $f"; exit 1; }
done

# Запасной путь без libass: субтитры лежат ГОТОВЫМ слоем (subs_c/subs_a),
# нужны только overlay и alphamerge — они есть даже в урезанной сборке.
# Но слой отрендерен из конкретного текста: если субтитры.srt правился,
# честно останавливаемся, а не собираем со старыми словами.
if [ "$FULL" = 0 ]; then
  for f in subs_c.mp4 subs_a.mp4 субтитры.sha; do
    [ -f "$DIR/$f" ] || { echo "Этот ffmpeg без libass, а запасного слоя субтитров ($f) нет. Поставьте полный: brew install ffmpeg"; exit 1; }
  done
  WANT=$(cat "$DIR/субтитры.sha")
  GOT=$( (shasum -a 256 "$DIR/субтитры.srt" 2>/dev/null || sha256sum "$DIR/субтитры.srt") | cut -d" " -f1 )
  if [ "$GOT" != "$WANT" ]; then
    echo "субтитры.srt правился, а этот ffmpeg вжигать текст не умеет (нет libass):"
    echo "готовый слой субтитров собран из ПРЕЖНЕГО текста, правки бы потерялись."
    echo "Поставьте полный ffmpeg (brew install ffmpeg) — тогда правки вожгутся, — или пришлите новый субтитры.srt мне, пересоберу слой."
    exit 1
  fi
  echo "Субтитры: ffmpeg без libass — беру готовый слой (текст совпадает с субтитры.srt)"
fi
VIDEO="${1:-video.mp4}"
[ -f "$VIDEO" ] || { echo "Не найден файл: $VIDEO"; exit 1; }
# Дважды собранный ролик — верный способ получить ДВЕ строки
# субтитров друг на друге: во второй заход они лягут поверх уже
# вжжённых. Ловим по имени файла.
case "$VIDEO" in
  *-готовый.mp4|*-готовый.MP4)
    echo "Это уже собранный ролик: субтитры и графика в нём вжжены."
    echo "Второй заход положит вторую строку субтитров поверх первой."
    echo "Возьмите ИСХОДНЫЙ дубль. Если всё же надо — sh собрать.sh \"$VIDEO\" заново"
    [ "$2" = "заново" ] || exit 1 ;;
esac
OUT="${VIDEO%.*}-готовый.mp4"
SEC=0.2   # обложка: столько секунд cover.png перед роликом

p()  { "$FP" -v error -select_streams "$1" -show_entries stream="$2"  -of csv=p=0 "$VIDEO"; }
pf() { "$FP" -v error -show_entries format="$1" -of csv=p=0 "$VIDEO"; }
W=$(p v:0 width);  H=$(p v:0 height)
FPS=$(p v:0 r_frame_rate)
PIX=$(p v:0 pix_fmt); VCODEC=$(p v:0 codec_name); ACODEC=$(p a:0 codec_name); BR=$(pf bit_rate)
ROT=$("$FP" -v error -select_streams v:0 -show_entries stream_side_data=rotation -of csv=p=0 "$VIDEO" 2>/dev/null | head -1)
: "${ROT:=0}"
# Снятый телефоном ролик часто лежит боком плюс метка поворота: работаем
# в тех размерах, в каких кадр ВИДЕН, а не в каких хранится.
case "$ROT" in 90|-90|270|-270) DW=$H; DH=$W ;; *) DW=$W; DH=$H ;; esac
echo "Ролик: $VCODEC ${DW}x${DH}, поворот $ROT, звук ${ACODEC:-нет}"

# Субтитры: SRT → ASS средствами самого ffmpeg, потом подменяется строка
# стиля. Через force_style то же самое не выходит: запятые внутри стиля
# ffmpeg считает своими разделителями, и субтитр молча не рисуется —
# проверено, кадр остаётся чистым, без единой ошибки в логе.
# Имя файла — явным ключом filename=: ffmpeg 8 (brew на маке) короткую
# форму subtitles=файл не разбирает («No option name near …»), а с
# ключом одинаково работают и 7-я, и 8-я версии.
# Имена рабочих файлов латиницей и без пробелов: путь уходит внутрь
# фильтра, где двоеточия и пробелы пришлось бы экранировать.
TMP=.overlay-build
if [ "$FULL" = 1 ]; then
rm -rf "$TMP"; mkdir -p "$TMP/fonts"
cp "$DIR/fonts/Montserrat-Black.ttf" "$TMP/fonts/"
"$FF" -y -v error -i "$DIR/субтитры.srt" "$TMP/raw.ass"
SUBSIZE=$(awk -v h="$DH" 'BEGIN{ printf "%d", h*0.028 }')
MARGIN=$(awk -v h="$DH" 'BEGIN{ printf "%d", h*0.193 }')
OUTLINE=$(awk -v s="$SUBSIZE" 'BEGIN{ v=int(s/13); if(v<3) v=3; printf "%d", v }')
STYLE="Style: Default,Montserrat Black,$SUBSIZE,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,$OUTLINE,0,2,60,60,$MARGIN,1"
# Имя шрифта — ПОЛНОЕ («Montserrat Black», это name ID 1 в ttf).
# По семейному имени «JetBrains Mono» libass шрифт не находит и молча
# уходит в системный: проверено — кадр с ним побайтово совпал с кадром,
# где указан заведомо несуществующий шрифт.
# ffmpeg пишет ASS в координатах 384x288 — переводим их в размер кадра,
# иначе кегль и отступ субтитров считаются не от того.
awk -v st="$STYLE" -v w="$DW" -v h="$DH" '/^Style: Default,/{print st;next} /^PlayResX:/{print "PlayResX: " w;next} /^PlayResY:/{print "PlayResY: " h;next} {print}' "$TMP/raw.ass" > "$TMP/subs.ass"
fi
# Битрейт как у исходника, но не ниже 10 Мбит/с.
TARGET=$(awk -v b="${BR:-0}" 'BEGIN{ if(b<1) b=12000000; if(b<10000000) b=10000000; printf "%d", b }')
HW=$("$FF" -hide_banner -encoders 2>/dev/null | grep -o "hevc_videotoolbox\|h264_videotoolbox" | tr "\n" " ")
case "$VCODEC:$HW" in
  hevc:*hevc_videotoolbox*) VE="hevc_videotoolbox -b:v $TARGET -tag:v hvc1" ;;
  *:*h264_videotoolbox*)    VE="h264_videotoolbox -b:v $TARGET" ;;
  hevc:*)                   VE="libx265 -preset medium -crf 18 -tag:v hvc1 -x265-params log-level=none" ;;
  *)                        VE="libx264 -preset medium -crf 17" ;;
esac
echo "Кодировщик: $VE"
echo "Собираю: обложка ${SEC}с + ролик + графика + субтитры…"

# [0] обложка · [1] ролик · [2] цвет слоя · [3] маска слоя.
# Слой лежит ДВУМЯ файлами: прозрачности в mp4 нет, webm с альфой
# собирается не везде, а две дорожки в одном mp4 не переживают ремукс.
# alphamerge сшивает цвет с маской обратно в прозрачную картинку.
# tpad=stop=-1:clone держит ПОСЛЕДНИЙ кадр слоя до конца ролика: на нём
# только фирменная шапка, и она остаётся в кадре, даже если дубль
# длиннее слоя. Без этого хвост ролика шёл вообще без шапки.
# eof_action=pass: слой кончился — картинка идёт дальше. Со shortest=1
# ролик ДЛИННЕЕ слоя обрезался по слою: 70-секундный дубль выходил
# 59.12 с видео при 70 с звука — 11 секунд черноты под звук.
# setpts прижимает видеодорожку ролика к нулю: в MOV с телефона она
# бывает начинается позже звука, и тогда в начале чёрный кадр.
# Обложка приклеивается concat-ом ПОСЛЕ графики и субтитров: они
# накладываются на чистое время ролика, и тайминги от заставки не едут.
# После concat частота кадров ТЕРЯЕТСЯ (переход через overlay), и без
# явного -r на выходе ffmpeg молча писал 25 к/с, выбрасывая каждый
# шестой кадр 30-кадрового ролика. Фильтр fps после concat не годится:
# он на конце потока съедал последний кадр. Проверено покадрово:
# только с -r выходит ровно (кадры обложки) + (кадры ролика).
if [ "$FULL" = 1 ]; then
  VF="[0:v]scale=$DW:$DH:flags=lanczos,format=$PIX,setsar=1,fps=$FPS[c];[2:v]scale=$DW:$DH:flags=lanczos[oc];[3:v]scale=$DW:$DH:flags=lanczos[oa];[oc][oa]alphamerge,tpad=stop=-1:stop_mode=clone[ov];[1:v]setpts=PTS-STARTPTS[cv];[cv][ov]overlay=0:0:format=auto:eof_action=pass,subtitles=filename=$TMP/subs.ass:fontsdir=$TMP/fonts,format=$PIX,setsar=1[m];[c][m]concat=n=2:v=1[v]"
  EXTRA=""
else
  VF="[0:v]scale=$DW:$DH:flags=lanczos,format=$PIX,setsar=1,fps=$FPS[c];[2:v]scale=$DW:$DH:flags=lanczos[oc];[3:v]scale=$DW:$DH:flags=lanczos[oa];[oc][oa]alphamerge,tpad=stop=-1:stop_mode=clone[ov];[5:v]scale=$DW:$DH:flags=lanczos[tc];[6:v]scale=$DW:$DH:flags=lanczos[ta];[tc][ta]alphamerge[tv];[1:v]setpts=PTS-STARTPTS[cv];[cv][ov]overlay=0:0:format=auto:eof_action=pass[m1];[m1][tv]overlay=0:0:format=auto:eof_action=pass,format=$PIX,setsar=1[m];[c][m]concat=n=2:v=1[v]"
  # Путь к слою кладём в РАБОЧУЮ папку: $EXTRA подставляется в
  # команду без кавычек (иначе «-i файл» приедет одним аргументом),
  # а папка ролика вполне может называться «Где ИИ создаёт ценность» —
  # пробелы рвали команду, и ffmpeg искал файл «…/Desktop/Где».
  mkdir -p "$TMP"
  cp "$DIR/subs_c.mp4" "$TMP/sc.mp4"; cp "$DIR/subs_a.mp4" "$TMP/sa.mp4"
  EXTRA="-i $TMP/sc.mp4 -i $TMP/sa.mp4"
fi
# ЗВУК НЕ ТРОГАЕМ ВООБЩЕ — как в лекции. Обложка нужна только
# КАРТИНКЕ: пересобирается одна видеодорожка, а звук идёт копией из
# исходника отдельным входом (проверено md5 — бит-в-бит), просто
# начинается на длину заставки позже. Сдвиг = заставка ПЛЮС исходное
# смещение дорожек (edit list в MOV с телефона), воспроизводится
# контейнером: положительный — звук позже (-itsoffset), отрицательный —
# начало срезается (-ss) с точностью до одного AAC-кадра (~21 мс).
# Никакой растяжки aresample: она правила таймстемпы вставкой сэмплов
# и слышалась как искажение.
AS=$("$FP" -v error -select_streams a:0 -show_entries stream=start_time -of csv=p=0 "$VIDEO" 2>/dev/null || echo 0)
VS=$("$FP" -v error -select_streams v:0 -show_entries stream=start_time -of csv=p=0 "$VIDEO" 2>/dev/null || echo 0)
: "${AS:=0}"; : "${VS:=0}"
OFF=$(awk -v c="$SEC" -v a="$AS" -v v="$VS" 'BEGIN{ printf "%.3f", c + a - v }')
case "$OFF" in -*) AIN="-ss ${OFF#-}" ;; *) AIN="-itsoffset $OFF" ;; esac
# Пережим остаётся только для не-AAC дорожек: их в mp4 копией не положить.
AENC=aac; "$FF" -hide_banner -encoders 2>/dev/null | grep -q aac_at && AENC=aac_at
if [ -z "$ACODEC" ]; then
  AOPT="-an"; echo "Звук: в ролике его нет"
elif [ "$ACODEC" = "aac" ]; then
  AOPT="-c:a copy"; echo "Звук: копирую дорожку как есть (без пережима, сдвиг ${OFF}с)"
else
  AOPT="-c:a $AENC -b:a 256k"; echo "Звук: дорожка $ACODEC — в mp4 её копией не положить, пережимаю через $AENC 256k"
fi
# Входы: 0 обложка · 1 ролик · 2-3 слой графики · 4 ролик со сдвигом
# (из него берётся ТОЛЬКО звук) · 5-6 слой субтитров (только запасной
# путь). Аудиовход при EXTRA остаётся четвёртым: EXTRA идёт ПОСЛЕ него.
# -framerate у обложки обязателен: картинка по умолчанию идёт 25 к/с,
# и на 30-кадровом ролике заставка выходила 5 кадров (0.167 с) вместо 6.
if [ -n "$ACODEC" ]; then
  "$FF" -y -loglevel error -stats -loop 1 -framerate "$FPS" -t "$SEC" -i "$DIR/cover.png" \
    -i "$VIDEO" -i "$DIR/overlay_c.mp4" -i "$DIR/overlay_a.mp4" \
    $AIN -i "$VIDEO" $EXTRA \
    -filter_complex "$VF" \
    -map "[v]" -map 4:a:0 -r "$FPS" -c:v $VE -pix_fmt "$PIX" $AOPT -movflags +faststart "$OUT"
else
  "$FF" -y -loglevel error -stats -loop 1 -framerate "$FPS" -t "$SEC" -i "$DIR/cover.png" \
    -i "$VIDEO" -i "$DIR/overlay_c.mp4" -i "$DIR/overlay_a.mp4" \
    -f lavfi -t 0.1 -i anullsrc $EXTRA \
    -filter_complex "$VF" \
    -map "[v]" -r "$FPS" -c:v $VE -pix_fmt "$PIX" -an -movflags +faststart "$OUT"
fi
rm -rf "$TMP"

# Проверка декодированием: файл нужного размера и длины может не играть.
ERR=$("$FF" -v error -i "$OUT" -f null - 2>&1 || true)
[ -z "$ERR" ] || { echo "ОШИБКА: результат не декодируется — $(echo "$ERR" | head -1)"; exit 1; }
echo "Готово: $OUT"
