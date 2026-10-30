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

# 1. publish moves only when moving, 4/s, never while hidden
swap('''        if(now-moveThrottle.current>100){
          moveThrottle.current=now;
          channelRef.current.publish("move",{x:myCat.x,y:myCat.y,vx:myCat.vx,vy:myCat.vy,flip:myCat.flip,state:myCat.state});
        }''',
'''        if(now-moveThrottle.current>250){
          const lm=s._lastMove||{x:-1e5,y:-1e5,state:""};
          const moved=Math.hypot(myCat.x-lm.x,myCat.y-lm.y)>3||myCat.state!==lm.state;
          if(moved&&!document.hidden){
            moveThrottle.current=now;
            s._lastMove={x:myCat.x,y:myCat.y,state:myCat.state};
            window.__fikfukPubN=(window.__fikfukPubN||0)+1;
            channelRef.current.publish("move",{x:Math.round(myCat.x),y:Math.round(myCat.y),flip:myCat.flip,state:myCat.state});
          }
        }''',
'throttled move publishing')

# 2. receiver: set a glide target instead of snapping
swap('cat.x=d.x;cat.y=d.y;cat.vx=d.vx;cat.vy=d.vy;cat.flip=d.flip;cat.state=d.state;',
'''cat._tx=d.x;cat._ty=d.y;cat.flip=d.flip;cat.state=d.state;
      if(Math.hypot(d.x-cat.x,d.y-cat.y)>600){cat.x=d.x;cat.y=d.y;}
      cat.vx=0;cat.vy=0;''',
'move receiver sets target')

# 3. remote cats glide toward their target every frame
swap('''        if(cat.grabbed){cat.frame++;cat.state="sit";return;}
        cat.frame++;''',
'''        if(cat.grabbed){cat.frame++;cat.state="sit";return;}
        cat.frame++;
        if(!cat.isOwn&&!cat.isSys&&cat._tx!==undefined){
          cat.x+=(cat._tx-cat.x)*0.25;
          cat.y+=(cat._ty-cat.y)*0.25;
          cat.vx=0;cat.vy=0;
        }''',
'remote cats glide')

# 4. debug counter
swap('window.__fikfukSync=sendSync;',
'window.__fikfukSync=sendSync;\n    window.__fikfukPub=()=>window.__fikfukPubN||0;',
'publish counter')

if failures == 0:
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('\nAll steps applied. File written.')
else:
    print('\n' + str(failures) + ' step(s) failed. NOTHING was written. Paste this output.')