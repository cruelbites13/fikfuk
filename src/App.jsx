import { useState, useEffect, useRef, useCallback } from "react";
import * as Ably from "ably";
import { SpeedInsights } from "@vercel/speed-insights/react";

const ABLY_KEY  = import.meta.env.VITE_ABLY_KEY;
const CHANNEL   = "fikfuk-main";
const WORLD_W   = 10000;
const WORLD_H   = 10000;
const RESET_MS  = 3 * 60 * 60 * 1000;
const EPOCH_ANCHOR = 1700000000000;
const P = 3; // pixel scale
const ff = "'Press Start 2P',monospace";

// ─── Session / identity ───────────────────────────────────────────────────────
function getClientId(){
  let id = localStorage.getItem("fikfuk_cid");
  if(!id){ id="u_"+Math.random().toString(36).slice(2,12); localStorage.setItem("fikfuk_cid",id); }
  return id;
}
function getEpoch(){ return Math.floor((Date.now()-EPOCH_ANCHOR)/RESET_MS); }
function nextResetMs(){ return EPOCH_ANCHOR+(getEpoch()+1)*RESET_MS-Date.now(); }
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

// ─── Cat renderer ─────────────────────────────────────────────────────────────
function drawCat(ctx,x,y,p,frame,pal,flip,state,grabbed,isOwn,isSys,idle){
  ctx.save();
  if(idle) ctx.globalAlpha=0.38;
  ctx.translate(x,y);
  if(flip){ctx.translate(9*p,0);ctx.scale(-1,1);}
  const{body,shadow,stripe,inner,eye,pupil,nose}=pal;
  const bob=grabbed?0:Math.sin(frame*0.08)*(state==="run"?0:0.5);
  if(state==="sit"){
    ctx.fillStyle=body;ctx.fillRect(8*p,(6+bob)*p,p,4*p);ctx.fillRect(9*p,(9+bob)*p,p,p);
    ctx.fillStyle=inner;ctx.fillRect(8*p,(7+bob)*p,p,2*p);
  } else {
    const tw=Math.sin(frame*0.18)*2;
    ctx.fillStyle=body;
    ctx.fillRect((7+tw)*p,(3+bob)*p,p,p);ctx.fillRect((8+tw)*p,(4+bob)*p,p,2*p);ctx.fillRect((7+tw)*p,(6+bob)*p,p,p);
    ctx.fillStyle=inner;ctx.fillRect((7+tw)*p,(4+bob)*p,p,2*p);
  }
  ctx.fillStyle=shadow;ctx.fillRect(2*p,(5+bob)*p,7*p,6*p);
  ctx.fillStyle=body;
  ctx.fillRect(2*p,(4+bob)*p,7*p,5*p);ctx.fillRect(1*p,(5+bob)*p,p,3*p);ctx.fillRect(9*p,(5+bob)*p,p,3*p);
  ctx.fillStyle=inner;ctx.fillRect(4*p,(5+bob)*p,3*p,4*p);
  ctx.fillStyle=stripe;ctx.fillRect(2*p,(5+bob)*p,p,2*p);ctx.fillRect(8*p,(5+bob)*p,p,2*p);
  ctx.fillStyle=shadow;
  if(state==="run"){
    const lf=Math.sin(frame*0.28),a=lf*p,b=-lf*p;
    ctx.fillRect(2*p,(9+bob)*p+a,2*p,3*p);ctx.fillRect(5*p,(9+bob)*p+b,2*p,3*p);ctx.fillRect(7*p,(9+bob)*p+a,2*p,3*p);
  } else {
    ctx.fillRect(2*p,(9+bob)*p,2*p,3*p);ctx.fillRect(5*p,(9+bob)*p,2*p,3*p);ctx.fillRect(7*p,(9+bob)*p,2*p,3*p);
  }
  ctx.fillStyle=inner;
  ctx.fillRect(2*p,(11+bob)*p,2*p,p);ctx.fillRect(5*p,(11+bob)*p,2*p,p);ctx.fillRect(7*p,(11+bob)*p,2*p,p);
  ctx.fillStyle=body;ctx.fillRect(3*p,(3+bob)*p,5*p,2*p);
  ctx.fillStyle=shadow;ctx.fillRect(1*p,(bob-0.5)*p,9*p,5*p);
  ctx.fillStyle=body;
  ctx.fillRect(1*p,(bob-1)*p,9*p,5*p);ctx.fillRect(0,bob*p,p,3*p);ctx.fillRect(10*p,bob*p,p,3*p);
  ctx.fillStyle=body;ctx.fillRect(1*p,(bob-3)*p,2*p,3*p);ctx.fillRect(8*p,(bob-3)*p,2*p,3*p);
  ctx.fillStyle=inner;ctx.fillRect(1*p,(bob-2)*p,p,2*p);ctx.fillRect(9*p,(bob-2)*p,p,2*p);
  ctx.fillStyle=shadow;ctx.fillRect(1*p,(bob-3)*p,2*p,p);ctx.fillRect(8*p,(bob-3)*p,2*p,p);
  ctx.fillStyle=stripe;
  ctx.fillRect(4*p,(bob-1)*p,p,2*p);ctx.fillRect(6*p,(bob-1)*p,p,2*p);ctx.fillRect(5*p,bob*p,p,p);
  ctx.fillStyle="rgba(255,150,150,0.35)";
  ctx.fillRect(1*p,(bob+2)*p,2*p,p);ctx.fillRect(8*p,(bob+2)*p,2*p,p);
  const blink=(frame%220>210);
  if(idle||blink){
    ctx.fillStyle=idle?"#555":"#000";
    ctx.fillRect(2*p,(bob+1)*p,3*p,p);ctx.fillRect(6*p,(bob+1)*p,3*p,p);
  } else {
    ctx.fillStyle=eye;ctx.fillRect(2*p,(bob+1)*p,3*p,2*p);ctx.fillRect(6*p,(bob+1)*p,3*p,2*p);
    ctx.fillStyle=pupil;ctx.fillRect(3*p,(bob+1)*p,p,2*p);ctx.fillRect(7*p,(bob+1)*p,p,2*p);
    ctx.fillStyle="rgba(255,255,255,0.9)";ctx.fillRect(2*p,(bob+1)*p,p,p);ctx.fillRect(6*p,(bob+1)*p,p,p);
  }
  ctx.fillStyle=nose;ctx.fillRect(4*p,(bob+3)*p,3*p,p);ctx.fillRect(5*p,(bob+3)*p,p,2*p);
  ctx.fillStyle=shadow;ctx.fillRect(4*p,(bob+4)*p,p,p);ctx.fillRect(6*p,(bob+4)*p,p,p);
  ctx.fillStyle="rgba(255,255,255,0.5)";
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
  if(isOwn&&!isSys){ctx.fillStyle="rgba(255,80,80,0.85)";ctx.beginPath();ctx.arc(x+5.5*p,y-6,3,0,Math.PI*2);ctx.fill();}
  if(idle&&!isSys){
    ctx.globalAlpha=0.7+Math.sin(frame*0.06)*0.3;
    ctx.font=`${p*2.5}px ${ff}`;ctx.fillStyle="#aaaaff";
    ctx.fillText("zzz",x+10*p,y-10-Math.sin(frame*0.04)*4);
  }
  ctx.restore();
}

// ─── World objects renderer ───────────────────────────────────────────────────
function drawUFO(ctx,x,y,frame,confession,hitCount){
  ctx.save();ctx.translate(x,y);
  const hov=Math.sin(frame*0.04)*4;
  // tractor beam always visible
  ctx.fillStyle="rgba(100,200,255,0.06)";
  ctx.beginPath();ctx.moveTo(-4,hov+8);ctx.lineTo(-20,60);ctx.lineTo(20,60);ctx.lineTo(4,hov+8);ctx.fill();
  // hit flash
  if(hitCount>0){
    const flashAlpha=Math.max(0,0.4-hitCount*0.01);
    ctx.fillStyle=`rgba(255,100,100,${flashAlpha})`;
    ctx.beginPath();ctx.ellipse(0,hov,30,12,0,0,Math.PI*2);ctx.fill();
  }
  // body
  ctx.fillStyle="#2a2a4a";ctx.beginPath();ctx.ellipse(0,hov,28,10,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#4a4a8a";ctx.beginPath();ctx.ellipse(0,hov,22,8,0,0,Math.PI*2);ctx.fill();
  // dome
  ctx.fillStyle="#1a1a3a";ctx.beginPath();ctx.ellipse(0,hov-8,14,10,0,Math.PI,Math.PI*2);ctx.fill();
  ctx.fillStyle="rgba(100,200,255,0.4)";ctx.beginPath();ctx.ellipse(0,hov-8,12,8,0,Math.PI,Math.PI*2);ctx.fill();
  // lights
  [-16,-8,0,8,16].forEach((lx,i)=>{
    const on=Math.sin(frame*0.1+i*1.2)>0;
    ctx.fillStyle=on?"#ffff44":"#333344";
    ctx.beginPath();ctx.arc(lx,hov+2,3,0,Math.PI*2);ctx.fill();
  });
  ctx.restore();
  // confession bubble
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
  const alpha=revealed?0.9:0.3+Math.sin(frame*0.02)*0.1;
  ctx.globalAlpha=alpha;
  ctx.fillStyle="#3a2a1a";ctx.beginPath();ctx.ellipse(0,0,22,12,0,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle="#6a4a2a";ctx.lineWidth=1;ctx.stroke();
  ctx.fillStyle="#d4c4a0";
  ctx.fillRect(-10,-3,20,6);
  ctx.beginPath();ctx.arc(-12,0,5,0,Math.PI*2);ctx.fill();
  ctx.beginPath();ctx.arc(12,0,5,0,Math.PI*2);ctx.fill();
  // dig progress bar
  if(!revealed&&sitTimer>0){
    const pct=Math.min(sitTimer/180,1);
    ctx.globalAlpha=0.8;
    ctx.fillStyle="rgba(0,0,0,0.5)";ctx.fillRect(-20,16,40,5);
    ctx.fillStyle="#f5c842";ctx.fillRect(-20,16,40*pct,5);
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
  // simpler wilder version
  ctx.save();ctx.translate(x,y);
  if(flip){ctx.translate(9*P,0);ctx.scale(-1,1);}
  const bob=Math.sin(frame*0.15)*1.5;
  ctx.fillStyle=pal.body;
  ctx.fillRect(2*P,(4+bob)*P,7*P,5*P);
  ctx.fillRect(1*P,(bob-1)*P,9*P,5*P);
  ctx.fillStyle=pal.eye;ctx.fillRect(2*P,(bob+1)*P,2*P,2*P);ctx.fillRect(6*P,(bob+1)*P,2*P,2*P);
  ctx.fillStyle="#ff4444";ctx.fillRect(3*P,(bob+3)*P,3*P,1*P);
  ctx.restore();
}

function drawMouse(ctx,x,y,frame,flip){
  ctx.save();ctx.translate(x,y);
  if(flip){ctx.translate(6*P,0);ctx.scale(-1,1);}
  const bob=Math.sin(frame*0.2)*1;
  ctx.fillStyle="#888888";
  ctx.fillRect(1*P,(2+bob)*P,4*P,3*P);
  ctx.beginPath();ctx.arc(4.5*P,(3+bob)*P,2*P,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#ffaaaa";
  ctx.beginPath();ctx.arc(5.5*P,(2+bob)*P,1*P,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#555555";
  ctx.fillRect(0,(2+bob)*P,2*P,1);// tail
  ctx.restore();
}

function drawHuman(ctx,x,y,frame){
  ctx.save();ctx.translate(x,y);
  const bob=Math.sin(frame*0.06)*1;
  ctx.fillStyle="#f5cba7";ctx.fillRect(3*P,(bob)*P,4*P,4*P);// head
  ctx.fillStyle="#3498db";ctx.fillRect(2*P,(4+bob)*P,6*P,5*P);// body
  ctx.fillStyle="#f5cba7";
  ctx.fillRect(1*P,(4+bob)*P,2*P,4*P);ctx.fillRect(7*P,(4+bob)*P,2*P,4*P);// arms
  ctx.fillStyle="#2c3e50";
  ctx.fillRect(2*P,(9+bob)*P,2*P,4*P);ctx.fillRect(6*P,(9+bob)*P,2*P,4*P);// legs
  ctx.fillStyle="#e67e22";ctx.fillRect(2*P,(bob-1)*P,6*P,2*P);// hair
  ctx.restore();
}

function drawDiablo(ctx,x,y,frame,hp=10){
  ctx.save();ctx.translate(x,y);
  const pulse=Math.sin(frame*0.08)*0.3;
  ctx.globalAlpha=0.85+pulse;
  // glow
  const g=ctx.createRadialGradient(0,0,0,0,0,40);
  g.addColorStop(0,"rgba(200,0,0,0.3)");g.addColorStop(1,"rgba(200,0,0,0)");
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(0,0,40,0,Math.PI*2);ctx.fill();
  // body
  ctx.fillStyle="#1a0000";ctx.fillRect(-10*P,-5*P,20*P,15*P);
  ctx.fillStyle="#330000";ctx.fillRect(-8*P,-8*P,16*P,8*P);// head
  // horns
  ctx.fillStyle="#660000";
  ctx.fillRect(-10*P,-14*P,3*P,8*P);ctx.fillRect(7*P,-14*P,3*P,8*P);
  // eyes
  ctx.fillStyle=`rgba(255,${Math.floor(50+pulse*100)},0,0.9)`;
  ctx.beginPath();ctx.arc(-4*P,-4*P,3*P,0,Math.PI*2);ctx.fill();
  ctx.beginPath();ctx.arc(4*P,-4*P,3*P,0,Math.PI*2);ctx.fill();
  // wings
  ctx.fillStyle="rgba(80,0,0,0.6)";
  ctx.beginPath();ctx.moveTo(-10*P,0);ctx.lineTo(-30*P,-20*P);ctx.lineTo(-10*P,8*P);ctx.fill();
  ctx.beginPath();ctx.moveTo(10*P,0);ctx.lineTo(30*P,-20*P);ctx.lineTo(10*P,8*P);ctx.fill();
  // HP bar
  ctx.globalAlpha=0.85;
  ctx.fillStyle="rgba(0,0,0,0.6)";ctx.fillRect(-20*P,18*P,40*P,5);
  ctx.fillStyle="#ff2222";ctx.fillRect(-20*P,18*P,40*P*(hp/10),5);
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
  ctx.save();ctx.globalAlpha=cat.revealAlpha*(cat.idle?0.35:1);
  ctx.font=`${Math.max(7,p*1.8)}px ${ff}`;
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
const SPAWN_INTERVALS = { ufo:30, fossil:45, wildcat:20, mouse:15, human:60, diablo:180 }; // seconds

function spawnObj(type, existingObjs){
  const margin=500;
  const rx=()=>margin+Math.random()*(WORLD_W-margin*2);
  const ry=()=>margin+Math.random()*(WORLD_H-margin*2);
  const count=existingObjs.filter(o=>o.type===type).length;
  if(count>=SPAWN_LIMITS[type]) return null;
  const id=`${type}_${Date.now()}_${Math.random().toString(36).slice(2,6)}`;
  if(type==="ufo") return{
    type:"ufo",id,x:rx(),y:ry(),
    confession:NPC_CONFESSIONS[Math.floor(Math.random()*NPC_CONFESSIONS.length)],
    vx:(Math.random()-0.5)*0.4,vy:(Math.random()-0.5)*0.15,
    frame:0,hitCount:0,active:true,
  };
  if(type==="fossil") return{
    type:"fossil",id,x:rx(),y:ry(),
    confession:NPC_CONFESSIONS[Math.floor(Math.random()*NPC_CONFESSIONS.length)],
    revealed:false,sitTimer:0,frame:0,
  };
  if(type==="wildcat"){
    const palId=Math.floor(Math.random()*PALETTES.length);
    return{
      type:"wildcat",id,x:rx(),y:ry(),
      pal:{...PALETTES[palId]},flip:Math.random()>0.5,
      vx:(Math.random()-0.5)*1.5,vy:(Math.random()-0.5)*1.5,
      frame:Math.floor(Math.random()*200),
      wanderAngle:Math.random()*Math.PI*2,
      wanderTimer:Math.floor(Math.random()*120),
    };
  }
  if(type==="mouse") return{
    type:"mouse",id,x:rx(),y:ry(),flip:Math.random()>0.5,
    vx:(Math.random()-0.5)*2,vy:(Math.random()-0.5)*2,
    frame:Math.floor(Math.random()*200),
    wanderAngle:Math.random()*Math.PI*2,
    wanderTimer:Math.floor(Math.random()*60),
    alive:true,
  };
  if(type==="human") return{
    type:"human",id,x:rx(),y:ry(),
    vx:(Math.random()-0.5)*0.5,vy:0,
    frame:Math.floor(Math.random()*200),
    wanderAngle:Math.random()*Math.PI*2,
    wanderTimer:200+Math.floor(Math.random()*300),
    dropTimer:600,// drop confession every 600 frames ~10s
    breadcrumbs:[],
  };
  if(type==="diablo") return{
    type:"diablo",id:"diablo_0",
    x:WORLD_W/2+Math.random()*2000-1000,
    y:WORLD_H/2+Math.random()*2000-1000,
    vx:0.2,vy:0.1,frame:0,
    wanderAngle:Math.random()*Math.PI*2,
    wanderTimer:300,
    hp:10,// needs 10 laser hits to defeat
    hitCooldown:0,
  };
  return null;
}

function generateWorldObjects(){
  const objs=[];
  // start with minimal set
  const obj=spawnObj("ufo",objs); if(obj)objs.push(obj);
  const obj2=spawnObj("fossil",objs); if(obj2)objs.push(obj2);
  const obj3=spawnObj("wildcat",objs); if(obj3)objs.push(obj3);
  const obj4=spawnObj("mouse",objs); if(obj4)objs.push(obj4);
  const obj5=spawnObj("human",objs); if(obj5)objs.push(obj5);
  const obj6=spawnObj("diablo",objs); if(obj6)objs.push(obj6);
  return objs;
}

// ─── Cat factory ──────────────────────────────────────────────────────────────
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
  const [panel,       setPanel]       = useState(null);
  const [resetIn,     setResetIn]     = useState(nextResetMs());
  const [onlineCount, setOnlineCount] = useState(0);
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
    return[pc,ac];
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
      s.stars=genStars();
      s.worldObjs=generateWorldObjects();
      if(pendingSpawn.current){
        const{name,palId,restored}=pendingSpawn.current;
        pendingSpawn.current=null;
        s.cats=buildSysCats();
        const ox=restored?.x??2000+Math.random()*6000;
        const oy=restored?.y??2000+Math.random()*6000;
        const myCat=makeCat(ox,oy,palId,name,true,false,null,clientId.current);
        if(restored?.confessions)myCat.confessions=[...restored.confessions];
        s.cats.push(myCat);
        s.myId=myCat.id;
        s.cam={x:ox-cv.width/2,y:oy-cv.height/2};
        s.ready=true;
        saveSession({name,palId,confessions:myCat.confessions,x:ox,y:oy});
        setOnlineCount(1);
        connectAbly(myCat);
      }
    });
    return()=>cancelAnimationFrame(raf);
  },[phase]);

  function connectAbly(myCat){
    if(ablyRef.current)ablyRef.current.close();
    const ably=new Ably.Realtime({key:ABLY_KEY,clientId:clientId.current});
    ablyRef.current=ably;
    const channel=ably.channels.get(CHANNEL);
    channelRef.current=channel;
    const myPresenceData=()=>({
      name:myCat.name,palId:myCat.palId,
      x:myCat.x,y:myCat.y,flip:myCat.flip,
      confessions:myCat.confessions,
    });
    const addRemoteCat=(d,cid)=>{
      const s=gs.current;
      if(cid===clientId.current)return;
      s.cats=s.cats.filter(c=>c.id!==cid);
      if(!d||!d.name)return;
      const cat=makeCat(d.x??WORLD_W/2,d.y??WORLD_H/2,d.palId??0,d.name,false,false,null,cid);
      cat.confessions=d.confessions??[];
      cat.flip=d.flip??false;
      s.cats.push(cat);
      setOnlineCount(s.cats.filter(c=>!c.isSys).length);
    };
    channel.presence.subscribe("enter",(m)=>addRemoteCat(m.data,m.clientId));
    channel.presence.subscribe("present",(m)=>addRemoteCat(m.data,m.clientId));
    channel.presence.subscribe("leave",(m)=>{
      const s=gs.current;
      s.cats=s.cats.filter(c=>c.id!==m.clientId);
      setOnlineCount(s.cats.filter(c=>!c.isSys).length);
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
      cat.x=d.x;cat.y=d.y;cat.vx=d.vx;cat.vy=d.vy;cat.flip=d.flip;cat.state=d.state;
    });
    channel.subscribe("reset",()=>{
      localStorage.removeItem("fikfuk_s");
      const s=gs.current;
      s.cats=[];s.myId=null;s.ready=false;
      s.laserOn=false;s.laser={sx:-999,sy:-999,active:false};s.trail=[];
      s.worldObjs=[];
      setLaserOn(false);phaseRef.current="onboard";setPhase("onboard");
    });
    channel.presence.enter(myPresenceData());
    myCat._updatePresence=()=>channel.presence.update(myPresenceData());
    window.addEventListener("beforeunload",()=>channel.presence.leave());
  }

  useEffect(()=>{
    const sess=loadSession();
    if(sess)requestSpawn(sess.name,sess.palId,{confessions:sess.confessions,x:sess.x,y:sess.y});
    else{setPhase("onboard");phaseRef.current="onboard";}
  },[requestSpawn]);

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
      s.frame++;
      const W=cv.width,H=cv.height;
      const{laser,cam}=s;
      const myCat=s.cats.find(c=>c.id===s.myId);
      const laserWorld=laser.active?s2w(laser.sx,laser.sy):{wx:-9999,wy:-9999};
      s.cats.forEach(cat=>{
        if(cat.grabbed){cat.frame++;cat.state="sit";return;}
        cat.frame++;
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
        if(spd2>3.5){cat.vx=cat.vx/spd2*3.5;cat.vy=cat.vy/spd2*3.5;}
        if(!cat.isSys){cat.x+=cat.vx;cat.y+=cat.vy;}
        cat.x=Math.max(10,Math.min(WORLD_W-12*P,cat.x));
        cat.y=Math.max(10,Math.min(WORLD_H-14*P,cat.y));
        if(cat.revealTimer>0)cat.revealTimer--;
        else cat.revealAlpha=Math.max(0,cat.revealAlpha-0.025);
      });
      // ── spawn new objects over time ──
      if(s.frame%60===0){
        const types=["ufo","fossil","wildcat","mouse","human","diablo"];
        types.forEach(type=>{
          const interval=SPAWN_INTERVALS[type]*60;
          if(s.frame%(interval)===0){
            const newObj=spawnObj(type,s.worldObjs);
            if(newObj)s.worldObjs.push(newObj);
          }
        });
      }

      // ── laser hit detection on UFO ──
      const laserWx=laser.active?laserWorld.wx:-9999;
      const laserWy=laser.active?laserWorld.wy:-9999;

      const toRemove=new Set();
      const toAdd=[];

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
                myCat._boostTimer=300;
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
          obj.vx+=Math.cos(obj.wanderAngle)*0.015;
          obj.vy+=Math.sin(obj.wanderAngle)*0.015;
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
      });

      // apply removals and additions
      if(toRemove.size>0) s.worldObjs=s.worldObjs.filter(o=>!toRemove.has(o.id));
      if(toAdd.length>0) s.worldObjs.push(...toAdd);

      // apply cat speed boost
      if(myCat&&myCat._boostTimer>0){
        myCat._boostTimer--;
        myCat.vx*=1.02;myCat.vy*=1.02;
      }
      if(myCat&&channelRef.current){
        const now=Date.now();
        if(now-moveThrottle.current>100){
          moveThrottle.current=now;
          channelRef.current.publish("move",{x:myCat.x,y:myCat.y,vx:myCat.vx,vy:myCat.vy,flip:myCat.flip,state:myCat.state});
        }
      }
      if(s.frame%300===0&&myCat){
        const sess=loadSession();
        if(sess)saveSession({...sess,x:myCat.x,y:myCat.y,confessions:myCat.confessions});
      }
      ctx.fillStyle="#080810";ctx.fillRect(0,0,W,H);
      ctx.save();
      const bx=-cam.x,by=-cam.y;
      ctx.strokeStyle="rgba(255,50,50,0.15)";ctx.lineWidth=3;
      ctx.strokeRect(bx,by,WORLD_W,WORLD_H);
      ctx.restore();
      s.stars.forEach(st=>{
        const sx=(st.x-cam.x*0.3+W*10)%W;
        const sy=(st.y-cam.y*0.3+H*10)%H;
        ctx.beginPath();ctx.arc(sx,sy,st.r,0,Math.PI*2);
        ctx.fillStyle=`rgba(200,200,255,${st.a+Math.sin(s.frame*st.speed)*0.12})`;ctx.fill();
      });
      for(let gy=0;gy<H;gy+=4){ctx.fillStyle="rgba(0,0,0,0.06)";ctx.fillRect(0,gy,W,2);}
      s.worldObjs.forEach(obj=>{
        const{sx,sy}=w2s(obj.x,obj.y);
        if(sx<-100||sx>W+100||sy<-100||sy>H+200)return;
        if(obj.type==="ufo")drawUFO(ctx,sx,sy,obj.frame,null);
        if(obj.type==="fossil")drawFossil(ctx,sx,sy,obj.frame,obj.revealed,obj.sitTimer,obj.confession);
        if(obj.type==="wildcat")drawWildCat(ctx,sx,sy,obj.frame,obj.pal,obj.flip);
        if(obj.type==="mouse")drawMouse(ctx,sx,sy,obj.frame,obj.flip);
        if(obj.type==="human")drawHuman(ctx,sx,sy,obj.frame);
        if(obj.type==="diablo")drawDiablo(ctx,sx,sy,obj.frame,obj.hp);
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
      });
      s.cats.forEach(c=>{
        const{sx,sy}=w2s(c.x,c.y);
        if(sx<-60||sx>W+60||sy<-60||sy>H+60)return;
        if(!c.grabbed&&!c.isSys){
          ctx.save();ctx.globalAlpha=c.idle?0.08:0.15;ctx.fillStyle="#000";
          ctx.beginPath();ctx.ellipse(sx+5.5*P,sy+13*P,14,4,0,0,Math.PI*2);ctx.fill();ctx.restore();
        }
        drawCat(ctx,sx,sy,P,c.frame,c.pal,c.flip,c.state,c.grabbed,c.isOwn,c.isSys,c.idle);
        drawBubble(ctx,{...c,x:sx,y:sy},P);
      });
      if(laser.active&&!s.camDrag)drawLaser(ctx,laser.sx,laser.sy,s.trail,s.frame);
      const MM_W=130,MM_H=90,MM_X=W-MM_W-12,MM_Y=H-MM_H-70;
      ctx.save();
      // background
      ctx.fillStyle="rgba(0,0,0,0.7)";ctx.strokeStyle="rgba(255,50,50,0.3)";ctx.lineWidth=1;
      ctx.fillRect(MM_X,MM_Y,MM_W,MM_H);ctx.strokeRect(MM_X,MM_Y,MM_W,MM_H);
      // viewport box
      const vpx=MM_X+(cam.x/WORLD_W)*MM_W;
      const vpy=MM_Y+(cam.y/WORLD_H)*MM_H;
      const vpw=(W/WORLD_W)*MM_W;
      const vph=(H/WORLD_H)*MM_H;
      ctx.strokeStyle="rgba(255,255,255,0.2)";ctx.strokeRect(vpx,vpy,vpw,vph);
      // sys cats (policy=purple, about=green)
      s.cats.filter(c=>c.isSys).forEach(c=>{
        const mx=MM_X+(c.x/WORLD_W)*MM_W;
        const my=MM_Y+(c.y/WORLD_H)*MM_H;
        const col=c.sysType==="privacy"?"#7777ff":"#44cc44";
        ctx.fillStyle=col;
        ctx.fillRect(mx-2,my-2,4,4);
        ctx.font="5px monospace";
        ctx.fillStyle=col;
        ctx.fillText(c.sysType==="privacy"?"P":"A",mx+3,my+2);
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
      legend.forEach((l,i)=>{
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
  const onPointerDown=useCallback((e)=>{
    if(phaseRef.current!=="play")return;
    const{sx,sy}=getPos(e);
    const s=gs.current;
    const cat=catAtScreen(sx,sy);
    const now=Date.now();
    if(cat){
      if(lastTap.current.id===cat.id&&now-lastTap.current.time<400){
        setPanel({catId:cat.id,name:cat.name,confessions:[...cat.confessions],isOwn:cat.isOwn,isSys:cat.isSys,sysType:cat.sysType,eye:cat.pal.eye});
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
    const{sx,sy}=getPos(e);
    const s=gs.current;
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
    setInputVal("");setShowInput(false);
    startCooldown();
  };
  const panelAccent=panel?.isSys?(panel.sysType==="privacy"?"#7777ff":"#44cc44"):(panel?.isOwn?"#ff3232":"rgba(120,120,255,0.7)");
  return(
    <div style={{position:"fixed",inset:0,background:"#080810",fontFamily:ff,overflow:"hidden"}}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
        html,body,#root{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#080810;}
        *{box-sizing:border-box;}
        .pal-swatch{cursor:pointer;transition:transform .12s,box-shadow .15s;}
        .pal-swatch:hover{transform:scale(1.12);}
        .hbtn{transition:background .15s,box-shadow .15s;cursor:pointer;font-family:'Press Start 2P',monospace;}
        .hbtn:hover{background:rgba(255,50,50,0.2)!important;box-shadow:0 0 20px rgba(255,50,50,0.55)!important;}
      `}</style>
      <canvas ref={canvasRef}
        style={{position:"absolute",inset:0,width:"100%",height:"100%",display:"block",touchAction:"none",
          cursor:phase==="play"?(laserOn?"none":"grab"):"default",
          opacity:phase==="play"?1:0,pointerEvents:phase==="play"?"auto":"none"}}
        onMouseDown={onPointerDown} onMouseMove={onPointerMove}
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
        <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",background:"#080810",zIndex:100,padding:20}}>
          <div style={{background:"#0d0d1a",border:"2px solid #ff3232",boxShadow:"0 0 40px rgba(255,50,50,0.2)",padding:28,maxWidth:360,width:"100%",display:"flex",flexDirection:"column",gap:22}}>
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
      {phase==="play"&&(<>
        <div style={{position:"fixed",top:0,left:0,right:0,zIndex:10,pointerEvents:"none",display:"flex",justifyContent:"space-between",alignItems:"center",padding:"12px 16px",background:"linear-gradient(to bottom,rgba(8,8,16,0.85),transparent)"}}>
          <span style={{fontSize:9,color:"#ff4444",textShadow:"0 0 12px rgba(255,50,50,0.55)",letterSpacing:1}}>fikfuk.wtf</span>
          <div style={{display:"flex",gap:12,alignItems:"center"}}>
            <span style={{fontSize:7,color:"rgba(255,255,255,0.3)"}}>🐾 {onlineCount} online</span>
            <span style={{fontSize:7,color:"rgba(255,255,255,0.22)"}}>resets {fmtCountdown(resetIn)}</span>
          </div>
        </div>
        <button className="hbtn" onClick={centerOnCat}
          style={{position:"fixed",top:50,right:16,zIndex:10,fontSize:7,padding:"6px 10px",background:"rgba(8,8,16,0.7)",border:"1px solid rgba(255,50,50,0.3)",color:"rgba(255,100,100,0.6)"}}>
          find me
        </button>
        <div style={{position:"fixed",bottom:0,left:0,right:0,zIndex:20,display:"flex",gap:10,alignItems:"center",justifyContent:"center",padding:"12px 16px 20px",background:"linear-gradient(to top,rgba(8,8,16,0.92),transparent)"}}>
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
            <div style={{fontSize:7,color:"rgba(255,255,255,0.22)"}}>only your cat carries this · 30s cooldown</div>
            <div style={{display:"flex",gap:8,justifyContent:"flex-end"}}>
              <button onClick={()=>setShowInput(false)} style={{background:"transparent",border:"1px solid rgba(255,255,255,0.15)",color:"rgba(255,255,255,0.35)",fontFamily:ff,fontSize:7,padding:"6px 10px",cursor:"pointer"}}>cancel</button>
              <button onClick={submitConfession} style={{background:"rgba(255,50,50,0.15)",border:"1px solid #ff3232",color:"#ff7777",fontFamily:ff,fontSize:7,padding:"6px 12px",cursor:"pointer",boxShadow:"0 0 8px rgba(255,50,50,0.3)"}}>send</button>
            </div>
          </div>
        )}
      </>)}
      {panel&&(
        <div style={{position:"fixed",inset:0,zIndex:200,display:"flex",alignItems:"center",justifyContent:"center",background:"rgba(0,0,0,0.65)"}} onClick={()=>setPanel(null)}>
          <div onClick={e=>e.stopPropagation()} style={{background:"#0d0d1a",border:`2px solid ${panelAccent}`,boxShadow:`0 0 40px ${panelAccent}55`,padding:"20px",minWidth:280,maxWidth:"90vw",display:"flex",flexDirection:"column",gap:12}}>
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
            <div style={{fontSize:7,color:"rgba(255,255,255,0.18)",textAlign:"right"}}>tap outside to close</div>
          </div>
        </div>
      )}
      <SpeedInsights/>
    </div>
  );
}
