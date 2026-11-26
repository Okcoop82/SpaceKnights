"""Draws the app icon (shield + sword) at the sizes phones need."""
from PIL import Image, ImageDraw
import os
OUT = os.path.join(os.path.dirname(__file__), "..", "icons")
VOID, HULL, AMBER, CYAN = (10,14,19), (17,24,32), (240,176,60), (92,200,214)

def draw(size, pad_frac):
    S = 1024
    im = Image.new("RGB", (S, S), VOID)
    d = ImageDraw.Draw(im)
    # subtle panel ring
    d.ellipse([60,60,S-60,S-60], fill=HULL)
    p = pad_frac * S
    cx, top, bot, w = S/2, p, S - p, (S - 2*p) * 0.78
    l, r = cx - w/2, cx + w/2
    mid = top + (bot-top)*0.55
    shield = [(l, top+40), (cx, top), (r, top+40), (r, mid), (cx, bot), (l, mid)]
    d.polygon(shield, fill=AMBER)
    inset = 46
    inner = [(l+inset, top+40+inset*0.55), (cx, top+inset), (r-inset, top+40+inset*0.55),
             (r-inset, mid-6), (cx, bot-inset*1.6), (l+inset, mid-6)]
    d.polygon(inner, fill=VOID)
    # sword
    bw = w*0.09
    d.polygon([(cx-bw/2, top+inset+60), (cx, top+inset+10), (cx+bw/2, top+inset+60),
               (cx+bw/2, bot-inset*1.6-150), (cx-bw/2, bot-inset*1.6-150)], fill=CYAN)
    gy = top + (bot-top)*0.62
    d.rectangle([cx-w*0.30, gy, cx+w*0.30, gy+bw*0.8], fill=AMBER)
    d.rectangle([cx-bw*0.35, gy+bw*0.8, cx+bw*0.35, gy+bw*0.8+110], fill=AMBER)
    return im

def save(im, n, name):
    im.resize((n, n), Image.LANCZOS).save(os.path.join(OUT, name))

std = draw(1024, 0.17)
mask = draw(1024, 0.24)   # extra margin so Android's circle crop never clips it
for n in (192, 512): save(std, n, f"icon-{n}.png")
for n in (192, 512): save(mask, n, f"maskable-{n}.png")
save(mask, 180, "apple-touch-icon.png")
save(std, 32, "favicon-32.png")
