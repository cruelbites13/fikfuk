# patch_w29_audio_engine.py - a new ambient sound engine.
# Replaces the old single drone + random beeps with: soft Minecraft-style piano notes (sparse, wandering phrases in a
# different key and scale for each of the six worlds), slow quiet synth pads that change chords every ~17 seconds, and
# a generated reverb. On top of that each world has its own natural sound bed and little random sounds:
#   Malkuth: night wind, crickets, a far owl      Glass Garden: tiny glass tinkles and water drips
#   Root Archive: river, jungle shimmer, birds and parrots by day, frogs and crickets at night, drips
#   Ash Market: crackling fire, embers popping, wind      Sun Court: beach waves, gulls and birds by day
#   Iron Hall: low forge hum, metal clinks, fire crackle, wind
# Thunder is now a real noise-based rumble with a crack and rolling echoes (it still fires with storms). Rain is unchanged.
# The music and nature sounds ride the "music" volume, so "music off" silences them while effects, rain and thunder stay.
# Needs patch_w25_sound_modes.py first (any later patches are fine). All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_eng*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_snd25*/" not in src:
    print("ABORT: apply patch_w25_sound_modes.py first. Nothing written."); sys.exit(1)

ENG = r'''/*_eng*/const ENG=(function(){
  const CFG={
    malkuth:{root:220,sc:[0,3,5,7,10,12,15,17,19],gap:[7,13],sp:1.15,cut:2200,padCut:800,
      pad:[[0,7,10,15],[-2,5,10,14],[-4,3,7,12],[-5,2,7,10]],beds:{wind:0.55},ev:{owl:[0.04,"n"],cricket:[0.45,"n"]}},
    yesod:{root:293.66,sc:[0,2,4,7,9,12,14,16,19],gap:[5,10],sp:0.8,cut:3200,padCut:1100,
      pad:[[0,4,7,11],[-5,2,7,11],[2,5,9,12],[-3,4,7,11]],beds:{wind:0.12},ev:{tinkle:[0.35,0],drip:[0.22,0]}},
    netzach:{root:164.81,sc:[0,2,3,5,7,9,10,12,14],gap:[8,14],sp:1.3,cut:2000,padCut:700,
      pad:[[0,7,10,15],[5,9,12,16],[-2,2,5,10],[3,7,10,14]],beds:{river:0.8,jungle:0.9,wind:0.1},ev:{frog:[0.3,"n"],cricket:[0.5,"n"],bird:[0.3,"d"],parrot:[0.07,"d"],drip:[0.12,0]}},
    hod:{root:196,sc:[0,1,3,5,7,8,10,12,13],gap:[6,11],sp:0.95,cut:2000,padCut:700,
      pad:[[0,7,10,15],[1,5,8,12],[-2,5,10,14],[-4,3,7,12]],beds:{wind:0.4},ev:{crackle:[2.2,0],pop:[0.25,0]}},
    tiferet:{root:261.63,sc:[0,2,4,6,7,9,11,12,14],gap:[5,9],sp:0.9,cut:3000,padCut:1200,
      pad:[[0,4,7,11],[2,6,9,14],[7,11,14,19],[-3,4,7,12]],beds:{beach:1,wind:0.12},ev:{gull:[0.08,"d"],bird:[0.18,"d"],cricket:[0.25,"n"]}},
    gevurah:{root:146.83,sc:[0,1,3,6,7,10,12,13,15],gap:[7,12],sp:1.2,cut:1800,padCut:650,
      pad:[[0,7,10,15],[-2,5,10,14],[1,8,12,15],[-5,2,7,10]],beds:{forge:0.9,wind:0.3},ev:{clink:[0.3,0],crackle:[0.5,0]}}
  };
  const PEAK={wind:0.075,beach:0.11,river:0.085,jungle:0.04,forge:0.03};
  const rnd=(a,b)=>a+Math.random()*(b-a);
  function build(ac,destM0,destFx,getWid,getNight){
    const SR=ac.sampleRate;const destM=ac.createGain();destM.gain.value=1.45;destM.connect(destM0);
    const nb=ac.createBuffer(1,SR*4,SR),nd=nb.getChannelData(0);for(let i=0;i<nd.length;i++)nd[i]=Math.random()*2-1;
    function nsrc(loop){const s=ac.createBufferSource();s.buffer=nb;s.loop=!!loop;return s;}
    function filt(type,f,q){const b=ac.createBiquadFilter();b.type=type;b.frequency.value=f;b.Q.value=q||0.7;return b;}
    function gn(v){const g=ac.createGain();g.gain.value=v;return g;}
    // generated reverb
    const rvIn=gn(1),cv=ac.createConvolver(),rvOut=gn(0.55);
    {const L=Math.floor(SR*2.8),ib=ac.createBuffer(2,L,SR);for(let c=0;c<2;c++){const d=ib.getChannelData(c);for(let i=0;i<L;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/L,3.2);}cv.buffer=ib;}
    rvIn.connect(cv);cv.connect(rvOut);rvOut.connect(destM);
    function out(node,pan,send,dest){
      let n=node;
      if(ac.createStereoPanner&&pan){const p=ac.createStereoPanner();p.pan.value=Math.max(-1,Math.min(1,pan));node.connect(p);n=p;}
      n.connect(dest||destM);
      if(send>0){const s=gn(send);n.connect(s);s.connect(rvIn);}
    }
    function env(g,t,a,peak,d){g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(peak,t+a);g.gain.exponentialRampToValueAtTime(0.0001,t+a+d);}
    // ---------- voices ----------
    function piano(t,f,v,pan,dur,cut){
      dur=dur||3.2;const g=gn(0.0001),lp=filt("lowpass",cut||2600,0.5);
      [["triangle",1,1],["sine",2,0.35],["sine",3.01,0.1]].forEach(p=>{const o=ac.createOscillator();o.type=p[0];o.frequency.value=f*p[1];const og=gn(p[2]);o.connect(og);og.connect(g);o.start(t);o.stop(t+dur+0.1);});
      g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(v,t+0.008);g.gain.exponentialRampToValueAtTime(v*0.35,t+0.4);g.gain.exponentialRampToValueAtTime(0.0001,t+dur);
      g.connect(lp);out(lp,pan,0.55);
    }
    function pad(t,freqs,dur,cut){
      const g=gn(0.0001),lp=filt("lowpass",cut,0.4),v=0.0105;
      freqs.forEach(f=>{[-6,6].forEach(dt=>{const o=ac.createOscillator();o.type="sawtooth";o.frequency.value=f;o.detune.value=dt;o.connect(lp);o.start(t);o.stop(t+dur+0.1);});});
      g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(v,t+6);g.gain.setValueAtTime(v,t+dur-8);g.gain.exponentialRampToValueAtTime(0.0001,t+dur);
      lp.connect(g);out(g,0,0.35);
    }
    // ---------- nature one-shots ----------
    function burst(t,type,f,q,dur,v,pan,send){const s=nsrc(true),b=filt(type,f,q),g=gn(0.0001);s.connect(b);b.connect(g);env(g,t,0.003,v,dur);s.start(t,Math.random()*3);s.stop(t+dur+0.05);out(g,pan,send||0);}
    function tone(t,f0,f1,dur,v,pan,send,type,a){const o=ac.createOscillator(),g=gn(0.0001);o.type=type||"sine";o.frequency.setValueAtTime(f0,t);o.frequency.exponentialRampToValueAtTime(f1,t+dur*0.8);o.connect(g);env(g,t,a||0.01,v,dur);o.start(t);o.stop(t+dur+0.1);out(g,pan,send||0);}
    const EV={
      cricket(t){const f=rnd(4200,4800),pan=rnd(-0.8,0.8),o=ac.createOscillator(),g=gn(0.0001),am=ac.createOscillator(),ag=gn(0.5),vg=gn(0.5);
        o.frequency.value=f;am.type="square";am.frequency.value=rnd(26,34);am.connect(ag);ag.connect(vg.gain);o.connect(vg);vg.connect(g);
        const d=rnd(0.7,1.3);env(g,t,0.05,0.011,d);o.start(t);am.start(t);o.stop(t+d+0.2);am.stop(t+d+0.2);out(g,pan,0);},
      frog(t){const pan=rnd(-0.7,0.7);for(let i=0;i<2;i++){const tt=t+i*0.17,o=ac.createOscillator(),lp=filt("lowpass",900,1),g=gn(0.0001);o.type="sawtooth";o.frequency.setValueAtTime(rnd(150,190),tt);o.frequency.exponentialRampToValueAtTime(rnd(240,300),tt+0.1);o.connect(lp);lp.connect(g);env(g,tt,0.01,0.03,0.12);o.start(tt);o.stop(tt+0.25);out(g,pan,0.15);}},
      bird(t){const pan=rnd(-0.8,0.8),n=2+(Math.random()*3|0),base=rnd(2400,3400);for(let i=0;i<n;i++)tone(t+i*0.13,base*rnd(0.9,1.15),base*rnd(1.1,1.5),0.1,0.018,pan,0.2);},
      parrot(t){const pan=rnd(-0.8,0.8);tone(t,1300,2300,0.18,0.02,pan,0.3,"triangle");tone(t+0.2,2200,1000,0.25,0.02,pan,0.3,"triangle");},
      owl(t){const pan=rnd(-0.6,0.6);tone(t,360,300,0.45,0.03,pan,0.6,"sine",0.08);tone(t+0.6,330,260,0.7,0.03,pan,0.6,"sine",0.08);},
      crackle(t){burst(t,"highpass",rnd(1800,3500),0.7,rnd(0.015,0.05),rnd(0.03,0.07),rnd(-0.7,0.7),0);},
      pop(t){tone(t,rnd(500,800),rnd(120,200),0.09,0.035,rnd(-0.5,0.5),0.15,"triangle");},
      drip(t){const pan=rnd(-0.8,0.8),f=rnd(900,1500);tone(t,f,f*0.42,0.11,0.028,pan,0.7);},
      tinkle(t){const C=CFG.yesod,f=C.root*4*Math.pow(2,C.sc[Math.random()*C.sc.length|0]/12),pan=rnd(-0.8,0.8);tone(t,f,f,1.4,0.016,pan,0.7);tone(t,f*2.76,f*2.76,0.5,0.006,pan,0.5);},
      gull(t){const pan=rnd(-0.8,0.8),s=nsrc(true),b=filt("bandpass",rnd(1500,2000),6),g=gn(0.0001),o=ac.createOscillator();
        o.type="sawtooth";o.frequency.setValueAtTime(1900,t);o.frequency.exponentialRampToValueAtTime(1250,t+0.5);o.connect(b);b.connect(g);env(g,t,0.06,0.012,0.55);o.start(t);o.stop(t+0.7);out(g,pan,0.3);},
      clink(t){const f=rnd(900,1700),pan=rnd(-0.8,0.8);tone(t,f,f,0.6,0.016,pan,0.5,"triangle");tone(t,f*2.76,f*2.76,0.25,0.008,pan,0.4);tone(t,f*5.4,f*5.4,0.12,0.004,pan,0.3);}
    };
    // ---------- persistent beds ----------
    const B={};
    function lfo(f,depth,target){const o=ac.createOscillator(),d=gn(depth);o.frequency.value=f;o.connect(d);d.connect(target);o.start();return o;}
    {
      let g0=gn(0),g1=gn(0.6),s=nsrc(true);
      const bp=filt("bandpass",380,0.6);s.connect(bp);bp.connect(g1);g1.connect(g0);g0.connect(destM);lfo(0.08,0.35,g1.gain);lfo(0.13,0.15,bp.frequency);s.start(0,Math.random()*3);B.wind={g0};
      g0=gn(0);g1=gn(0.2);s=nsrc(true);const lp=filt("lowpass",1100,0.5);s.connect(lp);lp.connect(g1);
      const s2=nsrc(true),hp=filt("highpass",3200,0.4),g2=gn(0.18);s2.connect(hp);hp.connect(g2);g2.connect(g1);g1.connect(g0);g0.connect(destM);s.start(0,Math.random()*3);s2.start(0,Math.random()*3);B.beach={g0,sw:g1};
      g0=gn(0);s=nsrc(true);const b1=filt("bandpass",800,1),b2=filt("bandpass",2400,1.4),b3=filt("highpass",5000,0.5),ga=gn(0.7),gb=gn(0.45),gc=gn(0.15);
      s.connect(b1);b1.connect(ga);ga.connect(g0);s.connect(b2);b2.connect(gb);gb.connect(g0);s.connect(b3);b3.connect(gc);gc.connect(g0);g0.connect(destM);lfo(0.31,0.2,ga.gain);lfo(0.47,0.15,gb.gain);lfo(0.9,60,b2.frequency);s.start(0,Math.random()*3);B.river={g0};
      g0=gn(0);s=nsrc(true);const j1=filt("bandpass",6400,3),jg=gn(0.5),j2=filt("lowpass",500,0.5),jl=gn(0.35);
      s.connect(j1);j1.connect(jg);jg.connect(g0);s.connect(j2);j2.connect(jl);jl.connect(g0);g0.connect(destM);lfo(0.17,0.3,jg.gain);s.start(0,Math.random()*3);B.jungle={g0};
      g0=gn(0);const fl=filt("lowpass",420,0.6),fg=gn(0.3);[[98,"sine",1],[98.7,"sine",0.8],[196,"triangle",0.5]].forEach(p=>{const o=ac.createOscillator();o.type=p[1];o.frequency.value=p[0];const og=gn(p[2]);o.connect(og);og.connect(fl);o.start();});
      fl.connect(fg);fg.connect(g0);s=nsrc(true);const fh=filt("bandpass",2600,0.8),fhg=gn(0.5);s.connect(fh);fh.connect(fhg);fhg.connect(g0);lfo(0.15,0.25,fg.gain);g0.connect(destM);s.start(0,Math.random()*3);B.forge={g0};
    }
    function setBeds(w,t){const C=CFG[w]||CFG.malkuth;Object.keys(B).forEach(k=>{B[k].g0.gain.setTargetAtTime((C.beds[k]||0)*PEAK[k],t,2.5);});}
    // ---------- scheduler ----------
    let melT=0,padT=0,swT=0,padI=0,lastW="",curW="malkuth";const evT={};
    function wid(){const w=getWid();return CFG[w]?w:"malkuth";}
    function sched(now,upTo){
      const w=wid(),C=CFG[w],night=getNight();
      if(w!==lastW){lastW=w;setBeds(w,now);padI=0;if(padT>now+1)padT=now+0.5;if(melT>now+3)melT=now+2;}
      if(melT<now)melT=now+rnd(1,3);
      if(padT<now)padT=now+0.2;
      if(swT<now)swT=now+rnd(0.5,2);
      while(padT<upTo){const ch=C.pad[padI++%C.pad.length];let pr=C.root/2;if(pr<90)pr*=2;pad(padT,ch.map(s=>pr*Math.pow(2,s/12)),22,C.padCut);padT+=17;}
      while(melT<upTo){
        const n=2+(Math.random()*4|0);let idx=Math.random()*C.sc.length|0,t=melT;
        if(Math.random()<0.55)piano(t,(C.root<180?C.root:C.root/2)*Math.pow(2,C.sc[0]/12),0.07,-0.2,5,900);
        for(let i=0;i<n;i++){const f=C.root*Math.pow(2,C.sc[idx]/12);piano(t,f,rnd(0.045,0.085),rnd(-0.5,0.5),3.4,C.cut);t+=C.sp*rnd(0.55,1.25);idx=Math.max(0,Math.min(C.sc.length-1,idx+(Math.random()<0.5?-1:1)*(1+(Math.random()<0.35?1:0))));}
        melT=t+rnd(C.gap[0],C.gap[1]);
      }
      if(C.beds.beach){while(swT<upTo){B.beach.sw.gain.setTargetAtTime(0.85,swT,1.5);B.beach.sw.gain.setTargetAtTime(0.14,swT+3.2,1.8);swT+=rnd(7.5,10.5);}}else swT=upTo;
      Object.keys(C.ev).forEach(k=>{const r=C.ev[k][0],when=C.ev[k][1];
        if(!(k in evT)||evT[k]<now)evT[k]=now+rnd(0,1/r);
        while(evT[k]<upTo){const ok=when===0||(when==="n"?night:!night);if(ok)EV[k](evT[k]);evT[k]+=-Math.log(1-Math.random())/r;}});
    }
    // ---------- thunder (fx bus) ----------
    function thunder(t){
      const far=Math.random()<0.5,dl=far?0.35:0,vs=far?0.6:1;
      burst(t+dl*0.2,"highpass",1400,0.6,0.22,0.22*vs,0,0.25);
      {const s=nsrc(true),lp=filt("lowpass",650,0.7),g=gn(0.0001);lp.frequency.setValueAtTime(650,t+dl);lp.frequency.exponentialRampToValueAtTime(90,t+dl+3.8);s.connect(lp);lp.connect(g);
       g.gain.setValueAtTime(0.0001,t+dl);g.gain.exponentialRampToValueAtTime(0.65*vs,t+dl+0.12);g.gain.exponentialRampToValueAtTime(0.0001,t+dl+4.8);s.start(t+dl,Math.random()*3);s.stop(t+dl+5);g.connect(destFx);}
      [[0.9,0.22],[1.9,0.15],[3.1,0.09]].forEach(r=>{const s=nsrc(true),lp=filt("lowpass",rnd(220,380),0.7),g=gn(0.0001),tt=t+dl+r[0];s.connect(lp);lp.connect(g);
        g.gain.setValueAtTime(0.0001,tt);g.gain.exponentialRampToValueAtTime(r[1]*vs,tt+0.3);g.gain.exponentialRampToValueAtTime(0.0001,tt+2.2);s.start(tt,Math.random()*3);s.stop(tt+2.4);g.connect(destFx);});
      {const o=ac.createOscillator(),g=gn(0.0001);o.frequency.setValueAtTime(58,t+dl);o.frequency.exponentialRampToValueAtTime(30,t+dl+2.6);o.connect(g);
       g.gain.setValueAtTime(0.0001,t+dl);g.gain.exponentialRampToValueAtTime(0.22*vs,t+dl+0.15);g.gain.exponentialRampToValueAtTime(0.0001,t+dl+3.2);o.start(t+dl);o.stop(t+dl+3.3);g.connect(destFx);}
    }
    return{sched,thunder,setWorld(){},cfg:CFG};
  }
  return{build};
})();

'''

crlf = "\r\n" in src
if crlf:
    src = src.replace("\r\n", "\n")
n = 0
src = swap(src, "/*_sound*/const FKAudio=(function(){", ENG + "/*_sound*/const FKAudio=(function(){", "engine module"); n += 1
src = swap(src, "loops=null,lastSec=-1;/*_evsound*/",
  "loops=null,lastSec=-1,E=null,engT=null;/*_evsound*/", "state vars"); n += 1
src = swap(src, "  function note(){",
  "  function engStart(){if(E||!ctx)return;try{E=ENG.build(ctx,mus,master,()=>wid,()=>{try{return isNight();}catch(e){return false;}});engT=setInterval(()=>{try{if(!ctx||muted||musOff||document.hidden||ctx.state!==\"running\")return;E.sched(ctx.currentTime,ctx.currentTime+4);}catch(e){}},1000);if(!muted&&!musOff&&ctx.state===\"running\")E.sched(ctx.currentTime,ctx.currentTime+4);}catch(e){E=null;}}\n  function note(){", "engStart"); n += 1
src = swap(src, "drone={o1,o2,o3,f,lg};started=true;next();",
  "drone={o1,o2,o3,f,lg};started=true;[o1,o2,o3].forEach(o=>{try{o.stop();}catch(e){}});engStart();", "init"); n += 1
src = swap(src, "drone.lg.gain.setTargetAtTime(S.cut*0.35,t,0.8);next();",
  "drone.lg.gain.setTargetAtTime(S.cut*0.35,t,0.8);if(E&&ctx.state===\"running\"&&!muted&&!musOff)E.sched(ctx.currentTime,ctx.currentTime+4);", "setWorld"); n += 1
src = swap(src, 'thunder(){blip(75,28,2.2,0.22,"sine");setTimeout(()=>blip(130,40,1.6,0.12,"triangle"),250);},',
  'thunder(){if(!ctx||muted)return;if(!E)engStart();if(E)E.thunder(ctx.currentTime);else{blip(75,28,2.2,0.22,"sine");}},_eng(){return E;},', "thunder"); n += 1
if crlf:
    src = src.replace("\n", "\r\n")
open(P, "w", encoding="utf-8", newline="").write(src)
print(f"OK: {n} edits applied.")
