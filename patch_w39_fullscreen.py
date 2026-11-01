# patch_w39_fullscreen.py - a "full" button for phones and tablets (touch screens only).
# It sits under "find me" in the top-right corner. Tap it to hide the browser bars and fill the screen, tap again to leave.
# Works on Android phones and iPads. iPhone Safari does not allow any web page to go full screen, so on iPhone the button
# shows a short note on how to get the same result (Share, then Add to Home Screen, then open fikfuk from that icon).
# The button is hidden on computers, and hidden when the game is already running as a home-screen app.
# Needs no other patch. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_full*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)

MOD = r'''/*_full*/
function fkFull(){
  try{
    const d=document,el=d.documentElement,on=d.fullscreenElement||d.webkitFullscreenElement;
    if(on){const ex=d.exitFullscreen||d.webkitExitFullscreen;if(ex)ex.call(d);return;}
    const rq=el.requestFullscreen||el.webkitRequestFullscreen;
    if(rq){const r=rq.call(el);if(r&&r.catch)r.catch(()=>{});return;}
    if(d.getElementById("fk-fs-note"))return;
    const n=d.createElement("div");n.id="fk-fs-note";
    n.textContent="iphone safari cannot go full screen. tap share, then add to home screen, then open fikfuk from that icon.";
    n.style.cssText="position:fixed;left:12px;right:12px;bottom:96px;z-index:400;padding:12px;font:8px/1.9 'Press Start 2P',monospace;color:#ffd9a0;background:rgba(8,8,16,0.94);border:1px solid rgba(255,170,68,0.6);border-radius:12px;text-align:center";
    n.onclick=()=>n.remove();d.body.appendChild(n);setTimeout(()=>{try{n.remove();}catch(e){}},8000);
  }catch(e){}
}
let uid=100;'''

CRLF = "\r\n" in src
if CRLF: src = src.replace("\r\n", "\n")
n = 0
def S(old, new, label):
    global src, n
    src = swap(src, old, new, label); n += 1
S("let uid=100;", MOD, "fullscreen function")
S(".hbtn:hover{filter:brightness(1.35);transform:translateY(-1px);}", ".hfull{display:none}@media (pointer:coarse){.hfull{display:block}}@media (display-mode:standalone){.hfull{display:none!important}}.hbtn:hover{filter:brightness(1.35);transform:translateY(-1px);}", "css")
S('<button className="hbtn" onClick={()=>{FKAudio.unlock();FKAudio.toggle();',
  '<button className="hbtn hfull" onClick={fkFull} style={{position:"fixed",top:84,right:16,zIndex:10,fontSize:7,padding:"6px 10px",background:"rgba(8,8,16,0.7)",border:"1px solid rgba(255,255,255,0.18)",color:"rgba(255,255,255,0.55)"}}>full</button><button className="hbtn" onClick={()=>{FKAudio.unlock();FKAudio.toggle();', "button")
if CRLF: src = src.replace("\n", "\r\n")
open(P, "w", encoding="utf-8", newline="").write(src)
print(f"OK: {n} edits applied.")
