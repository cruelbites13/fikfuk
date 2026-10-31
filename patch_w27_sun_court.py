# patch_w27_sun_court.py - a fifth world: the Sun Court (Tiferet).
# A golden, bright-sky world with its own portal look and its own calm, major-key ambient music; falling gold motes,
# meteors and auroras. Every other world gets a portal to it and it has portals to all four.
# Its mechanic is a group ritual: six glowing sigils on the floor around a central sundial (rotated differently each
# 3-hour cycle). Cats sit still on them. When enough sigils are covered at once - 2 when the world is quiet, up to 6 when
# it is busy (60% of the cats online) - and held for about 5 seconds, the sun rises: a golden flash and chord, a beam from
# the sundial, and a soft golden halo around every cat in that world for the rest of the cycle. It needs at least two cats,
# on purpose. One small message when it happens, re-announced every ~40 s for late joiners. Recap: "raised the sun".
# Needs patch_w24_ash_market.py first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_sun*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_hod*/" not in src:
    print("ABORT: apply patch_w24_ash_market.py first. Nothing written."); sys.exit(1)

MOD = r'''/*_sun*/
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
let uid=100;'''

PORT_OLD = ('const PORTALS={malkuth:{yesod:[5750,4250],netzach:[4250,4250],hod:[5000,3000]},yesod:{malkuth:[5000,5700],netzach:[5750,4250],hod:[4250,4250]},'
            'netzach:{malkuth:[5000,5700],yesod:[4250,4250],hod:[5750,4250]},hod:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250]}};')
PORT_NEW = ('const PORTALS={malkuth:{yesod:[5750,4250],netzach:[4250,4250],hod:[5000,3000],tiferet:[6500,3300]},yesod:{malkuth:[5000,5700],netzach:[5750,4250],hod:[4250,4250],tiferet:[5000,3000]},'
            'netzach:{malkuth:[5000,5700],yesod:[4250,4250],hod:[5750,4250],tiferet:[5000,3000]},hod:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],tiferet:[5000,3000]},'
            'tiferet:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[3500,3500]}};')

src = swap(src, "let uid=100;", MOD, "sun module")
src = swap(src, 'hod:{name:"Ash Market",sky:["#2A0F08","#6A2A14"]}};', 'hod:{name:"Ash Market",sky:["#2A0F08","#6A2A14"]},tiferet:{name:"Sun Court",sky:["#2B1F08","#8A6A1C"]}};', "world table")
src = swap(src, PORT_OLD, PORT_NEW, "portals")
src = swap(src, 'hod:{root:98,scale:[0,1,5,7,8],wave:"triangle",cut:700,gap:[3,7],vol:0.075}',
    'hod:{root:98,scale:[0,1,5,7,8],wave:"triangle",cut:700,gap:[3,7],vol:0.075},\n    tiferet:{root:130.81,scale:[0,4,7,11,14],wave:"sine",cut:1100,gap:[3,6],vol:0.075}', "music")
src = swap(src, 'hod:{hor:[150,60,30],neb:[[255,120,50],[200,60,40]],star:[255,225,190],moon:["#3a1208","#8a3a1c","#e07a3a","#ffe0b0"],ring:false,glow:[255,150,70]}',
    'hod:{hor:[150,60,30],neb:[[255,120,50],[200,60,40]],star:[255,225,190],moon:["#3a1208","#8a3a1c","#e07a3a","#ffe0b0"],ring:false,glow:[255,150,70]},\n    tiferet:{hor:[190,140,40],neb:[[255,210,90],[255,150,60]],star:[255,245,210],moon:["#4a3410","#a8782a","#f0c050","#fff4c0"],ring:true,glow:[255,215,110]}', "sky theme")
src = swap(src, 'ctx.fillStyle=rg(world==="hod"?[255,170,90]:', 'ctx.fillStyle=rg(world==="tiferet"?[255,225,140]:world==="hod"?[255,170,90]:', "motes")
src = swap(src, 'hod: { ring: ["#2a0f08", "#6a2a14", "#e07a3a", "#ffe0a8"], glow: [255, 140, 60], core: [255, 235, 190], spark: "#ffcf80" }',
    'hod: { ring: ["#2a0f08", "#6a2a14", "#e07a3a", "#ffe0a8"], glow: [255, 140, 60], core: [255, 235, 190], spark: "#ffcf80" },\n    tiferet: { ring: ["#3a2808", "#8a6a1c", "#f0c050", "#fff4c0"], glow: [255, 215, 100], core: [255, 250, 220], spark: "#fff2b0" }', "portal palette")
src = swap(src, '} else if (dest === "hod") {',
    '} else if (dest === "tiferet") {\n      for (i = 0; i < 4; i++) { var ta = t * 0.03 + i * PI / 2, tx = x + Math.cos(ta) * (RX + 9), ty = y + Math.sin(ta) * (RY + 5) - 4;\n        ctx.fillStyle = rgba([255, 240, 170], 0.5 + 0.4 * Math.sin(t * 0.08 + i)); ctx.fillRect(g3(tx) - 1, g3(ty) - 5, 3, 11); ctx.fillRect(g3(tx) - 5, g3(ty) - 1, 11, 3); }\n    } else if (dest === "hod") {', "portal rays")
src = swap(src, '"Ash Market":"#ffb070"})[worldName]', '"Ash Market":"#ffb070","Sun Court":"#ffd96b"})[worldName]', "name colour")
src = swap(src, 'hod:"255,150,80"})[WORLD_ID]', 'hod:"255,150,80",tiferet:"255,210,100"})[WORLD_ID]', "minimap colour")
src = swap(src, 'hod:["drift","meteors","rain"]};', 'hod:["drift","meteors","rain"],tiferet:["aurora","meteors","drift"]};', "weather list")
src = swap(src, 'hod:"235,160,120"};', 'hod:"235,160,120",tiferet:"255,230,170"};', "rain colour")
src = swap(src, 'hod:["255,120,60","255,200,90"]};', 'hod:["255,120,60","255,200,90"],tiferet:["255,210,90","255,160,80"]};', "aurora colour")
src = swap(src, 'hod:"255,150,70"};', 'hod:"255,150,70",tiferet:"255,225,140"};', "drift colour")
src = swap(src, 'hod:"falling embers"}', 'hod:"falling embers",tiferet:"golden motes"}', "weather name")
src = swap(src, 'hodTick(s,d=>channelRef.current?.publish("hod",d));', 'hodTick(s,d=>channelRef.current?.publish("hod",d));sunTick(s,d=>channelRef.current?.publish("sun",d));', "tick")
src = swap(src, "drawHod(ctx,cam,W,H,s.frame,s);", "drawSun(ctx,cam,W,H,s.frame,s);drawHod(ctx,cam,W,H,s.frame,s);", "draw")
src = swap(src, 'channel.subscribe("hod",(msg)=>{',
    'channel.subscribe("sun",(msg)=>{if(msg.clientId===clientId.current)return;const d=msg.data||{};if(WORLD_ID!=="tiferet"||d.e!==getEpoch())return;if(!sunGet())return;if(SUN.lit){SUN.sil=0;return;}sunLight(gs.current,null);});'
    'channel.subscribe("hod",(msg)=>{', "listen")
src = swap(src, "{const _h=hodGet();if(_h)_h.br.forEach(",
    '{const _g=sunGet();if(_g)_g.forEach(g=>{ctx.fillStyle=g.on?"rgba(255,235,160,1)":"rgba(255,215,110,0.7)";ctx.fillRect(MM_X+(g.x/WORLD_W)*MM_W-1.5,MM_Y+(g.y/WORLD_H)*MM_H-1.5,3,3);});}'
    "{const _h=hodGet();if(_h)_h.br.forEach(", "minimap sigils")
src = swap(src, "Object.assign(RECAP,{e:ep,t0:Date.now(),fed:0,", "Object.assign(RECAP,{e:ep,t0:Date.now(),sunup:0,fed:0,", "recap reset")
src = swap(src, "fed:RECAP.fed||0}", "fed:RECAP.fed||0,sunup:RECAP.sunup||0}", "recap stat")
src = swap(src, "if(d.stats.fed)rows.push(", 'if(d.stats.sunup)rows.push(["raised the sun","yes"]);if(d.stats.fed)rows.push(', "recap row")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 22 edits applied.")
