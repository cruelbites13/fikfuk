content = open('src/App.jsx', encoding='utf-8').read()

# 1. Add whisper subscribe to Ably
old = '''    channel.subscribe("reaction",(msg)=>{'''

new = '''    channel.subscribe("whisper",(msg)=>{
      if(msg.clientId===clientId.current)return;
      // only show if it's addressed to me
      if(msg.data.targetId!==clientId.current)return;
      const s=gs.current;
      const myCat=s.cats.find(c=>c.id===s.myId);
      if(myCat){
        s._whisperMsg={text:msg.data.text,life:300,alpha:0};
      }
    });

    channel.subscribe("reaction",(msg)=>{'''

if old in content:
    content = content.replace(old, new)
    print('Whisper subscribe added')
else:
    print('FAILED - whisper subscribe')

# 2. Add whisper proximity detection in cat update loop
old2 = '''        // ── mood system ──
        if(cat.isOwn&&!cat.isSys){'''

new2 = '''        // ── whisper proximity ──
        if(cat.isOwn&&!cat.isSys){
          const nearCat=s.cats.find(c=>!c.isOwn&&!c.isSys&&!c.isGhost&&Math.hypot(cat.x-c.x,cat.y-c.y)<50);
          if(nearCat){
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
            cat._whisperTarget=null;
          }
        }

        // ── mood system ──
        if(cat.isOwn&&!cat.isSys){'''

if old in content:
    content = content.replace(old2, new2)
    print('Whisper proximity added')
else:
    print('FAILED - whisper proximity')

# 3. Draw whisper progress ring and received message
old3 = '''      if(laser.active&&!s.camDrag)drawLaser(ctx,laser.sx,laser.sy,s.trail,s.frame);'''

new3 = '''      if(laser.active&&!s.camDrag)drawLaser(ctx,laser.sx,laser.sy,s.trail,s.frame);

      // ── whisper UI ──
      const myCatW=s.cats.find(c=>c.id===s.myId);
      if(myCatW&&myCatW._whisperTimer>0){
        const{sx:wx,sy:wy}=w2s(myCatW.x,myCatW.y);
        const pct=myCatW._whisperTimer/180;
        ctx.save();
        ctx.strokeStyle=`rgba(150,180,255,${0.6+pct*0.4})`;
        ctx.lineWidth=2;
        ctx.beginPath();
        ctx.arc(wx+5.5*P,wy+5*P,28,-Math.PI/2,-Math.PI/2+pct*Math.PI*2);
        ctx.stroke();
        ctx.font=`6px ${ff}`;
        ctx.fillStyle="rgba(150,180,255,0.7)";
        ctx.fillText("whispering...",wx-15,wy-30);
        ctx.restore();
      }
      // received whisper
      if(s._whisperMsg){
        s._whisperMsg.life--;
        s._whisperMsg.alpha=Math.min(1,s._whisperMsg.life/60);
        if(s._whisperMsg.life<=0){s._whisperMsg=null;}
        else {
          ctx.save();
          ctx.globalAlpha=s._whisperMsg.alpha;
          ctx.font=`8px ${ff}`;
          const tw=ctx.measureText(s._whisperMsg.text).width;
          ctx.fillStyle="rgba(8,12,30,0.95)";
          ctx.strokeStyle="rgba(150,180,255,0.8)";ctx.lineWidth=1.5;
          rrect(ctx,W/2-tw/2-12,H/2-60,tw+24,32,4);
          ctx.fill();ctx.stroke();
          ctx.fillStyle="rgba(180,210,255,0.95)";
          ctx.fillText("✉ "+s._whisperMsg.text,W/2-tw/2,H/2-40);
          ctx.restore();
        }
      }
      // sent whisper indicator
      if(s._whisperSent){
        s._whisperSent.life--;
        s._whisperSent.alpha=Math.min(1,s._whisperSent.life/30);
        if(s._whisperSent.life<=0){s._whisperSent=null;}
        else {
          ctx.save();
          ctx.globalAlpha=s._whisperSent.alpha;
          ctx.font=`7px ${ff}`;
          ctx.fillStyle="rgba(150,180,255,0.8)";
          ctx.fillText(s._whisperSent.text,W/2-40,H/2-80);
          ctx.restore();
        }
      }'''

if old3 in content:
    content = content.replace(old3, new3)
    print('Whisper UI draw added')
else:
    print('FAILED - whisper draw')

open('src/App.jsx', 'w', encoding='utf-8').write(content)