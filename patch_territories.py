content = open('src/App.jsx', encoding='utf-8').read()

# 1. Add territory logic in cat update loop
old = '''        // ── whisper proximity ──
        if(cat.isOwn&&!cat.isSys){'''

new = '''        // ── territory claiming ──
        if(cat.isOwn&&!cat.isSys){
          const spd3=Math.hypot(cat.vx,cat.vy);
          if(spd3<0.3){
            cat._sitTimer=(cat._sitTimer||0)+1;
            if(cat._sitTimer===120){
              cat._territory={x:cat.x,y:cat.y,radius:80,name:cat.name,palBody:cat.pal.body};
              s._myTerritory=cat._territory;
            }
          } else {
            cat._sitTimer=0;
          }
        }

        // ── whisper proximity ──
        if(cat.isOwn&&!cat.isSys){'''

if old in content:
    content = content.replace(old, new)
    print('Territory logic added')
else:
    print('FAILED - territory logic')

# 2. Broadcast territory via presence update
old2 = '''        if(s.frame%300===0&&myCat){
        const sess=loadSession();
        if(sess)saveSession({...sess,x:myCat.x,y:myCat.y,confessions:myCat.confessions});
        // broadcast territory
        if(s._myTerritory&&myCat._updatePresence)myCat._updatePresence();
      }'''

new2 = '''        if(s.frame%300===0&&myCat){
        const sess=loadSession();
        if(sess)saveSession({...sess,x:myCat.x,y:myCat.y,confessions:myCat.confessions});
        if(s._myTerritory&&myCat._updatePresence)myCat._updatePresence();
      }'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Territory broadcast added')
else:
    print('FAILED - territory broadcast')

# 3. Draw territories
old3 = "      // \u2500\u2500 Secret Rooms \u2500\u2500"

new3 = (
    "      // \u2500\u2500 Territories \u2500\u2500\n"
    "      s.cats.filter(c=>!c.isSys&&c._territory).forEach(c=>{\n"
    "        const t=c._territory;\n"
    "        const{sx:tx,sy:ty}=w2s(t.x,t.y);\n"
    "        if(tx<-t.radius||tx>W+t.radius||ty<-t.radius||ty>H+t.radius)return;\n"
    "        ctx.save();\n"
    "        ctx.globalAlpha=0.12;\n"
    "        ctx.fillStyle=t.palBody||'#ffffff';\n"
    "        ctx.beginPath();ctx.arc(tx,ty,t.radius,0,Math.PI*2);ctx.fill();\n"
    "        ctx.globalAlpha=0.25;\n"
    "        ctx.strokeStyle=t.palBody||'#ffffff';\n"
    "        ctx.lineWidth=1;\n"
    "        ctx.setLineDash([4,4]);\n"
    "        ctx.beginPath();ctx.arc(tx,ty,t.radius,0,Math.PI*2);ctx.stroke();\n"
    "        ctx.setLineDash([]);\n"
    "        ctx.globalAlpha=0.4;\n"
    "        ctx.font=`6px ${ff}`;\n"
    "        ctx.fillStyle=t.palBody||'#ffffff';\n"
    "        const tw=ctx.measureText(t.name).width;\n"
    "        ctx.fillText(t.name,tx-tw/2,ty+t.radius+10);\n"
    "        ctx.restore();\n"
    "      });\n"
    "\n"
    "      // \u2500\u2500 Secret Rooms \u2500\u2500"
)

if "      // \u2500\u2500 Secret Rooms \u2500\u2500" in content:
    content = content.replace("      // \u2500\u2500 Secret Rooms \u2500\u2500", new3, 1)
    print('Territory draw added')
else:
    print('FAILED - territory draw')

# 4. Restore territory from presence data
old4 = """    const addRemoteCat=(d,cid)=>{
      const s=gs.current;
      if(cid===clientId.current)return;
      s.cats=s.cats.filter(c=>c.id!==cid);
      if(!d||!d.name)return;
      const cat=makeCat(d.x??WORLD_W/2,d.y??WORLD_H/2,d.palId??0,d.name,false,false,null,cid);
      cat.confessions=d.confessions??[];
      cat.flip=d.flip??false;
      s.cats.push(cat);
      setOnlineCount(s.cats.filter(c=>!c.isSys).length);
    };"""

new4 = """    const addRemoteCat=(d,cid)=>{
      const s=gs.current;
      if(cid===clientId.current)return;
      s.cats=s.cats.filter(c=>c.id!==cid);
      if(!d||!d.name)return;
      const cat=makeCat(d.x??WORLD_W/2,d.y??WORLD_H/2,d.palId??0,d.name,false,false,null,cid);
      cat.confessions=d.confessions??[];
      cat.flip=d.flip??false;
      if(d.territory) cat._territory=d.territory;
      s.cats.push(cat);
      setOnlineCount(s.cats.filter(c=>!c.isSys).length);
    };"""

if old4 in content:
    content = content.replace(old4, new4)
    print('Territory restore added')
else:
    print('FAILED - territory restore')

# 5. Include territory in presence data
old5 = """    const myPresenceData=()=>({
      name:myCat.name,palId:myCat.palId,
      x:myCat.x,y:myCat.y,flip:myCat.flip,
      confessions:myCat.confessions,
    });"""

new5 = """    const myPresenceData=()=>({
      name:myCat.name,palId:myCat.palId,
      x:myCat.x,y:myCat.y,flip:myCat.flip,
      confessions:myCat.confessions,
      territory:myCat._territory||null,
    });"""

if old5 in content:
    content = content.replace(old5, new5)
    print('Territory in presence added')
else:
    print('FAILED - territory presence')

open('src/App.jsx', 'w', encoding='utf-8').write(content)