content = open('src/App.jsx', encoding='utf-8').read()

# 1. Add black hole subscribe after letter subscribe
old = '''    channel.subscribe("reset",()=>{'''

new = '''    channel.subscribe("blackhole_hit",(msg)=>{
      const s=gs.current;
      const bh=s.worldObjs.find(o=>o.type==="blackhole");
      if(bh){
        bh.hp=(bh.hp||50)-1;
        if(bh.hp<=0){
          // closed - explosion effect
          s.particles.push(...Array.from({length:20},(_,i)=>({
            text:"✦",
            x:bh.x, y:bh.y,
            vx:Math.cos(i/20*Math.PI*2)*2,
            vy:Math.sin(i/20*Math.PI*2)*2,
            alpha:1, life:120, delay:0,
          })));
          // speed boost all cats
          s.cats.forEach(c=>{if(!c.isSys){c._boostTimer=300;}});
          s.worldObjs=s.worldObjs.filter(o=>o.type!=="blackhole");
          s._bhCooldown=45*60*60; // 45 min cooldown in frames
        }
      }
    });

    channel.subscribe("reset",()=>{'''

if old in content:
    content = content.replace(old, new)
    print('Blackhole subscribe added')
else:
    print('FAILED - subscribe')

# 2. Add blackhole to spawn system and world object update
old2 = '''      // ── spawn new objects over time ──
      if(s.frame%60===0){
        const types=["ufo","fossil","wildcat","mouse","human","diablo"];
        types.forEach(type=>{
          const interval=SPAWN_INTERVALS[type]*60;
          if(s.frame%(interval)===0){
            const newObj=spawnObj(type,s.worldObjs);
            if(newObj)s.worldObjs.push(newObj);
          }
        });
      }'''

new2 = '''      // ── spawn new objects over time ──
      if(s.frame%60===0){
        const types=["ufo","fossil","wildcat","mouse","human","diablo"];
        types.forEach(type=>{
          const interval=SPAWN_INTERVALS[type]*60;
          if(s.frame%(interval)===0){
            const newObj=spawnObj(type,s.worldObjs);
            if(newObj)s.worldObjs.push(newObj);
          }
        });
      }
      // black hole spawns every 45 min (162000 frames at 60fps)
      if(s._bhCooldown>0) s._bhCooldown--;
      if(!s.worldObjs.find(o=>o.type==="blackhole")&&s._bhCooldown===0&&s.frame>3600){
        s.worldObjs.push({
          type:"blackhole", id:"bh_0",
          x:1000+Math.random()*(WORLD_W-2000),
          y:1000+Math.random()*(WORLD_H-2000),
          hp:50, maxHp:50,
          pullRadius:300,
          frame:0,
        });
        s._bhCooldown=-1; // active
      }'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Blackhole spawn added')
else:
    print('FAILED - spawn')

# 3. Add blackhole physics in world object update loop
old3 = '''        // Breadcrumb - fades out over time
        if(obj.type==="breadcrumb"){
          obj.life=(obj.life||0)-1;
          if(obj.life<=0) toRemove.add(obj.id);
        }'''

new3 = '''        // Breadcrumb - fades out over time
        if(obj.type==="breadcrumb"){
          obj.life=(obj.life||0)-1;
          if(obj.life<=0) toRemove.add(obj.id);
        }
        // Black hole - pulls nearby cats
        if(obj.type==="blackhole"){
          obj.frame++;
          // pull all cats toward it
          s.cats.forEach(cat=>{
            if(cat.isSys) return;
            const dx=obj.x-cat.x, dy=obj.y-cat.y;
            const dist=Math.hypot(dx,dy);
            if(dist<obj.pullRadius&&dist>5){
              const pull=0.3*(1-dist/obj.pullRadius);
              cat.vx+=(dx/dist)*pull;
              cat.vy+=(dy/dist)*pull;
            }
          });
          // laser hit detection
          if(laser.active&&Math.hypot(laserWx-obj.x,laserWy-obj.y)<60){
            obj._hitCooldown=(obj._hitCooldown||0)-1;
            if((obj._hitCooldown||0)<=0){
              obj._hitCooldown=10;
              obj.hp=Math.max(0,obj.hp-1);
              channelRef.current?.publish("blackhole_hit",{});
              if(obj.hp<=0) toRemove.add(obj.id);
            }
          }
        }'''

if old3 in content:
    content = content.replace(old3, new3)
    print('Blackhole physics added')
else:
    print('FAILED - physics')

# 4. Draw blackhole
old4 = '''        if(obj.type==="diablo")drawDiablo(ctx,sx,sy,obj.frame,obj.hp);'''

new4 = '''        if(obj.type==="diablo")drawDiablo(ctx,sx,sy,obj.frame,obj.hp);
        if(obj.type==="blackhole"){
          ctx.save();
          const pulse=Math.sin(obj.frame*0.05)*0.3;
          // outer glow
          const grd=ctx.createRadialGradient(sx,sy,0,sx,sy,obj.pullRadius);
          grd.addColorStop(0,"rgba(0,0,0,0)");
          grd.addColorStop(0.7,"rgba(50,0,80,0.08)");
          grd.addColorStop(1,"rgba(100,0,150,0.02)");
          ctx.fillStyle=grd;
          ctx.beginPath();ctx.arc(sx,sy,obj.pullRadius,0,Math.PI*2);ctx.fill();
          // core
          const coreR=20+pulse*5;
          const cg=ctx.createRadialGradient(sx,sy,0,sx,sy,coreR);
          cg.addColorStop(0,"rgba(0,0,0,1)");
          cg.addColorStop(0.6,"rgba(60,0,100,0.8)");
          cg.addColorStop(1,"rgba(100,0,150,0)");
          ctx.fillStyle=cg;
          ctx.beginPath();ctx.arc(sx,sy,coreR,0,Math.PI*2);ctx.fill();
          // ring
          ctx.strokeStyle=`rgba(150,0,255,${0.5+pulse*0.3})`;
          ctx.lineWidth=2;
          ctx.beginPath();ctx.arc(sx,sy,coreR+4,0,Math.PI*2);ctx.stroke();
          // HP bar
          ctx.fillStyle="rgba(0,0,0,0.5)";ctx.fillRect(sx-30,sy+coreR+8,60,5);
          ctx.fillStyle="rgba(150,0,255,0.8)";ctx.fillRect(sx-30,sy+coreR+8,60*(obj.hp/obj.maxHp),5);
          // label
          ctx.font=`7px ${ff}`;ctx.fillStyle="rgba(180,100,255,0.8)";
          ctx.fillText("laser to close",sx-35,sy+coreR+22);
          ctx.restore();
        }'''

if old4 in content:
    content = content.replace(old4, new4)
    print('Blackhole draw added')
else:
    print('FAILED - draw')

# 5. Blackhole on minimap
old5 = '''      // oracle on minimap
      s.cats.filter(c=>c.sysType==="oracle").forEach(c=>{'''

new5 = '''      // blackhole on minimap
      const bh=s.worldObjs.find(o=>o.type==="blackhole");
      if(bh){
        const bhmx=MM_X+(bh.x/WORLD_W)*MM_W;
        const bhmy=MM_Y+(bh.y/WORLD_H)*MM_H;
        ctx.fillStyle=`rgba(150,0,255,${0.6+Math.sin(s.frame*0.1)*0.3})`;
        ctx.beginPath();ctx.arc(bhmx,bhmy,4,0,Math.PI*2);ctx.fill();
      }
      // oracle on minimap
      s.cats.filter(c=>c.sysType==="oracle").forEach(c=>{'''

if old5 in content:
    content = content.replace(old5, new5)
    print('Blackhole minimap added')
else:
    print('FAILED - minimap')

open('src/App.jsx', 'w', encoding='utf-8').write(content)