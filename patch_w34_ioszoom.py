# patch_w34_ioszoom.py - fixes the iPhone zoom that sticks after typing a name.
# Cause: iPhone Safari automatically zooms into any text box whose letters are smaller than 16px when you tap it (to
# "help" you read), and it often stays zoomed after the keyboard closes. All three text boxes in the game (cat name,
# confession, letter) use 9px letters, so every one of them triggers it. Fix, in two parts: (1) the page is told it may
# not be zoomed past 100%, which stops iPhone from zooming into text boxes in the first place; (2) when any text box
# loses focus, the page snaps back to normal zoom and scroll position, which also rescues a page that is already stuck.
# Pinch-zooming the game is turned off, which is what you want for a game anyway. Needs no other patch. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_zoomfix*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
MOD = r'''/*_zoomfix*/
if(typeof document!=="undefined"){try{
  const _vp="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no";
  const _setVp=()=>{let m=document.querySelector('meta[name="viewport"]');if(!m){m=document.createElement("meta");m.setAttribute("name","viewport");document.head.appendChild(m);}m.setAttribute("content",_vp);};
  _setVp();
  document.addEventListener("focusout",(e)=>{const t=e.target&&e.target.tagName;if(t!=="INPUT"&&t!=="TEXTAREA")return;
    setTimeout(()=>{try{const m=document.querySelector('meta[name="viewport"]');if(m){m.setAttribute("content","width=device-width, initial-scale=1");}}catch(x){}window.scrollTo(0,0);setTimeout(_setVp,120);},60);});
}catch(e){}}
let uid=100;'''
crlf = "\r\n" in src
if crlf: src = src.replace("\r\n", "\n")
src = swap(src, "let uid=100;", MOD, "zoom fix")
if crlf: src = src.replace("\n", "\r\n")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 1 edits applied.")
