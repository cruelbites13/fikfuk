# patch_w32_binah.py - an eighth world: Echo Deep (Binah), the world of understanding and silence.
# A dark teal deep-sea world with its own portal look (echo rings), rising bubbles, aurora and meteors, and a slow
# sea-wave soundscape. Every other world gets a portal to it (lower right) and it has portals to all seven.
# Its mechanic is the echo. Six tall Echo Stones stand around (new spots every cycle, shown as teal dots on the minimap).
# When anybody chirps within about 500 pixels of a stone, that stone remembers it and about 3 seconds later answers: a
# ring spreads out from the stone with a soft chirp sound, and any cat standing near the stone has its confessions
# revealed, as if it had been chirped at. Everyone sees the same thing (it follows the chirps already being shared, no new
# messages). Recap card: "echoes heard" (echoes that rang near you). Needs patch_w30_chesed.py first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_binah*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_chesed*/" not in src:
    print("ABORT: apply patch_w30_chesed.py first. Nothing written."); sys.exit(1)

MOD = r'''/*_binah*/
let _stE=-1,_stL=[],_ecQ=[];
function stonesList(){
  if(WORLD_ID!=="binah")return[];
  const e=getEpoch();
  if(_stE!==e){_stE=e;_stL=[];_ecQ=[];const r=mulberry32(hashStr(e+"|stones")),pt=PORTALS.binah||{};
    for(let i=0;i<600&&_stL.length<6;i++){const x=1200+r()*7600,y=1200+r()*7600;let ok=Math.hypot(x-5000,y-5000)>300;
      for(const k in pt)if(Math.hypot(x-pt[k][0],y-pt[k][1])<450)ok=false;
      _stL.forEach(o=>{if(Math.hypot(x-o.x,y-o.y)<1000)ok=false;});
      if(ok)_stL.push({x,y,q:0,fl:0});}}
  return _stL;
}
function echoChirp(x,y){const L=stonesList(),now=Date.now();L.forEach(st=>{if(!st.q&&Math.hypot(x-st.x,y-st.y)<500){st.q=now+3200;_ecQ.push(st);}});}
function echoTick(s){
  if(WORLD_ID!=="binah"){if(_ecQ.length)_ecQ.length=0;return;}
  stonesList();const now=Date.now();
  for(let i=_ecQ.length-1;i>=0;i--){const st=_ecQ[i];if(now<st.q)continue;_ecQ.splice(i,1);st.q=0;st.fl=now;
    const me=s.cats.find(c=>c.id===s.myId),d=me?Math.hypot(me.x-st.x,me.y-st.y):9999;
    if(d<700){try{FKAudio.chirp(0.7*(1-d/700));}catch(e){}}
    if(d<250)RECAP.echoes=(RECAP.echoes||0)+1;
    s.cats.forEach(c=>{if(c.isGhost||c.isSys)return;if(Math.hypot(c.x-st.x,c.y-st.y)<250&&c.confessions&&c.confessions.length){c.revealAlpha=Math.max(c.revealAlpha||0,0.9);c.revealTimer=100;}});}
}
function drawStones(ctx,cam,W,H,f){
  const L=stonesList();if(!L.length)return;const now=Date.now();
  L.forEach((st,i)=>{const sx=Math.round(st.x-cam.x),sy=Math.round(st.y-cam.y);if(sx<-300||sx>W+300||sy<-200||sy>H+160)return;
    const pend=st.q?1:0,el=st.fl?now-st.fl:99999,fa=Math.max(0,1-el/1400),pu=0.5+0.5*Math.sin(f*0.04+i*2);
    ctx.save();
    ctx.fillStyle="rgba(0,0,0,0.4)";ctx.beginPath();ctx.ellipse(sx+3,sy+4,34,11,0,0,6.2832);ctx.fill();
    ctx.fillStyle="#06202a";ctx.fillRect(sx-21,sy-96,42,96);ctx.fillStyle="#0f3f50";ctx.fillRect(sx-21,sy-96,30,96);ctx.fillStyle="#1d6a7c";ctx.fillRect(sx-21,sy-96,12,96);
    ctx.fillStyle="#0a2e3b";ctx.fillRect(sx-24,sy-102,48,6);
    ctx.globalCompositeOperation="lighter";
    const a=Math.min(1,0.25+0.2*pu+0.5*pend*pu+0.6*fa);
    ctx.fillStyle="rgba(120,230,240,"+a.toFixed(3)+")";ctx.fillRect(sx-3,sy-82,6,6);ctx.fillRect(sx-3,sy-64,6,18);ctx.fillRect(sx-9,sy-46,18,6);
    if(!LITE){ctx.fillStyle="rgba(90,200,220,"+(0.05+0.05*pu+0.1*fa).toFixed(3)+")";ctx.beginPath();ctx.ellipse(sx,sy-50,44,70,0,0,6.2832);ctx.fill();}
    if(fa>0){for(let k=0;k<2;k++){const r=Math.max(4,250*(1-fa)*(1-k*0.3));ctx.strokeStyle="rgba(170,245,255,"+(fa*0.7*(1-k*0.4)).toFixed(3)+")";ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(sx,sy,r,r/2,0,0,6.2832);ctx.stroke();}}
    ctx.restore();
  });
}
let uid=100;'''

CRLF = "\r\n" in src
if CRLF:
    src = src.replace("\r\n", "\n")
n = 0
def S(old, new, label):
    global src, n
    src = swap(src, old, new, label); n += 1

S("let uid=100;", MOD, "echo module")
S('chesed:{name:"Open Hand",sky:["#0A1830","#2C5C9A"]}};', 'chesed:{name:"Open Hand",sky:["#0A1830","#2C5C9A"]},binah:{name:"Echo Deep",sky:["#030E18","#0E3A4A"]}};', "world table")
# portals: edit the existing table text in place (every world gets a binah portal; binah gets its own table)
a = src.index("const PORTALS={"); b = src.index("};", src.index("chesed:{malkuth:", a)) + 2
tab = src[a:b]
if tab.count("chesed:[3500,5200]") != 6 or tab.count("gevurah:[3500,3300]}};") != 1:
    print("ABORT portals: unexpected portal table. Nothing written."); sys.exit(1)
tab = tab.replace("chesed:[3500,5200]", "chesed:[3500,5200],binah:[6500,5200]")
tab = tab.replace("gevurah:[3500,3300]}};", "gevurah:[3500,3300],binah:[6500,5200]},binah:{malkuth:[5000,5700],yesod:[5750,4250],netzach:[4250,4250],hod:[5000,3000],tiferet:[6500,3300],gevurah:[3500,3300],chesed:[3500,5200]}};")
src = src[:a] + tab + src[b:]; n += 1
S('chesed:{root:98,scale:[0,2,4,7,9],wave:"sine",cut:1300,gap:[3,6],vol:0.07}', 'chesed:{root:98,scale:[0,2,4,7,9],wave:"sine",cut:1300,gap:[3,6],vol:0.07},\n    binah:{root:65.41,scale:[0,3,5,7,10],wave:"sine",cut:420,gap:[6,10],vol:0.07}', "music table")
S('beds:{river:0.3,wind:0.1},ev:{tinkle:[0.12,0],bird:[0.15,"d"],cricket:[0.25,"n"],drip:[0.08,0]}}',
  'beds:{river:0.3,wind:0.1},ev:{tinkle:[0.12,0],bird:[0.15,"d"],cricket:[0.25,"n"],drip:[0.08,0]}},\n    binah:{root:130.81,sc:[0,2,3,7,8,12,14,15,19],gap:[8,14],sp:1.4,cut:1700,padCut:600,\n      pad:[[0,7,10,15],[-4,3,7,12],[-2,5,10,14],[-7,0,5,8]],beds:{beach:0.45,wind:0.2},ev:{drip:[0.28,0],owl:[0.03,"n"]}}', "engine config")
S('chesed:{hor:[60,120,200],neb:[[120,190,255],[200,230,255]],star:[225,240,255],moon:["#12284a","#3a6aa8","#8cc0f0","#eaf6ff"],ring:false,glow:[150,200,255]}',
  'chesed:{hor:[60,120,200],neb:[[120,190,255],[200,230,255]],star:[225,240,255],moon:["#12284a","#3a6aa8","#8cc0f0","#eaf6ff"],ring:false,glow:[150,200,255]},\n    binah:{hor:[20,90,110],neb:[[40,170,190],[30,90,160]],star:[190,240,250],moon:["#06202a","#14566a","#3aa0b0","#c8f4f4"],ring:false,glow:[90,200,220]}', "sky theme")
S('ctx.fillStyle=rg(world==="chesed"?[200,230,255]:', 'ctx.fillStyle=rg(world==="binah"?[140,230,240]:world==="chesed"?[200,230,255]:', "motes")
S('chesed: { ring: ["#0d2038", "#2a5a94", "#7ab8f0", "#eaf8ff"], glow: [140, 200, 255], core: [240, 250, 255], spark: "#ffffff" }',
  'chesed: { ring: ["#0d2038", "#2a5a94", "#7ab8f0", "#eaf8ff"], glow: [140, 200, 255], core: [240, 250, 255], spark: "#ffffff" },\n    binah: { ring: ["#041218", "#0f4050", "#2f9aa8", "#d8fbff"], glow: [90, 200, 220], core: [225, 252, 255], spark: "#c8ffff" }', "portal palette")
S('} else if (dest === "chesed") {',
  '} else if (dest === "binah") {\n      for (i = 0; i < 3; i++) { var bq = ((t * 0.012 + i / 3) % 1); ctx.strokeStyle = rgba([200, 250, 255], 0.6 * (1 - bq)); ctx.lineWidth = 2; ctx.beginPath(); ctx.ellipse(x, y, RX * (0.4 + 0.6 * bq), RY * (0.4 + 0.6 * bq), 0, 0, 6.2832); ctx.stroke(); }\n    } else if (dest === "chesed") {', "portal decor")
S('"Open Hand":"#9fd0ff"})[worldName]', '"Open Hand":"#9fd0ff","Echo Deep":"#7fe0e8"})[worldName]', "name colour")
S('chesed:"140,200,255"})[WORLD_ID]', 'chesed:"140,200,255",binah:"100,210,230"})[WORLD_ID]', "minimap colour")
S('chesed:["aurora","drift","rain"]};', 'chesed:["aurora","drift","rain"],binah:["aurora","meteors","drift"]};', "weather list")
S('chesed:"170,215,255"};', 'chesed:"170,215,255",binah:"140,220,230"};', "rain colour")
S('chesed:["90,200,255","200,230,255"]};', 'chesed:["90,200,255","200,230,255"],binah:["60,210,200","90,150,255"]};', "aurora colour")
S('chesed:"200,230,255"};', 'chesed:"200,230,255",binah:"120,230,240"};', "drift colour")
S('chesed:"drifting lights"}', 'chesed:"drifting lights",binah:"rising bubbles"}', "weather name")
S("ventTick(s);", "ventTick(s);echoTick(s);", "tick")
S("drawPools(ctx,cam,W,H,s.frame);", "drawStones(ctx,cam,W,H,s.frame);drawPools(ctx,cam,W,H,s.frame);", "draw")
S('{ctx.fillStyle="rgba(140,205,255,0.9)";poolsList()',
  '{ctx.fillStyle="rgba(120,235,245,0.95)";stonesList().forEach(v=>ctx.fillRect(MM_X+(v.x/WORLD_W)*MM_W-1.5,MM_Y+(v.y/WORLD_H)*MM_H-1.5,3,3));}'
  '{ctx.fillStyle="rgba(140,205,255,0.9)";poolsList()', "minimap stones")
S("kindChirp(x,y,fromId,gs.current);", 'kindChirp(x,y,fromId,gs.current);if(!_r&&WORLD_ID==="binah")echoChirp(x,y);', "chirp hook")
S("Object.assign(RECAP,{e:ep,t0:Date.now(),warmed:0,felt:0,", "Object.assign(RECAP,{e:ep,t0:Date.now(),echoes:0,warmed:0,felt:0,", "recap reset")
S("warmed:RECAP.warmed||0,felt:RECAP.felt||0}", "warmed:RECAP.warmed||0,felt:RECAP.felt||0,echoes:RECAP.echoes||0}", "recap stat")
S("if(d.stats.warmed)rows.push(", 'if(d.stats.echoes)rows.push(["echoes heard",String(d.stats.echoes)]);if(d.stats.warmed)rows.push(', "recap rows")
if CRLF:
    src = src.replace("\n", "\r\n")
open(P, "w", encoding="utf-8", newline="").write(src)
print(f"OK: {n} edits applied.")
