# patch_w26_onboarding.py - a three-step "how to play" card, shown once to each new player.
# After you spawn for the very first time, a small card (under the top buttons on tall screens, above the bottom buttons on short ones) teaches three things, one line each:
#   1/3 drag to walk (and flick to dash)   2/3 tap to chirp   3/3 glowing rings are portals, worlds reset every 3 hours.
# "next" moves on, "skip" closes it at any step, and it never shows again on that device (it remembers). It does not block
# the game: you can keep playing with it open. It is short, quiet, and fits every screen size.
# Needs patch_w16_recap.py (any later patch order is fine). All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_tut26*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_recap*/" not in src:
    print("ABORT: apply patch_w16_recap.py first. Nothing written."); sys.exit(1)

CARD = r'''{phase==="play"&&(<>{/*_tut26*/}
        {tut>0&&(
          <div className="htut" style={{position:"fixed",left:"50%",bottom:84,transform:"translateX(-50%)",width:"calc(100vw - 32px)",maxWidth:300,zIndex:30,boxSizing:"border-box",padding:"14px 16px",background:"rgba(10,10,24,0.9)",border:"1px solid rgba(255,255,255,0.16)",borderRadius:14,backdropFilter:"blur(10px)",WebkitBackdropFilter:"blur(10px)",fontFamily:ff,display:"flex",flexDirection:"column",gap:12}}>
            <div style={{fontSize:7,color:"rgba(255,255,255,0.35)"}}>{tut}/3</div>
            <div style={{fontSize:8,lineHeight:1.9,color:"rgba(255,255,255,0.85)"}}>{["drag anywhere to walk. flick fast to dash.","tap once to chirp. nearby cats reveal what they confessed.","glowing rings are portals to other worlds. every world resets every 3 hours."][tut-1]}</div>
            <div style={{display:"flex",justifyContent:"space-between"}}>
              <button className="hbtn" onClick={()=>{try{localStorage.setItem("fikfuk_tut","1");}catch(e){}setTut(0);}} style={{background:"transparent",border:"none",color:"rgba(255,255,255,0.4)",fontSize:7,padding:"6px 2px"}}>skip</button>
              <button className="hbtn" onClick={()=>{if(tut>=3){try{localStorage.setItem("fikfuk_tut","1");}catch(e){}setTut(0);}else setTut(tut+1);}} style={{background:"rgba(255,50,50,0.14)",border:"1px solid rgba(255,80,80,0.45)",color:"#ff7777",fontSize:7,padding:"7px 12px"}}>{tut>=3?"got it":"next"}</button>
            </div>
          </div>
        )}'''
src = swap(src, ".hbtn:hover{filter:brightness(1.35);transform:translateY(-1px);}", ".htut{top:132px!important;bottom:auto!important}@media (max-height:480px){.htut{top:auto!important;bottom:84px!important;left:16px!important;transform:none!important;width:250px!important}}\n        .hbtn:hover{filter:brightness(1.35);transform:translateY(-1px);}", "css")
src = swap(src, '{phase==="play"&&(<>', CARD, "card")
src = swap(src, "const [lite,setLite]=useState(LITE);", "const [lite,setLite]=useState(LITE);const [tut,setTut]=useState(0);", "state") if "const [lite,setLite]=useState(LITE);" in src else swap(src, "const [recap,setRecap]=useState(null);", "const [recap,setRecap]=useState(null);const [tut,setTut]=useState(0);", "state")
src = swap(src, "recapStart();setRecap(null);", 'recapStart();setRecap(null);try{if(!localStorage.getItem("fikfuk_tut"))setTut(1);}catch(e){}', "show on first spawn")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 5 edits applied.")
