# patch_w5_sky.py - new 2.5D sky for every world: a glowing horizon, drifting nebula clouds, a lit moon/planet per world
# (ringed moon, glass planet, moss moon), three layers of pixel stars that move at different speeds,
# floating sparks and an occasional shooting star. Keeps the day/night colour cycle and everything drawn on top
# of the sky (reset flash, red countdown, scanlines). Needs patch_w2_content first. Safe to run twice.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
if "var drawSky=" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "const WORLDS=" not in src:
    print("ABORT: apply patch_w2_content.py first. Nothing written."); sys.exit(1)
def once(text, s, label):
    if text.count(s) != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {text.count(s)}. Nothing written."); sys.exit(1)
FUNC = r"""var drawSky=(function(){
  var TH={
    malkuth:{hor:[70,60,140],neb:[[110,90,220],[60,80,200]],star:[215,215,255],moon:["#2c2850","#6a62b8","#b9b1f0","#f1eeff"],ring:true,glow:[150,140,255]},
    yesod:  {hor:[185,150,235],neb:[[230,150,255],[130,190,255]],star:[255,240,255],moon:["#4a2f6e","#9a74d0","#d9b8ff","#fff0ff"],ring:false,glow:[225,175,255]},
    netzach:{hor:[40,110,70],neb:[[70,200,110],[200,190,80]],star:[225,255,215],moon:["#10281a","#2f6a3c","#79b25a","#ecf0a0"],ring:false,glow:[130,225,130]}
  };
  function hs(n){n=Math.imul(n^61,2654435761);n^=n>>>15;n=Math.imul(n,2246822519);n^=n>>>13;return(n>>>0)/4294967296;}
  function rg(c,a){return"rgba("+(c[0]|0)+","+(c[1]|0)+","+(c[2]|0)+","+a.toFixed(3)+")";}
  var SW=1024,SH=768,L=[{n:70,v:0.08,r:3,a:0.5},{n:42,v:0.2,r:3,a:0.7},{n:22,v:0.42,r:6,a:0.95}];
  var tiles={},TW=1024,TH2=640;
  return function drawSky(ctx,W,H,cam,t,world,skyCol,night){
    var T=TH[world]||TH.malkuth,i,j,k,m=/(\d+),(\d+),(\d+)/.exec(skyCol)||[0,8,8,16],zc=[+m[1],+m[2],+m[3]];
    ctx.save();
    // 1. base: day-cycle colour at the top, world horizon glow rising from the bottom (stepped bands)
    ctx.fillStyle=skyCol;ctx.fillRect(0,0,W,H);
    var bands=14;
    for(i=0;i<bands;i++){var y0=Math.round(H*(0.25+0.75*(i/bands)));ctx.fillStyle=rg(T.hor,(night?0.034:0.045));ctx.fillRect(0,y0,W,H-y0);}
    // 2. nebula clouds, painted once per world into a seamless tile, then scrolled with parallax
    var nt=tiles[world];
    if(!nt){nt=tiles[world]=document.createElement("canvas");nt.width=TW;nt.height=TH2;var g=nt.getContext("2d");g.globalCompositeOperation="lighter";
      for(i=0;i<6;i++){var bx=hs(i*13+1)*TW,by=hs(i*17+5)*TH2,c=T.neb[i%2],rr=hs(i+9)*0.8-0.4;
        for(var ox=-1;ox<=1;ox++)for(var oy=-1;oy<=1;oy++)for(j=0;j<4;j++){g.fillStyle=rg(c,0.016+0.013*j);g.beginPath();
          g.ellipse(bx+ox*TW,by+oy*TH2,300-j*60+hs(i)*80,120-j*24,rr,0,6.2832);g.fill();}}}
    var ox0=-(((cam.x*0.12+t*0.05)%TW)+TW)%TW,oy0=-((cam.y*0.12%TH2)+TH2)%TH2;
    for(i=0;ox0+i*TW<W;i++)for(j=0;oy0+j*TH2<H;j++)ctx.drawImage(nt,Math.round(ox0+i*TW),Math.round(oy0+j*TH2));
    // 3. world body (moon / glass planet / moss moon) with top-left light, parallax 0.03
    var mx=Math.round(W*0.78-cam.x*0.03),my=Math.round(H*0.2-cam.y*0.03),R=58;
    for(i=3;i>=1;i--){ctx.fillStyle=rg(T.glow,0.035*(5-i));ctx.beginPath();ctx.arc(mx,my,R+i*16,0,6.2832);ctx.fill();}
    if(T.ring){ctx.lineWidth=7;ctx.strokeStyle="rgba(150,140,220,0.55)";ctx.beginPath();ctx.ellipse(mx,my+4,R+34,15,-0.35,Math.PI,6.2832);ctx.stroke();}
    var tone=T.moon;
    ctx.fillStyle=tone[0];ctx.beginPath();ctx.arc(mx,my,R,0,6.2832);ctx.fill();
    ctx.fillStyle=tone[1];ctx.beginPath();ctx.arc(mx-7,my-7,R-8,0,6.2832);ctx.fill();
    ctx.fillStyle=tone[2];ctx.beginPath();ctx.arc(mx-15,my-15,R-24,0,6.2832);ctx.fill();
    ctx.fillStyle=tone[3];ctx.beginPath();ctx.arc(mx-22,my-22,R-40,0,6.2832);ctx.fill();
    ctx.fillStyle="rgba(0,0,20,0.22)";
    for(i=0;i<4;i++){ctx.beginPath();ctx.arc(mx+(hs(i+30)-0.4)*R*1.1,my+(hs(i+40)-0.3)*R*1.1,4+hs(i+50)*8,0,6.2832);ctx.fill();}
    if(T.ring){ctx.lineWidth=7;ctx.strokeStyle="rgba(190,180,250,0.7)";ctx.beginPath();ctx.ellipse(mx,my+4,R+34,15,-0.35,0,Math.PI);ctx.stroke();}
    // 4. three parallax star layers, pixel squares, grouped twinkle
    for(k=0;k<3;k++){
      var lay=L[k];
      for(i=0;i<lay.n;i++){
        var sx=((hs(k*500+i*3)*SW-cam.x*lay.v)%SW+SW)%SW*(W/SW+0.0)+0,sy=((hs(k*500+i*3+1)*SH-cam.y*lay.v)%SH+SH)%SH*(H/SH);
        var tw=0.55+0.45*Math.sin(t*(0.015+hs(k*500+i*3+2)*0.04)+i),al=lay.a*tw*(night?1:0.85);
        ctx.fillStyle=rg(T.star,al);
        var s=(i%7===0&&k===2)?6:lay.r-(k===0?1:0);
        ctx.fillRect(Math.round(sx/3)*3,Math.round(sy/3)*3,s,s);
        if(k===2&&i%5===0){ctx.fillStyle=rg(T.star,al*0.4);ctx.fillRect(Math.round(sx/3)*3-3,Math.round(sy/3)*3,9,3);}
      }
    }
    // 5. world motes: sparks drifting upward (yesod glass dust / netzach spores / malkuth embers)
    ctx.globalCompositeOperation="lighter";
    for(i=0;i<22;i++){
      var life=((t*(0.2+hs(i)*0.35)+hs(i*9)*600)%600)/600,
          px=((hs(i*5+2)*W+Math.sin(t*0.01+i*2)*16-cam.x*0.55)%W+W)%W,
          py=H-life*(H+40)+20-((cam.y*0.55)%H);
      py=((py%H)+H)%H;
      ctx.fillStyle=rg(world==="netzach"?[200,255,140]:world==="yesod"?[255,220,255]:[190,180,255],0.7*Math.sin(life*Math.PI));
      ctx.fillRect(Math.round(px/3)*3,Math.round(py/3)*3,3,3);
    }
    // 6. rare shooting star (every ~9s, seeded by the cycle number)
    var per=540,ph=t%per,cyc=(t/per)|0;
    if(ph<28){var p=ph/28,x0=hs(cyc*3+1)*W*0.7+W*0.25,y0=hs(cyc*3+2)*H*0.35;
      for(i=0;i<9;i++){ctx.fillStyle=rg([255,255,255],(1-p)*(1-i/9)*0.9);var q=p*220-i*7;ctx.fillRect(Math.round((x0-q)/3)*3,Math.round((y0+q*0.45)/3)*3,3,3);}}
    ctx.restore();
  };
})();
"""
# 1. sky fill (+ the old per-world tint) -> drawSky
s1 = "ctx.fillStyle=skyCol;ctx.fillRect(0,0,W,H);"; once(src, s1, "sky fill")
e1 = "ctx.fillStyle=_g;ctx.fillRect(0,0,W,H);ctx.restore();}}"; once(src, e1, "world tint end")
i = src.index(s1); j = src.index(e1) + len(e1)
src = src[:i] + "drawSky(ctx,W,H,cam,s.frame,WORLD_ID,skyCol,isNight());" + src[j:]
# 2. old star loop (now drawn inside drawSky)
s2 = "s.stars.forEach(st=>{"; once(src, s2, "star loop start")
i = src.index(s2); e2 = "ctx.fill();\n"
k = src.index("});", i) + 3
body = src[i:k]
if "st.speed" not in body or body.count("\n") > 8:
    print("ABORT star loop shape unexpected. Nothing written."); sys.exit(1)
src = src[:i] + src[k:]
# 3. the function itself
a = "var drawPortal=(function"
if src.count(a) == 1: src = src.replace(a, FUNC + "\n" + a)
else:
    b = "const WORLD_CAP=50;"; once(src, b, "function anchor"); src = src.replace(b, FUNC + "\n" + b)
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 3 edits applied (new sky, old stars removed, sky function added).")
