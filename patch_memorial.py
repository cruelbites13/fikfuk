content = open('src/App.jsx', encoding='utf-8').read()

# 1. Add paw print spawning in Patates movement block
old = '''          // reveal confession when any player cat is near
          if(myCat){
            const pdx=myCat.x-cat.x,pdy=myCat.y-cat.y;
            const pdist=Math.hypot(pdx,pdy);
            if(pdist<140){
              cat.revealAlpha=Math.min(1,cat.revealAlpha+0.04);
              cat.revealTimer=100;
              // cycle through his messages slowly
              cat._cycleTimer=(cat._cycleTimer||0)+1;
              if(cat._cycleTimer>240){
                cat._cycleTimer=0;
                const idx=(cat._msgIdx||0);
                const next=(idx+1)%cat.confessions.length;
                cat._msgIdx=next;
                const msg=cat.confessions[next];
                cat.confessions=cat.confessions.filter(m=>m!==msg);
                cat.confessions.push(msg);
              }
            }
          }'''

new = '''          // reveal confession when any player cat is near
          if(myCat){
            const pdx=myCat.x-cat.x,pdy=myCat.y-cat.y;
            const pdist=Math.hypot(pdx,pdy);
            if(pdist<140){
              cat.revealAlpha=Math.min(1,cat.revealAlpha+0.04);
              cat.revealTimer=100;
              cat._cycleTimer=(cat._cycleTimer||0)+1;
              if(cat._cycleTimer>240){
                cat._cycleTimer=0;
                const idx=(cat._msgIdx||0);
                const next=(idx+1)%cat.confessions.length;
                cat._msgIdx=next;
                const msg=cat.confessions[next];
                cat.confessions=cat.confessions.filter(m=>m!==msg);
                cat.confessions.push(msg);
              }
            }
          }
          // leave glowing paw prints while moving
          if(cat.state==="run"){
            cat._pawTimer=(cat._pawTimer||0)+1;
            if(cat._pawTimer>40){
              cat._pawTimer=0;
              toAdd.push({
                type:"pawprint",
                id:`paw_${Date.now()}_${Math.random().toString(36).slice(2,5)}`,
                x:cat.x+Math.random()*10-5,
                y:cat.y+10+Math.random()*6,
                life:600, alpha:0, frame:0,
              });
            }
          }'''

if old in content:
    content = content.replace(old, new)
    print('Paw print spawning added')
else:
    print('FAILED - paw spawning')

# 2. Add paw print update in world obj loop
old2 = '''        // Breadcrumb - fades out over time
        if(obj.type==="breadcrumb"){
          obj.life=(obj.life||0)-1;
          if(obj.life<=0) toRemove.add(obj.id);
        }'''

new2 = '''        // Breadcrumb - fades out over time
        if(obj.type==="breadcrumb"){
          obj.life=(obj.life||0)-1;
          if(obj.life<=0) toRemove.add(obj.id);
        }
        // Paw prints - fade in then out
        if(obj.type==="pawprint"){
          obj.life--;
          if(obj.life<=0) toRemove.add(obj.id);
          else if(obj.life>500) obj.alpha=Math.min(0.7,(600-obj.life)/100*0.7);
          else obj.alpha=Math.max(0,obj.life/500*0.7);
        }'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Paw print update added')
else:
    print('FAILED - paw update')

# 3. Draw paw prints
old3 = '''        if(obj.type==="letter"){'''

new3 = '''        if(obj.type==="pawprint"){
          if(obj.alpha>0){
            const{sx:px,sy:py}=w2s(obj.x,obj.y);
            if(px>-20&&px<W+20&&py>-20&&py<H+20){
              ctx.save();
              ctx.globalAlpha=obj.alpha;
              ctx.fillStyle="#e07b39";
              // main pad
              ctx.beginPath();ctx.ellipse(px,py,5,4,0,0,Math.PI*2);ctx.fill();
              // toe beans
              [[-4,-5],[0,-6],[4,-5],[-6,-3],[6,-3]].forEach(([tx,ty])=>{
                ctx.beginPath();ctx.ellipse(px+tx,py+ty,2,2,0,0,Math.PI*2);ctx.fill();
              });
              ctx.restore();
            }
          }
        }
        if(obj.type==="letter"){'''

if old3 in content:
    content = content.replace(old3, new3)
    print('Paw print draw added')
else:
    print('FAILED - paw draw')

# 4. Also add paw print minimap dots
old4 = '''      // blackhole on minimap'''

new4 = '''      // patates paw prints on minimap (subtle)
      s.worldObjs.filter(o=>o.type==="pawprint"&&o.alpha>0.3).forEach(o=>{
        const pmx=MM_X+(o.x/WORLD_W)*MM_W;
        const pmy=MM_Y+(o.y/WORLD_H)*MM_H;
        ctx.fillStyle=`rgba(224,123,57,${o.alpha*0.5})`;
        ctx.fillRect(pmx,pmy,1,1);
      });
      // blackhole on minimap'''

if old4 in content:
    content = content.replace(old4, new4)
    print('Paw print minimap added')
else:
    print('FAILED - paw minimap')

open('src/App.jsx', 'w', encoding='utf-8').write(content)