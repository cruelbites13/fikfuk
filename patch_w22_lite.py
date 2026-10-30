# patch_w22_lite.py - lighter graphics mode for slower phones.
# A new small button "fx full / fx lite" sits next to the sound button. Lite turns off the heaviest decoration: sky events
# (aurora, rain streaks, meteors, petals; the rain SOUND, thunder and the event label still work), the soft glow halos around
# the beacon, shards and pages, and the dash ghost trail. Gameplay, cats, portals and everything you can interact with are
# identical. The choice is remembered on that device.
# Automatic: if nobody has chosen yet and the game runs under about 34 frames a second for its first 12 seconds, it switches
# itself to lite and says so briefly at the bottom. (A hidden tab restarts the measurement, so switching tabs never trips it.)
# Needs patch_w21_dash.py first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_lite*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_dash*/" not in src:
    print("ABORT: apply patch_w21_dash.py first. Nothing written."); sys.exit(1)

src = swap(src, "let uid=100;", '/*_lite*/let LITE=false;try{LITE=localStorage.getItem("fikfuk_lite")==="1";}catch(e){}\nlet uid=100;', "lite flag")
src = swap(src, "const [recap,setRecap]=useState(null);", "const [recap,setRecap]=useState(null);const [lite,setLite]=useState(LITE);", "lite state")
src = swap(src, 'FKAudio.rain(ev.type==="rain"?ev.a:0);', 'FKAudio.rain(ev.type==="rain"?ev.a:0);if(LITE)return;', "weather off in lite")
src = swap(src, "ctx.fillStyle=gr;ctx.fillRect(sx-rad,cy-rad,rad*2,rad*2);", "if(!LITE){ctx.fillStyle=gr;ctx.fillRect(sx-rad,cy-rad,rad*2,rad*2);}", "beacon glow")
src = swap(src, "[[50,0.07],[34,0.09],[20,0.13],[9,0.22]].forEach(", "(LITE?[[12,0.24]]:[[50,0.07],[34,0.09],[20,0.13],[9,0.22]]).forEach(", "beacon beam")
src = swap(src, "ctx.fillStyle=gr;ctx.fillRect(sx-rad,gy-rad,rad*2,rad*2);", "if(!LITE){ctx.fillStyle=gr;ctx.fillRect(sx-rad,gy-rad,rad*2,rad*2);}", "shard glow")
src = swap(src, "ctx.fillStyle=gr;ctx.fillRect(sx-55,py-65,110,110);", "if(!LITE){ctx.fillStyle=gr;ctx.fillRect(sx-55,py-65,110,110);}", "page glow")
src = swap(src, "const T=s._dashTr;if(!T||!T.length)return;", "const T=s._dashTr;if(!T||!T.length||LITE)return;", "dash trail")
AUTO = ('/*_lite*/{const _n=performance.now(),_a=s._ad||(s._ad={t:_n,r:0,done:false});if(!_a.done){if(document.hidden){_a.t=_n;_a.r=0;}else{_a.r++;const _e=_n-_a.t;'
        'if(_e>12000){_a.done=true;let _c=null;try{_c=localStorage.getItem("fikfuk_lite");}catch(e){}if(!LITE&&_c===null&&_a.r/(_e/1000)<34){LITE=true;setLite(true);try{localStorage.setItem("fikfuk_lite","1");}catch(e){}s._liteNote=300;}}}}}\n      /*_fpsGate*/{')
src = swap(src, "/*_fpsGate*/{", AUTO, "auto detect")
src = swap(src, 'ctx.fillText("flick to dash",W/2,H-110);ctx.restore();}}',
    'ctx.fillText("flick to dash",W/2,H-110);ctx.restore();}'
    'if(s._liteNote>0){s._liteNote--;ctx.save();ctx.font="8px "+ff;ctx.textAlign="center";ctx.fillStyle=`rgba(255,255,255,${Math.min(0.6,s._liteNote/60)})`;ctx.fillText("lite graphics on - tap fx to change",W/2,H-110);ctx.restore();}}', "lite note")
BTN = ('<button className="hbtn" onClick={()=>{LITE=!LITE;setLite(LITE);try{localStorage.setItem("fikfuk_lite",LITE?"1":"0");}catch(e){}}} '
       'style={{position:"fixed",top:50,right:184,zIndex:10,fontSize:7,padding:"6px 10px",background:"rgba(8,8,16,0.7)",border:"1px solid rgba(255,255,255,0.18)",color:"rgba(255,255,255,0.55)"}}>{lite?"fx lite":"fx full"}</button>'
       '<button className="hbtn" onClick={()=>{FKAudio.unlock();FKAudio.toggle();')
src = swap(src, '<button className="hbtn" onClick={()=>{FKAudio.unlock();FKAudio.toggle();', BTN, "toggle button")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 10 edits applied.")
