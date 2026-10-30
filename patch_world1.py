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

# 1. shared clock + seeded RNG helpers
swap('''function getEpoch(){ return Math.floor((Date.now()-EPOCH_ANCHOR)/RESET_MS); }
function nextResetMs(){ return EPOCH_ANCHOR+(getEpoch()+1)*RESET_MS-Date.now(); }''',
'''// shared world clock: Ably server time minus this device's clock
let clockOffset=0;
function sharedNow(){ return Date.now()+clockOffset; }
function getEpoch(){ return Math.floor((sharedNow()-EPOCH_ANCHOR)/RESET_MS); }
function nextResetMs(){ return EPOCH_ANCHOR+(getEpoch()+1)*RESET_MS-sharedNow(); }

// seeded RNG: same epoch + same tag = same sequence on every device
function hashStr(str){
  let h1=0xdeadbeef,h2=0x41c6ce57;
  for(let i=0;i<str.length;i++){
    const ch=str.charCodeAt(i);
    h1=Math.imul(h1^ch,2654435761);
    h2=Math.imul(h2^ch,1597334677);
  }
  h1=Math.imul(h1^(h1>>>16),2246822507)^Math.imul(h2^(h2>>>13),3266489909);
  h2=Math.imul(h2^(h2>>>16),2246822507)^Math.imul(h1^(h1>>>13),3266489909);
  return (h1^h2)>>>0;
}
function mulberry32(a){
  return function(){
    a|=0; a=a+0x6D2B79F5|0;
    let t=Math.imul(a^(a>>>15),1|a);
    t=t+Math.imul(t^(t>>>7),61|t)^t;
    return ((t^(t>>>14))>>>0)/4294967296;
  };
}
function worldRng(tag){ return mulberry32(hashStr("fikfuk:"+getEpoch()+":"+tag)); }''',
'clock + seeded RNG helpers')

# 2. spawnObj: take an optional rng + slot, replace Math.random() inside it
start = content.find('function spawnObj(type, existingObjs){')
end = content.find('function generateWorldObjects(){')
if start == -1 or end == -1 or end < start:
    failures += 1
    print('FAILED - could not locate spawnObj / generateWorldObjects')
else:
    body = content[start:end]
    body = body.replace('function spawnObj(type, existingObjs){',
        'function spawnObj(type, existingObjs, rng, slot){\n  const R=rng||Math.random;', 1)
    body = body.replace('Math.random()', 'R()')
    old_id = 'const id=`${type}_${Date.now()}_${R().toString(36).slice(2,6)}`;'
    new_id = 'const id=(slot!=null)?`${type}_${getEpoch()}_${slot}`:`${type}_${Date.now()}_${Math.random().toString(36).slice(2,6)}`;'
    if old_id in body:
        body = body.replace(old_id, new_id)
        content = content[:start] + body + content[end:]
        print('OK     - spawnObj uses seeded rng')
    else:
        failures += 1
        print('FAILED - spawnObj id line not found')

# 3. generateWorldObjects: seeded, one stream per type
g_start = content.find('function generateWorldObjects(){')
g_marker = '  return objs;\n}'
g_end = content.find(g_marker, g_start)
if g_start == -1 or g_end == -1:
    failures += 1
    print('FAILED - generateWorldObjects not found')
else:
    g_end += len(g_marker)
    content = content[:g_start] + '''function generateWorldObjects(){
  const objs=[];
  ["ufo","fossil","wildcat","mouse","human","diablo"].forEach(type=>{
    const obj=spawnObj(type,objs,worldRng("init:"+type),0);
    if(obj)objs.push(obj);
  });
  return objs;
}''' + content[g_end:]
    print('OK     - generateWorldObjects seeded')

# 4. spawn effect: remember epoch + debug helper (must run BEFORE step 6)
swap('s.worldObjs=generateWorldObjects();',
'''s.worldObjs=generateWorldObjects();
      s._worldEpoch=getEpoch();
      s._initObjs=s.worldObjs.map(o=>({type:o.type,x:Math.round(o.x),y:Math.round(o.y)}));
      window.__fikfuk=()=>({epoch:getEpoch(),offsetMs:Math.round(clockOffset),initial:s._initObjs});''',
'epoch tracking + __fikfuk debug helper')

# 5. oracle position seeded
swap('''    const ocat=makeCat(
      1000+Math.random()*(WORLD_W-2000),
      1000+Math.random()*(WORLD_H-2000),''',
'''    const orng=worldRng("oracle");
    const ocat=makeCat(
      1000+orng()*(WORLD_W-2000),
      1000+orng()*(WORLD_H-2000),''',
'oracle seeded')

# 6. Ably server time -> clock offset; regenerate if our epoch was wrong
swap('''    ablyRef.current=ably;
    const channel=ably.channels.get(CHANNEL);''',
'''    ablyRef.current=ably;
    // sync to Ably's server clock so every player shares one world clock
    const _t0=Date.now();
    ably.time().then(serverT=>{
      const _t1=Date.now();
      clockOffset=serverT-(_t0+_t1)/2;
      const s=gs.current;
      if(s.ready&&getEpoch()!==s._worldEpoch){
        s.worldObjs=generateWorldObjects();
        s._worldEpoch=getEpoch();
        s._initObjs=s.worldObjs.map(o=>({type:o.type,x:Math.round(o.x),y:Math.round(o.y)}));
        const orc=s.cats.find(c=>c.sysType==="oracle");
        if(orc){const r=worldRng("oracle");orc.x=1000+r()*(WORLD_W-2000);orc.y=1000+r()*(WORLD_H-2000);}
      }
    }).catch(()=>{});
    const channel=ably.channels.get(CHANNEL);''',
'Ably clock offset')

if failures == 0:
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('\nAll steps applied. File written.')
else:
    print('\n' + str(failures) + ' step(s) failed. NOTHING was written. Paste this output.')