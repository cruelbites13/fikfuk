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

# 1. remember when a joystick press began and how far it moved
swap('s.joystick={active:true,startX:sx,startY:sy,dx:0,dy:0};',
     's.joystick={active:true,startX:sx,startY:sy,dx:0,dy:0,t0:Date.now(),maxD:0};',
     'joystick records start time')

swap('      s.joystick.dy=sy-s.joystick.startY;',
'''      s.joystick.dy=sy-s.joystick.startY;
      s.joystick.maxD=Math.max(s.joystick.maxD||0,Math.hypot(s.joystick.dx,s.joystick.dy));''',
     'joystick tracks max distance')

# 2. on release, a short barely-moved press is a chirp
swap('''    s.camDrag=null;
    s.joystick={active:false,startX:0,startY:0,dx:0,dy:0};
    if(!s.laserOn){s.laser.active=false;s.trail=[];}
  },[]);''',
'''    s.camDrag=null;
    {
      const j=s.joystick;
      if(j&&j.active&&j.t0&&Date.now()-j.t0<250&&(j.maxD||0)<12&&!s.laserOn)doChirp();
    }
    s.joystick={active:false,startX:0,startY:0,dx:0,dy:0};
    if(!s.laserOn){s.laser.active=false;s.trail=[];}
  },[]);''',
     'chirp on short tap')

# 3. chirp helpers (function declarations, only use refs)
swap('  const onPointerDown=useCallback((e)=>{',
'''  function applyChirp(x,y,fromId){
    const s=gs.current;
    s._chirps=s._chirps||[];
    s._chirps.push({x,y,life:60});
    s.cats.forEach(c=>{
      if(c.id===fromId||c.isGhost)return;
      if(Math.hypot(c.x-x,c.y-y)<250&&c.confessions.length){
        c.revealAlpha=Math.max(c.revealAlpha,0.9);
        c.revealTimer=100;
      }
    });
  }
  function doChirp(){
    const s=gs.current;
    const myCat=s.cats.find(c=>c.id===s.myId);
    if(!myCat||myCat.idle)return;
    const now=Date.now();
    if(now-(s._lastChirp||0)<3000)return;
    s._lastChirp=now;
    applyChirp(myCat.x,myCat.y,myCat.id);
    channelRef.current?.publish("chirp",{x:Math.round(myCat.x),y:Math.round(myCat.y)});
  }
  const onPointerDown=useCallback((e)=>{''',
     'chirp helpers')

# 4. receive other players' chirps
swap('channel.subscribe("blackhole_hit",(msg)=>{',
'''channel.subscribe("chirp",(msg)=>{
      if(msg.clientId===clientId.current)return;
      applyChirp(msg.data.x,msg.data.y,msg.clientId);
    });
    channel.subscribe("blackhole_hit",(msg)=>{''',
     'chirp subscriber')

# 5. draw ripples + purr circles
swap('for(let gy=0;gy<H;gy+=4){ctx.fillStyle="rgba(0,0,0,0.06)";ctx.fillRect(0,gy,W,2);}',
'''for(let gy=0;gy<H;gy+=4){ctx.fillStyle="rgba(0,0,0,0.06)";ctx.fillRect(0,gy,W,2);}

      // chirp ripples
      if(s._chirps&&s._chirps.length){
        s._chirps=s._chirps.filter(c=>c.life>0);
        s._chirps.forEach(c=>{
          c.life--;
          const{sx:rcx,sy:rcy}=w2s(c.x+5.5*P,c.y+5*P);
          const prog=1-c.life/60;
          ctx.save();
          ctx.globalAlpha=Math.max(0,(1-prog)*0.5);
          ctx.strokeStyle="rgba(255,220,150,1)";ctx.lineWidth=2;
          ctx.beginPath();ctx.arc(rcx,rcy,prog*250,0,Math.PI*2);ctx.stroke();
          ctx.restore();
        });
      }

      // purr circles: 3+ sitting cats close together
      if(s.frame%20===0){
        const sit=s.cats.filter(c=>!c.isSys&&!c.isGhost&&!c.idle&&c.state==="sit");
        s.cats.forEach(c=>{
          c._purr=sit.includes(c)&&sit.filter(o=>o!==c&&Math.hypot(o.x-c.x,o.y-c.y)<130).length>=2;
        });
      }
      if(!window.__fikfukPurr)window.__fikfukPurr=()=>gs.current.cats.filter(c=>c._purr).map(c=>c.name);
      s.cats.forEach(c=>{
        if(!c._purr)return;
        if(c.confessions.length){c.revealAlpha=Math.min(1,c.revealAlpha+0.03);c.revealTimer=40;}
        const{sx:ppx,sy:ppy}=w2s(c.x,c.y);
        if(ppx<-80||ppx>W+80||ppy<-80||ppy>H+80)return;
        ctx.save();
        ctx.globalAlpha=0.18+Math.sin(s.frame*0.08)*0.06;
        ctx.fillStyle="rgba(255,200,120,1)";
        ctx.beginPath();ctx.arc(ppx+5.5*P,ppy+5*P,48,0,Math.PI*2);ctx.fill();
        ctx.restore();
      });''',
     'ripples + purr circles')

if failures == 0:
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('\nAll steps applied. File written.')
else:
    print('\n' + str(failures) + ' step(s) failed. NOTHING was written. Paste this output.')