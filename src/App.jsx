import { useState, useEffect, useRef, useCallback } from "react";
import * as Ably from "ably";
import { SpeedInsights } from "@vercel/speed-insights/react";
import { Analytics } from "@vercel/analytics/react";

const ABLY_KEY = import.meta.env.VITE_ABLY_KEY;
const CHANNEL = "fikfuk-main";

function getClientId(){
  let id = localStorage.getItem("fikfuk_cid");
  if(!id){ id = "u_"+Math.random().toString(36).slice(2,12); localStorage.setItem("fikfuk_cid",id); }
  return id;
}

const PALETTES = [
  { id:0, label:"wheat",   body:"#f5deb3", shadow:"#c8a97e", stripe:"#b8860b", inner:"#ffb6c1", eye:"#2ecc71", pupil:"#1a5c36", nose:"#ff9eb5" },
  { id:1, label:"slate",   body:"#b0c4de", shadow:"#7a9ab5", stripe:"#4a7fa5", inner:"#ffc0cb", eye:"#3498db", pupil:"#1a4f7a", nose:"#ffb6c1" },
  { id:2, label:"ember",   body:"#ff9966", shadow:"#cc5500", stripe:"#cc4400", inner:"#ffccaa", eye:"#f1c40f", pupil:"#7a6000", nose:"#ff8fab" },
  { id:3, label:"void",    body:"#2c2c3e", shadow:"#1a1a2e", stripe:"#3d3d5c", inner:"#ff8fab", eye:"#9b59b6", pupil:"#5b1f8a", nose:"#ffb6c1" },
  { id:4, label:"honey",   body:"#f0e68c", shadow:"#c8b400", stripe:"#daa520", inner:"#fff0a0", eye:"#27ae60", pupil:"#145a32", nose:"#ffb6c1" },
  { id:5, label:"ghost",   body:"#e8e8e8", shadow:"#aaaaaa", stripe:"#888888", inner:"#ffccdd", eye:"#e74c3c", pupil:"#7a0000", nose:"#ff9eb5" },
  { id:6, label:"caramel", body:"#d2691e", shadow:"#8b3a0a", stripe:"#a0522d", inner:"#ffccaa", eye:"#16a085", pupil:"#0a4a3a", nose:"#ffb6c1" },
];

const SYS_PAL_PRIVACY = { body:"#1a1a2e", shadow:"#0d0d1a", stripe:"#2d2d5e", inner:"#c0c0ff", eye:"#7777ff", pupil:"#3333aa", nose:"#aaaaff", _name:"policy" };
const SYS_PAL_ABOUT   = { body:"#1a2e1a", shadow:"#0d1a0d", stripe:"#2d5e2d", inner:"#c0ffc0", eye:"#44cc44", pupil:"#226622", nose:"#aaffaa", _name:"about"  };
const PRIVACY_LINES = ["anonymous","no accounts","no emails","confessions live 3hrs","then wiped forever","no tracking · ever"];
const ABOUT_LINES   = ["fikfuk.wtf","a canvas of strangers","& their pixel cats","built by cruelbites","donate via solana","double-tap to donate"];

function drawCat(ctx, x, y, p, frame, pal, flip, state, grabbed, isOwn, isSys, idle) {
  ctx.save();
  if (idle) ctx.globalAlpha = 0.38;
  ctx.translate(x, y);
  if (flip) { ctx.translate(9*p, 0); ctx.scale(-1, 1); }
  const { body, shadow, stripe, inner, eye, pupil, nose } = pal;
  const bob = grabbed ? 0 : Math.sin(frame * 0.08) * (state === "run" ? 0 : 0.5);
  if (state === "sit") {
    ctx.fillStyle=body; ctx.fillRect(8*p,(6+bob)*p,p,4*p); ctx.fillRect(9*p,(9+bob)*p,p,p);
    ctx.fillStyle=inner; ctx.fillRect(8*p,(7+bob)*p,p,2*p);
  } else {
    const tw=Math.sin(frame*0.18)*2;
    ctx.fillStyle=body;
    ctx.fillRect((7+tw)*p,(3+bob)*p,p,p); ctx.fillRect((8+tw)*p,(4+bob)*p,p,2*p); ctx.fillRect((7+tw)*p,(6+bob)*p,p,p);
    ctx.fillStyle=inner; ctx.fillRect((7+tw)*p,(4+bob)*p,p,2*p);
  }
  ctx.fillStyle=shadow; ctx.fillRect(2*p,(5+bob)*p,7*p,6*p);
  ctx.fillStyle=body;
  ctx.fillRect(2*p,(4+bob)*p,7*p,5*p); ctx.fillRect(1*p,(5+bob)*p,p,3*p); ctx.fillRect(9*p,(5+bob)*p,p,3*p);
  ctx.fillStyle=inner; ctx.fillRect(4*p,(5+bob)*p,3*p,4*p);
  ctx.fillStyle=stripe; ctx.fillRect(2*p,(5+bob)*p,p,2*p); ctx.fillRect(8*p,(5+bob)*p,p,2*p);
  ctx.fillStyle=shadow;
  if (state==="run") {
    const lf=Math.sin(frame*0.28),a=lf*p,b=-lf*p;
    ctx.fillRect(2*p,(9+bob)*p+a,2*p,3*p); ctx.fillRect(5*p,(9+bob)*p+b,2*p,3*p); ctx.fillRect(7*p,(9+bob)*p+a,2*p,3*p);
  } else {
    ctx.fillRect(2*p,(9+bob)*p,2*p,3*p); ctx.fillRect(5*p,(9+bob)*p,2*p,3*p); ctx.fillRect(7*p,(9+bob)*p,2*p,3*p);
  }
  ctx.fillStyle=inner;
  ctx.fillRect(2*p,(11+bob)*p,2*p,p); ctx.fillRect(5*p,(11+bob)*p,2*p,p); ctx.fillRect(7*p,(11+bob)*p,2*p,p);
  ctx.fillStyle=body; ctx.fillRect(3*p,(3+bob)*p,5*p,2*p);
  ctx.fillStyle=shadow; ctx.fillRect(1*p,(bob-0.5)*p,9*p,5*p);
  ctx.fillStyle=body;
  ctx.fillRect(1*p,(bob-1)*p,9*p,5*p); ctx.fillRect(0,bob*p,p,3*p); ctx.fillRect(10*p,bob*p,p,3*p);
  ctx.fillStyle=body; ctx.fillRect(1*p,(bob-3)*p,2*p,3*p); ctx.fillRect(8*p,(bob-3)*p,2*p,3*p);
  ctx.fillStyle=inner; ctx.fillRect(1*p,(bob-2)*p,p,2*p); ctx.fillRect(9*p,(bob-2)*p,p,2*p);
  ctx.fillStyle=shadow; ctx.fillRect(1*p,(bob-3)*p,2*p,p); ctx.fillRect(8*p,(bob-3)*p,2*p,p);
  ctx.fillStyle=stripe;
  ctx.fillRect(4*p,(bob-1)*p,p,2*p); ctx.fillRect(6*p,(bob-1)*p,p,2*p); ctx.fillRect(5*p,bob*p,p,p);
  ctx.fillStyle="rgba(255,150,150,0.35)";
  ctx.fillRect(1*p,(bob+2)*p,2*p,p); ctx.fillRect(8*p,(bob+2)*p,2*p,p);
  const blink=(frame%220>210);
  if (idle||blink) {
    ctx.fillStyle=idle?"#555":"#000";
    ctx.fillRect(2*p,(bob+1)*p,3*p,p); ctx.fillRect(6*p,(bob+1)*p,3*p,p);
  } else {
    ctx.fillStyle=eye; ctx.fillRect(2*p,(bob+1)*p,3*p,2*p); ctx.fillRect(6*p,(bob+1)*p,3*p,2*p);
    ctx.fillStyle=pupil; ctx.fillRect(3*p,(bob+1)*p,p,2*p); ctx.fillRect(7*p,(bob+1)*p,p,2*p);
    ctx.fillStyle="rgba(255,255,255,0.9)"; ctx.fillRect(2*p,(bob+1)*p,p,p); ctx.fillRect(6*p,(bob+1)*p,p,p);
  }
  ctx.fillStyle=nose; ctx.fillRect(4*p,(bob+3)*p,3*p,p); ctx.fillRect(5*p,(bob+3)*p,p,2*p);
  ctx.fillStyle=shadow; ctx.fillRect(4*p,(bob+4)*p,p,p); ctx.fillRect(6*p,(bob+4)*p,p,p);
  ctx.fillStyle="rgba(255,255,255,0.5)";
  ctx.fillRect(-2*p,(bob+2)*p,3*p,1); ctx.fillRect(-p,(bob+3)*p,2*p,1);
  ctx.fillRect(10*p,(bob+2)*p,3*p,1); ctx.fillRect(10*p,(bob+3)*p,2*p,1);
  if (grabbed) {
    const t=frame*0.2; ctx.fillStyle="rgba(255,220,100,0.85)";
    [[3,Math.sin(t)*7-10],[7,Math.cos(t)*7-10],[5,Math.sin(t+1)*6-12]].forEach(([ox,oy])=>ctx.fillRect(ox*p,oy,p,p));
  }
  if (isSys) {
    ctx.strokeStyle=eye; ctx.lineWidth=1;
    ctx.globalAlpha=(idle?0.1:0.35)+Math.sin(frame*0.05)*0.2;
    ctx.beginPath(); ctx.arc(5.5*p,(bob+4)*p,20,0,Math.PI*2); ctx.stroke();
  }
  ctx.restore();
  ctx.save();
  if (idle) ctx.globalAlpha=0.35;
  ctx.font=`${Math.max(6,p*1.5)}px 'Press Start 2P',monospace`;
  const tag=pal._name||"";
  if (tag) {
    const tw2=ctx.measureText(tag).width;
    ctx.fillStyle=isSys?eye:(isOwn?"rgba(255,80,80,0.9)":"rgba(180,180,255,0.6)");
    ctx.fillText(tag, x+5.5*p-tw2/2, y+16*p);
  }
  if (isOwn&&!isSys) {
    ctx.fillStyle="rgba(255,80,80,0.85)";
    ctx.beginPath(); ctx.arc(x+5.5*p,y-6,3,0,Math.PI*2); ctx.fill();
  }
  if (idle&&!isSys) {
    const zx=x+10*p, zy=y-10-Math.sin(frame*0.04)*4;
    ctx.globalAlpha=0.7+Math.sin(frame*0.06)*0.3;
    ctx.font=`${p*2.5}px 'Press Start 2P',monospace`;
    ctx.fillStyle="#aaaaff";
    ctx.fillText("zzz", zx, zy);
  }
  ctx.restore();
}

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
  ctx.save();ctx.globalAlpha=cat.revealAlpha*(cat.idle?0.35:1);
  ctx.font=`${Math.max(7,p*1.8)}px 'Press Start 2P',monospace`;
  const tw=ctx.measureText(text).width,pad=10,bh=26,bw=tw+pad*2;
  const bx=cx-bw/2,by=cy-bh-12;
  ctx.fillStyle="rgba(0,0,0,0.45)";rrect(ctx,bx+2,by+2,bw,bh,4);ctx.fill();
  ctx.fillStyle="#0d0d1a";ctx.strokeStyle="#ff4444";ctx.lineWidth=1.5;
  rrect(ctx,bx,by,bw,bh,4);ctx.fill();ctx.stroke();
  ctx.beginPath();ctx.moveTo(cx-5,by+bh);ctx.lineTo(cx,by+bh+10);ctx.lineTo(cx+5,by+bh);
  ctx.fillStyle="#0d0d1a";ctx.fill();
  ctx.beginPath();ctx.moveTo(cx-5,by+bh);ctx.lineTo(cx,by+bh+10);ctx.lineTo(cx+5,by+bh);
  ctx.strokeStyle="#ff4444";ctx.lineWidth=1.5;ctx.stroke();
  ctx.fillStyle="#ff8888";ctx.fillText(text,bx+pad,by+bh-8);
  ctx.restore();
}

function drawRangeRing(ctx,cat,p){
  if(!cat.showRange)return;
  ctx.save();ctx.globalAlpha=cat.showRange*0.18;
  ctx.beginPath();ctx.arc(cat.x+5.5*p,cat.y+5*p,cat.range,0,Math.PI*2);
  ctx.strokeStyle="#ff4444";ctx.lineWidth=1;ctx.setLineDash([4,4]);ctx.stroke();
  ctx.restore();
}

function genStars(w,h){
  return Array.from({length:90},()=>({
    x:Math.random()*w,y:Math.random()*h,
    r:Math.random()*1.4+0.2,a:Math.random()*0.5+0.15,speed:Math.random()*0.02+0.005
  }));
}

const RESET_MS=3*60*60*1000;
// Fixed anchor so all clients share the same reset clock
const EPOCH_ANCHOR = 1700000000000;
function getEpoch(){return Math.floor((Date.now()-EPOCH_ANCHOR)/RESET_MS);}
function nextResetMs(){return EPOCH_ANCHOR+(getEpoch()+1)*RESET_MS-Date.now();}
function fmtCountdown(ms){
  if(ms<=0)return"00:00:00";
  const h=Math.floor(ms/3600000),m=Math.floor((ms%3600000)/60000),s=Math.floor((ms%60000)/1000);
  return`${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
}
function loadSession(){
  try{const r=localStorage.getItem("fikfuk_s");if(!r)return null;const s=JSON.parse(r);if(s.epoch===getEpoch())return s;}catch(e){}
  return null;
}
function saveSession(d){localStorage.setItem("fikfuk_s",JSON.stringify({...d,epoch:getEpoch()}));}

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
    range:110+Math.random()*140,showRange:0,
    state:"sit",flip:Math.random()>0.5,
    revealAlpha:0,revealTimer:0,
    frame:Math.floor(Math.random()*200),
    wanderAngle:Math.random()*Math.PI*2,
    wanderTimer:Math.floor(Math.random()*120),
    grabbed:false,idle:false,
  };
}

const COOLDOWN_SEC=30;
const ff="'Press Start 2P',monospace";
const P=3;

export default function App(){
  const canvasRef  = useRef(null);
  const clientId   = useRef(getClientId());
  const ablyRef    = useRef(null);
  const channelRef = useRef(null);
  const gs         = useRef({
    cats:[],laser:{x:-999,y:-999,active:false},
    trail:[],stars:[],frame:0,
    drag:null,laserOn:false,myId:null,ready:false,
  });
  const animRef      = useRef(null);
  const phaseRef     = useRef("loading");
  const pendingSpawn = useRef(null);
  const moveThrottle = useRef(0);
  const myClientId  = useRef(null);

  const [phase,       setPhase]       = useState("loading");
  const [pickName,    setPickName]    = useState("");
  const [pickPal,     setPickPal]     = useState(0);
  const [laserOn,     setLaserOn]     = useState(false);
  const [showInput,   setShowInput]   = useState(false);
  const [inputVal,    setInputVal]    = useState("");
  const [cooldown,    setCooldown]    = useState(0);
  const [panel,       setPanel]       = useState(null);
  const [resetIn,     setResetIn]     = useState(nextResetMs());
  const [onlineCount, setOnlineCount] = useState(0);
  const lastTap = useRef({id:null,time:0});

  function buildSysCats(W,H){
    const m=60;
    const pc=makeCat(W*0.12+Math.random()*W*0.15,m+Math.random()*(H-m*2),SYS_PAL_PRIVACY,"policy",false,true,"privacy");
    pc.confessions=[...PRIVACY_LINES];
    const ac=makeCat(W*0.7+Math.random()*W*0.18,m+Math.random()*(H-m*2),SYS_PAL_ABOUT,"about",false,true,"about");
    ac.confessions=[...ABOUT_LINES];
    return[pc,ac];
  }

  const requestSpawn=useCallback((name,palId,restored=null)=>{
    pendingSpawn.current={name,palId,restored};
    phaseRef.current="play";
    setPhase("play");
  },[]);

  // Connect to Ably
  function connectAbly(myCat){
    if(ablyRef.current) ablyRef.current.close();

    const ably = new Ably.Realtime({
      key: ABLY_KEY,
      clientId: clientId.current,
    });
    ablyRef.current = ably;

    const channel = ably.channels.get(CHANNEL);
    channelRef.current = channel;

    const myPresenceData = ()=>({
      name:myCat.name, palId:myCat.palId,
      x:myCat.x, y:myCat.y, flip:myCat.flip,
      confessions:myCat.confessions,
    });

    // ── Presence: who is online ──────────────────────────────────────────
    // Someone entered — add their cat
    channel.presence.subscribe("enter",(member)=>{
      if(member.clientId===clientId.current) return;
      const s=gs.current;
      const d=member.data;
      s.cats=s.cats.filter(c=>c.id!==member.clientId);
      const cat=makeCat(d.x,d.y,d.palId,d.name,false,false,null,member.clientId);
      cat.confessions=d.confessions??[];
      cat.flip=d.flip??false;
      s.cats.push(cat);
      setOnlineCount(s.cats.filter(c=>!c.isSys).length);
    });

    // Someone left — remove their cat
    channel.presence.subscribe("leave",(member)=>{
      const s=gs.current;
      s.cats=s.cats.filter(c=>c.id!==member.clientId);
      setOnlineCount(s.cats.filter(c=>!c.isSys).length);
    });

    // Someone updated their data
    channel.presence.subscribe("update",(member)=>{
      if(member.clientId===clientId.current) return;
      const cat=gs.current.cats.find(c=>c.id===member.clientId);
      if(cat&&member.data.confessions) cat.confessions=member.data.confessions;
      if(cat&&member.data.idle!==undefined) cat.idle=member.data.idle;
    });

    // sync presence when fully loaded
    channel.presence.subscribe("present",(member)=>{
      if(member.clientId===clientId.current) return;
      const s=gs.current;
      if(s.cats.find(c=>c.id===member.clientId)) return;
      const d=member.data;
      if(!d||!d.name) return;
      const cat=makeCat(d.x,d.y,d.palId,d.name,false,false,null,member.clientId);
      cat.confessions=d.confessions??[];
      cat.flip=d.flip??false;
      s.cats.push(cat);
      setOnlineCount(s.cats.filter(c=>!c.isSys).length);
    });

    // ── Messages: movement + reset ───────────────────────────────────────
    channel.subscribe("move",(msg)=>{
      if(msg.clientId===clientId.current) return;
      const cat=gs.current.cats.find(c=>c.id===msg.clientId);
      if(!cat) return;
      const d=msg.data;
      cat.x=d.x;cat.y=d.y;cat.vx=d.vx;cat.vy=d.vy;cat.flip=d.flip;cat.state=d.state;
    });

    channel.subscribe("reset",()=>{
      localStorage.removeItem("fikfuk_s");
      const s=gs.current;
      s.cats=[];s.myId=null;s.ready=false;
      s.laserOn=false;s.laser={x:-999,y:-999,active:false};s.trail=[];
      setLaserOn(false);
      phaseRef.current="onboard";
      setPhase("onboard");
    });

    // ── Enter presence (announces us to everyone) ────────────────────────
    channel.presence.enter(myPresenceData());

    // ── Tab close: leave presence ────────────────────────────────────────
    window.addEventListener("beforeunload",()=>{
      channel.presence.leave();
    });

    // ── Store update fn for later use ────────────────────────────────────
    myCat._updatePresence = ()=>{
      channel.presence.update(myPresenceData());
    };
  }

  // Spawn after canvas mounted
  useEffect(()=>{
    if(phase!=="play")return;
    const raf=requestAnimationFrame(()=>{
      const cv=canvasRef.current;if(!cv)return;
      cv.width=cv.offsetWidth||window.innerWidth;
      cv.height=cv.offsetHeight||window.innerHeight;
      const W=cv.width,H=cv.height;
      const s=gs.current;
      s.stars=genStars(W,H);
      if(pendingSpawn.current){
        const{name,palId,restored}=pendingSpawn.current;
        pendingSpawn.current=null;
        s.cats=buildSysCats(W,H);
        const m=80;
        const ox=restored?.x??m+Math.random()*(W-m*2);
        const oy=restored?.y??m+Math.random()*(H-m*2);
        const myCat=makeCat(ox,oy,palId,name,true,false,null);
        if(restored?.confessions)myCat.confessions=[...restored.confessions];
        s.cats.push(myCat);
        s.myId=myCat.id;
        s.ready=true;
        saveSession({name,palId,catId:myCat.id,confessions:myCat.confessions,x:myCat.x,y:myCat.y});
        setOnlineCount(1);
        connectAbly(myCat);
      }
    });
    return()=>cancelAnimationFrame(raf);
  },[phase]);

  // Session check
  useEffect(()=>{
    const sess=loadSession();
    if(sess){requestSpawn(sess.name,sess.palId,{confessions:sess.confessions,x:sess.x,y:sess.y});}
    else{setPhase("onboard");phaseRef.current="onboard";}
  },[requestSpawn]);

  // Reset countdown
  useEffect(()=>{
    const iv=setInterval(()=>{
      setResetIn(nextResetMs());
      if(nextResetMs()<=1000){
        localStorage.removeItem("fikfuk_s");
        channelRef.current?.publish("reset",{});
      }
    },1000);
    return()=>clearInterval(iv);
  },[]);

  // Visibility → idle
  useEffect(()=>{
    const onVis=()=>{
      const s=gs.current;
      const myCat=s.cats.find(c=>c.id===s.myId);
      if(!myCat)return;
      myCat.idle=document.hidden;
      if(myCat._updatePresence) myCat._updatePresence();
    };
    document.addEventListener("visibilitychange",onVis);
    return()=>document.removeEventListener("visibilitychange",onVis);
  },[]);

  // Game loop
  useEffect(()=>{
    if(phase!=="play")return;
    const cv=canvasRef.current;if(!cv)return;
    const ctx=cv.getContext("2d");
    const resize=()=>{cv.width=cv.offsetWidth||window.innerWidth;cv.height=cv.offsetHeight||window.innerHeight;gs.current.stars=genStars(cv.width,cv.height);};
    window.addEventListener("resize",resize);

    const tick=()=>{
      const s=gs.current;
      if(!s.ready){animRef.current=requestAnimationFrame(tick);return;}
      s.frame++;
      const W=cv.width,H=cv.height;
      const{laser}=s;
      const myCat=s.cats.find(c=>c.id===s.myId);

      s.cats.forEach(cat=>{
        if(cat.grabbed){cat.frame++;cat.state="sit";return;}
        cat.frame++;
        const cx=cat.x+5.5*P,cy=cat.y+5*P;
        const dx=laser.x-cx,dy=laser.y-cy;
        const dist=Math.hypot(dx,dy);
        const inRange=cat.isOwn&&!cat.isSys&&!cat.idle&&laser.active&&dist<cat.range;
        cat.showRange=inRange?Math.min(1,cat.showRange+0.08):Math.max(0,cat.showRange-0.05);
        if(inRange){
          cat.state="run";
          const spd=dist<50?1.2:2.2;
          cat.vx+=(dx/dist)*spd*0.1;cat.vy+=(dy/dist)*spd*0.1;
          cat.flip=dx<0;
          if(dist<70){cat.revealAlpha=Math.min(1,cat.revealAlpha+0.05);cat.revealTimer=80;}
        } else if(cat.isOwn&&!cat.isSys){
          cat.wanderTimer--;
          if(cat.wanderTimer<=0){
            cat.wanderAngle+=(Math.random()-0.5)*1.5;
            cat.wanderTimer=80+Math.random()*140;
            cat.state=Math.random()>0.45?"sit":"run";
          }
          if(cat.state==="run"){cat.vx+=Math.cos(cat.wanderAngle)*0.03;cat.vy+=Math.sin(cat.wanderAngle)*0.03;cat.flip=cat.vx<0;}
        }
        cat.vx*=0.86;cat.vy*=0.86;
        const spd2=Math.hypot(cat.vx,cat.vy);
        if(spd2>3.2){cat.vx=cat.vx/spd2*3.2;cat.vy=cat.vy/spd2*3.2;}
        if(!cat.isSys){cat.x+=cat.vx;cat.y+=cat.vy;}
        const mg=10;
        if(cat.x<mg){cat.x=mg;cat.vx*=-0.5;}
        if(cat.x>W-12*P){cat.x=W-12*P;cat.vx*=-0.5;}
        if(cat.y<mg){cat.y=mg;cat.vy*=-0.5;}
        if(cat.y>H-14*P){cat.y=H-14*P;cat.vy*=-0.5;}
        if(cat.revealTimer>0)cat.revealTimer--;
        else cat.revealAlpha=Math.max(0,cat.revealAlpha-0.025);
      });

      // Broadcast position
      if(myCat&&channelRef.current){
        const now=Date.now();
        if(now-moveThrottle.current>100){
          moveThrottle.current=now;
          channelRef.current.publish("move",{
            x:myCat.x,y:myCat.y,vx:myCat.vx,vy:myCat.vy,
            flip:myCat.flip,state:myCat.state,
          });
        }
      }

      // Persist
      if(s.frame%300===0&&myCat){
        const sess=loadSession();
        if(sess)saveSession({...sess,x:myCat.x,y:myCat.y,confessions:myCat.confessions});
      }

      ctx.fillStyle="#080810";ctx.fillRect(0,0,W,H);
      s.stars.forEach(st=>{
        ctx.beginPath();ctx.arc(st.x,st.y,st.r,0,Math.PI*2);
        ctx.fillStyle=`rgba(200,200,255,${st.a+Math.sin(s.frame*st.speed)*0.12})`;ctx.fill();
      });
      for(let gy=0;gy<H;gy+=4){ctx.fillStyle="rgba(0,0,0,0.07)";ctx.fillRect(0,gy,W,2);}
      s.cats.forEach(c=>drawRangeRing(ctx,c,P));
      s.cats.forEach(c=>{
        if(!c.grabbed&&!c.isSys){
          ctx.save();ctx.globalAlpha=c.idle?0.08:0.18;ctx.fillStyle="#000";
          ctx.beginPath();ctx.ellipse(c.x+5.5*P,c.y+13*P,14,4,0,0,Math.PI*2);ctx.fill();ctx.restore();
        }
        drawCat(ctx,c.x,c.y,P,c.frame,c.pal,c.flip,c.state,c.grabbed,c.isOwn,c.isSys,c.idle);
      });
      s.cats.forEach(c=>drawBubble(ctx,c,P));
      if(laser.active&&!s.drag)drawLaser(ctx,laser.x,laser.y,s.trail,s.frame);
      animRef.current=requestAnimationFrame(tick);
    };
    animRef.current=requestAnimationFrame(tick);
    return()=>{cancelAnimationFrame(animRef.current);window.removeEventListener("resize",resize);};
  },[phase]);

  const getPos=(e)=>{
    const r=canvasRef.current.getBoundingClientRect();
    const src=e.touches?e.touches[0]:e;
    return{x:src.clientX-r.left,y:src.clientY-r.top};
  };
  const catAtPos=(x,y)=>{
    const cats=gs.current.cats;
    for(let i=cats.length-1;i>=0;i--){
      const c=cats[i];
      if(Math.hypot(x-(c.x+5.5*P),y-(c.y+5*P))<28)return c;
    }
    return null;
  };

  const onPointerDown=useCallback((e)=>{
    if(phaseRef.current!=="play")return;
    const{x,y}=getPos(e);
    const s=gs.current;
    const cat=catAtPos(x,y);
    const now=Date.now();
    if(cat){
      if(lastTap.current.id===cat.id&&now-lastTap.current.time<400){
        setPanel({catId:cat.id,name:cat.name,confessions:[...cat.confessions],isOwn:cat.isOwn,isSys:cat.isSys,sysType:cat.sysType,eye:cat.pal.eye});
        lastTap.current={id:null,time:0};return;
      }
      lastTap.current={id:cat.id,time:now};
      if(cat.isOwn&&!cat.isSys){
        s.drag={catId:cat.id,offX:x-cat.x,offY:y-cat.y};
        cat.grabbed=true;cat.vx=0;cat.vy=0;
      }
      return;
    }
    lastTap.current={id:null,time:0};
    if(s.laserOn)s.laser={x,y,active:true};
  },[]);

  const onPointerMove=useCallback((e)=>{
    if(phaseRef.current!=="play")return;
    const{x,y}=getPos(e);
    const s=gs.current;
    if(s.drag){
      const cat=s.cats.find(c=>c.id===s.drag.catId);
      if(cat){cat.x=x-s.drag.offX;cat.y=y-s.drag.offY;}
      return;
    }
    if(s.laserOn){
      s.laser={x,y,active:true};
      s.trail.push({x,y});
      if(s.trail.length>24)s.trail.shift();
    }
  },[]);

  const onPointerUp=useCallback(()=>{
    const s=gs.current;
    if(s.drag){const cat=s.cats.find(c=>c.id===s.drag.catId);if(cat)cat.grabbed=false;s.drag=null;}
    if(!s.laserOn){s.laser.active=false;s.trail=[];}
  },[]);

  const onPointerLeave=useCallback(()=>{
    const s=gs.current;
    if(!s.drag){s.laser.active=false;s.trail=[];}
  },[]);

  const toggleLaser=useCallback(()=>{
    const next=!gs.current.laserOn;
    gs.current.laserOn=next;
    if(!next){gs.current.laser.active=false;gs.current.trail=[];}
    setLaserOn(next);
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
    if(myCat._updatePresence) myCat._updatePresence();
    setInputVal("");setShowInput(false);
    startCooldown();
  };

  const panelAccent=panel?.isSys?(panel.sysType==="privacy"?"#7777ff":"#44cc44"):(panel?.isOwn?"#ff3232":"rgba(120,120,255,0.7)");

  return(
    <div style={{width:"100%",height:"100dvh",background:"#080810",position:"relative",overflow:"hidden",fontFamily:ff}}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
        html,body,#root{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#080810;}
        *{box-sizing:border-box;margin:0;padding:0;}
        .pal-swatch{cursor:pointer;transition:transform .12s,box-shadow .15s;}
        .pal-swatch:hover{transform:scale(1.12);}
        .hbtn{transition:background .15s,box-shadow .15s;cursor:pointer;font-family:${ff};}
        .hbtn:hover{background:rgba(255,50,50,0.2)!important;box-shadow:0 0 20px rgba(255,50,50,0.55)!important;}
      `}</style>

      <canvas ref={canvasRef}
        style={{display:"block",position:"absolute",inset:0,width:"100%",height:"100%",touchAction:"none",cursor:phase==="play"?(laserOn?"none":"grab"):"default",opacity:phase==="play"?1:0,pointerEvents:phase==="play"?"auto":"none"}}
        onMouseDown={onPointerDown} onMouseMove={onPointerMove}
        onMouseUp={onPointerUp} onMouseLeave={onPointerLeave}
        onTouchStart={e=>{e.preventDefault();onPointerDown(e);}}
        onTouchMove={e=>{e.preventDefault();onPointerMove(e);}}
        onTouchEnd={onPointerUp}
      />

      {phase==="loading"&&(
        <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",background:"#080810",zIndex:100}}>
          <span style={{fontFamily:ff,fontSize:10,color:"#ff6666"}}>loading...</span>
        </div>
      )}

      {phase==="onboard"&&(
        <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",background:"#080810",zIndex:100,padding:20}}>
          <div style={{background:"#0d0d1a",border:"2px solid #ff3232",boxShadow:"0 0 40px rgba(255,50,50,0.2)",padding:28,maxWidth:360,width:"100%",display:"flex",flexDirection:"column",gap:22}}>
            <div>
              <div style={{fontFamily:ff,fontSize:12,color:"#ff4444",letterSpacing:2,textShadow:"0 0 18px rgba(255,50,50,0.55)"}}>fikfuk.wtf</div>
              <div style={{fontFamily:ff,fontSize:6,color:"rgba(255,255,255,0.25)",marginTop:8,lineHeight:2}}>anonymous · resets every 3 hrs</div>
            </div>
            <div style={{width:"100%",height:1,background:"rgba(255,50,50,0.2)"}}/>
            <div>
              <div style={{fontFamily:ff,fontSize:7,color:"rgba(255,100,100,0.7)",marginBottom:10}}>// name your cat</div>
              <input maxLength={12} value={pickName} autoFocus
                onChange={e=>setPickName(e.target.value)}
                onKeyDown={e=>{if(e.key==="Enter"&&pickName.trim())requestSpawn(pickName.trim(),pickPal);}}
                placeholder="max 12 chars..."
                style={{background:"transparent",border:"none",borderBottom:"1px solid rgba(255,50,50,0.4)",color:"#fff",fontFamily:ff,fontSize:9,padding:"6px 2px",outline:"none",width:"100%"}}
              />
            </div>
            <div>
              <div style={{fontFamily:ff,fontSize:7,color:"rgba(255,100,100,0.7)",marginBottom:10}}>// pick a coat</div>
              <div style={{display:"flex",gap:8,flexWrap:"wrap"}}>
                {PALETTES.map(p=>(
                  <div key={p.id} className="pal-swatch" onClick={()=>setPickPal(p.id)}
                    style={{width:34,height:34,background:p.body,position:"relative",border:`2px solid ${pickPal===p.id?"#ff3232":"rgba(255,255,255,0.1)"}`,boxShadow:pickPal===p.id?"0 0 14px rgba(255,50,50,0.65)":"none"}}>
                    {pickPal===p.id&&<div style={{position:"absolute",inset:0,background:"rgba(255,50,50,0.15)"}}/>}
                    <div style={{position:"absolute",bottom:3,right:3,width:8,height:8,background:p.eye,border:"1px solid rgba(0,0,0,0.5)"}}/>
                  </div>
                ))}
              </div>
              <div style={{fontFamily:ff,fontSize:6,color:"rgba(255,255,255,0.25)",marginTop:8}}>{PALETTES[pickPal].label}</div>
            </div>
            <button className="hbtn"
              onClick={()=>{if(pickName.trim())requestSpawn(pickName.trim(),pickPal);}}
              style={{fontSize:8,padding:"13px",background:pickName.trim()?"rgba(255,50,50,0.18)":"rgba(30,30,50,0.5)",border:`2px solid ${pickName.trim()?"#ff3232":"rgba(255,50,50,0.2)"}`,color:pickName.trim()?"#ff7777":"rgba(255,100,100,0.3)",boxShadow:pickName.trim()?"0 0 14px rgba(255,50,50,0.3)":"none",cursor:pickName.trim()?"pointer":"not-allowed",letterSpacing:1}}>
              spawn my cat →
            </button>
          </div>
        </div>
      )}

      {phase==="play"&&(<>
        <div style={{position:"fixed",top:0,left:0,right:0,zIndex:10,pointerEvents:"none",display:"flex",justifyContent:"space-between",alignItems:"center",padding:"12px 16px",background:"linear-gradient(to bottom,rgba(8,8,16,0.85),transparent)"}}>
          <span style={{fontSize:9,color:"#ff4444",textShadow:"0 0 12px rgba(255,50,50,0.55)",letterSpacing:1}}>fikfuk.wtf</span>
          <div style={{display:"flex",gap:12,alignItems:"center"}}>
            <span style={{fontSize:7,color:"rgba(255,255,255,0.3)"}}>🐾 {onlineCount} online</span>
            <span style={{fontSize:7,color:"rgba(255,255,255,0.22)"}}>resets {fmtCountdown(resetIn)}</span>
          </div>
        </div>

        <div style={{position:"fixed",bottom:0,left:0,right:0,zIndex:20,display:"flex",gap:10,alignItems:"center",justifyContent:"center",padding:"12px 16px 20px",background:"linear-gradient(to top,rgba(8,8,16,0.92),transparent)"}}>
          <button className="hbtn" onClick={toggleLaser} style={{fontSize:8,background:laserOn?"rgba(255,50,50,0.22)":"transparent",border:`2px solid ${laserOn?"#ff3232":"rgba(255,50,50,0.45)"}`,color:laserOn?"#ff4444":"rgba(255,100,100,0.6)",padding:"10px 13px",boxShadow:laserOn?"0 0 18px rgba(255,50,50,0.5)":"none"}}>
            {laserOn?"🔴 laser on":"⭕ laser off"}
          </button>
          {!showInput&&(
            <button className="hbtn" onClick={()=>{if(cooldown===0)setShowInput(true);}} style={{fontSize:8,background:cooldown>0?"rgba(40,40,60,0.6)":"transparent",border:`2px solid ${cooldown>0?"rgba(255,50,50,0.25)":"#ff3232"}`,color:cooldown>0?"rgba(255,100,100,0.4)":"#ff6666",padding:"10px 14px",boxShadow:cooldown>0?"none":"0 0 14px rgba(255,50,50,0.35)",cursor:cooldown>0?"not-allowed":"pointer"}}>
              {cooldown>0?`⏳ ${cooldown}s`:"+ confess"}
            </button>
          )}
        </div>

        {showInput&&(
          <div style={{position:"fixed",bottom:0,left:0,right:0,background:"rgba(8,8,16,0.97)",border:"2px solid #ff3232",borderBottom:"none",boxShadow:"0 0 30px rgba(255,50,50,0.25)",padding:"16px",zIndex:30,display:"flex",flexDirection:"column",gap:10}}>
            <span style={{fontSize:8,color:"#ff6666"}}>// confess to your cat</span>
            <input autoFocus maxLength={28} value={inputVal}
              onChange={e=>setInputVal(e.target.value)}
              onKeyDown={e=>e.key==="Enter"&&submitConfession()}
              placeholder="max 28 chars..."
              style={{background:"transparent",border:"none",borderBottom:"1px solid rgba(255,50,50,0.35)",color:"#fff",fontFamily:ff,fontSize:9,padding:"6px 2px",outline:"none",width:"100%"}}
            />
            <div style={{fontSize:7,color:"rgba(255,255,255,0.22)"}}>→ only your cat carries this · 30s cooldown</div>
            <div style={{display:"flex",gap:8,justifyContent:"flex-end"}}>
              <button onClick={()=>setShowInput(false)} style={{background:"transparent",border:"1px solid rgba(255,255,255,0.15)",color:"rgba(255,255,255,0.35)",fontFamily:ff,fontSize:7,padding:"6px 10px",cursor:"pointer"}}>cancel</button>
              <button onClick={submitConfession} style={{background:"rgba(255,50,50,0.15)",border:"1px solid #ff3232",color:"#ff7777",fontFamily:ff,fontSize:7,padding:"6px 12px",cursor:"pointer",boxShadow:"0 0 8px rgba(255,50,50,0.3)"}}>send →</button>
            </div>
          </div>
        )}
      </>)}

      {panel&&(
        <div style={{position:"fixed",inset:0,zIndex:200,display:"flex",alignItems:"center",justifyContent:"center",background:"rgba(0,0,0,0.65)"}} onClick={()=>setPanel(null)}>
          <div onClick={e=>e.stopPropagation()} style={{background:"#0d0d1a",border:`2px solid ${panelAccent}`,boxShadow:`0 0 40px ${panelAccent}55`,padding:"20px",minWidth:280,maxWidth:"90vw",display:"flex",flexDirection:"column",gap:12}}>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
              <span style={{fontSize:8,color:panelAccent}}>🐾 {panel.name}{panel.isOwn&&!panel.isSys?" (you)":""}</span>
              <button onClick={()=>setPanel(null)} style={{background:"transparent",border:"none",color:"rgba(255,100,100,0.5)",fontFamily:ff,fontSize:8,cursor:"pointer"}}>✕</button>
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
                <div style={{fontSize:7,color:"#44cc44"}}>◎ donate via solana</div>
                <div onClick={()=>navigator.clipboard?.writeText("3oDULkLmFSXppKGyKLQjE32MSSmDcyAcZL2jWy94rbp2")}
                  style={{fontFamily:"monospace",fontSize:7,color:"rgba(100,255,100,0.7)",background:"rgba(0,255,0,0.06)",border:"1px solid rgba(68,204,68,0.25)",padding:"8px",wordBreak:"break-all",lineHeight:1.8,cursor:"pointer",userSelect:"all"}}>
                  3oDULkLmFSXppKGyKLQjE32MSSmDcyAcZL2jWy94rbp2
                </div>
                <div style={{fontSize:6,color:"rgba(255,255,255,0.2)"}}>tap address to copy</div>
              </div>
            )}
            <div style={{fontSize:7,color:"rgba(255,255,255,0.18)",textAlign:"right"}}>tap outside to close</div>
          </div>
        </div>
      )}
      <SpeedInsights />
      <Analytics />
    </div>
  );
}
