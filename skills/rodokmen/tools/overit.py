#!/usr/bin/env python3
"""Ověření čtení zápisu nebo rozřezání hustého rejstříku (indexu) na čitelné pásy.

Použití:
  overit.py <snímek.jpg> x0,y0,x1,y1 <prefix> [v]
      Výřez zápisu rozdělený na dvě poloviny (šířka 1900 px; v = dělit vodorovně).
  overit.py <snímek.jpg> rejstrik <prefix> [pasy=5]
      Rozřeže celou stránku rejstříku na N vodorovných pásů s 10% překryvem (šířka 2000 px),
      aby žádný řádek nebyl přeříznutý vejpůl a AI nepřehlédla hledané jméno.
"""
import glob, os, shutil, subprocess, sys
for _s in (sys.stdout, sys.stderr):   # UTF-8 výstup i na Windows bez -X utf8 (cp1250 neumí třeba „→“)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")


def magick():
    return (shutil.which("magick") or next(iter(sorted(glob.glob(r"C:\Program Files\ImageMagick*\magick.exe"))), None)
            or (os.name != "nt" and shutil.which("convert")))


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    MAGICK = magick()
    f, box, pre = sys.argv[1:4]
    if f == "rejstrik":
        f, box = box, "rejstrik"
    os.makedirs(os.path.dirname(os.path.abspath(pre)), exist_ok=True)
    if box == "rejstrik":
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        step = 1.0 / n
        ov = 0.05   # 5 % nahoře i dole = 10 % překryv mezi sousedními pásy
        parts = [(0.0, max(0.0, i * step - ov), 1.0, min(1.0, (i + 1) * step + ov)) for i in range(n)]
        target_w = 2000
    else:
        mode = sys.argv[4] if len(sys.argv) > 4 else "h"
        x0, y0, x1, y1 = map(float, box.split(","))
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
            sys.exit(f"Oblast {box} musí být zlomky 0..1 (x0 < x1, y0 < y1), ne pixely.")
        if mode == "v":
            ym = (y0 + y1) / 2
            parts = [(x0, y0, x1, min(1.0, ym + 0.02)), (x0, max(0.0, ym - 0.02), x1, y1)]
        else:
            xm = (x0 + x1) / 2
            parts = [(x0, y0, min(1.0, xm + 0.02), y1), (max(0.0, xm - 0.02), y0, x1, y1)]
        target_w = 1900

    if MAGICK:
        W, H = map(int, subprocess.run([MAGICK, f + "[0]", "-format", "%w %h", "info:"],
                                       capture_output=True, text=True, check=True).stdout.split())
        for i, (a, b, c, d) in enumerate(parts):
            o = f"{pre}_{i}.jpg"
            subprocess.run([MAGICK, f, "-crop", "%dx%d+%d+%d" % (round((c - a) * W), round((d - b) * H), round(a * W), round(b * H)),
                            "+repage", "-resize", f"{target_w}x", "-quality", "90", o], check=True)
            print(o)
    else:
        from PIL import Image
        with Image.open(f) as im:
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            W, H = im.size
            for i, (a, b, c, d) in enumerate(parts):
                o = f"{pre}_{i}.jpg"
                crop_im = im.crop((round(a * W), round(b * H), round(c * W), round(d * H)))
                nw, nh = target_w, max(1, round(crop_im.size[1] * target_w / max(1, crop_im.size[0])))
                crop_im.resize((nw, nh), Image.Resampling.LANCZOS).save(o, "JPEG", quality=90)
                print(o)


if __name__ == "__main__":
    main()
