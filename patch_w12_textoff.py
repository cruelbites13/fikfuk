# patch_w12_textoff.py - the emergency text-off switch.
# When text is off: other players' confessions, bubbles, letters, whispers, wall entries and tide reveals are hidden,
# and nobody can send new confessions, letters or whispers. The small cat NPCs (policy, about, Patates, Oracle) keep talking.
# Emoji tags, reactions, movement and everything else keep working. A small amber "text paused" shows in the top pill.
# Two ways to turn it on:
#   1) a visitor opens fikfuk.wtf/?text=off  (their own view only, handy for screen recordings)
#   2) YOU edit public/flags.json to {"textOff": true} and run vercel --prod. Every open game picks it up within a minute.
#      To turn text back on, set it to false and deploy again.
# This patch also creates public/flags.json (text on) if it is missing. Needs patch_w10_ui first. Safe to run twice.
import sys, os
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
if "/*_textoff*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_ui10*/" not in src:
    print("ABORT: apply patch_w10_ui.py first. Nothing written."); sys.exit(1)
def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written."); sys.exit(1)
    return text.replace(old, new)

src = swap(src, "const WORLD_CAP=50;",
 '/*_textoff*/let TEXT_OFF=typeof location!=="undefined"&&/[?&]text=off/.test(location.search),_textSet=null;'
 'function _pollFlags(){fetch("/flags.json?t="+Date.now(),{cache:"no-store"}).then(r=>r.ok?r.json():null).then(j=>{if(j&&typeof j.textOff==="boolean"){'
 'TEXT_OFF=j.textOff||/[?&]text=off/.test(location.search);if(_textSet)_textSet(TEXT_OFF);}}).catch(()=>{});}'
 'if(typeof window!=="undefined"&&!window.__fkFlags){window.__fkFlags=setInterval(_pollFlags,60000);_pollFlags();}'
 "const WORLD_CAP=50;", "flag code")
src = swap(src, "const [fade,setFade]=useState(false);",
 "const [fade,setFade]=useState(false);const [textOff,setTextOff]=useState(TEXT_OFF);_textSet=setTextOff;"
 "useEffect(()=>{if(textOff){setShowInput(false);setShowLetterInput(false);}},[textOff]);", "state")
src = swap(src, "if(cat.revealAlpha<=0||!cat.confessions.length)return;", "if(cat.revealAlpha<=0||!cat.confessions.length||(TEXT_OFF&&!cat.isSys))return;", "bubbles")
src = swap(src, "wallConfessions.forEach(wc=>{", "(TEXT_OFF?[]:wallConfessions).forEach(wc=>{", "wall")
src = swap(src, "if(cat._whisperTimer===300&&cat.confessions.length>0){", "if(cat._whisperTimer===300&&cat.confessions.length>0&&!TEXT_OFF){", "whisper send")
src = swap(src, "if(s._whisperMsg){", "if(s._whisperMsg&&TEXT_OFF)s._whisperMsg=null;if(s._whisperMsg){", "whisper show")
src = swap(src, "if(!inputVal.trim()||cooldown>0)return;", "if(!inputVal.trim()||cooldown>0||TEXT_OFF)return;", "confess guard")
src = swap(src, "if(cooldown===0)setShowInput(true);", "if(cooldown===0&&!TEXT_OFF)setShowInput(true);", "confess button")
src = swap(src, "onClick={()=>setShowLetterInput(true)}", "onClick={()=>{if(!TEXT_OFF)setShowLetterInput(true);}}", "letter button")
src = swap(src, "if(Math.abs(csx-tideSx)<60&&cat.confessions.length>0){", "if(Math.abs(csx-tideSx)<60&&cat.confessions.length>0&&!TEXT_OFF){", "tide")
src = swap(src, "confessions:[...cat.confessions],isOwn:cat.isOwn", "confessions:(TEXT_OFF&&!cat.isSys&&!cat.isOwn)?[]:[...cat.confessions],isOwn:cat.isOwn", "cat panel")
src = swap(src, 'if(obj.type==="letter"){', 'if(obj.type==="letter"&&TEXT_OFF)return;if(obj.type==="letter"){', "letters")
src = swap(src, 'textShadow:"0 0 8px currentColor"}}>{worldName}</span>',
 'textShadow:"0 0 8px currentColor"}}>{worldName}</span>{textOff&&<span style={{fontSize:7,color:"#ffbb55"}}>text paused</span>}', "notice")
open(P, "w", encoding="utf-8", newline="").write(src)

pub = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(P))), "public")
fp = os.path.join(pub, "flags.json")
if os.path.isdir(pub) and not os.path.exists(fp):
    open(fp, "w", encoding="utf-8").write('{"textOff": false}\n'); made = " Created public/flags.json."
elif not os.path.isdir(pub):
    made = " NOTE: there is no public folder next to src, so create public/flags.json yourself with {\"textOff\": false}."
else:
    made = " public/flags.json already exists, left untouched."
print("OK: 13 edits applied." + made)
