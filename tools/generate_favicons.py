#!/usr/bin/env python3
# Mushroom Lab — favicon generator (v4): tiny-size tuning so the mushroom is visible at 16×16.
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import json

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / "assets" / "favicon"
OUT.mkdir(parents=True, exist_ok=True)

FG    = (233,238,242,255)   # mushroom fill
OUTL  = (7,10,19,255)       # dark outline (helps on light tab bars)
EYES  = (15,18,24,255)
RINGC = (20,255,236,230)    # teal ring
CARD  = (11,14,18,255)      # iOS card bg

def draw_mushroom(d: ImageDraw.ImageDraw, cx, cy, s, *, with_eyes=True, outline_px=0):
    # Cap
    cap_w, cap_h = 184*s, 136*s
    cap_box = [cx-cap_w/2, cy-38*s-cap_h/2, cx+cap_w/2, cy-38*s+cap_h/2]
    if outline_px:
        d.ellipse(cap_box, outline=OUTL, width=outline_px)
    d.ellipse(cap_box, fill=FG)

    # Stem
    stem_w, stem_h = 72*s, 96*s
    stem_box = [cx-stem_w/2, cy-6*s, cx+stem_w/2, cy-6*s+stem_h]
    r = int(18*s)
    if outline_px:
        d.rounded_rectangle(stem_box, radius=r, outline=OUTL, width=outline_px)
    d.rounded_rectangle(stem_box, radius=r, fill=FG)

    # Eyes (skip below 48px final icon)
    if with_eyes:
        er = 4*s
        d.ellipse([cx-16*s-er, cy+22*s-er, cx-16*s+er, cy+22*s+er], fill=EYES)
        d.ellipse([cx+16*s-er, cy+22*s-er, cx+16*s+er, cy+22*s+er], fill=EYES)

def render_icon(size: int, *, ring=True):
    im = Image.new("RGBA", (size,size), (0,0,0,0))
    d  = ImageDraw.Draw(im, "RGBA")
    s  = size/256.0
    cx = cy = size/2

    # Optional teal ring (suppressed at tiny sizes)
    if ring:
        pad   = int(size*0.09)
        width = max(2, int(size*0.08))
        d.ellipse([pad,pad,size-pad,size-pad], outline=RINGC, width=width)
        im = im.filter(ImageFilter.GaussianBlur(max(0, int(size*0.004))))

    # Soft shadow for readability
    sh = Image.new("RGBA",(size,size),(0,0,0,0))
    ds = ImageDraw.Draw(sh,"RGBA")
    draw_mushroom(ds, cx, cy, s, with_eyes=False)
    sh = sh.filter(ImageFilter.GaussianBlur(max(1,int(size*0.03))))
    sh = Image.eval(sh, lambda p: int(p*0.22))
    im.alpha_composite(sh)

    # Outline for tiny sizes
    outline_px = 0
    eyes = True
    if size <= 32:
        outline_px = 2 if size >= 24 else 1
        eyes = False
    elif size < 48:
        outline_px = 1
        eyes = False

    draw_mushroom(d, cx, cy, s, with_eyes=eyes, outline_px=outline_px)
    return im

# Transparent PNGs (ring only for ≥64)
for n in [16,24,32,48,64,128,192,256,512]:
    img = render_icon(n, ring=(n>=64))
    img.save(OUT/f"icon-{n}.png")

# Standard names
Image.open(OUT/"icon-16.png").save(OUT/"favicon-16x16.png")
Image.open(OUT/"icon-32.png").save(OUT/"favicon-32x32.png")
Image.open(OUT/"icon-192.png").save(OUT/"android-chrome-192x192.png")
Image.open(OUT/"icon-512.png").save(OUT/"android-chrome-512x512.png")

# Multi-size ICO (Windows/Chrome prefer this)
Image.open(OUT/"icon-64.png").save(
    OUT/"favicon.ico", format="ICO",
    sizes=[(16,16),(24,24),(32,32),(48,48),(64,64)]
)

# Apple touch icon (iOS wants a card)
def apple_icon(size=180):
    card = Image.new("RGBA",(size,size),CARD)
    # gentle vignette
    m = Image.new("L",(size,size),0); dm=ImageDraw.Draw(m)
    dm.ellipse((-int(size*.2),-int(size*.2),int(size*1.2),int(size*1.2)), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(int(size*.12)))
    lifted = Image.composite(Image.new("RGBA",(size,size),(16,22,30,255)), card, m)
    g = render_icon(int(size*0.70), ring=True)
    out = Image.new("RGBA",(size,size),CARD)
    out.alpha_composite(lifted)
    out.alpha_composite(g, (int(size*0.15), int(size*0.15)))
    rr = Image.new("L",(size,size),0); dr=ImageDraw.Draw(rr)
    dr.rounded_rectangle([0,0,size,size], radius=int(size*0.22), fill=255)
    out.putalpha(rr); return out

apple_icon(180).save(OUT/"apple-touch-icon.png")

# Simple transparent SVG (mushroom + ring)
svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <circle cx="128" cy="128" r="112" fill="none" stroke="#14ffec" stroke-width="14" stroke-linecap="round" opacity="0.85"/>
  <g fill="#e9eef2" stroke="#070a13" stroke-width="3">
    <ellipse cx="128" cy="90" rx="92" ry="68"/>
    <rect x="94" y="106" width="68" height="92" rx="18" ry="18"/>
  </g>
</svg>"""
(OUT/"favicon.svg").write_text(svg, encoding="utf-8")

# Safari pinned tab mask (monochrome)
(OUT/"safari-pinned-tab.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">'
    '<ellipse cx="128" cy="90" rx="92" ry="68" fill="#000"/>'
    '<rect x="94" y="106" width="68" height="92" rx="18" ry="18" fill="#000"/>'
    '</svg>',
    encoding="utf-8"
)

# Manifest
(OUT/"site.webmanifest").write_text(json.dumps({
  "name":"Mushroom Lab",
  "short_name":"MushroomLab",
  "icons":[
    {"src":"/assets/favicon/android-chrome-192x192.png","sizes":"192x192","type":"image/png"},
    {"src":"/assets/favicon/android-chrome-512x512.png","sizes":"512x512","type":"image/png"}
  ],
  "theme_color":"#0b0e12",
  "background_color":"#0b0e12",
  "display":"standalone"
}, indent=2), encoding="utf-8")

print("Favicons written to", OUT)
