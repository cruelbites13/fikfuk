# patch_cid.py - give every player a NEW random id each 3-hour cycle (so cats can't be linked across cycles).
# 1) getClientId() remembers which cycle its id belongs to and makes a fresh id when the cycle changed.
# 2) every time a cat is spawned, the id is re-read, so a tab that lived through a wipe gets the new id
#    before it connects to Ably. All ~30 uses in the game read clientId.current, so nothing else changes.
# Independent of patch_wipe. All-or-nothing, idempotent, safe on Windows (CRLF) files.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "fikfuk_cid_e" in src:
    print("Already patched. Nothing written."); sys.exit(0)

src = swap(src, 'let id = localStorage.getItem("fikfuk_cid");',
           'const _ce=String(getEpoch());let id = localStorage.getItem("fikfuk_cid");'
           'if(id&&localStorage.getItem("fikfuk_cid_e")!==_ce)id=null;', "cycle check")
src = swap(src, 'localStorage.setItem("fikfuk_cid",id); }',
           'localStorage.setItem("fikfuk_cid",id); }localStorage.setItem("fikfuk_cid_e",_ce);', "remember cycle")
src = swap(src, "const myCat=makeCat(ox,oy,palId,name,true,false,null,clientId.current);",
           "clientId.current=getClientId();const myCat=makeCat(ox,oy,palId,name,true,false,null,clientId.current);", "refresh at spawn")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 3 edits applied. Everyone gets one new id on first load after deploy, then a new id each 3-hour cycle.")
