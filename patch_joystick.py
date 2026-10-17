content = open('src/App.jsx', encoding='utf-8').read()

# 1. Fix territory sit timer - raise threshold so normal wandering doesn't trigger it
old = '''          const spd3=Math.hypot(cat.vx,cat.vy);
          if(spd3<0.3){
            cat._sitTimer=(cat._sitTimer||0)+1;
            if(cat._sitTimer===120){
              cat._territory={x:cat.x,y:cat.y,radius:80,name:cat.name,palBody:cat.pal.body};
              s._myTerritory=cat._territory;
            }
          } else {
            cat._sitTimer=0;
          }'''

new = '''          const spd3=Math.hypot(cat.vx,cat.vy);
          if(spd3<0.1&&cat.state==="sit"){
            cat._sitTimer=(cat._sitTimer||0)+1;
            if(cat._sitTimer===180){
              cat._territory={x:cat.x,y:cat.y,radius:80,name:cat.name,palBody:cat.pal.body};
              s._myTerritory=cat._territory;
            }
          } else {
            cat._sitTimer=0;
          }'''

if old in content:
    content = content.replace(old, new)
    print('Sit timer fixed')
else:
    print('FAILED - sit timer')

# 2. Add joystick state to gs ref
old2 = '''    particles:[],
  });'''

new2 = '''    particles:[],
    joystick:{active:false,startX:0,startY:0,dx:0,dy:0},
  });'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Joystick state added')
else:
    print('FAILED - joystick state')

# 3. Apply joystick force to own cat in update loop
old3 = '''        } else if(cat.isOwn&&!cat.isSys){
          cat.wanderTimer--;
          if(cat.wanderTimer<=0){
            cat.wanderAngle+=(Math.random()-0.5)*1.5;
            cat.wanderTimer=80+Math.random()*140;
            cat.state=Math.random()>0.45?"sit":"run";
          }
          if(cat.state==="run"){cat.vx+=Math.cos(cat.wanderAngle)*0.03;cat.vy+=Math.sin(cat.wanderAngle)*0.03;cat.flip=cat.vx<0;}
        }'''

new3 = '''        } else if(cat.isOwn&&!cat.isSys){
          const joy=s.joystick;
          if(joy.active&&(Math.abs(joy.dx)>5||Math.abs(joy.dy)>5)){
            // joystick overrides wander
            const jlen=Math.hypot(joy.dx,joy.dy);
            const jspd=Math.min(jlen/30,1)*3;
            cat.vx+=(joy.dx/jlen)*jspd*0.15;
            cat.vy+=(joy.dy/jlen)*jspd*0.15;
            cat.flip=joy.dx<0;
            cat.state="run";
            cat.wanderTimer=60;
          } else {
            cat.wanderTimer--;
            if(cat.wanderTimer<=0){
              cat.wanderAngle+=(Math.random()-0.5)*1.5;
              cat.wanderTimer=80+Math.random()*140;
              cat.state=Math.random()>0.45?"sit":"run";
            }
            if(cat.state==="run"){cat.vx+=Math.cos(cat.wanderAngle)*0.03;cat.vy+=Math.sin(cat.wanderAngle)*0.03;cat.flip=cat.vx<0;}
          }
        }'''

if old3 in content:
    content = content.replace(old3, new3)
    print('Joystick force added')
else:
    print('FAILED - joystick force')

# 4. Draw joystick on screen
old4 = '''      if(laser.active&&!s.camDrag)drawLaser(ctx,laser.sx,laser.sy,s.trail,s.frame);'''

new4 = '''      if(laser.active&&!s.camDrag)drawLaser(ctx,laser.sx,laser.sy,s.trail,s.frame);

      // ── joystick draw ──
      const joy=s.joystick;
      const JX=80,JY=H-100,JR=45;
      ctx.save();
      // base ring
      ctx.globalAlpha=0.25;
      ctx.strokeStyle="#ffffff";ctx.lineWidth=2;
      ctx.beginPath();ctx.arc(JX,JY,JR,0,Math.PI*2);ctx.stroke();
      ctx.globalAlpha=0.08;
      ctx.fillStyle="#ffffff";
      ctx.beginPath();ctx.arc(JX,JY,JR,0,Math.PI*2);ctx.fill();
      // stick
      const stickX=joy.active?Math.min(JR*0.7,Math.max(-JR*0.7,joy.dx*0.6)):0;
      const stickY=joy.active?Math.min(JR*0.7,Math.max(-JR*0.7,joy.dy*0.6)):0;
      ctx.globalAlpha=joy.active?0.7:0.3;
      ctx.fillStyle="#ffffff";
      ctx.beginPath();ctx.arc(JX+stickX,JY+stickY,18,0,Math.PI*2);ctx.fill();
      ctx.restore();'''

if old4 in content:
    content = content.replace(old4, new4)
    print('Joystick draw added')
else:
    print('FAILED - joystick draw')

# 5. Handle joystick touch input - separate touch zone (left side of screen)
old5 = '''  const onPointerDown=useCallback((e)=>{
    if(phaseRef.current!=="play")return;
    const{sx,sy}=getPos(e);
    const s=gs.current;
    const cat=catAtScreen(sx,sy);
    const now=Date.now();'''

new5 = '''  const onPointerDown=useCallback((e)=>{
    if(phaseRef.current!=="play")return;
    const{sx,sy}=getPos(e);
    const s=gs.current;
    // joystick zone - left quarter of screen, bottom half
    const cv=canvasRef.current;
    if(cv&&sx<cv.width*0.35&&sy>cv.height*0.5){
      s.joystick={active:true,startX:sx,startY:sy,dx:0,dy:0,touchId:e.touches?.[0]?.identifier??-1};
      return;
    }
    const cat=catAtScreen(sx,sy);
    const now=Date.now();'''

if old5 in content:
    content = content.replace(old5, new5)
    print('Joystick touch down added')
else:
    print('FAILED - joystick down')

# 6. Update joystick on move
old6 = '''  const onPointerMove=useCallback((e)=>{
    if(phaseRef.current!=="play")return;
    const{sx,sy}=getPos(e);
    const s=gs.current;
    if(s.drag){'''

new6 = '''  const onPointerMove=useCallback((e)=>{
    if(phaseRef.current!=="play")return;
    const s=gs.current;
    // handle joystick touch
    if(s.joystick?.active&&e.touches){
      for(let t of e.touches){
        if(t.identifier===s.joystick.touchId){
          const r=canvasRef.current.getBoundingClientRect();
          s.joystick.dx=t.clientX-r.left-s.joystick.startX;
          s.joystick.dy=t.clientY-r.top-s.joystick.startY;
          return;
        }
      }
    }
    const{sx,sy}=getPos(e);
    if(s.drag){'''

if old6 in content:
    content = content.replace(old6, new6)
    print('Joystick move added')
else:
    print('FAILED - joystick move')

# 7. Reset joystick on pointer up
old7 = '''  const onPointerUp=useCallback(()=>{
    const s=gs.current;
    if(s.drag){const cat=s.cats.find(c=>c.id===s.drag.catId);if(cat)cat.grabbed=false;s.drag=null;}
    s.camDrag=null;
    if(!s.laserOn){s.laser.active=false;s.trail=[];}
  },[]);'''

new7 = '''  const onPointerUp=useCallback(()=>{
    const s=gs.current;
    if(s.drag){const cat=s.cats.find(c=>c.id===s.drag.catId);if(cat)cat.grabbed=false;s.drag=null;}
    s.camDrag=null;
    s.joystick={active:false,startX:0,startY:0,dx:0,dy:0};
    if(!s.laserOn){s.laser.active=false;s.trail=[];}
  },[]);'''

if old7 in content:
    content = content.replace(old7, new7)
    print('Joystick reset added')
else:
    print('FAILED - joystick reset')

open('src/App.jsx', 'w', encoding='utf-8').write(content)