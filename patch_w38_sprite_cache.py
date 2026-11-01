# patch_w38_sprite_cache.py - speed: every cat is drawn once as a small picture, then re-used.
# A cat is built from about 100 tiny rectangles, and the game was redrawing all of them for every cat on every frame
# (with 40 cats on screen that is around 4,000 drawing commands per frame). Now each distinct look of a cat (coat, sitting
# or running, facing left or right, which of the few bobbing/leg/tail/blink poses it is in) is drawn once into a hidden
# picture and then stamped onto the screen with a single command. The pictures are the same pixels the old code produced,
# except that the gentle idle bob moves in 5 small steps instead of a smooth glide (not noticeable at this size).
# Cats doing something special (grabbed, asleep/idle, doing a sit-action like stretching or yawning, and the NPC cats with
# glowing rings) still use the old drawing code, so nothing about how they look changes.
# Needs no other patch. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_spr*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)

WRAP = r'''/*_spr*/
const _SPRC=new Map();let _SPRN=0,_SO=null;
function drawCat(ctx,x,y,p,frame,pal,flip,state,grabbed,isOwn,isSys,idle){
  if(grabbed||isSys||idle||_catAct||(state!=="sit"&&state!=="run")||typeof document==="undefined")return drawCat0(ctx,x,y,p,frame,pal,flip,state,grabbed,isOwn,isSys,idle);
  const run=state==="run",bq=run?0:Math.round(Math.sin(frame*0.08)*2),a=run?Math.round(Math.sin(frame*0.28)):0,sw=Math.round(Math.sin(frame*0.1)),bl=(frame%220>210)?1:0;
  const sid=pal._sk||(pal._sk=pal.body+pal.shadow+pal.stripe+pal.inner+pal.eye+pal.pupil+pal.nose),key=sid+"|"+p+"|"+state+"|"+(flip?1:0)+"|"+bq+"|"+a+"|"+sw+"|"+bl;
  let c=_SPRC.get(key);
  if(!c){
    if(_SPRC.size>800)_SPRC.clear();
    const ox=Math.ceil(5*p),oy=Math.ceil(7*p);c=document.createElement("canvas");c.width=Math.ceil(22*p);c.height=Math.ceil(23*p);
    const g=c.getContext("2d");g.imageSmoothingEnabled=false;
    _SO={bob:bq/4,a:a,sw:sw,blink:!!bl};try{drawCat0(g,ox,oy,p,frame,pal,flip,state,false,isOwn,false,false);}finally{_SO=null;}
    c._ox=ox;c._oy=oy;_SPRC.set(key,c);
  }
  ctx.drawImage(c,Math.round(x-c._ox),Math.round(y-c._oy));
  const tag=pal._name||"";
  if(tag){
    const lk=tag+"|"+p+"|"+(isOwn?1:0);let L=_SPRC.get(lk);
    if(!L){const g0=document.createElement("canvas").getContext("2d");g0.font=`${Math.max(6,p*1.5)}px ${ff}`;const w=Math.ceil(g0.measureText(tag).width)+4,h=Math.ceil(p*2.2)+2;
      L=document.createElement("canvas");L.width=w;L.height=h;const g=L.getContext("2d");g.font=`${Math.max(6,p*1.5)}px ${ff}`;g.fillStyle=isOwn?"rgba(255,80,80,0.9)":"rgba(180,180,255,0.6)";g.fillText(tag,2,Math.ceil(p*1.7));L._tw=w-4;_SPRC.set(lk,L);}
    ctx.drawImage(L,Math.round(x+5.5*p-L._tw/2-2),Math.round(y+16*p-Math.ceil(p*1.7)));}
}
function drawCat0(ctx,x,y,p,frame,pal,flip,state,grabbed,isOwn,isSys,idle){'''

CRLF = "\r\n" in src
if CRLF: src = src.replace("\r\n", "\n")
n = 0
def S(old, new, label):
    global src, n
    src = swap(src, old, new, label); n += 1
S('const tag=pal._name||"";', 'const tag=_SO?"":(pal._name||"");', "label")
S("function drawCat(ctx,x,y,p,frame,pal,flip,state,grabbed,isOwn,isSys,idle){", WRAP, "wrapper")
S('const bob=grabbed?0:Math.sin(frame*0.08)*(state==="run"?0:0.5);', 'const bob=_SO?_SO.bob:(grabbed?0:Math.sin(frame*0.08)*(state==="run"?0:0.5));', "bob")
S("const sw=Math.round(Math.sin(frame*0.1)*1);", "const sw=_SO?_SO.sw:Math.round(Math.sin(frame*0.1)*1);", "tail sway")
S("const lf=run?Math.sin(frame*0.28):0,a=Math.round(lf),b=-a;", "const lf=run?Math.sin(frame*0.28):0,a=_SO?_SO.a:Math.round(lf),b=-a;", "legs")
S("const blink=(frame%220>210)||_a===1||_a===4||_a===5;", "const blink=_SO?_SO.blink:((frame%220>210)||_a===1||_a===4||_a===5);", "blink")
if CRLF: src = src.replace("\n", "\r\n")
open(P, "w", encoding="utf-8", newline="").write(src)
print(f"OK: {n} edits applied.")
