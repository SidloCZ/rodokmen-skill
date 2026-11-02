#!/usr/bin/env python3
# Matriky AHMP (Praha) – stáhne snímek slepením dlaždic Zoomify.
# Použití: ahmp_scan.py XID SCAN OUT.jpg [down] [x0,y0,x1,y1]   (down=0 plné rozlišení, 1 = poloviční…; oblast ve zlomcích)
# XID svazku vypíše ahmp_search.sh. Trvalý odkaz: https://katalog.ahmp.cz/pragapublica/permalink?xid=<XID>&scan=<N>
import glob,shutil,sys,re,math,subprocess,urllib.request,os,tempfile
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); import slusne  # noqa: E402 – brzda proti zablokování archivem (společný limit dotazů, tools/slusne.py)
for _s in (sys.stdout, sys.stderr):   # UTF-8 výstup i na Windows bez -X utf8 (cp1250 neumí třeba „→“)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")
def magick():
    return shutil.which("magick") or next(iter(sorted(glob.glob(r"C:\Program Files\ImageMagick*\magick.exe"))),None) or (os.name!="nt" and shutil.which("convert"))
MAGICK=magick()
xid,scan,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
down=int(sys.argv[4]) if len(sys.argv)>4 else 0
reg=[float(v) for v in sys.argv[5].split(',')] if len(sys.argv)>5 else [0,0,1,1]  # x0,y0,x1,y1 zlomky
UA={'User-Agent':'Mozilla/5.0 genealogy-research'}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
pl=get(f'https://katalog.ahmp.cz/pragapublica/permalink?xid={xid}&scan={scan}').decode('utf-8','replace')
path=re.search(r'zoomifyImgPath = "([^"]+)"',pl).group(1)
props=get(path+'/ImageProperties.xml').decode()
W=int(re.search(r'WIDTH="(\d+)"',props).group(1)); H=int(re.search(r'HEIGHT="(\d+)"',props).group(1)); T=int(re.search(r'TILESIZE="(\d+)"',props).group(1))
tiers=[(W,H)]
while tiers[-1][0]>T or tiers[-1][1]>T:
    w,h=tiers[-1]; tiers.append(((w+1)//2,(h+1)//2))
tiers.reverse()
ntiles=[(math.ceil(w/T),math.ceil(h/T)) for w,h in tiers]
z=len(tiers)-1-down
off=sum(a*b for a,b in ntiles[:z])
cols,rows=ntiles[z]
d=tempfile.mkdtemp()
files=[]
tw,th=tiers[z]
xs=list(range(int(reg[0]*tw)//T, min(cols,math.ceil(reg[2]*tw/T)))); ys=list(range(int(reg[1]*th)//T, min(rows,math.ceil(reg[3]*th/T))))
for y in ys:
    for x in xs:
        idx=off+y*cols+x; g=idx//256
        f=f'{d}/{y:03d}_{x:03d}.jpg'
        open(f,'wb').write(get(f'{path}/TileGroup{g}/{z}-{x}-{y}.jpg')); files.append(f)
if MAGICK:
    rowsf=[]
    nc=len(xs)
    for i,y in enumerate(ys):
        rf=f'{d}/row{y:03d}.png'; subprocess.run([MAGICK,*files[i*nc:(i+1)*nc],'+append',rf],check=True); rowsf.append(rf)
    subprocess.run([MAGICK,*rowsf,'-append','-quality','90',out],check=True)
else:
    from PIL import Image
    grid=[[Image.open(f'{d}/{y:03d}_{x:03d}.jpg').copy() for x in xs] for y in ys]
    cw=sum(im.size[0] for im in grid[0]) if grid else 0
    ch=sum(r[0].size[1] for r in grid if r)
    canvas=Image.new('RGB',(cw,ch))
    yo=0
    for r in grid:
        xo=0
        for im in r:
            canvas.paste(im,(xo,yo)); xo+=im.size[0]
        yo+=r[0].size[1] if r else 0
    os.makedirs(os.path.dirname(os.path.abspath(out)),exist_ok=True)
    canvas.save(out,'JPEG',quality=90)
shutil.rmtree(d, ignore_errors=True)
print(out,tiers[z],'src',path,'permalink',f'https://katalog.ahmp.cz/pragapublica/permalink?xid={xid}&scan={scan}')
