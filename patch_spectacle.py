content = open('src/App.jsx', encoding='utf-8').read()

# 1. Add floating confession particles array to game state
old = '''  const gs           = useRef({
    cats:[], worldObjs:[],
    laser:{sx:-999,sy:-999,active:false},
    trail:[], stars:[], frame:0,
    drag:null, laserOn:false, myId:null, ready:false,
    cam:{x:0,y:0},
    camDrag:null,
  });'''

new = '''  const gs           = useRef({
    cats:[], worldObjs:[],
    laser:{sx:-999,sy:-999,active:false},
    trail:[], stars:[], frame:0,
    drag:null, laserOn:false, myId:null, ready:false,
    cam:{x:0,y:0},
    camDrag:null,
    particles:[], // floating confession particles for reset spectacle
  });'''

if old in content:
    content = content.replace(old, new)
    print('Particles array added')
else:
    print('FAILED - particles array')

# 2. Replace reset countdown logic with spectacle version
old2 = '''    const iv=setInterval(()=>{
      setResetIn(nextResetMs());
      if(nextResetMs()<=1000){
        localStorage.removeItem("fikfuk_s");
        channelRef.current?.publish("reset",{});
      }
    },1000);
    return()=>clearInterval(iv);'''

new2 = '''    const iv=setInterval(()=>{
      const ms=nextResetMs();
      setResetIn(ms);
      const s=gs.current;
      const myCat=s.cats.find(c=>c.id===s.myId);

      // 30s before - spawn floating confession particles
      if(ms<=30000&&ms>29000&&myCat){
        s.cats.filter(c=>!c.isSys&&c.confessions.length>0).forEach(cat=>{
          cat.confessions.forEach((text,i)=>{
            s.particles.push({
              text,
              x:cat.x, y:cat.y,
              vx:(Math.random()-0.5)*0.5,
              vy:-0.8-Math.random()*0.5,
              alpha:1, life:600,
              delay:i*20,
            });
          });
        });
      }

      if(ms<=1000){
        localStorage.removeItem("fikfuk_s");
        channelRef.current?.publish("reset",{});
      }
    },1000);
    return()=>clearInterval(iv);'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Spectacle timer added')
else:
    print('FAILED - spectacle timer')

# 3. Add spectacle sky overlay and particles to draw loop
old3 = '''      const skyCol=getSkyColor();
      ctx.fillStyle=skyCol;ctx.fillRect(0,0,W,H);
      // night overlay - more stars visible at night
      if(isNight()){
        ctx.fillStyle="rgba(0,0,10,0.15)";ctx.fillRect(0,0,W,H);
      }'''

new3 = '''      const skyCol=getSkyColor();
      ctx.fillStyle=skyCol;ctx.fillRect(0,0,W,H);
      // night overlay - more stars visible at night
      if(isNight()){
        ctx.fillStyle="rgba(0,0,10,0.15)";ctx.fillRect(0,0,W,H);
      }
      // ── reset spectacle overlay ──
      const msLeft=nextResetMs();
      if(msLeft<60000){
        // sky goes red
        const redAlpha=Math.min(0.6,(60000-msLeft)/60000*0.6);
        ctx.fillStyle=`rgba(180,0,0,${redAlpha})`;
        ctx.fillRect(0,0,W,H);
      }
      if(msLeft<10000){
        // big countdown center screen
        const secs=Math.ceil(msLeft/1000);
        ctx.save();
        ctx.font=`${Math.min(80,W/4)}px ${ff}`;
        ctx.fillStyle=`rgba(255,50,50,${0.8+Math.sin(Date.now()*0.01)*0.2})`;
        ctx.textAlign="center";
        ctx.fillText(secs,W/2,H/2);
        ctx.font=`14px ${ff}`;
        ctx.fillStyle="rgba(255,150,150,0.7)";
        ctx.fillText("the world resets",W/2,H/2+50);
        ctx.restore();
      }'''

if old3 in content:
    content = content.replace(old3, new3)
    print('Spectacle sky added')
else:
    print('FAILED - spectacle sky')

# 4. Update and draw particles in game loop, after stars
old4 = '''      for(let gy=0;gy<H;gy+=4){ctx.fillStyle="rgba(0,0,0,0.06)";ctx.fillRect(0,gy,W,2);}'''

new4 = '''      for(let gy=0;gy<H;gy+=4){ctx.fillStyle="rgba(0,0,0,0.06)";ctx.fillRect(0,gy,W,2);}

      // ── floating confession particles ──
      s.particles=s.particles.filter(p=>p.life>0);
      s.particles.forEach(p=>{
        if(p.delay>0){p.delay--;return;}
        p.life--;
        p.x+=p.vx; p.y+=p.vy;
        p.alpha=Math.min(1,p.life/60);
        const{sx:px,sy:py}=w2s(p.x,p.y);
        ctx.save();
        ctx.globalAlpha=p.alpha*0.85;
        ctx.font=`7px ${ff}`;
        ctx.fillStyle=`hsl(${10+Math.random()*20},80%,75%)`;
        ctx.fillText(p.text,px,py);
        ctx.restore();
      });'''

if old4 in content:
    content = content.replace(old4, new4)
    print('Particles draw added')
else:
    print('FAILED - particles draw')

# 5. White flash on actual reset
old5 = '''      if(ms<=1000){
        localStorage.removeItem("fikfuk_s");
        channelRef.current?.publish("reset",{});
      }'''

new5 = '''      if(ms<=1000){
        localStorage.removeItem("fikfuk_s");
        channelRef.current?.publish("reset",{});
        // white flash
        gs.current._flashTimer=30;
      }'''

if old5 in content:
    content = content.replace(old5, new5)
    print('Flash trigger added')
else:
    print('FAILED - flash trigger')

# 6. Draw white flash
old6 = '''      // ── reset spectacle overlay ──'''

new6 = '''      // ── white flash on reset ──
      if(s._flashTimer>0){
        s._flashTimer--;
        ctx.fillStyle=`rgba(255,255,255,${s._flashTimer/30})`;
        ctx.fillRect(0,0,W,H);
      }
      // ── reset spectacle overlay ──'''

if old6 in content:
    content = content.replace(old6, new6)
    print('White flash draw added')
else:
    print('FAILED - white flash draw')

open('src/App.jsx', 'w', encoding='utf-8').write(content)