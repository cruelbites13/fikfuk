# patch_probe.py - richer __fikfuk() for the two-device test: epoch, time left, clock offset, online count,
# Black Hole slot, Diablo position/hp, secret room positions. Run: python patch_probe.py
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
OLD = "window.__fikfuk=()=>({epoch:getEpoch(),offsetMs:Math.round(clockOffset),initial:s._initObjs});"
if src.count(OLD) != 1:
    print(f"ABORT: expected exactly 1 match, found {src.count(OLD)}. Nothing written."); sys.exit(1)
NEW = ('window.__fikfuk=()=>{const _d=s.worldObjs.find(o=>o.type==="diablo"),_b=s.worldObjs.find(o=>o.type==="blackhole");'
  'return{epoch:getEpoch(),msLeft:Math.round(nextResetMs()),offsetMs:Math.round(clockOffset),initial:s._initObjs,'
  'online:s.cats.filter(c=>!c.isSys&&!c.isGhost).length,dead:Array.from(s._dead||[]).length,bhSlot:_b?_b.slot:null,'
  'diablo:_d?{x:Math.round(_d.x),y:Math.round(_d.y),hp:_d.hp}:null,'
  'rooms:(typeof secretRooms==="function"?secretRooms():[]).map(r=>[Math.round(r.x),Math.round(r.y)])};};')
open(P, "w", encoding="utf-8", newline="").write(src.replace(OLD, NEW))
print("OK. In the browser console run __fikfuk() on both devices and compare epoch, msLeft (within ~2s), diablo, rooms.")
