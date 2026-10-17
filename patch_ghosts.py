content = open('src/App.jsx', encoding='utf-8').read()

# 1. When a player leaves, turn their cat into a ghost instead of removing it
old = '''    channel.presence.subscribe("leave",(m)=>{
      const s=gs.current;
      s.cats=s.cats.filter(c=>c.id!==m.clientId);
      setOnlineCount(s.cats.filter(c=>!c.isSys).length);
    });'''

new = '''    channel.presence.subscribe("leave",(m)=>{
      const s=gs.current;
      const leavingCat=s.cats.find(c=>c.id===m.clientId);
      if(leavingCat){
        // turn into ghost instead of instant removal
        leavingCat.isGhost=true;
        leavingCat.ghostTimer=120; // 2 seconds at 60fps
        leavingCat.idle=true;
      }
      setOnlineCount(s.cats.filter(c=>!c.isSys&&!c.isGhost).length);
    });'''

if old in content:
    content = content.replace(old, new)
    print('Ghost on leave added')
else:
    print('FAILED - leave handler')

# 2. Update ghost timer in game loop, remove when faded
old2 = '''      // apply removals and additions
      if(toRemove.size>0) s.worldObjs=s.worldObjs.filter(o=>!toRemove.has(o.id));
      if(toAdd.length>0) s.worldObjs.push(...toAdd);'''

new2 = '''      // update ghost cats
      s.cats.forEach(cat=>{
        if(cat.isGhost){
          cat.ghostTimer=(cat.ghostTimer||0)-1;
          cat.ghostAlpha=Math.max(0,(cat.ghostTimer||0)/120);
        }
      });
      s.cats=s.cats.filter(c=>!c.isGhost||c.ghostTimer>0);

      // apply removals and additions
      if(toRemove.size>0) s.worldObjs=s.worldObjs.filter(o=>!toRemove.has(o.id));
      if(toAdd.length>0) s.worldObjs.push(...toAdd);'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Ghost timer loop added')
else:
    print('FAILED - ghost timer')

# 3. Draw ghosts with fade effect
old3 = '''        if(!c.grabbed&&!c.isSys){
          ctx.save();ctx.globalAlpha=c.idle?0.08:0.15;ctx.fillStyle="#000";
          ctx.beginPath();ctx.ellipse(sx+5.5*P,sy+13*P,14,4,0,0,Math.PI*2);ctx.fill();ctx.restore();
        }
        drawCat(ctx,sx,sy,P,c.frame,c.pal,c.flip,c.state,c.grabbed,c.isOwn,c.isSys,c.idle);'''

new3 = '''        if(!c.grabbed&&!c.isSys&&!c.isGhost){
          ctx.save();ctx.globalAlpha=c.idle?0.08:0.15;ctx.fillStyle="#000";
          ctx.beginPath();ctx.ellipse(sx+5.5*P,sy+13*P,14,4,0,0,Math.PI*2);ctx.fill();ctx.restore();
        }
        if(c.isGhost){
          ctx.save();
          ctx.globalAlpha=(c.ghostAlpha||0)*0.5;
          // blue-white ghost tint
          ctx.filter="grayscale(1) brightness(2) sepia(0.3) hue-rotate(200deg)";
          drawCat(ctx,sx,sy,P,c.frame,c.pal,c.flip,"sit",false,false,false,true);
          ctx.filter="none";
          ctx.restore();
        } else {
          drawCat(ctx,sx,sy,P,c.frame,c.pal,c.flip,c.state,c.grabbed,c.isOwn,c.isSys,c.idle);
        }'''

if old3 in content:
    content = content.replace(old3, new3)
    print('Ghost draw added')
else:
    print('FAILED - ghost draw')

open('src/App.jsx', 'w', encoding='utf-8').write(content)