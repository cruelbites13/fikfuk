# patch_w31_ghostfix.py - fixes the freeze that happened when a player left.
# Cause: when a player leaves, their cat turns into a see-through "ghost" for 2 seconds. The ghost was drawn with a canvas
# filter (grayscale/hue-rotate), and a cat is drawn with dozens of small shapes, so the browser ran that filter on every
# single shape, 60 times a second. One ghost took the game from 60 frames per second down to about 1 (in my test).
# On top of that, the 2 second timer counted frames, not time, so while the game crawled the ghost stayed for a minute or
# more, which kept it crawling. Two changes: (1) no canvas filter, the ghost is just drawn faint with a pale blue glow;
# (2) the ghost timer now uses real time, so it is always gone after 2 seconds, however slow the device. No other patch needed first.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_ghostfix*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
n = 0
src = swap(src, "leavingCat.ghostTimer=120; // 2 seconds at 60fps", "leavingCat.ghostTimer=120;leavingCat.ghostUntil=Date.now()+2000;/*_ghostfix*/", "leave handler"); n += 1
src = swap(src, "cat.ghostTimer=(cat.ghostTimer||0)-1;", "cat.ghostTimer=cat.ghostUntil?Math.max(0,Math.round((cat.ghostUntil-Date.now())/16.67)):(cat.ghostTimer||0)-1;", "ghost timer"); n += 1
src = swap(src, 'ctx.filter="grayscale(1) brightness(2) sepia(0.3) hue-rotate(200deg)";', "", "filter on"); n += 1
src = swap(src, 'ctx.filter="none";', 'ctx.globalCompositeOperation="lighter";ctx.fillStyle="rgba(150,190,255,"+Math.min(0.5,(c.ghostAlpha||0)*0.5).toFixed(3)+")";ctx.beginPath();ctx.ellipse(sx+5.5*P,sy+5*P,24,28,0,0,6.2832);ctx.fill();', "filter off"); n += 1
open(P, "w", encoding="utf-8", newline="").write(src)
print(f"OK: {n} edits applied.")
