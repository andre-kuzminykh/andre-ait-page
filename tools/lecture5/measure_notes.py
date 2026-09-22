# -*- coding: utf-8 -*-
import io, json, glob, os, sys

NOTES = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'build', 'l5', 'notes')
def text(n):
    s = n['title']
    for b in n['blocks']:
        v = b['v']
        if b['t'] == 'cards': s += ''.join(c['h'] + c['p'] for c in v)
        elif isinstance(v, list): s += ''.join(v)
        else: s += v
    return s
bad = 0
for f in sorted(glob.glob(os.path.join(NOTES, '*.json'))):
    d = json.load(io.open(f, encoding='utf-8'))
    b = d['blocks']; p = sum(1 for x in b if x['t'] == 'p'); n = sum(1 for x in b if x['t'] == 'note')
    L = len(text(d))
    msg = []
    if not 6 <= len(b) <= 10: msg.append('блоков %d' % len(b))
    if p < 4: msg.append('p=%d' % p)
    if n != 1: msg.append('note=%d' % n)
    if not 2500 <= L <= 4000: msg.append('знаков %d' % L)
    if msg:
        bad += 1
        print(f, '->', ', '.join(msg))
print('проверено %d, с замечаниями %d' % (len(glob.glob(os.path.join(NOTES, '*.json'))), bad))
sys.exit(1 if bad else 0)
