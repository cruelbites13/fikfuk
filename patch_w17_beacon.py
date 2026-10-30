# patch_w17_beacon.py - the first shared world event: the Beacon.
# Every world has one stone beacon somewhere in it (a different spot every 3-hour cycle). It is dark until enough cats
# gather inside its ring and stay there for about 8 seconds: 2 cats when the world is quiet, 3 when 6 or more are online.
# When it lights, a gold beam shoots into the sky for everybody in that world, a soft chord plays, and it stays lit until the
# wipe. It shows as a small dot on the minimap. If you were close when it lit, your recap card says so.
# Uses the existing connection (one tiny message when it lights). Needs patch_w16_recap.py first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_beacon*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_recap*/" not in src:
    print("ABORT: apply patch_w16_recap.py first. Nothing written."); sys.exit(1)

MOD = r'''/*_beacon*/
const BEACONS={};
function beaconGet(w){
  const e=getEpoch();let b=BEACONS[w];
  if(!b||b.e!==e){
    const r=mulberry32(hashStr(e+"|"+w+"|beacon"));let x=5000,y=3000;
    for(let i=0;i<14;i++){x=1500+r()*7000;y=1500+r()*7000;let ok=Math.hypot(x-5000,y-1800)>700&&Math.hypot(x-5000,y-5000)>600;
      const pt=PORTALS[w]||{};for(const k in pt){if(Math.hypot(x-pt[k][0],y-pt[k][1])<650)ok=false;}if(ok)break;}
    b=BEACONS[w]={e,x,y,charge:0,lit:false,n:0,need:2,flash:0,sil:0,gap:25};
  }
  return b;
}
function beaconLight(b,s,pub){
  if(b.lit)return;b.lit=true;b.charge=1;b.flash=50;b.sil=0;b.gap=20+Math.floor(Math.random()*30);
  try{FKAudio.beacon();}catch(e){}
  const me=s.cats.find(c=>c.id===s.myId);if(me&&Math.hypot(me.x-b.x,me.y-b.y)<500)RECAP.lit=(RECAP.lit||0)+1;
  if(pub)pub({e:b.e,w:WORLD_ID});
}
function beaconTick(s,pub){
  const b=beaconGet(WORLD_ID);
  const real=s.cats.filter(c=>!c.isSys&&!c.isGhost&&!c.idle);
  b.need=real.length>=6?3:2;
  b.n=real.filter(c=>Math.hypot(c.x-b.x,(c.y-b.y)*2)<170).length;
  if(b.flash>0)b.flash--;
  if(b.lit){
    if(s.frame%60===0){b.sil++;if(b.sil>=b.gap){b.sil=0;b.gap=25+Math.floor(Math.random()*30);if(pub)pub({e:b.e,w:WORLD_ID});}}
  }else{
    if(b.n>=b.need)b.charge=Math.min(1,b.charge+1/480);else b.charge=Math.max(0,b.charge-1/1200);
    if(b.charge>=1)beaconLight(b,s,pub);
  }
}
function drawBeacon(ctx,sx,sy,b,f){
  const lit=b.lit,k=lit?1:b.charge,pulse=0.5+0.5*Math.sin(f*0.05);
  const el=(x,y,rx,ry,col)=>{ctx.fillStyle=col;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.fill();};
  ctx.save();
  ctx.lineWidth=2;ctx.strokeStyle=lit?"rgba(255,225,140,0.35)":"rgba(160,190,255,0.22)";ctx.setLineDash([6,8]);
  ctx.beginPath();ctx.ellipse(sx,sy,170,85,0,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);
  if(!lit&&b.charge>0){ctx.strokeStyle="rgba(255,215,120,0.9)";ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(sx,sy,170,85,0,-Math.PI/2,-Math.PI/2+b.charge*Math.PI*2);ctx.stroke();}
  ctx.restore();
  el(sx,sy+6,36,13,"rgba(0,0,0,0.4)");el(sx,sy+2,31,10,"#2a2c3c");el(sx,sy-2,24,8,"#3a3d52");el(sx,sy-6,17,6,"#4c5070");
  ctx.fillStyle="#34364a";ctx.fillRect(sx-9,sy-36,18,30);ctx.fillStyle="#474b6c";ctx.fillRect(sx-9,sy-36,6,30);ctx.fillStyle="#232536";ctx.fillRect(sx+4,sy-36,5,30);
  const cy=sy-62+Math.sin(f*0.04)*3,r=Math.round(120+135*k),g=Math.round(150+75*k),bl=Math.round(220-80*k);
  ctx.save();ctx.globalCompositeOperation="lighter";
  const rad=50+70*k,gr=ctx.createRadialGradient(sx,cy,4,sx,cy,rad);gr.addColorStop(0,`rgba(${r},${g},${bl},${0.10+0.28*k+0.08*pulse})`);gr.addColorStop(1,`rgba(${r},${g},${bl},0)`);
  ctx.fillStyle=gr;ctx.fillRect(sx-rad,cy-rad,rad*2,rad*2);
  if(lit){
    const top=Math.min(cy-1600,-200);
    [[50,0.07],[34,0.09],[20,0.13],[9,0.22]].forEach(([hw,al])=>{const y0=cy+26,bg=ctx.createLinearGradient(0,y0,0,top);bg.addColorStop(0,"rgba(255,220,140,0)");bg.addColorStop(Math.min(0.2,50/(y0-top)),`rgba(255,220,140,${al})`);bg.addColorStop(1,"rgba(255,220,140,0)");ctx.fillStyle=bg;ctx.fillRect(sx-hw,top,hw*2,y0-top);});
    ctx.fillStyle="rgba(255,240,190,0.8)";for(let i=0;i<9;i++){const my=cy-((f*0.9+i*83)%700);ctx.fillRect(Math.round(sx+Math.sin(i*7+f*0.02)*22),Math.round(my),3,3);}
    if(b.flash>0){ctx.strokeStyle=`rgba(255,235,170,${b.flash/50*0.6})`;ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(sx,sy,(50-b.flash)*7+20,(50-b.flash)*3.5+10,0,0,Math.PI*2);ctx.stroke();}
  }
  ctx.restore();
  ctx.fillStyle=`rgb(${r},${g},${bl})`;ctx.beginPath();ctx.moveTo(sx,cy-20);ctx.lineTo(sx+12,cy);ctx.lineTo(sx,cy+20);ctx.lineTo(sx-12,cy);ctx.closePath();ctx.fill();
  ctx.fillStyle=`rgb(${Math.min(255,r+70)},${Math.min(255,g+60)},${Math.min(255,bl+50)})`;ctx.beginPath();ctx.moveTo(sx,cy-20);ctx.lineTo(sx,cy+20);ctx.lineTo(sx-12,cy);ctx.closePath();ctx.fill();
  ctx.fillStyle="rgba(255,255,255,0.85)";ctx.beginPath();ctx.moveTo(sx-2,cy-9);ctx.lineTo(sx+2,cy-5);ctx.lineTo(sx-2,cy-1);ctx.closePath();ctx.fill();
  if(!lit&&(b.n>0||b.charge>0)){ctx.font="8px "+ff;ctx.textAlign="center";ctx.fillStyle="rgba(255,255,255,0.7)";ctx.fillText(b.n+"/"+b.need,sx,sy+30);}
}
let uid=100;'''

src = swap(src, "let uid=100;", MOD, "beacon module")
src = swap(src, 'blip(660,1320,0.5,0.06,"sine");},',
    'blip(660,1320,0.5,0.06,"sine");},'
    'beacon(){if(!ctx||muted)return;blip(523,523,2.2,0.07,"sine");setTimeout(()=>blip(659,659,2,0.06,"sine"),180);setTimeout(()=>blip(784,784,2.2,0.06,"sine"),360);setTimeout(()=>blip(1047,1047,2.6,0.05,"sine"),540);},', "beacon sound")
src = swap(src, "if(s.frame%20===0&&s.myId){const _m=",
    'if(s.myId&&s.ready)beaconTick(s,d=>channelRef.current?.publish("beacon",d));if(s.frame%20===0&&s.myId){const _m=', "beacon tick")
src = swap(src, "/*_rings*/{",
    "{const _b=beaconGet(WORLD_ID),_bx=_b.x-cam.x,_by=_b.y-cam.y;if(_bx>-220&&_bx<W+220&&_by>-220&&_by<(_b.lit?H+1700:H+220))drawBeacon(ctx,_bx,_by,_b,s.frame);}/*_rings*/{", "draw beacon")
src = swap(src, 'channel.subscribe("wall",(msg)=>{',
    'channel.subscribe("beacon",(msg)=>{if(msg.clientId===clientId.current)return;const d=msg.data||{};if(d.w!==WORLD_ID)return;const b=beaconGet(WORLD_ID);if(d.e!==b.e)return;if(b.lit){b.sil=0;return;}beaconLight(b,gs.current,null);});'
    'channel.subscribe("wall",(msg)=>{', "listen")
src = swap(src, "// sys cats (policy=purple, about=green)",
    '{const _b=beaconGet(WORLD_ID);ctx.fillStyle=_b.lit?"rgba(255,225,140,1)":"rgba(160,190,255,0.8)";ctx.fillRect(MM_X+(_b.x/WORLD_W)*MM_W-2,MM_Y+(_b.y/WORLD_H)*MM_H-2,4,4);}// sys cats (policy=purple, about=green)', "minimap dot")
src = swap(src, "Object.assign(RECAP,{e:ep,t0:Date.now(),mice:0,", "Object.assign(RECAP,{e:ep,t0:Date.now(),lit:0,mice:0,", "recap reset")
src = swap(src, "purr:RECAP.purr,peak:RECAP.peak}", "purr:RECAP.purr,peak:RECAP.peak,lit:RECAP.lit||0}", "recap stat")
src = swap(src, "if(d.stats.mice)rows.push(", 'if(d.stats.lit)rows.push(["lit the beacon","yes"]);if(d.stats.mice)rows.push(', "recap row")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 10 edits applied.")
