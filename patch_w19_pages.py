# patch_w19_pages.py - Root Archive gets its own mechanic: buried pages.
# Root Archive (netzach) hides 8 buried pages in the ground (new spots every 3-hour cycle). Nothing marks them except a
# small mound with a paper corner poking out. Sit still on a mound for about 6 seconds (any cat counts, so friends dig
# faster only in the sense that somebody always keeps it going) and the page comes up and stands there for the rest of the
# cycle, for everyone. Walk next to an opened page and it shows one line from the archive. Found pages appear as small
# dots on the minimap. Lines are fixed archive fragments written into the game, not player text. If you were the digger,
# your recap card gets a "pages dug up" row. One tiny message goes out when a page is opened.
# Needs patch_w18_shards.py first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_pages*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_shard*/" not in src:
    print("ABORT: apply patch_w18_shards.py first. Nothing written."); sys.exit(1)

MOD = r'''/*_pages*/
const PAGE_LINES=["the archive remembers what you forgot","page 14: nobody read page 13","roots grow toward the sound of purring","a cat sat here for three hours","the index is missing, on purpose","if you can read this, stay","dig where the quiet is","every wipe is a footnote","someone loved this world","the oldest cat was never named","read twice, purr once","the last page is blank. write it","this page was buried by a friend","ink dries, whiskers do not","chapter 0: the first nap","the library has no walls"];
let _pgE=-1,_pgL=[];
function pagesList(){
  if(WORLD_ID!=="netzach")return[];
  const e=getEpoch();
  if(_pgE!==e){_pgE=e;_pgL=[];const r=mulberry32(hashStr(e+"|pages"));const pt=PORTALS.netzach||{};
    for(let i=0;i<400&&_pgL.length<8;i++){const x=1200+r()*7600,y=1200+r()*7600;let ok=Math.hypot(x-5000,y-5000)>500;
      for(const k in pt)if(Math.hypot(x-pt[k][0],y-pt[k][1])<500)ok=false;
      _pgL.forEach(o=>{if(Math.hypot(x-o.x,y-o.y)<750)ok=false;});
      if(ok)_pgL.push({x,y,i:_pgL.length,p:0,open:false,line:PAGE_LINES[Math.floor(r()*PAGE_LINES.length)]});}}
  return _pgL;
}
function pageOpen(o,s,pub){
  if(o.open)return;o.open=true;o.p=1;o.t=0;
  try{FKAudio.page();}catch(e){}
  if(pub){const me=s.cats.find(c=>c.id===s.myId);if(me&&Math.hypot(me.x-o.x,(me.y-o.y)*2)<80)RECAP.pages=(RECAP.pages||0)+1;pub({e:getEpoch(),w:"netzach",i:o.i});}
}
function pagesTick(s,pub){
  const L=pagesList();if(!L.length)return;
  const sit=s.cats.filter(c=>!c.isSys&&!c.isGhost&&!c.idle&&c.state==="sit");
  L.forEach(o=>{if(o.open)return;
    const n=sit.filter(c=>Math.hypot(c.x-o.x,(c.y-o.y)*2)<70).length;
    if(n>0)o.p=Math.min(1,o.p+1/360);else o.p=Math.max(0,o.p-1/900);
    if(o.p>=1)pageOpen(o,s,pub);});
}
function drawPages(ctx,cam,W,H,f,s){
  const L=pagesList();if(!L.length)return;
  const me=s.cats.find(c=>c.id===s.myId);
  L.forEach(o=>{
    const sx=Math.round(o.x-cam.x),sy=Math.round(o.y-cam.y);if(sx<-200||sx>W+200||sy<-80||sy>H+120)return;
    const el=(x,y,rx,ry,c)=>{ctx.fillStyle=c;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.fill();};
    if(!o.open){
      el(sx,sy+3,30,10,"rgba(0,0,0,0.35)");el(sx,sy,26,9,"#2a2418");el(sx-3,sy-2,19,6,"#3b3322");el(sx-5,sy-3,10,3,"#4d432d");
      ctx.fillStyle="#d8d2b8";ctx.fillRect(sx+8,sy-9,7,4);ctx.fillStyle="#a9a38a";ctx.fillRect(sx+8,sy-6,7,1);
      if(o.p>0){ctx.strokeStyle="rgba(190,255,170,0.9)";ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(sx,sy,38,19,0,-Math.PI/2,-Math.PI/2+o.p*Math.PI*2);ctx.stroke();
        ctx.fillStyle="#4d432d";for(let i=0;i<4;i++){const a=(f*0.2+i*1.6),h=Math.abs(Math.sin(a))*14;ctx.fillRect(Math.round(sx-14+i*9),Math.round(sy-4-h),3,3);}}
    }else{
      o.t=(o.t||0)+1;const bob=Math.round(Math.sin(f*0.04+o.i)*2),rise=Math.min(1,o.t/40);
      el(sx,sy+3,22,8,"rgba(0,0,0,0.35)");el(sx,sy,18,6,"#3a3d3a");el(sx,sy-2,13,4,"#4c514c");
      const py=sy-8-Math.round(30*rise)+bob;
      ctx.save();ctx.globalCompositeOperation="lighter";const gr=ctx.createRadialGradient(sx,py-10,3,sx,py-10,55);gr.addColorStop(0,"rgba(170,255,170,0.22)");gr.addColorStop(1,"rgba(170,255,170,0)");ctx.fillStyle=gr;ctx.fillRect(sx-55,py-65,110,110);ctx.restore();
      ctx.fillStyle="#e8e2c8";ctx.fillRect(sx-11,py-26,22,30);ctx.fillStyle="#c9c3a8";ctx.fillRect(sx+6,py-26,5,30);ctx.fillStyle="#8e8a74";
      for(let i=0;i<5;i++)ctx.fillRect(sx-8,py-21+i*5,i%2?10:14,2);
      if(me&&Math.hypot(me.x-o.x,(me.y-o.y)*2)<150){
        ctx.save();ctx.font="8px "+ff;ctx.textAlign="center";const tw=ctx.measureText(o.line).width+16;
        ctx.fillStyle="rgba(10,20,12,0.82)";ctx.fillRect(Math.round(sx-tw/2),py-62,Math.round(tw),22);ctx.strokeStyle="rgba(170,255,170,0.5)";ctx.lineWidth=1;ctx.strokeRect(Math.round(sx-tw/2)+0.5,py-62+0.5,Math.round(tw)-1,21);
        ctx.fillStyle="rgba(215,255,200,0.95)";ctx.fillText(o.line,sx,py-47);ctx.restore();}
    }
  });
}
let uid=100;'''

src = swap(src, "let uid=100;", MOD, "pages module")
src = swap(src, 'setTimeout(()=>blip(1047,1047,2.6,0.05,"sine"),540);},',
    'setTimeout(()=>blip(1047,1047,2.6,0.05,"sine"),540);},page(){if(!ctx||muted)return;blip(392,784,0.35,0.06,"triangle");setTimeout(()=>blip(587,1175,0.4,0.05,"sine"),160);},', "page sound")
src = swap(src, 'beaconTick(s,d=>channelRef.current?.publish("beacon",d));',
    'beaconTick(s,d=>channelRef.current?.publish("beacon",d));pagesTick(s,d=>channelRef.current?.publish("dig",d));', "pages tick")
src = swap(src, "drawShards(ctx,cam,W,H,s.frame);{const _b=", "drawShards(ctx,cam,W,H,s.frame);drawPages(ctx,cam,W,H,s.frame,s);{const _b=", "draw pages")
src = swap(src, 'channel.subscribe("beacon",(msg)=>{',
    'channel.subscribe("dig",(msg)=>{if(msg.clientId===clientId.current)return;const d=msg.data||{};if(d.w!=="netzach"||WORLD_ID!=="netzach"||d.e!==getEpoch())return;const o=pagesList()[d.i];if(o&&!o.open)pageOpen(o,gs.current,null);});'
    'channel.subscribe("beacon",(msg)=>{', "listen")
src = swap(src, '{ctx.fillStyle="rgba(200,185,255,0.9)";shardList()',
    '{ctx.fillStyle="rgba(190,255,170,0.9)";pagesList().forEach(o=>{if(o.open)ctx.fillRect(MM_X+(o.x/WORLD_W)*MM_W-1.5,MM_Y+(o.y/WORLD_H)*MM_H-1.5,3,3);});}{ctx.fillStyle="rgba(200,185,255,0.9)";shardList()', "minimap pages")
src = swap(src, "Object.assign(RECAP,{e:ep,t0:Date.now(),lit:0,", "Object.assign(RECAP,{e:ep,t0:Date.now(),pages:0,lit:0,", "recap reset")
src = swap(src, "peak:RECAP.peak,lit:RECAP.lit||0}", "peak:RECAP.peak,lit:RECAP.lit||0,pages:RECAP.pages||0}", "recap stat")
src = swap(src, 'if(d.stats.lit)rows.push(', 'if(d.stats.pages)rows.push(["pages dug up",String(d.stats.pages)]);if(d.stats.lit)rows.push(', "recap row")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 9 edits applied.")
