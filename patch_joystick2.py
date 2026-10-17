content = open('src/App.jsx', encoding='utf-8').read()

# Fix joystick draw - only show when active
old = '''      // ── joystick draw ──
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

new = '''      // ── joystick draw (only when active) ──
      const joy=s.joystick;
      if(joy.active){
        const JX=joy.startX, JY=joy.startY, JR=50;
        const stickX=Math.min(JR*0.8,Math.max(-JR*0.8,joy.dx));
        const stickY=Math.min(JR*0.8,Math.max(-JR*0.8,joy.dy));
        ctx.save();
        // outer ring
        ctx.globalAlpha=0.3;
        ctx.strokeStyle="#ffffff";ctx.lineWidth=2;
        ctx.beginPath();ctx.arc(JX,JY,JR,0,Math.PI*2);ctx.stroke();
        ctx.globalAlpha=0.08;
        ctx.fillStyle="#ffffff";
        ctx.beginPath();ctx.arc(JX,JY,JR,0,Math.PI*2);ctx.fill();
        // inner stick
        ctx.globalAlpha=0.7;
        ctx.fillStyle="#ffffff";
        ctx.beginPath();ctx.arc(JX+stickX,JY+stickY,20,0,Math.PI*2);ctx.fill();
        ctx.restore();
      }'''

if old in content:
    content = content.replace(old, new)
    print('Joystick draw fixed')
else:
    print('FAILED - draw')

# Fix joystick zone - trigger anywhere, not just left side
# Works on both mobile and PC (mouse drag)
old2 = '''    // joystick zone - anywhere on left 40% of screen below 40% height
    const cv=canvasRef.current;
    if(cv&&sx<cv.width*0.4&&sy>cv.height*0.4&&!s.laserOn){
      s.joystick={active:true,startX:sx,startY:sy,dx:0,dy:0};
      return;
    }'''

new2 = '''    // joystick - anywhere on canvas when laser is off and not hitting a cat
    const cv=canvasRef.current;
    if(cv&&!s.laserOn&&!cat){
      s.joystick={active:true,startX:sx,startY:sy,dx:0,dy:0};
      return;
    }'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Joystick zone fixed')
else:
    print('FAILED - zone')

# Fix joystick move - simpler tracking
old3 = '''    // handle joystick touch
    if(s.joystick?.active&&e.touches){
      const r=canvasRef.current.getBoundingClientRect();
      // find the touch that started in joystick zone
      for(let t of e.touches){
        const tx=t.clientX-r.left;
        const ty=t.clientY-r.top;
        const distFromStart=Math.hypot(tx-s.joystick.startX,ty-s.joystick.startY);
        if(distFromStart<150){
          s.joystick.dx=tx-s.joystick.startX;
          s.joystick.dy=ty-s.joystick.startY;
          return;
        }
      }
    }'''

new3 = '''    // joystick move tracking
    if(s.joystick?.active){
      s.joystick.dx=sx-s.joystick.startX;
      s.joystick.dy=sy-s.joystick.startY;
      // if laser is on, don't use joystick
      if(s.laserOn) return;
      return;
    }'''

if old3 in content:
    content = content.replace(old3, new3)
    print('Joystick move fixed')
else:
    print('FAILED - move')

# Fix joystick force - clamp movement properly
old4 = '''          if(joy.active&&(Math.abs(joy.dx)>5||Math.abs(joy.dy)>5)){
            // joystick overrides wander
            const jlen=Math.hypot(joy.dx,joy.dy);
            const jspd=Math.min(jlen/30,1)*3;
            cat.vx+=(joy.dx/jlen)*jspd*0.15;
            cat.vy+=(joy.dy/jlen)*jspd*0.15;
            cat.flip=joy.dx<0;
            cat.state="run";
            cat.wanderTimer=60;'''

new4 = '''          if(joy.active&&Math.hypot(joy.dx,joy.dy)>8){
            const jlen=Math.hypot(joy.dx,joy.dy);
            const jclamped=Math.min(jlen,80);
            const jspd=(jclamped/80)*2.5;
            cat.vx+=(joy.dx/jlen)*jspd*0.2;
            cat.vy+=(joy.dy/jlen)*jspd*0.2;
            cat.flip=joy.dx<0;
            cat.state="run";
            cat.wanderTimer=60;'''

if old4 in content:
    content = content.replace(old4, new4)
    print('Joystick force fixed')
else:
    print('FAILED - force')

open('src/App.jsx', 'w', encoding='utf-8').write(content)