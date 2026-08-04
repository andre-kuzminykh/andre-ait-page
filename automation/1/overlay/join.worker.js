/* Сборка «обложка + ролик» прямо в браузере — FR-SITE23.
 *
 * Ядро ffmpeg.wasm живёт в этом воркере, а не в странице: exec() блокирующий,
 * на главном потоке он на полминуты подвесил бы вкладку вместе с прогрессом.
 *
 * Главное свойство: дорожка ролика КОПИРУЕТСЯ (-c copy), а не пережимается.
 * Ради секунды заставки перекодировать весь исходник — потерять качество.
 */
importScripts('vendor/ffmpeg-core.js');

var core = null;
var out = [];                       // строки лога последней команды

/* Обложку кодируем ТЕМ ЖЕ кодеком, что и ролик. Иначе склейка потоков
   молча собирает файл, где дорожка объявлена как h264, а пакеты внутри
   h265: плеер показывает секунду заставки и глохнет, а файл весит в сто
   раз меньше исходника. Именно так это и сломалось в первый раз.

   H.265 в списке нет намеренно. libx265 в ядре есть, но в wasm он
   однопоточный и без ассемблера: тридцать кадров 1080×1920 не уложились
   и в десять минут (замерено). Лучше честно отказать, чем подвесить
   вкладку на полчаса. */
var ENCODER = { h264: 'libx264' };

function say(stage, pct) {
    self.postMessage({ type: 'stage', stage: stage, pct: pct });
}

/* ffprobe отдаёт поля в порядке потока, а не в порядке -show_entries,
   поэтому читаем по ключам: позиционный разбор молча врёт (pix_fmt
   приезжал на месте fps и заставка не кодировалась). */
function probe(file, section, fields, stream) {
    out = [];
    var args = ['-v', 'error'];
    if (stream) args = args.concat(['-select_streams', stream]);
    args = args.concat(['-show_entries', section + '=' + fields,
        '-of', 'default=noprint_wrappers=1', file]);
    core.ffprobe.apply(core, args);
    core.reset();
    var kv = {};
    out.join('\n').split('\n').forEach(function (line) {
        var i = line.indexOf('=');
        if (i > 0) {
            var val = line.slice(i + 1).trim();
            if (val && val !== 'N/A') kv[line.slice(0, i).trim()] = val;
        }
    });
    return kv;
}

function run(args, what) {
    out = [];
    core.exec.apply(core, args);
    var ret = core.ret;
    core.reset();
    if (ret !== 0) throw new Error(what + ': ' + out.join(' | '));
}

self.onmessage = function (e) {
    var m = e.data;
    (async function () {
        try {
            if (!core) {
                say('Загружаю ffmpeg…', 3);
                core = await createFFmpegCore({ mainScriptUrlOrBlob: m.coreURL });
                core.setLogger(function (d) { if (d && d.message) out.push(d.message); });
            }
            core.FS.writeFile('cover.png', m.cover);
            core.FS.writeFile('in.mp4', m.video);
            var inSize = m.video.length;

            say('Читаю параметры ролика…', 12);
            var v = probe('in.mp4', 'stream', 'codec_name,codec_tag_string,width,height,r_frame_rate,pix_fmt', 'v:0');
            var a = probe('in.mp4', 'stream', 'codec_name,sample_rate,channels', 'a:0');
            var f = probe('in.mp4', 'format', 'duration');
            var W = v.width, H = v.height, FPS = v.r_frame_rate;
            var PIX = v.pix_fmt || 'yuv420p';
            var inDur = parseFloat(f.duration || '0');
            if (!W || !H || !FPS) throw new Error('не удалось прочитать параметры ролика');
            self.postMessage({ type: 'probe', video: v, audio: a, duration: inDur });

            var VENC = ENCODER[v.codec_name];
            if (!VENC) throw new Error('ролик в кодеке ' + (v.codec_name || '?').toUpperCase() +
                ', а в браузере обложку можно подготовить только под H.264. ' +
                'Выход: экспортировать ролик в H.264 — либо собрать скриптом, ' +
                'у ffmpeg на компьютере с этим проблем нет');
            var hasAudio = !!a.codec_name;
            if (hasAudio && a.codec_name !== 'aac') throw new Error('звук в кодеке «' +
                a.codec_name + '» — склейка без перекодирования не сойдётся');

            // 1. Заставка → клип ровно с теми же параметрами, что у ролика:
            //    кодек, тег, размер, частота кадров, формат пикселей и звук.
            say('Готовлю обложку…', 25);
            var args = ['-y', '-loglevel', 'error',
                '-loop', '1', '-framerate', FPS, '-t', String(m.sec), '-i', 'cover.png'];
            if (hasAudio) {
                args = args.concat(['-f', 'lavfi', '-t', String(m.sec),
                    '-i', 'anullsrc=r=' + a.sample_rate + ':cl=' +
                          (a.channels === '1' ? 'mono' : 'stereo')]);
            }
            args = args.concat([
                '-vf', 'scale=' + W + ':' + H + ':flags=lanczos,format=' + PIX + ',setsar=1',
                '-c:v', VENC, '-preset', 'medium', '-crf', '14', '-pix_fmt', PIX]);
            if (v.codec_tag_string && /^[a-z0-9]{4}$/i.test(v.codec_tag_string)) {
                args = args.concat(['-tag:v', v.codec_tag_string]);
            }
            args = hasAudio
                ? args.concat(['-c:a', 'aac', '-b:a', '192k',
                    '-ar', a.sample_rate, '-ac', a.channels, '-shortest'])
                : args.concat(['-an']);
            run(args.concat(['cover.mp4']), 'обложка');

            // 2. Склейка потоков. Ролик копируется байт в байт.
            say('Склеиваю…', 60);
            core.FS.writeFile('list.txt',
                new TextEncoder().encode("file 'cover.mp4'\nfile 'in.mp4'\n"));
            run(['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'list.txt',
                '-c', 'copy', '-movflags', '+faststart', 'out.mp4'], 'склейка');

            /* 3. Проверка результата. Склейка потоков умеет возвращать 0 и при
               этом уложить пакеты ролика под параметры декодера обложки: файл
               выходит нужного веса и длины, а плеер показывает одну заставку и
               глохнет. Ловит это только попытка ДЕКОДИРОВАТЬ то, что вышло. */
            say('Проверяю результат…', 85);
            var outStat = core.FS.stat('out.mp4');
            var outDur = parseFloat(probe('out.mp4', 'format', 'duration').duration || '0');
            var wantDur = inDur + Number(m.sec);
            if (inDur && Math.abs(outDur - wantDur) > 1.5) {
                throw new Error('длительность не сошлась: ожидал ' + wantDur.toFixed(1) +
                    ' с, получилось ' + outDur.toFixed(1) + ' с');
            }
            if (outStat.size < inSize) {
                throw new Error('файл получился меньше исходника (' +
                    Math.round(outStat.size / 1048576) + ' МБ против ' +
                    Math.round(inSize / 1048576) + ' МБ) — дорожка потерялась при склейке');
            }
            out = [];
            core.exec('-v', 'error', '-ss', String(Number(m.sec) + 1), '-t', '3',
                '-i', 'out.mp4', '-f', 'null', '-');
            core.reset();
            /* «Aborted()» ядро печатает в конце ЛЮБОЙ команды — это его способ
               завершить процесс, а не ошибка. Без этого фильтра проверка
               заворачивала и совершенно здоровые H.264-склейки. */
            var noise = out.filter(function (l) {
                return l && l.trim() && !/^Aborted\(\)/.test(l.trim());
            });
            if (noise.length) {
                throw new Error('склеенный файл не декодируется после заставки (' +
                    noise[0].slice(0, 90) + '). Параметры декодера у обложки и ролика ' +
                    'не совпали — соберите скриптом, он умеет пересобрать');
            }

            say('Отдаю файл…', 95);
            var data = core.FS.readFile('out.mp4');
            ['cover.png', 'in.mp4', 'cover.mp4', 'list.txt', 'out.mp4'].forEach(function (name) {
                try { core.FS.unlink(name); } catch (ignored) { /* уже нет */ }
            });
            self.postMessage({
                type: 'done', data: data,
                info: v.codec_name + ' ' + W + '×' + H + ', ' + Math.round(outDur) + ' с'
            }, [data.buffer]);
        } catch (err) {
            self.postMessage({ type: 'error', message: String((err && err.message) || err) });
        }
    })();
};
