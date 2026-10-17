content = open('src/App.jsx', encoding='utf-8').read()

# 1. Add letter drop button to HUD alongside confess button
old = '''          {!showInput&&(
            <button className="hbtn" onClick={()=>{if(cooldown===0)setShowInput(true);}}
              style={{fontSize:8,background:cooldown>0?"rgba(40,40,60,0.6)":"transparent",border:`2px solid ${cooldown>0?"rgba(255,50,50,0.25)":"#ff3232"}`,color:cooldown>0?"rgba(255,100,100,0.4)":"#ff6666",padding:"10px 14px",boxShadow:cooldown>0?"none":"0 0 14px rgba(255,50,50,0.35)",cursor:cooldown>0?"not-allowed":"pointer"}}>
              {cooldown>0?`${cooldown}s`:"+ confess"}
            </button>
          )}'''

new = '''          {!showInput&&(
            <button className="hbtn" onClick={()=>{if(cooldown===0)setShowInput(true);}}
              style={{fontSize:8,background:cooldown>0?"rgba(40,40,60,0.6)":"transparent",border:`2px solid ${cooldown>0?"rgba(255,50,50,0.25)":"#ff3232"}`,color:cooldown>0?"rgba(255,100,100,0.4)":"#ff6666",padding:"10px 14px",boxShadow:cooldown>0?"none":"0 0 14px rgba(255,50,50,0.35)",cursor:cooldown>0?"not-allowed":"pointer"}}>
              {cooldown>0?`${cooldown}s`:"+ confess"}
            </button>
          )}
          <button className="hbtn" onClick={()=>setShowLetterInput(true)}
            style={{fontSize:8,background:"transparent",border:"2px solid rgba(100,150,255,0.45)",color:"rgba(150,180,255,0.7)",padding:"10px 13px"}}>
            ✉ letter
          </button>'''

if old in content:
    content = content.replace(old, new)
    print('Letter button added')
else:
    print('FAILED - letter button')

# 2. Add showLetterInput state
old2 = "  const [cooldown,    setCooldown]    = useState(0);"
new2 = "  const [cooldown,    setCooldown]    = useState(0);\n  const [showLetterInput, setShowLetterInput] = useState(false);\n  const [letterVal, setLetterVal] = useState(\"\");"

if old2 in content:
    content = content.replace(old2, new2)
    print('Letter state added')
else:
    print('FAILED - letter state')

# 3. Add letter input panel and letter markers in world
old3 = '''      {showInput&&(
          <div style={{position:"fixed",bottom:0,left:0,right:0,background:"rgba(8,8,16,0.97)",border:"2px solid #ff3232",borderBottom:"none",boxShadow:"0 0 30px rgba(255,50,50,0.25)",padding:"16px",zIndex:30,display:"flex",flexDirection:"column",gap:10}}>'''

new3 = '''      {showLetterInput&&(
          <div style={{position:"fixed",bottom:0,left:0,right:0,background:"rgba(8,8,16,0.97)",border:"2px solid rgba(100,150,255,0.6)",borderBottom:"none",boxShadow:"0 0 30px rgba(100,150,255,0.2)",padding:"16px",zIndex:30,display:"flex",flexDirection:"column",gap:10}}>
            <span style={{fontSize:8,color:"rgba(150,180,255,0.9)"}}>// drop a letter here</span>
            <input autoFocus maxLength={40} value={letterVal}
              onChange={e=>setLetterVal(e.target.value)}
              onKeyDown={e=>{
                if(e.key==="Enter"&&letterVal.trim()){
                  const s=gs.current;
                  const myCat=s.cats.find(c=>c.id===s.myId);
                  if(myCat){
                    const letter={id:Date.now()+"_l",x:myCat.x,y:myCat.y-50,text:letterVal.trim().slice(0,40),life:1800,alpha:0};
                    s.worldObjs.push({type:"letter",...letter,frame:0});
                    channelRef.current?.publish("letter",{letter});
                  }
                  setLetterVal("");setShowLetterInput(false);
                }
              }}
              placeholder="leave a message for strangers... (40 chars)"
              style={{background:"transparent",border:"none",borderBottom:"1px solid rgba(100,150,255,0.35)",color:"#fff",fontFamily:ff,fontSize:9,padding:"6px 2px",outline:"none",width:"100%"}}
            />
            <div style={{fontSize:7,color:"rgba(255,255,255,0.22)"}}>→ dropped at your cat's location · anyone can find it</div>
            <div style={{display:"flex",gap:8,justifyContent:"flex-end"}}>
              <button onClick={()=>setShowLetterInput(false)} style={{background:"transparent",border:"1px solid rgba(255,255,255,0.15)",color:"rgba(255,255,255,0.35)",fontFamily:ff,fontSize:7,padding:"6px 10px",cursor:"pointer"}}>cancel</button>
              <button onClick={()=>{
                if(letterVal.trim()){
                  const s=gs.current;
                  const myCat=s.cats.find(c=>c.id===s.myId);
                  if(myCat){
                    const letter={id:Date.now()+"_l",x:myCat.x,y:myCat.y-50,text:letterVal.trim().slice(0,40),life:1800,alpha:0};
                    s.worldObjs.push({type:"letter",...letter,frame:0});
                    channelRef.current?.publish("letter",{letter});
                  }
                  setLetterVal("");setShowLetterInput(false);
                }
              }} style={{background:"rgba(100,150,255,0.15)",border:"1px solid rgba(100,150,255,0.6)",color:"rgba(150,180,255,0.9)",fontFamily:ff,fontSize:7,padding:"6px 12px",cursor:"pointer"}}>drop ✉</button>
            </div>
          </div>
        )}

      {showInput&&(
          <div style={{position:"fixed",bottom:0,left:0,right:0,background:"rgba(8,8,16,0.97)",border:"2px solid #ff3232",borderBottom:"none",boxShadow:"0 0 30px rgba(255,50,50,0.25)",padding:"16px",zIndex:30,display:"flex",flexDirection:"column",gap:10}}>'''

if old3 in content:
    content = content.replace(old3, new3)
    print('Letter input panel added')
else:
    print('FAILED - letter panel')

# 4. Subscribe to letter messages
old4 = '''    channel.subscribe("wall",(msg)=>{
      if(msg.clientId===clientId.current)return;
      addToWall(msg.data.entry.text);
    });'''

new4 = '''    channel.subscribe("wall",(msg)=>{
      if(msg.clientId===clientId.current)return;
      addToWall(msg.data.entry.text);
    });

    channel.subscribe("letter",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const l=msg.data.letter;
      gs.current.worldObjs.push({type:"letter",...l,frame:0,alpha:0});
    });'''

if old4 in content:
    content = content.replace(old4, new4)
    print('Letter subscribe added')
else:
    print('FAILED - letter subscribe')

# 5. Draw letters in world
old5 = '''        if(obj.type==="breadcrumb"){
          const alpha=Math.min(1,(obj.life/60))*0.9;
          ctx.save();ctx.globalAlpha=alpha;
          ctx.font=`7px ${ff}`;
          const tw=ctx.measureText(obj.text).width;
          ctx.fillStyle="rgba(10,20,10,0.85)";
          ctx.strokeStyle="#44ff44";ctx.lineWidth=1;
          rrect(ctx,sx-tw/2-8,sy-16,tw+16,22,3);
          ctx.fill();ctx.stroke();
          ctx.fillStyle="#aaffaa";
          ctx.fillText(obj.text,sx-tw/2,sy-1);
          ctx.restore();
        }'''

new5 = '''        if(obj.type==="breadcrumb"){
          const alpha=Math.min(1,(obj.life/60))*0.9;
          ctx.save();ctx.globalAlpha=alpha;
          ctx.font=`7px ${ff}`;
          const tw=ctx.measureText(obj.text).width;
          ctx.fillStyle="rgba(10,20,10,0.85)";
          ctx.strokeStyle="#44ff44";ctx.lineWidth=1;
          rrect(ctx,sx-tw/2-8,sy-16,tw+16,22,3);
          ctx.fill();ctx.stroke();
          ctx.fillStyle="#aaffaa";
          ctx.fillText(obj.text,sx-tw/2,sy-1);
          ctx.restore();
        }
        if(obj.type==="letter"){
          obj.alpha=Math.min(1,(obj.alpha||0)+0.01);
          obj.life=(obj.life||1800)-1;
          if(obj.life<=0){toRemove.add(obj.id);return;}
          const la=obj.alpha*Math.min(1,obj.life/120);
          ctx.save();ctx.globalAlpha=la;
          // envelope icon
          ctx.font="16px serif";ctx.fillText("✉",sx-8,sy+8);
          // on hover proximity - show text
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
        }'''

if old5 in content:
    content = content.replace(old5, new5)
    print('Letter draw added')
else:
    print('FAILED - letter draw')

open('src/App.jsx', 'w', encoding='utf-8').write(content)