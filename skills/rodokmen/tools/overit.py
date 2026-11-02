#!/usr/bin/env python3
# Ověření čtení (např. po pomocníkovi): výřez zápisu rozdělený na dvě poloviny 1900 px. Použití: overit.py <snímek.jpg> x0,y0,x1,y1 <prefix> [v]  (v = dělit vodorovně)
import glob,os,shutil,sys,subprocess
for _s in (sys.stdout, sys.stderr):   # UTF-8 výstup i na Windows bez -X utf8 (cp1250 neumí třeba „→“)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")
def magick():
    return shutil.which("magick") or next(iter(sorted(glob.glob(r"C:\Program Files\ImageMagick*\magick.exe"))),None) or (os.name!="nt" and shutil.which("convert"))
MAGICK=magick()
f,box,pre=sys.argv[1:4]; mode=sys.argv[4] if len(sys.argv)>4 else 'h'
x0,y0,x1,y1=map(float,box.split(','))
if not (0<=x0<x1<=1 and 0<=y0<y1<=1): sys.exit(f'Oblast {box} musí být zlomky 0..1 (x0 < x1, y0 < y1), ne pixely.')
if mode=='v': ym=(y0+y1)/2; parts=[(x0,y0,x1,ym+0.02),(x0,ym-0.02,x1,y1)]
else: xm=(x0+x1)/2; parts=[(x0,y0,xm+0.02,y1),(xm-0.02,y0,x1,y1)]
if MAGICK:
    W,H=map(int,subprocess.run([MAGICK,f+'[0]','-format','%w %h','info:'],capture_output=True,text=True).stdout.split())
    for i,(a,b,c,d) in enumerate(parts):
        o=f'{pre}_{i}.jpg'; subprocess.run([MAGICK,f,'-crop','%dx%d+%d+%d'%((c-a)*W,(d-b)*H,a*W,b*H),'+repage','-resize','1900x',o]); print(o)
else:
    from PIL import Image
    with Image.open(f) as im:
        if im.mode not in ("RGB", "L"): im = im.convert("RGB")
        W,H=im.size
        for i,(a,b,c,d) in enumerate(parts):
            o=f'{pre}_{i}.jpg'
            crop_im=im.crop((round(a*W),round(b*H),round(c*W),round(d*H)))
            nw,nh=1900,max(1,round(crop_im.size[1]*1900/max(1,crop_im.size[0])))
            crop_im.resize((nw,nh),Image.Resampling.LANCZOS).save(o,"JPEG",quality=90)
            print(o)
