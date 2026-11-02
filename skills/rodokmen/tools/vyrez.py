#!/usr/bin/env python3
"""Výřez zápisu ze staženého snímku stránky (z jakéhokoli portálu).

Použití:
  vyrez.py <snimek.jpg> <klic> [x0,y0,x1,y1]
      x0..y1 = oblast zápisu jako zlomky šířky a výšky stránky (0..1); bez nich se bere celá stránka.
      Uloží zdroje/<klic>.jpg (plné rozlišení) a vyrezy/<klic>.jpg (zmenšeno na max. 1800 px pro web).

Výřez dělejte velkoryse: celý zápis včetně hlavičky sloupců, okrajových poznámek a podpisů.
Potřebuje ImageMagick (příkaz `magick`).
"""
import glob, os, shutil, subprocess, sys
for _s in (sys.stdout, sys.stderr):   # UTF-8 výstup i na Windows bez -X utf8 (cp1250 neumí třeba „→“)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def magick():
    """Cesta k ImageMagicku; není-li nainstalován, vrátí None a použije se Python Pillow (PIL)."""
    return (shutil.which("magick") or next(iter(sorted(glob.glob(r"C:\Program Files\ImageMagick*\magick.exe"))), None)
            or (os.name != "nt" and shutil.which("convert")))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, key = sys.argv[1], sys.argv[2]
    MAGICK = magick()
    full = os.path.join(ROOT, "zdroje", key + ".jpg")
    small = os.path.join(ROOT, "vyrezy", key + ".jpg")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    os.makedirs(os.path.dirname(small), exist_ok=True)
    crop_box = None
    if len(sys.argv) > 3:
        x0, y0, x1, y1 = (float(v) for v in sys.argv[3].split(","))
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):   # pixely by ImageMagick jen varoval a uložil celou stránku
            sys.exit(f"Oblast {sys.argv[3]} musí být zlomky 0..1 (x0 < x1, y0 < y1), ne pixely – "
                     "např. 0.1,0.25,0.9,0.6 = od 10 % do 90 % šířky a od 25 % do 60 % výšky.")
        crop_box = (x0, y0, x1, y1)
    if MAGICK:
        cmd = [MAGICK, src, "-auto-orient"]
        if crop_box:
            x0, y0, x1, y1 = crop_box
            w, h = (int(v) for v in subprocess.run([MAGICK, src + "[0]", "-auto-orient", "-format", "%w %h", "info:"],
                                                    capture_output=True, text=True, check=True).stdout.split())
            cmd += ["-crop", f"{round((x1 - x0) * w)}x{round((y1 - y0) * h)}+{round(x0 * w)}+{round(y0 * h)}", "+repage"]
        subprocess.run(cmd + ["+profile", "!icc,*", "+set", "comment", "-quality", "90", full], check=True)
        subprocess.run([MAGICK, full, "-resize", "1800x1800>", "-quality", "85", small], check=True)
    else:
        try:
            from PIL import Image, ImageOps
        except ImportError:
            sys.exit("Chybí ImageMagick (příkaz magick) i knihovna Pillow (PIL). Nainstaluj Pillow (`pip install Pillow`) nebo ImageMagick.")
        with Image.open(src) as im:
            icc = im.info.get("icc_profile")
            im = ImageOps.exif_transpose(im)
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            if crop_box:
                x0, y0, x1, y1 = crop_box
                w, h = im.size
                im = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
            save_kw = {"quality": 90}
            if icc:
                save_kw["icc_profile"] = icc
            im.save(full, "JPEG", **save_kw)
            im_small = im.copy()
            im_small.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
            save_kw["quality"] = 85
            im_small.save(small, "JPEG", **save_kw)
    print("uloženo:", full, "a", small)


if __name__ == "__main__":
    main()
