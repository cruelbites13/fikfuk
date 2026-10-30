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

swap('''      // apply removals and additions''',
'''      // ── shared-clock paths: same position for every player ──
      {
        const tSec=(sharedNow()-EPOCH_ANCHOR)/1000;
        const PATHS={
          ufo:{ax:1100,ay:600,per:540},
          diablo:{ax:1500,ay:1000,per:720},
          wildcat:{ax:350,ay:250,per:120},
          human:{ax:700,ay:450,per:300},
        };
        s.worldObjs.forEach(obj=>{
          const P0=PATHS[obj.type];
          if(!P0)return;
          if(obj.bx===undefined){
            obj.bx=obj.x;obj.by=obj.y;
            const r=mulberry32(hashStr("path:"+obj.id));
            obj.ph1=r()*Math.PI*2;obj.ph2=r()*Math.PI*2;
            obj.k=0.8+r()*0.5; // per-object speed variety
          }
          const w=Math.PI*2/(P0.per/obj.k);
          const nx=obj.bx+P0.ax*Math.sin(w*tSec+obj.ph1);
          const ny=obj.by+P0.ay*Math.sin(w*1.31*tSec+obj.ph2);
          obj.vx=P0.ax*w*Math.cos(w*tSec+obj.ph1); // used for facing
          obj.flip=obj.vx<0;
          obj.x=Math.max(500,Math.min(WORLD_W-500,nx));
          obj.y=Math.max(500,Math.min(WORLD_H-500,ny));
        });
        if(!window.__fikfukLive){
          window.__fikfukLive=()=>s.worldObjs
            .filter(o=>PATHS[o.type])
            .map(o=>o.type+" "+Math.round(o.x)+","+Math.round(o.y));
        }
      }

      // apply removals and additions''',
'shared-clock path block')

if failures == 0:
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('\nAll steps applied. File written.')
else:
    print('\n' + str(failures) + ' step(s) failed. NOTHING was written. Paste this output.')