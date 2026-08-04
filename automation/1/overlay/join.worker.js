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

function say(stage, pct) {
    self.postMessage({ type: 'stage', stage: stage, pct: pct });
}

/* ffprobe отдаёт поля в порядке потока, а не в порядке -show_entries,
   поэтому читаем по ключам: позиционный разбор молча врёт (pix_fmt
   приезжал на месте fps и заставка не кодировалась). */
function probe(fields, stream) {
    out = [];
    core.ffprobe('-v', 'error', '-select_streams', stream, '-show_entries',
        'stream=' + fields, '-of', 'default=noprint_wrappers=1', 'in.mp4');
    core.reset();
    var kv = {};
    out.join('\n').split('\n').forEach(function (line) {
        var i = line.indexOf('=');
        if (i > 0) kv[line.slice(0, i).trim()] = line.slice(i + 1).trim();
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

            say('Читаю параметры ролика…', 12);
            var v = probe('width,height,r_frame_rate,pix_fmt', 'v:0');
            var a = probe('sample_rate,channels', 'a:0');
            var W = v.width, H = v.height, FPS = v.r_frame_rate;
            var PIX = v.pix_fmt || 'yuv420p';
            var AR = a.sample_rate || '48000', AC = a.channels || '2';
            if (!W || !H || !FPS) throw new Error('не удалось прочитать параметры ролика');
            self.postMessage({ type: 'probe', video: v, audio: a });

            // 1. Заставка → клип ровно с теми же параметрами, что у ролика.
            //    Иначе склейка потоков откажется их соединять.
            say('Готовлю обложку…', 25);
            run(['-y', '-loglevel', 'error',
                '-loop', '1', '-framerate', FPS, '-t', String(m.sec), '-i', 'cover.png',
                '-f', 'lavfi', '-t', String(m.sec),
                '-i', 'anullsrc=r=' + AR + ':cl=' + (AC === '1' ? 'mono' : 'stereo'),
                '-vf', 'scale=' + W + ':' + H + ':flags=lanczos,format=' + PIX + ',setsar=1',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', PIX,
                '-c:a', 'aac', '-b:a', '192k', '-ar', AR, '-ac', AC,
                '-shortest', 'cover.mp4'], 'обложка');

            // 2. Склейка потоков. Ролик копируется байт в байт.
            say('Склеиваю…', 60);
            core.FS.writeFile('list.txt',
                new TextEncoder().encode("file 'cover.mp4'\nfile 'in.mp4'\n"));
            try {
                run(['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'list.txt',
                    '-c', 'copy', '-movflags', '+faststart', 'out.mp4'], 'склейка');
            } catch (err) {
                // Параметры всё-таки разошлись — пересобираем целиком.
                // CRF 16 на глаз неотличим, но это уже перекодирование,
                // и пользователь должен об этом узнать, а не догадываться.
                self.postMessage({ type: 'reencode', reason: String(err.message || err) });
                say('Параметры не совпали, пересобираю целиком…', 65);
                run(['-y', '-loglevel', 'error', '-i', 'cover.mp4', '-i', 'in.mp4',
                    '-filter_complex', '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]',
                    '-map', '[v]', '-map', '[a]',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', PIX,
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', 'out.mp4'],
                    'пересборка');
            }

            say('Отдаю файл…', 95);
            var data = core.FS.readFile('out.mp4');
            ['cover.png', 'in.mp4', 'cover.mp4', 'list.txt', 'out.mp4'].forEach(function (f) {
                try { core.FS.unlink(f); } catch (ignored) { /* уже нет */ }
            });
            self.postMessage({ type: 'done', data: data }, [data.buffer]);
        } catch (err) {
            self.postMessage({ type: 'error', message: String((err && err.message) || err) });
        }
    })();
};
