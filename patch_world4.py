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

# 1. diablo gets a unique id like every other object
swap('type:"diablo",id:"diablo_0",', 'type:"diablo",id,', 'diablo unique id')

# 2. announce UFO / Diablo deaths when the removal set is applied
swap('if(toRemove.size>0) s.worldObjs=s.worldObjs.filter(o=>!toRemove.has(o.id));',
'''if(toRemove.size>0){
        toRemove.forEach(id=>{
          const o=s.worldObjs.find(x=>x.id===id);
          if(o&&(o.type==="ufo"||o.type==="diablo")){
            s._dead=s._dead||new Set();
            s._dead.add(id);
            channelRef.current?.publish("obj_dead",{id,type:o.type,x:Math.round(o.x),y:Math.round(o.y)});
          }
        });
        s.worldObjs=s.worldObjs.filter(o=>!toRemove.has(o.id));
      }''',
'announce deaths')

# 3. share Diablo HP on every hit
swap('obj.hitCooldown=30;',
'''obj.hitCooldown=30;
            channelRef.current?.publish("dia_hit",{id:obj.id,hp:obj.hp});''',
'share diablo hits')

# 4. subscribers + sync sender
swap('channel.subscribe("blackhole_hit",(msg)=>{',
'''const applyDead=(id,type,x,y,announce)=>{
      const s=gs.current;
      s._dead=s._dead||new Set();
      const had=s.worldObjs.find(o=>o.id===id);
      s._dead.add(id);
      s.worldObjs=s.worldObjs.filter(o=>o.id!==id);
      if(had&&type==="diablo"&&announce){
        s.worldObjs.push({type:"fossil",id:"fossil_reward_"+id,x:x+100,y:y+100,confession:"u defeated diablo",revealed:true,sitTimer:999,frame:0});
      }
    };
    channel.subscribe("obj_dead",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const d=msg.data;
      applyDead(d.id,d.type,d.x,d.y,true);
    });
    channel.subscribe("dia_hit",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const o=gs.current.worldObjs.find(x=>x.id===msg.data.id);
      if(o&&msg.data.hp>0&&msg.data.hp<o.hp)o.hp=msg.data.hp;
    });
    const sendSync=()=>{
      const s=gs.current;
      if(!s.ready)return;
      const bh=s.worldObjs.find(o=>o.type==="blackhole");
      const dia=s.worldObjs.find(o=>o.type==="diablo");
      channel.publish("sync",{
        dead:Array.from(s._dead||[]).slice(-50),
        bh:bh?{slot:bh.slot,hp:bh.hp}:null,
        dia:dia?{id:dia.id,hp:dia.hp}:null,
        bhClosed:(s._bhClosedSlot===undefined)?null:s._bhClosedSlot,
      });
    };
    window.__fikfukSync=sendSync;
    channel.subscribe("sync",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const s=gs.current;
      const d=msg.data;
      (d.dead||[]).forEach(id=>{
        if(!(s._dead&&s._dead.has(id)))applyDead(id,null,0,0,false);
      });
      const bh=s.worldObjs.find(o=>o.type==="blackhole");
      if(bh&&d.bh&&d.bh.slot===bh.slot&&d.bh.hp<bh.hp)bh.hp=Math.max(1,d.bh.hp);
      if(d.bhClosed!==null&&d.bhClosed!==undefined){
        s._bhClosedSlot=d.bhClosed;
        if(bh&&bh.slot===d.bhClosed)s.worldObjs=s.worldObjs.filter(o=>o.type!=="blackhole");
      }
      const dia=s.worldObjs.find(o=>o.type==="diablo"&&d.dia&&o.id===d.dia.id);
      if(dia&&d.dia.hp>0&&d.dia.hp<dia.hp)dia.hp=d.dia.hp;
    });
    channel.subscribe("blackhole_hit",(msg)=>{''',
'subscribers + sync')

# 5. newcomers get a sync from existing players
swap('channel.presence.subscribe("enter",(m)=>addRemoteCat(m.data,m.clientId));',
'''channel.presence.subscribe("enter",(m)=>{
      addRemoteCat(m.data,m.clientId);
      setTimeout(()=>{try{sendSync();}catch(e){}},500+Math.random()*2500);
    });''',
'sync on join')

# 6. periodic sync (one interval only)
swap('myCat._updatePresence=()=>channel.presence.update(myPresenceData());',
'''myCat._updatePresence=()=>channel.presence.update(myPresenceData());
    if(window.__fikfukSyncIv)clearInterval(window.__fikfukSyncIv);
    window.__fikfukSyncIv=setInterval(()=>{try{sendSync();}catch(e){}},45000);''',
'periodic sync')

if failures == 0:
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('\nAll steps applied. File written.')
else:
    print('\n' + str(failures) + ' step(s) failed. NOTHING was written. Paste this output.')