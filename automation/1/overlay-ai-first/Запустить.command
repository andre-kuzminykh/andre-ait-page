#!/bin/sh
# Открывает страницу через локальный сервер.
#
# Зачем сервер: страница читает слова субтитров из соседнего файла
# «субтитры.srt», а из file:// браузер соседний файл не отдаёт — это его
# политика безопасности, обойти её нельзя. Из http://127.0.0.1 всё работает.
#
# macOS: двойной клик по файлу. Linux: sh Запустить.command
cd "$(dirname "$0")" || exit 1
PORT=8767
URL="http://127.0.0.1:$PORT/index.html"

if command -v python3 >/dev/null 2>&1;   then SRV="python3 -m http.server $PORT"
elif command -v python >/dev/null 2>&1;  then SRV="python -m SimpleHTTPServer $PORT"
elif command -v php >/dev/null 2>&1;     then SRV="php -S 127.0.0.1:$PORT"
else
    echo "Не нашёл ни python3, ни php — нечем поднять локальный сервер."
    echo "Поставьте python3 или откройте папку любым другим веб-сервером."
    read -r _ ; exit 1
fi

$SRV >/dev/null 2>&1 &
SRV_PID=$!
sleep 1
(open "$URL" 2>/dev/null || xdg-open "$URL" 2>/dev/null) &

echo "Страница открыта: $URL"
echo "Это окно держит сервер — сверните его, но не закрывайте."
echo "Закончили — нажмите Ctrl+C."
trap 'kill $SRV_PID 2>/dev/null' EXIT
wait $SRV_PID
