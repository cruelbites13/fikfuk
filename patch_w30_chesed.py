# patch_w30_chesed.py - a seventh world: the Open Hand (Chesed), the world of kindness.
# A calm blue-white world with its own portal look, drifting lights, rain and aurora, and a soft river-and-chimes
# soundscape. Every other world gets a portal to it and it has portals to all six.
# Its mechanic is warmth. When anybody chirps, every other cat within reach is warmed: it glows gold for 25 seconds
# (everybody sees it, no extra messages needed) and the cat that was warmed gets a short speed boost. There are nine
# glowing Still Pools scattered around (new spots every cycle, shown as blue dots on the minimap). Chirp from inside a
# pool and your warmth reaches almost twice as far. Recap card: "cats warmed" (by you) and "warmth received" (from others).
# Needs patch_w29_audio_engine.py first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_chesed*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_eng*/" not in src or "/*_vent*/" not in src:
    print("ABORT: apply patch_w28_iron_hall.py and patch_w29_audio_engine.py first. Nothing written."); sys.exit(1)

MOD = r'''/*_chesed*/
let _plE=-1,_plL=[];
function poolsList(){
  if(WORLD_ID!=="chesed")return[];
  const e=getEpoch();
  if(_plE!==e){_plE=e;_plL=[];const r=mulberry32(hashStr(e+"|pools")),pt=PORTALS.chesed||{};
    for(let i=0;i<600&&_plL.length<9;i++){const x=1200+r()*7600,y=1200+r()*7600;let ok=Math.hypot(x-5000,y-5000)>250;
      for(const k in pt)if(Math.hypot(x-pt[k][0],y-pt[k][1])<450)ok=false;
      _plL.forEach(o=>{if(Math.hypot(x-o.x,y-o.y)<700)ok=false;});
      if(ok)_plL.push({x,y,r:150+Math.floor(r()*40)});}}
  return _plL;
}
function poolAt(x,y){const L=poolsList();for(let i=0;i<L.length;i++){if(Math.hypot(x-L[i].x,(y-L[i].y)*2)<L[i].r)return L[i];}return null;}
function drawPools(ctx,cam,W,H,f){
  const L=poolsList();if(!L.length)return;
  ctx.save();
  L.forEach((p,i)=>{const sx=Math.round(p.x-cam.x),sy=Math.round(p.y-cam.y);if(sx<-p.r-40||sx>W+p.r+40||sy<-p.r||sy>H+p.r)return;
    const ry=p.r/2,pu=0.5+0.5*Math.sin(f*0.03+i);
    ctx.globalCompositeOperation="source-over";ctx.fillStyle="rgba(10,30,60,0.55)";ctx.beginPath();ctx.ellipse(sx,sy,p.r+6,ry+3,0,0,6.2832);ctx.fill();
    ctx.fillStyle="rgba(40,100,170,0.55)";ctx.beginPath();ctx.ellipse(sx,sy,p.r-4,ry-2,0,0,6.2832);ctx.fill();
    ctx.globalCompositeOperation="lighter";
    for(let k=0;k<4;k++){ctx.fillStyle="rgba(120,190,255,"+(0.05+0.025*pu)*(4-k)/4+")";ctx.beginPath();ctx.ellipse(sx,sy,p.r-10-k*22,ry-5-k*10,0,0,6.2832);ctx.fill();}
    for(let k=0;k<2;k++){const q=((f*0.012+k*0.5+i*0.17)%1);ctx.strokeStyle="rgba(210,235,255,"+(0.5*(1-q)).toFixed(3)+")";ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(sx,sy,6+(p.r-14)*q,3+(ry-7)*q,0,0,6.2832);ctx.stroke();}
    for(let k=0;k<5;k++){const a=f*0.02+k*1.26+i,tw=0.5+0.5*Math.sin(f*0.07+k*2+i);ctx.fillStyle="rgba(235,248,255,"+(0.25+0.6*tw).toFixed(3)+")";
      ctx.fillRect(Math.round((sx+Math.cos(a)*(p.r-26)*0.8)/3)*3,Math.round((sy+Math.sin(a)*(ry-12)*0.8-((f*0.4+k*17)%24))/3)*3,3,3);}
  });
  ctx.restore();
}
function kindChirp(x,y,fromId,s){
  if(!s)return;const pool=poolAt(x,y),R=250*(pool?1.8:1),now=Date.now();let n=0;
  s.cats.forEach(c=>{if(c.id===fromId||c.isGhost||c.idle)return;
    if(Math.hypot(c.x-x,c.y-y)<R){n++;c._glowUntil=now+25000;
      for(let i=0;i<3;i++)s.particles.push({text:"<3",x:c.x+4+i*7,y:c.y-6,vx:(Math.random()-0.5)*0.5,vy:-0.45-Math.random()*0.4,alpha:1,life:120+i*10,delay:i*8});
      if(c.id===s.myId){c._boostTimer=Math.max(c._boostTimer||0,240);RECAP.felt=(RECAP.felt||0)+1;try{FKAudio.feed(true);}catch(e){}}}});
  if(fromId===s.myId&&n)RECAP.warmed=(RECAP.warmed||0)+n;
}
let uid=100;'''

PORT_OLD = ('const PORTALS={malkuth:{yesod:[5750,4250],netzach:[4250,4250],hod:[5000,3000],tiferet:[6500,3300],gevurah:[3500,3300]},yesod:{malkuth:[5000,5700],netzach:[5750,4250],hod:[4250,4250],tiferet:[5000,3000],gevurah:[6500,3500]},'
            'netzach:{malkuth:[5000,5700],yesod:[4250,4250],hod:[5750,4250],tiferet:[5000,3000],gevurah:[3500,3500]},hod:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],tiferet:[5000,3000],gevurah:[6500,3500]},'
            'tiferet:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[3500,3500],gevurah:[6500,3500]},'
            'gevurah:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[3500,3500],tiferet:[6500,3500]}};')
PORT_NEW = ('const PORTALS={malkuth:{yesod:[5750,4250],netzach:[4250,4250],hod:[5000,3000],tiferet:[6500,3300],gevurah:[3500,3300],chesed:[3500,5200]},yesod:{malkuth:[5000,5700],netzach:[5750,4250],hod:[4250,4250],tiferet:[5000,3000],gevurah:[6500,3500],chesed:[3500,5200]},'
            'netzach:{malkuth:[5000,5700],yesod:[4250,4250],hod:[5750,4250],tiferet:[5000,3000],gevurah:[3500,3500],chesed:[3500,5200]},hod:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],tiferet:[5000,3000],gevurah:[6500,3500],chesed:[3500,5200]},'
            'tiferet:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[3500,3500],gevurah:[6500,3500],chesed:[3500,5200]},'
            'gevurah:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[3500,3500],tiferet:[6500,3500],chesed:[3500,5200]},'
            'chesed:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[5000,3000],tiferet:[6500,3300],gevurah:[3500,3300]}};')

CRLF = "\r\n" in src
if CRLF:
    src = src.replace("\r\n", "\n")
n = 0
def S(old, new, label):
    global src, n
    src = swap(src, old, new, label); n += 1

S("let uid=100;", MOD, "pool module")
S('gevurah:{name:"Iron Hall",sky:["#1A0608","#4A0F18"]}};', 'gevurah:{name:"Iron Hall",sky:["#1A0608","#4A0F18"]},chesed:{name:"Open Hand",sky:["#0A1830","#2C5C9A"]}};', "world table")
S(PORT_OLD, PORT_NEW, "portals")
S('gevurah:{root:73.42,scale:[0,1,3,6,7],wave:"triangle",cut:520,gap:[3,6],vol:0.07}',
  'gevurah:{root:73.42,scale:[0,1,3,6,7],wave:"triangle",cut:520,gap:[3,6],vol:0.07},\n    chesed:{root:98,scale:[0,2,4,7,9],wave:"sine",cut:1300,gap:[3,6],vol:0.07}', "music table")
S('beds:{forge:0.9,wind:0.3},ev:{clink:[0.3,0],crackle:[0.5,0]}}',
  'beds:{forge:0.9,wind:0.3},ev:{clink:[0.3,0],crackle:[0.5,0]}},\n    chesed:{root:196,sc:[0,2,4,7,9,12,14,16,19],gap:[5,9],sp:0.85,cut:3000,padCut:1100,\n      pad:[[0,4,7,14],[-3,4,7,12],[5,9,12,16],[-5,2,7,11]],beds:{river:0.3,wind:0.1},ev:{tinkle:[0.12,0],bird:[0.15,"d"],cricket:[0.25,"n"],drip:[0.08,0]}}', "engine config")
S('gevurah:{hor:[140,30,40],neb:[[220,40,60],[90,90,120]],star:[255,210,215],moon:["#2a0a10","#7a1a2a","#d04050","#ffd0d8"],ring:true,glow:[255,70,90]}',
  'gevurah:{hor:[140,30,40],neb:[[220,40,60],[90,90,120]],star:[255,210,215],moon:["#2a0a10","#7a1a2a","#d04050","#ffd0d8"],ring:true,glow:[255,70,90]},\n    chesed:{hor:[60,120,200],neb:[[120,190,255],[200,230,255]],star:[225,240,255],moon:["#12284a","#3a6aa8","#8cc0f0","#eaf6ff"],ring:false,glow:[150,200,255]}', "sky theme")
S('ctx.fillStyle=rg(world==="gevurah"?[255,110,100]:', 'ctx.fillStyle=rg(world==="chesed"?[200,230,255]:world==="gevurah"?[255,110,100]:', "motes")
S('gevurah: { ring: ["#1a0608", "#5a1420", "#d03a4c", "#ffc8d0"], glow: [255, 70, 90], core: [255, 225, 230], spark: "#ffb0b8" }',
  'gevurah: { ring: ["#1a0608", "#5a1420", "#d03a4c", "#ffc8d0"], glow: [255, 70, 90], core: [255, 225, 230], spark: "#ffb0b8" },\n    chesed: { ring: ["#0d2038", "#2a5a94", "#7ab8f0", "#eaf8ff"], glow: [140, 200, 255], core: [240, 250, 255], spark: "#ffffff" }', "portal palette")
S('} else if (dest === "gevurah") {',
  '} else if (dest === "chesed") {\n      for (i = 0; i < 5; i++) { var cl = ((t * 0.35 + i * 17) % 45), ca = i * 1.27 + 0.4, cx2 = x + Math.cos(ca) * (RX - 4), cy2 = y + Math.sin(ca) * (RY - 2) - cl;\n        ctx.fillStyle = rgba([225, 242, 255], 0.9 - cl / 50); ctx.fillRect(g3(cx2) - 1, g3(cy2) - 1, 3, 3); ctx.fillRect(g3(cx2) - 1, g3(cy2) - 4, 3, 3); }\n    } else if (dest === "gevurah") {', "portal decor")
S('"Iron Hall":"#ff7a88"})[worldName]', '"Iron Hall":"#ff7a88","Open Hand":"#9fd0ff"})[worldName]', "name colour")
S('gevurah:"255,90,110"})[WORLD_ID]', 'gevurah:"255,90,110",chesed:"140,200,255"})[WORLD_ID]', "minimap colour")
S('gevurah:["meteors","rain","drift"]};', 'gevurah:["meteors","rain","drift"],chesed:["aurora","drift","rain"]};', "weather list")
S('gevurah:"255,150,160"};', 'gevurah:"255,150,160",chesed:"170,215,255"};', "rain colour")
S('gevurah:["255,70,90","255,150,90"]};', 'gevurah:["255,70,90","255,150,90"],chesed:["90,200,255","200,230,255"]};', "aurora colour")
S('gevurah:"255,110,100"};', 'gevurah:"255,110,100",chesed:"200,230,255"};', "drift colour")
S('gevurah:"red sparks"}', 'gevurah:"red sparks",chesed:"drifting lights"}', "weather name")
S("drawVents(ctx,cam,W,H,s.frame);drawSun(ctx,cam,W,H,s.frame,s);", "drawPools(ctx,cam,W,H,s.frame);drawVents(ctx,cam,W,H,s.frame);drawSun(ctx,cam,W,H,s.frame,s);", "draw")
S("{const _g=sunGet();if(_g)_g.forEach(",
  '{ctx.fillStyle="rgba(140,205,255,0.9)";poolsList().forEach(v=>ctx.fillRect(MM_X+(v.x/WORLD_W)*MM_W-1.5,MM_Y+(v.y/WORLD_H)*MM_H-1.5,3,3));}'
  "{const _g=sunGet();if(_g)_g.forEach(", "minimap pools")
S('function applyChirp(x,y,fromId,_r){if(!_r&&WORLD_ID==="yesod")shardRelay(x,y,fromId,applyChirp);',
  'function applyChirp(x,y,fromId,_r){if(!_r&&WORLD_ID==="yesod")shardRelay(x,y,fromId,applyChirp);if(!_r&&WORLD_ID==="chesed")kindChirp(x,y,fromId,gs.current);', "chirp hook")
S("Object.assign(RECAP,{e:ep,t0:Date.now(),rides:0,singed:0,", "Object.assign(RECAP,{e:ep,t0:Date.now(),warmed:0,felt:0,rides:0,singed:0,", "recap reset")
S("rides:RECAP.rides||0,singed:RECAP.singed||0}", "rides:RECAP.rides||0,singed:RECAP.singed||0,warmed:RECAP.warmed||0,felt:RECAP.felt||0}", "recap stat")
S("if(d.stats.rides)rows.push(", 'if(d.stats.warmed)rows.push(["cats warmed",String(d.stats.warmed)]);if(d.stats.felt>=2)rows.push(["warmth received",String(d.stats.felt)]);if(d.stats.rides)rows.push(', "recap rows")
if CRLF:
    src = src.replace("\n", "\r\n")
open(P, "w", encoding="utf-8", newline="").write(src)
print(f"OK: {n} edits applied.")
