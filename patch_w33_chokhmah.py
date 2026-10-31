# patch_w33_chokhmah.py - a ninth world: the Starloom (Chokhmah), the world of wisdom.
# A silver-and-indigo starfield world with its own portal look (orbiting stars), star-dust, aurora and meteors, and a
# bright airy soundscape. Every other world gets a portal to it (top middle) and it has portals to all eight.
# Its mechanic is the constellation. Seven stars lie in a chain (a new pattern every cycle, shown on the minimap). The
# next star in the chain has a tall pale beam so you can spot it from afar. Walk up to each star in order and the lines
# between them light up; reaching the seventh completes the constellation: you glow for 40 seconds with a speed boost,
# and everyone in the world sees you glow (one tiny message, sent only on completion). Then the chain starts over so you
# can draw it again. Recap card: "constellations" drawn. Needs patch_w32_binah.py first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_choch*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_binah*/" not in src:
    print("ABORT: apply patch_w32_binah.py first. Nothing written."); sys.exit(1)

MOD = r'''/*_choch*/
let _skE=-1,_skL=[],_skI=0,_skFl=0;
function starsList(){
  if(WORLD_ID!=="chokhmah")return[];
  const e=getEpoch();
  if(_skE!==e){_skE=e;_skI=0;_skL=[];const r=mulberry32(hashStr(e+"|stars")),pt=PORTALS.chokhmah||{};
    let x=3000+r()*4000,y=3000+r()*4000;
    for(let i=0;i<7;i++){
      if(i>0){for(let t=0;t<40;t++){const a=r()*6.2832,d=650+r()*300,nx=x+Math.cos(a)*d,ny=y+Math.sin(a)*d*0.8;let ok=nx>1200&&nx<8800&&ny>1200&&ny<8800;
        for(const k in pt)if(Math.hypot(nx-pt[k][0],ny-pt[k][1])<400)ok=false;if(ok){x=nx;y=ny;break;}}}
      _skL.push({x,y});}}
  return _skL;
}
function starTick(s,pub){
  if(WORLD_ID!=="chokhmah"){_skI=0;return;}
  const L=starsList();if(!L.length)return;
  const me=s.cats.find(c=>c.id===s.myId);if(!me||me.idle)return;
  const st=L[_skI];if(!st||Math.hypot(me.x-st.x,(me.y-st.y)*2)>=110)return;
  _skI++;
  if(_skI<L.length){try{FKAudio.page();}catch(e){}return;}
  _skI=0;_skFl=Date.now();const now=Date.now();me._glowUntil=now+40000;me._boostTimer=600;RECAP.consts=(RECAP.consts||0)+1;try{FKAudio.beacon();}catch(e){}
  for(let i=0;i<8;i++)s.particles.push({text:"*",x:me.x+(i-4)*7,y:me.y-6,vx:(Math.random()-0.5)*0.6,vy:-0.5-Math.random()*0.5,alpha:1,life:150+i*10,delay:i*5});
  try{pub({e:getEpoch()});}catch(e){}
}
function starGlow(s,cid){
  const c=s.cats.find(k=>k.id===cid);if(!c||c.isGhost)return;c._glowUntil=Date.now()+40000;
  for(let i=0;i<6;i++)s.particles.push({text:"*",x:c.x+(i-3)*8,y:c.y-6,vx:(Math.random()-0.5)*0.6,vy:-0.5-Math.random()*0.5,alpha:1,life:140+i*10,delay:i*5});
}
function drawStarLoom(ctx,cam,W,H,f){
  const L=starsList();if(!L.length)return;const now=Date.now(),fl=Math.max(0,1-(now-_skFl)/2500),pu=0.5+0.5*Math.sin(f*0.07);
  ctx.save();ctx.globalCompositeOperation="lighter";ctx.lineWidth=2;
  for(let i=0;i<L.length-1;i++){const a=L[i],b=L[i+1],lit=i+1<_skI;
    ctx.strokeStyle="rgba(225,232,255,"+Math.min(0.9,(lit?0.5:0.09)+fl*0.5).toFixed(3)+")";ctx.beginPath();ctx.moveTo(Math.round(a.x-cam.x),Math.round(a.y-cam.y));ctx.lineTo(Math.round(b.x-cam.x),Math.round(b.y-cam.y));ctx.stroke();}
  L.forEach((p,i)=>{const sx=Math.round(p.x-cam.x),sy=Math.round(p.y-cam.y),lit=i<_skI,nx=i===_skI;
    if(nx&&sx>-30&&sx<W+30&&sy>0&&sy-700<H){for(let k=0;k<3;k++){ctx.fillStyle="rgba(215,225,255,"+((0.045+0.03*pu)*(3-k)/3).toFixed(3)+")";ctx.fillRect(sx-3-k*3,sy-700,6+k*6,700);}}
    if(sx<-60||sx>W+60||sy<-60||sy>H+60)return;
    const al=lit?0.95:nx?0.7+0.3*pu:0.35,col=lit?"255,244,200":"200,212,255",sz=nx?1.3:1;
    ctx.fillStyle="rgba("+col+","+Math.min(1,al+fl*0.4).toFixed(3)+")";
    ctx.fillRect(Math.round((sx-3*sz)/3)*3,Math.round((sy-3*sz)/3)*3,Math.round(6*sz/3)*3,Math.round(6*sz/3)*3);
    ctx.fillRect(Math.round((sx-1)/3)*3,sy-Math.round(9*sz),3,Math.round(18*sz));ctx.fillRect(sx-Math.round(9*sz),Math.round((sy-1)/3)*3,Math.round(18*sz),3);
    if((lit||nx)&&!LITE){ctx.fillStyle="rgba("+col+",0.10)";ctx.beginPath();ctx.ellipse(sx,sy,34,22,0,0,6.2832);ctx.fill();}
  });
  ctx.restore();
}
let uid=100;'''

CRLF = "\r\n" in src
if CRLF:
    src = src.replace("\r\n", "\n")
n = 0
def S(old, new, label):
    global src, n
    src = swap(src, old, new, label); n += 1

S("let uid=100;", MOD, "star module")
S('binah:{name:"Echo Deep",sky:["#030E18","#0E3A4A"]}};', 'binah:{name:"Echo Deep",sky:["#030E18","#0E3A4A"]},chokhmah:{name:"Starloom",sky:["#060610","#2A2E48"]}};', "world table")
a = src.index("const PORTALS={"); b = src.index("};", src.index("binah:{malkuth:", a)) + 2
tab = src[a:b]
if tab.count("binah:[6500,5200]") != 7 or tab.count("chesed:[3500,5200]}};") != 1:
    print("ABORT portals: unexpected portal table. Nothing written."); sys.exit(1)
tab = tab.replace("binah:[6500,5200]", "binah:[6500,5200],chokhmah:[5000,2200]")
tab = tab.replace("chesed:[3500,5200]}};", "chesed:[3500,5200],chokhmah:[5000,2200]},chokhmah:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[5000,3000],tiferet:[6500,3300],gevurah:[3500,3300],chesed:[3500,5200],binah:[6500,5200]}};")
src = src[:a] + tab + src[b:]; n += 1
S('binah:{root:65.41,scale:[0,3,5,7,10],wave:"sine",cut:420,gap:[6,10],vol:0.07}', 'binah:{root:65.41,scale:[0,3,5,7,10],wave:"sine",cut:420,gap:[6,10],vol:0.07},\n    chokhmah:{root:174.61,scale:[0,2,4,7,9],wave:"sine",cut:1500,gap:[3,6],vol:0.07}', "music table")
S('beds:{beach:0.45,wind:0.2},ev:{drip:[0.28,0],owl:[0.03,"n"]}}',
  'beds:{beach:0.45,wind:0.2},ev:{drip:[0.28,0],owl:[0.03,"n"]}},\n    chokhmah:{root:174.61,sc:[0,2,4,6,7,9,11,12,14],gap:[5,10],sp:1.0,cut:3400,padCut:1300,\n      pad:[[0,4,7,11],[2,6,9,14],[-5,2,7,11],[7,11,14,18]],beds:{wind:0.15},ev:{tinkle:[0.3,0],owl:[0.03,"n"]}}', "engine config")
S('binah:{hor:[20,90,110],neb:[[40,170,190],[30,90,160]],star:[190,240,250],moon:["#06202a","#14566a","#3aa0b0","#c8f4f4"],ring:false,glow:[90,200,220]}',
  'binah:{hor:[20,90,110],neb:[[40,170,190],[30,90,160]],star:[190,240,250],moon:["#06202a","#14566a","#3aa0b0","#c8f4f4"],ring:false,glow:[90,200,220]},\n    chokhmah:{hor:[90,100,150],neb:[[170,180,230],[110,120,180]],star:[240,242,255],moon:["#1c2034","#555d88","#a9b2e0","#f2f4ff"],ring:true,glow:[200,210,255]}', "sky theme")
S('ctx.fillStyle=rg(world==="binah"?[140,230,240]:', 'ctx.fillStyle=rg(world==="chokhmah"?[225,230,255]:world==="binah"?[140,230,240]:', "motes")
S('binah: { ring: ["#041218", "#0f4050", "#2f9aa8", "#d8fbff"], glow: [90, 200, 220], core: [225, 252, 255], spark: "#c8ffff" }',
  'binah: { ring: ["#041218", "#0f4050", "#2f9aa8", "#d8fbff"], glow: [90, 200, 220], core: [225, 252, 255], spark: "#c8ffff" },\n    chokhmah: { ring: ["#0a0c1a", "#2a3058", "#8a96d8", "#f2f4ff"], glow: [190, 200, 255], core: [245, 247, 255], spark: "#ffffff" }', "portal palette")
S('} else if (dest === "binah") {',
  '} else if (dest === "chokhmah") {\n      for (i = 0; i < 3; i++) { for (var cj = 0; cj < 5; cj++) { var cang = t * 0.05 + i * 2.09 - cj * 0.14; ctx.fillStyle = rgba([240, 244, 255], 0.9 - cj * 0.17); ctx.fillRect(g3(x + Math.cos(cang) * (RX + 6)) - 1, g3(y + Math.sin(cang) * (RY + 3)) - 1, 3, 3); } }\n    } else if (dest === "binah") {', "portal decor")
S('"Echo Deep":"#7fe0e8"})[worldName]', '"Echo Deep":"#7fe0e8","Starloom":"#c9d2ff"})[worldName]', "name colour")
S('binah:"100,210,230"})[WORLD_ID]', 'binah:"100,210,230",chokhmah:"190,200,255"})[WORLD_ID]', "minimap colour")
S('binah:["aurora","meteors","drift"]};', 'binah:["aurora","meteors","drift"],chokhmah:["meteors","aurora","drift"]};', "weather list")
S('binah:"140,220,230"};', 'binah:"140,220,230",chokhmah:"190,200,235"};', "rain colour")
S('binah:["60,210,200","90,150,255"]};', 'binah:["60,210,200","90,150,255"],chokhmah:["170,190,255","230,235,255"]};', "aurora colour")
S('binah:"120,230,240"};', 'binah:"120,230,240",chokhmah:"220,225,255"};', "drift colour")
S('binah:"rising bubbles"}', 'binah:"rising bubbles",chokhmah:"star dust"}', "weather name")
S("ventTick(s);echoTick(s);", 'ventTick(s);echoTick(s);starTick(s,d=>channelRef.current?.publish("star",d));', "tick")
S("drawStones(ctx,cam,W,H,s.frame);", "drawStarLoom(ctx,cam,W,H,s.frame);drawStones(ctx,cam,W,H,s.frame);", "draw")
S('{ctx.fillStyle="rgba(120,235,245,0.95)";stonesList()',
  '{starsList().forEach((v,i)=>{ctx.fillStyle=i===_skI?"rgba(255,255,255,1)":i<_skI?"rgba(255,235,160,0.95)":"rgba(170,185,255,0.7)";ctx.fillRect(MM_X+(v.x/WORLD_W)*MM_W-1.5,MM_Y+(v.y/WORLD_H)*MM_H-1.5,3,3);});}'
  '{ctx.fillStyle="rgba(120,235,245,0.95)";stonesList()', "minimap stars")
S('channel.subscribe("sun",(msg)=>{if(msg.clientId===clientId.current)return;',
  'channel.subscribe("star",(msg)=>{if(msg.clientId===clientId.current||WORLD_ID!=="chokhmah")return;starGlow(gs.current,msg.clientId);});channel.subscribe("sun",(msg)=>{if(msg.clientId===clientId.current)return;', "star message")
S("Object.assign(RECAP,{e:ep,t0:Date.now(),echoes:0,", "Object.assign(RECAP,{e:ep,t0:Date.now(),consts:0,echoes:0,", "recap reset")
S("echoes:RECAP.echoes||0}", "echoes:RECAP.echoes||0,consts:RECAP.consts||0}", "recap stat")
S("if(d.stats.echoes)rows.push(", 'if(d.stats.consts)rows.push(["constellations",String(d.stats.consts)]);if(d.stats.echoes)rows.push(', "recap rows")
if CRLF:
    src = src.replace("\n", "\r\n")
open(P, "w", encoding="utf-8", newline="").write(src)
print(f"OK: {n} edits applied.")
