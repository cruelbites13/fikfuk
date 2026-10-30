# patch_rate.py - adaptive move send rate. Few players: keep the smooth 4 sends/s. Crowded: slow down,
# because message load grows with the square of players. <=8 players: 250ms, <=16: 400ms, more: 600ms.
# For testing, type __fikfukGap=600 in the console to force a gap (400 or 600), and __fikfukGap=0 to go back.
# Run from the project folder: python patch_rate.py
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
OLD = "if(now-moveThrottle.current>250){"
if "_moveGap" in src: print("Already patched. Nothing written."); sys.exit(0)
if src.count(OLD) != 1:
    print(f"ABORT: expected exactly 1 match, found {src.count(OLD)}. Nothing written."); sys.exit(1)
NEW = ("if(s.frame%60===0){const _n=s.cats.filter(c=>!c.isSys&&!c.isGhost).length;s._moveGap=window.__fikfukGap||(_n<=8?250:_n<=16?400:600);}"
       "if(now-moveThrottle.current>(s._moveGap||250)){")
open(P, "w", encoding="utf-8", newline="").write(src.replace(OLD, NEW))
print("OK. Test: hold the stick 10s and compare __fikfukPub() before/after: ~40 normally, ~25 with __fikfukGap=400, ~17 with __fikfukGap=600.")
