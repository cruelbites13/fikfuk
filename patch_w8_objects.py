# patch_w8_objects.py - redraw the small world objects in the new style: the UFO (shaded saucer, glass dome with a little
# green passenger, glowing rim lights, stepped tractor beam with a lit pool on the ground), fossils (dirt mound with a
# shaded skull and bones), mice, the human, and wild cats (now the new cat with angry red eyes). Same sizes, same speeds,
# same hit areas, same text bubbles and progress bars. Needs patch_w7_cat_redraw first (wild cats reuse the new cat). Safe to run twice.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
if "/*_objstyle*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "function _cmix(" not in src:
    print("ABORT: apply patch_w7_cat_redraw.py first. Nothing written."); sys.exit(1)
NL = "\r\n" if "\r\n" in src else "\n"
NEW = r"""/*_objstyle*/function drawUFO(ctx,x,y,frame,confession,hitCount){
  ctx.save();ctx.translate(x,y);
  const hov=Math.sin(frame*0.04)*4,pu=0.5+0.5*Math.sin(frame*0.07);
  // soft ground shadow far below (shrinks as it rises)
  ctx.fillStyle="rgba(0,0,0,"+(0.16-hov*0.01)+")";ctx.beginPath();ctx.ellipse(8,64,26-hov,7,0,0,Math.PI*2);ctx.fill();
  // tractor beam: stepped layers fading toward the ground, lit pool on the ground
  ctx.save();ctx.globalCompositeOperation="lighter";
  for(let i=0;i<4;i++){ctx.fillStyle="rgba(100,200,255,"+(0.035+0.012*i*pu)+")";
    ctx.beginPath();ctx.moveTo(-4-i*2,hov+9);ctx.lineTo(-20+i*4,62);ctx.lineTo(20-i*4,62);ctx.lineTo(4+i*2,hov+9);ctx.fill();}
  ctx.fillStyle="rgba(120,220,255,"+(0.10+0.06*pu)+")";ctx.beginPath();ctx.ellipse(0,62,22,6,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="rgba(200,245,255,0.14)";ctx.beginPath();ctx.ellipse(0,62,12,3.2,0,0,Math.PI*2);ctx.fill();
  ctx.restore();
  if(hitCount>0){
    const flashAlpha=Math.max(0,0.4-hitCount*0.01);
    ctx.fillStyle="rgba(255,100,100,"+flashAlpha+")";
    ctx.beginPath();ctx.ellipse(0,hov,32,13,0,0,Math.PI*2);ctx.fill();
  }
  // hull: dark underside, mid body, lit top-left rim
  ctx.fillStyle="#14142e";ctx.beginPath();ctx.ellipse(0,hov+4,24,8,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#26264a";ctx.beginPath();ctx.ellipse(0,hov,29,10,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#3a3a72";ctx.beginPath();ctx.ellipse(-2,hov-1,26,8,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#5656a0";ctx.beginPath();ctx.ellipse(-4,hov-2,20,5.5,0,Math.PI*1.05,Math.PI*1.95);ctx.fill();
  ctx.strokeStyle="rgba(190,190,255,0.7)";ctx.lineWidth=2;ctx.beginPath();ctx.ellipse(-1,hov-1,26,8.5,0,Math.PI*1.1,Math.PI*1.55);ctx.stroke();
  // dome: glass with a little green passenger and a highlight
  ctx.fillStyle="#12122c";ctx.beginPath();ctx.ellipse(0,hov-6,14,11,0,Math.PI,Math.PI*2);ctx.fill();
  ctx.fillStyle="rgba(110,210,255,0.42)";ctx.beginPath();ctx.ellipse(0,hov-6,12,9,0,Math.PI,Math.PI*2);ctx.fill();
  ctx.fillStyle="#7ee07e";ctx.fillRect(-3,hov-12,6,6);ctx.fillStyle="#1a3a1a";ctx.fillRect(-2,hov-10,1.5,2);ctx.fillRect(1,hov-10,1.5,2);
  ctx.fillStyle="rgba(255,255,255,0.55)";ctx.beginPath();ctx.ellipse(-5,hov-11,3,2,-0.6,0,Math.PI*2);ctx.fill();
  // rim lights with glow
  [-18,-9,0,9,18].forEach((lx,i)=>{
    const on=Math.sin(frame*0.1+i*1.2)>0;
    if(on){ctx.fillStyle="rgba(255,255,100,0.22)";ctx.beginPath();ctx.arc(lx,hov+3,6,0,Math.PI*2);ctx.fill();}
    ctx.fillStyle=on?"#ffff66":"#2c2c44";
    ctx.beginPath();ctx.arc(lx,hov+3,2.6,0,Math.PI*2);ctx.fill();
  });
  ctx.restore();
  if(confession){
    ctx.save();
    ctx.font=`7px ${ff}`;
    const tw=ctx.measureText(confession).width;
    const bx=x-tw/2-8,by=y+55,bw=tw+16,bh=22;
    ctx.fillStyle="rgba(10,20,10,0.85)";ctx.strokeStyle="#44ff44";ctx.lineWidth=1;
    rrect(ctx,bx,by,bw,bh,3);ctx.fill();ctx.stroke();
    ctx.fillStyle="#88ff88";ctx.fillText(confession,bx+8,by+15);
    ctx.restore();
  }
}

function drawFossil(ctx,x,y,frame,revealed,sitTimer,confession){
  ctx.save();ctx.translate(x,y);
  const alpha=revealed?0.95:0.38+Math.sin(frame*0.02)*0.1;
  ctx.globalAlpha=alpha;
  // dirt mound: dark base, lit top-left, tiny pebbles
  ctx.fillStyle="#1f150c";ctx.beginPath();ctx.ellipse(3,3,26,13,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#3a2816";ctx.beginPath();ctx.ellipse(0,0,24,12,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#58402a";ctx.beginPath();ctx.ellipse(-3,-2,19,8.5,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#78593a";ctx.beginPath();ctx.ellipse(-8,-4,10,4.5,-0.2,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#2a1c10";[[10,3],[16,-2],[-14,4],[4,6]].forEach(q=>ctx.fillRect(q[0],q[1],3,3));
  if(revealed){
    // bones: femur pair and a small skull, shaded
    ctx.fillStyle="#9c8c6a";ctx.fillRect(-12,-2,24,6);
    ctx.fillStyle="#d8c9a4";ctx.fillRect(-12,-3,24,5);ctx.fillStyle="#f3e8c8";ctx.fillRect(-12,-3,24,2);
    [-13,13].forEach((bx,i)=>{ctx.fillStyle="#d8c9a4";ctx.beginPath();ctx.arc(bx,i?3:-4,5,0,Math.PI*2);ctx.fill();ctx.fillStyle="#f3e8c8";ctx.beginPath();ctx.arc(bx-1.5,(i?3:-4)-1.5,2.5,0,Math.PI*2);ctx.fill();});
    ctx.fillStyle="#cdbd98";ctx.beginPath();ctx.ellipse(0,-6,7,5.5,0,0,Math.PI*2);ctx.fill();
    ctx.fillStyle="#efe3c0";ctx.beginPath();ctx.ellipse(-1.5,-7.5,4.5,3,0,0,Math.PI*2);ctx.fill();
    ctx.fillStyle="#2a1c10";ctx.fillRect(-4,-7,3,3);ctx.fillRect(1,-7,3,3);ctx.fillRect(-1,-3,2,2);
  } else {
    ctx.strokeStyle="rgba(212,196,160,0.55)";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(-6,-4);ctx.lineTo(6,4);ctx.moveTo(6,-4);ctx.lineTo(-6,4);ctx.stroke();
  }
  if(!revealed&&sitTimer>0){
    const pct=Math.min(sitTimer/180,1);
    ctx.globalAlpha=0.8;
    ctx.fillStyle="rgba(0,0,0,0.5)";ctx.fillRect(-20,16,40,5);
    ctx.fillStyle="#f5c842";ctx.fillRect(-20,16,40*pct,5);
    ctx.fillStyle="#fff2a8";ctx.fillRect(-20,16,40*pct,1.5);
    for(let i=0;i<4;i++){ctx.fillStyle="rgba(200,170,120,"+(0.5-i*0.1)+")";ctx.fillRect(-12+((frame*0.6+i*13)%24),-6-((frame*0.5+i*7)%14),3,3);}
  }
  if(revealed&&confession){
    ctx.font=`6px ${ff}`;ctx.fillStyle="#ffddaa";
    ctx.globalAlpha=0.9;
    const tw=ctx.measureText(confession).width;
    ctx.fillStyle="rgba(0,0,0,0.6)";ctx.fillRect(-tw/2-4,16,tw+8,14);
    ctx.fillStyle="#ffddaa";ctx.fillText(confession,-tw/2,27);
  }
  ctx.restore();
}

function drawWildCat(ctx,x,y,frame,pal,flip){
  drawCat(ctx,x,y,P,frame,pal,flip,"run",false,false,false,false);
  ctx.save();ctx.translate(x,y);
  if(flip){ctx.translate(9*P,0);ctx.scale(-1,1);}
  ctx.fillStyle="#ff3b2e";ctx.fillRect(2*P,P,P,P);ctx.fillRect(7*P,P,P,P);
  ctx.fillStyle="#2a0000";ctx.fillRect(2*P,0,3*P,P*0.6);ctx.fillRect(6*P,0,3*P,P*0.6);
  ctx.fillStyle="rgba(255,255,255,0.9)";ctx.fillRect(5*P,4*P,P,P);
  ctx.restore();
}

function drawMouse(ctx,x,y,frame,flip){
  ctx.save();ctx.translate(x,y);
  if(flip){ctx.translate(6*P,0);ctx.scale(-1,1);}
  const bob=Math.sin(frame*0.2)*1,st=Math.sin(frame*0.4)>0?1:0;
  const R=(c,a,b,w,h)=>{ctx.fillStyle=c;ctx.fillRect(a*P,(b+bob)*P,w*P,h*P);};
  ctx.fillStyle="rgba(0,0,0,0.25)";ctx.beginPath();ctx.ellipse(3.5*P,6*P,10,3,0,0,Math.PI*2);ctx.fill();
  R("#d49aa8",-1,4,1,1);R("#d49aa8",-2,3.4,1,1);R("#d49aa8",-3,3,1,1);              // tail
  R("#585868",1,3,5,3);R("#8a8a9c",1,2,5,3);R("#b8b8cc",1,2,3,1);R("#b8b8cc",1,3,1,1);  // body
  R("#8a8a9c",4,2,3,3);R("#b8b8cc",4,2,2,1);R("#585868",5,4,2,1);                          // head
  R("#ffb0b8",4,0.6,2,2);R("#8a8a9c",4,0.6,1,2);R("#ffd0d6",5,1,1,1);                      // ear
  R("#101018",5,3,1,1);R("#ffb0b8",7,3.4,1,1);                                            // eye, nose
  R("#3c3c4c",2,6-st*0,1,1);R("#3c3c4c",4,6,1,1);R("#3c3c4c",st?5:2,6,1,1);                // feet
  ctx.restore();
}

function drawHuman(ctx,x,y,frame){
  ctx.save();ctx.translate(x,y);
  const bob=Math.sin(frame*0.06)*1;
  const R=(c,a,b,w,h)=>{ctx.fillStyle=c;ctx.fillRect(a*P,(b+bob)*P,w*P,h*P);};
  ctx.fillStyle="rgba(0,0,0,0.25)";ctx.beginPath();ctx.ellipse(5*P,13.3*P,14,4.5,0,0,Math.PI*2);ctx.fill();
  R("#1c2836",2,9,2,3);R("#2c3e50",2,9,1,3);R("#1c2836",6,9,2,3);R("#2c3e50",6,9,1,3);   // legs
  R("#101820",2,12,2,1);R("#101820",6,12,2,1);R("#3a4a5a",2,12,1,1);R("#3a4a5a",6,12,1,1); // shoes
  R("#2a78b0",2,4,6,5);R("#4aa0e0",2,4,2,4);R("#1e5a86",7,4,1,5);R("#1e5a86",2,8,6,1);      // hoodie
  R("#f5cba7",1,4,1,4);R("#d9a883",1,4,1,4);R("#2a78b0",1,4,2,3);R("#f5cba7",1,7,1,1);R("#1e5a86",8,4,1,3);R("#f5cba7",8,7,1,1); // arms
  R("#f5cba7",3,0,4,4);R("#fde0c6",3,0,2,2);R("#d9a883",6,1,1,3);R("#d9a883",3,3,4,1);      // head
  R("#e67e22",2,-1,6,2);R("#f39c4a",2,-1,3,1);R("#b05a10",7,0,1,2);R("#e67e22",2,1,1,2);   // hair
  R("#2a1a10",4,2,1,1);R("#2a1a10",6,2,1,1);
  ctx.restore();
}""".replace("\n", NL)
a = "function drawUFO("
b = "function drawDiablo("
if src.count(a) != 1 or src.count(b) != 1:
    print("ABORT: object functions not found exactly once. Nothing written."); sys.exit(1)
i = src.index(a); j = src.index(b)
seg = src[i:j]
for need in ("function drawFossil(", "function drawWildCat(", "function drawMouse(", "function drawHuman("):
    if need not in seg:
        print("ABORT: unexpected layout, missing " + need + ". Nothing written."); sys.exit(1)
src = src[:i] + NEW + NL + NL + src[j:]
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: objects redrawn (UFO, fossil, wild cat, mouse, human).")
