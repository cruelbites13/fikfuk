# patch_w25_sound_modes.py - the sound button now has three states instead of two.
# Tap it to cycle:  "sound on" (music + effects)  ->  "music off" (only effects: chirps, purrs, portals, rain, beacon,
# the countdown...)  ->  "sound off" (silence)  ->  back to "sound on". Your choice is remembered. Players who had muted before
# stay muted. The ambient drone, the sparse chimes and their echo are the "music"; everything else is "effects".
# Same button, same place - no new UI. Needs patch_w14_eventsounds.py (any later patch is fine). All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_snd25*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_evsound*/" not in src:
    print("ABORT: apply patch_w14_eventsounds.py first. Nothing written."); sys.exit(1)

src = swap(src, "muted=false,started=false,", "muted=false,mus=null,musOff=false,started=false,", "vars")
src = swap(src, 'try{muted=localStorage.getItem("fikfuk_mute")==="1";}catch(e){}',
    '/*_snd25*/try{const _m=localStorage.getItem("fikfuk_snd");if(_m==="off")muted=true;else if(_m==="fx")musOff=true;else if(_m!=="all")muted=localStorage.getItem("fikfuk_mute")==="1";}catch(e){}', "read setting")
src = swap(src, "master.connect(comp);comp.connect(ctx.destination);", "master.connect(comp);comp.connect(ctx.destination);mus=ctx.createGain();mus.gain.value=musOff?0:1;mus.connect(master);", "music bus")
src = swap(src, "dl.connect(master);", "dl.connect(mus);", "echo to music bus")
src = swap(src, "g.gain.value=0.05;f.connect(g);g.connect(master);", "g.gain.value=0.05;f.connect(g);g.connect(mus);", "drone to music bus")
src = swap(src, "o.connect(g);g.connect(master);g.connect(delay);", "o.connect(g);g.connect(mus);g.connect(delay);", "chimes to music bus")
src = swap(src, "const S=SC[wid],t=ctx.currentTime,deg=", "if(musOff)return;const S=SC[wid],t=ctx.currentTime,deg=", "skip chimes when off")
src = swap(src, 'toggle(){muted=!muted;try{localStorage.setItem("fikfuk_mute",muted?"1":"0");}catch(e){}if(master)master.gain.setTargetAtTime(muted?0:0.55,ctx.currentTime,0.08);},',
    'toggle(){if(muted){muted=false;musOff=false;}else if(musOff){muted=true;}else{musOff=true;}'
    'try{localStorage.setItem("fikfuk_snd",muted?"off":musOff?"fx":"all");localStorage.setItem("fikfuk_mute",muted?"1":"0");}catch(e){}'
    'const t=ctx?ctx.currentTime:0;if(master)master.gain.setTargetAtTime(muted?0:0.55,t,0.08);if(mus)mus.gain.setTargetAtTime(musOff?0:1,t,0.08);},mode(){return muted?"off":musOff?"fx":"all";},', "cycle")
src = swap(src, "const [lite,setLite]=useState(LITE);", "const [lite,setLite]=useState(LITE);const [sndMode,setSndMode]=useState(FKAudio.mode());", "state")
src = swap(src, "FKAudio.toggle();setMuted(FKAudio.isMuted());", "FKAudio.toggle();setMuted(FKAudio.isMuted());setSndMode(FKAudio.mode());", "click")
src = swap(src, '{muted?"sound off":"sound on"}</button>', '{sndMode==="off"?"sound off":sndMode==="fx"?"music off":"sound on"}</button>', "label")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 11 edits applied.")
