# patch_w40_emotes.py - a "talk" button in the bottom bar. Tap it, pick a small emote (heart, ?, !, zzz, paw, fish)
# and it floats above your cat for everyone nearby to see. No words, so it still works when text is switched off.
# One emote per second at most. Needs patch_w12_textoff.py applied first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written."); sys.exit(1)
    return text.replace(old, new)
if "/*_emote*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_textoff*/" not in src:
    print("ABORT: apply patch_w12_textoff.py first. Nothing written."); sys.exit(1)
nl = "\r\n" if "\r\n" in src else "\n"
t = src
t = swap(t, "  const [showTagPicker, setShowTagPicker] = useState(false);",
 "  const [showTagPicker, setShowTagPicker] = useState(false);" + nl +
 "  const [showTalk, setShowTalk] = useState(false);/*_emote*/" + nl +
 "  const sayEmote=(e)=>{const s=gs.current;const now=Date.now();if(now-(s._emoteAt||0)<1000)return;s._emoteAt=now;const me=s.cats.find(c=>c.id===s.myId);if(!me)return;if(!me._reactions)me._reactions=[];me._reactions.push({emoji:e,life:180,x:Math.random()*30-15,vy:-0.5-Math.random()*0.3});channelRef.current?.publish(\"reaction\",{targetId:s.myId,emoji:e});setShowTalk(false);};", "state")
BTN = '''          <button className="hbtn" onClick={()=>setShowTalk(v=>!v)}
            style={{fontSize:8,background:showTalk?"rgba(120,255,160,0.18)":"transparent",border:"2px solid rgba(120,255,160,0.45)",color:"rgba(150,255,180,0.8)",padding:"10px 13px"}}>
            talk
          </button>
'''.replace("\n", nl)
t = swap(t, '          <button className="hbtn" onClick={()=>setShowTagPicker(true)}', BTN + '          <button className="hbtn" onClick={()=>setShowTagPicker(true)}', "button")
SHEET = '''        {showTalk&&!showTagPicker&&(
          <div style={{position:"fixed",left:"50%",bottom:76,transform:"translateX(-50%)",zIndex:25,display:"flex",gap:6,padding:"8px 10px",background:"rgba(8,8,16,0.95)",border:"1px solid rgba(120,255,160,0.45)",borderRadius:6,maxWidth:"calc(100vw - 16px)",boxSizing:"border-box"}}>
            {["❤️","❓","❗","💤","🐾","🐟"].map(e=>(
              <button key={e} onClick={()=>sayEmote(e)} style={{fontSize:20,background:"rgba(255,255,255,0.06)",border:"1px solid rgba(120,255,160,0.25)",padding:"6px",cursor:"pointer",borderRadius:4}}>{e}</button>
            ))}
          </div>
        )}
'''.replace("\n", nl)
t = swap(t, "        {showTagPicker&&(", SHEET + "        {showTagPicker&&(", "sheet")
t = swap(t, "@media (max-width:350px){.hlogo{display:none}", "@media (max-width:350px){.hbar{gap:4px!important;padding:12px 4px 18px!important}.hbar .hbtn{padding:9px 6px!important}.hlogo{display:none}", "css")
open(P, "w", encoding="utf-8", newline="").write(t)
print("OK: 5 edits applied.")
