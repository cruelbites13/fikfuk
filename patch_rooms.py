# patch_rooms.py - Secret Rooms: use the shared clock (not the device clock) and recompute when the
# epoch changes, instead of once at page load. Run from the project folder: python patch_rooms.py
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written."); sys.exit(1)
    return text.replace(old, new)
if "_srEpoch" in src: print("Already patched. Nothing written."); sys.exit(0)
src = swap(src, "const seed=Math.floor((Date.now()-1700000000000)/(3*60*60*1000));", "const seed=getEpoch();", "seed from shared clock")
src = swap(src, "const SECRET_ROOMS=getSecretRooms();",
  "let _srEpoch=null,_srCache=[];function secretRooms(){const e=getEpoch();if(e!==_srEpoch){_srEpoch=e;_srCache=getSecretRooms();}return _srCache;}", "lazy cache")
src = swap(src, "SECRET_ROOMS.forEach((room,i)=>{", "secretRooms().forEach((room,i)=>{", "draw loop")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 3 edits applied. Check: __fikfuk().epoch is the same on two devices, and rooms sit in the same place on both.")
