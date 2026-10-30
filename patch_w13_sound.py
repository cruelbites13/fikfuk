# patch_w13_sound.py - sound: a quiet generated ambient soundscape for each world (nothing to download, made live in the browser),
# a soft chirp sound that gets louder when the chirp is close to you, a pluck when you confess, and a whoosh through portals.
# Malkuth: deep slow hum with sparse low bells. Glass Garden: brighter glassy chimes with an echo. Root Archive: very low, slow, earthy tones.
# Sound starts after your first tap or key press (browsers require that), is kept quiet on purpose, and a small "sound" button
# next to "find me" mutes it; the choice is remembered. Needs patch_w3_portals first. Safe to run twice.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
if "/*_sound*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "function hopTo(" not in src or "const WORLD_CAP=50;" not in src:
    print("ABORT: apply patch_w3_portals.py first. Nothing written."); sys.exit(1)
def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written."); sys.exit(1)
    return text.replace(old, new)
NL = "\r\n" if "\r\n" in src else "\n"
AUDIO = r"""/*_sound*/const FKAudio=(function(){
  let ctx=null,master=null,delay=null,drone=null,timer=null,wid="malkuth",muted=false,started=false;
  try{muted=localStorage.getItem("fikfuk_mute")==="1";}catch(e){}
  const SC={
    malkuth:{root:110,scale:[0,3,5,7,10],wave:"sine",cut:520,gap:[5,9],vol:0.07},
    yesod:{root:196,scale:[0,2,4,7,9],wave:"triangle",cut:1500,gap:[2.4,5],vol:0.075},
    netzach:{root:82.41,scale:[0,2,3,7,8],wave:"sine",cut:400,gap:[6,11],vol:0.08}
  };
  function env(g,t,a,peak,d){g.gain.cancelScheduledValues(t);g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(peak,t+a);g.gain.exponentialRampToValueAtTime(0.0001,t+a+d);}
  function init(){
    if(ctx)return;
    const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;
    ctx=new AC();master=ctx.createGain();master.gain.value=muted?0:0.55;
    const comp=ctx.createDynamicsCompressor();master.connect(comp);comp.connect(ctx.destination);
    delay=ctx.createDelay(1.5);delay.delayTime.value=0.42;const fb=ctx.createGain();fb.gain.value=0.38;const dl=ctx.createBiquadFilter();dl.type="lowpass";dl.frequency.value=1800;
    delay.connect(dl);dl.connect(fb);fb.connect(delay);dl.connect(master);
    const f=ctx.createBiquadFilter();f.type="lowpass";f.frequency.value=SC[wid].cut;f.Q.value=0.7;
    const g=ctx.createGain();g.gain.value=0.05;f.connect(g);g.connect(master);
    const o1=ctx.createOscillator(),o2=ctx.createOscillator(),o3=ctx.createOscillator();
    o1.type=o2.type="sine";o3.type="triangle";o1.frequency.value=SC[wid].root;o2.frequency.value=SC[wid].root*1.5;o2.detune.value=6;o3.frequency.value=SC[wid].root*0.5;
    [o1,o2,o3].forEach(o=>{o.connect(f);o.start();});
    const lfo=ctx.createOscillator(),lg=ctx.createGain();lfo.frequency.value=0.07;lg.gain.value=SC[wid].cut*0.35;lfo.connect(lg);lg.connect(f.frequency);lfo.start();
    drone={o1,o2,o3,f,lg};started=true;next();
  }
  function note(){
    if(!ctx||muted||document.hidden)return;
    const S=SC[wid],t=ctx.currentTime,deg=S.scale[Math.floor(Math.random()*S.scale.length)],oct=Math.random()<0.5?2:4;
    const o=ctx.createOscillator(),g=ctx.createGain();o.type=S.wave;o.frequency.value=S.root*oct*Math.pow(2,deg/12);
    o.connect(g);g.connect(master);g.connect(delay);env(g,t,0.015,S.vol,2.6);o.start(t);o.stop(t+2.8);
  }
  function next(){const S=SC[wid];clearTimeout(timer);timer=setTimeout(()=>{note();next();},(S.gap[0]+Math.random()*(S.gap[1]-S.gap[0]))*1000);}
  function blip(f0,f1,dur,vol,type){
    if(!ctx||muted)return;const t=ctx.currentTime,o=ctx.createOscillator(),g=ctx.createGain();
    o.type=type||"sine";o.frequency.setValueAtTime(f0,t);o.frequency.exponentialRampToValueAtTime(f1,t+dur*0.6);
    o.connect(g);g.connect(master);env(g,t,0.008,vol,dur);o.start(t);o.stop(t+dur+0.1);
  }
  return{
    unlock(){try{init();if(ctx&&ctx.state==="suspended")ctx.resume();}catch(e){}},
    isMuted(){return muted;},
    toggle(){muted=!muted;try{localStorage.setItem("fikfuk_mute",muted?"1":"0");}catch(e){}if(master)master.gain.setTargetAtTime(muted?0:0.55,ctx.currentTime,0.08);},
    setWorld(id){
      if(!SC[id])return;wid=id;if(!drone)return;const S=SC[id],t=ctx.currentTime;
      drone.o1.frequency.setTargetAtTime(S.root,t,0.8);drone.o2.frequency.setTargetAtTime(S.root*1.5,t,0.8);drone.o3.frequency.setTargetAtTime(S.root*0.5,t,0.8);
      drone.f.frequency.setTargetAtTime(S.cut,t,0.8);drone.lg.gain.setTargetAtTime(S.cut*0.35,t,0.8);next();
    },
    chirp(v){blip(900,1500,0.22,0.05+0.12*Math.max(0,Math.min(1,v)),"sine");},
    confess(){blip(330,220,0.5,0.14,"triangle");setTimeout(()=>blip(494,330,0.5,0.08,"sine"),90);},
    portal(){if(!ctx||muted)return;const t=ctx.currentTime,o=ctx.createOscillator(),f=ctx.createBiquadFilter(),g=ctx.createGain();
      o.type="sawtooth";o.frequency.setValueAtTime(120,t);o.frequency.exponentialRampToValueAtTime(900,t+0.7);f.type="lowpass";f.frequency.setValueAtTime(300,t);f.frequency.exponentialRampToValueAtTime(3500,t+0.7);
      o.connect(f);f.connect(g);g.connect(master);env(g,t,0.1,0.11,0.9);o.start(t);o.stop(t+1.1);blip(660,1320,0.5,0.06,"sine");},
    _dbg(){return{ctx:!!ctx,state:ctx&&ctx.state,started,wid,muted};}
  };
})();
if(typeof document!=="undefined"){const _un=()=>FKAudio.unlock();["pointerdown","touchstart","keydown"].forEach(e=>document.addEventListener(e,_un,{once:true,passive:true}));}""".replace("\n", NL)
src = swap(src, "const WORLD_CAP=50;", AUDIO + NL + "const WORLD_CAP=50;", "audio module")
src = swap(src, "WORLD_ID=id;setWorldName(WORLDS[id].name);", "WORLD_ID=id;setWorldName(WORLDS[id].name);FKAudio.setWorld(id);", "world sound on hop")
src = swap(src, 'WORLD_ID="malkuth";setWorldName(WORLDS.malkuth.name);', 'WORLD_ID="malkuth";setWorldName(WORLDS.malkuth.name);FKAudio.setWorld("malkuth");', "world sound on spawn")
src = swap(src, "joinWorld(dest);", "joinWorld(dest);FKAudio.portal();", "portal sound")
src = swap(src, "s._chirps.push({x,y,life:60});",
  "s._chirps.push({x,y,life:60});{const _m=s.cats.find(c=>c.id===s.myId);if(_m){const _d=Math.hypot(_m.x-x,_m.y-y);if(_d<500)FKAudio.chirp(1-_d/500);}}", "chirp sound")
src = swap(src, "addToWall(wallEntry.text);", "addToWall(wallEntry.text);FKAudio.confess();", "confess sound")
src = swap(src, "const [fade,setFade]=useState(false);", "const [fade,setFade]=useState(false);const [muted,setMuted]=useState(FKAudio.isMuted());", "mute state")
BTN = ('<button className="hbtn" onClick={()=>{FKAudio.unlock();FKAudio.toggle();setMuted(FKAudio.isMuted());}} '
 'style={{position:"fixed",top:50,right:100,zIndex:10,fontSize:7,padding:"6px 10px",background:"rgba(8,8,16,0.7)",border:"1px solid rgba(255,255,255,0.18)",color:"rgba(255,255,255,0.55)"}}>'
 '{muted?"sound off":"sound on"}</button>')
src = swap(src, '<div style={{position:"fixed",bottom:0,left:0,right:0,zIndex:20,display:"flex",gap:10,', BTN + '<div style={{position:"fixed",bottom:0,left:0,right:0,zIndex:20,display:"flex",gap:10,', "mute button")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 8 edits applied. Tap once in the game to start sound.")
