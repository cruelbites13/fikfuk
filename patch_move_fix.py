content = open('src/App.jsx', encoding='utf-8').read()

# 1. Fix TDZ: resolve pointer position BEFORE the joystick check
old = '''    // joystick move tracking
    if(s.joystick?.active){
      s.joystick.dx=sx-s.joystick.startX;
      s.joystick.dy=sy-s.joystick.startY;
      // if laser is on, don't use joystick
      if(s.laserOn) return;
      return;
    }
    const{sx,sy}=getPos(e);'''

new = '''    const{sx,sy}=getPos(e);
    if(s.joystick?.active){
      s.joystick.dx=sx-s.joystick.startX;
      s.joystick.dy=sy-s.joystick.startY;
      return;
    }'''

if old in content:
    content = content.replace(old, new)
    print('1 TDZ fix applied')
else:
    print('FAILED 1 - TDZ')

# 2. Owned cat sits when there is no input (no auto-wander)
old2 = '''          } else {
            cat.wanderTimer--;
            if(cat.wanderTimer<=0){
              cat.wanderAngle+=(Math.random()-0.5)*1.5;
              cat.wanderTimer=80+Math.random()*140;
              cat.state=Math.random()>0.45?"sit":"run";
            }
            if(cat.state==="run"){cat.vx+=Math.cos(cat.wanderAngle)*0.03;cat.vy+=Math.sin(cat.wanderAngle)*0.03;cat.flip=cat.vx<0;}
          }'''

new2 = '''          } else {
            cat.state="sit";
          }'''

if old2 in content:
    content = content.replace(old2, new2)
    print('2 Idle sit applied')
else:
    print('FAILED 2 - idle sit')

# 3. Camera follows own cat every frame (paused while panning or dragging)
old3 = '''      const{laser,cam}=s;
      const myCat=s.cats.find(c=>c.id===s.myId);'''

new3 = '''      const{laser,cam}=s;
      const myCat=s.cats.find(c=>c.id===s.myId);
      if(myCat&&!s.camDrag&&!s.drag){
        const camTx=Math.max(0,Math.min(WORLD_W-W,myCat.x+5.5*P-W/2));
        const camTy=Math.max(0,Math.min(WORLD_H-H,myCat.y+5*P-H/2));
        cam.x+=(camTx-cam.x)*0.1;
        cam.y+=(camTy-cam.y)*0.1;
      }'''

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('3 Camera follow applied')
else:
    print('FAILED 3 - camera follow')

# 4. Pan = right mouse button or two fingers (cancels joystick)
old4 = '''    const cat=catAtScreen(sx,sy);
    // joystick: tap anywhere when laser off and not tapping a cat'''

new4 = '''    if(e.button===2||(e.touches&&e.touches.length>=2)){
      s.joystick={active:false,startX:0,startY:0,dx:0,dy:0};
      s.camDrag={lastSx:sx,lastSy:sy};
      return;
    }
    const cat=catAtScreen(sx,sy);
    // joystick: tap anywhere when laser off and not tapping a cat'''

if old4 in content:
    content = content.replace(old4, new4)
    print('4 Pan gesture applied')
else:
    print('FAILED 4 - pan gesture')

# 5. Stop the right-click menu so right-drag can pan
old5 = 'onMouseDown={onPointerDown} onMouseMove={onPointerMove}'
new5 = 'onContextMenu={e=>e.preventDefault()} onMouseDown={onPointerDown} onMouseMove={onPointerMove}'

if old5 in content and 'onContextMenu' not in content:
    content = content.replace(old5, new5, 1)
    print('5 Context menu blocked')
else:
    print('FAILED 5 - context menu (or already present)')

open('src/App.jsx', 'w', encoding='utf-8').write(content)