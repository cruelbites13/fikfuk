# patch_w15_catacts.py - cats have their own little life. A cat that has been sitting for a few seconds starts doing
# things on its own, and every cat on your screen does it, including other players' cats:
#   groom (a paw washes the face, eyes closed) - stretch (the body slowly stretches out) - tail flick (a quick extra swish)
#   - yawn (mouth open, eyes squeezed) - and after about 25 seconds of sitting: sleep (eyes closed, settled lower, floating "z"s).
# Which action and when depends on the cat, so a group of sitting cats never moves in sync. Walking, sitting and
# the NPC cats are unchanged; nothing is sent over the network. Needs patch_w7_cat_redraw first. Safe to run twice.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
if "/*_catact*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "function _cmix(" not in src:
    print("ABORT: apply patch_w7_cat_redraw.py first. Nothing written."); sys.exit(1)
def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written."); sys.exit(1)
    return text.replace(old, new)

src = swap(src, "function _cmix(",
 "/*_catact*/let _catAct=0;function _actFor(c){const t=c._sitT||0;if(t<240||c.isSys||c.grabbed)return 0;if(t>1500)return 4;"
 "const i=Math.floor((t-240)/300);if((t-240)%300>200)return 0;return[1,2,3,5,0,0][hashStr(String(c.id)+\":\"+i)%6];}\nfunction _cmix(", "act helpers")
src = swap(src, 'const sit=state==="sit",run=state==="run";',
 'const sit=state==="sit",run=state==="run";const _a=(sit&&!isSys)?_catAct:0;'
 'if(_a===2){const _k=0.5+0.5*Math.sin(frame*0.05);ctx.translate(0,12.5*p);ctx.scale(1+0.14*_k,1-0.08*_k);ctx.translate(0,-12.5*p);}'
 'if(_a===4){ctx.translate(0,1.2*p);}', "action setup")
src = swap(src, "const blink=(frame%220>210);",
 'if(_a===1){const _k=Math.round(Math.sin(frame*0.25)*1);R(T.deep,6,1+_k,4,3);R(body,6,1+_k,3,2);R(T.hi,6,1+_k,2,1);R(inner,7,2+_k,1,1);R("#ff8a9a",5,4,1,1);}'
 'if(_a===5){R("#6a1020",4,4,3,2);R("#ff8a9a",5,5,1,1);}'
 'if(_a===3){const _w=Math.round(Math.sin(frame*0.35)*2);R(stripe,10+_w,7,1,3);R(body,11+_w,6,1,2);}'
 "const blink=(frame%220>210)||_a===1||_a===4||_a===5;", "action drawing")
src = swap(src, 'if(isOwn&&!isSys){ctx.fillStyle="rgba(255,80,80,0.85)";ctx.beginPath();ctx.arc(x+5.5*p,y-6,3,0,Math.PI*2);ctx.fill();}',
 'if(_catAct===4&&!isSys){const _zt=frame*0.03;for(let i=0;i<3;i++){const ph=(_zt+i*0.33)%1;ctx.globalAlpha=(1-ph)*0.8;ctx.font=(p*(1.6+i*0.5))+"px "+ff;ctx.fillStyle="#bbbbff";ctx.fillText("z",x+10*p+ph*8*p,y-6-ph*14*p);}ctx.globalAlpha=idle?0.35:1;}'
 'if(isOwn&&!isSys){ctx.fillStyle="rgba(255,80,80,0.85)";ctx.beginPath();ctx.arc(x+5.5*p,y-6,3,0,Math.PI*2);ctx.fill();}', "sleep z")
src = swap(src, "drawCat(ctx,sx,sy,P,c.frame,c.pal,c.flip,c.state,c.grabbed,c.isOwn,c.isSys,c.idle);",
 'c._sitT=(c.state==="sit"&&!c.isSys)?(c._sitT||0)+1:0;_catAct=_actFor(c);drawCat(ctx,sx,sy,P,c.frame,c.pal,c.flip,c.state,c.grabbed,c.isOwn,c.isSys,c.idle);_catAct=0;', "draw call")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 5 edits applied (groom, stretch, tail flick, yawn, sleep).")
