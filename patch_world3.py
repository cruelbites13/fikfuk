content = open('src/App.jsx', encoding='utf-8').read()
failures = 0

def swap(old, new, label):
    global content, failures
    n = content.count(old)
    if n == 1:
        content = content.replace(old, new)
        print('OK     -', label)
    else:
        failures += 1
        print('FAILED -', label, '(found', n, 'matches, expected 1)')

# 1. spawn timers: shared-clock slots + seeded spawns
swap('const interval=SPAWN_INTERVALS[type]*60;',
'''const slotNow=Math.floor((sharedNow()-EPOCH_ANCHOR)/(SPAWN_INTERVALS[type]*1000));
          s._spawnSlot=s._spawnSlot||{};
          if(s._spawnSlot[type]===undefined)s._spawnSlot[type]=slotNow;''',
'spawn slot setup')

swap('if(s.frame%(interval)===0){',
'''if(slotNow!==s._spawnSlot[type]){
            s._spawnSlot[type]=slotNow;''',
'spawn slot trigger')

swap('const newObj=spawnObj(type,s.worldObjs);',
'const newObj=spawnObj(type,s.worldObjs,mulberry32(hashStr("fikfuk:spawn:"+type+":"+slotNow)),"t"+slotNow);',
'seeded spawn')

# 2. black hole: deterministic schedule
swap('''      // black hole spawns every 45 min (162000 frames at 60fps)
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
      }''',
'''      // black hole: fixed schedule on the shared clock
      // active for the first 20 min of every 45 min slot, seeded position
      {
        const bhSlotMs=45*60*1000;
        const sinceA=sharedNow()-EPOCH_ANCHOR;
        const bhSlot=Math.floor(sinceA/bhSlotMs);
        const inWindow=(sinceA%bhSlotMs)<20*60*1000;
        const bhPos=(slot)=>{
          const r=mulberry32(hashStr("fikfuk:bh:"+slot));
          return {x:1000+r()*(WORLD_W-2000),y:1000+r()*(WORLD_H-2000)};
        };
        const bhObj=s.worldObjs.find(o=>o.type==="blackhole");
        if(inWindow&&!bhObj&&s._bhClosedSlot!==bhSlot){
          const p=bhPos(bhSlot);
          s.worldObjs.push({type:"blackhole",id:"bh_"+bhSlot,x:p.x,y:p.y,hp:50,maxHp:50,pullRadius:300,frame:0,slot:bhSlot});
        }
        if(!inWindow&&bhObj){
          s.worldObjs=s.worldObjs.filter(o=>o.type!=="blackhole");
        }
        if(!window.__fikfukBH){
          window.__fikfukBH=(slot)=>{
            const sl=(slot===undefined)?Math.floor((sharedNow()-EPOCH_ANCHOR)/bhSlotMs):slot;
            const p=bhPos(sl);
            return {slot:sl,x:Math.round(p.x),y:Math.round(p.y),activeNow:((sharedNow()-EPOCH_ANCHOR)%bhSlotMs)<20*60*1000};
          };
        }
      }''',
'black hole schedule')

# 3. black hole closing records the slot so it cannot respawn
swap('s._bhCooldown=45*60*60; // 45 min cooldown in frames',
     's._bhClosedSlot=bh.slot;',
     'remote close records slot')

swap('if(obj.hp<=0) toRemove.add(obj.id);',
     'if(obj.hp<=0){ s._bhClosedSlot=obj.slot; toRemove.add(obj.id); }',
     'local close records slot')

# 4. ignore own echoed blackhole_hit messages
swap('channel.subscribe("blackhole_hit",(msg)=>{',
'''channel.subscribe("blackhole_hit",(msg)=>{
      if(msg.clientId===clientId.current)return;''',
'ignore own echo')

# 5. tides on the shared clock
swap('const tidePhase = s.frame % TIDE_PERIOD;',
     'const tidePhase = (((sharedNow()-EPOCH_ANCHOR)/1000*60)%TIDE_PERIOD);',
     'tide on shared clock')

if failures == 0:
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('\nAll steps applied. File written.')
else:
    print('\n' + str(failures) + ' step(s) failed. NOTHING was written. Paste this output.')