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

swap('''        if(!window.__fikfukLive){
          window.__fikfukLive=()=>s.worldObjs
            .filter(o=>PATHS[o.type])
            .map(o=>o.type+" "+Math.round(o.x)+","+Math.round(o.y));
        }''',
'''        if(!window.__fikfukLive){
          window.__fikfukLive=()=>s.worldObjs
            .filter(o=>PATHS[o.type])
            .map(o=>o.type+" "+Math.round(o.x)+","+Math.round(o.y));
          // evaluate every path at one fixed time t (seconds since EPOCH_ANCHOR)
          window.__fikfukAt=(t)=>s.worldObjs
            .filter(o=>PATHS[o.type]&&o.bx!==undefined)
            .map(o=>{
              const p=PATHS[o.type];
              const w=Math.PI*2/(p.per/o.k);
              const x=Math.max(500,Math.min(WORLD_W-500,o.bx+p.ax*Math.sin(w*t+o.ph1)));
              const y=Math.max(500,Math.min(WORLD_H-500,o.by+p.ay*Math.sin(w*1.31*t+o.ph2)));
              return o.type+" "+Math.round(x)+","+Math.round(y);
            });
        }''',
'fixed-time debug helper')

if failures == 0:
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('\nApplied. File written.')
else:
    print('\nFAILED. NOTHING was written. Paste this output.')