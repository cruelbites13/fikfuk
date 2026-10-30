# patch_debug.py - adds a tiny on-screen readout when the URL has ?debug, so you can prove the
# 60Hz frame gate on a phone with no console: it shows renders/s and game ticks/s.
# Needs patch_fps.py applied first. Run from the project folder: python patch_debug.py
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written."); sys.exit(1)
    return text.replace(old, new)
if "__fikfukHz" in src: print("Already patched. Nothing written."); sys.exit(0)
if "_fpsGate" not in src: print("ABORT: run patch_fps.py first. Nothing written."); sys.exit(1)

HELPER = ('const _k=window.__fk=window.__fk||{r:0,t:0,t0:performance.now()};_k.r++;'
 'if(!window.__fikfukHz){window.__fikfukHz=()=>{const dt=(performance.now()-_k.t0)/1000,o={renders:+(_k.r/dt).toFixed(1),ticks:+(_k.t/dt).toFixed(1)};_k.r=0;_k.t=0;_k.t0=performance.now();return o;};'
 'if(/[?&]debug/.test(location.search)){const d=document.createElement("div");d.style.cssText="position:fixed;left:6px;bottom:6px;z-index:99;font:11px monospace;color:#6f6;background:#000a;padding:2px 5px;pointer-events:none";document.body.appendChild(d);'
 'setInterval(()=>{const o=window.__fikfukHz();d.textContent="render "+o.renders+"/s  tick "+o.ticks+"/s";},1000);}}')
src = swap(src, "/*_fpsGate*/{const _t=performance.now();", "/*_fpsGate*/{" + HELPER + "const _t=performance.now();", "counter")
src = swap(src, "s._acc-=16.67;}", "s._acc-=16.67;_k.t++;}", "tick count")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK. Open the game with ?debug on the end of the address, e.g. fikfuk.wtf/?debug")
