# patch_w9_bosses.py - the two big dramatic objects in the new style.
# Diablo: a hulking demon with flapping leathery wings, lit curved horns, glowing eyes with slit pupils, jagged teeth,
# glowing cracks that burn brighter the more he is hurt, rising embers, a ground shadow and a red glow on the ground.
# Black hole: a dark sphere with a lit purple rim, a tilted glowing accretion disk that passes behind and in front,
# matter spiralling in, and faint rings contracting toward it. Same sizes, pull radius, hit areas, HP bars and labels.
# Needs patch_w8_objects first. Safe to run twice.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
if "/*_bossstyle*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_objstyle*/" not in src:
    print("ABORT: apply patch_w8_objects.py first. Nothing written."); sys.exit(1)
NL = "\r\n" if "\r\n" in src else "\n"
DIABLO = r"""/*_bossstyle*/function drawDiablo(ctx,x,y,frame,hp=10){
  ctx.save();ctx.translate(x,y);
  const pulse=Math.sin(frame*0.08)*0.3,flap=Math.sin(frame*0.05),rage=1-Math.max(0,Math.min(10,hp))/10;
  const R=(c,a,b,w,h)=>{ctx.fillStyle=c;ctx.fillRect(a*P,b*P,w*P,h*P);};
  ctx.fillStyle="rgba(0,0,0,0.32)";ctx.beginPath();ctx.ellipse(2*P,14*P,17*P,4.6*P,0,0,Math.PI*2);ctx.fill();
  ctx.save();ctx.globalCompositeOperation="lighter";
  for(let i=0;i<4;i++){ctx.fillStyle="rgba(200,20,0,"+(0.035+0.012*rage*4)+")";ctx.beginPath();ctx.ellipse(0,13.5*P,(24-i*4)*P,(6.5-i*1)*P,0,0,Math.PI*2);ctx.fill();}
  const g=ctx.createRadialGradient(0,0,0,0,0,50);g.addColorStop(0,"rgba(220,20,0,"+(0.26+rage*0.2)+")");g.addColorStop(1,"rgba(200,0,0,0)");
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(0,0,50,0,Math.PI*2);ctx.fill();ctx.restore();
  ctx.globalAlpha=Math.min(1,0.92+pulse*0.25);
  const wing=(s,fill,bone)=>{
    const wy=(-20+flap*3)*P;
    ctx.fillStyle=fill;ctx.beginPath();ctx.moveTo(s*9*P,-2*P);ctx.lineTo(s*30*P,wy);
    ctx.quadraticCurveTo(s*25*P,wy*0.2,s*27*P,-4*P);ctx.quadraticCurveTo(s*21*P,-1*P,s*21*P,2*P);
    ctx.quadraticCurveTo(s*16*P,3*P,s*14*P,6*P);ctx.quadraticCurveTo(s*11*P,5*P,s*9*P,8*P);ctx.closePath();ctx.fill();
    ctx.strokeStyle=bone;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(s*9*P,-2*P);ctx.lineTo(s*30*P,wy);ctx.stroke();
    ctx.lineWidth=1.5;ctx.strokeStyle="rgba(120,20,20,0.9)";
    [[27,-4],[21,2],[14,6]].forEach(q=>{ctx.beginPath();ctx.moveTo(s*9*P,-2*P);ctx.lineTo(s*q[0]*P,q[1]*P);ctx.stroke();});
  };
  wing(-1,"#4a0a0a","#a03020");wing(1,"#2a0505","#6a1a14");
  R("#0b0000",-10,-5,20,15);R("#230303",-9,-5,17,13);R("#420909",-9,-5,6,11);R("#5a1010",-9,-5,2,6);R("#100000",5,-4,5,13);
  R("#0b0000",-9,8,18,2);
  const cr=0.45+0.35*rage+0.15*Math.sin(frame*0.1);
  ctx.save();ctx.globalCompositeOperation="lighter";
  [[-5,-3,3,1],[-3,-2,1,3],[0,-1,1,5],[1,3,4,1],[-6,3,1,4],[3,-3,1,3],[-2,6,5,1]].forEach(q=>{ctx.fillStyle="rgba(255,"+(70+rage*110|0)+",0,"+cr+")";ctx.fillRect(q[0]*P,q[1]*P,q[2]*P,q[3]*P);});
  ctx.fillStyle="rgba(255,120,0,"+(0.10+0.18*rage)+")";ctx.beginPath();ctx.arc(0,2.5*P,6*P,0,Math.PI*2);ctx.fill();ctx.restore();
  R("#120000",-8,-9,16,10);R("#330606",-8,-9,12,8);R("#561010",-8,-9,6,2);R("#6c1616",-8,-9,2,4);R("#1a0000",4,-8,4,8);
  R("#0a0000",-6,-1,12,2);
  for(let i=0;i<6;i++){ctx.fillStyle="#e8dcc4";ctx.fillRect((-6+i*2)*P,-1*P,P,P);ctx.fillRect((-5+i*2)*P,0,P,P);}
  R("#4a0808",-10,-8,3,3);R("#7a1410",-11,-11,3,4);R("#a02a20",-12,-14,2,4);R("#e07060",-12,-14,1,3);R("#7a1410",-10,-9,1,2);
  R("#2a0404",7,-8,3,3);R("#4a0a08",8,-11,3,4);R("#661a14",10,-14,2,4);R("#8a2a20",10,-14,1,3);
  const ec="rgba(255,"+Math.floor(60+pulse*100+rage*60)+",0,0.95)";
  ctx.save();ctx.globalCompositeOperation="lighter";ctx.fillStyle="rgba(255,60,0,0.18)";
  ctx.beginPath();ctx.arc(-4*P,-4*P,7*P,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(4*P,-4*P,7*P,0,Math.PI*2);ctx.fill();ctx.restore();
  ctx.fillStyle=ec;ctx.beginPath();ctx.arc(-4*P,-4*P,3*P,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(4*P,-4*P,3*P,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#1a0000";ctx.fillRect(-4.4*P,-6*P,0.9*P,4*P);ctx.fillRect(3.6*P,-6*P,0.9*P,4*P);
  ctx.fillStyle="rgba(255,255,255,0.8)";ctx.fillRect(-6*P,-5.5*P,P,P*0.8);ctx.fillRect(2*P,-5.5*P,P,P*0.8);
  ctx.fillStyle="#0a0000";ctx.fillRect(-7*P,-8*P,6*P,1.2*P);ctx.fillRect(1*P,-8*P,6*P,1.2*P);
  [-9,-3,3,7].forEach(cx=>{R("#0b0000",cx,10,2,2);R("#d8c8b0",cx,12,1,1);});
  ctx.save();ctx.globalCompositeOperation="lighter";
  for(let i=0;i<8;i++){const lf=((frame*(0.35+i*0.04)+i*37)%100)/100,ex=(-14+i*4+Math.sin(frame*0.05+i)*3)*P,ey=(10-lf*26)*P;
    ctx.fillStyle="rgba(255,"+(120+i*10)+",30,"+(0.9*Math.sin(lf*Math.PI))+")";ctx.fillRect(ex,ey,3,3);}
  ctx.restore();
  ctx.globalAlpha=0.9;
  ctx.fillStyle="rgba(0,0,0,0.6)";ctx.fillRect(-20*P,18*P,40*P,5);
  ctx.fillStyle="#ff2222";ctx.fillRect(-20*P,18*P,40*P*(hp/10),5);
  ctx.fillStyle="#ff9a8a";ctx.fillRect(-20*P,18*P,40*P*(hp/10),1.5);
  ctx.restore();
}""".replace("\n", NL)
BH = r"""// outer glow
          const grd=ctx.createRadialGradient(sx,sy,0,sx,sy,obj.pullRadius);
          grd.addColorStop(0,"rgba(0,0,0,0)");
          grd.addColorStop(0.7,"rgba(50,0,80,0.08)");
          grd.addColorStop(1,"rgba(100,0,150,0.02)");
          ctx.fillStyle=grd;
          ctx.beginPath();ctx.arc(sx,sy,obj.pullRadius,0,Math.PI*2);ctx.fill();
          const coreR=20+pulse*5;
          for(let i=0;i<4;i++){const lf=((obj.frame*0.004+i*0.25)%1),rr=obj.pullRadius*(1-lf*0.9);
            ctx.strokeStyle="rgba(150,60,255,"+(0.12*Math.sin(lf*Math.PI))+")";ctx.lineWidth=2;ctx.beginPath();ctx.arc(sx,sy,rr,0,Math.PI*2);ctx.stroke();}
          const disk=(a0,a1,bright)=>{ctx.save();ctx.translate(sx,sy);ctx.rotate(-0.28);
            const cols=["255,240,200","255,170,60","230,90,200","140,50,230","80,30,160"];
            for(let j=0;j<5;j++){const rx=coreR*(1.8+j*0.7),ry=rx*0.3;ctx.strokeStyle="rgba("+cols[j]+","+(bright*(0.85-j*0.12))+")";ctx.lineWidth=6-j*0.8;
              ctx.setLineDash([16-j,9]);ctx.lineDashOffset=-obj.frame*(1.8-j*0.25);ctx.beginPath();ctx.ellipse(0,0,rx,ry,0,a0,a1);ctx.stroke();}
            ctx.setLineDash([]);ctx.restore();};
          ctx.save();ctx.globalCompositeOperation="lighter";disk(Math.PI,Math.PI*2,0.55);ctx.restore();
          const cg=ctx.createRadialGradient(sx,sy,coreR*0.8,sx,sy,coreR*1.9);
          cg.addColorStop(0,"rgba(100,20,170,0.7)");cg.addColorStop(1,"rgba(100,0,150,0)");
          ctx.fillStyle=cg;ctx.beginPath();ctx.arc(sx,sy,coreR*1.9,0,Math.PI*2);ctx.fill();
          ctx.fillStyle="#000";ctx.beginPath();ctx.arc(sx,sy,coreR,0,Math.PI*2);ctx.fill();
          ctx.strokeStyle="rgba(190,110,255,"+(0.55+pulse*0.3)+")";ctx.lineWidth=2;ctx.beginPath();ctx.arc(sx,sy,coreR+1,0,Math.PI*2);ctx.stroke();
          ctx.strokeStyle="rgba(255,225,255,0.55)";ctx.lineWidth=2;ctx.beginPath();ctx.arc(sx,sy,coreR+1,Math.PI*1.05,Math.PI*1.55);ctx.stroke();
          ctx.save();ctx.globalCompositeOperation="lighter";disk(0,Math.PI,1);ctx.restore();
          ctx.save();ctx.globalCompositeOperation="lighter";
          for(let i=0;i<16;i++){const lf=((obj.frame*0.012+i*0.0625)%1),ang=obj.frame*0.03+i*2.4+lf*5,r=coreR*(4.2-lf*3.3);
            ctx.fillStyle="rgba("+(i%3?"190,120,255":"255,255,255")+","+(0.8*Math.sin(lf*Math.PI))+")";ctx.fillRect(Math.round((sx+Math.cos(ang)*r)/3)*3,Math.round((sy+Math.sin(ang)*r*0.55)/3)*3,3,3);}
          ctx.restore();
          // HP bar""".replace("\n", NL)
a = "function drawDiablo("; z = "function drawLaser("
if src.count(a) != 1 or src.count(z) != 1:
    print("ABORT: Diablo/Laser functions not found exactly once. Nothing written."); sys.exit(1)
i = src.index(a); j = src.index(z)
c = src.rfind("//", i, j)
end = c if c > i and "Laser" in src[c:j] and src[c:j].count("\n") <= 1 else j
src = src[:i] + DIABLO + NL + src[end:]
o = "// outer glow"
if src.count(o) != 1:
    print("ABORT: black hole glow marker not found exactly once. Nothing written."); sys.exit(1)
p = src.index(o); q = src.index("// HP bar", p)
src = src[:p] + BH + src[q + len("// HP bar"):]
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: Diablo and the black hole redrawn.")
