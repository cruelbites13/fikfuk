# patch_w35_patates_grave.py - a memorial for Patates.
# Patates now rests by his own grave in the Malkuth Gate, right by the spawn point: a stone with his name and a paw,
# a little fence, candles, a fish offering, flowers and (at night) fireflies, all on a warm glow. Patates the NPC stays
# close to it (he wanders around the grave, and walks back if he drifts away) and now carries a soft golden halo, a
# little star above his head and tiny orbiting lights. Every time anyone brings him a mouse (the existing feeding), a new
# flower is planted at the grave, so it fills with flowers over each 3-hour cycle. Walking up to the grave plants one
# for you too, floats "rest easy, patates", and your recap card shows "paid respects: patates". No new network messages.
# Needs patch_w33_chokhmah.py first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_grave*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_choch*/" not in src:
    print("ABORT: apply patch_w33_chokhmah.py first. Nothing written."); sys.exit(1)

MOD = r'''/*_grave*/
const GRAVE={x:5000,y:4770};let _gFl=0,_gE=-1,_gPaid=false,_gPat=null;
function graveFlowers(){const e=getEpoch();if(_gE!==e){_gE=e;_gFl=0;_gPaid=false;}return _gFl;}
function graveFlower(){graveFlowers();_gFl=Math.min(36,_gFl+1);}
function graveTick(s){
  if(WORLD_ID!=="malkuth")return;graveFlowers();
  const me=s.cats.find(c=>c.id===s.myId);if(!me||me.idle||_gPaid)return;
  if(Math.hypot(me.x+16-GRAVE.x,(me.y+30-GRAVE.y)*2)<140){_gPaid=true;graveFlower();RECAP.paid=1;try{FKAudio.feed(true);}catch(e){}
    s.particles.push({text:"rest easy, patates",x:GRAVE.x-70,y:GRAVE.y-110,vx:0,vy:-0.25,alpha:1,life:280,delay:0});
    for(let i=0;i<5;i++)s.particles.push({text:"<3",x:GRAVE.x-24+i*12,y:GRAVE.y-70,vx:(Math.random()-0.5)*0.5,vy:-0.5-Math.random()*0.4,alpha:1,life:150+i*10,delay:i*7});}
}
function patLeash(s){
  if(WORLD_ID!=="malkuth"){_gPat=null;return;}
  const c=s.cats.find(k=>k.sysType==="patates");_gPat=c||null;if(!c)return;
  const dx=GRAVE.x+10-c.x,dy=GRAVE.y+70-c.y;
  if(Math.hypot(dx,dy*2)>210){c.wanderAngle=Math.atan2(dy,dx);c.state="run";c.wanderTimer=Math.max(c.wanderTimer||0,15);{const _a=0.04+Math.min(0.2,(Math.hypot(dx,dy*2)-210)/1500);c.vx+=Math.cos(c.wanderAngle)*_a;c.vy+=Math.sin(c.wanderAngle)*_a;}c.flip=c.vx<0;}
}
function drawGrave(ctx,cam,W,H,f){
  if(WORLD_ID!=="malkuth")return;
  const sx=Math.round(GRAVE.x-cam.x),sy=Math.round(GRAVE.y-cam.y);
  if(sx<-260||sx>W+260||sy<-170||sy>H+130)return;
  const night=isNight(),pu=0.5+0.5*Math.sin(f*0.04),nF=4+graveFlowers();
  ctx.save();
  // warm ground glow
  ctx.globalCompositeOperation="lighter";
  for(let k=0;k<4;k++){ctx.fillStyle="rgba(255,170,80,"+((night?0.075:0.04)*(4-k)/4+0.01*pu).toFixed(3)+")";ctx.beginPath();ctx.ellipse(sx,sy+16,170-k*28,76-k*12,0,0,6.2832);ctx.fill();}
  ctx.globalCompositeOperation="source-over";
  // mound
  ctx.fillStyle="#16301f";ctx.beginPath();ctx.ellipse(sx,sy+14,98,31,0,0,6.2832);ctx.fill();
  ctx.fillStyle="#1f4a2c";ctx.beginPath();ctx.ellipse(sx,sy+10,86,24,0,0,6.2832);ctx.fill();
  ctx.fillStyle="#2b6a3c";for(let i=0;i<14;i++){const a=i*0.9,gx=sx+Math.cos(a)*(30+(i*13)%52),gy=sy+10+Math.sin(a)*(8+(i*7)%14);ctx.fillRect(Math.round(gx/3)*3,Math.round(gy/3)*3,3,6);}
  // fence (rails then posts)
  ctx.strokeStyle="#9c7a48";ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(sx,sy+8,124,46,0,0.3,Math.PI-0.3);ctx.stroke();
  for(let i=0;i<9;i++){const a=0.3+i*(Math.PI-0.6)/8,px=Math.round(sx+Math.cos(a)*124),py=Math.round(sy+8+Math.sin(a)*46);
    ctx.fillStyle="#6b4f2c";ctx.fillRect(px-2,py-16,6,18);ctx.fillStyle="#c9a36a";ctx.fillRect(px-3,py-17,6,17);ctx.fillStyle="#e7c88e";ctx.fillRect(px-3,py-20,6,4);}
  // tombstone
  ctx.fillStyle="rgba(0,0,0,0.35)";ctx.beginPath();ctx.ellipse(sx+6,sy+2,44,10,0,0,6.2832);ctx.fill();
  ctx.fillStyle="#4e5361";ctx.fillRect(sx-33,sy-8,66,10);ctx.fillStyle="#6c7180";ctx.fillRect(sx-33,sy-8,66,3);
  ctx.fillStyle="#7f8594";ctx.fillRect(sx-27,sy-70,54,62);ctx.fillRect(sx-21,sy-76,42,6);ctx.fillRect(sx-15,sy-82,30,6);
  ctx.fillStyle="#9aa0ad";ctx.fillRect(sx-27,sy-70,12,62);ctx.fillRect(sx-21,sy-76,8,6);ctx.fillRect(sx-15,sy-82,8,6);
  ctx.fillStyle="#5d6270";ctx.fillRect(sx+15,sy-70,12,62);ctx.fillRect(sx+13,sy-76,8,6);
  ctx.fillStyle="#4d7a4a";ctx.fillRect(sx-27,sy-14,9,6);ctx.fillRect(sx-27,sy-20,3,6);ctx.fillRect(sx+21,sy-12,6,4);
  ctx.fillStyle="#262935";ctx.textAlign="center";ctx.textBaseline="middle";ctx.font="6px 'Press Start 2P',monospace";
  ctx.fillText("PATATES",sx,sy-58);ctx.fillText("good boy",sx,sy-45);
  ctx.fillRect(sx-5,sy-24,10,7);ctx.fillRect(sx-11,sy-31,4,4);ctx.fillRect(sx-5,sy-35,4,4);ctx.fillRect(sx+2,sy-35,4,4);ctx.fillRect(sx+8,sy-31,4,4);
  ctx.textAlign="left";ctx.textBaseline="alphabetic";
  // offerings: fish
  ctx.fillStyle="#ff9a4a";ctx.fillRect(sx+30,sy+14,15,6);ctx.fillStyle="#ffc58a";ctx.fillRect(sx+33,sy+14,9,2);ctx.fillStyle="#e07b39";ctx.fillRect(sx+27,sy+11,3,12);ctx.fillStyle="#262935";ctx.fillRect(sx+40,sy+16,2,2);
  // flowers
  const cols=["#ff9ec8","#ffd966","#ffffff","#ff7a5c","#b9a0ff"];
  for(let i=0;i<nF;i++){const h=((Math.imul(i+7,2654435761)>>>0)%1000)/1000,h2=((Math.imul(i+31,40503)>>>0)%1000)/1000,a=0.12+h*(Math.PI-0.24),
    fx=Math.round((sx+Math.cos(a)*(44+h2*66))/3)*3,fy=Math.round((sy+14+Math.sin(a)*(10+h2*30))/3)*3;
    ctx.fillStyle="#3f9a4f";ctx.fillRect(fx,fy,3,6);ctx.fillStyle=cols[i%5];ctx.fillRect(fx-3,fy-3,3,3);ctx.fillRect(fx+3,fy-3,3,3);ctx.fillRect(fx,fy-6,3,3);ctx.fillStyle="#fff2a8";ctx.fillRect(fx,fy-3,3,3);}
  // candles
  [-52,52].forEach((dx,i)=>{const cx=sx+dx,cy=sy+4;ctx.fillStyle="#f3ead2";ctx.fillRect(cx-3,cy-12,6,14);ctx.fillStyle="#cbbf9c";ctx.fillRect(cx+1,cy-12,2,14);
    const fl=0.75+0.25*Math.sin(f*0.23+i*3);ctx.globalCompositeOperation="lighter";ctx.fillStyle="rgba(255,190,90,"+(0.16*fl).toFixed(3)+")";ctx.beginPath();ctx.ellipse(cx,cy-18,26,16,0,0,6.2832);ctx.fill();
    ctx.fillStyle="rgba(255,210,120,"+(0.9*fl).toFixed(3)+")";ctx.fillRect(cx-2,cy-21,4,8);ctx.fillStyle="rgba(255,250,220,"+fl.toFixed(3)+")";ctx.fillRect(cx-1,cy-18,2,5);ctx.globalCompositeOperation="source-over";});
  // fireflies at night
  if(night){ctx.globalCompositeOperation="lighter";for(let k=0;k<7;k++){const a=f*0.008+k*0.9,tw=0.4+0.6*Math.abs(Math.sin(f*0.05+k*2));ctx.fillStyle="rgba(255,235,140,"+tw.toFixed(3)+")";ctx.fillRect(Math.round((sx+Math.cos(a*1.3+k)*(90+k*8))/3)*3,Math.round((sy-26+Math.sin(a+k)*(34+k*3))/3)*3,3,3);}}
  // Patates' halo, star and orbiting lights
  const c=_gPat;
  if(c){const hx=Math.round(c.x+5.5*3-cam.x),hy=Math.round(c.y+5*3-cam.y);
    ctx.globalCompositeOperation="lighter";
    for(let k=0;k<3;k++){ctx.fillStyle="rgba(255,200,110,"+((0.07+0.025*pu)*(3-k)/3).toFixed(3)+")";ctx.beginPath();ctx.ellipse(hx,hy+4,56-k*14,40-k*10,0,0,6.2832);ctx.fill();}
    const by=hy-44+Math.sin(f*0.06)*3;ctx.fillStyle="rgba(255,236,160,"+(0.7+0.3*pu).toFixed(3)+")";
    ctx.fillRect(Math.round(hx/3)*3-1,Math.round(by/3)*3-8,3,17);ctx.fillRect(Math.round(hx/3)*3-8,Math.round(by/3)*3-1,17,3);ctx.fillStyle="rgba(255,255,255,0.9)";ctx.fillRect(Math.round(hx/3)*3-1,Math.round(by/3)*3-1,3,3);
    for(let k=0;k<3;k++){const a=f*0.03+k*2.09;ctx.fillStyle="rgba(255,225,150,"+(0.5+0.4*Math.sin(f*0.08+k)).toFixed(3)+")";ctx.fillRect(Math.round((hx+Math.cos(a)*34)/3)*3,Math.round((hy+Math.sin(a)*20-4)/3)*3,3,3);}}
  ctx.restore();
}
let uid=100;'''

CRLF = "\r\n" in src
if CRLF: src = src.replace("\r\n", "\n")
n = 0
def S(old, new, label):
    global src, n
    src = swap(src, old, new, label); n += 1
S("let uid=100;", MOD, "grave module")
S('const pat=makeCat(cx,cy-250,SYS_PAL_PATATES,"patates",false,true,"patates");', 'const pat=makeCat(cx+90,cy-150,SYS_PAL_PATATES,"patates",false,true,"patates");', "patates position")
S('starTick(s,d=>channelRef.current?.publish("star",d));', 'starTick(s,d=>channelRef.current?.publish("star",d));graveTick(s);patLeash(s);', "tick")
S("drawStarLoom(ctx,cam,W,H,s.frame);", "drawGrave(ctx,cam,W,H,s.frame);drawStarLoom(ctx,cam,W,H,s.frame);", "draw")
S("const line=FEED_LINES[Math.floor(Math.random()*FEED_LINES.length)];FKAudio.feed(mine);", "graveFlower();const line=FEED_LINES[Math.floor(Math.random()*FEED_LINES.length)];FKAudio.feed(mine);", "feeding plants a flower")
S("Object.assign(RECAP,{e:ep,t0:Date.now(),consts:0,", "Object.assign(RECAP,{e:ep,t0:Date.now(),paid:0,consts:0,", "recap reset")
S("consts:RECAP.consts||0}", "consts:RECAP.consts||0,paid:RECAP.paid||0}", "recap stat")
S("if(d.stats.consts)rows.push(", 'if(d.stats.paid)rows.push(["paid respects","patates"]);if(d.stats.consts)rows.push(', "recap rows")
if CRLF: src = src.replace("\n", "\r\n")
open(P, "w", encoding="utf-8", newline="").write(src)
print(f"OK: {n} edits applied.")
