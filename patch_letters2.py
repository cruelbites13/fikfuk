content = open('src/App.jsx', encoding='utf-8').read()

old = '''          ctx.fillStyle="#aaffaa";
          ctx.fillText(obj.text,sx-tw/2,sy-1);
          ctx.restore();
        }
      });'''

new = '''          ctx.fillStyle="#aaffaa";
          ctx.fillText(obj.text,sx-tw/2,sy-1);
          ctx.restore();
        }
        if(obj.type==="letter"){
          obj.alpha=Math.min(1,(obj.alpha||0)+0.01);
          obj.life=(obj.life||1800)-1;
          if(obj.life<=0){toRemove.add(obj.id);}
          else {
            const la=obj.alpha*Math.min(1,obj.life/120);
            ctx.save();ctx.globalAlpha=la;
            ctx.font="16px serif";ctx.fillText("✉",sx-8,sy+8);
            const myCat2=gs.current.cats.find(c=>c.id===gs.current.myId);
            if(myCat2&&Math.hypot(myCat2.x-obj.x,myCat2.y-obj.y)<80){
              ctx.font=`7px ${ff}`;
              const tw=ctx.measureText(obj.text).width;
              ctx.fillStyle="rgba(8,12,30,0.9)";
              ctx.strokeStyle="rgba(100,150,255,0.7)";ctx.lineWidth=1;
              rrect(ctx,sx-tw/2-8,sy-30,tw+16,20,3);
              ctx.fill();ctx.stroke();
              ctx.fillStyle="rgba(150,180,255,0.95)";
              ctx.fillText(obj.text,sx-tw/2,sy-16);
            }
            ctx.restore();
          }
        }
      });'''

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Letter draw added')
else:
    print('FAILED')
    idx = content.find('#aaffaa')
    print(repr(content[idx:idx+150]))