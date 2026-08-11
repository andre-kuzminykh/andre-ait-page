# -*- coding: utf-8 -*-
"""Синхронно переводит англицизмы в книге и в данных панели всех восьми лекций.

    python3 apply_terms.py --dry     # только показать, что изменится
    python3 apply_terms.py           # записать

Запускать из корня репозитория.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import translit

BOOK = 'automation/AI_Automation Engineer_Book.txt'
DRY = '--dry' in sys.argv


def do_book():
    raw = open(BOOK, 'rb').read().decode('utf-8-sig')
    crlf = '\r\n' in raw
    text = raw.replace('\r\n', '\n')
    new = translit.translate(text)
    changed = sum(1 for a, b in zip(text.split('\n'), new.split('\n')) if a != b)
    print('книга: изменённых строк %d' % changed)
    if not DRY:
        out = new.replace('\n', '\r\n') if crlf else new
        open(BOOK, 'wb').write(b'\xef\xbb\xbf' + out.encode('utf-8'))
    return text, new


def do_panels():
    total = 0
    for n in range(1, 9):
        path = 'automation/%d/index.html' % n
        if not os.path.exists(path):
            continue  # закрытый модуль — файла нет
        html = open(path, encoding='utf-8').read()
        m = re.search(r'(<script id="slide-notes"[^>]*>)(.*?)(</script>)', html, re.S)
        data = json.loads(m.group(2))
        hits = 0
        for key, note in data.items():
            if note.get('title'):
                t = translit.translate(note['title'])
                if t != note['title']:
                    note['title'] = t; hits += 1
            for b in note.get('blocks', []):
                v = b['v']
                if isinstance(v, list):
                    nv = [translit.translate(x) for x in v]
                else:
                    nv = translit.translate(v)
                if nv != v:
                    b['v'] = nv; hits += 1
        print('лекция %d: изменённых блоков %d' % (n, hits))
        total += hits
        if not DRY:
            body = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            html = html[:m.start(2)] + body + html[m.end(2):]
            open(path, 'w', encoding='utf-8').write(html)
    print('всего блоков панели изменено: %d' % total)


if __name__ == '__main__':
    old, new = do_book()
    do_panels()
    if DRY:
        print('\n--- строки книги, где остались латинские слова ---')
        skip = re.compile(r'^[\sA-Za-z0-9=+\-*/().,:;{}\[\]"\'|<>%№#@?!]*$')
        for i, l in enumerate(new.split('\n')):
            for w in re.findall(r"[A-Za-z][A-Za-z\-']{2,}", l):
                print('  L%-5d %s' % (i + 1, w))
                break
