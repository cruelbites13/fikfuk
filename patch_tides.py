content = open('src/App.jsx', encoding='utf-8').read()

# 1. Add tide logic after scanlines draw
old = '''      for(let gy=0;gy<H;gy+=4){ctx.fillStyle="rgba(0,0,0,0.06)";ctx.fillRect(0,gy,W,2);}'''

new = '''      for(let gy=0;gy<H;gy+=4){ctx.fillStyle="rgba(0,0,0,0.06)";ctx.fillRect(0,gy,W,2);}

      // ── Confession Tide ──
      // tide sweeps across world every 15 min (54000 frames)
      const TIDE_PERIOD = 54000;
      const tidePhase = s.frame % TIDE_PERIOD;
      const tideActive = tidePhase < WORLD_W / 2; // active for first half
      if(tideActive){
        // world x position of tide wave front
        const tideWorldX = tidePhase * 2;
        const tideSx = tideWorldX - cam.x;
        // draw wave
        const tideGrad = ctx.createLinearGradient(tideSx-80,0,tideSx+40,0);
        tideGrad.addColorStop(0,"rgba(100,180,255,0)");
        tideGrad.addColorStop(0.5,"rgba(150,210,255,0.12)");
        tideGrad.addColorStop(1,"rgba(100,180,255,0)");
        ctx.fillStyle=tideGrad;
        ctx.fillRect(tideSx-80,0,120,H);
        // reveal confessions of cats the tide touches
        s.cats.forEach(cat=>{
          const{sx:csx}=w2s(cat.x,cat.y);
          if(Math.abs(csx-tideSx)<60&&cat.confessions.length>0){
            cat.revealAlpha=Math.min(1,cat.revealAlpha+0.08);
            cat.revealTimer=90;
          }
        });
      }'''

if old in content:
    content = content.replace(old, new)
    print('Confession Tides added')
else:
    print('FAILED - tides')

open('src/App.jsx', 'w', encoding='utf-8').write(content)