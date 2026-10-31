# patch_w24_ash_market.py - a fourth world: the Ash Market (Hod).
# A warm, smoky world: ember-orange sky, its own portal look, its own ambient music, falling embers / meteors / ash-rain.
# Every other world gets a new portal to it, and it has portals back to all three.
# Its mechanic is a shared goal: 24 glowing embers lie scattered (new spots every 3-hour cycle). Walk over one to pick it up
# ("embers 2" shows at the bottom). Sit next to one of the 3 cold braziers to feed it one ember every half second; each needs
# 3 to light. When all 3 are lit the market opens for everyone in that world: a warm tint and a slow rise of paper lanterns
# for the rest of the cycle, plus the beacon chord. Pickups and feeding are shared with one small message each, and the
# brazier fuel is re-announced every ~40 s so late joiners catch up. Recap card gets an "embers fed" row.
# Needs patch_w22_lite.py first (it reads the lite flag). All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_hod*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_lite*/" not in src:
    print("ABORT: apply patch_w22_lite.py first. Nothing written."); sys.exit(1)

MOD = r'''/*_hod*/
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
let uid=100;'''

PORT_OLD = 'const PORTALS={malkuth:{yesod:[5750,4250],netzach:[4250,4250]},yesod:{malkuth:[5000,5700],netzach:[5750,4250]},netzach:{malkuth:[5000,5700],yesod:[4250,4250]}};'
PORT_NEW = ('const PORTALS={malkuth:{yesod:[5750,4250],netzach:[4250,4250],hod:[5000,3000]},yesod:{malkuth:[5000,5700],netzach:[5750,4250],hod:[4250,4250]},'
            'netzach:{malkuth:[5000,5700],yesod:[4250,4250],hod:[5750,4250]},hod:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250]}};')

src = swap(src, "let uid=100;", MOD, "hod module")
src = swap(src, 'netzach:{name:"Root Archive",sky:["#0D2318","#2E5A3A"],purrRadius:170}};', 'netzach:{name:"Root Archive",sky:["#0D2318","#2E5A3A"],purrRadius:170},hod:{name:"Ash Market",sky:["#2A0F08","#6A2A14"]}};', "world table")
src = swap(src, PORT_OLD, PORT_NEW, "portals")
src = swap(src, 'netzach:{root:82.41,scale:[0,2,3,7,8],wave:"sine",cut:400,gap:[6,11],vol:0.08}',
    'netzach:{root:82.41,scale:[0,2,3,7,8],wave:"sine",cut:400,gap:[6,11],vol:0.08},\n    hod:{root:98,scale:[0,1,5,7,8],wave:"triangle",cut:700,gap:[3,7],vol:0.075}', "music")
src = swap(src, 'netzach:{hor:[40,110,70],neb:[[70,200,110],[200,190,80]],star:[225,255,215],moon:["#10281a","#2f6a3c","#79b25a","#ecf0a0"],ring:false,glow:[130,225,130]}',
    'netzach:{hor:[40,110,70],neb:[[70,200,110],[200,190,80]],star:[225,255,215],moon:["#10281a","#2f6a3c","#79b25a","#ecf0a0"],ring:false,glow:[130,225,130]},\n    hod:{hor:[150,60,30],neb:[[255,120,50],[200,60,40]],star:[255,225,190],moon:["#3a1208","#8a3a1c","#e07a3a","#ffe0b0"],ring:false,glow:[255,150,70]}', "sky theme")
src = swap(src, 'ctx.fillStyle=rg(world==="netzach"?[200,255,140]:', 'ctx.fillStyle=rg(world==="hod"?[255,170,90]:world==="netzach"?[200,255,140]:', "motes")
src = swap(src, 'netzach: { ring: ["#0b1c12", "#244a2c", "#5f8f45", "#d9d77a"], glow: [120, 220, 130], core: [235, 255, 190], spark: "#ffe9a0" }',
    'netzach: { ring: ["#0b1c12", "#244a2c", "#5f8f45", "#d9d77a"], glow: [120, 220, 130], core: [235, 255, 190], spark: "#ffe9a0" },\n    hod: { ring: ["#2a0f08", "#6a2a14", "#e07a3a", "#ffe0a8"], glow: [255, 140, 60], core: [255, 235, 190], spark: "#ffcf80" }', "portal palette")
src = swap(src, '} else if (dest === "malkuth") {',
    '} else if (dest === "hod") {\n      for (i = 0; i < 5; i++) { var ea = 0.4 + i * 1.3, ex = x + Math.cos(ea) * RX, ey = y + Math.sin(ea) * RY - ((t * 0.5 + i * 23) % 40);\n        ctx.fillStyle = rgba([255, 170 + i * 10, 80], 0.9 - ((t * 0.5 + i * 23) % 40) / 50); ctx.fillRect(g3(ex) - 1, g3(ey) - 1, 3, 3); }\n    } else if (dest === "malkuth") {', "portal embers")
src = swap(src, '"Root Archive":"#8fd070"})[worldName]', '"Root Archive":"#8fd070","Ash Market":"#ffb070"})[worldName]', "name colour")
src = swap(src, 'netzach:"130,225,130"})[WORLD_ID]', 'netzach:"130,225,130",hod:"255,150,80"})[WORLD_ID]', "minimap colour")
src = swap(src, 'netzach:["drift","meteors","rain"]};', 'netzach:["drift","meteors","rain"],hod:["drift","meteors","rain"]};', "weather list")
src = swap(src, 'netzach:"150,230,190"};', 'netzach:"150,230,190",hod:"235,160,120"};', "rain colour")
src = swap(src, 'netzach:["120,255,150","200,255,120"]};', 'netzach:["120,255,150","200,255,120"],hod:["255,120,60","255,200,90"]};', "aurora colour")
src = swap(src, 'netzach:"170,255,150"};', 'netzach:"170,255,150",hod:"255,150,70"};', "drift colour")
src = swap(src, 'netzach:"spore drift"}', 'netzach:"spore drift",hod:"falling embers"}', "weather name")
src = swap(src, 'pagesTick(s,d=>channelRef.current?.publish("dig",d));', 'pagesTick(s,d=>channelRef.current?.publish("dig",d));hodTick(s,d=>channelRef.current?.publish("hod",d));', "tick")
src = swap(src, "drawDashTrail(ctx,cam,s);", "drawHod(ctx,cam,W,H,s.frame,s);drawDashTrail(ctx,cam,s);", "draw")
src = swap(src, 'channel.subscribe("dig",(msg)=>{',
    'channel.subscribe("hod",(msg)=>{if(msg.clientId===clientId.current)return;const d=msg.data||{};if(WORLD_ID!=="hod"||d.e!==getEpoch())return;const L=hodGet();if(!L)return;'
    'if(d.k==="e"){const o=L.em[d.i];if(o)o.taken=true;}'
    'else if(d.k==="b"){const b=L.br[d.i];if(b&&(d.f|0)>b.fuel){b.fuel=Math.min(b.need,d.f|0);hodFuel(b);}HOD.sil=0;}'
    'else if(d.k==="s"&&Array.isArray(d.f)){L.br.forEach((b,i)=>{const f=Math.min(b.need,d.f[i]|0);if(f>b.fuel){b.fuel=f;hodFuel(b);}});HOD.sil=0;}});'
    'channel.subscribe("dig",(msg)=>{', "listen")
src = swap(src, '{ctx.fillStyle="rgba(190,255,170,0.9)";pagesList()',
    '{const _h=hodGet();if(_h)_h.br.forEach(b=>{ctx.fillStyle=b.lit?"rgba(255,200,110,1)":"rgba(255,120,60,0.9)";ctx.fillRect(MM_X+(b.x/WORLD_W)*MM_W-2,MM_Y+(b.y/WORLD_H)*MM_H-2,4,4);});}'
    '{ctx.fillStyle="rgba(190,255,170,0.9)";pagesList()', "minimap braziers")
src = swap(src, "Object.assign(RECAP,{e:ep,t0:Date.now(),dashes:0,", "Object.assign(RECAP,{e:ep,t0:Date.now(),fed:0,embers:0,dashes:0,", "recap reset")
src = swap(src, "dashes:RECAP.dashes||0}", "dashes:RECAP.dashes||0,fed:RECAP.fed||0}", "recap stat")
src = swap(src, "if(d.stats.pages)rows.push(", 'if(d.stats.fed)rows.push(["embers fed",String(d.stats.fed)]);if(d.stats.pages)rows.push(', "recap row")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 22 edits applied.")
