#!/usr/bin/env python3
"""Generate brand raster assets: apple-touch-icon.png (180) and og-image.png (1200x630).
Uses Pillow + macOS system fonts. Run: python3 make_images.py  (not deployed)."""
import os
from PIL import Image, ImageDraw, ImageFont
SITE = os.path.dirname(os.path.abspath(__file__))
INK=(15,27,45); TEAL=(14,110,122); TEALLT=(86,191,201); WHITE=(255,255,255); MUTED=(150,165,185)

def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)
MENLO="/System/Library/Fonts/Menlo.ttc"      # 0 reg, 1 bold
HELV="/System/Library/Fonts/Helvetica.ttc"   # 0 reg, 1 bold

def center_text(d, box, text, fnt, fill):
    x0,y0,x1,y1=box
    l,t,r,b=d.textbbox((0,0),text,font=fnt)
    w,h=r-l,b-t
    d.text((x0+(x1-x0-w)/2-l, y0+(y1-y0-h)/2-t), text, font=fnt, fill=fill)

# ---- apple-touch-icon 180x180 (iOS masks corners; fill full square) ----
ico=Image.new("RGB",(180,180),INK)
d=ImageDraw.Draw(ico)
center_text(d,(0,8,180,180),"SCR",font(MENLO,58,1),WHITE)
d.ellipse((138,30,160,52),fill=TEAL)
ico.save(os.path.join(SITE,"apple-touch-icon.png"))

# ---- og-image 1200x630 ----
W,H=1200,630
img=Image.new("RGB",(W,H),INK)
d=ImageDraw.Draw(img)
# subtle accent bar on the left
d.rectangle((0,0,10,H),fill=TEAL)
M=84
# brand mark badge
d.rounded_rectangle((M,72,M+64,72+64),radius=14,fill=TEAL)
center_text(d,(M,72,M+64,72+64),"SCR",font(MENLO,24,1),WHITE)
d.text((M+80,86),"Scientific Claim Registry",font=font(HELV,30,1),fill=WHITE)
# headline
hl=font(HELV,64,1)
d.text((M,206),"Publications have DOIs.",font=hl,fill=WHITE)
d.text((M,284),"Claims have no identity.",font=hl,fill=TEALLT)
# subline
d.text((M,398),"The Scientific Claim Registry — persistent IDs for scientific claims.",font=font(HELV,27,0),fill=MUTED)
# id row
ids=["DOI","ORCID","NCT","SCR-…"]
x=M
for i,t in enumerate(ids):
    f=font(MENLO,22,0)
    l,tt,r,b=d.textbbox((0,0),t,font=f); w=r-l
    pad=14
    fill=TEAL if t=="SCR-…" else (30,44,66)
    txtfill=WHITE if t=="SCR-…" else MUTED
    d.rounded_rectangle((x,486,x+w+pad*2,486+44),radius=10,fill=fill)
    d.text((x+pad-l,486+ (44-(b-tt))/2 - tt),t,font=f,fill=txtfill)
    x+=w+pad*2+12
# footer line
d.text((M,560),"scientificclaims.org",font=font(MENLO,24,1),fill=TEALLT)
foot="CC BY 4.0  ·  operated by BIO"
f2=font(HELV,22,0); l,tt,r,b=d.textbbox((0,0),foot,font=f2)
d.text((W-M-(r-l),562),foot,font=f2,fill=MUTED)
img.save(os.path.join(SITE,"og-image.png"),"PNG")
print("Wrote apple-touch-icon.png (180) and og-image.png (1200x630).")
