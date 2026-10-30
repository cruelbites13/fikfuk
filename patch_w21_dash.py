# patch_w21_dash.py - the dash.
# Flick your finger (or mouse) fast across the screen and release: your cat bursts forward about 3-4 times faster for a
# fraction of a second, leaving a few fading ghost copies behind it and a quick whoosh. A flick means a drag of at least
# 55 px that is let go within 0.23 seconds. Slow steering, the chirp tap and everything else behave exactly as before.
# It recharges for 2.5 seconds. For the first dash-less 15-25 seconds of a new player's session, a faint "flick to dash"
# hint shows at the bottom (once ever dashed, it never shows again). The recap card counts dashes (3 or more).
# Other players see the dash as a fast run. Needs patch_w20_weather.py first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_dash*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_wx*/" not in src:
    print("ABORT: apply patch_w20_weather.py first. Nothing written."); sys.exit(1)

DASHFN = r'''/*_dash*/function doDash(dx,dy){
    const s=gs.current,m=s.cats.find(c=>c.id===s.myId);
    if(!m||m.idle||m.grabbed||s.frame<(s._dashCd||0))return;
    const l=Math.hypot(dx,dy)||1;
    s._dashCd=s.frame+150;m._dash=12;m._dx=dx/l;m._dy=dy/l;m.vx+=m._dx*6;m.vy+=m._dy*6;m.flip=dx<0;m.state="run";
    s._dashTr=s._dashTr||[];FKAudio.dash();RECAP.dashes=(RECAP.dashes||0)+1;s._dh=true;
    try{localStorage.setItem("fikfuk_dh","1");}catch(e){}
  }
  function doChirp(){'''
TRAIL = r'''function drawDashTrail(ctx,cam,s){
  const T=s._dashTr;if(!T||!T.length)return;
  for(let i=T.length-1;i>=0;i--){const g=T[i];if(--g.life<=0){T.splice(i,1);continue;}
    ctx.save();ctx.globalAlpha=g.life/14*0.42;drawCat(ctx,Math.round(g.x-cam.x),Math.round(g.y-cam.y),P,40,g.pal,g.flip,"run",false,false,false,false);ctx.restore();}
}
let uid=100;'''

src = swap(src, "function doChirp(){", DASHFN, "dash function")
src = swap(src, "let uid=100;", TRAIL, "trail drawer")
src = swap(src, "if(j&&j.active&&j.t0&&Date.now()-j.t0<250&&(j.maxD||0)<12&&!s.laserOn)doChirp();",
    "if(j&&j.active&&j.t0&&Date.now()-j.t0<250&&(j.maxD||0)<12&&!s.laserOn)doChirp();"
    "else if(j&&j.active&&j.t0&&Date.now()-j.t0<230&&Math.hypot(j.dx,j.dy)>=55&&!s.laserOn)doDash(j.dx,j.dy);", "flick detect")
src = swap(src, "// apply cat speed boost",
    'if(myCat&&myCat._dash>0){myCat._dash--;myCat.vx+=myCat._dx*2.0;myCat.vy+=myCat._dy*2.0;myCat.state="run";if(s.frame%2===0)(s._dashTr||(s._dashTr=[])).push({x:myCat.x,y:myCat.y,flip:myCat.flip,pal:myCat.pal,life:14});myCat._cap=11;}else if(myCat&&myCat._cap>3.5){myCat._cap=Math.max(3.5,myCat._cap*0.9);}\n      // apply cat speed boost', "dash physics")
src = swap(src, "if(spd2>3.5){cat.vx=cat.vx/spd2*3.5;cat.vy=cat.vy/spd2*3.5;}", "{const _cp=cat._cap||3.5;if(spd2>_cp){cat.vx=cat.vx/spd2*_cp;cat.vy=cat.vy/spd2*_cp;}}", "speed cap")
src = swap(src, "drawPages(ctx,cam,W,H,s.frame,s);", "drawPages(ctx,cam,W,H,s.frame,s);drawDashTrail(ctx,cam,s);", "draw trail")
src = swap(src, "// ── reset spectacle overlay ──",
    '{if(s._dh===undefined){try{s._dh=!!localStorage.getItem("fikfuk_dh");}catch(e){s._dh=true;}}'
    'if(!s._dh&&s.myId&&s.frame>900&&s.frame<1700){const _a=Math.min(1,(s.frame-900)/60,(1700-s.frame)/60);ctx.save();ctx.font="8px "+ff;ctx.textAlign="center";ctx.fillStyle=`rgba(255,255,255,${0.55*_a})`;ctx.fillText("flick to dash",W/2,H-110);ctx.restore();}}\n      // ── reset spectacle overlay ──', "hint")
src = swap(src, 'thunder(){blip(75,28,2.2,0.22,"sine");setTimeout(()=>blip(130,40,1.6,0.12,"triangle"),250);},',
    'thunder(){blip(75,28,2.2,0.22,"sine");setTimeout(()=>blip(130,40,1.6,0.12,"triangle"),250);},'
    'dash(){blip(240,1100,0.2,0.07,"triangle");blip(1500,420,0.14,0.035,"sine");},', "dash sound")
src = swap(src, "Object.assign(RECAP,{e:ep,t0:Date.now(),pages:0,", "Object.assign(RECAP,{e:ep,t0:Date.now(),dashes:0,pages:0,", "recap reset")
src = swap(src, "pages:RECAP.pages||0}", "pages:RECAP.pages||0,dashes:RECAP.dashes||0}", "recap stat")
src = swap(src, "if(d.stats.hops)rows.push(", 'if(d.stats.dashes>=3)rows.push(["dashes",String(d.stats.dashes)]);if(d.stats.hops)rows.push(', "recap row")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 11 edits applied.")
