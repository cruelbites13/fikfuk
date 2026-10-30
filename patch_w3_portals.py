# patch_w3_portals.py - world step 3 of 3: glowing rings that carry a cat between the three worlds.
# - walk into a ring: screen fades, you arrive in the other world standing just beside its ring back
# - each ring shows the destination name and "?" for its crowd (no live counts, keeps traffic low)
# - before entering, the destination's headcount is checked (50 max); full world = you are nudged back, with a note
# - a 4 second cooldown between hops so nobody can hammer the connection
# Needs patch_w2_content first. All-or-nothing, idempotent, safe on Windows files.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in src else "\n"

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "const PORTALS=" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "const WORLDS=" not in src:
    print("ABORT: apply patch_w2_content.py first. Nothing written."); sys.exit(1)

src = swap(src, "purrRadius:170}};",
    "purrRadius:170}};const WORLD_CAP=50;"
    "const PORTALS={malkuth:{yesod:[5750,4250],netzach:[4250,4250]},"
    "yesod:{malkuth:[5000,5700],netzach:[5750,4250]},"
    "netzach:{malkuth:[5000,5700],yesod:[4250,4250]}};"
    "function awayFromRing(p){const dx=WORLD_W/2-p[0],dy=WORLD_H/2-p[1],d=Math.hypot(dx,dy)||1;return[p[0]+dx/d*170,p[1]+dy/d*170];}", "portal table")
src = swap(src, 'const [worldName,setWorldName]=useState("Malkuth Gate");',
    'const [worldName,setWorldName]=useState("Malkuth Gate");const [fade,setFade]=useState(false);', "fade state")

HOP = NL.join([
 "  function hopTo(dest){",
 "    const s=gs.current;",
 "    const me=s.cats.find(c=>c.id===s.myId);",
 "    const t=Date.now();",
 "    if(!me||!s.ready||s._hop||!WORLDS[dest]||t-(s._hopT||0)<4000)return;",
 "    s._hop=true;s._hopT=t;setFade(true);",
 "    const from=WORLD_ID;",
 "    const finish=(ok)=>{",
 "      if(!ok){",
 "        const p=(PORTALS[from]||{})[dest];if(p){const q=awayFromRing(p);me.x=q[0];me.y=q[1];me.vx=0;me.vy=0;}",
 "        s.particles.push({text:\"that world is full\",x:me.x-30,y:me.y-20,vx:0,vy:-0.4,alpha:1,life:200,delay:0});",
 "        setFade(false);s._hop=false;return;",
 "      }",
 "      setTimeout(()=>{",
 "        joinWorld(dest);",
 "        const back=(PORTALS[dest]||{})[from];const q=back?awayFromRing(back):[WORLD_W/2,WORLD_H/2];",
 "        me.x=q[0];me.y=q[1];me.vx=0;me.vy=0;s._lastMove=null;",
 "        const cv=canvasRef.current;if(cv)s.cam={x:me.x-cv.width/2,y:me.y-cv.height/2};",
 "        setFade(false);setTimeout(()=>{s._hop=false;},300);",
 "      },350);",
 "    };",
 "    let called=false;const once=(ok)=>{if(called)return;called=true;finish(ok);};",
 "    setTimeout(()=>once(true),2500);",
 "    try{ablyRef.current.channels.get(channelFor(dest)).presence.get().then(m=>once(!m||m.length<WORLD_CAP)).catch(()=>once(true));}catch(e){once(true);}",
 "  }",
 "",
 "  function joinWorld(id){"])
src = swap(src, "  function joinWorld(id){", HOP, "hopTo")

src = swap(src, "if(s.frame%60===0){const _n=s.cats.filter(c=>!c.isSys&&!c.isGhost).length;",
    "/*_portal*/if(!s._hop){const _pt=PORTALS[WORLD_ID]||{};for(const _d in _pt){if(Math.hypot(myCat.x-_pt[_d][0],myCat.y-_pt[_d][1])<60){hopTo(_d);break;}}}"
    "if(s.frame%60===0){const _n=s.cats.filter(c=>!c.isSys&&!c.isGhost).length;", "ring trigger")

DRAW = ("/*_rings*/{const _pt=PORTALS[WORLD_ID]||{};for(const _d in _pt){const _sx=_pt[_d][0]-cam.x,_sy=_pt[_d][1]-cam.y;"
 "if(_sx<-120||_sx>W+120||_sy<-120||_sy>H+120)continue;"
 "const _pu=Math.sin(s.frame*0.05);ctx.save();ctx.lineWidth=3;"
 "for(let _i=0;_i<3;_i++){ctx.strokeStyle=\"rgba(180,140,255,\"+(0.55-_i*0.15+_pu*0.15)+\")\";ctx.beginPath();ctx.arc(_sx,_sy,26+_i*12+_pu*3,0,Math.PI*2);ctx.stroke();}"
 "ctx.fillStyle=\"rgba(180,140,255,0.12)\";ctx.beginPath();ctx.arc(_sx,_sy,26,0,Math.PI*2);ctx.fill();"
 "ctx.font=\"7px \"+ff;ctx.textAlign=\"center\";ctx.fillStyle=\"rgba(255,255,255,0.75)\";ctx.fillText(WORLDS[_d].name,_sx,_sy-62);"
 "ctx.fillStyle=\"rgba(255,255,255,0.4)\";ctx.fillText(\"?\",_sx,_sy+74);ctx.restore();}}")
src = swap(src, "const myCatSR=gs.current.cats.find(c=>c.id===gs.current.myId);", DRAW + "const myCatSR=gs.current.cats.find(c=>c.id===gs.current.myId);", "draw rings")

src = swap(src, '<span style={{fontSize:7,color:"rgba(255,255,255,0.45)"}}>{worldName}</span>',
    '<div style={{position:"fixed",left:0,top:0,right:0,bottom:0,background:"#000",opacity:fade?1:0,pointerEvents:"none",transition:"opacity 0.3s",zIndex:50}}/>'
    '<span style={{fontSize:7,color:"rgba(255,255,255,0.45)"}}>{worldName}</span>', "fade overlay")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 6 edits applied. Walk into a ring in the world to travel. Console shortcut: __fikfukGo(\"yesod\") still works.")
