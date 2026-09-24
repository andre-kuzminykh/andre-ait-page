# Склейка снимков в ряд для просмотра: montage.py out.png n_per_row scale files...
import sys
from PIL import Image
out, per, scale = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
files = sys.argv[4:]
ims = [Image.open(f).convert("RGB") for f in files]
ims = [im.resize((int(im.width*scale), int(im.height*scale)), Image.LANCZOS) for im in ims]
w = max(i.width for i in ims); h = max(i.height for i in ims)
rows = (len(ims)+per-1)//per
M = Image.new("RGB", (per*w + (per-1)*8, rows*h + (rows-1)*8), (128,128,128))
for n, im in enumerate(ims):
    M.paste(im, ((n%per)*(w+8), (n//per)*(h+8)))
M.save(out)
print(M.size)
