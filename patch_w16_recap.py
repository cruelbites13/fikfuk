# patch_w16_recap.py - the reset recap card.
# While you play, the game quietly counts a few things about your cat's life in this world (mice caught, portals taken,
# time spent purring with others, whispers sent, boss hits, biggest crowd you saw). When the 3-hour wipe happens, it draws
# a tall 9:16 picture (your cat, its name, the world, the stats) and shows a small thumbnail on the screen where you
# pick a new cat, with "save" and "share" buttons. Nothing is sent anywhere; the picture is made on your own device.
# Needs the earlier world patches (w2). All-or-nothing, idempotent, CRLF-safe.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_recap*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "const WORLDS=" not in src:
    print("ABORT: apply the world patches (w1..w2) first. Nothing written."); sys.exit(1)

MOD = r'''/*_recap*/
const RECAP={e:-1,t0:0,mice:0,hops:0,words:0,hits:0,purr:0,peak:0,w:{}};
function recapStart(){let d=null;try{d=JSON.parse(localStorage.getItem("fikfuk_r")||"null");}catch(e){}
  const ep=getEpoch();if(d&&d.e===ep){Object.assign(RECAP,d);}else{Object.assign(RECAP,{e:ep,t0:Date.now(),mice:0,hops:0,words:0,hits:0,purr:0,peak:0,w:{}});}
  RECAP.w[WORLD_ID]=1;}
function recapSave(){try{localStorage.setItem("fikfuk_r",JSON.stringify(RECAP));}catch(e){}}
function recapFmt(ms){const m=Math.max(1,Math.round(ms/60000));return m<60?m+"m":Math.floor(m/60)+"h "+(m%60)+"m";}
function renderRecap(d){
  const W=540,H=960,cv=document.createElement("canvas");cv.width=W;cv.height=H;const ctx=cv.getContext("2d");
  ctx.imageSmoothingEnabled=false;
  const w=WORLDS[d.world]||WORLDS.malkuth;
  try{ctx.fillStyle=w.sky[0];ctx.fillRect(0,0,W,H);drawSky(ctx,W,H,{x:5000,y:5000},0,d.world,"#0B0B18",true);}catch(e){}
  let g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,"rgba(0,0,0,0.55)");g.addColorStop(0.35,"rgba(0,0,0,0.05)");g.addColorStop(0.6,"rgba(0,0,0,0.45)");g.addColorStop(1,"rgba(0,0,0,0.85)");
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  ctx.textAlign="center";ctx.textBaseline="alphabetic";
  ctx.fillStyle="#ff4444";ctx.font="22px "+ff;ctx.fillText("fikfuk.wtf",W/2,80);
  ctx.fillStyle="rgba(255,255,255,0.55)";ctx.font="12px "+ff;ctx.fillText(w.name,W/2,114);
  // glow + ground under the cat
  const p=16,cx=W/2,cy=360;
  ctx.save();ctx.globalCompositeOperation="lighter";
  g=ctx.createRadialGradient(cx,cy+70,10,cx,cy+70,230);g.addColorStop(0,"rgba(255,120,120,0.30)");g.addColorStop(1,"rgba(255,120,120,0)");
  ctx.fillStyle=g;ctx.fillRect(0,cy-200,W,520);ctx.restore();
  ctx.fillStyle="rgba(0,0,0,0.45)";ctx.beginPath();ctx.ellipse(cx,cy+11*p,6.4*p,1.4*p,0,0,Math.PI*2);ctx.fill();
  drawCat(ctx,cx-4.5*p,cy-p,p,40,d.pal,d.flip,"sit",false,false,false,false);
  ctx.fillStyle="#fff";ctx.font="26px "+ff;ctx.fillText(d.name,W/2,cy+11*p+64);
  const rows=[["stayed",recapFmt(d.lived)]];
  if(d.stats.mice)rows.push(["mice caught",String(d.stats.mice)]);
  if(d.stats.hops)rows.push(["portals taken",String(d.stats.hops)]);
  if(d.stats.purr>=30)rows.push(["purring together",recapFmt(d.stats.purr*1000)]);
  if(d.stats.words)rows.push(["whispers sent",String(d.stats.words)]);
  if(d.stats.hits)rows.push(["boss hits",String(d.stats.hits)]);
  if(d.stats.peak>1)rows.push(["most cats at once",String(d.stats.peak)]);
  let y=cy+11*p+128;
  rows.slice(0,5).forEach(r=>{ctx.textAlign="left";ctx.fillStyle="rgba(255,255,255,0.5)";ctx.font="12px "+ff;ctx.fillText(r[0],64,y);
    ctx.textAlign="right";ctx.fillStyle="#fff";ctx.font="16px "+ff;ctx.fillText(r[1],W-64,y);
    ctx.fillStyle="rgba(255,255,255,0.08)";ctx.fillRect(64,y+14,W-128,1);y+=42;});
  ctx.textAlign="center";ctx.fillStyle="rgba(255,100,100,0.85)";ctx.font="13px "+ff;ctx.fillText("this world is gone",W/2,H-62);
  ctx.fillStyle="rgba(255,255,255,0.3)";ctx.font="9px "+ff;ctx.fillText("resets every 3 hours",W/2,H-34);
  return cv.toDataURL("image/png");
}
function recapSnap(m){
  const stats={mice:RECAP.mice,hops:RECAP.hops,words:RECAP.words,hits:RECAP.hits,purr:RECAP.purr,peak:RECAP.peak};
  const d={name:m.name,pal:{...m.pal,_name:""},flip:!!m.flip,world:WORLD_ID,stats,lived:Date.now()-(RECAP.t0||Date.now())};
  try{d.img=renderRecap(d);}catch(e){d.img=null;}
  try{localStorage.removeItem("fikfuk_r");}catch(e){}
  return d.img?d:null;
}
function recapDownload(r){const a=document.createElement("a");a.href=r.img;a.download="fikfuk-"+(r.name||"cat").replace(/[^a-z0-9]+/gi,"_")+".png";document.body.appendChild(a);a.click();a.remove();}
async function recapShare(r){try{const b=await (await fetch(r.img)).blob();const f=new File([b],"fikfuk.png",{type:"image/png"});
  if(navigator.canShare&&navigator.canShare({files:[f]})){await navigator.share({files:[f],title:"fikfuk.wtf",text:"my cat's life in fikfuk.wtf"});return;}}catch(e){if(e&&e.name==="AbortError")return;}
  recapDownload(r);}
let uid=100;'''

UI = r'''{recap&&(
              <div style={{display:"flex",gap:14,alignItems:"center"}}>
                <img src={recap.img} alt="" onClick={()=>recapDownload(recap)} style={{width:48,height:85,objectFit:"cover",border:"1px solid rgba(255,50,50,0.35)",cursor:"pointer",imageRendering:"pixelated"}}/>
                <div style={{display:"flex",flexDirection:"column",gap:10}}>
                  <div style={{fontSize:7,color:"rgba(255,255,255,0.45)",lineHeight:1.8}}>the last world is gone</div>
                  <div style={{display:"flex",gap:14}}>
                    <button onClick={()=>recapDownload(recap)} style={{background:"transparent",border:"none",color:"#ff6666",fontFamily:ff,fontSize:7,cursor:"pointer",padding:0}}>save</button>
                    {typeof navigator!=="undefined"&&navigator.share&&<button onClick={()=>recapShare(recap)} style={{background:"transparent",border:"none",color:"#ff6666",fontFamily:ff,fontSize:7,cursor:"pointer",padding:0}}>share</button>}
                  </div>
                </div>
              </div>
            )}'''

src = swap(src, "let uid=100;", MOD, "recap module")
src = swap(src, 'const [worldName,setWorldName]=useState("Malkuth Gate");',
    'const [worldName,setWorldName]=useState("Malkuth Gate");const [recap,setRecap]=useState(null);', "recap state")
src = swap(src, "gs.current._spawnEpoch=getEpoch();saveSession({name,palId,confessions:myCat.confessions,x:ox,y:oy});",
    "gs.current._spawnEpoch=getEpoch();saveSession({name,palId,confessions:myCat.confessions,x:ox,y:oy});recapStart();setRecap(null);", "start counting")
src = swap(src, 'localStorage.removeItem("fikfuk_s");try{ablyRef.current.close();}catch(e){}_g.cats=[];',
    'localStorage.removeItem("fikfuk_s");{const _m=_g.cats.find(c=>c.id===_g.myId);if(_m)setRecap(recapSnap(_m));}try{ablyRef.current.close();}catch(e){}_g.cats=[];', "snapshot at wipe")
src = swap(src, "myCat._boostTimer=300;FKAudio.squeak();", "myCat._boostTimer=300;FKAudio.squeak();RECAP.mice++;", "count mice")
src = swap(src, "joinWorld(dest);FKAudio.portal();", "joinWorld(dest);FKAudio.portal();RECAP.hops++;RECAP.w[dest]=1;", "count portals")
src = swap(src, "addToWall(wallEntry.text);FKAudio.confess();", "addToWall(wallEntry.text);FKAudio.confess();RECAP.words++;", "count whispers")
src = swap(src, 'FKAudio.hit(obj.hp);channelRef.current?.publish("dia_hit"', 'FKAudio.hit(obj.hp);RECAP.hits++;channelRef.current?.publish("dia_hit"', "count boss hits")
src = swap(src, "if(!window.__fikfukPurr)window.__fikfukPurr=",
    "if(s.frame%20===0&&s.myId){const _m=s.cats.find(c=>c.id===s.myId);if(_m&&_m._purr)RECAP.purr+=20/60;RECAP.peak=Math.max(RECAP.peak,s.cats.filter(c=>!c.isSys&&!c.isGhost).length);}"
    "if(s.frame%600===0&&s.myId)recapSave();if(!window.__fikfukPurr)window.__fikfukPurr=", "purr and crowd")
src = swap(src, 'maxWidth:360,width:"100%",display:"flex",flexDirection:"column",gap:22}}>', 'maxWidth:360,width:"100%",display:"flex",flexDirection:"column",gap:22}}>' + UI, "recap UI")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 10 edits applied.")
