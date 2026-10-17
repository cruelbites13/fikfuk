content = open('src/App.jsx', encoding='utf-8').read()

old = '''        } else if(cat.sysType==="patates"){
          // gentle, careful wandering - short bursts then long pauses
          cat.wanderTimer--;
          if(cat.wanderTimer<=0){
            if(cat.state==="sit"){
              cat.wanderAngle=Math.random()*Math.PI*2;
              cat.wanderTimer=20+Math.random()*30;
              cat.state="run";
            } else {
              cat.wanderTimer=180+Math.random()*240;
              cat.state="sit";
            }
          }
          if(cat.state==="run"){
            cat.vx+=Math.cos(cat.wanderAngle)*0.02;
            cat.vy+=Math.sin(cat.wanderAngle)*0.02;
            cat.flip=cat.vx<0;
          }
        }'''

new = '''        } else if(cat.sysType==="patates"){
          // gentle, careful wandering - short bursts then long pauses
          cat.wanderTimer--;
          if(cat.wanderTimer<=0){
            if(cat.state==="sit"){
              cat.wanderAngle=Math.random()*Math.PI*2;
              cat.wanderTimer=20+Math.random()*30;
              cat.state="run";
            } else {
              cat.wanderTimer=180+Math.random()*240;
              cat.state="sit";
            }
          }
          if(cat.state==="run"){
            cat.vx+=Math.cos(cat.wanderAngle)*0.02;
            cat.vy+=Math.sin(cat.wanderAngle)*0.02;
            cat.flip=cat.vx<0;
          }
          // reveal confession when any player cat is near
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
          }
        }'''

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Patates confession trigger added')
else:
    print('FAILED')