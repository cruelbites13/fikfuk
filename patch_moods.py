content = open('src/App.jsx', encoding='utf-8').read()

# 1. Add mood update logic in the cat update loop, after Patates movement block
old = '''        cat.vx*=0.86;cat.vy*=0.86;
        const spd2=Math.hypot(cat.vx,cat.vy);
        if(spd2>3.5){cat.vx=cat.vx/spd2*3.5;cat.vy=cat.vy/spd2*3.5;}
        if(!cat.isSys||cat.sysType==="patates"){cat.x+=cat.vx;cat.y+=cat.vy;}'''

new = '''        // ── mood system ──
        if(cat.isOwn&&!cat.isSys){
          if(!cat.mood) cat.mood="neutral";
          if(!cat.moodTimer) cat.moodTimer=0;
          cat.moodTimer--;
          // scared - near diablo
          const nearDiablo=s.worldObjs.find(o=>o.type==="diablo"&&Math.hypot(cat.x-o.x,cat.y-o.y)<200);
          if(nearDiablo){ cat.mood="scared"; cat.moodTimer=180; }
          // happy - caught a mouse recently
          if(cat._boostTimer>0){ cat.mood="happy"; }
          // friendly - near another player cat
          const nearPlayer=s.cats.find(c=>!c.isOwn&&!c.isSys&&!c.isGhost&&Math.hypot(cat.x-c.x,cat.y-c.y)<100);
          if(nearPlayer&&cat.mood==="neutral"){ cat.mood="friendly"; cat.moodTimer=300; }
          // reset to neutral
          if(cat.moodTimer<=0) cat.mood="neutral";
        }

        cat.vx*=0.86;cat.vy*=0.86;
        const spd2=Math.hypot(cat.vx,cat.vy);
        if(spd2>3.5){cat.vx=cat.vx/spd2*3.5;cat.vy=cat.vy/spd2*3.5;}
        if(!cat.isSys||cat.sysType==="patates"){cat.x+=cat.vx;cat.y+=cat.vy;}'''

if old in content:
    content = content.replace(old, new)
    print('Mood logic added')
else:
    print('FAILED - mood logic')

# 2. Draw mood emoji above own cat
old2 = '''        drawCat(ctx,sx,sy,P,c.frame,c.pal,c.flip,c.state,c.grabbed,c.isOwn,c.isSys,c.idle);
        drawBubble(ctx,{...c,x:sx,y:sy},P);'''

new2 = '''        drawCat(ctx,sx,sy,P,c.frame,c.pal,c.flip,c.state,c.grabbed,c.isOwn,c.isSys,c.idle);
        drawBubble(ctx,{...c,x:sx,y:sy},P);
        // mood indicator above own cat
        if(c.isOwn&&!c.isSys&&c.mood&&c.mood!=="neutral"){
          const moodEmoji={scared:"😱",happy:"😻",friendly:"😸"}[c.mood]||"";
          if(moodEmoji){
            ctx.save();
            ctx.font="14px serif";
            ctx.globalAlpha=0.85;
            ctx.fillText(moodEmoji,sx+2*P,sy-12);
            ctx.restore();
          }
        }'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Mood emoji draw added')
else:
    print('FAILED - mood draw')

open('src/App.jsx', 'w', encoding='utf-8').write(content)