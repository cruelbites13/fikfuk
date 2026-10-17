content = open('src/App.jsx', encoding='utf-8').read()

# Fix 1: Whisper timer should NOT block movement - remove the implicit stun
old = '''          if(nearCat){
            cat._whisperTimer=(cat._whisperTimer||0)+1;
            cat._whisperTarget=nearCat.id;
            if(cat._whisperTimer===180&&cat.confessions.length>0){
              // send whisper
              const text=cat.confessions[cat.confessions.length-1];
              channelRef.current?.publish("whisper",{targetId:nearCat.id,text});
              cat._whisperTimer=0;
              // show sent indicator
              s._whisperSent={text:"✉ whispered",life:120,alpha:1};
            }
          } else {
            cat._whisperTimer=0;
            cat._whisperTarget=null;'''

new = '''          if(nearCat){
            cat._whisperTimer=(cat._whisperTimer||0)+1;
            cat._whisperTarget=nearCat.id;
            // whisper sends silently - does NOT stun the cat
            if(cat._whisperTimer===300&&cat.confessions.length>0){
              const text=cat.confessions[cat.confessions.length-1];
              channelRef.current?.publish("whisper",{targetId:nearCat.id,text});
              cat._whisperTimer=0;
              s._whisperSent={text:"whispered",life:120,alpha:1};
            }
          } else {
            cat._whisperTimer=0;
            cat._whisperTarget=null;'''

if old in content:
    content = content.replace(old, new)
    print('Whisper stun fixed')
else:
    print('FAILED - whisper stun')

# Fix 2: Joystick touchId - store pointer position directly, not touchId
old2 = '''    // joystick zone - left quarter of screen, bottom half
    const cv=canvasRef.current;
    if(cv&&sx<cv.width*0.35&&sy>cv.height*0.5){
      s.joystick={active:true,startX:sx,startY:sy,dx:0,dy:0,touchId:e.touches?.[0]?.identifier??-1};
      return;
    }'''

new2 = '''    // joystick zone - left quarter of screen, bottom half
    const cv=canvasRef.current;
    if(cv&&sx<cv.width*0.35&&sy>cv.height*0.5){
      s.joystick={active:true,startX:sx,startY:sy,dx:0,dy:0};
      return;
    }'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Joystick touchId fix')
else:
    print('FAILED - joystick touchId')

# Fix 3: Joystick move - use position directly instead of touchId matching
old3 = '''    // handle joystick touch
    if(s.joystick?.active&&e.touches){
      for(let t of e.touches){
        if(t.identifier===s.joystick.touchId){
          const r=canvasRef.current.getBoundingClientRect();
          s.joystick.dx=t.clientX-r.left-s.joystick.startX;
          s.joystick.dy=t.clientY-r.top-s.joystick.startY;
          return;
        }
      }
    }'''

new3 = '''    // handle joystick touch
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

if old3 in content:
    content = content.replace(old3, new3)
    print('Joystick move tracking fixed')
else:
    print('FAILED - joystick move')

# Fix 4: Raise joystick zone detection - make it larger and always visible
old4 = '''    const cv=canvasRef.current;
    if(cv&&sx<cv.width*0.35&&sy>cv.height*0.5){
      s.joystick={active:true,startX:sx,startY:sy,dx:0,dy:0};
      return;
    }'''

new4 = '''    const cv=canvasRef.current;
    // joystick: anywhere on left 40% of screen below 40% height
    if(cv&&sx<cv.width*0.4&&sy>cv.height*0.4&&!s.laserOn){
      s.joystick={active:true,startX:sx,startY:sy,dx:0,dy:0};
      return;
    }'''

if old4 in content:
    content = content.replace(old4, new4)
    print('Joystick zone expanded')
else:
    print('FAILED - joystick zone')

open('src/App.jsx', 'w', encoding='utf-8').write(content)