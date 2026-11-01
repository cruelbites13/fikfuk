# patch_w37_bugreport.py - policy tweak: no mention of the hosting services, and a bug-report line instead.
# Replaces the policy point about hosts and page-speed stats with: found a glitch or bug? mention @cruelbites on X with a
# screenshot or, even better, a video. The handle is a tappable link to x.com/cruelbites. Needs patch_w36_booth_policy.py first.
# All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
if "/*_bugline*/" in src or "found a glitch or bug?" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_booth*/" not in src:
    print("ABORT: apply patch_w36_booth_policy.py first. Nothing written."); sys.exit(1)
OLD = '<div style={{fontSize:7,color:"rgba(200,200,255,0.85)",lineHeight:2}}>like any website, our hosts (vercel and ably) see basic technical info such as your ip address, and we use anonymous page-speed stats.</div>'
NEW = ('<div style={{fontSize:7,color:"rgba(200,200,255,0.85)",lineHeight:2}}>found a glitch or bug? mention <a href="https://x.com/cruelbites" target="_blank" rel="noopener noreferrer" style={{color:"#9cc4ff"}}>@cruelbites</a> on x with a screenshot or, even better, a video, and it gets fixed.</div>')
n = src.count(OLD)
if n != 1:
    print(f"ABORT policy text: expected exactly 1 match, found {n}. Nothing written."); sys.exit(1)
src = src.replace(OLD, NEW)
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 1 edits applied.")
