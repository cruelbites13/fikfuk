# patch_w28_iron_hall.py - a sixth world: the Iron Hall (Gevurah).
# A dark crimson world of steel and fire: its own portal look (spikes), a low, tense ambient tune, falling red sparks,
# meteors and rain. Every other world gets a portal to it and it has portals to all five.
# Its mechanic is a rhythm hazard: 12 flame vents in the floor (new spots every cycle). Each erupts every 9 seconds on a
# fixed beat that is the same for everybody (from the shared clock, no messages). About a second before, its ring pulses
# red as a warning. If you are standing on a vent when it erupts, the flames throw you away from it. But if you DASH
# through during the eruption, you ride the flame instead: no knockback and a speed boost. Vents show as dots on the minimap.
# Recap card: "flames ridden" and "times singed". Needs patch_w27_sun_court.py first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_vent*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_sun*/" not in src:
    print("ABORT: apply patch_w27_sun_court.py first. Nothing written."); sys.exit(1)

MOD = r'''/*_vent*/
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
let uid=100;'''

PORT_OLD = ('const PORTALS={malkuth:{yesod:[5750,4250],netzach:[4250,4250],hod:[5000,3000],tiferet:[6500,3300]},yesod:{malkuth:[5000,5700],netzach:[5750,4250],hod:[4250,4250],tiferet:[5000,3000]},'
            'netzach:{malkuth:[5000,5700],yesod:[4250,4250],hod:[5750,4250],tiferet:[5000,3000]},hod:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],tiferet:[5000,3000]},'
            'tiferet:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[3500,3500]}};')
PORT_NEW = ('const PORTALS={malkuth:{yesod:[5750,4250],netzach:[4250,4250],hod:[5000,3000],tiferet:[6500,3300],gevurah:[3500,3300]},yesod:{malkuth:[5000,5700],netzach:[5750,4250],hod:[4250,4250],tiferet:[5000,3000],gevurah:[6500,3500]},'
            'netzach:{malkuth:[5000,5700],yesod:[4250,4250],hod:[5750,4250],tiferet:[5000,3000],gevurah:[3500,3500]},hod:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],tiferet:[5000,3000],gevurah:[6500,3500]},'
            'tiferet:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[3500,3500],gevurah:[6500,3500]},'
            'gevurah:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[3500,3500],tiferet:[6500,3500]}};')

src = swap(src, "let uid=100;", MOD, "vent module")
src = swap(src, 'tiferet:{name:"Sun Court",sky:["#2B1F08","#8A6A1C"]}};', 'tiferet:{name:"Sun Court",sky:["#2B1F08","#8A6A1C"]},gevurah:{name:"Iron Hall",sky:["#1A0608","#4A0F18"]}};', "world table")
src = swap(src, PORT_OLD, PORT_NEW, "portals")
src = swap(src, 'tiferet:{root:130.81,scale:[0,4,7,11,14],wave:"sine",cut:1100,gap:[3,6],vol:0.075}',
    'tiferet:{root:130.81,scale:[0,4,7,11,14],wave:"sine",cut:1100,gap:[3,6],vol:0.075},\n    gevurah:{root:73.42,scale:[0,1,3,6,7],wave:"triangle",cut:520,gap:[3,6],vol:0.07}', "music")
src = swap(src, 'tiferet:{hor:[190,140,40],neb:[[255,210,90],[255,150,60]],star:[255,245,210],moon:["#4a3410","#a8782a","#f0c050","#fff4c0"],ring:true,glow:[255,215,110]}',
    'tiferet:{hor:[190,140,40],neb:[[255,210,90],[255,150,60]],star:[255,245,210],moon:["#4a3410","#a8782a","#f0c050","#fff4c0"],ring:true,glow:[255,215,110]},\n    gevurah:{hor:[140,30,40],neb:[[220,40,60],[90,90,120]],star:[255,210,215],moon:["#2a0a10","#7a1a2a","#d04050","#ffd0d8"],ring:true,glow:[255,70,90]}', "sky theme")
src = swap(src, 'ctx.fillStyle=rg(world==="tiferet"?[255,225,140]:', 'ctx.fillStyle=rg(world==="gevurah"?[255,110,100]:world==="tiferet"?[255,225,140]:', "motes")
src = swap(src, 'tiferet: { ring: ["#3a2808", "#8a6a1c", "#f0c050", "#fff4c0"], glow: [255, 215, 100], core: [255, 250, 220], spark: "#fff2b0" }',
    'tiferet: { ring: ["#3a2808", "#8a6a1c", "#f0c050", "#fff4c0"], glow: [255, 215, 100], core: [255, 250, 220], spark: "#fff2b0" },\n    gevurah: { ring: ["#1a0608", "#5a1420", "#d03a4c", "#ffc8d0"], glow: [255, 70, 90], core: [255, 225, 230], spark: "#ffb0b8" }', "portal palette")
src = swap(src, '} else if (dest === "tiferet") {',
    '} else if (dest === "gevurah") {\n      for (i = 0; i < 5; i++) { var ga = 0.3 + i * 0.62, gx = x + Math.cos(ga) * RX, gy = y + Math.sin(ga) * RY, gh = 14 + (i % 2) * 7;\n        ctx.fillStyle = P.ring[2]; ctx.fillRect(g3(gx) - 1, g3(gy) - gh, 3, gh); ctx.fillStyle = P.ring[3]; ctx.fillRect(g3(gx) - 1, g3(gy) - gh, 3, 3); }\n    } else if (dest === "tiferet") {', "portal spikes")
src = swap(src, '"Sun Court":"#ffd96b"})[worldName]', '"Sun Court":"#ffd96b","Iron Hall":"#ff7a88"})[worldName]', "name colour")
src = swap(src, 'tiferet:"255,210,100"})[WORLD_ID]', 'tiferet:"255,210,100",gevurah:"255,90,110"})[WORLD_ID]', "minimap colour")
src = swap(src, 'tiferet:["aurora","meteors","drift"]};', 'tiferet:["aurora","meteors","drift"],gevurah:["meteors","rain","drift"]};', "weather list")
src = swap(src, 'tiferet:"255,230,170"};', 'tiferet:"255,230,170",gevurah:"255,150,160"};', "rain colour")
src = swap(src, 'tiferet:["255,210,90","255,160,80"]};', 'tiferet:["255,210,90","255,160,80"],gevurah:["255,70,90","255,150,90"]};', "aurora colour")
src = swap(src, 'tiferet:"255,225,140"};', 'tiferet:"255,225,140",gevurah:"255,110,100"};', "drift colour")
src = swap(src, 'tiferet:"golden motes"}', 'tiferet:"golden motes",gevurah:"red sparks"}', "weather name")
src = swap(src, 'sunTick(s,d=>channelRef.current?.publish("sun",d));', 'sunTick(s,d=>channelRef.current?.publish("sun",d));ventTick(s);', "tick")
src = swap(src, "drawSun(ctx,cam,W,H,s.frame,s);", "drawVents(ctx,cam,W,H,s.frame);drawSun(ctx,cam,W,H,s.frame,s);", "draw")
src = swap(src, "{const _g=sunGet();if(_g)_g.forEach(",
    '{ctx.fillStyle="rgba(255,90,70,0.85)";ventsList().forEach(v=>ctx.fillRect(MM_X+(v.x/WORLD_W)*MM_W-1.5,MM_Y+(v.y/WORLD_H)*MM_H-1.5,3,3));}'
    "{const _g=sunGet();if(_g)_g.forEach(", "minimap vents")
src = swap(src, "Object.assign(RECAP,{e:ep,t0:Date.now(),sunup:0,", "Object.assign(RECAP,{e:ep,t0:Date.now(),rides:0,singed:0,sunup:0,", "recap reset")
src = swap(src, "sunup:RECAP.sunup||0}", "sunup:RECAP.sunup||0,rides:RECAP.rides||0,singed:RECAP.singed||0}", "recap stat")
src = swap(src, "if(d.stats.sunup)rows.push(", 'if(d.stats.rides)rows.push(["flames ridden",String(d.stats.rides)]);if(d.stats.singed>=2)rows.push(["times singed",String(d.stats.singed)]);if(d.stats.sunup)rows.push(', "recap rows")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 21 edits applied.")
