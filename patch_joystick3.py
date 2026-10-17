content = open('src/App.jsx', encoding='utf-8').read()

old = '''    // joystick: anywhere on left 40% of screen below 40% height
    if(cv&&sx<cv.width*0.4&&sy>cv.height*0.4&&!s.laserOn){
      s.joystick={active:true,startX:sx,startY:sy,dx:0,dy:0};
      return;
    }
    const cat=catAtScreen(sx,sy);'''

new = '''    const cat=catAtScreen(sx,sy);
    // joystick: tap anywhere when laser off and not tapping a cat
    if(!cat&&!s.laserOn&&cv){
      s.joystick={active:true,startX:sx,startY:sy,dx:0,dy:0};
      return;
    }'''

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Joystick zone fixed')
else:
    print('FAILED')
    idx = content.find('s.joystick={active:true')
    print(repr(content[idx-200:idx+50]))