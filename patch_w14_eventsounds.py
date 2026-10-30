# patch_w14_eventsounds.py - sounds for what happens in the world, on top of the ambient sound patch:
# - Diablo: a low growl that swells as you walk toward him, and a thud-and-crack when he is hit
# - black hole: a deep rumble that rises and drops in pitch as you near it, and a collapsing boom when it is closed
# - UFO: a faint hum when you are close
# - purr circles: a soft purr when you are sitting in one
# - mice: a squeak when you catch one; Patates: a warm two-note chime when he is fed
# - reset countdown: a slow heartbeat for the last minute, then ten rising ticks, so the wipe is felt
# Obeys the sound button. Needs patch_w13_sound first. Safe to run twice.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
if "/*_evsound*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_sound*/" not in src:
    print("ABORT: apply patch_w13_sound.py first. Nothing written."); sys.exit(1)
def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written."); sys.exit(1)
    return text.replace(old, new)
NL = "\r\n" if "\r\n" in src else "\n"
EV = r"""    near(v){
      if(!ctx||muted)return;
      if(!loops){loops={};
        const mk=(type,fa,ftype,fq)=>{const g=ctx.createGain();g.gain.value=0;const f=ctx.createBiquadFilter();f.type=ftype;f.frequency.value=fq;f.connect(g);g.connect(master);
          const os=fa.map(fr=>{const o=ctx.createOscillator();o.type=type;o.frequency.value=fr;o.connect(f);o.start();return o;});return{g,os,f};};
        loops.dia=mk("sawtooth",[55,55.7,82,110,165],"lowpass",300);
        loops.bh=mk("sine",[38,40.5,57,76,114],"lowpass",420);
        loops.ufo=mk("sine",[220,223.5,330],"lowpass",900);
        const pg=ctx.createGain();pg.gain.value=0;const po=ctx.createOscillator();po.type="triangle";po.frequency.value=110;
        const am=ctx.createGain();am.gain.value=0.5;const lf=ctx.createOscillator();lf.frequency.value=24;const lg=ctx.createGain();lg.gain.value=0.5;
        lf.connect(lg);lg.connect(am.gain);po.connect(am);am.connect(pg);pg.connect(master);po.start();lf.start();{const p2=ctx.createOscillator();p2.type="sine";p2.frequency.value=220;p2.connect(am);p2.start();}loops.purr={g:pg};
      }
      const t=ctx.currentTime,c=(x)=>Math.max(0,Math.min(1,x||0));
      loops.dia.g.gain.setTargetAtTime(0.10*c(v.dia)*c(v.dia),t,0.3);
      loops.bh.g.gain.setTargetAtTime(0.13*c(v.bh),t,0.3);loops.bh.os[0].frequency.setTargetAtTime(38-10*c(v.bh),t,0.3);loops.bh.os[3].frequency.setTargetAtTime(76-20*c(v.bh),t,0.3);
      loops.ufo.g.gain.setTargetAtTime(0.035*c(v.ufo),t,0.3);
      loops.purr.g.gain.setTargetAtTime(0.11*c(v.purr),t,0.5);
    },
    hit(hp,remote){const v=remote?0.06:0.14;blip(170,55,0.3,v,"sawtooth");blip(1300,380,0.09,v*0.5,"square");},
    squeak(){blip(1800,2600,0.09,0.08,"square");setTimeout(()=>blip(2300,1500,0.08,0.06,"square"),90);},
    feed(mine){const v=mine?0.12:0.05;blip(784,784,0.7,v,"sine");setTimeout(()=>blip(1175,1175,0.8,v*0.8,"sine"),130);},
    collapse(){blip(320,28,1.6,0.2,"sine");setTimeout(()=>blip(90,24,1.2,0.12,"triangle"),200);},
    countdown(ms){
      if(!ctx||muted||document.hidden||ms>=60000||ms<=0){return;}
      const sec=Math.ceil(ms/1000);if(sec===lastSec)return;lastSec=sec;
      if(sec<=10)blip(280+(10-sec)*55,280+(10-sec)*55+20,0.18,0.07+0.012*(10-sec),"sine");
      else if(sec%2===0){blip(95,52,0.2,0.16,"sine");blip(190,100,0.08,0.06,"triangle");setTimeout(()=>{blip(88,48,0.18,0.12,"sine");blip(176,92,0.07,0.05,"triangle");},170);}
    },""".replace("\n", NL)
src = swap(src, "let ctx=null,master=null,delay=null,drone=null,timer=null,wid=\"malkuth\",muted=false,started=false;",
                "let ctx=null,master=null,delay=null,drone=null,timer=null,wid=\"malkuth\",muted=false,started=false,loops=null,lastSec=-1;/*_evsound*/", "audio state")
src = swap(src, "    _dbg(){return{", EV + "    _dbg(){return{", "audio methods")
src = swap(src, "myCat._boostTimer=300;", "myCat._boostTimer=300;FKAudio.squeak();", "mouse squeak")
src = swap(src, "const line=FEED_LINES[Math.floor(Math.random()*FEED_LINES.length)];", "const line=FEED_LINES[Math.floor(Math.random()*FEED_LINES.length)];FKAudio.feed(mine);", "feed chime")
src = swap(src, 'channelRef.current?.publish("dia_hit",{id:obj.id,hp:obj.hp});', 'FKAudio.hit(obj.hp);channelRef.current?.publish("dia_hit",{id:obj.id,hp:obj.hp});', "diablo hit")
src = swap(src, "if(o&&msg.data.hp>0&&msg.data.hp<o.hp)o.hp=msg.data.hp;", "if(o&&msg.data.hp>0&&msg.data.hp<o.hp){o.hp=msg.data.hp;FKAudio.hit(msg.data.hp,true);}", "remote diablo hit")
src = swap(src, "if(obj.hp<=0){ s._bhClosedSlot=obj.slot; toRemove.add(obj.id); }", "if(obj.hp<=0){ s._bhClosedSlot=obj.slot; toRemove.add(obj.id); FKAudio.collapse(); }", "black hole closed")
src = swap(src, "const msLeft=nextResetMs();",
 "if(s.frame%8===0){const _me=s.cats.find(c=>c.id===s.myId);if(_me){const _n={dia:0,bh:0,ufo:0,purr:_me._purr?1:0};"
 "s.worldObjs.forEach(o=>{if(o.type!==\"diablo\"&&o.type!==\"blackhole\"&&o.type!==\"ufo\")return;const d=Math.hypot(_me.x-o.x,_me.y-o.y);"
 "if(o.type===\"diablo\")_n.dia=Math.max(_n.dia,1-d/700);else if(o.type===\"blackhole\")_n.bh=Math.max(_n.bh,1-d/((o.pullRadius||300)+250));else _n.ufo=Math.max(_n.ufo,1-d/450);});FKAudio.near(_n);}}"
 "FKAudio.countdown(nextResetMs());const msLeft=nextResetMs();", "per-frame sound update")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 8 edits applied (Diablo, black hole, UFO, purr, mouse, Patates, countdown sounds).")
