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

# 1. lines Patates says when fed
swap('const ORACLE_RESPONSES=[',
'''const FEED_LINES=["a mouse! thank u","my favorite, how did u know","purr purr, so good","i saved a spot for u","best treat ever","u always know what i like"];
const ORACLE_RESPONSES=[''',
'feed lines')

# 2. catching a mouse means carrying it
swap('myCat._boostTimer=300;',
'''myCat._boostTimer=300;
                myCat._carry=true;
                if(!s._carryHint){
                  s._carryHint=true;
                  s.particles.push({text:"bring it to patates",x:myCat.x-20,y:myCat.y-10,vx:0,vy:-0.4,alpha:1,life:200,delay:0});
                }''',
'carry a caught mouse')

# 3. feeding effect (local + broadcast)
swap('  function applyChirp(x,y,fromId){',
'''  function feedPatates(pat,mine){
    const s=gs.current;
    if(!mine&&pat._glowUntil&&pat._glowUntil>Date.now()+50000)return;
    const line=FEED_LINES[Math.floor(Math.random()*FEED_LINES.length)];
    pat._glowUntil=Date.now()+60000;
    for(let i=0;i<6;i++){
      s.particles.push({text:"<3",x:pat.x+4+i*6,y:pat.y-6,vx:(Math.random()-0.5)*0.6,vy:-0.5-Math.random()*0.5,alpha:1,life:150+i*10,delay:i*6});
    }
    s.particles.push({text:line,x:pat.x-10,y:pat.y-30,vx:0,vy:-0.25,alpha:1,life:260,delay:0});
    if(mine){
      const me=s.cats.find(c=>c.id===s.myId);
      if(me){me._glowUntil=Date.now()+60000;me._boostTimer=300;}
      channelRef.current?.publish("feed",{});
    }
  }
  function applyChirp(x,y,fromId){''',
'feedPatates function')

# 4. see other players feeding him
swap('channel.subscribe("chirp",(msg)=>{',
'''channel.subscribe("feed",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const pat=gs.current.cats.find(c=>c.sysType==="patates");
      if(pat)feedPatates(pat,false);
    });
    channel.subscribe("chirp",(msg)=>{''',
'feed subscriber')

# 5. delivery check each frame
swap('      // apply removals and additions',
'''      // patates feeding: deliver a carried mouse
      {
        const patF=s.cats.find(c=>c.sysType==="patates");
        if(patF&&myCat&&myCat._carry&&Math.hypot(myCat.x-patF.x,myCat.y-patF.y)<80){
          myCat._carry=false;
          feedPatates(patF,true);
        }
      }

      // apply removals and additions''',
'delivery check')

# 6. warm glow around fed cats
swap('// chirp ripples',
'''// glow around fed cats
      s.cats.forEach(c=>{
        if(!c._glowUntil||c._glowUntil<Date.now())return;
        const{sx:gx,sy:gy}=w2s(c.x,c.y);
        if(gx<-100||gx>W+100||gy<-100||gy>H+100)return;
        const left=(c._glowUntil-Date.now())/60000;
        ctx.save();
        ctx.globalAlpha=Math.min(0.35,left*0.5)*(0.8+Math.sin(s.frame*0.06)*0.2);
        const gg=ctx.createRadialGradient(gx+5.5*P,gy+5*P,4,gx+5.5*P,gy+5*P,60);
        gg.addColorStop(0,"rgba(255,190,110,1)");
        gg.addColorStop(1,"rgba(255,190,110,0)");
        ctx.fillStyle=gg;
        ctx.beginPath();ctx.arc(gx+5.5*P,gy+5*P,60,0,Math.PI*2);ctx.fill();
        ctx.restore();
      });

      // chirp ripples''',
'fed glow')

# 7. draw the carried mouse above your cat
swap('// mood indicator above own cat',
'''if(c.isOwn&&c._carry){drawMouse(ctx,sx-6,sy-18,c.frame,c.flip);}
        // mood indicator above own cat''',
'carried mouse icon')

# 8. minimap: patates and oracle get their own colour and letter
swap('const col=c.sysType==="privacy"?"#7777ff":"#44cc44";',
     'const col=c.sysType==="privacy"?"#7777ff":c.sysType==="patates"?"#ffaa44":c.sysType==="oracle"?"#cc44ff":"#44cc44";',
     'minimap colours')

swap('ctx.fillText(c.sysType==="privacy"?"P":"A",mx+3,my+2);',
     'ctx.fillText(c.sysType==="privacy"?"P":c.sysType==="patates"?"\\u2665":c.sysType==="oracle"?"?":"A",mx+3,my+2);',
     'minimap letters')

# 9. debug helper
swap('window.__fikfukSync=sendSync;',
'''window.__fikfukSync=sendSync;
    window.__fikfukMouse=()=>{const s=gs.current;const m=s.cats.find(c=>c.id===s.myId);if(m)m._carry=true;};''',
'debug helper')

if failures == 0:
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('\nAll steps applied. File written.')
else:
    print('\n' + str(failures) + ' step(s) failed. NOTHING was written. Paste this output.')