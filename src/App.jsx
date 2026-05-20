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
function drawUFO(ctx,x,y,frame,confession){
  ctx.save();ctx.translate(x,y);
  const hov=Math.sin(frame*0.04)*4;
  // beam
  if(confession){
    ctx.fillStyle="rgba(150,255,150,0.08)";
    ctx.beginPath();ctx.moveTo(-4,hov+8);ctx.lineTo(-20,60);ctx.lineTo(20,60);ctx.lineTo(4,hov+8);ctx.fill();
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
    ctx.beginPath();ctx.roundRect(bx,by,bw,bh,3);ctx.fill();ctx.stroke();
    ctx.fillStyle="#88ff88";ctx.fillText(confession,bx+8,by+15);
    ctx.restore();
  }
}

function drawFossil(ctx,x,y,frame,revealed){
  ctx.save();ctx.translate(x,y);
  const alpha=revealed?0.9:0.3+Math.sin(frame*0.02)*0.1;
  ctx.globalAlpha=alpha;
  // ground mark
  ctx.fillStyle="#3a2a1a";ctx.beginPath();ctx.ellipse(0,0,22,12,0,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle="#6a4a2a";ctx.lineWidth=1;ctx.stroke();
  // bone pattern
  ctx.fillStyle="#d4c4a0";
  ctx.fillRect(-10,-3,20,6);
  ctx.beginPath();ctx.arc(-12,0,5,0,Math.PI*2);ctx.fill();
  ctx.beginPath();ctx.arc(12,0,5,0,Math.PI*2);ctx.fill();
  if(revealed){
    ctx.font=`6px ${ff}`;ctx.fillStyle="#ffddaa";
    ctx.globalAlpha=0.8;ctx.fillText("fossil",- 10,18);
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

function drawDiablo(ctx,x,y,frame){
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

function generateWorldObjects(){
  const objs=[];
  const margin=500;
  // UFOs - 15 scattered
  for(let i=0;i<15;i++){
    objs.push({
      type:"ufo", id:`ufo_${i}`,
      x:margin+Math.random()*(WORLD_W-margin*2),
      y:margin+Math.random()*(WORLD_H-margin*2),
      confession:NPC_CONFESSIONS[Math.floor(Math.random()*NPC_CONFESSIONS.length)],
      vx:(Math.random()-0.5)*0.3, vy:(Math.random()-0.5)*0.1,
      frame:Math.floor(Math.random()*200),
    });
  }
  // Fossils - 25 buried
  for(let i=0;i<25;i++){
    objs.push({
      type:"fossil", id:`fossil_${i}`,
      x:margin+Math.random()*(WORLD_W-margin*2),
      y:margin+Math.random()*(WORLD_H-margin*2),
      confession:NPC_CONFESSIONS[Math.floor(Math.random()*NPC_CONFESSIONS.length)],
      revealed:false, frame:0,
    });
  }
  // Wild cats - 20
  for(let i=0;i<20;i++){
    const palId=Math.floor(Math.random()*PALETTES.length);
    objs.push({
      type:"wildcat", id:`wc_${i}`,
      x:margin+Math.random()*(WORLD_W-margin*2),
      y:margin+Math.random()*(WORLD_H-margin*2),
      pal:{...PALETTES[palId]},
      flip:Math.random()>0.5,
      vx:(Math.random()-0.5)*1.5, vy:(Math.random()-0.5)*1.5,
      frame:Math.floor(Math.random()*200),
      wanderAngle:Math.random()*Math.PI*2,
      wanderTimer:Math.floor(Math.random()*120),
    });
  }
  // Mice - 30
  for(let i=0;i<30;i++){
    objs.push({
      type:"mouse", id:`mouse_${i}`,
      x:margin+Math.random()*(WORLD_W-margin*2),
      y:margin+Math.random()*(WORLD_H-margin*2),
      flip:Math.random()>0.5,
      vx:(Math.random()-0.5)*2, vy:(Math.random()-0.5)*2,
      frame:Math.floor(Math.random()*200),
      wanderAngle:Math.random()*Math.PI*2,
      wanderTimer:Math.floor(Math.random()*60),
    });
  }
  // Human NPC - 3
  for(let i=0;i<3;i++){
    objs.push({
      type:"human", id:`human_${i}`,
      x:margin+Math.random()*(WORLD_W-margin*2),
      y:margin+Math.random()*(WORLD_H-margin*2),
      vx:(Math.random()-0.5)*0.5, vy:0,
      frame:Math.floor(Math.random()*200),
      wanderAngle:Math.random()*Math.PI*2,
      wanderTimer:200+Math.floor(Math.random()*300),
      dropTimer:0,
    });
  }
  // Diablo - 1 boss
  objs.push({
    type:"diablo", id:"diablo_0",
    x:WORLD_W/2+Math.random()*500-250,
    y:WORLD_H/2+Math.random()*500-250,
    vx:0.2, vy:0.1, frame:0,
    wanderAngle:Math.random()*Math.PI*2,
    wanderTimer:300,
  });
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
  function buildSysCats(){
    const pc=makeCat(100
