# -*- coding: utf-8 -*-
"""Ширина строки по метрикам самого ttf — без браузера и без рендера.

Зачем. Владелец увидел «субтитры наслаиваются друг на друга»: длинная
реплика не влезала в полосу и переносилась на вторую строку. Ловить это
рендером дорого (Chromium или ffmpeg на каждый прогон), а строковый тест
«сколько слов» не ловит вовсе — «способны AI-агенты, важно посмотреть»
это четыре слова и 1120px при полосе 940. Поэтому читаем cmap и hmtx
шрифта и складываем ширины букв: обычный pytest, никаких зависимостей.

Оценка идёт СВЕРХУ: кернинг (у Montserrat он в GPOS и почти всегда
отрицательный) и отрицательный letter-spacing страницы делают настоящую
строку чуть уже. Значит «влезло по метрикам» → влезет и в кадре.
"""
import struct


class Шрифт(object):
    def __init__(self, путь):
        self.d = d = open(путь, "rb").read()
        self.t = {}
        for i in range(struct.unpack(">H", d[4:6])[0]):
            o = 12 + 16 * i
            self.t[d[o:o + 4].decode("latin1")] = struct.unpack(">II", d[o + 8:o + 16])
        self.upem = struct.unpack(">H", d[self.t["head"][0] + 18:self.t["head"][0] + 20])[0]
        self.hmetrics = struct.unpack(">H", d[self.t["hhea"][0] + 34:self.t["hhea"][0] + 36])[0]
        self.hmtx = self.t["hmtx"][0]
        self.cmap = self._cmap()

    def _cmap(self):
        """Юникод → номер глифа из подтаблицы формата 4."""
        d, (o, _) = self.d, self.t["cmap"]
        адрес = None
        for i in range(struct.unpack(">H", d[o + 2:o + 4])[0]):
            pid, eid, off = struct.unpack(">HHI", d[o + 4 + 8 * i:o + 12 + 8 * i])
            if struct.unpack(">H", d[o + off:o + off + 2])[0] == 4 and \
                    (pid, eid) in ((3, 1), (3, 10), (0, 3), (0, 4)):
                адрес = o + off
        if адрес is None:
            raise ValueError("в шрифте нет cmap формата 4")
        o = адрес
        seg2 = struct.unpack(">H", d[o + 6:o + 8])[0]
        seg = seg2 // 2
        ends = struct.unpack(">%dH" % seg, d[o + 14:o + 14 + seg2])
        s = o + 16 + seg2
        starts = struct.unpack(">%dH" % seg, d[s:s + seg2]); s += seg2
        deltas = struct.unpack(">%dh" % seg, d[s:s + seg2]); s += seg2
        база = s
        ranges = struct.unpack(">%dH" % seg, d[s:s + seg2])
        карта = {}
        for i in range(seg):
            for c in range(starts[i], min(ends[i], 0xFFFF) + 1):
                if ranges[i] == 0:
                    g = (c + deltas[i]) & 0xFFFF
                else:
                    a = база + 2 * i + ranges[i] + 2 * (c - starts[i])
                    if a + 2 > len(d):
                        continue
                    g = struct.unpack(">H", d[a:a + 2])[0]
                    if g:
                        g = (g + deltas[i]) & 0xFFFF
                if g:
                    карта[c] = g
        return карта

    def аванс(self, глиф):
        i = min(глиф, self.hmetrics - 1)
        return struct.unpack(">H", self.d[self.hmtx + 4 * i:self.hmtx + 4 * i + 2])[0]

    def ширина(self, текст, кегль):
        """Ширина строки в пикселях при данном кегле."""
        сумма = 0
        for ch in текст:
            г = self.cmap.get(ord(ch))
            if г is None:                      # нет буквы в шрифте — считаем по «?»
                г = self.cmap.get(ord("?"), 0)
            сумма += self.аванс(г)
        return сумма * кегль / float(self.upem)

    def коэффициент_libass(self):
        """Во сколько раз libass рисует МЕЛЬЧЕ, чем сказано в Fontsize.

        libass (вслед за VSFilter) трактует Fontsize как высоту строки
        winAscent+winDescent из таблицы OS/2, а не как размер em. У
        Montserrat Black это 1.562em, поэтому «Fontsize 53» выходит на
        экран как 34px. Собирающий скрипт умножает кегль на обратную
        величину — иначе вжжённые субтитры мельче превью в полтора раза.
        """
        o, _ = self.t["OS/2"]
        винА = struct.unpack(">H", self.d[o + 74:o + 76])[0]
        винН = struct.unpack(">H", self.d[o + 76:o + 78])[0]
        return self.upem / float(винА + винН)


if __name__ == "__main__":
    import sys
    ш = Шрифт(sys.argv[1])
    кегль = float(sys.argv[3]) if len(sys.argv) > 3 else 50.0
    print("%.0fpx: %.1fpx  «%s»" % (кегль, ш.ширина(sys.argv[2], кегль), sys.argv[2]))
