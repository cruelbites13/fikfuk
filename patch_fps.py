# patch_fps.py - cap the game tick at 60 runs/second so physics and every frame-counted timer
# behave the same on 60Hz, 90Hz, 120Hz and 144Hz screens. Run from the project folder.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "_fpsGate" in src:
    print("Already patched. Nothing written."); sys.exit(0)

GATE = ("/*_fpsGate*/{const _t=performance.now();s._acc=Math.min((s._acc||0)+(_t-(s._lastT||_t)),100);s._lastT=_t;"
        "if(s._acc<14.67){animRef.current=requestAnimationFrame(tick);return;}s._acc-=16.67;}\n      s.frame++;")
out = swap(src, "s.frame++;", GATE, "tick gate")
open(P, "w", encoding="utf-8", newline="").write(out)
print("OK: 60Hz frame gate added before s.frame++. Test: hold full stick 5s on a 60Hz and a 120Hz screen, distances should match.")
