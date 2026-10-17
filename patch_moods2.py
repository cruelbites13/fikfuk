content = open('src/App.jsx', encoding='utf-8').read()

old = '''        drawBubble(ctx,{...c,x:sx,y:sy},P);
      });
      if(laser.active&&!s.camDrag)drawLaser(ctx,laser.sx,laser.sy,s.trail,s.frame);'''

new = '''        drawBubble(ctx,{...c,x:sx,y:sy},P);
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
        }
      });
      if(laser.active&&!s.camDrag)drawLaser(ctx,laser.sx,laser.sy,s.trail,s.frame);'''

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Mood emoji draw added')
else:
    print('FAILED')
    idx = content.find('drawBubble(ctx,{...c')
    print(repr(content[idx:idx+150]))