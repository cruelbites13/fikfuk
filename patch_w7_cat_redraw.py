# patch_w7_cat_redraw.py - a new cat: rounder head with tabby marks and lit ears, a chest patch, haunches, a curling tail,
# bigger shiny eyes, soft light from the top-left with a darker far side, and a proper walking gait.
# Same size, same palettes, same name tags, same sit/run/idle/grabbed behaviour. Replaces patch_w6 if you did not apply it;
# if you did apply it, this replaces its lighting (the soft ground shadow from it stays). Safe to run twice.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
if "function _cmix(" in src:
    print("Already patched. Nothing written."); sys.exit(0)
def once(text, s, label):
    if text.count(s) != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {text.count(s)}. Nothing written."); sys.exit(1)
a = 'const bob=grabbed?0:Math.sin(frame*0.08)*(state==="run"?0:0.5);'; once(src, a, "bob line")
w = "ctx.fillRect(-2*p,(bob+2)*p,3*p,1);"; once(src, w, "whisker line")
i = src.index(a) + len(a)
j = src.rindex('ctx.fillStyle="rgba(255,255,255,0.5)";', i, src.index(w))
NL = "\r\n" if "\r\n" in src else "\n"
NEW = r"""  const R=(c,x,y,w,h)=>{ctx.fillStyle=c;ctx.fillRect(x*p,(y+bob)*p,w*p,h*p);};
  const T=pal._t||(pal._t={hi:_cmix(body,"#ffffff",0.34),lo:shadow,deep:_cmix(shadow,"#000000",0.4),hi2:_cmix(inner,"#ffffff",0.45),rim:_cmix(body,"#ffffff",0.55)});
  const sit=state==="sit",run=state==="run";
  const sw=Math.round(Math.sin(frame*0.1)*1);
  // tail (behind the body)
  if(sit){R(T.deep,8,11,4,1);R(shadow,9,10,3,1);R(stripe,11,10,1,1);R(body,9,11,2,1);}
  else{[[9,10],[10,9],[11,7],[11,5],[10+sw,3]].forEach((q,i)=>{R(i%2?stripe:shadow,q[0],q[1],2,2);R(T.hi,q[0],q[1],1,1);});R(inner,10+sw,3,1,1);}
  // body: dark back layer, lit main mass, haunches, chest
  R(T.deep,2,12,8,1);
  R(shadow,2,5,8,7);R(body,2,5,6,6);R(T.hi,2,5,2,5);R(T.hi,3,5,3,1);R(T.deep,8,10,2,2);R(shadow,2,11,8,1);
  if(sit){R(body,1,8,3,4);R(T.hi,1,8,1,3);R(shadow,8,8,3,4);R(T.deep,10,9,1,3);R(T.deep,1,12,3,1);}
  else{R(body,1,9,2,3);R(T.hi,1,9,1,2);R(shadow,9,9,2,3);}
  R(inner,4,6,3,5);R(T.hi2,4,6,1,3);R(shadow,6,9,1,2);
  R(stripe,2,6,2,1);R(stripe,2,8,2,1);R(stripe,7,6,2,1);R(stripe,7,8,2,1);
  // legs
  if(sit){R(body,4,11,2,2);R(shadow,6,11,2,2);R(inner,4,12,2,1);R(inner,6,12,2,1);R(T.hi,4,11,1,1);}
  else{
    const lf=run?Math.sin(frame*0.28):0,a=Math.round(lf),b=-a;
    R(body,3,11,2,2+Math.max(0,a));R(shadow,6,11,2,2+Math.max(0,b));
    R(inner,3,12+Math.max(0,a),2,1);R(inner,6,12+Math.max(0,b),2,1);R(T.hi,3,11,1,1);
    R(body,1,11,2,1+Math.max(0,b));R(shadow,9,11,2,1+Math.max(0,a));
  }
  // ears
  R(body,1,-4,1,1);R(body,1,-3,2,1);R(body,0,-2,3,2);R(inner,1,-3,1,2);R(T.rim,1,-4,1,1);R(T.hi,0,-2,1,1);
  R(body,9,-4,1,1);R(body,8,-3,2,1);R(body,8,-2,3,2);R(inner,9,-3,1,2);R(shadow,10,-2,1,2);R(shadow,9,-4,1,1);
  // head: lit top-left, shaded bottom-right, rounded corners
  R(shadow,2,4,7,1);R(body,2,-1,7,1);R(body,0,0,11,3);R(body,1,3,9,1);
  R(T.rim,2,-1,3,1);R(T.hi,0,0,2,2);R(T.hi,5,-1,2,1);
  R(shadow,9,1,2,3);R(shadow,1,3,9,1);R(T.deep,10,2,1,2);
  R(stripe,4,-1,1,2);R(stripe,6,-1,1,2);R(stripe,5,0,1,1);R(stripe,0,2,2,1);R(stripe,9,2,2,1);
  R(inner,3,3,5,2);R(T.hi2,3,3,2,1);
  ctx.fillStyle="rgba(255,150,150,0.35)";ctx.fillRect(1*p,(bob+3)*p,2*p,p);ctx.fillRect(8*p,(bob+3)*p,2*p,p);
  const blink=(frame%220>210);
  if(idle||blink){
    ctx.fillStyle=idle?"#555":"#000";
    ctx.fillRect(2*p,(bob+1)*p,3*p,p);ctx.fillRect(6*p,(bob+1)*p,3*p,p);
  } else {
    ctx.fillStyle=_cmix(eye,"#000000",0.3);ctx.fillRect(2*p,(bob+1)*p,3*p,2*p);ctx.fillRect(6*p,(bob+1)*p,3*p,2*p);
    ctx.fillStyle=eye;ctx.fillRect(2*p,(bob+1)*p,3*p,p);ctx.fillRect(6*p,(bob+1)*p,3*p,p);
    ctx.fillStyle=pupil;ctx.fillRect(3*p,(bob+1)*p,p,2*p);ctx.fillRect(7*p,(bob+1)*p,p,2*p);
    ctx.fillStyle="rgba(255,255,255,0.95)";ctx.fillRect(2*p,(bob+1)*p,p,p);ctx.fillRect(6*p,(bob+1)*p,p,p);
  }
  ctx.fillStyle=nose;ctx.fillRect(4*p,(bob+3)*p,3*p,p);ctx.fillRect(5*p,(bob+3)*p,p,2*p);
  ctx.fillStyle=T.deep;ctx.fillRect(4*p,(bob+4)*p,p,p);ctx.fillRect(6*p,(bob+4)*p,p,p);""".replace("\n", NL)
src = src[:i] + NL + NEW + "  " + src[j:]
helper = ('function _cmix(c,t,k){if(typeof c!=="string"||c[0]!=="#"||c.length<7)return c;'
 'const n=parseInt(c.slice(1,7),16),m=parseInt(t.slice(1,7),16),r=(n>>16)&255,g=(n>>8)&255,b=n&255,R2=(m>>16)&255,G=(m>>8)&255,B=m&255;'
 'return"rgb("+Math.round(r+(R2-r)*k)+","+Math.round(g+(G-g)*k)+","+Math.round(b+(B-b)*k)+")";}'+NL)
f = "function drawCat(ctx,x,y,p,frame,pal,flip,state,grabbed,isOwn,isSys,idle){"; once(src, f, "drawCat")
src = src.replace(f, helper + f)
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: new cat applied.")
