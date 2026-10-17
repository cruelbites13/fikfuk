content = open('src/App.jsx', encoding='utf-8').read()

old = '''        } else if(cat.isOwn&&!cat.isSys){
          cat.wanderTimer--;
          if(cat.wanderTimer<=0){
            cat.wanderAngle+=(Math.random()-0.5)*1.5;
            cat.wanderTimer=80+Math.random()*140;
            cat.state=Math.random()>0.45?"sit":"run";
          }
          if(cat.state==="run"){cat.vx+=Math.cos(cat.wanderAngle)*0.03;cat.vy+=Math.sin(cat.wanderAngle)*0.03;cat.flip=cat.vx<0;}
        }'''

new = '''        } else if(cat.isOwn&&!cat.isSys){
          cat.wanderTimer--;
          if(cat.wanderTimer<=0){
            cat.wanderAngle+=(Math.random()-0.5)*1.5;
            cat.wanderTimer=80+Math.random()*140;
            cat.state=Math.random()>0.45?"sit":"run";
          }
          if(cat.state==="run"){cat.vx+=Math.cos(cat.wanderAngle)*0.03;cat.vy+=Math.sin(cat.wanderAngle)*0.03;cat.flip=cat.vx<0;}
        } else if(cat.sysType==="patates"){
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

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Patates movement added')
else:
    print('FAILED')