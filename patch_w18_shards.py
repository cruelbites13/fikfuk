# patch_w18_shards.py - Glass Garden gets its own mechanic: glass shards that refract chirps.
# Glass Garden (yesod) now has 7 tall violet glass shards scattered through it (new spots every 3-hour cycle).
# When anybody chirps near a shard, it catches the chirp and bends it: after a short beat, two other shards light up and
# repeat the chirp from where THEY stand, with a prism flash of colour between them. Cats sitting next to those far shards
# get their whispers revealed, so a whisper can travel across the garden. Everything is worked out on each player's device
# (same positions for everyone, no new messages). Other worlds are untouched; the shards also show as pale dots on the minimap.
# Needs the world patches (w2) and patch_w17_beacon.py (for the draw spot). All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_shard*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_beacon*/" not in src:
    print("ABORT: apply patch_w17_beacon.py first. Nothing written."); sys.exit(1)

MOD = r'''/*_shard*/
let _shE=-1,_shL=[];const SHLINKS=[];
function shardList(){
  if(WORLD_ID!=="yesod")return[];
  const e=getEpoch();
  if(_shE!==e){_shE=e;_shL=[];const r=mulberry32(hashStr(e+"|shards"));const pt=PORTALS.yesod||{};
    for(let i=0;i<300&&_shL.length<7;i++){const x=1200+r()*7600,y=1200+r()*7600;let ok=true;
      for(const k in pt)if(Math.hypot(x-pt[k][0],y-pt[k][1])<500)ok=false;
      _shL.forEach(o=>{if(Math.hypot(x-o.x,y-o.y)<1000)ok=false;});
      if(ok)_shL.push({x,y,h:70+Math.floor(r()*40),flash:0});}}
  return _shL;
}
function shardRelay(x,y,fromId,fire){
  const L=shardList(),cx=x+16.5,cy=y+15;let a=null,ad=1e9;
  L.forEach(o=>{const d=Math.hypot(o.x-cx,o.y-cy);if(d<330&&d<ad){a=o;ad=d;}});
  if(!a)return;a.flash=40;
  L.filter(o=>o!==a).map(o=>({o,d:Math.hypot(o.x-a.x,o.y-a.y)})).filter(t=>t.d<2600).sort((p,q)=>p.d-q.d).slice(0,2).forEach(t=>{
    SHLINKS.push({a,b:t.o,life:50});
    setTimeout(()=>{if(WORLD_ID!=="yesod")return;t.o.flash=40;fire(t.o.x-16.5,t.o.y-15,fromId,true);},350+t.d*0.35);});
}
function drawShards(ctx,cam,W,H,f){
  const L=shardList();if(!L.length)return;
  for(let i=SHLINKS.length-1;i>=0;i--){if(--SHLINKS[i].life<=0)SHLINKS.splice(i,1);}
  ctx.save();ctx.globalCompositeOperation="lighter";
  SHLINKS.forEach(l=>{const al=l.life/50*0.55,ax=l.a.x-cam.x,ay=l.a.y-l.a.h*0.6-cam.y,bx=l.b.x-cam.x,by=l.b.y-l.b.h*0.6-cam.y;
    [["255,120,200",-3],["120,230,255",0],["255,230,140",3]].forEach(([c,o])=>{ctx.strokeStyle=`rgba(${c},${al})`;ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(ax,ay+o);ctx.lineTo(bx,by+o);ctx.stroke();});});
  ctx.restore();
  const poly=(pts,col)=>{ctx.fillStyle=col;ctx.beginPath();ctx.moveTo(pts[0][0],pts[0][1]);for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]);ctx.closePath();ctx.fill();};
  L.forEach(o=>{
    const sx=Math.round(o.x-cam.x),sy=Math.round(o.y-cam.y);if(sx<-140||sx>W+140||sy<-20||sy-o.h>H)return;
    const fl=o.flash/40;if(o.flash>0)o.flash--;
    ctx.fillStyle="rgba(0,0,0,0.4)";ctx.beginPath();ctx.ellipse(sx+4,sy+4,26,8,0,0,Math.PI*2);ctx.fill();
    const one=(ox,oy,h,k)=>{const x=sx+ox,y=sy+oy;
      poly([[x-12*k,y],[x-1*k,y],[x+1*k,y-h],[x-9*k,y-h*0.7]],"#b9aef0");
      poly([[x-1*k,y],[x+12*k,y],[x+8*k,y-h*0.75],[x+1*k,y-h]],"#7566c0");
      ctx.fillStyle="rgba(240,235,255,0.9)";ctx.fillRect(Math.round(x-9*k),Math.round(y-h*0.7),2,Math.round(h*0.7));};
    one(20,3,o.h*0.55,0.8);one(0,0,o.h,1);
    ctx.save();ctx.globalCompositeOperation="lighter";
    const gy=sy-o.h*0.5,rad=60+50*fl,gr=ctx.createRadialGradient(sx,gy,4,sx,gy,rad);gr.addColorStop(0,`rgba(190,170,255,${0.10+0.40*fl+0.04*Math.sin(f*0.05+o.x)})`);gr.addColorStop(1,"rgba(190,170,255,0)");
    ctx.fillStyle=gr;ctx.fillRect(sx-rad,gy-rad,rad*2,rad*2);
    if(fl>0){[["255,120,200",-0.5],["120,230,255",-0.25],["255,230,140",0]].forEach(([c,a])=>{ctx.strokeStyle=`rgba(${c},${fl*0.7})`;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(sx+1,sy-o.h);ctx.lineTo(sx+1+Math.cos(a-0.3)*70*fl,sy-o.h+Math.sin(a-0.3)*70*fl);ctx.stroke();});}
    ctx.fillStyle="rgba(255,255,255,0.8)";const sp=(f+o.x)%90;if(sp<6)ctx.fillRect(sx-4+Math.round((o.x*7)%9),sy-o.h*0.8+sp,2,2);
    ctx.restore();});
}
let uid=100;'''

src = swap(src, "let uid=100;", MOD, "shard module")
src = swap(src, "function applyChirp(x,y,fromId){",
    'function applyChirp(x,y,fromId,_r){if(!_r&&WORLD_ID==="yesod")shardRelay(x,y,fromId,applyChirp);', "relay hook")
src = swap(src, "{const _b=beaconGet(WORLD_ID),_bx=_b.x-cam.x,",
    "drawShards(ctx,cam,W,H,s.frame);{const _b=beaconGet(WORLD_ID),_bx=_b.x-cam.x,", "draw shards")
src = swap(src, '{const _b=beaconGet(WORLD_ID);ctx.fillStyle=_b.lit?',
    '{ctx.fillStyle="rgba(200,185,255,0.9)";shardList().forEach(o=>ctx.fillRect(MM_X+(o.x/WORLD_W)*MM_W-1.5,MM_Y+(o.y/WORLD_H)*MM_H-1.5,3,3));}{const _b=beaconGet(WORLD_ID);ctx.fillStyle=_b.lit?', "minimap shards")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 4 edits applied.")
