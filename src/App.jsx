import { useState, useEffect, useRef, useCallback } from "react";
import * as Ably from "ably";
import { SpeedInsights } from "@vercel/speed-insights/react";

const ABLY_KEY  = import.meta.env.VITE_ABLY_KEY;
const CHANNEL   = "fikfuk-main";let WORLD_ID="malkuth";function channelFor(id){return id==="malkuth"?CHANNEL:"fikfuk:"+id;}const WORLDS={malkuth:{name:"Malkuth Gate",sky:["#0B0B18","#1A1A3A"]},yesod:{name:"Glass Garden",sky:["#2A2440","#B8A8E0"],chirpRadius:1.5},netzach:{name:"Root Archive",sky:["#0D2318","#2E5A3A"],purrRadius:170},hod:{name:"Ash Market",sky:["#2A0F08","#6A2A14"]},tiferet:{name:"Sun Court",sky:["#2B1F08","#8A6A1C"]},gevurah:{name:"Iron Hall",sky:["#1A0608","#4A0F18"]}};/*_eng*/const ENG=(function(){
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

/*_sound*/const FKAudio=(function(){
  let ctx=null,master=null,delay=null,drone=null,timer=null,wid="malkuth",muted=false,mus=null,musOff=false,started=false,loops=null,lastSec=-1,E=null,engT=null;/*_evsound*/
  /*_snd25*/try{const _m=localStorage.getItem("fikfuk_snd");if(_m==="off")muted=true;else if(_m==="fx")musOff=true;else if(_m!=="all")muted=localStorage.getItem("fikfuk_mute")==="1";}catch(e){}
  const SC={
    malkuth:{root:110,scale:[0,3,5,7,10],wave:"sine",cut:520,gap:[5,9],vol:0.07},
    yesod:{root:196,scale:[0,2,4,7,9],wave:"triangle",cut:1500,gap:[2.4,5],vol:0.075},
    netzach:{root:82.41,scale:[0,2,3,7,8],wave:"sine",cut:400,gap:[6,11],vol:0.08},
    hod:{root:98,scale:[0,1,5,7,8],wave:"triangle",cut:700,gap:[3,7],vol:0.075},
    tiferet:{root:130.81,scale:[0,4,7,11,14],wave:"sine",cut:1100,gap:[3,6],vol:0.075},
    gevurah:{root:73.42,scale:[0,1,3,6,7],wave:"triangle",cut:520,gap:[3,6],vol:0.07}
  };
  function env(g,t,a,peak,d){g.gain.cancelScheduledValues(t);g.gain.setValueAtTime(0.0001,t);g.gain.exponentialRampToValueAtTime(peak,t+a);g.gain.exponentialRampToValueAtTime(0.0001,t+a+d);}
  function init(){
    if(ctx)return;
    const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;
    ctx=new AC();master=ctx.createGain();master.gain.value=muted?0:0.55;
    const comp=ctx.createDynamicsCompressor();master.connect(comp);comp.connect(ctx.destination);mus=ctx.createGain();mus.gain.value=musOff?0:1;mus.connect(master);
    delay=ctx.createDelay(1.5);delay.delayTime.value=0.42;const fb=ctx.createGain();fb.gain.value=0.38;const dl=ctx.createBiquadFilter();dl.type="lowpass";dl.frequency.value=1800;
    delay.connect(dl);dl.connect(fb);fb.connect(delay);dl.connect(mus);
    const f=ctx.createBiquadFilter();f.type="lowpass";f.frequency.value=SC[wid].cut;f.Q.value=0.7;
    const g=ctx.createGain();g.gain.value=0.05;f.connect(g);g.connect(mus);
    const o1=ctx.createOscillator(),o2=ctx.createOscillator(),o3=ctx.createOscillator();
    o1.type=o2.type="sine";o3.type="triangle";o1.frequency.value=SC[wid].root;o2.frequency.value=SC[wid].root*1.5;o2.detune.value=6;o3.frequency.value=SC[wid].root*0.5;
    [o1,o2,o3].forEach(o=>{o.connect(f);o.start();});
    const lfo=ctx.createOscillator(),lg=ctx.createGain();lfo.frequency.value=0.07;lg.gain.value=SC[wid].cut*0.35;lfo.connect(lg);lg.connect(f.frequency);lfo.start();
    drone={o1,o2,o3,f,lg};started=true;[o1,o2,o3].forEach(o=>{try{o.stop();}catch(e){}});engStart();
  }
  function engStart(){if(E||!ctx)return;try{E=ENG.build(ctx,mus,master,()=>wid,()=>{try{return isNight();}catch(e){return false;}});engT=setInterval(()=>{try{if(!ctx||muted||musOff||document.hidden||ctx.state!=="running")return;E.sched(ctx.currentTime,ctx.currentTime+4);}catch(e){}},1000);if(!muted&&!musOff&&ctx.state==="running")E.sched(ctx.currentTime,ctx.currentTime+4);}catch(e){E=null;}}
  function note(){
    if(!ctx||muted||document.hidden)return;
    if(musOff)return;const S=SC[wid],t=ctx.currentTime,deg=S.scale[Math.floor(Math.random()*S.scale.length)],oct=Math.random()<0.5?2:4;
    const o=ctx.createOscillator(),g=ctx.createGain();o.type=S.wave;o.frequency.value=S.root*oct*Math.pow(2,deg/12);
    o.connect(g);g.connect(mus);g.connect(delay);env(g,t,0.015,S.vol,2.6);o.start(t);o.stop(t+2.8);
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
    toggle(){if(muted){muted=false;musOff=false;}else if(musOff){muted=true;}else{musOff=true;}try{localStorage.setItem("fikfuk_snd",muted?"off":musOff?"fx":"all");localStorage.setItem("fikfuk_mute",muted?"1":"0");}catch(e){}const t=ctx?ctx.currentTime:0;if(master)master.gain.setTargetAtTime(muted?0:0.55,t,0.08);if(mus)mus.gain.setTargetAtTime(musOff?0:1,t,0.08);},mode(){return muted?"off":musOff?"fx":"all";},
    setWorld(id){
      if(!SC[id])return;wid=id;if(!drone)return;const S=SC[id],t=ctx.currentTime;
      drone.o1.frequency.setTargetAtTime(S.root,t,0.8);drone.o2.frequency.setTargetAtTime(S.root*1.5,t,0.8);drone.o3.frequency.setTargetAtTime(S.root*0.5,t,0.8);
      drone.f.frequency.setTargetAtTime(S.cut,t,0.8);drone.lg.gain.setTargetAtTime(S.cut*0.35,t,0.8);if(E&&ctx.state==="running"&&!muted&&!musOff)E.sched(ctx.currentTime,ctx.currentTime+4);
    },
    chirp(v){blip(900,1500,0.22,0.05+0.12*Math.max(0,Math.min(1,v)),"sine");},
    confess(){blip(330,220,0.5,0.14,"triangle");setTimeout(()=>blip(494,330,0.5,0.08,"sine"),90);},
    portal(){if(!ctx||muted)return;const t=ctx.currentTime,o=ctx.createOscillator(),f=ctx.createBiquadFilter(),g=ctx.createGain();
      o.type="sawtooth";o.frequency.setValueAtTime(120,t);o.frequency.exponentialRampToValueAtTime(900,t+0.7);f.type="lowpass";f.frequency.setValueAtTime(300,t);f.frequency.exponentialRampToValueAtTime(3500,t+0.7);
      o.connect(f);f.connect(g);g.connect(master);env(g,t,0.1,0.11,0.9);o.start(t);o.stop(t+1.1);blip(660,1320,0.5,0.06,"sine");},beacon(){if(!ctx||muted)return;blip(523,523,2.2,0.07,"sine");setTimeout(()=>blip(659,659,2,0.06,"sine"),180);setTimeout(()=>blip(784,784,2.2,0.06,"sine"),360);setTimeout(()=>blip(1047,1047,2.6,0.05,"sine"),540);},page(){if(!ctx||muted)return;blip(392,784,0.35,0.06,"triangle");setTimeout(()=>blip(587,1175,0.4,0.05,"sine"),160);},rain(v){if(!ctx||muted)return;let R=FKAudio._r;if(!R){if(!(v>0))return;const len=ctx.sampleRate*2,buf=ctx.createBuffer(1,len,ctx.sampleRate),d=buf.getChannelData(0);for(let i=0;i<len;i++)d[i]=Math.random()*2-1;const mk=(ft,fq,q)=>{const s=ctx.createBufferSource();s.buffer=buf;s.loop=true;const f=ctx.createBiquadFilter();f.type=ft;f.frequency.value=fq;f.Q.value=q;const g=ctx.createGain();g.gain.value=0;s.connect(f);f.connect(g);g.connect(master);s.start(0,Math.random()*1.5);return g;};R=FKAudio._r={hi:mk("bandpass",4200,0.6),lo:mk("bandpass",1400,0.8),rum:mk("lowpass",260,0.5),v:-1};}if(Math.abs(R.v-v)<0.02)return;R.v=v;const t=ctx.currentTime;R.hi.gain.setTargetAtTime(0.09*v,t,0.8);R.lo.gain.setTargetAtTime(0.08*v,t,0.8);R.rum.gain.setTargetAtTime(0.05*v,t,1.2);},thunder(){if(!ctx||muted)return;if(!E)engStart();if(E)E.thunder(ctx.currentTime);else{blip(75,28,2.2,0.22,"sine");}},_eng(){return E;},dash(){blip(240,1100,0.2,0.07,"triangle");blip(1500,420,0.14,0.035,"sine");},
    near(v){
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
    },    _dbg(){return{ctx:!!ctx,state:ctx&&ctx.state,started,wid,muted};}
  };
})();
if(typeof document!=="undefined"){const _un=()=>FKAudio.unlock();["pointerdown","touchstart","keydown"].forEach(e=>document.addEventListener(e,_un,{once:true,passive:true}));}
const WORLD_CAP=50;const PORTALS={malkuth:{yesod:[5750,4250],netzach:[4250,4250],hod:[5000,3000],tiferet:[6500,3300],gevurah:[3500,3300]},yesod:{malkuth:[5000,5700],netzach:[5750,4250],hod:[4250,4250],tiferet:[5000,3000],gevurah:[6500,3500]},netzach:{malkuth:[5000,5700],yesod:[4250,4250],hod:[5750,4250],tiferet:[5000,3000],gevurah:[3500,3500]},hod:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],tiferet:[5000,3000],gevurah:[6500,3500]},tiferet:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[3500,3500],gevurah:[6500,3500]},gevurah:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[3500,3500],tiferet:[6500,3500]}};function awayFromRing(p){const dx=WORLD_W/2-p[0],dy=WORLD_H/2-p[1],d=Math.hypot(dx,dy)||1;return[p[0]+dx/d*170,p[1]+dy/d*170];}
var drawSky=(function(){
  var TH={
    malkuth:{hor:[70,60,140],neb:[[110,90,220],[60,80,200]],star:[215,215,255],moon:["#2c2850","#6a62b8","#b9b1f0","#f1eeff"],ring:true,glow:[150,140,255]},
    yesod:  {hor:[185,150,235],neb:[[230,150,255],[130,190,255]],star:[255,240,255],moon:["#4a2f6e","#9a74d0","#d9b8ff","#fff0ff"],ring:false,glow:[225,175,255]},
    netzach:{hor:[40,110,70],neb:[[70,200,110],[200,190,80]],star:[225,255,215],moon:["#10281a","#2f6a3c","#79b25a","#ecf0a0"],ring:false,glow:[130,225,130]},
    hod:{hor:[150,60,30],neb:[[255,120,50],[200,60,40]],star:[255,225,190],moon:["#3a1208","#8a3a1c","#e07a3a","#ffe0b0"],ring:false,glow:[255,150,70]},
    tiferet:{hor:[190,140,40],neb:[[255,210,90],[255,150,60]],star:[255,245,210],moon:["#4a3410","#a8782a","#f0c050","#fff4c0"],ring:true,glow:[255,215,110]},
    gevurah:{hor:[140,30,40],neb:[[220,40,60],[90,90,120]],star:[255,210,215],moon:["#2a0a10","#7a1a2a","#d04050","#ffd0d8"],ring:true,glow:[255,70,90]}
  };
  function hs(n){n=Math.imul(n^61,2654435761);n^=n>>>15;n=Math.imul(n,2246822519);n^=n>>>13;return(n>>>0)/4294967296;}
  function rg(c,a){return"rgba("+(c[0]|0)+","+(c[1]|0)+","+(c[2]|0)+","+a.toFixed(3)+")";}
  var SW=1024,SH=768,L=[{n:70,v:0.08,r:3,a:0.5},{n:42,v:0.2,r:3,a:0.7},{n:22,v:0.42,r:6,a:0.95}];
  var tiles={},TW=1024,TH2=640;
  return function drawSky(ctx,W,H,cam,t,world,skyCol,night){
    var T=TH[world]||TH.malkuth,i,j,k,m=/(\d+),(\d+),(\d+)/.exec(skyCol)||[0,8,8,16],zc=[+m[1],+m[2],+m[3]];
    ctx.save();
    // 1. base: day-cycle colour at the top, world horizon glow rising from the bottom (stepped bands)
    ctx.fillStyle=skyCol;ctx.fillRect(0,0,W,H);
    var bands=14;
    for(i=0;i<bands;i++){var y0=Math.round(H*(0.25+0.75*(i/bands)));ctx.fillStyle=rg(T.hor,(night?0.034:0.045));ctx.fillRect(0,y0,W,H-y0);}
    // 2. nebula clouds, painted once per world into a seamless tile, then scrolled with parallax
    var nt=tiles[world];
    if(!nt){nt=tiles[world]=document.createElement("canvas");nt.width=TW;nt.height=TH2;var g=nt.getContext("2d");g.globalCompositeOperation="lighter";
      for(i=0;i<6;i++){var bx=hs(i*13+1)*TW,by=hs(i*17+5)*TH2,c=T.neb[i%2],rr=hs(i+9)*0.8-0.4;
        for(var ox=-1;ox<=1;ox++)for(var oy=-1;oy<=1;oy++)for(j=0;j<4;j++){g.fillStyle=rg(c,0.016+0.013*j);g.beginPath();
          g.ellipse(bx+ox*TW,by+oy*TH2,300-j*60+hs(i)*80,120-j*24,rr,0,6.2832);g.fill();}}}
    var ox0=-(((cam.x*0.12+t*0.05)%TW)+TW)%TW,oy0=-((cam.y*0.12%TH2)+TH2)%TH2;
    for(i=0;ox0+i*TW<W;i++)for(j=0;oy0+j*TH2<H;j++)ctx.drawImage(nt,Math.round(ox0+i*TW),Math.round(oy0+j*TH2));
    // 3. world body (moon / glass planet / moss moon) with top-left light, parallax 0.03
    var mx=Math.round(W*0.78-cam.x*0.03),my=Math.round(H*0.2-cam.y*0.03),R=58;
    for(i=3;i>=1;i--){ctx.fillStyle=rg(T.glow,0.035*(5-i));ctx.beginPath();ctx.arc(mx,my,R+i*16,0,6.2832);ctx.fill();}
    if(T.ring){ctx.lineWidth=7;ctx.strokeStyle="rgba(150,140,220,0.55)";ctx.beginPath();ctx.ellipse(mx,my+4,R+34,15,-0.35,Math.PI,6.2832);ctx.stroke();}
    var tone=T.moon;
    ctx.fillStyle=tone[0];ctx.beginPath();ctx.arc(mx,my,R,0,6.2832);ctx.fill();
    ctx.fillStyle=tone[1];ctx.beginPath();ctx.arc(mx-7,my-7,R-8,0,6.2832);ctx.fill();
    ctx.fillStyle=tone[2];ctx.beginPath();ctx.arc(mx-15,my-15,R-24,0,6.2832);ctx.fill();
    ctx.fillStyle=tone[3];ctx.beginPath();ctx.arc(mx-22,my-22,R-40,0,6.2832);ctx.fill();
    ctx.fillStyle="rgba(0,0,20,0.22)";
    for(i=0;i<4;i++){ctx.beginPath();ctx.arc(mx+(hs(i+30)-0.4)*R*1.1,my+(hs(i+40)-0.3)*R*1.1,4+hs(i+50)*8,0,6.2832);ctx.fill();}
    if(T.ring){ctx.lineWidth=7;ctx.strokeStyle="rgba(190,180,250,0.7)";ctx.beginPath();ctx.ellipse(mx,my+4,R+34,15,-0.35,0,Math.PI);ctx.stroke();}
    // 4. three parallax star layers, pixel squares, grouped twinkle
    for(k=0;k<3;k++){
      var lay=L[k];
      for(i=0;i<lay.n;i++){
        var sx=((hs(k*500+i*3)*SW-cam.x*lay.v)%SW+SW)%SW*(W/SW+0.0)+0,sy=((hs(k*500+i*3+1)*SH-cam.y*lay.v)%SH+SH)%SH*(H/SH);
        var tw=0.55+0.45*Math.sin(t*(0.015+hs(k*500+i*3+2)*0.04)+i),al=lay.a*tw*(night?1:0.85);
        ctx.fillStyle=rg(T.star,al);
        var s=(i%7===0&&k===2)?6:lay.r-(k===0?1:0);
        ctx.fillRect(Math.round(sx/3)*3,Math.round(sy/3)*3,s,s);
        if(k===2&&i%5===0){ctx.fillStyle=rg(T.star,al*0.4);ctx.fillRect(Math.round(sx/3)*3-3,Math.round(sy/3)*3,9,3);}
      }
    }
    // 5. world motes: sparks drifting upward (yesod glass dust / netzach spores / malkuth embers)
    ctx.globalCompositeOperation="lighter";
    for(i=0;i<22;i++){
      var life=((t*(0.2+hs(i)*0.35)+hs(i*9)*600)%600)/600,
          px=((hs(i*5+2)*W+Math.sin(t*0.01+i*2)*16-cam.x*0.55)%W+W)%W,
          py=H-life*(H+40)+20-((cam.y*0.55)%H);
      py=((py%H)+H)%H;
      ctx.fillStyle=rg(world==="gevurah"?[255,110,100]:world==="tiferet"?[255,225,140]:world==="hod"?[255,170,90]:world==="netzach"?[200,255,140]:world==="yesod"?[255,220,255]:[190,180,255],0.7*Math.sin(life*Math.PI));
      ctx.fillRect(Math.round(px/3)*3,Math.round(py/3)*3,3,3);
    }
    // 6. rare shooting star (every ~9s, seeded by the cycle number)
    var per=540,ph=t%per,cyc=(t/per)|0;
    if(ph<28){var p=ph/28,x0=hs(cyc*3+1)*W*0.7+W*0.25,y0=hs(cyc*3+2)*H*0.35;
      for(i=0;i<9;i++){ctx.fillStyle=rg([255,255,255],(1-p)*(1-i/9)*0.9);var q=p*220-i*7;ctx.fillRect(Math.round((x0-q)/3)*3,Math.round((y0+q*0.45)/3)*3,3,3);}}
    ctx.restore();
  };
})();

var drawPortal=(function () {
  var PAL = {
    malkuth: { ring: ["#15122e", "#3a3470", "#8f86d8", "#e8e4ff"], glow: [170, 160, 255], core: [235, 230, 255], spark: "#ffffff" },
    yesod:   { ring: ["#2a1f4a", "#6b55a8", "#b7a0f0", "#f4eaff"], glow: [200, 170, 255], core: [255, 240, 255], spark: "#ffffff" },
    netzach: { ring: ["#0b1c12", "#244a2c", "#5f8f45", "#d9d77a"], glow: [120, 220, 130], core: [235, 255, 190], spark: "#ffe9a0" },
    hod: { ring: ["#2a0f08", "#6a2a14", "#e07a3a", "#ffe0a8"], glow: [255, 140, 60], core: [255, 235, 190], spark: "#ffcf80" },
    tiferet: { ring: ["#3a2808", "#8a6a1c", "#f0c050", "#fff4c0"], glow: [255, 215, 100], core: [255, 250, 220], spark: "#fff2b0" },
    gevurah: { ring: ["#1a0608", "#5a1420", "#d03a4c", "#ffc8d0"], glow: [255, 70, 90], core: [255, 225, 230], spark: "#ffb0b8" }
  };
  function h(n) { n = Math.imul(n ^ 61, 2654435761); n ^= n >>> 15; n = Math.imul(n, 2246822519); n ^= n >>> 13; return (n >>> 0) / 4294967296; }
  function g3(v) { return Math.round(v / 3) * 3; }
  function rgba(c, a) { return "rgba(" + c[0] + "," + c[1] + "," + c[2] + "," + a.toFixed(3) + ")"; }
  var RX = 56, RY = 28;
  return function drawPortal(ctx, x, y, t, dest) {
    var P = PAL[dest] || PAL.malkuth, i, k, a, ang;
    var pulse = 0.5 + 0.5 * Math.sin(t * 0.045);
    ctx.save();
    // 1. ground glow bands + contact shadow
    ctx.fillStyle = "rgba(0,0,0,0.38)";
    ctx.beginPath(); ctx.ellipse(x + 4, y + 5, RX + 10, RY + 5, 0, 0, 6.2832); ctx.fill();
    ctx.globalCompositeOperation = "lighter";
    for (i = 0; i < 5; i++) {
      ctx.fillStyle = rgba(P.glow, (0.05 + 0.025 * pulse) * (5 - i) / 5 + 0.015);
      ctx.beginPath(); ctx.ellipse(x, y, RX + 44 - i * 8, RY + 22 - i * 4, 0, 0, 6.2832); ctx.fill();
    }
    ctx.globalCompositeOperation = "source-over";
    // 2. back half of the ring (far side), stepped tones
    function arc(w, col, a0, a1, rx, ry, dx, dy) {
      ctx.lineWidth = w; ctx.strokeStyle = col; ctx.beginPath();
      ctx.ellipse(x + (dx || 0), y + (dy || 0), rx || RX, ry || RY, 0, a0, a1); ctx.stroke();
    }
    var PI = Math.PI;
    arc(12, P.ring[0], PI, 2 * PI, RX, RY, 0, 0);
    arc(9, P.ring[1], PI, 2 * PI, RX, RY, 0, 0);
    arc(3, P.ring[2], PI * 1.05, PI * 1.55, RX, RY, 0, -1);
    ctx.globalCompositeOperation = "lighter";
    // 3. floor of the gate (bright core inside the ring)
    for (i = 0; i < 4; i++) {
      ctx.fillStyle = rgba(P.core, 0.12 + 0.09 * i + 0.06 * pulse * (i / 3));
      ctx.beginPath(); ctx.ellipse(x, y, RX - 8 - i * 9, RY - 4 - i * 4.5, 0, 0, 6.2832); ctx.fill();
    }
    // 4. light column: stacked bands, shimmering, narrowing and fading with height
    var H = 128;
    for (k = 0; k < H; k += 6) {
      var f = k / H, hw = g3((RX - 12) * (1 - f * 0.55) + 2 * Math.sin(t * 0.03 + k * 0.12));
      a = (0.68 * (1 - f) * (1 - f) + 0.03) * (0.75 + 0.25 * Math.sin(t * 0.06 - k * 0.09));
      ctx.fillStyle = rgba(P.glow, a);
      ctx.fillRect(x - hw, y - k - 6, hw * 2, 6);
    }
    for (i = 0; i < 6; i++) {            // slow vertical streaks inside the column
      var sx = x + g3((h(i + 7) - 0.5) * 70 * (1 - ((t * 0.4 + i * 37) % 120) / 260));
      var sy = y - ((t * (0.35 + h(i) * 0.3) + i * 53) % H);
      ctx.fillStyle = rgba(P.core, 0.35 * (1 - (y - sy) / H));
      ctx.fillRect(sx, g3(sy), 3, 9);
    }
    ctx.globalCompositeOperation = "source-over";
    // 5. per-world dressing standing on the far half
    if (dest === "yesod") {
      for (i = 0; i < 7; i++) {
        ang = PI * (1.08 + 0.84 * (i / 6)); var cx = x + Math.cos(ang) * RX, cy = y + Math.sin(ang) * RY;
        var ch = 16 + h(i + 3) * 14, hue = (t * 0.6 + i * 50) % 360;
        ctx.fillStyle = "hsla(" + hue + ",70%,78%,0.85)"; ctx.beginPath();
        ctx.moveTo(cx - 5, cy); ctx.lineTo(cx, cy - ch); ctx.lineTo(cx + 5, cy); ctx.closePath(); ctx.fill();
        ctx.fillStyle = "rgba(255,255,255,0.7)"; ctx.beginPath();
        ctx.moveTo(cx - 5, cy); ctx.lineTo(cx, cy - ch); ctx.lineTo(cx - 1, cy); ctx.closePath(); ctx.fill();
      }
    }
    ctx.globalCompositeOperation = "lighter";
    // 6. particles rising through the column
    for (i = 0; i < 16; i++) {
      var life = ((t * (0.5 + h(i * 3) * 0.6) + h(i * 5) * 200) % 120) / 120;
      var px = x + (h(i * 7 + 1) - 0.5) * (RX * 1.5) * (1 - life * 0.5) + Math.sin(t * 0.04 + i) * 5;
      var py = y - 6 - life * 110 + (h(i * 11) - 0.5) * 20;
      ctx.fillStyle = rgba(i % 3 === 0 ? [255, 255, 255] : P.core, 0.9 * Math.sin(life * PI));
      var s = i % 4 === 0 ? 6 : 3; ctx.fillRect(g3(px), g3(py), s, s);
    }
    ctx.globalCompositeOperation = "source-over";
    // 7. front half of the ring (near side) drawn over the column
    arc(12, P.ring[0], 0, PI, RX, RY, 0, 0);
    arc(9, P.ring[1], 0, PI, RX, RY, 0, 0);
    arc(5, P.ring[2], 0.1, PI * 0.45, RX - 1, RY - 1, 0, -1);
    arc(2, P.ring[3], 0.25, PI * 0.35, RX - 1, RY - 1, 0, -2);
    // 8. runes / lights travelling round the ring
    for (i = 0; i < 8; i++) {
      ang = t * 0.012 + i * (PI / 4);
      var rx2 = x + Math.cos(ang) * RX, ry2 = y + Math.sin(ang) * RY, near = Math.sin(ang) > 0;
      ctx.fillStyle = rgba(P.core, near ? 0.95 : 0.45);
      ctx.fillRect(g3(rx2) - 1, g3(ry2) - 1, near ? 6 : 3, near ? 6 : 3);
    }
    // 9. world-specific accents on the near side
    if (dest === "netzach") {
      ctx.lineWidth = 3; ctx.strokeStyle = P.ring[2];
      for (i = 0; i < 3; i++) {
        var ra = 0.35 + i * 1.05, bx = x + Math.cos(ra) * RX, by = y + Math.sin(ra) * RY;
        ctx.beginPath(); ctx.moveTo(bx, by);
        ctx.quadraticCurveTo(bx + 10 * (i - 1), by - 14 - i * 3, bx + 4 + 12 * Math.sin(t * 0.02 + i), by - 26 - 6 * i);
        ctx.stroke();
        ctx.fillStyle = P.ring[3]; ctx.fillRect(g3(bx + 4 + 12 * Math.sin(t * 0.02 + i)) - 1, g3(by - 26 - 6 * i) - 1, 3, 3);
      }
    } else if (dest === "gevurah") {
      for (i = 0; i < 5; i++) { var ga = 0.3 + i * 0.62, gx = x + Math.cos(ga) * RX, gy = y + Math.sin(ga) * RY, gh = 14 + (i % 2) * 7;
        ctx.fillStyle = P.ring[2]; ctx.fillRect(g3(gx) - 1, g3(gy) - gh, 3, gh); ctx.fillStyle = P.ring[3]; ctx.fillRect(g3(gx) - 1, g3(gy) - gh, 3, 3); }
    } else if (dest === "tiferet") {
      for (i = 0; i < 4; i++) { var ta = t * 0.03 + i * PI / 2, tx = x + Math.cos(ta) * (RX + 9), ty = y + Math.sin(ta) * (RY + 5) - 4;
        ctx.fillStyle = rgba([255, 240, 170], 0.5 + 0.4 * Math.sin(t * 0.08 + i)); ctx.fillRect(g3(tx) - 1, g3(ty) - 5, 3, 11); ctx.fillRect(g3(tx) - 5, g3(ty) - 1, 11, 3); }
    } else if (dest === "hod") {
      for (i = 0; i < 5; i++) { var ea = 0.4 + i * 1.3, ex = x + Math.cos(ea) * RX, ey = y + Math.sin(ea) * RY - ((t * 0.5 + i * 23) % 40);
        ctx.fillStyle = rgba([255, 170 + i * 10, 80], 0.9 - ((t * 0.5 + i * 23) % 40) / 50); ctx.fillRect(g3(ex) - 1, g3(ey) - 1, 3, 3); }
    } else if (dest === "malkuth") {
      for (i = 0; i < 3; i++) {
        var sa = 0.5 + i * 2.1, sxs = x + Math.cos(sa) * (RX + 3), sys = y + Math.sin(sa) * (RY + 2) - 6;
        var tw = 0.5 + 0.5 * Math.sin(t * 0.07 + i * 2);
        ctx.fillStyle = rgba([255, 255, 255], 0.4 + 0.5 * tw);
        ctx.fillRect(g3(sxs) - 1, g3(sys) - 7, 3, 15); ctx.fillRect(g3(sxs) - 7, g3(sys) - 1, 15, 3);
      }
    }
    ctx.restore();
  };
})();


const WORLD_W   = 10000;
const WORLD_H   = 10000;
const RESET_MS  = 3 * 60 * 60 * 1000;
const EPOCH_ANCHOR = 1700000000000;
const DAY_CYCLE_MS = 30 * 60 * 1000; // 30 min full cycle
function getDayProgress(){
  // 0.0 = midnight, 0.5 = noon, 1.0 = midnight again
  return ((Date.now()-EPOCH_ANCHOR) % DAY_CYCLE_MS) / DAY_CYCLE_MS;
}
function isNight(){
  const p=getDayProgress();
  return p<0.25||p>0.75; // night = first and last quarter
}
function getSkyColor(){
  const p=getDayProgress();
  // 0=midnight #080810, 0.25=dawn #1a0f2e, 0.5=noon #0d1a2e, 0.75=dusk #2e0f1a
  if(p<0.25){
    const t=p/0.25;
    return blendColor([8,8,16],[26,15,46],t);
  } else if(p<0.5){
    const t=(p-0.25)/0.25;
    return blendColor([26,15,46],[13,26,46],t);
  } else if(p<0.75){
    const t=(p-0.5)/0.25;
    return blendColor([13,26,46],[46,15,26],t);
  } else {
    const t=(p-0.75)/0.25;
    return blendColor([46,15,26],[8,8,16],t);
  }
}
function blendColor(a,b,t){
  const r=Math.round(a[0]+(b[0]-a[0])*t);
  const g=Math.round(a[1]+(b[1]-a[1])*t);
  const bl=Math.round(a[2]+(b[2]-a[2])*t);
  return `rgb(${r},${g},${bl})`;
}
const P = 3; // pixel scale
const ff = "'Press Start 2P',monospace";

// ─── Session / identity ───────────────────────────────────────────────────────
function getClientId(){
  const _ce=String(getEpoch());let id = localStorage.getItem("fikfuk_cid");if(id&&localStorage.getItem("fikfuk_cid_e")!==_ce)id=null;
  if(!id){ id="u_"+Math.random().toString(36).slice(2,12); localStorage.setItem("fikfuk_cid",id); }localStorage.setItem("fikfuk_cid_e",_ce);
  return id;
}
// shared world clock: Ably server time minus this device's clock
let clockOffset=0;
function sharedNow(){ return Date.now()+clockOffset; }
function getEpoch(){ return Math.floor((sharedNow()-EPOCH_ANCHOR)/RESET_MS); }
function nextResetMs(){ return EPOCH_ANCHOR+(getEpoch()+1)*RESET_MS-sharedNow(); }

// seeded RNG: same epoch + same tag = same sequence on every device
function hashStr(str){
  let h1=0xdeadbeef,h2=0x41c6ce57;
  for(let i=0;i<str.length;i++){
    const ch=str.charCodeAt(i);
    h1=Math.imul(h1^ch,2654435761);
    h2=Math.imul(h2^ch,1597334677);
  }
  h1=Math.imul(h1^(h1>>>16),2246822507)^Math.imul(h2^(h2>>>13),3266489909);
  h2=Math.imul(h2^(h2>>>16),2246822507)^Math.imul(h1^(h1>>>13),3266489909);
  return (h1^h2)>>>0;
}
function mulberry32(a){
  return function(){
    a|=0; a=a+0x6D2B79F5|0;
    let t=Math.imul(a^(a>>>15),1|a);
    t=t+Math.imul(t^(t>>>7),61|t)^t;
    return ((t^(t>>>14))>>>0)/4294967296;
  };
}
function worldRng(tag){ return mulberry32(hashStr("fikfuk:"+getEpoch()+":"+tag+(WORLD_ID==="malkuth"?"":":w:"+WORLD_ID))); }
function fmtCountdown(ms){
  if(ms<=0)return"00:00:00";
  const h=Math.floor(ms/3600000),m=Math.floor((ms%3600000)/60000),s=Math.floor((ms%60000)/1000);
  return`${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
}
function loadSession(){
  try{const r=localStorage.getItem("fikfuk_s");if(!r)return null;const s=JSON.parse(r);if(s.epoch===getEpoch())return s;}catch(e){}
  return null;
}
function saveSession(d){ localStorage.setItem("fikfuk_s",JSON.stringify({...d,epoch:getEpoch()})); }

// ─── Palettes ─────────────────────────────────────────────────────────────────
const PALETTES = [
  { id:0, label:"wheat",   body:"#f5deb3", shadow:"#c8a97e", stripe:"#b8860b", inner:"#ffb6c1", eye:"#2ecc71", pupil:"#1a5c36", nose:"#ff9eb5" },
  { id:1, label:"slate",   body:"#b0c4de", shadow:"#7a9ab5", stripe:"#4a7fa5", inner:"#ffc0cb", eye:"#3498db", pupil:"#1a4f7a", nose:"#ffb6c1" },
  { id:2, label:"ember",   body:"#ff9966", shadow:"#cc5500", stripe:"#cc4400", inner:"#ffccaa", eye:"#f1c40f", pupil:"#7a6000", nose:"#ff8fab" },
  { id:3, label:"void",    body:"#2c2c3e", shadow:"#1a1a2e", stripe:"#3d3d5c", inner:"#ff8fab", eye:"#9b59b6", pupil:"#5b1f8a", nose:"#ffb6c1" },
  { id:4, label:"honey",   body:"#f0e68c", shadow:"#c8b400", stripe:"#daa520", inner:"#fff0a0", eye:"#27ae60", pupil:"#145a32", nose:"#ffb6c1" },
  { id:5, label:"ghost",   body:"#e8e8e8", shadow:"#aaaaaa", stripe:"#888888", inner:"#ffccdd", eye:"#e74c3c", pupil:"#7a0000", nose:"#ff9eb5" },
  { id:6, label:"caramel", body:"#d2691e", shadow:"#8b3a0a", stripe:"#a0522d", inner:"#ffccaa", eye:"#16a085", pupil:"#0a4a3a", nose:"#ffb6c1" },
];
const SYS_PAL_PRIVACY={ body:"#1a1a2e",shadow:"#0d0d1a",stripe:"#2d2d5e",inner:"#c0c0ff",eye:"#7777ff",pupil:"#3333aa",nose:"#aaaaff",_name:"policy" };
const SYS_PAL_ABOUT  ={ body:"#1a2e1a",shadow:"#0d1a0d",stripe:"#2d5e2d",inner:"#c0ffc0",eye:"#44cc44",pupil:"#226622",nose:"#aaffaa",_name:"about"  };
const PRIVACY_LINES=["anonymous","no accounts","no emails","confessions live 3hrs","then wiped forever","no tracking · ever"];
const ABOUT_LINES  =["fikfuk.wtf","a canvas of strangers","& their pixel cats","built by cruelbites","donate via solana","double-tap to donate"];
const SYS_PAL_PATATES={ body:"#e07b39",shadow:"#a85a28",stripe:"#c4672f",inner:"#ffd9a0",eye:"#ffcc66",pupil:"#7a4a10",nose:"#ffb6c1",_name:"patates" };
const PATATES_LINES=["thank u for taking care of me","i loved being clingy with u","my naughty days were the best days","i am okay now, dont worry","i still hear u calling my name","u gave me a good life"];
const SYS_PAL_ORACLE={ body:"#1a0a2e",shadow:"#0d0514",stripe:"#3d1a5e",inner:"#e0c0ff",eye:"#cc44ff",pupil:"#660099",nose:"#ff88ff",_name:"oracle" };
const FEED_LINES=["a mouse! thank u","my favorite, how did u know","purr purr, so good","i saved a spot for u","best treat ever","u always know what i like"];
const ORACLE_RESPONSES=[
  "yes, but not yet","no, and that is okay","the stars say maybe","ask again at midnight",
  "your cat knows the answer","it has already happened","let it go","not in this session",
  "the wall holds your answer","yes, absolutely","never","only if u confess first",
];

// ─── Cat renderer ─────────────────────────────────────────────────────────────
/*_catact*/let _catAct=0;function _actFor(c){const t=c._sitT||0;if(t<240||c.isSys||c.grabbed)return 0;if(t>1500)return 4;const i=Math.floor((t-240)/300);if((t-240)%300>200)return 0;return[1,2,3,5,0,0][hashStr(String(c.id)+":"+i)%6];}
function _cmix(c,t,k){if(typeof c!=="string"||c[0]!=="#"||c.length<7)return c;const n=parseInt(c.slice(1,7),16),m=parseInt(t.slice(1,7),16),r=(n>>16)&255,g=(n>>8)&255,b=n&255,R2=(m>>16)&255,G=(m>>8)&255,B=m&255;return"rgb("+Math.round(r+(R2-r)*k)+","+Math.round(g+(G-g)*k)+","+Math.round(b+(B-b)*k)+")";}
function drawCat(ctx,x,y,p,frame,pal,flip,state,grabbed,isOwn,isSys,idle){
  ctx.save();
  if(idle) ctx.globalAlpha=0.38;
  ctx.translate(x,y);
  if(flip){ctx.translate(9*p,0);ctx.scale(-1,1);}
  const{body,shadow,stripe,inner,eye,pupil,nose}=pal;
  const bob=grabbed?0:Math.sin(frame*0.08)*(state==="run"?0:0.5);
  const R=(c,x,y,w,h)=>{ctx.fillStyle=c;ctx.fillRect(x*p,(y+bob)*p,w*p,h*p);};
  const T=pal._t||(pal._t={hi:_cmix(body,"#ffffff",0.34),lo:shadow,deep:_cmix(shadow,"#000000",0.4),hi2:_cmix(inner,"#ffffff",0.45),rim:_cmix(body,"#ffffff",0.55)});
  const sit=state==="sit",run=state==="run";const _a=(sit&&!isSys)?_catAct:0;if(_a===2){const _k=0.5+0.5*Math.sin(frame*0.05);ctx.translate(0,12.5*p);ctx.scale(1+0.14*_k,1-0.08*_k);ctx.translate(0,-12.5*p);}if(_a===4){ctx.translate(0,1.2*p);}
  const sw=Math.round(Math.sin(frame*0.1)*1);
  // tail (behind the body)
  if(sit){R(T.deep,8,11,4,1);R(shadow,9,10,3,1);R(stripe,11,10,1,1);R(body,9,11,2,1);}
  else{[[9,10],[10,9],[11,7],[11,5],[10+sw,3]].forEach((q,i)=>{R(i%2?stripe:shadow,q[0],q[1],2,2);R(T.hi,q[0],q[1],1,1);});R(inner,10+sw,3,1,1);}
  // body: dark back layer, lit main mass, haunches, chest
  R(T.deep,2,12,8,1);
  R(shadow,2,5,8,7);R(body,2,5,6,6);R(T.hi,2,5,2,5);R(T.hi,3,5,3,1);R(T.deep,8,10,2,2);R(shadow,2,11,8,1);
  if(sit){R(body,1,8,3,4);R(T.hi,1,8,1,3);R(shadow,8,8,3,4);R(T.deep,10,9,1,3);R(T.deep,1,12,3,1);}
  else{R(body,1,9,2,3);R(T.hi,1,9,1,2);R(shadow,9,9,2,3);}
  R(inner,4,6,3,5);R(T.hi2,4,6,1,3);R(shadow,6,9,1,2);
  R(stripe,2,6,2,1);R(stripe,2,8,2,1);R(stripe,7,6,2,1);R(stripe,7,8,2,1);
  // legs
  if(sit){R(body,4,11,2,2);R(shadow,6,11,2,2);R(inner,4,12,2,1);R(inner,6,12,2,1);R(T.hi,4,11,1,1);}
  else{
    const lf=run?Math.sin(frame*0.28):0,a=Math.round(lf),b=-a;
    R(body,3,11,2,2+Math.max(0,a));R(shadow,6,11,2,2+Math.max(0,b));
    R(inner,3,12+Math.max(0,a),2,1);R(inner,6,12+Math.max(0,b),2,1);R(T.hi,3,11,1,1);
    R(body,1,11,2,1+Math.max(0,b));R(shadow,9,11,2,1+Math.max(0,a));
  }
  // ears
  R(body,1,-4,1,1);R(body,1,-3,2,1);R(body,0,-2,3,2);R(inner,1,-3,1,2);R(T.rim,1,-4,1,1);R(T.hi,0,-2,1,1);
  R(body,9,-4,1,1);R(body,8,-3,2,1);R(body,8,-2,3,2);R(inner,9,-3,1,2);R(shadow,10,-2,1,2);R(shadow,9,-4,1,1);
  // head: lit top-left, shaded bottom-right, rounded corners
  R(shadow,2,4,7,1);R(body,2,-1,7,1);R(body,0,0,11,3);R(body,1,3,9,1);
  R(T.rim,2,-1,3,1);R(T.hi,0,0,2,2);R(T.hi,5,-1,2,1);
  R(shadow,9,1,2,3);R(shadow,1,3,9,1);R(T.deep,10,2,1,2);
  R(stripe,4,-1,1,2);R(stripe,6,-1,1,2);R(stripe,5,0,1,1);R(stripe,0,2,2,1);R(stripe,9,2,2,1);
  R(inner,3,3,5,2);R(T.hi2,3,3,2,1);
  ctx.fillStyle="rgba(255,150,150,0.35)";ctx.fillRect(1*p,(bob+3)*p,2*p,p);ctx.fillRect(8*p,(bob+3)*p,2*p,p);
  if(_a===1){const _k=Math.round(Math.sin(frame*0.25)*1);R(T.deep,6,1+_k,4,3);R(body,6,1+_k,3,2);R(T.hi,6,1+_k,2,1);R(inner,7,2+_k,1,1);R("#ff8a9a",5,4,1,1);}if(_a===5){R("#6a1020",4,4,3,2);R("#ff8a9a",5,5,1,1);}if(_a===3){const _w=Math.round(Math.sin(frame*0.35)*2);R(stripe,10+_w,7,1,3);R(body,11+_w,6,1,2);}const blink=(frame%220>210)||_a===1||_a===4||_a===5;
  if(idle||blink){
    ctx.fillStyle=idle?"#555":"#000";
    ctx.fillRect(2*p,(bob+1)*p,3*p,p);ctx.fillRect(6*p,(bob+1)*p,3*p,p);
  } else {
    ctx.fillStyle=_cmix(eye,"#000000",0.3);ctx.fillRect(2*p,(bob+1)*p,3*p,2*p);ctx.fillRect(6*p,(bob+1)*p,3*p,2*p);
    ctx.fillStyle=eye;ctx.fillRect(2*p,(bob+1)*p,3*p,p);ctx.fillRect(6*p,(bob+1)*p,3*p,p);
    ctx.fillStyle=pupil;ctx.fillRect(3*p,(bob+1)*p,p,2*p);ctx.fillRect(7*p,(bob+1)*p,p,2*p);
    ctx.fillStyle="rgba(255,255,255,0.95)";ctx.fillRect(2*p,(bob+1)*p,p,p);ctx.fillRect(6*p,(bob+1)*p,p,p);
  }
  ctx.fillStyle=nose;ctx.fillRect(4*p,(bob+3)*p,3*p,p);ctx.fillRect(5*p,(bob+3)*p,p,2*p);
  ctx.fillStyle=T.deep;ctx.fillRect(4*p,(bob+4)*p,p,p);ctx.fillRect(6*p,(bob+4)*p,p,p);  ctx.fillStyle="rgba(255,255,255,0.5)";
  ctx.fillRect(-2*p,(bob+2)*p,3*p,1);ctx.fillRect(-p,(bob+3)*p,2*p,1);
  ctx.fillRect(10*p,(bob+2)*p,3*p,1);ctx.fillRect(10*p,(bob+3)*p,2*p,1);
  if(grabbed){
    const t=frame*0.2;ctx.fillStyle="rgba(255,220,100,0.85)";
    [[3,Math.sin(t)*7-10],[7,Math.cos(t)*7-10],[5,Math.sin(t+1)*6-12]].forEach(([ox,oy])=>ctx.fillRect(ox*p,oy,p,p));
  }
  if(isSys){
    ctx.strokeStyle=eye;ctx.lineWidth=1;
    ctx.globalAlpha=(idle?0.1:0.35)+Math.sin(frame*0.05)*0.2;
    ctx.beginPath();ctx.arc(5.5*p,(bob+4)*p,20,0,Math.PI*2);ctx.stroke();
  }
  ctx.restore();
  // name + indicators
  ctx.save();
  if(idle)ctx.globalAlpha=0.35;
  ctx.font=`${Math.max(6,p*1.5)}px ${ff}`;
  const tag=pal._name||"";
  if(tag){
    const tw2=ctx.measureText(tag).width;
    ctx.fillStyle=isSys?eye:(isOwn?"rgba(255,80,80,0.9)":"rgba(180,180,255,0.6)");
    ctx.fillText(tag,x+5.5*p-tw2/2,y+16*p);
  }
  if(_catAct===4&&!isSys){const _zt=frame*0.03;for(let i=0;i<3;i++){const ph=(_zt+i*0.33)%1;ctx.globalAlpha=(1-ph)*0.8;ctx.font=(p*(1.6+i*0.5))+"px "+ff;ctx.fillStyle="#bbbbff";ctx.fillText("z",x+10*p+ph*8*p,y-6-ph*14*p);}ctx.globalAlpha=idle?0.35:1;}if(isOwn&&!isSys){ctx.fillStyle="rgba(255,80,80,0.85)";ctx.beginPath();ctx.arc(x+5.5*p,y-6,3,0,Math.PI*2);ctx.fill();}
  if(idle&&!isSys){
    ctx.globalAlpha=0.7+Math.sin(frame*0.06)*0.3;
    ctx.font=`${p*2.5}px ${ff}`;ctx.fillStyle="#aaaaff";
    ctx.fillText("zzz",x+10*p,y-10-Math.sin(frame*0.04)*4);
  }
  ctx.restore();
}

// ─── World objects renderer ───────────────────────────────────────────────────
/*_objstyle*/function drawUFO(ctx,x,y,frame,confession,hitCount){
  ctx.save();ctx.translate(x,y);
  const hov=Math.sin(frame*0.04)*4,pu=0.5+0.5*Math.sin(frame*0.07);
  // soft ground shadow far below (shrinks as it rises)
  ctx.fillStyle="rgba(0,0,0,"+(0.16-hov*0.01)+")";ctx.beginPath();ctx.ellipse(8,64,26-hov,7,0,0,Math.PI*2);ctx.fill();
  // tractor beam: stepped layers fading toward the ground, lit pool on the ground
  ctx.save();ctx.globalCompositeOperation="lighter";
  for(let i=0;i<4;i++){ctx.fillStyle="rgba(100,200,255,"+(0.035+0.012*i*pu)+")";
    ctx.beginPath();ctx.moveTo(-4-i*2,hov+9);ctx.lineTo(-20+i*4,62);ctx.lineTo(20-i*4,62);ctx.lineTo(4+i*2,hov+9);ctx.fill();}
  ctx.fillStyle="rgba(120,220,255,"+(0.10+0.06*pu)+")";ctx.beginPath();ctx.ellipse(0,62,22,6,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="rgba(200,245,255,0.14)";ctx.beginPath();ctx.ellipse(0,62,12,3.2,0,0,Math.PI*2);ctx.fill();
  ctx.restore();
  if(hitCount>0){
    const flashAlpha=Math.max(0,0.4-hitCount*0.01);
    ctx.fillStyle="rgba(255,100,100,"+flashAlpha+")";
    ctx.beginPath();ctx.ellipse(0,hov,32,13,0,0,Math.PI*2);ctx.fill();
  }
  // hull: dark underside, mid body, lit top-left rim
  ctx.fillStyle="#14142e";ctx.beginPath();ctx.ellipse(0,hov+4,24,8,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#26264a";ctx.beginPath();ctx.ellipse(0,hov,29,10,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#3a3a72";ctx.beginPath();ctx.ellipse(-2,hov-1,26,8,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#5656a0";ctx.beginPath();ctx.ellipse(-4,hov-2,20,5.5,0,Math.PI*1.05,Math.PI*1.95);ctx.fill();
  ctx.strokeStyle="rgba(190,190,255,0.7)";ctx.lineWidth=2;ctx.beginPath();ctx.ellipse(-1,hov-1,26,8.5,0,Math.PI*1.1,Math.PI*1.55);ctx.stroke();
  // dome: glass with a little green passenger and a highlight
  ctx.fillStyle="#12122c";ctx.beginPath();ctx.ellipse(0,hov-6,14,11,0,Math.PI,Math.PI*2);ctx.fill();
  ctx.fillStyle="rgba(110,210,255,0.42)";ctx.beginPath();ctx.ellipse(0,hov-6,12,9,0,Math.PI,Math.PI*2);ctx.fill();
  ctx.fillStyle="#7ee07e";ctx.fillRect(-3,hov-12,6,6);ctx.fillStyle="#1a3a1a";ctx.fillRect(-2,hov-10,1.5,2);ctx.fillRect(1,hov-10,1.5,2);
  ctx.fillStyle="rgba(255,255,255,0.55)";ctx.beginPath();ctx.ellipse(-5,hov-11,3,2,-0.6,0,Math.PI*2);ctx.fill();
  // rim lights with glow
  [-18,-9,0,9,18].forEach((lx,i)=>{
    const on=Math.sin(frame*0.1+i*1.2)>0;
    if(on){ctx.fillStyle="rgba(255,255,100,0.22)";ctx.beginPath();ctx.arc(lx,hov+3,6,0,Math.PI*2);ctx.fill();}
    ctx.fillStyle=on?"#ffff66":"#2c2c44";
    ctx.beginPath();ctx.arc(lx,hov+3,2.6,0,Math.PI*2);ctx.fill();
  });
  ctx.restore();
  if(confession){
    ctx.save();
    ctx.font=`7px ${ff}`;
    const tw=ctx.measureText(confession).width;
    const bx=x-tw/2-8,by=y+55,bw=tw+16,bh=22;
    ctx.fillStyle="rgba(10,20,10,0.85)";ctx.strokeStyle="#44ff44";ctx.lineWidth=1;
    rrect(ctx,bx,by,bw,bh,3);ctx.fill();ctx.stroke();
    ctx.fillStyle="#88ff88";ctx.fillText(confession,bx+8,by+15);
    ctx.restore();
  }
}

function drawFossil(ctx,x,y,frame,revealed,sitTimer,confession){
  ctx.save();ctx.translate(x,y);
  const alpha=revealed?0.95:0.38+Math.sin(frame*0.02)*0.1;
  ctx.globalAlpha=alpha;
  // dirt mound: dark base, lit top-left, tiny pebbles
  ctx.fillStyle="#1f150c";ctx.beginPath();ctx.ellipse(3,3,26,13,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#3a2816";ctx.beginPath();ctx.ellipse(0,0,24,12,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#58402a";ctx.beginPath();ctx.ellipse(-3,-2,19,8.5,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#78593a";ctx.beginPath();ctx.ellipse(-8,-4,10,4.5,-0.2,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#2a1c10";[[10,3],[16,-2],[-14,4],[4,6]].forEach(q=>ctx.fillRect(q[0],q[1],3,3));
  if(revealed){
    // bones: femur pair and a small skull, shaded
    ctx.fillStyle="#9c8c6a";ctx.fillRect(-12,-2,24,6);
    ctx.fillStyle="#d8c9a4";ctx.fillRect(-12,-3,24,5);ctx.fillStyle="#f3e8c8";ctx.fillRect(-12,-3,24,2);
    [-13,13].forEach((bx,i)=>{ctx.fillStyle="#d8c9a4";ctx.beginPath();ctx.arc(bx,i?3:-4,5,0,Math.PI*2);ctx.fill();ctx.fillStyle="#f3e8c8";ctx.beginPath();ctx.arc(bx-1.5,(i?3:-4)-1.5,2.5,0,Math.PI*2);ctx.fill();});
    ctx.fillStyle="#cdbd98";ctx.beginPath();ctx.ellipse(0,-6,7,5.5,0,0,Math.PI*2);ctx.fill();
    ctx.fillStyle="#efe3c0";ctx.beginPath();ctx.ellipse(-1.5,-7.5,4.5,3,0,0,Math.PI*2);ctx.fill();
    ctx.fillStyle="#2a1c10";ctx.fillRect(-4,-7,3,3);ctx.fillRect(1,-7,3,3);ctx.fillRect(-1,-3,2,2);
  } else {
    ctx.strokeStyle="rgba(212,196,160,0.55)";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(-6,-4);ctx.lineTo(6,4);ctx.moveTo(6,-4);ctx.lineTo(-6,4);ctx.stroke();
  }
  if(!revealed&&sitTimer>0){
    const pct=Math.min(sitTimer/180,1);
    ctx.globalAlpha=0.8;
    ctx.fillStyle="rgba(0,0,0,0.5)";ctx.fillRect(-20,16,40,5);
    ctx.fillStyle="#f5c842";ctx.fillRect(-20,16,40*pct,5);
    ctx.fillStyle="#fff2a8";ctx.fillRect(-20,16,40*pct,1.5);
    for(let i=0;i<4;i++){ctx.fillStyle="rgba(200,170,120,"+(0.5-i*0.1)+")";ctx.fillRect(-12+((frame*0.6+i*13)%24),-6-((frame*0.5+i*7)%14),3,3);}
  }
  if(revealed&&confession){
    ctx.font=`6px ${ff}`;ctx.fillStyle="#ffddaa";
    ctx.globalAlpha=0.9;
    const tw=ctx.measureText(confession).width;
    ctx.fillStyle="rgba(0,0,0,0.6)";ctx.fillRect(-tw/2-4,16,tw+8,14);
    ctx.fillStyle="#ffddaa";ctx.fillText(confession,-tw/2,27);
  }
  ctx.restore();
}

function drawWildCat(ctx,x,y,frame,pal,flip){
  drawCat(ctx,x,y,P,frame,pal,flip,"run",false,false,false,false);
  ctx.save();ctx.translate(x,y);
  if(flip){ctx.translate(9*P,0);ctx.scale(-1,1);}
  ctx.fillStyle="#ff3b2e";ctx.fillRect(2*P,P,P,P);ctx.fillRect(7*P,P,P,P);
  ctx.fillStyle="#2a0000";ctx.fillRect(2*P,0,3*P,P*0.6);ctx.fillRect(6*P,0,3*P,P*0.6);
  ctx.fillStyle="rgba(255,255,255,0.9)";ctx.fillRect(5*P,4*P,P,P);
  ctx.restore();
}

function drawMouse(ctx,x,y,frame,flip){
  ctx.save();ctx.translate(x,y);
  if(flip){ctx.translate(6*P,0);ctx.scale(-1,1);}
  const bob=Math.sin(frame*0.2)*1,st=Math.sin(frame*0.4)>0?1:0;
  const R=(c,a,b,w,h)=>{ctx.fillStyle=c;ctx.fillRect(a*P,(b+bob)*P,w*P,h*P);};
  ctx.fillStyle="rgba(0,0,0,0.25)";ctx.beginPath();ctx.ellipse(3.5*P,6*P,10,3,0,0,Math.PI*2);ctx.fill();
  R("#d49aa8",-1,4,1,1);R("#d49aa8",-2,3.4,1,1);R("#d49aa8",-3,3,1,1);              // tail
  R("#585868",1,3,5,3);R("#8a8a9c",1,2,5,3);R("#b8b8cc",1,2,3,1);R("#b8b8cc",1,3,1,1);  // body
  R("#8a8a9c",4,2,3,3);R("#b8b8cc",4,2,2,1);R("#585868",5,4,2,1);                          // head
  R("#ffb0b8",4,0.6,2,2);R("#8a8a9c",4,0.6,1,2);R("#ffd0d6",5,1,1,1);                      // ear
  R("#101018",5,3,1,1);R("#ffb0b8",7,3.4,1,1);                                            // eye, nose
  R("#3c3c4c",2,6-st*0,1,1);R("#3c3c4c",4,6,1,1);R("#3c3c4c",st?5:2,6,1,1);                // feet
  ctx.restore();
}

function drawHuman(ctx,x,y,frame){
  ctx.save();ctx.translate(x,y);
  const bob=Math.sin(frame*0.06)*1;
  const R=(c,a,b,w,h)=>{ctx.fillStyle=c;ctx.fillRect(a*P,(b+bob)*P,w*P,h*P);};
  ctx.fillStyle="rgba(0,0,0,0.25)";ctx.beginPath();ctx.ellipse(5*P,13.3*P,14,4.5,0,0,Math.PI*2);ctx.fill();
  R("#1c2836",2,9,2,3);R("#2c3e50",2,9,1,3);R("#1c2836",6,9,2,3);R("#2c3e50",6,9,1,3);   // legs
  R("#101820",2,12,2,1);R("#101820",6,12,2,1);R("#3a4a5a",2,12,1,1);R("#3a4a5a",6,12,1,1); // shoes
  R("#2a78b0",2,4,6,5);R("#4aa0e0",2,4,2,4);R("#1e5a86",7,4,1,5);R("#1e5a86",2,8,6,1);      // hoodie
  R("#f5cba7",1,4,1,4);R("#d9a883",1,4,1,4);R("#2a78b0",1,4,2,3);R("#f5cba7",1,7,1,1);R("#1e5a86",8,4,1,3);R("#f5cba7",8,7,1,1); // arms
  R("#f5cba7",3,0,4,4);R("#fde0c6",3,0,2,2);R("#d9a883",6,1,1,3);R("#d9a883",3,3,4,1);      // head
  R("#e67e22",2,-1,6,2);R("#f39c4a",2,-1,3,1);R("#b05a10",7,0,1,2);R("#e67e22",2,1,1,2);   // hair
  R("#2a1a10",4,2,1,1);R("#2a1a10",6,2,1,1);
  ctx.restore();
}

/*_bossstyle*/function drawDiablo(ctx,x,y,frame,hp=10){
  ctx.save();ctx.translate(x,y);
  const pulse=Math.sin(frame*0.08)*0.3,flap=Math.sin(frame*0.05),rage=1-Math.max(0,Math.min(10,hp))/10;
  const R=(c,a,b,w,h)=>{ctx.fillStyle=c;ctx.fillRect(a*P,b*P,w*P,h*P);};
  ctx.fillStyle="rgba(0,0,0,0.32)";ctx.beginPath();ctx.ellipse(2*P,14*P,17*P,4.6*P,0,0,Math.PI*2);ctx.fill();
  ctx.save();ctx.globalCompositeOperation="lighter";
  for(let i=0;i<4;i++){ctx.fillStyle="rgba(200,20,0,"+(0.035+0.012*rage*4)+")";ctx.beginPath();ctx.ellipse(0,13.5*P,(24-i*4)*P,(6.5-i*1)*P,0,0,Math.PI*2);ctx.fill();}
  const g=ctx.createRadialGradient(0,0,0,0,0,50);g.addColorStop(0,"rgba(220,20,0,"+(0.26+rage*0.2)+")");g.addColorStop(1,"rgba(200,0,0,0)");
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(0,0,50,0,Math.PI*2);ctx.fill();ctx.restore();
  ctx.globalAlpha=Math.min(1,0.92+pulse*0.25);
  const wing=(s,fill,bone)=>{
    const wy=(-20+flap*3)*P;
    ctx.fillStyle=fill;ctx.beginPath();ctx.moveTo(s*9*P,-2*P);ctx.lineTo(s*30*P,wy);
    ctx.quadraticCurveTo(s*25*P,wy*0.2,s*27*P,-4*P);ctx.quadraticCurveTo(s*21*P,-1*P,s*21*P,2*P);
    ctx.quadraticCurveTo(s*16*P,3*P,s*14*P,6*P);ctx.quadraticCurveTo(s*11*P,5*P,s*9*P,8*P);ctx.closePath();ctx.fill();
    ctx.strokeStyle=bone;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(s*9*P,-2*P);ctx.lineTo(s*30*P,wy);ctx.stroke();
    ctx.lineWidth=1.5;ctx.strokeStyle="rgba(120,20,20,0.9)";
    [[27,-4],[21,2],[14,6]].forEach(q=>{ctx.beginPath();ctx.moveTo(s*9*P,-2*P);ctx.lineTo(s*q[0]*P,q[1]*P);ctx.stroke();});
  };
  wing(-1,"#4a0a0a","#a03020");wing(1,"#2a0505","#6a1a14");
  R("#0b0000",-10,-5,20,15);R("#230303",-9,-5,17,13);R("#420909",-9,-5,6,11);R("#5a1010",-9,-5,2,6);R("#100000",5,-4,5,13);
  R("#0b0000",-9,8,18,2);
  const cr=0.45+0.35*rage+0.15*Math.sin(frame*0.1);
  ctx.save();ctx.globalCompositeOperation="lighter";
  [[-5,-3,3,1],[-3,-2,1,3],[0,-1,1,5],[1,3,4,1],[-6,3,1,4],[3,-3,1,3],[-2,6,5,1]].forEach(q=>{ctx.fillStyle="rgba(255,"+(70+rage*110|0)+",0,"+cr+")";ctx.fillRect(q[0]*P,q[1]*P,q[2]*P,q[3]*P);});
  ctx.fillStyle="rgba(255,120,0,"+(0.10+0.18*rage)+")";ctx.beginPath();ctx.arc(0,2.5*P,6*P,0,Math.PI*2);ctx.fill();ctx.restore();
  R("#120000",-8,-9,16,10);R("#330606",-8,-9,12,8);R("#561010",-8,-9,6,2);R("#6c1616",-8,-9,2,4);R("#1a0000",4,-8,4,8);
  R("#0a0000",-6,-1,12,2);
  for(let i=0;i<6;i++){ctx.fillStyle="#e8dcc4";ctx.fillRect((-6+i*2)*P,-1*P,P,P);ctx.fillRect((-5+i*2)*P,0,P,P);}
  R("#4a0808",-10,-8,3,3);R("#7a1410",-11,-11,3,4);R("#a02a20",-12,-14,2,4);R("#e07060",-12,-14,1,3);R("#7a1410",-10,-9,1,2);
  R("#2a0404",7,-8,3,3);R("#4a0a08",8,-11,3,4);R("#661a14",10,-14,2,4);R("#8a2a20",10,-14,1,3);
  const ec="rgba(255,"+Math.floor(60+pulse*100+rage*60)+",0,0.95)";
  ctx.save();ctx.globalCompositeOperation="lighter";ctx.fillStyle="rgba(255,60,0,0.18)";
  ctx.beginPath();ctx.arc(-4*P,-4*P,7*P,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(4*P,-4*P,7*P,0,Math.PI*2);ctx.fill();ctx.restore();
  ctx.fillStyle=ec;ctx.beginPath();ctx.arc(-4*P,-4*P,3*P,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(4*P,-4*P,3*P,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#1a0000";ctx.fillRect(-4.4*P,-6*P,0.9*P,4*P);ctx.fillRect(3.6*P,-6*P,0.9*P,4*P);
  ctx.fillStyle="rgba(255,255,255,0.8)";ctx.fillRect(-6*P,-5.5*P,P,P*0.8);ctx.fillRect(2*P,-5.5*P,P,P*0.8);
  ctx.fillStyle="#0a0000";ctx.fillRect(-7*P,-8*P,6*P,1.2*P);ctx.fillRect(1*P,-8*P,6*P,1.2*P);
  [-9,-3,3,7].forEach(cx=>{R("#0b0000",cx,10,2,2);R("#d8c8b0",cx,12,1,1);});
  ctx.save();ctx.globalCompositeOperation="lighter";
  for(let i=0;i<8;i++){const lf=((frame*(0.35+i*0.04)+i*37)%100)/100,ex=(-14+i*4+Math.sin(frame*0.05+i)*3)*P,ey=(10-lf*26)*P;
    ctx.fillStyle="rgba(255,"+(120+i*10)+",30,"+(0.9*Math.sin(lf*Math.PI))+")";ctx.fillRect(ex,ey,3,3);}
  ctx.restore();
  ctx.globalAlpha=0.9;
  ctx.fillStyle="rgba(0,0,0,0.6)";ctx.fillRect(-20*P,18*P,40*P,5);
  ctx.fillStyle="#ff2222";ctx.fillRect(-20*P,18*P,40*P*(hp/10),5);
  ctx.fillStyle="#ff9a8a";ctx.fillRect(-20*P,18*P,40*P*(hp/10),1.5);
  ctx.restore();
}
// ─── Laser ───────────────────────────────────────────────────────────────────
function drawLaser(ctx,x,y,trail,frame){
  trail.forEach((t,i)=>{
    const a=(i/trail.length)*0.5,r=(i/trail.length)*5+1;
    ctx.beginPath();ctx.arc(t.x,t.y,r,0,Math.PI*2);
    ctx.fillStyle=`rgba(255,40,40,${a})`;ctx.fill();
  });
  const g=ctx.createRadialGradient(x,y,0,x,y,18);
  g.addColorStop(0,"rgba(255,80,80,0.55)");g.addColorStop(1,"rgba(255,0,0,0)");
  ctx.beginPath();ctx.arc(x,y,18,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
  ctx.beginPath();ctx.arc(x,y,5,0,Math.PI*2);ctx.fillStyle="rgba(255,60,60,0.85)";ctx.fill();
  ctx.beginPath();ctx.arc(x,y,2.5,0,Math.PI*2);ctx.fillStyle="#fff";ctx.fill();
  const s=1+Math.sin(frame*0.3)*0.5;
  ctx.fillStyle="rgba(255,180,180,0.85)";
  ctx.fillRect(x-8*s,y-1,5*s,2);ctx.fillRect(x+4*s,y-1,5*s,2);
  ctx.fillRect(x-1,y-8*s,2,5*s);ctx.fillRect(x-1,y+4*s,2,5*s);
}

// ─── Bubble ───────────────────────────────────────────────────────────────────
function rrect(ctx,x,y,w,h,r){
  ctx.beginPath();
  ctx.moveTo(x+r,y);ctx.lineTo(x+w-r,y);ctx.quadraticCurveTo(x+w,y,x+w,y+r);
  ctx.lineTo(x+w,y+h-r);ctx.quadraticCurveTo(x+w,y+h,x+w-r,y+h);
  ctx.lineTo(x+r,y+h);ctx.quadraticCurveTo(x,y+h,x,y+h-r);
  ctx.lineTo(x,y+r);ctx.quadraticCurveTo(x,y,x+r,y);
  ctx.closePath();
}
function drawBubble(ctx,cat,p){
  if(cat.revealAlpha<=0||!cat.confessions.length)return;
  const text=cat.confessions[cat.confessions.length-1];
  const cx=cat.x+5.5*p,cy=cat.y-4;
  const isPatates=cat.sysType==="patates";
  const accent=isPatates?"#ffaa44":"#ff4444";
  const textCol=isPatates?"#ffd9a0":"#ff8888";
  ctx.save();ctx.globalAlpha=cat.revealAlpha*(cat.idle?0.35:1);
  ctx.font=`${Math.max(7,p*1.8)}px ${ff}`;
  const tw=ctx.measureText(text).width,pad=10,bh=26,bw=tw+pad*2;
  const bx=cx-bw/2,by=cy-bh-12;
  ctx.fillStyle="rgba(0,0,0,0.30)";rrect(ctx,bx+1,by+4,bw,bh,9);ctx.fill();ctx.strokeStyle=accent;ctx.globalAlpha*=0.14;ctx.lineWidth=6;rrect(ctx,bx,by,bw,bh,9);ctx.stroke();ctx.globalAlpha/=0.14;
  ctx.fillStyle="rgba(22,16,30,0.95)";ctx.strokeStyle=accent;ctx.lineWidth=1.2;
  rrect(ctx,bx,by,bw,bh,9);ctx.fill();ctx.stroke();ctx.fillStyle="rgba(255,255,255,0.06)";rrect(ctx,bx+2,by+2,bw-4,bh/2-2,7);ctx.fill();
  ctx.beginPath();ctx.moveTo(cx-5,by+bh);ctx.lineTo(cx,by+bh+10);ctx.lineTo(cx+5,by+bh);
  ctx.fillStyle="rgba(22,16,30,0.95)";ctx.fill();
  ctx.beginPath();ctx.moveTo(cx-5,by+bh);ctx.lineTo(cx,by+bh+10);ctx.lineTo(cx+5,by+bh);
  ctx.strokeStyle=accent;ctx.lineWidth=1.5;ctx.stroke();
  ctx.fillStyle=textCol;ctx.fillText(text,bx+pad,by+bh-8);
  ctx.restore();
}

// ─── Stars ────────────────────────────────────────────────────────────────────
function genStars(count=300){
  return Array.from({length:count},()=>({
    x:Math.random()*WORLD_W, y:Math.random()*WORLD_H,
    r:Math.random()*1.4+0.2, a:Math.random()*0.5+0.15,
    speed:Math.random()*0.02+0.005,
  }));
}

// ─── World object generator ───────────────────────────────────────────────────
const NPC_CONFESSIONS=[
  "I still sleep w lights on","I talk to myself a lot","I google my own name",
  "I pretend I'm in a movie","I cry at commercials","I eat cereal at 3am",
  "I rehearse arguments","I fake laugh constantly","I'm scared of silence",
  "I miss someone I shouldn't","I lied about being ok","I still check their profile",
];

// ── Spawn rates (max alive at once) ──────────────────────────────────────────
const SPAWN_LIMITS = { ufo:2, fossil:3, wildcat:3, mouse:5, human:1, diablo:1 };

// ── Secret Rooms ─────────────────────────────────────────────────────────────
// fixed positions per epoch so all players share them
function getSecretRooms(){
  const rooms=[];
  const seed=getEpoch()+(WORLD_ID==="malkuth"?0:hashStr(WORLD_ID)%997);
  // deterministic positions based on session seed
  for(let i=0;i<8;i++){
    const angle=(seed*7+i*137.5)%360*(Math.PI/180);
    const dist=1500+((seed*13+i*97)%3000);
    rooms.push({
      x:WORLD_W/2+Math.cos(angle)*dist,
      y:WORLD_H/2+Math.sin(angle)*dist,
      radius:80,
      confession:NPC_CONFESSIONS[(seed*3+i*7)%NPC_CONFESSIONS.length],
    });
  }
  return rooms;
}
let _srEpoch=null,_srCache=[];function secretRooms(){const e=getEpoch()+"|"+WORLD_ID;if(e!==_srEpoch){_srEpoch=e;_srCache=getSecretRooms();}return _srCache;}

// ── Confession Wall ───────────────────────────────────────────────────────────
const WALL_X = 5000; // center of world
const WALL_Y = 1800; // north of spawn
const WALL_W = 600;
const WALL_H = 300;
// shared wall confessions (synced via Ably)
const wallConfessions = []; // {text, x, y, alpha, id}
function addToWall(text){
  if(wallConfessions.length>=20) wallConfessions.shift();
  wallConfessions.push({
    text: text.slice(0,28),
    x: 20+Math.random()*(WALL_W-160),
    y: 30+Math.random()*(WALL_H-50),
    alpha: 0,
    id: Date.now()+"_"+Math.random().toString(36).slice(2,6),
  });
}
const SPAWN_INTERVALS = { ufo:30, fossil:45, wildcat:20, mouse:15, human:60, diablo:180 }; // seconds

function spawnObj(type, existingObjs, rng, slot){
  const R=rng||Math.random;
  const margin=500;
  const rx=()=>margin+R()*(WORLD_W-margin*2);
  const ry=()=>margin+R()*(WORLD_H-margin*2);
  const count=existingObjs.filter(o=>o.type===type).length;
  if(count>=SPAWN_LIMITS[type]) return null;
  const id=(slot!=null)?`${type}_${getEpoch()}_${slot}`:`${type}_${Date.now()}_${Math.random().toString(36).slice(2,6)}`;
  if(type==="ufo") return{
    type:"ufo",id,x:rx(),y:ry(),
    confession:NPC_CONFESSIONS[Math.floor(R()*NPC_CONFESSIONS.length)],
    vx:(R()-0.5)*0.4,vy:(R()-0.5)*0.15,
    frame:0,hitCount:0,active:true,
  };
  if(type==="fossil") return{
    type:"fossil",id,x:rx(),y:ry(),
    confession:NPC_CONFESSIONS[Math.floor(R()*NPC_CONFESSIONS.length)],
    revealed:false,sitTimer:0,frame:0,
  };
  if(type==="wildcat"){
    const palId=Math.floor(R()*PALETTES.length);
    return{
      type:"wildcat",id,x:rx(),y:ry(),
      pal:{...PALETTES[palId]},flip:R()>0.5,
      vx:(R()-0.5)*1.5,vy:(R()-0.5)*1.5,
      frame:Math.floor(R()*200),
      wanderAngle:R()*Math.PI*2,
      wanderTimer:Math.floor(R()*120),
    };
  }
  if(type==="mouse") return{
    type:"mouse",id,x:rx(),y:ry(),flip:R()>0.5,
    vx:(R()-0.5)*2,vy:(R()-0.5)*2,
    frame:Math.floor(R()*200),
    wanderAngle:R()*Math.PI*2,
    wanderTimer:Math.floor(R()*60),
    alive:true,
  };
  if(type==="human") return{
    type:"human",id,x:rx(),y:ry(),
    vx:(R()-0.5)*0.5,vy:0,
    frame:Math.floor(R()*200),
    wanderAngle:R()*Math.PI*2,
    wanderTimer:200+Math.floor(R()*300),
    dropTimer:600,// drop confession every 600 frames ~10s
    breadcrumbs:[],
  };
  if(type==="diablo") return{
    type:"diablo",id,
    x:WORLD_W/2+R()*2000-1000,
    y:WORLD_H/2+R()*2000-1000,
    vx:0.2,vy:0.1,frame:0,
    wanderAngle:R()*Math.PI*2,
    wanderTimer:300,
    hp:10,// needs 10 laser hits to defeat
    hitCooldown:0,
  };
  return null;
}

function generateWorldObjects(){
  const objs=[];
  ["ufo","fossil","wildcat","mouse","human","diablo"].forEach(type=>{
    const obj=spawnObj(type,objs,worldRng("init:"+type),0);
    if(obj)objs.push(obj);
  });
  return objs;
}

// ─── Cat factory ──────────────────────────────────────────────────────────────
/*_recap*/
const RECAP={e:-1,t0:0,mice:0,hops:0,words:0,hits:0,purr:0,peak:0,w:{}};
function recapStart(){let d=null;try{d=JSON.parse(localStorage.getItem("fikfuk_r")||"null");}catch(e){}
  const ep=getEpoch();if(d&&d.e===ep){Object.assign(RECAP,d);}else{Object.assign(RECAP,{e:ep,t0:Date.now(),rides:0,singed:0,sunup:0,fed:0,embers:0,dashes:0,pages:0,lit:0,mice:0,hops:0,words:0,hits:0,purr:0,peak:0,w:{}});}
  RECAP.w[WORLD_ID]=1;}
function recapSave(){try{localStorage.setItem("fikfuk_r",JSON.stringify(RECAP));}catch(e){}}
function recapFmt(ms){const m=Math.max(1,Math.round(ms/60000));return m<60?m+"m":Math.floor(m/60)+"h "+(m%60)+"m";}
function renderRecap(d){
  const W=540,H=960,cv=document.createElement("canvas");cv.width=W;cv.height=H;const ctx=cv.getContext("2d");
  ctx.imageSmoothingEnabled=false;
  const w=WORLDS[d.world]||WORLDS.malkuth;
  try{ctx.fillStyle=w.sky[0];ctx.fillRect(0,0,W,H);drawSky(ctx,W,H,{x:5000,y:5000},0,d.world,"#0B0B18",true);}catch(e){}
  let g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,"rgba(0,0,0,0.55)");g.addColorStop(0.35,"rgba(0,0,0,0.05)");g.addColorStop(0.6,"rgba(0,0,0,0.45)");g.addColorStop(1,"rgba(0,0,0,0.85)");
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  ctx.textAlign="center";ctx.textBaseline="alphabetic";
  ctx.fillStyle="#ff4444";ctx.font="22px "+ff;ctx.fillText("fikfuk.wtf",W/2,80);
  ctx.fillStyle="rgba(255,255,255,0.55)";ctx.font="12px "+ff;ctx.fillText(w.name,W/2,114);
  // glow + ground under the cat
  const p=16,cx=W/2,cy=360;
  ctx.save();ctx.globalCompositeOperation="lighter";
  g=ctx.createRadialGradient(cx,cy+70,10,cx,cy+70,230);g.addColorStop(0,"rgba(255,120,120,0.30)");g.addColorStop(1,"rgba(255,120,120,0)");
  ctx.fillStyle=g;ctx.fillRect(0,cy-200,W,520);ctx.restore();
  ctx.fillStyle="rgba(0,0,0,0.45)";ctx.beginPath();ctx.ellipse(cx,cy+11*p,6.4*p,1.4*p,0,0,Math.PI*2);ctx.fill();
  drawCat(ctx,cx-4.5*p,cy-p,p,40,d.pal,d.flip,"sit",false,false,false,false);
  ctx.fillStyle="#fff";ctx.font="26px "+ff;ctx.fillText(d.name,W/2,cy+11*p+64);
  const rows=[["stayed",recapFmt(d.lived)]];
  if(d.stats.rides)rows.push(["flames ridden",String(d.stats.rides)]);if(d.stats.singed>=2)rows.push(["times singed",String(d.stats.singed)]);if(d.stats.sunup)rows.push(["raised the sun","yes"]);if(d.stats.fed)rows.push(["embers fed",String(d.stats.fed)]);if(d.stats.pages)rows.push(["pages dug up",String(d.stats.pages)]);if(d.stats.lit)rows.push(["lit the beacon","yes"]);if(d.stats.mice)rows.push(["mice caught",String(d.stats.mice)]);
  if(d.stats.dashes>=3)rows.push(["dashes",String(d.stats.dashes)]);if(d.stats.hops)rows.push(["portals taken",String(d.stats.hops)]);
  if(d.stats.purr>=30)rows.push(["purring together",recapFmt(d.stats.purr*1000)]);
  if(d.stats.words)rows.push(["whispers sent",String(d.stats.words)]);
  if(d.stats.hits)rows.push(["boss hits",String(d.stats.hits)]);
  if(d.stats.peak>1)rows.push(["most cats at once",String(d.stats.peak)]);
  let y=cy+11*p+128;
  rows.slice(0,5).forEach(r=>{ctx.textAlign="left";ctx.fillStyle="rgba(255,255,255,0.5)";ctx.font="12px "+ff;ctx.fillText(r[0],64,y);
    ctx.textAlign="right";ctx.fillStyle="#fff";ctx.font="16px "+ff;ctx.fillText(r[1],W-64,y);
    ctx.fillStyle="rgba(255,255,255,0.08)";ctx.fillRect(64,y+14,W-128,1);y+=42;});
  ctx.textAlign="center";ctx.fillStyle="rgba(255,100,100,0.85)";ctx.font="13px "+ff;ctx.fillText("this world is gone",W/2,H-62);
  ctx.fillStyle="rgba(255,255,255,0.3)";ctx.font="9px "+ff;ctx.fillText("resets every 3 hours",W/2,H-34);
  return cv.toDataURL("image/png");
}
function recapSnap(m){
  const stats={mice:RECAP.mice,hops:RECAP.hops,words:RECAP.words,hits:RECAP.hits,purr:RECAP.purr,peak:RECAP.peak,lit:RECAP.lit||0,pages:RECAP.pages||0,dashes:RECAP.dashes||0,fed:RECAP.fed||0,sunup:RECAP.sunup||0,rides:RECAP.rides||0,singed:RECAP.singed||0};
  const d={name:m.name,pal:{...m.pal,_name:""},flip:!!m.flip,world:WORLD_ID,stats,lived:Date.now()-(RECAP.t0||Date.now())};
  try{d.img=renderRecap(d);}catch(e){d.img=null;}
  try{localStorage.removeItem("fikfuk_r");}catch(e){}
  return d.img?d:null;
}
function recapDownload(r){const a=document.createElement("a");a.href=r.img;a.download="fikfuk-"+(r.name||"cat").replace(/[^a-z0-9]+/gi,"_")+".png";document.body.appendChild(a);a.click();a.remove();}
async function recapShare(r){try{const b=await (await fetch(r.img)).blob();const f=new File([b],"fikfuk.png",{type:"image/png"});
  if(navigator.canShare&&navigator.canShare({files:[f]})){await navigator.share({files:[f],title:"fikfuk.wtf",text:"my cat's life in fikfuk.wtf"});return;}}catch(e){if(e&&e.name==="AbortError")return;}
  recapDownload(r);}
/*_beacon*/
const BEACONS={};
function beaconGet(w){
  const e=getEpoch();let b=BEACONS[w];
  if(!b||b.e!==e){
    const r=mulberry32(hashStr(e+"|"+w+"|beacon"));let x=5000,y=3000;
    for(let i=0;i<14;i++){x=1500+r()*7000;y=1500+r()*7000;let ok=Math.hypot(x-5000,y-1800)>700&&Math.hypot(x-5000,y-5000)>600;
      const pt=PORTALS[w]||{};for(const k in pt){if(Math.hypot(x-pt[k][0],y-pt[k][1])<650)ok=false;}if(ok)break;}
    b=BEACONS[w]={e,x,y,charge:0,lit:false,n:0,need:2,flash:0,sil:0,gap:25};
  }
  return b;
}
function beaconLight(b,s,pub){
  if(b.lit)return;b.lit=true;b.charge=1;b.flash=50;b.sil=0;b.gap=20+Math.floor(Math.random()*30);
  try{FKAudio.beacon();}catch(e){}
  const me=s.cats.find(c=>c.id===s.myId);if(me&&Math.hypot(me.x-b.x,me.y-b.y)<500)RECAP.lit=(RECAP.lit||0)+1;
  if(pub)pub({e:b.e,w:WORLD_ID});
}
function beaconTick(s,pub){
  const b=beaconGet(WORLD_ID);
  const real=s.cats.filter(c=>!c.isSys&&!c.isGhost&&!c.idle);
  b.need=real.length>=6?3:2;
  b.n=real.filter(c=>Math.hypot(c.x-b.x,(c.y-b.y)*2)<170).length;
  if(b.flash>0)b.flash--;
  if(b.lit){
    if(s.frame%60===0){b.sil++;if(b.sil>=b.gap){b.sil=0;b.gap=25+Math.floor(Math.random()*30);if(pub)pub({e:b.e,w:WORLD_ID});}}
  }else{
    if(b.n>=b.need)b.charge=Math.min(1,b.charge+1/480);else b.charge=Math.max(0,b.charge-1/1200);
    if(b.charge>=1)beaconLight(b,s,pub);
  }
}
function drawBeacon(ctx,sx,sy,b,f){
  const lit=b.lit,k=lit?1:b.charge,pulse=0.5+0.5*Math.sin(f*0.05);
  const el=(x,y,rx,ry,col)=>{ctx.fillStyle=col;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.fill();};
  ctx.save();
  ctx.lineWidth=2;ctx.strokeStyle=lit?"rgba(255,225,140,0.35)":"rgba(160,190,255,0.22)";ctx.setLineDash([6,8]);
  ctx.beginPath();ctx.ellipse(sx,sy,170,85,0,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);
  if(!lit&&b.charge>0){ctx.strokeStyle="rgba(255,215,120,0.9)";ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(sx,sy,170,85,0,-Math.PI/2,-Math.PI/2+b.charge*Math.PI*2);ctx.stroke();}
  ctx.restore();
  el(sx,sy+6,36,13,"rgba(0,0,0,0.4)");el(sx,sy+2,31,10,"#2a2c3c");el(sx,sy-2,24,8,"#3a3d52");el(sx,sy-6,17,6,"#4c5070");
  ctx.fillStyle="#34364a";ctx.fillRect(sx-9,sy-36,18,30);ctx.fillStyle="#474b6c";ctx.fillRect(sx-9,sy-36,6,30);ctx.fillStyle="#232536";ctx.fillRect(sx+4,sy-36,5,30);
  const cy=sy-62+Math.sin(f*0.04)*3,r=Math.round(120+135*k),g=Math.round(150+75*k),bl=Math.round(220-80*k);
  ctx.save();ctx.globalCompositeOperation="lighter";
  const rad=50+70*k,gr=ctx.createRadialGradient(sx,cy,4,sx,cy,rad);gr.addColorStop(0,`rgba(${r},${g},${bl},${0.10+0.28*k+0.08*pulse})`);gr.addColorStop(1,`rgba(${r},${g},${bl},0)`);
  if(!LITE){ctx.fillStyle=gr;ctx.fillRect(sx-rad,cy-rad,rad*2,rad*2);}
  if(lit){
    const top=Math.min(cy-1600,-200);
    (LITE?[[12,0.24]]:[[50,0.07],[34,0.09],[20,0.13],[9,0.22]]).forEach(([hw,al])=>{const y0=cy+26,bg=ctx.createLinearGradient(0,y0,0,top);bg.addColorStop(0,"rgba(255,220,140,0)");bg.addColorStop(Math.min(0.2,50/(y0-top)),`rgba(255,220,140,${al})`);bg.addColorStop(1,"rgba(255,220,140,0)");ctx.fillStyle=bg;ctx.fillRect(sx-hw,top,hw*2,y0-top);});
    ctx.fillStyle="rgba(255,240,190,0.8)";for(let i=0;i<9;i++){const my=cy-((f*0.9+i*83)%700);ctx.fillRect(Math.round(sx+Math.sin(i*7+f*0.02)*22),Math.round(my),3,3);}
    if(b.flash>0){ctx.strokeStyle=`rgba(255,235,170,${b.flash/50*0.6})`;ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(sx,sy,(50-b.flash)*7+20,(50-b.flash)*3.5+10,0,0,Math.PI*2);ctx.stroke();}
  }
  ctx.restore();
  ctx.fillStyle=`rgb(${r},${g},${bl})`;ctx.beginPath();ctx.moveTo(sx,cy-20);ctx.lineTo(sx+12,cy);ctx.lineTo(sx,cy+20);ctx.lineTo(sx-12,cy);ctx.closePath();ctx.fill();
  ctx.fillStyle=`rgb(${Math.min(255,r+70)},${Math.min(255,g+60)},${Math.min(255,bl+50)})`;ctx.beginPath();ctx.moveTo(sx,cy-20);ctx.lineTo(sx,cy+20);ctx.lineTo(sx-12,cy);ctx.closePath();ctx.fill();
  ctx.fillStyle="rgba(255,255,255,0.85)";ctx.beginPath();ctx.moveTo(sx-2,cy-9);ctx.lineTo(sx+2,cy-5);ctx.lineTo(sx-2,cy-1);ctx.closePath();ctx.fill();
  if(!lit&&(b.n>0||b.charge>0)){ctx.font="8px "+ff;ctx.textAlign="center";ctx.fillStyle="rgba(255,255,255,0.7)";ctx.fillText(b.n+"/"+b.need,sx,sy+30);}
}
/*_shard*/
let _shE=-1,_shL=[];const SHLINKS=[];
function shardList(){
  if(WORLD_ID!=="yesod")return[];
  const e=getEpoch();
  if(_shE!==e){_shE=e;_shL=[];const r=mulberry32(hashStr(e+"|shards"));const pt=PORTALS.yesod||{};
    for(let i=0;i<300&&_shL.length<7;i++){const x=1200+r()*7600,y=1200+r()*7600;let ok=true;
      for(const k in pt)if(Math.hypot(x-pt[k][0],y-pt[k][1])<500)ok=false;
      _shL.forEach(o=>{if(Math.hypot(x-o.x,y-o.y)<1000)ok=false;});
      if(ok)_shL.push({x,y,h:70+Math.floor(r()*40),flash:0});}}
  return _shL;
}
function shardRelay(x,y,fromId,fire){
  const L=shardList(),cx=x+16.5,cy=y+15;let a=null,ad=1e9;
  L.forEach(o=>{const d=Math.hypot(o.x-cx,o.y-cy);if(d<330&&d<ad){a=o;ad=d;}});
  if(!a)return;a.flash=40;
  L.filter(o=>o!==a).map(o=>({o,d:Math.hypot(o.x-a.x,o.y-a.y)})).filter(t=>t.d<2600).sort((p,q)=>p.d-q.d).slice(0,2).forEach(t=>{
    SHLINKS.push({a,b:t.o,life:50});
    setTimeout(()=>{if(WORLD_ID!=="yesod")return;t.o.flash=40;fire(t.o.x-16.5,t.o.y-15,fromId,true);},350+t.d*0.35);});
}
function drawShards(ctx,cam,W,H,f){
  const L=shardList();if(!L.length)return;
  for(let i=SHLINKS.length-1;i>=0;i--){if(--SHLINKS[i].life<=0)SHLINKS.splice(i,1);}
  ctx.save();ctx.globalCompositeOperation="lighter";
  SHLINKS.forEach(l=>{const al=l.life/50*0.55,ax=l.a.x-cam.x,ay=l.a.y-l.a.h*0.6-cam.y,bx=l.b.x-cam.x,by=l.b.y-l.b.h*0.6-cam.y;
    [["255,120,200",-3],["120,230,255",0],["255,230,140",3]].forEach(([c,o])=>{ctx.strokeStyle=`rgba(${c},${al})`;ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(ax,ay+o);ctx.lineTo(bx,by+o);ctx.stroke();});});
  ctx.restore();
  const poly=(pts,col)=>{ctx.fillStyle=col;ctx.beginPath();ctx.moveTo(pts[0][0],pts[0][1]);for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]);ctx.closePath();ctx.fill();};
  L.forEach(o=>{
    const sx=Math.round(o.x-cam.x),sy=Math.round(o.y-cam.y);if(sx<-140||sx>W+140||sy<-20||sy-o.h>H)return;
    const fl=o.flash/40;if(o.flash>0)o.flash--;
    ctx.fillStyle="rgba(0,0,0,0.4)";ctx.beginPath();ctx.ellipse(sx+4,sy+4,26,8,0,0,Math.PI*2);ctx.fill();
    const one=(ox,oy,h,k)=>{const x=sx+ox,y=sy+oy;
      poly([[x-12*k,y],[x-1*k,y],[x+1*k,y-h],[x-9*k,y-h*0.7]],"#b9aef0");
      poly([[x-1*k,y],[x+12*k,y],[x+8*k,y-h*0.75],[x+1*k,y-h]],"#7566c0");
      ctx.fillStyle="rgba(240,235,255,0.9)";ctx.fillRect(Math.round(x-9*k),Math.round(y-h*0.7),2,Math.round(h*0.7));};
    one(20,3,o.h*0.55,0.8);one(0,0,o.h,1);
    ctx.save();ctx.globalCompositeOperation="lighter";
    const gy=sy-o.h*0.5,rad=60+50*fl,gr=ctx.createRadialGradient(sx,gy,4,sx,gy,rad);gr.addColorStop(0,`rgba(190,170,255,${0.10+0.40*fl+0.04*Math.sin(f*0.05+o.x)})`);gr.addColorStop(1,"rgba(190,170,255,0)");
    if(!LITE){ctx.fillStyle=gr;ctx.fillRect(sx-rad,gy-rad,rad*2,rad*2);}
    if(fl>0){[["255,120,200",-0.5],["120,230,255",-0.25],["255,230,140",0]].forEach(([c,a])=>{ctx.strokeStyle=`rgba(${c},${fl*0.7})`;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(sx+1,sy-o.h);ctx.lineTo(sx+1+Math.cos(a-0.3)*70*fl,sy-o.h+Math.sin(a-0.3)*70*fl);ctx.stroke();});}
    ctx.fillStyle="rgba(255,255,255,0.8)";const sp=(f+o.x)%90;if(sp<6)ctx.fillRect(sx-4+Math.round((o.x*7)%9),sy-o.h*0.8+sp,2,2);
    ctx.restore();});
}
/*_pages*/
const PAGE_LINES=["the archive remembers what you forgot","page 14: nobody read page 13","roots grow toward the sound of purring","a cat sat here for three hours","the index is missing, on purpose","if you can read this, stay","dig where the quiet is","every wipe is a footnote","someone loved this world","the oldest cat was never named","read twice, purr once","the last page is blank. write it","this page was buried by a friend","ink dries, whiskers do not","chapter 0: the first nap","the library has no walls"];
let _pgE=-1,_pgL=[];
function pagesList(){
  if(WORLD_ID!=="netzach")return[];
  const e=getEpoch();
  if(_pgE!==e){_pgE=e;_pgL=[];const r=mulberry32(hashStr(e+"|pages"));const pt=PORTALS.netzach||{};
    for(let i=0;i<400&&_pgL.length<8;i++){const x=1200+r()*7600,y=1200+r()*7600;let ok=Math.hypot(x-5000,y-5000)>500;
      for(const k in pt)if(Math.hypot(x-pt[k][0],y-pt[k][1])<500)ok=false;
      _pgL.forEach(o=>{if(Math.hypot(x-o.x,y-o.y)<750)ok=false;});
      if(ok)_pgL.push({x,y,i:_pgL.length,p:0,open:false,line:PAGE_LINES[Math.floor(r()*PAGE_LINES.length)]});}}
  return _pgL;
}
function pageOpen(o,s,pub){
  if(o.open)return;o.open=true;o.p=1;o.t=0;
  try{FKAudio.page();}catch(e){}
  if(pub){const me=s.cats.find(c=>c.id===s.myId);if(me&&Math.hypot(me.x-o.x,(me.y-o.y)*2)<80)RECAP.pages=(RECAP.pages||0)+1;pub({e:getEpoch(),w:"netzach",i:o.i});}
}
function pagesTick(s,pub){
  const L=pagesList();if(!L.length)return;
  const sit=s.cats.filter(c=>!c.isSys&&!c.isGhost&&!c.idle&&c.state==="sit");
  L.forEach(o=>{if(o.open)return;
    const n=sit.filter(c=>Math.hypot(c.x-o.x,(c.y-o.y)*2)<70).length;
    if(n>0)o.p=Math.min(1,o.p+1/360);else o.p=Math.max(0,o.p-1/900);
    if(o.p>=1)pageOpen(o,s,pub);});
}
function drawPages(ctx,cam,W,H,f,s){
  const L=pagesList();if(!L.length)return;
  const me=s.cats.find(c=>c.id===s.myId);
  L.forEach(o=>{
    const sx=Math.round(o.x-cam.x),sy=Math.round(o.y-cam.y);if(sx<-200||sx>W+200||sy<-80||sy>H+120)return;
    const el=(x,y,rx,ry,c)=>{ctx.fillStyle=c;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.fill();};
    if(!o.open){
      el(sx,sy+3,30,10,"rgba(0,0,0,0.35)");el(sx,sy,26,9,"#2a2418");el(sx-3,sy-2,19,6,"#3b3322");el(sx-5,sy-3,10,3,"#4d432d");
      ctx.fillStyle="#d8d2b8";ctx.fillRect(sx+8,sy-9,7,4);ctx.fillStyle="#a9a38a";ctx.fillRect(sx+8,sy-6,7,1);
      if(o.p>0){ctx.strokeStyle="rgba(190,255,170,0.9)";ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(sx,sy,38,19,0,-Math.PI/2,-Math.PI/2+o.p*Math.PI*2);ctx.stroke();
        ctx.fillStyle="#4d432d";for(let i=0;i<4;i++){const a=(f*0.2+i*1.6),h=Math.abs(Math.sin(a))*14;ctx.fillRect(Math.round(sx-14+i*9),Math.round(sy-4-h),3,3);}}
    }else{
      o.t=(o.t||0)+1;const bob=Math.round(Math.sin(f*0.04+o.i)*2),rise=Math.min(1,o.t/40);
      el(sx,sy+3,22,8,"rgba(0,0,0,0.35)");el(sx,sy,18,6,"#3a3d3a");el(sx,sy-2,13,4,"#4c514c");
      const py=sy-8-Math.round(30*rise)+bob;
      ctx.save();ctx.globalCompositeOperation="lighter";const gr=ctx.createRadialGradient(sx,py-10,3,sx,py-10,55);gr.addColorStop(0,"rgba(170,255,170,0.22)");gr.addColorStop(1,"rgba(170,255,170,0)");if(!LITE){ctx.fillStyle=gr;ctx.fillRect(sx-55,py-65,110,110);}ctx.restore();
      ctx.fillStyle="#e8e2c8";ctx.fillRect(sx-11,py-26,22,30);ctx.fillStyle="#c9c3a8";ctx.fillRect(sx+6,py-26,5,30);ctx.fillStyle="#8e8a74";
      for(let i=0;i<5;i++)ctx.fillRect(sx-8,py-21+i*5,i%2?10:14,2);
      if(me&&Math.hypot(me.x-o.x,(me.y-o.y)*2)<150){
        ctx.save();ctx.font="8px "+ff;ctx.textAlign="center";const tw=ctx.measureText(o.line).width+16;
        ctx.fillStyle="rgba(10,20,12,0.82)";ctx.fillRect(Math.round(sx-tw/2),py-62,Math.round(tw),22);ctx.strokeStyle="rgba(170,255,170,0.5)";ctx.lineWidth=1;ctx.strokeRect(Math.round(sx-tw/2)+0.5,py-62+0.5,Math.round(tw)-1,21);
        ctx.fillStyle="rgba(215,255,200,0.95)";ctx.fillText(o.line,sx,py-47);ctx.restore();}
    }
  });
}
/*_wx*/
const WX_LIST={malkuth:["meteors","aurora","rain"],yesod:["drift","aurora","rain"],netzach:["drift","meteors","rain"],hod:["drift","meteors","rain"],tiferet:["aurora","meteors","drift"],gevurah:["meteors","rain","drift"]};
const WX_RAIN={malkuth:"170,200,255",yesod:"205,190,255",netzach:"150,230,190",hod:"235,160,120",tiferet:"255,230,170",gevurah:"255,150,160"};
const WX_AUR={malkuth:["80,255,170","90,160,255"],yesod:["255,140,220","150,200,255"],netzach:["120,255,150","200,255,120"],hod:["255,120,60","255,200,90"],tiferet:["255,210,90","255,160,80"],gevurah:["255,70,90","255,150,90"]};
const WX_DRIFT={malkuth:"255,170,90",yesod:"255,170,220",netzach:"170,255,150",hod:"255,150,70",tiferet:"255,225,140",gevurah:"255,110,100"};
const WX_NAME={meteors:"meteor shower",aurora:"aurora",rain:"rain",drift:{malkuth:"embers",yesod:"petal drift",netzach:"spore drift",hod:"falling embers",tiferet:"golden motes",gevurah:"red sparks"}};
let _wxKey="",_wxEv=null;const WXM=[],WXP=[],WXR=[];let _wxFl=0;
function wxCurrent(){
  const f=typeof window!=="undefined"?window.__wxForce:null;
  if(f)return{type:f,start:Date.now()-60000,end:1e15,a:1,forced:true};
  const now=sharedNow(),slot=Math.floor(now/600000),key=slot+"|"+WORLD_ID;
  if(key!==_wxKey){_wxKey=key;_wxEv=null;const r=mulberry32(hashStr(key+"|wx"));
    if(r()<0.4){const l=WX_LIST[WORLD_ID]||WX_LIST.malkuth,start=slot*600000+Math.floor(r()*480000);_wxEv={type:l[Math.floor(r()*l.length)],start,end:start+90000};}}
  if(!_wxEv||now<_wxEv.start||now>_wxEv.end)return null;
  return{..._wxEv,a:Math.max(0,Math.min(1,(now-_wxEv.start)/6000,(_wxEv.end-now)/6000)),now};
}
function drawWeather(ctx,W,H,f,night){
  const ev=wxCurrent();if(!ev){if(WXM.length)WXM.length=0;if(WXP.length)WXP.length=0;if(WXR.length)WXR.length=0;FKAudio.rain(0);return;}
  const a=ev.a*(night?1:0.55),w=WORLD_ID;
  FKAudio.rain(ev.type==="rain"?ev.a:0);if(LITE)return;
  if(ev.type==="rain"){ctx.fillStyle=`rgba(0,10,30,${0.2*ev.a})`;ctx.fillRect(0,0,W,H);}
  ctx.save();ctx.globalCompositeOperation="lighter";
  if(ev.type==="aurora"){
    const cols=WX_AUR[w]||WX_AUR.malkuth;
    cols.forEach((col,ci)=>{for(let x=0;x<W;x+=6){const k=x*0.012+f*0.012*(ci?1.4:1)+ci*2;
      const top=H*(0.06+0.12*Math.sin(k)+0.06*Math.sin(k*2.3+f*0.01)+ci*0.08),h=H*(0.3+0.1*Math.sin(k*1.7+1));
      const g=ctx.createLinearGradient(0,top,0,top+h);g.addColorStop(0,`rgba(${col},0)`);g.addColorStop(0.3,`rgba(${col},${0.30*a*(0.6+0.4*Math.sin(x*0.05+f*0.02))})`);g.addColorStop(1,`rgba(${col},0)`);
      ctx.fillStyle=g;ctx.fillRect(x,top,6,h);}});
  }else if(ev.type==="meteors"){
    if(Math.random()<0.07*a&&WXM.length<14){WXM.push({x:W*(0.25+Math.random()*0.9),y:-20,vx:-(5+Math.random()*3),vy:2.5+Math.random()*2,l:0});}
    for(let i=WXM.length-1;i>=0;i--){const m=WXM[i];m.x+=m.vx;m.y+=m.vy;m.l++;if(m.y>H*0.8||m.x<-100||m.l>200){WXM.splice(i,1);continue;}
      const tx=m.x-m.vx*14,ty=m.y-m.vy*14,g=ctx.createLinearGradient(m.x,m.y,tx,ty);g.addColorStop(0,`rgba(255,250,230,${0.9*a})`);g.addColorStop(1,"rgba(255,220,160,0)");
      ctx.strokeStyle=g;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(m.x,m.y);ctx.lineTo(tx,ty);ctx.stroke();ctx.fillStyle=`rgba(255,255,255,${a})`;ctx.fillRect(Math.round(m.x)-1,Math.round(m.y)-1,3,3);}
  }else if(ev.type==="rain"){
    const col=WX_RAIN[w]||WX_RAIN.malkuth,k=ev.a*0.8;
    for(let n=0;n<5&&WXR.length<260;n++)WXR.push({x:Math.random()*(W+120),y:-20,v:15+Math.random()*7,l:9+Math.random()*8});
    ctx.lineWidth=2;ctx.strokeStyle=`rgba(${col},${0.75*k})`;ctx.beginPath();
    for(let i=WXR.length-1;i>=0;i--){const d=WXR[i];d.y+=d.v;d.x-=d.v*0.18;if(d.y>H+10){WXR.splice(i,1);continue;}ctx.moveTo(d.x,d.y);ctx.lineTo(d.x+d.l*0.18,d.y-d.l);}
    ctx.stroke();
    if(ev.a>0.9&&_wxFl<=0&&Math.random()<0.0012){_wxFl=14;setTimeout(()=>{try{FKAudio.thunder();}catch(e){}},500+Math.random()*900);}
  }else if(ev.type==="drift"){
    const col=WX_DRIFT[w]||WX_DRIFT.malkuth;
    if(Math.random()<0.8*a&&WXP.length<90)WXP.push({x:Math.random()*W*1.2,y:-10,s:0.6+Math.random()*1.2,ph:Math.random()*6.28,sz:3+Math.floor(Math.random()*3)});
    for(let i=WXP.length-1;i>=0;i--){const p=WXP[i];p.y+=p.s;p.x-=0.5*p.s;p.ph+=0.03;if(p.y>H+10||p.x<-20){WXP.splice(i,1);continue;}
      ctx.fillStyle=`rgba(${col},${0.9*a})`;ctx.fillRect(Math.round(p.x+Math.sin(p.ph)*14),Math.round(p.y),p.sz,p.sz);}
  }
  ctx.restore();
  if(_wxFl>0){ctx.fillStyle=`rgba(220,230,255,${_wxFl/14*0.26})`;ctx.fillRect(0,0,W,H);_wxFl--;}
  const age=ev.forced?(f%600):(ev.now-ev.start)/1000*60;
  if(age<330){const nm=typeof WX_NAME[ev.type]==="object"?WX_NAME[ev.type][w]:WX_NAME[ev.type];ctx.save();ctx.font="8px "+ff;ctx.textAlign="center";ctx.fillStyle=`rgba(255,255,255,${Math.min(0.6,(330-age)/120)*0.9})`;ctx.fillText(nm||"",W/2,H*0.16);ctx.restore();}
}
function drawDashTrail(ctx,cam,s){
  const T=s._dashTr;if(!T||!T.length||LITE)return;
  for(let i=T.length-1;i>=0;i--){const g=T[i];if(--g.life<=0){T.splice(i,1);continue;}
    ctx.save();ctx.globalAlpha=g.life/14*0.42;drawCat(ctx,Math.round(g.x-cam.x),Math.round(g.y-cam.y),P,40,g.pal,g.flip,"run",false,false,false,false);ctx.restore();}
}
/*_lite*/let LITE=false;try{LITE=localStorage.getItem("fikfuk_lite")==="1";}catch(e){}
/*_hod*/
const HOD={e:-1,L:null,carry:0,open:false,sil:0,gap:30,flash:0};const HODL=[];
function hodGet(){
  if(WORLD_ID!=="hod")return null;
  const e=getEpoch();
  if(HOD.e!==e||!HOD.L){HOD.e=e;HOD.carry=0;HOD.open=false;HOD.flash=0;HODL.length=0;
    const r=mulberry32(hashStr(e+"|hod")),pt=PORTALS.hod||{},em=[],br=[];
    const free=(x,y,min,list)=>{for(const k in pt)if(Math.hypot(x-pt[k][0],y-pt[k][1])<500)return false;if(Math.hypot(x-5000,y-5000)<350)return false;return list.every(o=>Math.hypot(x-o.x,y-o.y)>=min);};
    for(let i=0;i<500&&br.length<3;i++){const x=1500+r()*7000,y=1500+r()*7000;if(free(x,y,1600,br))br.push({x,y,i:br.length,fuel:0,need:3,lit:false,flash:0});}
    for(let i=0;i<900&&em.length<24;i++){const x=1000+r()*8000,y=1000+r()*8000;if(free(x,y,260,em)&&br.every(b=>Math.hypot(x-b.x,y-b.y)>200))em.push({x,y,i:em.length,taken:false});}
    HOD.L={em,br};}
  return HOD.L;
}
function hodFuel(b){
  if(b.fuel>=b.need&&!b.lit){b.lit=true;b.flash=40;}
  const L=HOD.L;if(L&&!HOD.open&&L.br.every(x=>x.lit)){HOD.open=true;HOD.flash=60;try{FKAudio.beacon();}catch(x){}}
}
function hodTick(s,pub){
  const L=hodGet();if(!L)return;
  const me=s.cats.find(c=>c.id===s.myId);if(!me||me.idle)return;
  const e=getEpoch();
  L.em.forEach(o=>{if(!o.taken&&Math.hypot(me.x-o.x,me.y-o.y)<32){o.taken=true;HOD.carry++;RECAP.embers=(RECAP.embers||0)+1;try{FKAudio.page();}catch(x){}pub({k:"e",e,i:o.i});}});
  if(HOD.carry>0&&me.state==="sit"&&s.frame%30===0){
    const b=L.br.find(b=>!b.lit&&Math.hypot(me.x-b.x,(me.y-b.y)*2)<110);
    if(b){HOD.carry--;b.fuel++;RECAP.fed=(RECAP.fed||0)+1;try{FKAudio.feed(true);}catch(x){}hodFuel(b);pub({k:"b",e,i:b.i,f:b.fuel});}}
  if(L.br.some(b=>b.fuel>0)&&s.frame%60===0){HOD.sil++;if(HOD.sil>=HOD.gap){HOD.sil=0;HOD.gap=30+Math.floor(Math.random()*30);pub({k:"s",e,f:L.br.map(b=>b.fuel)});}}
}
function drawHod(ctx,cam,W,H,f,s){
  const L=hodGet();if(!L)return;
  const me=s.cats.find(c=>c.id===s.myId);
  L.em.forEach(o=>{if(o.taken)return;const sx=Math.round(o.x-cam.x),sy=Math.round(o.y-cam.y);if(sx<-40||sx>W+40||sy<-40||sy>H+40)return;
    const by=sy+Math.round(Math.sin(f*0.07+o.i)*3);
    if(!LITE){ctx.save();ctx.globalCompositeOperation="lighter";const g=ctx.createRadialGradient(sx,by,1,sx,by,26);g.addColorStop(0,"rgba(255,150,60,0.45)");g.addColorStop(1,"rgba(255,150,60,0)");ctx.fillStyle=g;ctx.fillRect(sx-26,by-26,52,52);ctx.restore();}
    ctx.fillStyle="#ff9a3c";ctx.fillRect(sx-3,by-5,6,10);ctx.fillRect(sx-5,by-3,10,6);ctx.fillStyle="#ffe2a0";ctx.fillRect(sx-2,by-3,4,6);});
  L.br.forEach(b=>{const sx=Math.round(b.x-cam.x),sy=Math.round(b.y-cam.y);if(sx<-220||sx>W+220||sy<-220||sy>H+320)return;
    const k=b.lit?1:b.fuel/b.need,el=(x,y,rx,ry,c)=>{ctx.fillStyle=c;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.fill();};
    el(sx,sy+5,34,11,"rgba(0,0,0,0.4)");
    ctx.fillStyle="#2a2018";ctx.fillRect(sx-16,sy-14,5,18);ctx.fillRect(sx+11,sy-14,5,18);ctx.fillRect(sx-2,sy-10,4,14);
    el(sx,sy-24,24,9,"#3a2c22");el(sx,sy-22,22,7,"#4e3a2c");el(sx,sy-26,18,6,"#1c1410");el(sx,sy-26,14,5,k>0?"#c2461c":"#4a2a20");
    if(k>0){const fl=Math.round(4+k*22+Math.sin(f*0.25+b.i)*2),h2=Math.round(fl*0.8),h3=Math.round(fl*0.5);
      ctx.fillStyle="#ff7a2a";ctx.fillRect(sx-8,sy-28-fl,16,fl);ctx.fillStyle="#ffb347";ctx.fillRect(sx-5,sy-28-h2,10,h2);ctx.fillStyle="#fff1b8";ctx.fillRect(sx-2,sy-28-h3,4,h3);
      if(!LITE){ctx.save();ctx.globalCompositeOperation="lighter";const R=60+120*k,g=ctx.createRadialGradient(sx,sy-34,4,sx,sy-34,R);g.addColorStop(0,`rgba(255,140,50,${0.18+0.22*k})`);g.addColorStop(1,"rgba(255,140,50,0)");ctx.fillStyle=g;ctx.fillRect(sx-R,sy-34-R,R*2,R*2);ctx.restore();}}
    if(b.flash>0)b.flash--;
    if(me&&!b.lit&&Math.hypot(me.x-b.x,(me.y-b.y)*2)<240){ctx.save();ctx.font="8px "+ff;ctx.textAlign="center";ctx.fillStyle="rgba(255,200,150,0.85)";ctx.fillText(b.fuel+"/"+b.need,sx,sy+32);ctx.restore();}});
  if(HOD.carry>0){ctx.save();ctx.font="8px "+ff;ctx.textAlign="center";ctx.fillStyle="rgba(255,170,90,0.9)";ctx.fillText("embers "+HOD.carry,W/2,H-100);ctx.restore();}
  if(HOD.open){
    ctx.fillStyle="rgba(255,120,40,0.05)";ctx.fillRect(0,0,W,H);
    if(Math.random()<(LITE?0.03:0.06)&&HODL.length<(LITE?10:26))HODL.push({x:Math.random()*W,y:H+20,v:0.4+Math.random()*0.5,ph:Math.random()*6.28});
    for(let i=HODL.length-1;i>=0;i--){const l=HODL[i];l.y-=l.v;l.ph+=0.02;if(l.y<-30){HODL.splice(i,1);continue;}const x=Math.round(l.x+Math.sin(l.ph)*12),y=Math.round(l.y);
      if(!LITE){ctx.save();ctx.globalCompositeOperation="lighter";const g=ctx.createRadialGradient(x,y,1,x,y,20);g.addColorStop(0,"rgba(255,170,70,0.35)");g.addColorStop(1,"rgba(255,170,70,0)");ctx.fillStyle=g;ctx.fillRect(x-20,y-20,40,40);ctx.restore();}
      ctx.fillStyle="#ffb04a";ctx.fillRect(x-4,y-6,8,11);ctx.fillStyle="#fff0b0";ctx.fillRect(x-2,y-3,4,5);ctx.fillStyle="#7a3a14";ctx.fillRect(x-4,y-7,8,2);}
  }else if(HODL.length)HODL.length=0;
  if(HOD.flash>0){ctx.fillStyle=`rgba(255,210,130,${HOD.flash/60*0.22})`;ctx.fillRect(0,0,W,H);HOD.flash--;}
}
/*_sun*/
const SUN={e:-1,S:null,charge:0,lit:false,occ:0,need:2,sil:0,gap:25,flash:0};
function sunGet(){
  if(WORLD_ID!=="tiferet")return null;
  const e=getEpoch();
  if(SUN.e!==e||!SUN.S){SUN.e=e;SUN.charge=0;SUN.lit=false;SUN.flash=0;const r=mulberry32(hashStr(e+"|sun")),a0=r()*6.283;
    SUN.S=[0,1,2,3,4,5].map(i=>({x:5000+Math.cos(a0+i*1.0472)*430,y:5000+Math.sin(a0+i*1.0472)*344,on:false,me:false}));}
  return SUN.S;
}
function sunLight(s,pub){
  if(SUN.lit)return;SUN.lit=true;SUN.charge=1;SUN.flash=70;SUN.sil=0;SUN.gap=25+Math.floor(Math.random()*30);
  try{FKAudio.beacon();}catch(e){}
  if(SUN.S&&SUN.S.some(g=>g.me))RECAP.sunup=1;
  if(pub)pub({e:getEpoch()});
}
function sunTick(s,pub){
  const S=sunGet();if(!S)return;
  const real=s.cats.filter(c=>!c.isSys&&!c.isGhost&&!c.idle),me=s.cats.find(c=>c.id===s.myId);let occ=0;
  S.forEach(g=>{g.on=real.some(c=>c.state==="sit"&&Math.hypot(c.x-g.x,(c.y-g.y)*2)<72);if(g.on)occ++;g.me=!!(me&&!me.idle&&me.state==="sit"&&Math.hypot(me.x-g.x,(me.y-g.y)*2)<72);});
  SUN.occ=occ;SUN.need=Math.min(6,Math.max(2,Math.ceil(real.length*0.6)));
  if(SUN.flash>0)SUN.flash--;
  if(SUN.lit){if(s.frame%60===0){SUN.sil++;if(SUN.sil>=SUN.gap){SUN.sil=0;SUN.gap=25+Math.floor(Math.random()*30);pub({e:getEpoch()});}}}
  else{if(occ>=SUN.need)SUN.charge=Math.min(1,SUN.charge+1/300);else SUN.charge=Math.max(0,SUN.charge-1/900);if(SUN.charge>=1)sunLight(s,pub);}
}
function drawSun(ctx,cam,W,H,f,s){
  const S=sunGet();if(!S)return;
  const cx=Math.round(5000-cam.x),cy=Math.round(5000-cam.y),lit=SUN.lit,pulse=0.5+0.5*Math.sin(f*0.05);
  const ell=(x,y,rx,ry,c)=>{ctx.fillStyle=c;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.fill();};
  S.forEach(g=>{const sx=Math.round(g.x-cam.x),sy=Math.round(g.y-cam.y);if(sx<-120||sx>W+120||sy<-80||sy>H+80)return;
    if(g.on){ell(sx,sy,70,35,"rgba(255,215,110,0.16)");}
    ctx.lineWidth=2;ctx.strokeStyle=g.on?"rgba(255,225,130,0.9)":"rgba(255,215,110,0.32)";ctx.beginPath();ctx.ellipse(sx,sy,70,35,0,0,Math.PI*2);ctx.stroke();
    ctx.strokeStyle=g.on?"rgba(255,235,160,0.7)":"rgba(255,215,110,0.2)";ctx.beginPath();ctx.ellipse(sx,sy,38,19,0,0,Math.PI*2);ctx.stroke();
    ctx.fillStyle=g.on?"rgba(255,240,180,0.95)":"rgba(255,215,110,0.4)";ctx.fillRect(sx-2,sy-2,4,4);ctx.fillRect(sx-72,sy-1,6,3);ctx.fillRect(sx+66,sy-1,6,3);ctx.fillRect(sx-1,sy-37,3,5);ctx.fillRect(sx-1,sy+32,3,5);});
  if(cx>-220&&cx<W+220&&cy>-1700&&cy<H+220){
    ell(cx,cy+6,100,50,"rgba(0,0,0,0.35)");ell(cx,cy,92,46,"#4a3410");ell(cx,cy-3,78,38,"#6b4d18");ell(cx,cy-6,62,30,lit?"#f0c050":"#8a6a1c");
    ctx.lineWidth=3;ctx.strokeStyle="rgba(255,225,130,0.95)";if(!lit&&SUN.charge>0){ctx.beginPath();ctx.ellipse(cx,cy-6,62,30,0,-Math.PI/2,-Math.PI/2+SUN.charge*Math.PI*2);ctx.stroke();}
    ctx.fillStyle=lit?"#fff4c0":"#c9a24a";ctx.fillRect(cx-3,cy-44,6,38);ctx.fillStyle=lit?"#fffbe0":"#e2c070";ctx.fillRect(cx-3,cy-44,2,38);
    if(lit){ctx.save();ctx.globalCompositeOperation="lighter";const top=Math.min(cy-1600,-200);
      (LITE?[[30,0.1],[8,0.22]]:[[46,0.07],[30,0.09],[18,0.13],[8,0.22]]).forEach(([hw,al])=>{const y0=cy-40,bg=ctx.createLinearGradient(0,y0,0,top);bg.addColorStop(0,"rgba(255,235,150,0)");bg.addColorStop(Math.min(0.2,50/(y0-top)),`rgba(255,235,150,${al})`);bg.addColorStop(1,"rgba(255,235,150,0)");ctx.fillStyle=bg;ctx.fillRect(cx-hw,top,hw*2,y0-top);});
      if(!LITE){const R=140+30*pulse,g=ctx.createRadialGradient(cx,cy-40,6,cx,cy-40,R);g.addColorStop(0,"rgba(255,225,130,0.3)");g.addColorStop(1,"rgba(255,225,130,0)");ctx.fillStyle=g;ctx.fillRect(cx-R,cy-40-R,R*2,R*2);}
      ctx.restore();}
    if(!lit&&(SUN.occ>0||SUN.charge>0)){ctx.save();ctx.font="8px "+ff;ctx.textAlign="center";ctx.fillStyle="rgba(255,235,170,0.85)";ctx.fillText(SUN.occ+"/"+SUN.need,cx,cy+66);ctx.restore();}}
  if(lit){
    ctx.fillStyle="rgba(255,200,90,0.04)";ctx.fillRect(0,0,W,H);
    if(!LITE){ctx.save();ctx.globalCompositeOperation="lighter";s.cats.forEach(c=>{if(c.isSys||c.isGhost)return;const hx=Math.round(c.x+5.5*P-cam.x),hy=Math.round(c.y+5*P-cam.y);if(hx<-60||hx>W+60||hy<-60||hy>H+60)return;
      const g=ctx.createRadialGradient(hx,hy,3,hx,hy,46);g.addColorStop(0,"rgba(255,215,110,0.28)");g.addColorStop(1,"rgba(255,215,110,0)");ctx.fillStyle=g;ctx.fillRect(hx-46,hy-46,92,92);});ctx.restore();}
  }
  if(SUN.flash>0){ctx.fillStyle=`rgba(255,235,160,${SUN.flash/70*0.3})`;ctx.fillRect(0,0,W,H);}
}
/*_vent*/
let _vnE=-1,_vnL=[];const VENT_P=9000;
function ventsList(){
  if(WORLD_ID!=="gevurah")return[];
  const e=getEpoch();
  if(_vnE!==e){_vnE=e;_vnL=[];const r=mulberry32(hashStr(e+"|vents")),pt=PORTALS.gevurah||{};
    for(let i=0;i<600&&_vnL.length<12;i++){const x=1200+r()*7600,y=1200+r()*7600;let ok=Math.hypot(x-5000,y-5000)>300;
      for(const k in pt)if(Math.hypot(x-pt[k][0],y-pt[k][1])<450)ok=false;
      _vnL.forEach(o=>{if(Math.hypot(x-o.x,y-o.y)<650)ok=false;});
      if(ok)_vnL.push({x,y,off:Math.floor(r()*VENT_P),last:-1,snd:-1});}}
  return _vnL;
}
function ventTick(s){
  const L=ventsList();if(!L.length)return;
  const me=s.cats.find(c=>c.id===s.myId);if(!me||me.idle)return;
  const now=sharedNow();
  L.forEach(v=>{const t=(now+v.off)%VENT_P;if(t<8000||t>8700)return;const idx=Math.floor((now+v.off)/VENT_P),d=Math.hypot(me.x-v.x,(me.y-v.y)*2);
    if(v.snd!==idx&&d<700){v.snd=idx;try{FKAudio.hit(4,true);}catch(e){}}
    if(v.last===idx||d>=64)return;v.last=idx;
    if(me._dash>0){me._boostTimer=120;RECAP.rides=(RECAP.rides||0)+1;try{FKAudio.dash();}catch(e){}}
    else{const dx=me.x-v.x,dy=me.y-v.y,l=Math.hypot(dx,dy)||1;me.vx+=dx/l*9;me.vy+=dy/l*9;me._cap=Math.max(me._cap||3.5,9);RECAP.singed=(RECAP.singed||0)+1;try{FKAudio.hit(8,true);}catch(e){}}});
}
function drawVents(ctx,cam,W,H,f){
  const L=ventsList();if(!L.length)return;const now=sharedNow();
  L.forEach(v=>{const sx=Math.round(v.x-cam.x),sy=Math.round(v.y-cam.y);if(sx<-120||sx>W+120||sy<-240||sy>H+90)return;
    const t=(now+v.off)%VENT_P,el=(x,y,rx,ry,c)=>{ctx.fillStyle=c;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.fill();};
    const warn=t>=6800&&t<8000?(t-6800)/1200:0,erupt=t>=8000&&t<8700?(t-8000)/700:-1;
    el(sx,sy+3,40,14,"rgba(0,0,0,0.4)");el(sx,sy,34,12,"#2a1418");el(sx,sy-1,28,9,"#120708");
    el(sx,sy-1,16,5,warn>0||erupt>=0?"#d03a2a":"#5a1a14");
    if(warn>0){const a=0.25+0.6*warn*(0.6+0.4*Math.sin(f*0.5));ctx.lineWidth=2;ctx.strokeStyle=`rgba(255,80,70,${a})`;ctx.beginPath();ctx.ellipse(sx,sy,64,32,0,0,Math.PI*2);ctx.stroke();
      ctx.fillStyle=`rgba(255,110,60,${a})`;ctx.fillRect(sx-14+((f*0.4)|0)%28,sy-6-((f*0.9)|0)%16,3,3);}
    if(erupt>=0){const h=Math.round(150*Math.sin(Math.min(1,erupt*1.4)*Math.PI*0.5)*(1-0.4*erupt)),w2=Math.round(26-8*erupt);
      ctx.fillStyle="#d03a2a";ctx.fillRect(sx-w2,sy-h,w2*2,h);ctx.fillStyle="#ff7a3a";ctx.fillRect(sx-w2*0.66,sy-h*0.88,w2*1.32,h*0.88);ctx.fillStyle="#ffd890";ctx.fillRect(sx-w2*0.3,sy-h*0.7,w2*0.6,h*0.7);
      ctx.strokeStyle=`rgba(255,160,90,${0.8*(1-erupt)})`;ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(sx,sy,30+erupt*60,15+erupt*30,0,0,Math.PI*2);ctx.stroke();
      if(!LITE){ctx.save();ctx.globalCompositeOperation="lighter";const R=110,g=ctx.createRadialGradient(sx,sy-h*0.4,6,sx,sy-h*0.4,R);g.addColorStop(0,"rgba(255,110,50,0.4)");g.addColorStop(1,"rgba(255,110,50,0)");ctx.fillStyle=g;ctx.fillRect(sx-R,sy-h*0.4-R,R*2,R*2);ctx.restore();}}
  });
}
let uid=100;
function makeCat(x,y,palOrObj,name,isOwn=false,isSys=false,sysType=null,remoteId=null){
  const palObj=typeof palOrObj==="number"?{...PALETTES[palOrObj],_name:name}:{...palOrObj};
  if(!palObj._name)palObj._name=name;
  return{
    id:remoteId??(uid++).toString(),
    x,y,vx:0,vy:0,
    pal:palObj,palId:typeof palOrObj==="number"?palOrObj:null,
    name,isOwn,isSys,sysType,
    confessions:[],
    range:150+Math.random()*100,showRange:0,
    state:"sit",flip:Math.random()>0.5,
    revealAlpha:0,revealTimer:0,
    frame:Math.floor(Math.random()*200),
    wanderAngle:Math.random()*Math.PI*2,
    wanderTimer:Math.floor(Math.random()*120),
    grabbed:false,idle:false,
  };
}

const COOLDOWN_SEC=30;

// ─── Component ────────────────────────────────────────────────────────────────
export default function App(){
  const canvasRef    = useRef(null);
  const clientId     = useRef(getClientId());
  const ablyRef      = useRef(null);
  const channelRef   = useRef(null);
  const gs           = useRef({
    cats:[], worldObjs:[],
    laser:{sx:-999,sy:-999,active:false}, // screen coords
    trail:[], stars:[], frame:0,
    drag:null, laserOn:false, myId:null, ready:false,
    // camera: world position of top-left corner
    cam:{x:0,y:0},
    // drag camera
    camDrag:null,
    // reset spectacle particles
    particles:[],
    joystick:{active:false,startX:0,startY:0,dx:0,dy:0},
  });
  const animRef      = useRef(null);
  const phaseRef     = useRef("loading");
  const pendingSpawn = useRef(null);
  const moveThrottle = useRef(0);

  const [phase,       setPhase]       = useState("loading");
  const [pickName,    setPickName]    = useState("");
  const [pickPal,     setPickPal]     = useState(0);
  const [laserOn,     setLaserOn]     = useState(false);
  const [showInput,   setShowInput]   = useState(false);
  const [inputVal,    setInputVal]    = useState("");
  const [cooldown,    setCooldown]    = useState(0);
  const [showLetterInput, setShowLetterInput] = useState(false);
  const [letterVal, setLetterVal] = useState("");
  const [showTagPicker, setShowTagPicker] = useState(false);
  const [myTag, setMyTag] = useState("");
  const [panel,       setPanel]       = useState(null);
  const [resetIn,     setResetIn]     = useState(nextResetMs());
  const [onlineCount, setOnlineCount] = useState(0);const [worldName,setWorldName]=useState("Malkuth Gate");const [recap,setRecap]=useState(null);const [lite,setLite]=useState(LITE);const [tut,setTut]=useState(0);const [sndMode,setSndMode]=useState(FKAudio.mode());const [fade,setFade]=useState(false);const [muted,setMuted]=useState(FKAudio.isMuted());
  const lastTap = useRef({id:null,time:0});

  // ── world → screen conversion ──────────────────────────────────────────────
  const w2s=(wx,wy)=>{
    const{cam}=gs.current;
    return{sx:wx-cam.x, sy:wy-cam.y};
  };
  const s2w=(sx,sy)=>{
    const{cam}=gs.current;
    return{wx:sx+cam.x, wy:sy+cam.y};
  };

  // ── Build system cats ──────────────────────────────────────────────────────

  // ── Build system cats ──────────────────────────────────────────────────────
  function buildSysCats(){
    // spawn near center so new users find them easily
    const cx=WORLD_W/2, cy=WORLD_H/2;
    const pc=makeCat(cx-300,cy+200,SYS_PAL_PRIVACY,"policy",false,true,"privacy");
    pc.confessions=[...PRIVACY_LINES];
    const ac=makeCat(cx+300,cy+200,SYS_PAL_ABOUT,"about",false,true,"about");
    ac.confessions=[...ABOUT_LINES];
    // patates - tribute cat, always present near spawn
    const pat=makeCat(cx,cy-250,SYS_PAL_PATATES,"patates",false,true,"patates");
    pat.confessions=[...PATATES_LINES];
    pat.wanderTimer=0;
    // oracle - rare, random location far from spawn
    const oraclePal={...SYS_PAL_ORACLE};
    const orng=worldRng("oracle");
    const ocat=makeCat(
      1000+orng()*(WORLD_W-2000),
      1000+orng()*(WORLD_H-2000),
      oraclePal,"oracle",false,true,"oracle"
    );
    ocat.confessions=["i see all","i know all","ask me anything","double-tap to consult"];
    ocat._isOracle=true;
    return WORLD_ID==="malkuth"?[pc,ac,pat]:[ocat];
  }

  const requestSpawn=useCallback((name,palId,restored=null)=>{
    pendingSpawn.current={name,palId,restored};
    phaseRef.current="play";
    setPhase("play");
  },[]);

  useEffect(()=>{
    if(phase!=="play")return;
    const raf=requestAnimationFrame(()=>{
      const cv=canvasRef.current;if(!cv)return;
      cv.width=cv.offsetWidth||window.innerWidth;
      cv.height=cv.offsetHeight||window.innerHeight;
      const s=gs.current;
      WORLD_ID="malkuth";setWorldName(WORLDS.malkuth.name);FKAudio.setWorld("malkuth");s.stars=genStars();
      s.worldObjs=generateWorldObjects();
      s._worldEpoch=getEpoch();
      s._initObjs=s.worldObjs.map(o=>({type:o.type,x:Math.round(o.x),y:Math.round(o.y)}));
      window.__fikfuk=()=>({epoch:getEpoch(),offsetMs:Math.round(clockOffset),initial:s._initObjs});
      if(pendingSpawn.current){
        const{name,palId,restored}=pendingSpawn.current;
        pendingSpawn.current=null;
        s.cats=buildSysCats();
        const ox=restored?.x??2000+Math.random()*6000;
        const oy=restored?.y??2000+Math.random()*6000;
        clientId.current=getClientId();const myCat=makeCat(ox,oy,palId,name,true,false,null,clientId.current);
        if(restored?.confessions)myCat.confessions=[...restored.confessions];
        s.cats.push(myCat);
        s.myId=myCat.id;
        s.cam={x:ox-cv.width/2,y:oy-cv.height/2};
        s.ready=true;
        gs.current._spawnEpoch=getEpoch();saveSession({name,palId,confessions:myCat.confessions,x:ox,y:oy});recapStart();setRecap(null);try{if(!localStorage.getItem("fikfuk_tut"))setTut(1);}catch(e){}
        setOnlineCount(1);
        connectAbly(myCat);
      }
    });
    return()=>cancelAnimationFrame(raf);
  },[phase]);

  function hopTo(dest){
    const s=gs.current;
    const me=s.cats.find(c=>c.id===s.myId);
    const t=Date.now();
    if(!me||!s.ready||s._hop||!WORLDS[dest]||t-(s._hopT||0)<4000)return;
    s._hop=true;s._hopT=t;setFade(true);
    const from=WORLD_ID;
    const finish=(ok)=>{
      if(!ok){
        const p=(PORTALS[from]||{})[dest];if(p){const q=awayFromRing(p);me.x=q[0];me.y=q[1];me.vx=0;me.vy=0;}
        s.particles.push({text:"that world is full",x:me.x-30,y:me.y-20,vx:0,vy:-0.4,alpha:1,life:200,delay:0});
        setFade(false);s._hop=false;return;
      }
      setTimeout(()=>{
        joinWorld(dest);FKAudio.portal();RECAP.hops++;RECAP.w[dest]=1;
        const back=(PORTALS[dest]||{})[from];const q=back?awayFromRing(back):[WORLD_W/2,WORLD_H/2];
        me.x=q[0];me.y=q[1];me.vx=0;me.vy=0;s._lastMove=null;
        const cv=canvasRef.current;if(cv)s.cam={x:me.x-cv.width/2,y:me.y-cv.height/2};
        setFade(false);setTimeout(()=>{s._hop=false;},300);
      },350);
    };
    let called=false;const once=(ok)=>{if(called)return;called=true;finish(ok);};
    setTimeout(()=>once(true),2500);
    try{ablyRef.current.channels.get(channelFor(dest)).presence.get().then(m=>once(!m||m.length<WORLD_CAP)).catch(()=>once(true));}catch(e){once(true);}
  }

  function joinWorld(id){
    const s=gs.current;
    const me=s.cats.find(c=>c.id===s.myId);
    if(!me||!s.ready||id===WORLD_ID||!WORLDS[id])return;
    WORLD_ID=id;setWorldName(WORLDS[id].name);FKAudio.setWorld(id);
    s.cats=buildSysCats();s.cats.push(me);
    me._territory=null;s._myTerritory=null;me._carry=false;
    s.worldObjs=generateWorldObjects();
    s._worldEpoch=getEpoch();
    s._initObjs=s.worldObjs.map(o=>({type:o.type,x:Math.round(o.x),y:Math.round(o.y)}));
    s._dead=new Set();s._bhClosedSlot=undefined;s._spawnSlot={};s._chirps=[];s.particles=[];s._syncSeen={};s._joinAnswered={};
    wallConfessions.length=0;
    setOnlineCount(1);
    connectAbly(me);
  }

  function connectAbly(myCat){
    if(ablyRef.current)ablyRef.current.close();
    const ably=new Ably.Realtime({key:ABLY_KEY,clientId:clientId.current});
    ablyRef.current=ably;
    // sync to Ably's server clock so every player shares one world clock
    const _t0=Date.now();
    ably.time().then(serverT=>{
      const _t1=Date.now();
      clockOffset=serverT-(_t0+_t1)/2;if(gs.current._spawnEpoch!=null)gs.current._spawnEpoch=getEpoch();
      const s=gs.current;
      if(s.ready&&getEpoch()!==s._worldEpoch){
        s.worldObjs=generateWorldObjects();
        s._worldEpoch=getEpoch();
        s._initObjs=s.worldObjs.map(o=>({type:o.type,x:Math.round(o.x),y:Math.round(o.y)}));
        const orc=s.cats.find(c=>c.sysType==="oracle");
        if(orc){const r=worldRng("oracle");orc.x=1000+r()*(WORLD_W-2000);orc.y=1000+r()*(WORLD_H-2000);}
      }
    }).catch(()=>{});
    const channel=ably.channels.get(channelFor(WORLD_ID));
    channelRef.current=channel;
    const myPresenceData=()=>({
      name:myCat.name,palId:myCat.palId,
      x:myCat.x,y:myCat.y,flip:myCat.flip,
      confessions:myCat.confessions,
      territory:myCat._territory||null,
    });
    const addRemoteCat=(d,cid)=>{
      const s=gs.current;
      if(cid===clientId.current)return;
      s.cats=s.cats.filter(c=>c.id!==cid);
      if(!d||!d.name)return;
      const cat=makeCat(d.x??WORLD_W/2,d.y??WORLD_H/2,d.palId??0,d.name,false,false,null,cid);
      cat.confessions=d.confessions??[];
      cat.flip=d.flip??false;
      if(d.territory) cat._territory=d.territory;
      s.cats.push(cat);
      setOnlineCount(s.cats.filter(c=>!c.isSys).length);
    };
    channel.subscribe("sync",(m)=>{try{const d=m.data;if(d&&d.for){const s=gs.current;(s._syncSeen=s._syncSeen||{})[d.for]=Date.now();}}catch(e){}});
    channel.presence.subscribe("enter",(m)=>{
      addRemoteCat(m.data,m.clientId);
      {const _j=m.clientId,_me=clientId.current,_t0=Date.now(),_ja=(gs.current._joinAnswered=gs.current._joinAnswered||{});if(_j&&_j!==_me&&_t0-(_ja[_j]||0)>120000){_ja[_j]=_t0;const _hs=(x)=>{let h=2166136261;for(let i=0;i<x.length;i++){h^=x.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;};const _ids=gs.current.cats.filter(c=>!c.isOwn&&!c.isSys&&!c.isGhost&&c.id!==_j).map(c=>c.id);_ids.push(_me);_ids.sort((a,b)=>_hs(_j+":"+a)-_hs(_j+":"+b)||(a<b?-1:1));const _rank=_ids.indexOf(_me);if(_rank<3)setTimeout(()=>{try{sendSync(_j);}catch(e){}},300+Math.random()*1000);else if(_rank<6)setTimeout(()=>{const _t=(gs.current._syncSeen||{})[_j]||0;if(_t<_t0){try{sendSync(_j);}catch(e){}}},3500+Math.random()*1000);}}
    });
    channel.presence.subscribe("present",(m)=>addRemoteCat(m.data,m.clientId));
    channel.presence.subscribe("leave",(m)=>{
      const s=gs.current;
      const leavingCat=s.cats.find(c=>c.id===m.clientId);
      if(leavingCat){
        // turn into ghost instead of instant removal
        leavingCat.isGhost=true;
        leavingCat.ghostTimer=120; // 2 seconds at 60fps
        leavingCat.idle=true;
      }
      setOnlineCount(s.cats.filter(c=>!c.isSys&&!c.isGhost).length);
    });
    channel.presence.subscribe("update",(m)=>{
      if(m.clientId===clientId.current)return;
      const cat=gs.current.cats.find(c=>c.id===m.clientId);
      if(cat&&m.data.confessions)cat.confessions=m.data.confessions;
      if(cat&&m.data.idle!==undefined)cat.idle=m.data.idle;
    });
    channel.subscribe("move",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const cat=gs.current.cats.find(c=>c.id===msg.clientId);
      if(!cat)return;
      const d=msg.data;
      cat._tx=d.x;cat._ty=d.y;cat.flip=d.flip;cat.state=d.state;
      if(Math.hypot(d.x-cat.x,d.y-cat.y)>600){cat.x=d.x;cat.y=d.y;}
      cat.vx=0;cat.vy=0;
    });
    channel.subscribe("sun",(msg)=>{if(msg.clientId===clientId.current)return;const d=msg.data||{};if(WORLD_ID!=="tiferet"||d.e!==getEpoch())return;if(!sunGet())return;if(SUN.lit){SUN.sil=0;return;}sunLight(gs.current,null);});channel.subscribe("hod",(msg)=>{if(msg.clientId===clientId.current)return;const d=msg.data||{};if(WORLD_ID!=="hod"||d.e!==getEpoch())return;const L=hodGet();if(!L)return;if(d.k==="e"){const o=L.em[d.i];if(o)o.taken=true;}else if(d.k==="b"){const b=L.br[d.i];if(b&&(d.f|0)>b.fuel){b.fuel=Math.min(b.need,d.f|0);hodFuel(b);}HOD.sil=0;}else if(d.k==="s"&&Array.isArray(d.f)){L.br.forEach((b,i)=>{const f=Math.min(b.need,d.f[i]|0);if(f>b.fuel){b.fuel=f;hodFuel(b);}});HOD.sil=0;}});channel.subscribe("dig",(msg)=>{if(msg.clientId===clientId.current)return;const d=msg.data||{};if(d.w!=="netzach"||WORLD_ID!=="netzach"||d.e!==getEpoch())return;const o=pagesList()[d.i];if(o&&!o.open)pageOpen(o,gs.current,null);});channel.subscribe("beacon",(msg)=>{if(msg.clientId===clientId.current)return;const d=msg.data||{};if(d.w!==WORLD_ID)return;const b=beaconGet(WORLD_ID);if(d.e!==b.e)return;if(b.lit){b.sil=0;return;}beaconLight(b,gs.current,null);});channel.subscribe("wall",(msg)=>{
      if(msg.clientId===clientId.current)return;
      addToWall(msg.data.entry.text);
    });

    channel.subscribe("letter",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const l=msg.data.letter;
      gs.current.worldObjs.push({type:"letter",...l,frame:0,alpha:0});
    });

    channel.subscribe("whisper",(msg)=>{
      if(msg.clientId===clientId.current)return;
      // only show if it's addressed to me
      if(msg.data.targetId!==clientId.current)return;
      const s=gs.current;
      const myCat=s.cats.find(c=>c.id===s.myId);
      if(myCat){
        s._whisperMsg={text:msg.data.text,life:300,alpha:0};
      }
    });

    channel.subscribe("reaction",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const s=gs.current;
      const targetCat=s.cats.find(c=>c.id===msg.data.targetId);
      if(targetCat){
        if(!targetCat._reactions) targetCat._reactions=[];
        targetCat._reactions.push({
          emoji:msg.data.emoji, life:180,
          x:Math.random()*30-15, vy:-0.5-Math.random()*0.3,
        });
      }
    });

    channel.subscribe("tag",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const s=gs.current;
      const cat=s.cats.find(c=>c.id===msg.clientId);
      if(cat) cat._tag=msg.data.tag;
    });

    const applyDead=(id,type,x,y,announce)=>{
      const s=gs.current;
      s._dead=s._dead||new Set();
      const had=s.worldObjs.find(o=>o.id===id);
      s._dead.add(id);
      s.worldObjs=s.worldObjs.filter(o=>o.id!==id);
      if(had&&type==="diablo"&&announce){
        s.worldObjs.push({type:"fossil",id:"fossil_reward_"+id,x:x+100,y:y+100,confession:"u defeated diablo",revealed:true,sitTimer:999,frame:0});
      }
    };
    channel.subscribe("obj_dead",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const d=msg.data;
      applyDead(d.id,d.type,d.x,d.y,true);
    });
    channel.subscribe("dia_hit",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const o=gs.current.worldObjs.find(x=>x.id===msg.data.id);
      if(o&&msg.data.hp>0&&msg.data.hp<o.hp){o.hp=msg.data.hp;FKAudio.hit(msg.data.hp,true);}
    });
    const sendSync=(_for)=>{
      const s=gs.current;
      if(!s.ready)return;
      const bh=s.worldObjs.find(o=>o.type==="blackhole");
      const dia=s.worldObjs.find(o=>o.type==="diablo");
      channel.publish("sync",{
        dead:Array.from(s._dead||[]).slice(-50),
        bh:bh?{slot:bh.slot,hp:bh.hp}:null,
        dia:dia?{id:dia.id,hp:dia.hp}:null,
        bhClosed:(s._bhClosedSlot===undefined)?null:s._bhClosedSlot,for:_for||null,
      });
    };
    window.__fikfukSync=sendSync;window.__fikfukGo=joinWorld;window.__fikfukWorld=()=>WORLD_ID;window.__fikfukSys=()=>gs.current.cats.filter(c=>c.isSys).map(c=>c.sysType);
    window.__fikfukMouse=()=>{const s=gs.current;const m=s.cats.find(c=>c.id===s.myId);if(m)m._carry=true;};
    window.__fikfukPub=()=>window.__fikfukPubN||0;
    channel.subscribe("sync",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const s=gs.current;
      const d=msg.data;
      (d.dead||[]).forEach(id=>{
        if(!(s._dead&&s._dead.has(id)))applyDead(id,null,0,0,false);
      });
      const bh=s.worldObjs.find(o=>o.type==="blackhole");
      if(bh&&d.bh&&d.bh.slot===bh.slot&&d.bh.hp<bh.hp)bh.hp=Math.max(1,d.bh.hp);
      if(d.bhClosed!==null&&d.bhClosed!==undefined){
        s._bhClosedSlot=d.bhClosed;
        if(bh&&bh.slot===d.bhClosed)s.worldObjs=s.worldObjs.filter(o=>o.type!=="blackhole");
      }
      const dia=s.worldObjs.find(o=>o.type==="diablo"&&d.dia&&o.id===d.dia.id);
      if(dia&&d.dia.hp>0&&d.dia.hp<dia.hp)dia.hp=d.dia.hp;
    });
    channel.subscribe("feed",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const pat=gs.current.cats.find(c=>c.sysType==="patates");
      if(pat)feedPatates(pat,false);
    });
    channel.subscribe("chirp",(msg)=>{
      if(msg.clientId===clientId.current)return;
      applyChirp(msg.data.x,msg.data.y,msg.clientId);
    });
    channel.subscribe("blackhole_hit",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const s=gs.current;
      const bh=s.worldObjs.find(o=>o.type==="blackhole");
      if(bh){
        bh.hp=(bh.hp||50)-1;
        if(bh.hp<=0){
          // closed - explosion effect
          s.particles.push(...Array.from({length:20},(_,i)=>({
            text:"✦",
            x:bh.x, y:bh.y,
            vx:Math.cos(i/20*Math.PI*2)*2,
            vy:Math.sin(i/20*Math.PI*2)*2,
            alpha:1, life:120, delay:0,
          })));
          // speed boost all cats
          s.cats.forEach(c=>{if(!c.isSys){c._boostTimer=300;}});
          s.worldObjs=s.worldObjs.filter(o=>o.type!=="blackhole");
          s._bhClosedSlot=bh.slot;
        }
      }
    });

    channel.subscribe("reset",()=>{try{ablyRef.current.close();}catch(e){}
      localStorage.removeItem("fikfuk_s");
      const s=gs.current;
      s.cats=[];s.myId=null;s.ready=false;
      s.laserOn=false;s.laser={sx:-999,sy:-999,active:false};s.trail=[];
      s.worldObjs=[];
      setLaserOn(false);phaseRef.current="onboard";setPhase("onboard");
    });
    channel.presence.enter(myPresenceData());
    myCat._updatePresence=()=>channel.presence.update(myPresenceData());
    if(window.__fikfukSyncIv)clearInterval(window.__fikfukSyncIv);
    window.__fikfukSyncIv=setInterval(()=>{try{sendSync();}catch(e){}},45000);

    // reconnection handler - re-enter presence if connection drops and recovers
    ably.connection.on("connected",()=>{
      // re-enter presence after reconnect
      channel.presence.enter(myPresenceData());
    });

    ably.connection.on("disconnected",()=>{
      console.log("Ably disconnected - will auto reconnect");
    });

    ably.connection.on("suspended",()=>{
      console.log("Ably suspended - trying to reconnect");
    });

    if(window.__fkUnload)window.removeEventListener("beforeunload",window.__fkUnload);window.__fkUnload=()=>{try{channel.presence.leave();}catch(e){}};window.addEventListener("beforeunload",window.__fkUnload);

    // re-enter presence when tab becomes visible again
    if(window.__fkVis)document.removeEventListener("visibilitychange",window.__fkVis);document.addEventListener("visibilitychange",window.__fkVis=()=>{
      if(!document.hidden&&ably.connection.state==="connected"){
        channel.presence.enter(myPresenceData());
      }
    });
  }

  useEffect(()=>{
    const sess=loadSession();
    if(sess)requestSpawn(sess.name,sess.palId,{confessions:sess.confessions,x:sess.x,y:sess.y});
    else{setPhase("onboard");phaseRef.current="onboard";}
  },[requestSpawn]);

  useEffect(()=>{
    const iv=setInterval(()=>{
      const ms=nextResetMs();
      /*_wipeLocal*/{const _g=gs.current;if(phaseRef.current==="play"&&_g._spawnEpoch!=null&&getEpoch()!==_g._spawnEpoch){localStorage.removeItem("fikfuk_s");{const _m=_g.cats.find(c=>c.id===_g.myId);if(_m)setRecap(recapSnap(_m));}try{ablyRef.current.close();}catch(e){}_g.cats=[];_g.myId=null;_g.ready=false;_g.laserOn=false;_g.laser={sx:-999,sy:-999,active:false};_g.trail=[];_g.worldObjs=[];_g._spawnEpoch=null;wallConfessions.length=0;setMyTag("");setLaserOn(false);phaseRef.current="onboard";setPhase("onboard");return;}}
      setResetIn(ms);
      const s=gs.current;
      const myCat=s.cats.find(c=>c.id===s.myId);

      // 30s before - spawn floating confession particles
      if(ms<=30000&&ms>29000&&myCat){
        s.cats.filter(c=>!c.isSys&&c.confessions.length>0).forEach(cat=>{
          cat.confessions.forEach((text,i)=>{
            s.particles.push({
              text,
              x:cat.x, y:cat.y,
              vx:(Math.random()-0.5)*0.5,
              vy:-0.8-Math.random()*0.5,
              alpha:1, life:600,
              delay:i*20,
            });
          });
        });
      }

      if(ms<=1000){
        localStorage.removeItem("fikfuk_s");
        /* reset is local now: no broadcast */
        // white flash
        gs.current._flashTimer=30;
      }
    },1000);
    return()=>clearInterval(iv);
  },[]);

  useEffect(()=>{
    const onVis=()=>{
      const s=gs.current;
      const myCat=s.cats.find(c=>c.id===s.myId);
      if(!myCat)return;
      myCat.idle=document.hidden;
      if(myCat._updatePresence)myCat._updatePresence();
    };
    document.addEventListener("visibilitychange",onVis);
    return()=>document.removeEventListener("visibilitychange",onVis);
  },[]);

  useEffect(()=>{
    if(phase!=="play")return;
    const cv=canvasRef.current;if(!cv)return;
    const ctx=cv.getContext("2d");
    const resize=()=>{cv.width=cv.offsetWidth||window.innerWidth;cv.height=cv.offsetHeight||window.innerHeight;};
    window.addEventListener("resize",resize);
    const tick=()=>{
      const s=gs.current;
      if(!s.ready){animRef.current=requestAnimationFrame(tick);return;}
      /*_lite*/{const _n=performance.now(),_a=s._ad||(s._ad={t:_n,r:0,done:false});if(!_a.done){if(document.hidden){_a.t=_n;_a.r=0;}else{_a.r++;const _e=_n-_a.t;if(_e>12000){_a.done=true;let _c=null;try{_c=localStorage.getItem("fikfuk_lite");}catch(e){}if(!LITE&&_c===null&&_a.r/(_e/1000)<34){LITE=true;setLite(true);try{localStorage.setItem("fikfuk_lite","1");}catch(e){}s._liteNote=300;}}}}}
      /*_fpsGate*/{const _k=window.__fk=window.__fk||{r:0,t:0,t0:performance.now()};_k.r++;if(!window.__fikfukHz){window.__fikfukHz=()=>{const dt=(performance.now()-_k.t0)/1000,o={renders:+(_k.r/dt).toFixed(1),ticks:+(_k.t/dt).toFixed(1)};_k.r=0;_k.t=0;_k.t0=performance.now();return o;};if(/[?&]debug/.test(location.search)){const d=document.createElement("div");d.style.cssText="position:fixed;left:6px;bottom:6px;z-index:99;font:11px monospace;color:#6f6;background:#000a;padding:2px 5px;pointer-events:none";document.body.appendChild(d);setInterval(()=>{const o=window.__fikfukHz();d.textContent="render "+o.renders+"/s  tick "+o.ticks+"/s";},1000);}}const _t=performance.now();s._acc=Math.min((s._acc||0)+(_t-(s._lastT||_t)),100);s._lastT=_t;if(s._acc<14.67){animRef.current=requestAnimationFrame(tick);return;}s._acc-=16.67;_k.t++;}
      s.frame++;
      const W=cv.width,H=cv.height;
      const{laser,cam}=s;
      const myCat=s.cats.find(c=>c.id===s.myId);
      if(myCat&&!s.camDrag&&!s.drag){
        const camTx=Math.max(0,Math.min(WORLD_W-W,myCat.x+5.5*P-W/2));
        const camTy=Math.max(0,Math.min(WORLD_H-H,myCat.y+5*P-H/2));
        cam.x+=(camTx-cam.x)*0.1;
        cam.y+=(camTy-cam.y)*0.1;
      }
      const laserWorld=laser.active?s2w(laser.sx,laser.sy):{wx:-9999,wy:-9999};
      const toRemove=new Set();
      const toAdd=[];

      s.cats.forEach(cat=>{
        if(cat.grabbed){cat.frame++;cat.state="sit";return;}
        cat.frame++;
        if(!cat.isOwn&&!cat.isSys&&cat._tx!==undefined){
          cat.x+=(cat._tx-cat.x)*0.25;
          cat.y+=(cat._ty-cat.y)*0.25;
          cat.vx=0;cat.vy=0;
        }
        const dx=laserWorld.wx-(cat.x+5.5*P);
        const dy=laserWorld.wy-(cat.y+5*P);
        const dist=Math.hypot(dx,dy);
        const inRange=cat.isOwn&&!cat.isSys&&!cat.idle&&laser.active&&dist<cat.range;
        cat.showRange=inRange?Math.min(1,cat.showRange+0.08):Math.max(0,cat.showRange-0.05);
        if(inRange){
          cat.state="run";
          const spd=dist<50?1.2:2.5;
          cat.vx+=(dx/dist)*spd*0.1;cat.vy+=(dy/dist)*spd*0.1;
          cat.flip=dx<0;
          if(dist<70){cat.revealAlpha=Math.min(1,cat.revealAlpha+0.05);cat.revealTimer=80;}
        } else if(cat.isOwn&&!cat.isSys){
          const joy=s.joystick;
          if(joy.active&&Math.hypot(joy.dx,joy.dy)>8){
            const jlen=Math.hypot(joy.dx,joy.dy);
            const jclamped=Math.min(jlen,80);
            const jspd=(jclamped/80)*2.5;
            cat.vx+=(joy.dx/jlen)*jspd*0.2;
            cat.vy+=(joy.dy/jlen)*jspd*0.2;
            cat.flip=joy.dx<0;
            cat.state="run";
            cat.wanderTimer=60;
          } else {
            cat.state="sit";
          }
        } else if(cat.sysType==="oracle"){
          // slow mystical drift
          cat.wanderTimer--;
          if(cat.wanderTimer<=0){
            cat.wanderAngle+=(Math.random()-0.5)*0.8;
            cat.wanderTimer=300+Math.random()*400;
            cat.state=Math.random()>0.7?"run":"sit";
          }
          if(cat.state==="run"){
            cat.vx+=Math.cos(cat.wanderAngle)*0.01;
            cat.vy+=Math.sin(cat.wanderAngle)*0.01;
            cat.flip=cat.vx<0;
          }
        } else if(cat.sysType==="patates"){
          // gentle, careful wandering - short bursts then long pauses
          cat.wanderTimer--;
          if(cat.wanderTimer<=0){
            if(cat.state==="sit"){
              cat.wanderAngle=Math.random()*Math.PI*2;
              cat.wanderTimer=20+Math.random()*30;
              cat.state="run";
            } else {
              cat.wanderTimer=180+Math.random()*240;
              cat.state="sit";
            }
          }
          if(cat.state==="run"){
            cat.vx+=Math.cos(cat.wanderAngle)*0.02;
            cat.vy+=Math.sin(cat.wanderAngle)*0.02;
            cat.flip=cat.vx<0;
          }
          // reveal confession when any player cat is near
          if(myCat){
            const pdx=myCat.x-cat.x,pdy=myCat.y-cat.y;
            const pdist=Math.hypot(pdx,pdy);
            if(pdist<140){
              cat.revealAlpha=Math.min(1,cat.revealAlpha+0.04);
              cat.revealTimer=100;
              cat._cycleTimer=(cat._cycleTimer||0)+1;
              if(cat._cycleTimer>240){
                cat._cycleTimer=0;
                const idx=(cat._msgIdx||0);
                const next=(idx+1)%cat.confessions.length;
                cat._msgIdx=next;
                const msg=cat.confessions[next];
                cat.confessions=cat.confessions.filter(m=>m!==msg);
                cat.confessions.push(msg);
              }
            }
          }
          // leave glowing paw prints while moving
          if(cat.state==="run"){
            cat._pawTimer=(cat._pawTimer||0)+1;
            if(cat._pawTimer>40){
              cat._pawTimer=0;
              toAdd.push({
                type:"pawprint",
                id:`paw_${Date.now()}_${Math.random().toString(36).slice(2,5)}`,
                x:cat.x+Math.random()*10-5,
                y:cat.y+10+Math.random()*6,
                life:600, alpha:0, frame:0,
              });
            }
          }
        }
        // ── territory claiming ──
        if(cat.isOwn&&!cat.isSys){
          const spd3=Math.hypot(cat.vx,cat.vy);
          if(spd3<0.1&&cat.state==="sit"){
            cat._sitTimer=(cat._sitTimer||0)+1;
            if(cat._sitTimer===180){
              cat._territory={x:cat.x,y:cat.y,radius:80,name:cat.name,palBody:cat.pal.body};
              s._myTerritory=cat._territory;
            }
          } else {
            cat._sitTimer=0;
          }
        }

        // ── whisper proximity ──
        if(cat.isOwn&&!cat.isSys){
          const nearCat=s.cats.find(c=>!c.isOwn&&!c.isSys&&!c.isGhost&&Math.hypot(cat.x-c.x,cat.y-c.y)<50);
          if(nearCat){
            cat._whisperTimer=(cat._whisperTimer||0)+1;
            cat._whisperTarget=nearCat.id;
            // whisper sends silently - does NOT stun the cat
            if(cat._whisperTimer===300&&cat.confessions.length>0){
              const text=cat.confessions[cat.confessions.length-1];
              channelRef.current?.publish("whisper",{targetId:nearCat.id,text});
              cat._whisperTimer=0;
              s._whisperSent={text:"whispered",life:120,alpha:1};
            }
          } else {
            cat._whisperTimer=0;
            cat._whisperTarget=null;
          }
        }

        // ── mood system ──
        if(cat.isOwn&&!cat.isSys){
          if(!cat.mood) cat.mood="neutral";
          if(!cat.moodTimer) cat.moodTimer=0;
          cat.moodTimer--;
          // scared - near diablo
          const nearDiablo=s.worldObjs.find(o=>o.type==="diablo"&&Math.hypot(cat.x-o.x,cat.y-o.y)<200);
          if(nearDiablo){ cat.mood="scared"; cat.moodTimer=180; }
          // happy - caught a mouse recently
          if(cat._boostTimer>0){ cat.mood="happy"; }
          // friendly - near another player cat
          const nearPlayer=s.cats.find(c=>!c.isOwn&&!c.isSys&&!c.isGhost&&Math.hypot(cat.x-c.x,cat.y-c.y)<100);
          if(nearPlayer&&cat.mood==="neutral"){ cat.mood="friendly"; cat.moodTimer=300; }
          // reset to neutral
          if(cat.moodTimer<=0) cat.mood="neutral";
        }

        cat.vx*=0.86;cat.vy*=0.86;
        const spd2=Math.hypot(cat.vx,cat.vy);
        {const _cp=cat._cap||3.5;if(spd2>_cp){cat.vx=cat.vx/spd2*_cp;cat.vy=cat.vy/spd2*_cp;}}
        if(!cat.isSys||cat.sysType==="patates"||cat.sysType==="oracle"){cat.x+=cat.vx;cat.y+=cat.vy;}
        cat.x=Math.max(10,Math.min(WORLD_W-12*P,cat.x));
        cat.y=Math.max(10,Math.min(WORLD_H-14*P,cat.y));
        if(cat.revealTimer>0)cat.revealTimer--;
        else cat.revealAlpha=Math.max(0,cat.revealAlpha-0.025);
      });
      // ── spawn new objects over time ──
      if(s.frame%60===0){
        const types=["ufo","fossil","wildcat","mouse","human","diablo"];
        types.forEach(type=>{
          const slotNow=Math.floor((sharedNow()-EPOCH_ANCHOR)/(SPAWN_INTERVALS[type]*1000));
          s._spawnSlot=s._spawnSlot||{};
          if(s._spawnSlot[type]===undefined)s._spawnSlot[type]=slotNow;
          if(slotNow!==s._spawnSlot[type]){
            s._spawnSlot[type]=slotNow;
            const newObj=spawnObj(type,s.worldObjs,mulberry32(hashStr("fikfuk:spawn:"+type+":"+slotNow+(WORLD_ID==="malkuth"?"":":w:"+WORLD_ID))),"t"+slotNow);
            if(newObj)s.worldObjs.push(newObj);
          }
        });
      }
      // black hole: fixed schedule on the shared clock
      // active for the first 20 min of every 45 min slot, seeded position
      {
        const bhSlotMs=45*60*1000;
        const sinceA=sharedNow()-EPOCH_ANCHOR;
        const bhSlot=Math.floor(sinceA/bhSlotMs);
        const inWindow=(sinceA%bhSlotMs)<20*60*1000;
        const bhPos=(slot)=>{
          const r=mulberry32(hashStr("fikfuk:bh:"+slot+(WORLD_ID==="malkuth"?"":":w:"+WORLD_ID)));
          return {x:1000+r()*(WORLD_W-2000),y:1000+r()*(WORLD_H-2000)};
        };
        const bhObj=s.worldObjs.find(o=>o.type==="blackhole");
        if(inWindow&&!bhObj&&s._bhClosedSlot!==bhSlot){
          const p=bhPos(bhSlot);
          s.worldObjs.push({type:"blackhole",id:"bh_"+bhSlot,x:p.x,y:p.y,hp:50,maxHp:50,pullRadius:300,frame:0,slot:bhSlot});
        }
        if(!inWindow&&bhObj){
          s.worldObjs=s.worldObjs.filter(o=>o.type!=="blackhole");
        }
        if(!window.__fikfukBH){
          window.__fikfukBH=(slot)=>{
            const sl=(slot===undefined)?Math.floor((sharedNow()-EPOCH_ANCHOR)/bhSlotMs):slot;
            const p=bhPos(sl);
            return {slot:sl,x:Math.round(p.x),y:Math.round(p.y),activeNow:((sharedNow()-EPOCH_ANCHOR)%bhSlotMs)<20*60*1000};
          };
        }
      }

      // ── laser hit detection on UFO ──
      const laserWx=laser.active?laserWorld.wx:-9999;
      const laserWy=laser.active?laserWorld.wy:-9999;


      s.worldObjs.forEach(obj=>{
        obj.frame=(obj.frame||0)+1;

        // UFO - drifts, laser shoots it, drops confession
        if(obj.type==="ufo"){
          obj.x+=obj.vx;obj.y+=obj.vy;
          if(obj.x<200||obj.x>WORLD_W-200)obj.vx*=-1;
          if(obj.y<200||obj.y>WORLD_H-200)obj.vy*=-1;
          // laser hit
          if(laser.active&&Math.hypot(laserWx-obj.x,laserWy-obj.y)<40){
            obj.hitCount=(obj.hitCount||0)+1;
            if(obj.hitCount>30){
              // drop confession as breadcrumb
              toAdd.push({
                type:"breadcrumb",id:`bc_${Date.now()}`,
                x:obj.x,y:obj.y,
                text:obj.confession,
                life:600,frame:0,
              });
              toRemove.add(obj.id);
            }
          }
        }

        // Fossil - cat sits nearby to dig, reveals confession
        if(obj.type==="fossil"&&myCat){
          const fdist=Math.hypot(myCat.x-obj.x,myCat.y-obj.y);
          if(fdist<60){
            obj.sitTimer=(obj.sitTimer||0)+1;
            if(obj.sitTimer>180) obj.revealed=true; // 3 seconds
          } else {
            obj.sitTimer=Math.max(0,(obj.sitTimer||0)-1);
          }
        }

        // Wild cat - wanders, bumps player cat
        if(obj.type==="wildcat"){
          obj.wanderTimer--;
          if(obj.wanderTimer<=0){
            obj.wanderAngle+=(Math.random()-0.5)*2;
            obj.wanderTimer=40+Math.random()*80;
            obj.flip=Math.random()>0.5;
          }
          obj.vx+=Math.cos(obj.wanderAngle)*0.8*0.05;
          obj.vy+=Math.sin(obj.wanderAngle)*0.8*0.05;
          obj.vx*=0.9;obj.vy*=0.9;
          obj.x+=obj.vx;obj.y+=obj.vy;
          obj.x=Math.max(100,Math.min(WORLD_W-100,obj.x));
          obj.y=Math.max(100,Math.min(WORLD_H-100,obj.y));
          // bump player cat
          if(myCat){
            const bd=Math.hypot(myCat.x-obj.x,myCat.y-obj.y);
            if(bd<30){
              myCat.vx+=(myCat.x-obj.x)/bd*2;
              myCat.vy+=(myCat.y-obj.y)/bd*2;
            }
          }
        }

        // Mouse - fast wander, cat chases and catches it
        if(obj.type==="mouse"){
          // flee from nearby cats
          let flee=false;
          if(myCat){
            const md=Math.hypot(myCat.x-obj.x,myCat.y-obj.y);
            if(md<120){
              flee=true;
              obj.wanderAngle=Math.atan2(obj.y-myCat.y,obj.x-myCat.x);
              // caught!
              if(md<25){
                toRemove.add(obj.id);
                // speed boost for player cat
                myCat._boostTimer=300;FKAudio.squeak();RECAP.mice++;
                myCat._carry=(WORLD_ID==="malkuth");
                if(!s._carryHint&&WORLD_ID==="malkuth"){
                  s._carryHint=true;
                  s.particles.push({text:"bring it to patates",x:myCat.x-20,y:myCat.y-10,vx:0,vy:-0.4,alpha:1,life:200,delay:0});
                }
              }
            }
          }
          if(!flee){
            obj.wanderTimer--;
            if(obj.wanderTimer<=0){
              obj.wanderAngle+=(Math.random()-0.5)*2;
              obj.wanderTimer=40+Math.random()*60;
            }
          }
          obj.vx+=Math.cos(obj.wanderAngle)*1.2*0.08;
          obj.vy+=Math.sin(obj.wanderAngle)*1.2*0.08;
          obj.vx*=0.88;obj.vy*=0.88;
          obj.x+=obj.vx;obj.y+=obj.vy;
          obj.x=Math.max(100,Math.min(WORLD_W-100,obj.x));
          obj.y=Math.max(100,Math.min(WORLD_H-100,obj.y));
          obj.flip=obj.vx<0;
        }

        // Human NPC - walks slowly, drops confession breadcrumbs
        if(obj.type==="human"){
          obj.wanderTimer--;
          if(obj.wanderTimer<=0){
            obj.wanderAngle+=(Math.random()-0.5)*1;
            obj.wanderTimer=200+Math.random()*300;
          }
          obj.vx+=Math.cos(obj.wanderAngle)*0.02;
          obj.vx*=0.95;obj.x+=obj.vx;
          obj.x=Math.max(200,Math.min(WORLD_W-200,obj.x));
          obj.dropTimer=(obj.dropTimer||0)-1;
          if(obj.dropTimer<=0){
            obj.dropTimer=600;
            toAdd.push({
              type:"breadcrumb",id:`bc_${Date.now()}`,
              x:obj.x,y:obj.y,
              text:NPC_CONFESSIONS[Math.floor(Math.random()*NPC_CONFESSIONS.length)],
              life:900,frame:0,
            });
          }
        }

        // Diablo - roams, spooks cats, takes laser hits
        if(obj.type==="diablo"){
          obj.wanderTimer--;
          if(obj.wanderTimer<=0){
            obj.wanderAngle+=(Math.random()-0.5)*0.5;
            obj.wanderTimer=200+Math.random()*400;
          }
          const diabloSpd=isNight()?0.028:0.015;
          obj.vx+=Math.cos(obj.wanderAngle)*diabloSpd;
          obj.vy+=Math.sin(obj.wanderAngle)*diabloSpd;
          obj.vx*=0.98;obj.vy*=0.98;
          obj.x+=obj.vx;obj.y+=obj.vy;
          obj.x=Math.max(500,Math.min(WORLD_W-500,obj.x));
          obj.y=Math.max(500,Math.min(WORLD_H-500,obj.y));
          // spook cat
          if(myCat){
            const dd=Math.hypot(myCat.x-obj.x,myCat.y-obj.y);
            if(dd<200){
              myCat.vx+=(myCat.x-obj.x)/dd*0.5;
              myCat.vy+=(myCat.y-obj.y)/dd*0.5;
              myCat.state="run";
            }
          }
          // laser damage
          if(obj.hitCooldown>0) obj.hitCooldown--;
          if(laser.active&&obj.hitCooldown===0&&Math.hypot(laserWx-obj.x,laserWy-obj.y)<50){
            obj.hp=(obj.hp||10)-1;
            obj.hitCooldown=30;
            FKAudio.hit(obj.hp);RECAP.hits++;channelRef.current?.publish("dia_hit",{id:obj.id,hp:obj.hp});
            if(obj.hp<=0){
              // defeated - spawn fossil reward nearby
              toAdd.push({
                type:"fossil",id:`fossil_reward_${Date.now()}`,
                x:obj.x+100,y:obj.y+100,
                confession:"u defeated diablo",
                revealed:true,sitTimer:999,frame:0,
              });
              toRemove.add(obj.id);
            }
          }
        }

        // Breadcrumb - fades out over time
        if(obj.type==="breadcrumb"){
          obj.life=(obj.life||0)-1;
          if(obj.life<=0) toRemove.add(obj.id);
        }
        // Paw prints - fade in then out
        if(obj.type==="pawprint"){
          obj.life--;
          if(obj.life<=0) toRemove.add(obj.id);
          else if(obj.life>500) obj.alpha=Math.min(0.7,(600-obj.life)/100*0.7);
          else obj.alpha=Math.max(0,obj.life/500*0.7);
        }
        // Black hole - pulls nearby cats
        if(obj.type==="blackhole"){
          obj.frame++;
          // pull all cats toward it
          s.cats.forEach(cat=>{
            if(cat.isSys) return;
            const dx=obj.x-cat.x, dy=obj.y-cat.y;
            const dist=Math.hypot(dx,dy);
            if(dist<obj.pullRadius&&dist>5){
              const pull=0.3*(1-dist/obj.pullRadius);
              cat.vx+=(dx/dist)*pull;
              cat.vy+=(dy/dist)*pull;
            }
          });
          // laser hit detection
          if(laser.active&&Math.hypot(laserWx-obj.x,laserWy-obj.y)<60){
            obj._hitCooldown=(obj._hitCooldown||0)-1;
            if((obj._hitCooldown||0)<=0){
              obj._hitCooldown=10;
              obj.hp=Math.max(0,obj.hp-1);
              channelRef.current?.publish("blackhole_hit",{});
              if(obj.hp<=0){ s._bhClosedSlot=obj.slot; toRemove.add(obj.id); FKAudio.collapse(); }
            }
          }
        }
      });

      // update ghost cats
      s.cats.forEach(cat=>{
        if(cat.isGhost){
          cat.ghostTimer=(cat.ghostTimer||0)-1;
          cat.ghostAlpha=Math.max(0,(cat.ghostTimer||0)/120);
        }
      });
      s.cats=s.cats.filter(c=>!c.isGhost||c.ghostTimer>0);

      // ── shared-clock paths: same position for every player ──
      {
        const tSec=(sharedNow()-EPOCH_ANCHOR)/1000;
        const PATHS={
          ufo:{ax:1100,ay:600,per:540},
          diablo:{ax:1500,ay:1000,per:720},
          wildcat:{ax:350,ay:250,per:120},
          human:{ax:700,ay:450,per:300},
        };
        s.worldObjs.forEach(obj=>{
          const P0=PATHS[obj.type];
          if(!P0)return;
          if(obj.bx===undefined){
            obj.bx=obj.x;obj.by=obj.y;
            const r=mulberry32(hashStr("path:"+obj.id+(WORLD_ID==="malkuth"?"":":w:"+WORLD_ID)));
            obj.ph1=r()*Math.PI*2;obj.ph2=r()*Math.PI*2;
            obj.k=0.8+r()*0.5; // per-object speed variety
          }
          const w=Math.PI*2/(P0.per/obj.k);
          const nx=obj.bx+P0.ax*Math.sin(w*tSec+obj.ph1);
          const ny=obj.by+P0.ay*Math.sin(w*1.31*tSec+obj.ph2);
          obj.vx=P0.ax*w*Math.cos(w*tSec+obj.ph1); // used for facing
          obj.flip=obj.vx<0;
          obj.x=Math.max(500,Math.min(WORLD_W-500,nx));
          obj.y=Math.max(500,Math.min(WORLD_H-500,ny));
        });
        if(!window.__fikfukLive){
          window.__fikfukLive=()=>s.worldObjs
            .filter(o=>PATHS[o.type])
            .map(o=>o.type+" "+Math.round(o.x)+","+Math.round(o.y));
          // evaluate every path at one fixed time t (seconds since EPOCH_ANCHOR)
          window.__fikfukAt=(t)=>s.worldObjs
            .filter(o=>PATHS[o.type]&&o.bx!==undefined)
            .map(o=>{
              const p=PATHS[o.type];
              const w=Math.PI*2/(p.per/o.k);
              const x=Math.max(500,Math.min(WORLD_W-500,o.bx+p.ax*Math.sin(w*t+o.ph1)));
              const y=Math.max(500,Math.min(WORLD_H-500,o.by+p.ay*Math.sin(w*1.31*t+o.ph2)));
              return o.type+" "+Math.round(x)+","+Math.round(y);
            });
        }
      }

      // patates feeding: deliver a carried mouse
      {
        const patF=s.cats.find(c=>c.sysType==="patates");
        if(patF&&myCat&&myCat._carry&&Math.hypot(myCat.x-patF.x,myCat.y-patF.y)<80){
          myCat._carry=false;
          feedPatates(patF,true);
        }
      }

      // apply removals and additions
      if(toRemove.size>0){
        toRemove.forEach(id=>{
          const o=s.worldObjs.find(x=>x.id===id);
          if(o&&(o.type==="ufo"||o.type==="diablo")){
            s._dead=s._dead||new Set();
            s._dead.add(id);
            channelRef.current?.publish("obj_dead",{id,type:o.type,x:Math.round(o.x),y:Math.round(o.y)});
          }
        });
        s.worldObjs=s.worldObjs.filter(o=>!toRemove.has(o.id));
      }
      if(toAdd.length>0) s.worldObjs.push(...toAdd);

      if(myCat&&myCat._dash>0){myCat._dash--;myCat.vx+=myCat._dx*2.0;myCat.vy+=myCat._dy*2.0;myCat.state="run";if(s.frame%2===0)(s._dashTr||(s._dashTr=[])).push({x:myCat.x,y:myCat.y,flip:myCat.flip,pal:myCat.pal,life:14});myCat._cap=11;}else if(myCat&&myCat._cap>3.5){myCat._cap=Math.max(3.5,myCat._cap*0.9);}
      // apply cat speed boost
      if(myCat&&myCat._boostTimer>0){
        myCat._boostTimer--;
        myCat.vx*=1.02;myCat.vy*=1.02;
      }
      if(myCat&&channelRef.current){
        const now=Date.now();
        /*_portal*/if(!s._hop){const _pt=PORTALS[WORLD_ID]||{};for(const _d in _pt){if(Math.hypot(myCat.x-_pt[_d][0],(myCat.y-_pt[_d][1])*2)<62){hopTo(_d);break;}}}if(s.frame%60===0){const _n=s.cats.filter(c=>!c.isSys&&!c.isGhost).length;s._moveGap=window.__fikfukGap||(_n<=8?250:_n<=16?400:600);}if(now-moveThrottle.current>(s._moveGap||250)){
          const lm=s._lastMove||{x:-1e5,y:-1e5,state:""};
          const moved=Math.hypot(myCat.x-lm.x,myCat.y-lm.y)>3||myCat.state!==lm.state;
          if(moved&&!document.hidden){
            moveThrottle.current=now;
            s._lastMove={x:myCat.x,y:myCat.y,state:myCat.state};
            window.__fikfukPubN=(window.__fikfukPubN||0)+1;
            channelRef.current.publish("move",{x:Math.round(myCat.x),y:Math.round(myCat.y),flip:myCat.flip,state:myCat.state});
          }
        }
      }
      if(s.frame%300===0&&myCat){
        const sess=loadSession();
        if(sess)saveSession({...sess,x:myCat.x,y:myCat.y,confessions:myCat.confessions});
        if(myCat._territory&&myCat._updatePresence)myCat._updatePresence();
      }
      const skyCol=getSkyColor();
      drawSky(ctx,W,H,cam,s.frame,WORLD_ID,skyCol,isNight());drawWeather(ctx,W,H,s.frame,isNight());
      // night overlay - more stars visible at night
      if(isNight()){
        ctx.fillStyle="rgba(0,0,10,0.15)";ctx.fillRect(0,0,W,H);
      }
      // ── white flash on reset ──
      if(s._flashTimer>0){
        s._flashTimer--;
        ctx.fillStyle=`rgba(255,255,255,${s._flashTimer/30})`;
        ctx.fillRect(0,0,W,H);
      }
      {if(s._dh===undefined){try{s._dh=!!localStorage.getItem("fikfuk_dh");}catch(e){s._dh=true;}}if(!s._dh&&s.myId&&s.frame>900&&s.frame<1700){const _a=Math.min(1,(s.frame-900)/60,(1700-s.frame)/60);ctx.save();ctx.font="8px "+ff;ctx.textAlign="center";ctx.fillStyle=`rgba(255,255,255,${0.55*_a})`;ctx.fillText("flick to dash",W/2,H-110);ctx.restore();}if(s._liteNote>0){s._liteNote--;ctx.save();ctx.font="8px "+ff;ctx.textAlign="center";ctx.fillStyle=`rgba(255,255,255,${Math.min(0.6,s._liteNote/60)})`;ctx.fillText("lite graphics on - tap fx to change",W/2,H-110);ctx.restore();}}
      // ── reset spectacle overlay ──
      if(s.frame%8===0){const _me=s.cats.find(c=>c.id===s.myId);if(_me){const _n={dia:0,bh:0,ufo:0,purr:_me._purr?1:0};s.worldObjs.forEach(o=>{if(o.type!=="diablo"&&o.type!=="blackhole"&&o.type!=="ufo")return;const d=Math.hypot(_me.x-o.x,_me.y-o.y);if(o.type==="diablo")_n.dia=Math.max(_n.dia,1-d/700);else if(o.type==="blackhole")_n.bh=Math.max(_n.bh,1-d/((o.pullRadius||300)+250));else _n.ufo=Math.max(_n.ufo,1-d/450);});FKAudio.near(_n);}}FKAudio.countdown(nextResetMs());const msLeft=nextResetMs();
      if(msLeft<60000){
        // sky goes red
        const redAlpha=Math.min(0.6,(60000-msLeft)/60000*0.6);
        ctx.fillStyle=`rgba(180,0,0,${redAlpha})`;
        ctx.fillRect(0,0,W,H);
      }
      if(msLeft<10000){
        // big countdown center screen
        const secs=Math.ceil(msLeft/1000);
        ctx.save();
        ctx.font=`${Math.min(80,W/4)}px ${ff}`;
        ctx.fillStyle=`rgba(255,50,50,${0.8+Math.sin(Date.now()*0.01)*0.2})`;
        ctx.textAlign="center";
        ctx.fillText(secs,W/2,H/2);
        ctx.font=`14px ${ff}`;
        ctx.fillStyle="rgba(255,150,150,0.7)";
        ctx.fillText("the world resets",W/2,H/2+50);
        ctx.restore();
      }
      ctx.save();
      const bx=-cam.x,by=-cam.y;
      ctx.strokeStyle="rgba(255,50,50,0.15)";ctx.lineWidth=3;
      ctx.strokeRect(bx,by,WORLD_W,WORLD_H);
      ctx.restore();
      const nightBoost=isNight()?0.4:0;
      
      for(let gy=0;gy<H;gy+=4){ctx.fillStyle="rgba(0,0,0,0.06)";ctx.fillRect(0,gy,W,2);}

      // glow around fed cats
      s.cats.forEach(c=>{
        if(!c._glowUntil||c._glowUntil<Date.now())return;
        const{sx:gx,sy:gy}=w2s(c.x,c.y);
        if(gx<-100||gx>W+100||gy<-100||gy>H+100)return;
        const left=(c._glowUntil-Date.now())/60000;
        ctx.save();
        ctx.globalAlpha=Math.min(0.35,left*0.5)*(0.8+Math.sin(s.frame*0.06)*0.2);
        const gg=ctx.createRadialGradient(gx+5.5*P,gy+5*P,4,gx+5.5*P,gy+5*P,60);
        gg.addColorStop(0,"rgba(255,190,110,1)");
        gg.addColorStop(1,"rgba(255,190,110,0)");
        ctx.fillStyle=gg;
        ctx.beginPath();ctx.arc(gx+5.5*P,gy+5*P,60,0,Math.PI*2);ctx.fill();
        ctx.restore();
      });

      // chirp ripples
      if(s._chirps&&s._chirps.length){
        s._chirps=s._chirps.filter(c=>c.life>0);
        s._chirps.forEach(c=>{
          c.life--;
          const{sx:rcx,sy:rcy}=w2s(c.x+5.5*P,c.y+5*P);
          const prog=1-c.life/60;
          ctx.save();
          ctx.globalAlpha=Math.max(0,(1-prog)*0.5);
          ctx.strokeStyle="rgba(255,220,150,1)";ctx.lineWidth=2;
          ctx.beginPath();ctx.arc(rcx,rcy,prog*250*((WORLDS[WORLD_ID]||{}).chirpRadius||1),0,Math.PI*2);ctx.stroke();
          ctx.restore();
        });
      }

      // purr circles: 3+ sitting cats close together
      if(s.frame%20===0){
        const sit=s.cats.filter(c=>!c.isSys&&!c.isGhost&&!c.idle&&c.state==="sit");
        s.cats.forEach(c=>{
          c._purr=sit.includes(c)&&sit.filter(o=>o!==c&&Math.hypot(o.x-c.x,o.y-c.y)<((WORLDS[WORLD_ID]||{}).purrRadius||130)).length>=2;
        });
      }
      if(s.myId&&s.ready)beaconTick(s,d=>channelRef.current?.publish("beacon",d));pagesTick(s,d=>channelRef.current?.publish("dig",d));hodTick(s,d=>channelRef.current?.publish("hod",d));sunTick(s,d=>channelRef.current?.publish("sun",d));ventTick(s);if(s.frame%20===0&&s.myId){const _m=s.cats.find(c=>c.id===s.myId);if(_m&&_m._purr)RECAP.purr+=20/60;RECAP.peak=Math.max(RECAP.peak,s.cats.filter(c=>!c.isSys&&!c.isGhost).length);}if(s.frame%600===0&&s.myId)recapSave();if(!window.__fikfukPurr)window.__fikfukPurr=()=>gs.current.cats.filter(c=>c._purr).map(c=>c.name);
      s.cats.forEach(c=>{
        if(!c._purr)return;
        if(c.confessions.length){c.revealAlpha=Math.min(1,c.revealAlpha+0.03);c.revealTimer=40;}
        const{sx:ppx,sy:ppy}=w2s(c.x,c.y);
        if(ppx<-80||ppx>W+80||ppy<-80||ppy>H+80)return;
        ctx.save();
        ctx.globalAlpha=0.18+Math.sin(s.frame*0.08)*0.06;
        ctx.fillStyle="rgba(255,200,120,1)";
        ctx.beginPath();ctx.arc(ppx+5.5*P,ppy+5*P,48*(((WORLDS[WORLD_ID]||{}).purrRadius||130)/130),0,Math.PI*2);ctx.fill();
        ctx.restore();
      });

      // ── Confession Tide ──
      // tide sweeps across world every 15 min (54000 frames)
      const TIDE_PERIOD = 54000;
      const tidePhase = (((sharedNow()-EPOCH_ANCHOR)/1000*60)%TIDE_PERIOD);
      const tideActive = tidePhase < WORLD_W / 2; // active for first half
      if(tideActive){
        // world x position of tide wave front
        const tideWorldX = tidePhase * 2;
        const tideSx = tideWorldX - cam.x;
        // draw wave
        const tideGrad = ctx.createLinearGradient(tideSx-80,0,tideSx+40,0);
        tideGrad.addColorStop(0,"rgba(100,180,255,0)");
        tideGrad.addColorStop(0.5,"rgba(150,210,255,0.12)");
        tideGrad.addColorStop(1,"rgba(100,180,255,0)");
        ctx.fillStyle=tideGrad;
        ctx.fillRect(tideSx-80,0,120,H);
        // reveal confessions of cats the tide touches
        s.cats.forEach(cat=>{
          const{sx:csx}=w2s(cat.x,cat.y);
          if(Math.abs(csx-tideSx)<60&&cat.confessions.length>0){
            cat.revealAlpha=Math.min(1,cat.revealAlpha+0.08);
            cat.revealTimer=90;
          }
        });
      }

      // ── floating confession particles ──
      s.particles=s.particles.filter(p=>p.life>0);
      s.particles.forEach(p=>{
        if(p.delay>0){p.delay--;return;}
        p.life--;
        p.x+=p.vx; p.y+=p.vy;
        p.alpha=Math.min(1,p.life/60);
        const{sx:px,sy:py}=w2s(p.x,p.y);
        ctx.save();
        ctx.globalAlpha=p.alpha*0.85;
        ctx.font=`7px ${ff}`;
        ctx.fillStyle=`hsl(${10+Math.random()*20},80%,75%)`;
        ctx.fillText(p.text,px,py);
        ctx.restore();
      });
      // ── Territories ──
      s.cats.filter(c=>!c.isSys&&c._territory).forEach(c=>{
        const t=c._territory;
        const{sx:tx,sy:ty}=w2s(t.x,t.y);
        if(tx<-t.radius||tx>W+t.radius||ty<-t.radius||ty>H+t.radius)return;
        ctx.save();
        ctx.globalAlpha=0.12;
        ctx.fillStyle=t.palBody||'#ffffff';
        ctx.beginPath();ctx.arc(tx,ty,t.radius,0,Math.PI*2);ctx.fill();
        ctx.globalAlpha=0.25;
        ctx.strokeStyle=t.palBody||'#ffffff';
        ctx.lineWidth=1;
        ctx.setLineDash([4,4]);
        ctx.beginPath();ctx.arc(tx,ty,t.radius,0,Math.PI*2);ctx.stroke();
        ctx.setLineDash([]);
        ctx.globalAlpha=0.4;
        ctx.font=`6px ${ff}`;
        ctx.fillStyle=t.palBody||'#ffffff';
        const tw=ctx.measureText(t.name).width;
        ctx.fillText(t.name,tx-tw/2,ty+t.radius+10);
        ctx.restore();
      });

      // ── Secret Rooms ──
      drawShards(ctx,cam,W,H,s.frame);drawPages(ctx,cam,W,H,s.frame,s);drawVents(ctx,cam,W,H,s.frame);drawSun(ctx,cam,W,H,s.frame,s);drawHod(ctx,cam,W,H,s.frame,s);drawDashTrail(ctx,cam,s);{const _b=beaconGet(WORLD_ID),_bx=_b.x-cam.x,_by=_b.y-cam.y;if(_bx>-220&&_bx<W+220&&_by>-220&&_by<(_b.lit?H+1700:H+220))drawBeacon(ctx,_bx,_by,_b,s.frame);}/*_rings*/{const _pt=PORTALS[WORLD_ID]||{};for(const _d in _pt){const _sx=_pt[_d][0]-cam.x,_sy=_pt[_d][1]-cam.y;if(_sx<-160||_sx>W+160||_sy<-200||_sy>H+100)continue;drawPortal(ctx,_sx,_sy,s.frame,_d);ctx.save();ctx.font="7px "+ff;ctx.textAlign="center";ctx.fillStyle="rgba(255,255,255,0.8)";ctx.fillText(WORLDS[_d].name,_sx,_sy-150);ctx.fillStyle="rgba(255,255,255,0.4)";ctx.fillText("?",_sx,_sy+58);ctx.restore();}}const myCatSR=gs.current.cats.find(c=>c.id===gs.current.myId);
      secretRooms().forEach((room,i)=>{
        const rsx=room.x-cam.x;
        const rsy=room.y-cam.y;
        if(rsx<-room.radius||rsx>W+room.radius||rsy<-room.radius||rsy>H+room.radius)return;
        // check if player is inside
        const inside=myCatSR&&Math.hypot(myCatSR.x-room.x,myCatSR.y-room.y)<room.radius;
        ctx.save();
        if(inside){
          // full reveal
          ctx.globalAlpha=0.85;
          ctx.fillStyle="rgba(0,0,0,0.7)";
          ctx.beginPath();ctx.arc(rsx,rsy,room.radius,0,Math.PI*2);ctx.fill();
          ctx.strokeStyle="rgba(200,150,255,0.4)";ctx.lineWidth=1;ctx.stroke();
          // confession text
          ctx.font=`7px ${ff}`;
          const tw=ctx.measureText(room.confession).width;
          ctx.fillStyle="rgba(220,180,255,0.9)";
          ctx.fillText(room.confession,rsx-tw/2,rsy);
          ctx.font=`6px ${ff}`;
          ctx.fillStyle="rgba(180,140,255,0.5)";
          ctx.fillText("secret room",rsx-22,rsy+16);
        } else {
          // subtle hint from outside
          ctx.globalAlpha=0.15+Math.sin(s.frame*0.03+i)*0.05;
          ctx.fillStyle="rgba(150,100,255,0.3)";
          ctx.beginPath();ctx.arc(rsx,rsy,room.radius,0,Math.PI*2);ctx.fill();
        }
        ctx.restore();
      });

      // ── Draw Confession Wall ──
      const wallSx=WALL_X-cam.x-WALL_W/2;
      const wallSy=WALL_Y-cam.y-WALL_H/2;
      if(wallSx>-WALL_W&&wallSx<W&&wallSy>-WALL_H&&wallSy<H){
        ctx.save();
        // stone wall base
        ctx.fillStyle="#1a1510";
        ctx.fillRect(wallSx,wallSy,WALL_W,WALL_H);
        // stone texture lines
        ctx.strokeStyle="#2a2018";ctx.lineWidth=1;
        for(let wy=0;wy<WALL_H;wy+=30) ctx.strokeRect(wallSx,wallSy+wy,WALL_W,30);
        for(let wx=0;wx<WALL_W;wx+=60) ctx.strokeRect(wallSx+wx,wallSy,60,WALL_H);
        // border
        ctx.strokeStyle="#3a3028";ctx.lineWidth=3;
        ctx.strokeRect(wallSx,wallSy,WALL_W,WALL_H);
        // title
        ctx.font=`7px ${ff}`;ctx.fillStyle="rgba(255,200,100,0.5)";
        ctx.fillText("// wall of confessions",wallSx+10,wallSy+14);
        // confessions on wall
        ctx.font=`6px ${ff}`;
        wallConfessions.forEach(wc=>{
          wc.alpha=Math.min(1,wc.alpha+0.01);
          ctx.globalAlpha=wc.alpha*0.75;
          ctx.fillStyle=`hsl(${30+Math.random()*20},60%,70%)`;
          ctx.fillText(wc.text,wallSx+wc.x,wallSy+wc.y);
        });
        ctx.restore();
        // label above wall
        ctx.save();
        ctx.font=`8px ${ff}`;ctx.fillStyle="rgba(255,200,100,0.4)";
        const labelW=ctx.measureText("the wall").width;
        ctx.fillText("the wall",wallSx+WALL_W/2-labelW/2,wallSy-10);
        ctx.restore();
      }

      s.worldObjs.forEach(obj=>{
        const{sx,sy}=w2s(obj.x,obj.y);
        if(sx<-100||sx>W+100||sy<-100||sy>H+200)return;
        if(obj.type==="ufo")drawUFO(ctx,sx,sy,obj.frame,null);
        if(obj.type==="fossil")drawFossil(ctx,sx,sy,obj.frame,obj.revealed,obj.sitTimer,obj.confession);
        if(obj.type==="wildcat")drawWildCat(ctx,sx,sy,obj.frame,obj.pal,obj.flip);
        if(obj.type==="mouse")drawMouse(ctx,sx,sy,obj.frame,obj.flip);
        if(obj.type==="human")drawHuman(ctx,sx,sy,obj.frame);
        if(obj.type==="diablo")drawDiablo(ctx,sx,sy,obj.frame,obj.hp);
        if(obj.type==="blackhole"){
          ctx.save();
          const pulse=Math.sin(obj.frame*0.05)*0.3;
          // outer glow
          const grd=ctx.createRadialGradient(sx,sy,0,sx,sy,obj.pullRadius);
          grd.addColorStop(0,"rgba(0,0,0,0)");
          grd.addColorStop(0.7,"rgba(50,0,80,0.08)");
          grd.addColorStop(1,"rgba(100,0,150,0.02)");
          ctx.fillStyle=grd;
          ctx.beginPath();ctx.arc(sx,sy,obj.pullRadius,0,Math.PI*2);ctx.fill();
          const coreR=20+pulse*5;
          for(let i=0;i<4;i++){const lf=((obj.frame*0.004+i*0.25)%1),rr=obj.pullRadius*(1-lf*0.9);
            ctx.strokeStyle="rgba(150,60,255,"+(0.12*Math.sin(lf*Math.PI))+")";ctx.lineWidth=2;ctx.beginPath();ctx.arc(sx,sy,rr,0,Math.PI*2);ctx.stroke();}
          const disk=(a0,a1,bright)=>{ctx.save();ctx.translate(sx,sy);ctx.rotate(-0.28);
            const cols=["255,240,200","255,170,60","230,90,200","140,50,230","80,30,160"];
            for(let j=0;j<5;j++){const rx=coreR*(1.8+j*0.7),ry=rx*0.3;ctx.strokeStyle="rgba("+cols[j]+","+(bright*(0.85-j*0.12))+")";ctx.lineWidth=6-j*0.8;
              ctx.setLineDash([16-j,9]);ctx.lineDashOffset=-obj.frame*(1.8-j*0.25);ctx.beginPath();ctx.ellipse(0,0,rx,ry,0,a0,a1);ctx.stroke();}
            ctx.setLineDash([]);ctx.restore();};
          ctx.save();ctx.globalCompositeOperation="lighter";disk(Math.PI,Math.PI*2,0.55);ctx.restore();
          const cg=ctx.createRadialGradient(sx,sy,coreR*0.8,sx,sy,coreR*1.9);
          cg.addColorStop(0,"rgba(100,20,170,0.7)");cg.addColorStop(1,"rgba(100,0,150,0)");
          ctx.fillStyle=cg;ctx.beginPath();ctx.arc(sx,sy,coreR*1.9,0,Math.PI*2);ctx.fill();
          ctx.fillStyle="#000";ctx.beginPath();ctx.arc(sx,sy,coreR,0,Math.PI*2);ctx.fill();
          ctx.strokeStyle="rgba(190,110,255,"+(0.55+pulse*0.3)+")";ctx.lineWidth=2;ctx.beginPath();ctx.arc(sx,sy,coreR+1,0,Math.PI*2);ctx.stroke();
          ctx.strokeStyle="rgba(255,225,255,0.55)";ctx.lineWidth=2;ctx.beginPath();ctx.arc(sx,sy,coreR+1,Math.PI*1.05,Math.PI*1.55);ctx.stroke();
          ctx.save();ctx.globalCompositeOperation="lighter";disk(0,Math.PI,1);ctx.restore();
          ctx.save();ctx.globalCompositeOperation="lighter";
          for(let i=0;i<16;i++){const lf=((obj.frame*0.012+i*0.0625)%1),ang=obj.frame*0.03+i*2.4+lf*5,r=coreR*(4.2-lf*3.3);
            ctx.fillStyle="rgba("+(i%3?"190,120,255":"255,255,255")+","+(0.8*Math.sin(lf*Math.PI))+")";ctx.fillRect(Math.round((sx+Math.cos(ang)*r)/3)*3,Math.round((sy+Math.sin(ang)*r*0.55)/3)*3,3,3);}
          ctx.restore();
          // HP bar
          ctx.fillStyle="rgba(0,0,0,0.5)";ctx.fillRect(sx-30,sy+coreR+8,60,5);
          ctx.fillStyle="rgba(150,0,255,0.8)";ctx.fillRect(sx-30,sy+coreR+8,60*(obj.hp/obj.maxHp),5);
          // label
          ctx.font=`7px ${ff}`;ctx.fillStyle="rgba(180,100,255,0.8)";
          ctx.fillText("laser to close",sx-35,sy+coreR+22);
          ctx.restore();
        }
        if(obj.type==="breadcrumb"){
          const alpha=Math.min(1,(obj.life/60))*0.9;
          ctx.save();ctx.globalAlpha=alpha;
          ctx.font=`7px ${ff}`;
          const tw=ctx.measureText(obj.text).width;
          const bx=sx-tw/2-8,by=sy-16,bw=tw+16,bh=22;
          ctx.fillStyle="rgba(10,20,10,0.85)";
          ctx.strokeStyle="#44ff44";ctx.lineWidth=1;
          rrect(ctx,bx,by,bw,bh,3);
          ctx.fill();ctx.stroke();
          ctx.fillStyle="#aaffaa";
          ctx.fillText(obj.text,sx-tw/2,sy-1);
          ctx.restore();
        }
        if(obj.type==="pawprint"){
          if(obj.alpha>0){
            const{sx:px,sy:py}=w2s(obj.x,obj.y);
            if(px>-20&&px<W+20&&py>-20&&py<H+20){
              ctx.save();
              ctx.globalAlpha=obj.alpha;
              ctx.fillStyle="#e07b39";
              // main pad
              ctx.beginPath();ctx.ellipse(px,py,5,4,0,0,Math.PI*2);ctx.fill();
              // toe beans
              [[-4,-5],[0,-6],[4,-5],[-6,-3],[6,-3]].forEach(([tx,ty])=>{
                ctx.beginPath();ctx.ellipse(px+tx,py+ty,2,2,0,0,Math.PI*2);ctx.fill();
              });
              ctx.restore();
            }
          }
        }
        if(obj.type==="letter"){
          obj.alpha=Math.min(1,(obj.alpha||0)+0.01);
          obj.life=(obj.life||1800)-1;
          if(obj.life<=0){
            s.worldObjs=s.worldObjs.filter(o=>o.id!==obj.id);
          } else {
            const la=obj.alpha*Math.min(1,obj.life/120);
            ctx.save();ctx.globalAlpha=la;
            // pixel envelope instead of emoji
            ctx.fillStyle="rgba(150,180,255,0.8)";
            ctx.fillRect(sx-8,sy-6,16,12);
            ctx.strokeStyle="rgba(100,130,220,0.9)";ctx.lineWidth=1;
            ctx.strokeRect(sx-8,sy-6,16,12);
            // envelope flap lines
            ctx.beginPath();ctx.moveTo(sx-8,sy-6);ctx.lineTo(sx,sy+1);ctx.lineTo(sx+8,sy-6);
            ctx.stroke();
            const myCat2=gs.current.cats.find(c=>c.id===gs.current.myId);
            if(myCat2&&Math.hypot(myCat2.x-obj.x,myCat2.y-obj.y)<80){
              ctx.font=`7px ${ff}`;
              const tw=ctx.measureText(obj.text).width;
              ctx.fillStyle="rgba(8,12,30,0.9)";
              ctx.strokeStyle="rgba(100,150,255,0.7)";ctx.lineWidth=1;
              rrect(ctx,sx-tw/2-8,sy-30,tw+16,20,3);
              ctx.fill();ctx.stroke();
              ctx.fillStyle="rgba(150,180,255,0.95)";
              ctx.fillText(obj.text,sx-tw/2,sy-16);
            }
            ctx.restore();
          }
        }
      });
      s.cats.forEach(c=>{
        const{sx,sy}=w2s(c.x,c.y);
        if(sx<-60||sx>W+60||sy<-60||sy>H+60)return;
        if(!c.grabbed&&!c.isSys&&!c.isGhost){
          ctx.save();ctx.globalAlpha=c.idle?0.08:0.15;ctx.fillStyle="#000";
          ctx.beginPath();ctx.ellipse(sx+7.5*P,sy+13.3*P,20,6.5,0,0,Math.PI*2);ctx.fill();ctx.globalAlpha*=1.6;ctx.beginPath();ctx.ellipse(sx+7*P,sy+13.2*P,15,4.8,0,0,Math.PI*2);ctx.fill();ctx.globalAlpha*=1.4;ctx.beginPath();ctx.ellipse(sx+6.5*P,sy+13*P,10,3.2,0,0,Math.PI*2);ctx.fill();ctx.restore();
        }
        if(c.isGhost){
          ctx.save();
          ctx.globalAlpha=(c.ghostAlpha||0)*0.5;
          // blue-white ghost tint
          ctx.filter="grayscale(1) brightness(2) sepia(0.3) hue-rotate(200deg)";
          drawCat(ctx,sx,sy,P,c.frame,c.pal,c.flip,"sit",false,false,false,true);
          ctx.filter="none";
          ctx.restore();
        } else {
          c._sitT=(c.state==="sit"&&!c.isSys)?(c._sitT||0)+1:0;_catAct=_actFor(c);drawCat(ctx,sx,sy,P,c.frame,c.pal,c.flip,c.state,c.grabbed,c.isOwn,c.isSys,c.idle);_catAct=0;
        }
        drawBubble(ctx,{...c,x:sx,y:sy},P);
        // draw reactions floating above cat
        if(c._reactions&&c._reactions.length>0){
          c._reactions=c._reactions.filter(r=>r.life>0);
          c._reactions.forEach(r=>{
            r.life--;
            r._y=(r._y||0)+r.vy;
            const ra=Math.min(1,r.life/60);
            ctx.save();
            ctx.globalAlpha=ra;
            ctx.font="16px serif";
            ctx.fillText(r.emoji,sx+5.5*P+r.x,sy-20+r._y);
            ctx.restore();
          });
        }
        // draw cat tag
        if(c._tag){
          ctx.save();
          ctx.font="14px serif";
          ctx.globalAlpha=0.9;
          ctx.fillText(c._tag,sx+5.5*P+8,sy-8);
          ctx.restore();
        }
        if(c.isOwn&&c._carry){drawMouse(ctx,sx-6,sy-18,c.frame,c.flip);}
        // mood indicator above own cat
        if(c.isOwn&&!c.isSys&&c.mood&&c.mood!=="neutral"){
          const moodEmoji={scared:"😱",happy:"😻",friendly:"😸"}[c.mood]||"";
          if(moodEmoji){
            ctx.save();
            ctx.font="14px serif";
            ctx.globalAlpha=0.85;
            ctx.fillText(moodEmoji,sx+2*P,sy-12);
            ctx.restore();
          }
        }
      });
      if(laser.active&&!s.camDrag)drawLaser(ctx,laser.sx,laser.sy,s.trail,s.frame);

      // ── joystick draw (only when active) ──
      const joy=s.joystick;
      if(joy.active){
        const JX=joy.startX, JY=joy.startY, JR=50;
        const stickX=Math.min(JR*0.8,Math.max(-JR*0.8,joy.dx));
        const stickY=Math.min(JR*0.8,Math.max(-JR*0.8,joy.dy));
        ctx.save();
        // outer ring
        ctx.globalAlpha=0.3;
        ctx.strokeStyle="#ffffff";ctx.lineWidth=2;
        ctx.beginPath();ctx.arc(JX,JY,JR,0,Math.PI*2);ctx.stroke();
        ctx.globalAlpha=0.08;
        ctx.fillStyle="#ffffff";
        ctx.beginPath();ctx.arc(JX,JY,JR,0,Math.PI*2);ctx.fill();
        // inner stick
        ctx.globalAlpha=0.7;
        ctx.fillStyle="#ffffff";
        ctx.beginPath();ctx.arc(JX+stickX,JY+stickY,20,0,Math.PI*2);ctx.fill();
        ctx.restore();
      }

      // ── whisper UI ──
      const myCatW=s.cats.find(c=>c.id===s.myId);
      if(myCatW&&myCatW._whisperTimer>0){
        const{sx:wx,sy:wy}=w2s(myCatW.x,myCatW.y);
        const pct=myCatW._whisperTimer/180;
        ctx.save();
        ctx.strokeStyle=`rgba(150,180,255,${0.6+pct*0.4})`;
        ctx.lineWidth=2;
        ctx.beginPath();
        ctx.arc(wx+5.5*P,wy+5*P,28,-Math.PI/2,-Math.PI/2+pct*Math.PI*2);
        ctx.stroke();
        ctx.font=`6px ${ff}`;
        ctx.fillStyle="rgba(150,180,255,0.7)";
        ctx.fillText("whispering...",wx-15,wy-30);
        ctx.restore();
      }
      // received whisper
      if(s._whisperMsg){
        s._whisperMsg.life--;
        s._whisperMsg.alpha=Math.min(1,s._whisperMsg.life/60);
        if(s._whisperMsg.life<=0){s._whisperMsg=null;}
        else {
          ctx.save();
          ctx.globalAlpha=s._whisperMsg.alpha;
          ctx.font=`8px ${ff}`;
          const tw=ctx.measureText(s._whisperMsg.text).width;
          ctx.fillStyle="rgba(8,12,30,0.95)";
          ctx.strokeStyle="rgba(150,180,255,0.8)";ctx.lineWidth=1.5;
          rrect(ctx,W/2-tw/2-12,H/2-60,tw+24,32,4);
          ctx.fill();ctx.stroke();
          ctx.fillStyle="rgba(180,210,255,0.95)";
          ctx.fillText("✉ "+s._whisperMsg.text,W/2-tw/2,H/2-40);
          ctx.restore();
        }
      }
      // sent whisper indicator
      if(s._whisperSent){
        s._whisperSent.life--;
        s._whisperSent.alpha=Math.min(1,s._whisperSent.life/30);
        if(s._whisperSent.life<=0){s._whisperSent=null;}
        else {
          ctx.save();
          ctx.globalAlpha=s._whisperSent.alpha;
          ctx.font=`7px ${ff}`;
          ctx.fillStyle="rgba(150,180,255,0.8)";
          ctx.fillText(s._whisperSent.text,W/2-40,H/2-80);
          ctx.restore();
        }
      }
      const MM_W=130,MM_H=90,MM_X=W-MM_W-12,MM_Y=H-MM_H-96;
      ctx.save();
      // background
      const _ac=({malkuth:"150,140,255",yesod:"225,175,255",netzach:"130,225,130",hod:"255,150,80",tiferet:"255,210,100",gevurah:"255,90,110"})[WORLD_ID]||"150,140,255";ctx.fillStyle="rgba(6,6,16,0.72)";ctx.strokeStyle="rgba("+_ac+",0.5)";ctx.lineWidth=1.5;
      rrect(ctx,MM_X,MM_Y,MM_W,MM_H,8);ctx.fill();ctx.stroke();ctx.fillStyle="rgba("+_ac+",0.05)";ctx.fillRect(MM_X+3,MM_Y+3,MM_W-6,(MM_H-6)/2);
      // viewport box
      const vpx=MM_X+(cam.x/WORLD_W)*MM_W;
      const vpy=MM_Y+(cam.y/WORLD_H)*MM_H;
      const vpw=(W/WORLD_W)*MM_W;
      const vph=(H/WORLD_H)*MM_H;
      ctx.strokeStyle="rgba(255,255,255,0.2)";ctx.strokeRect(vpx,vpy,vpw,vph);{const _pp=PORTALS[WORLD_ID]||{};ctx.lineWidth=1.5;ctx.strokeStyle="rgba(200,150,255,0.95)";for(const _k in _pp){ctx.beginPath();ctx.arc(MM_X+(_pp[_k][0]/WORLD_W)*MM_W,MM_Y+(_pp[_k][1]/WORLD_H)*MM_H,2.5,0,Math.PI*2);ctx.stroke();}ctx.lineWidth=1;}
      {ctx.fillStyle="rgba(255,90,70,0.85)";ventsList().forEach(v=>ctx.fillRect(MM_X+(v.x/WORLD_W)*MM_W-1.5,MM_Y+(v.y/WORLD_H)*MM_H-1.5,3,3));}{const _g=sunGet();if(_g)_g.forEach(g=>{ctx.fillStyle=g.on?"rgba(255,235,160,1)":"rgba(255,215,110,0.7)";ctx.fillRect(MM_X+(g.x/WORLD_W)*MM_W-1.5,MM_Y+(g.y/WORLD_H)*MM_H-1.5,3,3);});}{const _h=hodGet();if(_h)_h.br.forEach(b=>{ctx.fillStyle=b.lit?"rgba(255,200,110,1)":"rgba(255,120,60,0.9)";ctx.fillRect(MM_X+(b.x/WORLD_W)*MM_W-2,MM_Y+(b.y/WORLD_H)*MM_H-2,4,4);});}{ctx.fillStyle="rgba(190,255,170,0.9)";pagesList().forEach(o=>{if(o.open)ctx.fillRect(MM_X+(o.x/WORLD_W)*MM_W-1.5,MM_Y+(o.y/WORLD_H)*MM_H-1.5,3,3);});}{ctx.fillStyle="rgba(200,185,255,0.9)";shardList().forEach(o=>ctx.fillRect(MM_X+(o.x/WORLD_W)*MM_W-1.5,MM_Y+(o.y/WORLD_H)*MM_H-1.5,3,3));}{const _b=beaconGet(WORLD_ID);ctx.fillStyle=_b.lit?"rgba(255,225,140,1)":"rgba(160,190,255,0.8)";ctx.fillRect(MM_X+(_b.x/WORLD_W)*MM_W-2,MM_Y+(_b.y/WORLD_H)*MM_H-2,4,4);}// sys cats (policy=purple, about=green)
      s.cats.filter(c=>c.isSys).forEach(c=>{
        const mx=MM_X+(c.x/WORLD_W)*MM_W;
        const my=MM_Y+(c.y/WORLD_H)*MM_H;
        const col=c.sysType==="privacy"?"#7777ff":c.sysType==="patates"?"#ffaa44":c.sysType==="oracle"?"#cc44ff":"#44cc44";
        ctx.fillStyle=col;
        ctx.fillRect(mx-2,my-2,4,4);
        ctx.font="5px monospace";
        ctx.fillStyle=col;
        ctx.fillText(c.sysType==="privacy"?"P":c.sysType==="patates"?"\u2665":c.sysType==="oracle"?"?":"A",mx+3,my+2);
      });
      // player cats with their actual color
      s.cats.filter(c=>!c.isSys).forEach(c=>{
        const mx=MM_X+(c.x/WORLD_W)*MM_W;
        const my=MM_Y+(c.y/WORLD_H)*MM_H;
        if(c.isOwn){
          // own cat - red with pulse
          ctx.fillStyle="#ff4444";
          ctx.beginPath();ctx.arc(mx,my,3,0,Math.PI*2);ctx.fill();
          ctx.strokeStyle="rgba(255,80,80,0.4)";ctx.lineWidth=1;
          ctx.beginPath();ctx.arc(mx,my,5,0,Math.PI*2);ctx.stroke();
        } else {
          // other players - use their body color
          ctx.fillStyle=c.pal?.body??"rgba(150,150,255,0.8)";
          ctx.strokeStyle="rgba(255,255,255,0.4)";ctx.lineWidth=0.5;
          ctx.beginPath();ctx.arc(mx,my,2.5,0,Math.PI*2);ctx.fill();ctx.stroke();
        }
      });
      // world objects
      s.worldObjs.forEach(obj=>{
        const mx=MM_X+(obj.x/WORLD_W)*MM_W;
        const my=MM_Y+(obj.y/WORLD_H)*MM_H;
        if(obj.type==="ufo"){ctx.fillStyle="rgba(100,200,255,0.6)";ctx.fillRect(mx-1,my-1,2,2);}
        if(obj.type==="diablo"){
          ctx.fillStyle="rgba(255,0,0,0.9)";
          ctx.beginPath();ctx.arc(mx,my,3,0,Math.PI*2);ctx.fill();
        }
      // wall on minimap
      const wmx=MM_X+(WALL_X/WORLD_W)*MM_W;
      const wmy=MM_Y+(WALL_Y/WORLD_H)*MM_H;
      ctx.fillStyle="rgba(255,200,100,0.6)";
      ctx.fillRect(wmx-3,wmy-2,6,3);
      // patates paw prints on minimap (subtle)
      s.worldObjs.filter(o=>o.type==="pawprint"&&o.alpha>0.3).forEach(o=>{
        const pmx=MM_X+(o.x/WORLD_W)*MM_W;
        const pmy=MM_Y+(o.y/WORLD_H)*MM_H;
        ctx.fillStyle=`rgba(224,123,57,${o.alpha*0.5})`;
        ctx.fillRect(pmx,pmy,1,1);
      });
      // blackhole on minimap
      const bh=s.worldObjs.find(o=>o.type==="blackhole");
      if(bh){
        const bhmx=MM_X+(bh.x/WORLD_W)*MM_W;
        const bhmy=MM_Y+(bh.y/WORLD_H)*MM_H;
        ctx.fillStyle=`rgba(150,0,255,${0.6+Math.sin(s.frame*0.1)*0.3})`;
        ctx.beginPath();ctx.arc(bhmx,bhmy,4,0,Math.PI*2);ctx.fill();
      }
      // oracle on minimap
      s.cats.filter(c=>c.sysType==="oracle").forEach(c=>{
        const omx=MM_X+(c.x/WORLD_W)*MM_W;
        const omy=MM_Y+(c.y/WORLD_H)*MM_H;
        ctx.fillStyle="rgba(200,68,255,0.8)";
        ctx.beginPath();ctx.arc(omx,omy,3,0,Math.PI*2);ctx.fill();
      });
        if(obj.type==="fossil"&&obj.revealed){
          ctx.fillStyle="rgba(255,220,100,0.6)";ctx.fillRect(mx-1,my-1,2,2);
        }
      });
      // legend
      const LX=MM_X+4, LY=MM_Y+MM_H+8;
      ctx.font="5px monospace";
      const legend=[
        {col:"#ff4444",label:"you"},
        {col:"rgba(150,150,255,0.9)",label:"players"},
        {col:"#7777ff",label:"policy"},
        {col:"#44cc44",label:"about"},
        {col:"rgba(100,200,255,0.7)",label:"ufo"},
        {col:"rgba(255,0,0,0.9)",label:"diablo"},
      ];
      ctx.globalAlpha=Math.max(0,Math.min(1,(1500-s.frame)/300));legend.forEach((l,i)=>{
        const lx=MM_X+(i%3)*(MM_W/3);
        const ly=MM_Y+MM_H+(Math.floor(i/3)*10)+6;
        ctx.fillStyle=l.col;
        ctx.fillRect(lx+2,ly-4,5,5);
        ctx.fillStyle="rgba(255,255,255,0.5)";
        ctx.fillText(l.label,lx+9,ly);
      });
      ctx.restore();
      animRef.current=requestAnimationFrame(tick);
    };
    animRef.current=requestAnimationFrame(tick);
    return()=>{cancelAnimationFrame(animRef.current);window.removeEventListener("resize",resize);};
  },[phase]);

  const getPos=(e)=>{
    const r=canvasRef.current.getBoundingClientRect();
    const src=e.touches?e.touches[0]:e;
    return{sx:src.clientX-r.left,sy:src.clientY-r.top};
  };
  const catAtScreen=(sx,sy)=>{
    const s=gs.current;
    for(let i=s.cats.length-1;i>=0;i--){
      const c=s.cats[i];
      const{sx:cx,sy:cy}=w2s(c.x,c.y);
      if(Math.hypot(sx-(cx+5.5*P),sy-(cy+5*P))<28)return c;
    }
    return null;
  };
  function feedPatates(pat,mine){
    const s=gs.current;
    if(!mine&&pat._glowUntil&&pat._glowUntil>Date.now()+50000)return;
    const line=FEED_LINES[Math.floor(Math.random()*FEED_LINES.length)];FKAudio.feed(mine);
    pat._glowUntil=Date.now()+60000;
    for(let i=0;i<6;i++){
      s.particles.push({text:"<3",x:pat.x+4+i*6,y:pat.y-6,vx:(Math.random()-0.5)*0.6,vy:-0.5-Math.random()*0.5,alpha:1,life:150+i*10,delay:i*6});
    }
    s.particles.push({text:line,x:pat.x-10,y:pat.y-30,vx:0,vy:-0.25,alpha:1,life:260,delay:0});
    if(mine){
      const me=s.cats.find(c=>c.id===s.myId);
      if(me){me._glowUntil=Date.now()+60000;me._boostTimer=300;}
      channelRef.current?.publish("feed",{});
    }
  }
  function applyChirp(x,y,fromId,_r){if(!_r&&WORLD_ID==="yesod")shardRelay(x,y,fromId,applyChirp);
    const s=gs.current;
    s._chirps=s._chirps||[];
    s._chirps.push({x,y,life:60});{const _m=s.cats.find(c=>c.id===s.myId);if(_m){const _d=Math.hypot(_m.x-x,_m.y-y);if(_d<500)FKAudio.chirp(1-_d/500);}}
    s.cats.forEach(c=>{
      if(c.id===fromId||c.isGhost)return;
      if(Math.hypot(c.x-x,c.y-y)<250*((WORLDS[WORLD_ID]||{}).chirpRadius||1)&&c.confessions.length){
        c.revealAlpha=Math.max(c.revealAlpha,0.9);
        c.revealTimer=100;
      }
    });
  }
  /*_dash*/function doDash(dx,dy){
    const s=gs.current,m=s.cats.find(c=>c.id===s.myId);
    if(!m||m.idle||m.grabbed||s.frame<(s._dashCd||0))return;
    const l=Math.hypot(dx,dy)||1;
    s._dashCd=s.frame+150;m._dash=12;m._dx=dx/l;m._dy=dy/l;m.vx+=m._dx*6;m.vy+=m._dy*6;m.flip=dx<0;m.state="run";
    s._dashTr=s._dashTr||[];FKAudio.dash();RECAP.dashes=(RECAP.dashes||0)+1;s._dh=true;
    try{localStorage.setItem("fikfuk_dh","1");}catch(e){}
  }
  function doChirp(){
    const s=gs.current;
    const myCat=s.cats.find(c=>c.id===s.myId);
    if(!myCat||myCat.idle)return;
    const now=Date.now();
    if(now-(s._lastChirp||0)<3000)return;
    s._lastChirp=now;
    applyChirp(myCat.x,myCat.y,myCat.id);
    channelRef.current?.publish("chirp",{x:Math.round(myCat.x),y:Math.round(myCat.y)});
  }
  const onPointerDown=useCallback((e)=>{
    if(phaseRef.current!=="play")return;
    const{sx,sy}=getPos(e);
    const s=gs.current;
    // joystick zone - left quarter of screen, bottom half
    const cv=canvasRef.current;
    if(e.button===2||(e.touches&&e.touches.length>=2)){
      s.joystick={active:false,startX:0,startY:0,dx:0,dy:0};
      s.camDrag={lastSx:sx,lastSy:sy};
      return;
    }
    const cat=catAtScreen(sx,sy);
    // joystick: tap anywhere when laser off and not tapping a cat
    if(!cat&&!s.laserOn&&cv){
      s.joystick={active:true,startX:sx,startY:sy,dx:0,dy:0,t0:Date.now(),maxD:0};
      return;
    }
    const now=Date.now();
    if(cat){
      if(lastTap.current.id===cat.id&&now-lastTap.current.time<400){
        if(cat.sysType==="oracle"){
          const response=ORACLE_RESPONSES[Math.floor(Math.random()*ORACLE_RESPONSES.length)];
          setPanel({catId:cat.id,name:"oracle",confessions:[response],isOwn:false,isSys:true,sysType:"oracle",eye:cat.pal.eye,isOracleResponse:true});
        } else {
          setPanel({catId:cat.id,name:cat.name,confessions:[...cat.confessions],isOwn:cat.isOwn,isSys:cat.isSys,sysType:cat.sysType,eye:cat.pal.eye});
        }
        lastTap.current={id:null,time:0};return;
      }
      lastTap.current={id:cat.id,time:now};
      if(cat.isOwn&&!cat.isSys){
        const wpos=s2w(sx,sy);
        s.drag={catId:cat.id,offX:wpos.wx-cat.x,offY:wpos.wy-cat.y};
        cat.grabbed=true;cat.vx=0;cat.vy=0;
      }
      return;
    }
    lastTap.current={id:null,time:0};
    if(s.laserOn){s.laser={sx,sy,active:true};}
    else{s.camDrag={lastSx:sx,lastSy:sy};}
  },[]);
  const onPointerMove=useCallback((e)=>{
    if(phaseRef.current!=="play")return;
    const s=gs.current;
    const{sx,sy}=getPos(e);
    if(s.joystick?.active){
      s.joystick.dx=sx-s.joystick.startX;
      s.joystick.dy=sy-s.joystick.startY;
      s.joystick.maxD=Math.max(s.joystick.maxD||0,Math.hypot(s.joystick.dx,s.joystick.dy));
      return;
    }
    if(s.drag){
      const wpos=s2w(sx,sy);
      const cat=s.cats.find(c=>c.id===s.drag.catId);
      if(cat){cat.x=wpos.wx-s.drag.offX;cat.y=wpos.wy-s.drag.offY;}
      return;
    }
    if(s.laserOn){
      if(s.laser.active){
        s.laser={sx,sy,active:true};
        s.trail.push({x:sx,y:sy});
        if(s.trail.length>24)s.trail.shift();
      }
      return;
    }
    if(s.camDrag){
      const dx=sx-s.camDrag.lastSx;
      const dy=sy-s.camDrag.lastSy;
      s.cam.x=Math.max(0,Math.min(WORLD_W-canvasRef.current.width,s.cam.x-dx));
      s.cam.y=Math.max(0,Math.min(WORLD_H-canvasRef.current.height,s.cam.y-dy));
      s.camDrag.lastSx=sx;
      s.camDrag.lastSy=sy;
    }
  },[]);
  const onPointerUp=useCallback(()=>{
    const s=gs.current;
    if(s.drag){const cat=s.cats.find(c=>c.id===s.drag.catId);if(cat)cat.grabbed=false;s.drag=null;}
    s.camDrag=null;
    {
      const j=s.joystick;
      if(j&&j.active&&j.t0&&Date.now()-j.t0<250&&(j.maxD||0)<12&&!s.laserOn)doChirp();else if(j&&j.active&&j.t0&&Date.now()-j.t0<230&&Math.hypot(j.dx,j.dy)>=55&&!s.laserOn)doDash(j.dx,j.dy);
    }
    s.joystick={active:false,startX:0,startY:0,dx:0,dy:0};
    if(!s.laserOn){s.laser.active=false;s.trail=[];}
  },[]);
  const onPointerLeave=useCallback(()=>{
    const s=gs.current;
    if(!s.drag){s.laser.active=false;s.trail=[];s.camDrag=null;}
  },[]);
  const toggleLaser=useCallback(()=>{
    const next=!gs.current.laserOn;
    gs.current.laserOn=next;
    if(!next){gs.current.laser.active=false;gs.current.trail=[];}
    setLaserOn(next);
  },[]);
  const centerOnCat=useCallback(()=>{
    const s=gs.current;
    const cv=canvasRef.current;
    const myCat=s.cats.find(c=>c.id===s.myId);
    if(!myCat||!cv)return;
    s.cam={x:myCat.x-cv.width/2,y:myCat.y-cv.height/2};
  },[]);
  const startCooldown=()=>{
    setCooldown(COOLDOWN_SEC);
    const iv=setInterval(()=>setCooldown(p=>{if(p<=1){clearInterval(iv);return 0;}return p-1;}),1000);
  };
  const submitConfession=()=>{
    if(!inputVal.trim()||cooldown>0)return;
    const s=gs.current;
    const myCat=s.cats.find(c=>c.id===s.myId);
    if(!myCat)return;
    myCat.confessions.push(inputVal.trim().slice(0,28));
    if(myCat.confessions.length>5)myCat.confessions.shift();
    const sess=loadSession();
    if(sess)saveSession({...sess,confessions:myCat.confessions});
    if(myCat._updatePresence)myCat._updatePresence();
    // add to confession wall
    const wallEntry={text:inputVal.trim().slice(0,28),x:20+Math.random()*440,y:30+Math.random()*250,alpha:0,id:Date.now()+"_"+Math.random().toString(36).slice(2,6)};
    addToWall(wallEntry.text);FKAudio.confess();RECAP.words++;
    // broadcast to all players
    channelRef.current?.publish("wall",{entry:wallEntry});
    setInputVal("");setShowInput(false);
    startCooldown();
  };
  const panelAccent=panel?.isSys?(panel.sysType==="privacy"?"#7777ff":panel.sysType==="about"?"#44cc44":panel.sysType==="patates"?"#ffaa44":panel.sysType==="oracle"?"#cc44ff":"#ffffff"):(panel?.isOwn?"#ff3232":"rgba(120,120,255,0.7)");
  return(
    <div style={{position:"fixed",inset:0,background:"#080810",fontFamily:ff,overflow:"hidden"}}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
        html,body,#root{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#080810;}
        *{box-sizing:border-box;}
        .pal-swatch{cursor:pointer;transition:transform .12s,box-shadow .15s;}
        .pal-swatch:hover{transform:scale(1.12);}
        .hbtn{transition:transform .12s,filter .15s,box-shadow .15s;cursor:pointer;font-family:'Press Start 2P',monospace;border-radius:12px!important;border-width:1px!important;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);background-image:linear-gradient(180deg,rgba(255,255,255,0.10),rgba(255,255,255,0) 60%)!important;-webkit-tap-highlight-color:transparent;}/*_ui10*/
        /*_gui23*/.hpill{max-width:calc(100vw - 24px);min-width:0;flex-shrink:1}.hpill span{white-space:nowrap}.hbar .hbtn{white-space:nowrap}@media (max-width:480px){.hwide{display:none}.hpill{gap:8px!important;padding:6px 10px!important}.hbar{gap:6px!important;padding:12px 8px 18px!important}.hbar .hbtn{font-size:7px!important;padding:9px 9px!important}}@media (max-width:350px){.hlogo{display:none}.htop{justify-content:center!important}}
        .htut{top:132px!important;bottom:auto!important}@media (max-height:480px){.htut{top:auto!important;bottom:84px!important;left:16px!important;transform:none!important;width:250px!important}}
        .hbtn:hover{filter:brightness(1.35);transform:translateY(-1px);}.hbtn:active{transform:translateY(1px) scale(.98);filter:brightness(1.1);}/*_ui11*/.sheet{border-radius:18px 18px 0 0!important;border-width:1px!important;background:rgba(10,10,24,0.84)!important;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);width:min(100%,560px);left:50%!important;right:auto!important;animation:sheetup .22s ease-out both;box-shadow:0 -12px 40px rgba(0,0,0,0.5)}@keyframes sheetup{from{opacity:0;transform:translate(-50%,24px)}to{opacity:1;transform:translate(-50%,0)}}.sheet input{padding:10px 2px!important;font-size:10px!important;caret-color:#fff}.sheet button{transition:filter .15s,transform .12s;border-radius:10px!important}.sheet button[style*='font-size: 7px']{padding:9px 14px!important}.sheet button:hover,.card button:hover{filter:brightness(1.4)}.sheet button:active,.card button:active{transform:scale(.96)}.scrim{backdrop-filter:blur(5px);-webkit-backdrop-filter:blur(5px);animation:fadein .18s ease-out both}@keyframes fadein{from{opacity:0}to{opacity:1}}.card{border-radius:16px!important;border-width:1px!important;background:linear-gradient(180deg,#15152c,#0b0b1a)!important;animation:pop .2s ease-out both}@keyframes pop{from{opacity:0;transform:scale(.95) translateY(8px)}to{opacity:1;transform:none}}.card button{border-radius:10px!important}
      `}</style>
      <canvas ref={canvasRef}
        style={{position:"absolute",inset:0,width:"100%",height:"100%",display:"block",touchAction:"none",
          cursor:phase==="play"?(laserOn?"none":"grab"):"default",
          opacity:phase==="play"?1:0,pointerEvents:phase==="play"?"auto":"none"}}
        onContextMenu={e=>e.preventDefault()} onMouseDown={onPointerDown} onMouseMove={onPointerMove}
        onMouseUp={onPointerUp} onMouseLeave={onPointerLeave}
        onTouchStart={e=>{e.preventDefault();onPointerDown(e);}}
        onTouchMove={e=>{e.preventDefault();onPointerMove(e);}}
        onTouchEnd={onPointerUp}
      />
      {phase==="loading"&&(
        <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",background:"#080810",zIndex:100}}>
          <span style={{fontSize:10,color:"#ff6666"}}>loading...</span>
        </div>
      )}
      {phase==="onboard"&&(
        <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",background:"#080810",zIndex:100,padding:20,overflowY:"auto"}}>
          <div style={{background:"#0d0d1a",border:"2px solid #ff3232",boxShadow:"0 0 40px rgba(255,50,50,0.2)",padding:28,maxWidth:360,width:"100%",display:"flex",flexDirection:"column",gap:22,margin:"auto"}}>{recap&&(
              <div style={{display:"flex",gap:14,alignItems:"center"}}>
                <img src={recap.img} alt="" onClick={()=>recapDownload(recap)} style={{width:48,height:85,objectFit:"cover",border:"1px solid rgba(255,50,50,0.35)",cursor:"pointer",imageRendering:"pixelated"}}/>
                <div style={{display:"flex",flexDirection:"column",gap:10}}>
                  <div style={{fontSize:7,color:"rgba(255,255,255,0.45)",lineHeight:1.8}}>the last world is gone</div>
                  <div style={{display:"flex",gap:14}}>
                    <button onClick={()=>recapDownload(recap)} style={{background:"transparent",border:"none",color:"#ff6666",fontFamily:ff,fontSize:7,cursor:"pointer",padding:0}}>save</button>
                    {typeof navigator!=="undefined"&&navigator.share&&<button onClick={()=>recapShare(recap)} style={{background:"transparent",border:"none",color:"#ff6666",fontFamily:ff,fontSize:7,cursor:"pointer",padding:0}}>share</button>}
                  </div>
                </div>
              </div>
            )}
            <div>
              <div style={{fontSize:12,color:"#ff4444",letterSpacing:2,textShadow:"0 0 18px rgba(255,50,50,0.55)"}}>fikfuk.wtf</div>
              <div style={{fontSize:6,color:"rgba(255,255,255,0.25)",marginTop:8,lineHeight:2}}>anonymous · resets every 3 hrs · 10k world</div>
            </div>
            <div style={{width:"100%",height:1,background:"rgba(255,50,50,0.2)"}}/>
            <div>
              <div style={{fontSize:7,color:"rgba(255,100,100,0.7)",marginBottom:10}}>// name your cat</div>
              <input maxLength={12} value={pickName} autoFocus
                onChange={e=>setPickName(e.target.value)}
                onKeyDown={e=>{if(e.key==="Enter"&&pickName.trim())requestSpawn(pickName.trim(),pickPal);}}
                placeholder="max 12 chars..."
                style={{background:"transparent",border:"none",borderBottom:"1px solid rgba(255,50,50,0.4)",color:"#fff",fontFamily:ff,fontSize:9,padding:"6px 2px",outline:"none",width:"100%"}}
              />
            </div>
            <div>
              <div style={{fontSize:7,color:"rgba(255,100,100,0.7)",marginBottom:10}}>// pick a coat</div>
              <div style={{display:"flex",gap:8,flexWrap:"wrap"}}>
                {PALETTES.map(p=>(
                  <div key={p.id} className="pal-swatch" onClick={()=>setPickPal(p.id)}
                    style={{width:34,height:34,background:p.body,position:"relative",border:`2px solid ${pickPal===p.id?"#ff3232":"rgba(255,255,255,0.1)"}`,boxShadow:pickPal===p.id?"0 0 14px rgba(255,50,50,0.65)":"none"}}>
                    {pickPal===p.id&&<div style={{position:"absolute",inset:0,background:"rgba(255,50,50,0.15)"}}/>}
                    <div style={{position:"absolute",bottom:3,right:3,width:8,height:8,background:p.eye,border:"1px solid rgba(0,0,0,0.5)"}}/>
                  </div>
                ))}
              </div>
              <div style={{fontSize:6,color:"rgba(255,255,255,0.25)",marginTop:8}}>{PALETTES[pickPal].label}</div>
            </div>
            <button className="hbtn"
              onClick={()=>{if(pickName.trim())requestSpawn(pickName.trim(),pickPal);}}
              style={{fontSize:8,padding:"13px",background:pickName.trim()?"rgba(255,50,50,0.18)":"rgba(30,30,50,0.5)",border:`2px solid ${pickName.trim()?"#ff3232":"rgba(255,50,50,0.2)"}`,color:pickName.trim()?"#ff7777":"rgba(255,100,100,0.3)",boxShadow:pickName.trim()?"0 0 14px rgba(255,50,50,0.3)":"none",cursor:pickName.trim()?"pointer":"not-allowed",letterSpacing:1}}>
              spawn my cat →
            </button>
          </div>
        </div>
      )}
      {phase==="play"&&(<>{/*_tut26*/}
        {tut>0&&(
          <div className="htut" style={{position:"fixed",left:"50%",bottom:84,transform:"translateX(-50%)",width:"calc(100vw - 32px)",maxWidth:300,zIndex:30,boxSizing:"border-box",padding:"14px 16px",background:"rgba(10,10,24,0.9)",border:"1px solid rgba(255,255,255,0.16)",borderRadius:14,backdropFilter:"blur(10px)",WebkitBackdropFilter:"blur(10px)",fontFamily:ff,display:"flex",flexDirection:"column",gap:12}}>
            <div style={{fontSize:7,color:"rgba(255,255,255,0.35)"}}>{tut}/3</div>
            <div style={{fontSize:8,lineHeight:1.9,color:"rgba(255,255,255,0.85)"}}>{["drag anywhere to walk. flick fast to dash.","tap once to chirp. nearby cats reveal what they confessed.","glowing rings are portals to other worlds. every world resets every 3 hours."][tut-1]}</div>
            <div style={{display:"flex",justifyContent:"space-between"}}>
              <button className="hbtn" onClick={()=>{try{localStorage.setItem("fikfuk_tut","1");}catch(e){}setTut(0);}} style={{background:"transparent",border:"none",color:"rgba(255,255,255,0.4)",fontSize:7,padding:"6px 2px"}}>skip</button>
              <button className="hbtn" onClick={()=>{if(tut>=3){try{localStorage.setItem("fikfuk_tut","1");}catch(e){}setTut(0);}else setTut(tut+1);}} style={{background:"rgba(255,50,50,0.14)",border:"1px solid rgba(255,80,80,0.45)",color:"#ff7777",fontSize:7,padding:"7px 12px"}}>{tut>=3?"got it":"next"}</button>
            </div>
          </div>
        )}
        <div className="htop" style={{position:"fixed",top:0,left:0,right:0,zIndex:10,pointerEvents:"none",display:"flex",justifyContent:"space-between",alignItems:"center",padding:"12px 16px",background:"linear-gradient(to bottom,rgba(8,8,16,0.85),transparent)"}}>
          <span className="hlogo" style={{fontSize:9,color:"#ff4444",textShadow:"0 0 12px rgba(255,50,50,0.55)",letterSpacing:1}}>fikfuk.wtf</span>
          <div className="hpill" style={{display:"flex",gap:12,alignItems:"center",padding:"6px 12px",background:"rgba(8,8,16,0.55)",border:"1px solid rgba(255,255,255,0.08)",borderRadius:999,backdropFilter:"blur(8px)",WebkitBackdropFilter:"blur(8px)"}}>
            <div style={{position:"fixed",left:0,top:0,right:0,bottom:0,background:"#000",opacity:fade?1:0,pointerEvents:"none",transition:"opacity 0.3s",zIndex:50}}/><span style={{fontSize:7,color:({"Malkuth Gate":"#b9b1f0","Glass Garden":"#e0c0ff","Root Archive":"#8fd070","Ash Market":"#ffb070","Sun Court":"#ffd96b","Iron Hall":"#ff7a88"})[worldName]||"#fff",textShadow:"0 0 8px currentColor"}}>{worldName}</span><span style={{fontSize:7,color:"rgba(255,255,255,0.3)"}}>🐾 {onlineCount}<span className="hwide"> online</span></span>
            <span style={{fontSize:7,color:"rgba(255,255,255,0.22)"}}><span className="hwide">resets </span>{fmtCountdown(resetIn)}</span>
            <span style={{fontSize:7,color:"rgba(255,255,255,0.22)"}}>{Math.floor(getDayProgress()*100)<25||Math.floor(getDayProgress()*100)>75?"🌙":"☀️"}</span>
          </div>
        </div>
        <button className="hbtn" onClick={centerOnCat}
          style={{position:"fixed",top:50,right:16,zIndex:10,fontSize:7,padding:"6px 10px",background:"rgba(8,8,16,0.7)",border:"1px solid rgba(255,50,50,0.3)",color:"rgba(255,100,100,0.6)"}}>
          find me
        </button>
        <button className="hbtn" onClick={()=>{LITE=!LITE;setLite(LITE);try{localStorage.setItem("fikfuk_lite",LITE?"1":"0");}catch(e){}}} style={{position:"fixed",top:50,right:184,zIndex:10,fontSize:7,padding:"6px 10px",background:"rgba(8,8,16,0.7)",border:"1px solid rgba(255,255,255,0.18)",color:"rgba(255,255,255,0.55)"}}>{lite?"fx lite":"fx full"}</button><button className="hbtn" onClick={()=>{FKAudio.unlock();FKAudio.toggle();setMuted(FKAudio.isMuted());setSndMode(FKAudio.mode());}} style={{position:"fixed",top:50,right:100,zIndex:10,fontSize:7,padding:"6px 10px",background:"rgba(8,8,16,0.7)",border:"1px solid rgba(255,255,255,0.18)",color:"rgba(255,255,255,0.55)"}}>{sndMode==="off"?"sound off":sndMode==="fx"?"music off":"sound on"}</button><div className="hbar" style={{position:"fixed",bottom:0,left:0,right:0,zIndex:20,display:"flex",gap:10,alignItems:"center",justifyContent:"center",padding:"12px 16px 20px",background:"linear-gradient(to top,rgba(8,8,16,0.92),transparent)"}}>
          <button className="hbtn" onClick={toggleLaser}
            style={{fontSize:8,background:laserOn?"rgba(255,50,50,0.22)":"transparent",border:`2px solid ${laserOn?"#ff3232":"rgba(255,50,50,0.45)"}`,color:laserOn?"#ff4444":"rgba(255,100,100,0.6)",padding:"10px 13px",boxShadow:laserOn?"0 0 18px rgba(255,50,50,0.5)":"none"}}>
            {laserOn?"laser on":"laser off"}
          </button>
          {!showInput&&(
            <button className="hbtn" onClick={()=>{if(cooldown===0)setShowInput(true);}}
              style={{fontSize:8,background:cooldown>0?"rgba(40,40,60,0.6)":"transparent",border:`2px solid ${cooldown>0?"rgba(255,50,50,0.25)":"#ff3232"}`,color:cooldown>0?"rgba(255,100,100,0.4)":"#ff6666",padding:"10px 14px",boxShadow:cooldown>0?"none":"0 0 14px rgba(255,50,50,0.35)",cursor:cooldown>0?"not-allowed":"pointer"}}>
              {cooldown>0?`${cooldown}s`:"+ confess"}
            </button>
          )}
          <button className="hbtn" onClick={()=>setShowLetterInput(true)}
            style={{fontSize:8,background:"transparent",border:"2px solid rgba(100,150,255,0.45)",color:"rgba(150,180,255,0.7)",padding:"10px 13px"}}>
            ✉ letter
          </button>
          <button className="hbtn" onClick={()=>setShowTagPicker(true)}
            style={{fontSize:8,background:"transparent",border:"2px solid rgba(255,200,100,0.45)",color:"rgba(255,200,100,0.7)",padding:"10px 13px"}}>
            {myTag||"tag"}
          </button>
        </div>
        {showTagPicker&&(
          <div className="sheet" style={{position:"fixed",bottom:0,left:0,right:0,background:"rgba(8,8,16,0.97)",border:"2px solid rgba(255,200,100,0.6)",borderBottom:"none",padding:"16px",zIndex:30,display:"flex",flexDirection:"column",gap:12}}>
            <span style={{fontSize:8,color:"rgba(255,200,100,0.9)"}}>// pick your tag</span>
            <div style={{display:"flex",gap:10,flexWrap:"wrap"}}>
              {["😺","😸","😹","😻","😼","😽","🙀","😿","😾","🐱","🐈","✨","💀","👻","🔥","💫","🌙","⭐","❤️","💔"].map(e=>(
                <button key={e} onClick={()=>{
                  setMyTag(e);
                  setShowTagPicker(false);
                  const s=gs.current;
                  const myCat=s.cats.find(c=>c.id===s.myId);
                  if(myCat){
                    myCat._tag=e;
                    channelRef.current?.publish("tag",{tag:e});
                  }
                }} style={{fontSize:20,background:"rgba(255,255,255,0.06)",border:"1px solid rgba(255,200,100,0.2)",padding:"6px",cursor:"pointer",borderRadius:4}}>
                  {e}
                </button>
              ))}
            </div>
            <div style={{display:"flex",gap:8,justifyContent:"flex-end"}}>
              {myTag&&<button onClick={()=>{
                setMyTag("");setShowTagPicker(false);
                const s=gs.current;
                const myCat=s.cats.find(c=>c.id===s.myId);
                if(myCat){myCat._tag="";channelRef.current?.publish("tag",{tag:""});}
              }} style={{background:"transparent",border:"1px solid rgba(255,100,100,0.3)",color:"rgba(255,100,100,0.5)",fontFamily:ff,fontSize:7,padding:"6px 10px",cursor:"pointer"}}>remove tag</button>}
              <button onClick={()=>setShowTagPicker(false)} style={{background:"transparent",border:"1px solid rgba(255,255,255,0.15)",color:"rgba(255,255,255,0.35)",fontFamily:ff,fontSize:7,padding:"6px 10px",cursor:"pointer"}}>cancel</button>
            </div>
          </div>
        )}

      {showLetterInput&&(
          <div className="sheet" style={{position:"fixed",bottom:0,left:0,right:0,background:"rgba(8,8,16,0.97)",border:"2px solid rgba(100,150,255,0.6)",borderBottom:"none",boxShadow:"0 0 30px rgba(100,150,255,0.2)",padding:"16px",zIndex:30,display:"flex",flexDirection:"column",gap:10}}>
            <span style={{fontSize:8,color:"rgba(150,180,255,0.9)"}}>// drop a letter here</span>
            <input autoFocus maxLength={40} value={letterVal}
              onChange={e=>setLetterVal(e.target.value)}
              onKeyDown={e=>{
                if(e.key==="Enter"&&letterVal.trim()){
                  const s=gs.current;
                  const myCat=s.cats.find(c=>c.id===s.myId);
                  if(myCat){
                    const letter={id:Date.now()+"_l",x:myCat.x,y:myCat.y-50,text:letterVal.trim().slice(0,40),life:1800,alpha:0};
                    s.worldObjs.push({type:"letter",...letter,frame:0});
                    channelRef.current?.publish("letter",{letter});
                  }
                  setLetterVal("");setShowLetterInput(false);
                }
              }}
              placeholder="leave a message for strangers... (40 chars)"
              style={{background:"transparent",border:"none",borderBottom:"1px solid rgba(100,150,255,0.35)",color:"#fff",fontFamily:ff,fontSize:9,padding:"6px 2px",outline:"none",width:"100%"}}
            />
            <div style={{fontSize:7,color:"rgba(255,255,255,0.22)"}}>→ dropped at your cat's location · anyone can find it</div>
            <div style={{display:"flex",gap:8,justifyContent:"flex-end"}}>
              <button onClick={()=>setShowLetterInput(false)} style={{background:"transparent",border:"1px solid rgba(255,255,255,0.15)",color:"rgba(255,255,255,0.35)",fontFamily:ff,fontSize:7,padding:"6px 10px",cursor:"pointer"}}>cancel</button>
              <button onClick={()=>{
                if(letterVal.trim()){
                  const s=gs.current;
                  const myCat=s.cats.find(c=>c.id===s.myId);
                  if(myCat){
                    const letter={id:Date.now()+"_l",x:myCat.x,y:myCat.y-50,text:letterVal.trim().slice(0,40),life:1800,alpha:0};
                    s.worldObjs.push({type:"letter",...letter,frame:0});
                    channelRef.current?.publish("letter",{letter});
                  }
                  setLetterVal("");setShowLetterInput(false);
                }
              }} style={{background:"rgba(100,150,255,0.15)",border:"1px solid rgba(100,150,255,0.6)",color:"rgba(150,180,255,0.9)",fontFamily:ff,fontSize:7,padding:"6px 12px",cursor:"pointer"}}>drop ✉</button>
            </div>
          </div>
        )}

      {showInput&&(
          <div className="sheet" style={{position:"fixed",bottom:0,left:0,right:0,background:"rgba(8,8,16,0.97)",border:"2px solid #ff3232",borderBottom:"none",boxShadow:"0 0 30px rgba(255,50,50,0.25)",padding:"16px",zIndex:30,display:"flex",flexDirection:"column",gap:10}}>
            <span style={{fontSize:8,color:"#ff6666"}}>// confess to your cat</span>
            <input autoFocus maxLength={28} value={inputVal}
              onChange={e=>setInputVal(e.target.value)}
              onKeyDown={e=>e.key==="Enter"&&submitConfession()}
              placeholder="max 28 chars..."
              style={{background:"transparent",border:"none",borderBottom:"1px solid rgba(255,50,50,0.35)",color:"#fff",fontFamily:ff,fontSize:9,padding:"6px 2px",outline:"none",width:"100%"}}
            />
            <div style={{fontSize:7,color:"rgba(255,255,255,0.22)"}}>only your cat carries this · 30s cooldown</div>
            <div style={{display:"flex",gap:8,justifyContent:"flex-end"}}>
              <button onClick={()=>setShowInput(false)} style={{background:"transparent",border:"1px solid rgba(255,255,255,0.15)",color:"rgba(255,255,255,0.35)",fontFamily:ff,fontSize:7,padding:"6px 10px",cursor:"pointer"}}>cancel</button>
              <button onClick={submitConfession} style={{background:"rgba(255,50,50,0.15)",border:"1px solid #ff3232",color:"#ff7777",fontFamily:ff,fontSize:7,padding:"6px 12px",cursor:"pointer",boxShadow:"0 0 8px rgba(255,50,50,0.3)"}}>send</button>
            </div>
          </div>
        )}
      </>)}
      {panel&&(
        <div className="scrim" style={{position:"fixed",inset:0,zIndex:200,display:"flex",alignItems:"center",justifyContent:"center",background:"rgba(0,0,0,0.65)"}} onClick={()=>setPanel(null)}>
          <div className="card" onClick={e=>e.stopPropagation()} style={{background:"#0d0d1a",border:`2px solid ${panelAccent}`,boxShadow:`0 0 40px ${panelAccent}55`,padding:"20px",minWidth:280,maxWidth:"90vw",display:"flex",flexDirection:"column",gap:12}}>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
              <span style={{fontSize:8,color:panelAccent}}>🐾 {panel.name}{panel.isOwn&&!panel.isSys?" (you)":""}</span>
              <button onClick={()=>setPanel(null)} style={{background:"transparent",border:"none",color:"rgba(255,100,100,0.5)",fontFamily:ff,fontSize:8,cursor:"pointer"}}>x</button>
            </div>
            <div style={{width:"100%",height:1,background:`${panelAccent}44`}}/>
            {!panel.confessions.length
              ?<span style={{fontSize:7,color:"rgba(255,255,255,0.3)"}}>no confessions yet</span>
              :panel.confessions.map((c,i)=>(
                <div key={i} style={{display:"flex",gap:10,padding:"7px 0",borderBottom:i<panel.confessions.length-1?`1px solid ${panelAccent}22`:"none"}}>
                  <span style={{fontSize:7,color:`${panelAccent}99`,minWidth:16}}>{i+1}</span>
                  <span style={{fontSize:8,color:"#ffcccc",lineHeight:1.8}}>{c}</span>
                </div>
              ))
            }
            {panel.sysType==="about"&&(
              <div style={{display:"flex",flexDirection:"column",gap:8,marginTop:4}}>
                <div style={{fontSize:7,color:"#44cc44"}}>donate via solana</div>
                <div onClick={()=>navigator.clipboard?.writeText("3oDULkLmFSXppKGyKLQjE32MSSmDcyAcZL2jWy94rbp2")}
                  style={{fontFamily:"monospace",fontSize:7,color:"rgba(100,255,100,0.7)",background:"rgba(0,255,0,0.06)",border:"1px solid rgba(68,204,68,0.25)",padding:"8px",wordBreak:"break-all",lineHeight:1.8,cursor:"pointer",userSelect:"all"}}>
                  3oDULkLmFSXppKGyKLQjE32MSSmDcyAcZL2jWy94rbp2
                </div>
                <div style={{fontSize:6,color:"rgba(255,255,255,0.2)"}}>tap to copy</div>
              </div>
            )}
            {panel&&!panel.isOwn&&!panel.isSys&&(
              <div style={{display:"flex",gap:8,flexWrap:"wrap",marginTop:4}}>
                {["❤️","😢","👀","🐾","😂","🤯"].map(emoji=>(
                  <button key={emoji} onClick={()=>{
                    const s=gs.current;
                    const targetCat=s.cats.find(c=>c.id===panel.catId);
                    if(targetCat){
                      if(!targetCat._reactions) targetCat._reactions=[];
                      targetCat._reactions.push({emoji,life:180,x:Math.random()*30-15,vy:-0.5-Math.random()*0.3});
                      channelRef.current?.publish("reaction",{targetId:panel.catId,emoji});
                    }
                    setPanel(null);
                  }} style={{background:"rgba(255,255,255,0.08)",border:"1px solid rgba(255,255,255,0.15)",fontSize:16,padding:"4px 8px",cursor:"pointer",borderRadius:4}}>
                    {emoji}
                  </button>
                ))}
              </div>
            )}
            <div style={{fontSize:7,color:"rgba(255,255,255,0.18)",textAlign:"right"}}>tap outside to close</div>
          </div>
        </div>
      )}
      <SpeedInsights/>
    </div>
  );
}
