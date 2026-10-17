content = open('src/App.jsx', encoding='utf-8').read()

# 1. Add reaction and tag state
old = "  const [showLetterInput, setShowLetterInput] = useState(false);\n  const [letterVal, setLetterVal] = useState(\"\");"
new = """  const [showLetterInput, setShowLetterInput] = useState(false);
  const [letterVal, setLetterVal] = useState("");
  const [showTagPicker, setShowTagPicker] = useState(false);
  const [myTag, setMyTag] = useState("");"""

if old in content:
    content = content.replace(old, new)
    print('Tag state added')
else:
    print('FAILED - tag state')

# 2. Add reaction subscribe to Ably
old2 = '''    channel.subscribe("blackhole_hit",(msg)=>{'''
new2 = '''    channel.subscribe("reaction",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const s=gs.current;
      const targetCat=s.cats.find(c=>c.id===msg.data.targetId);
      if(targetCat){
        if(!targetCat._reactions) targetCat._reactions=[];
        targetCat._reactions.push({
          emoji:msg.data.emoji, life:180,
          x:Math.random()*30-15, vy:-0.5-Math.random()*0.3,
        });
      }
    });

    channel.subscribe("tag",(msg)=>{
      if(msg.clientId===clientId.current)return;
      const s=gs.current;
      const cat=s.cats.find(c=>c.id===msg.clientId);
      if(cat) cat._tag=msg.data.tag;
    });

    channel.subscribe("blackhole_hit",(msg)=>{'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Reaction/tag subscribe added')
else:
    print('FAILED - subscribe')

# 3. Add reaction buttons to panel (for non-own, non-sys cats)
old3 = '''            <div style={{fontSize:7,color:"rgba(255,255,255,0.18)",textAlign:"right"}}>tap outside to close</div>'''

new3 = '''            {panel&&!panel.isOwn&&!panel.isSys&&(
              <div style={{display:"flex",gap:8,flexWrap:"wrap",marginTop:4}}>
                {["❤️","😢","👀","🐾","😂","🤯"].map(emoji=>(
                  <button key={emoji} onClick={()=>{
                    const s=gs.current;
                    const targetCat=s.cats.find(c=>c.id===panel.catId);
                    if(targetCat){
                      if(!targetCat._reactions) targetCat._reactions=[];
                      targetCat._reactions.push({emoji,life:180,x:Math.random()*30-15,vy:-0.5-Math.random()*0.3});
                      channelRef.current?.publish("reaction",{targetId:panel.catId,emoji});
                    }
                    setPanel(null);
                  }} style={{background:"rgba(255,255,255,0.08)",border:"1px solid rgba(255,255,255,0.15)",fontSize:16,padding:"4px 8px",cursor:"pointer",borderRadius:4}}>
                    {emoji}
                  </button>
                ))}
              </div>
            )}
            <div style={{fontSize:7,color:"rgba(255,255,255,0.18)",textAlign:"right"}}>tap outside to close</div>'''

if old3 in content:
    content = content.replace(old3, new3)
    print('Reaction buttons added')
else:
    print('FAILED - reaction buttons')

# 4. Draw reactions and tags on cats
old4 = '''        // mood indicator above own cat
        if(c.isOwn&&!c.isSys&&c.mood&&c.mood!=="neutral"){'''

new4 = '''        // draw reactions floating above cat
        if(c._reactions&&c._reactions.length>0){
          c._reactions=c._reactions.filter(r=>r.life>0);
          c._reactions.forEach(r=>{
            r.life--;
            r._y=(r._y||0)+r.vy;
            const ra=Math.min(1,r.life/60);
            ctx.save();
            ctx.globalAlpha=ra;
            ctx.font="16px serif";
            ctx.fillText(r.emoji,sx+5.5*P+r.x,sy-20+r._y);
            ctx.restore();
          });
        }
        // draw cat tag
        if(c._tag){
          ctx.save();
          ctx.font="14px serif";
          ctx.globalAlpha=0.9;
          ctx.fillText(c._tag,sx+5.5*P+8,sy-8);
          ctx.restore();
        }
        // mood indicator above own cat
        if(c.isOwn&&!c.isSys&&c.mood&&c.mood!=="neutral"){'''

if old4 in content:
    content = content.replace(old4, new4)
    print('Reactions/tags draw added')
else:
    print('FAILED - draw')

# 5. Add tag button to toolbar
old5 = '''          <button className="hbtn" onClick={()=>setShowLetterInput(true)}
            style={{fontSize:8,background:"transparent",border:"2px solid rgba(100,150,255,0.45)",color:"rgba(150,180,255,0.7)",padding:"10px 13px"}}>
            ✉ letter
          </button>'''

new5 = '''          <button className="hbtn" onClick={()=>setShowLetterInput(true)}
            style={{fontSize:8,background:"transparent",border:"2px solid rgba(100,150,255,0.45)",color:"rgba(150,180,255,0.7)",padding:"10px 13px"}}>
            ✉ letter
          </button>
          <button className="hbtn" onClick={()=>setShowTagPicker(true)}
            style={{fontSize:8,background:"transparent",border:"2px solid rgba(255,200,100,0.45)",color:"rgba(255,200,100,0.7)",padding:"10px 13px"}}>
            {myTag||"tag"}
          </button>'''

if old5 in content:
    content = content.replace(old5, new5)
    print('Tag button added')
else:
    print('FAILED - tag button')

# 6. Add tag picker panel
old6 = '''      {showLetterInput&&('''

new6 = '''      {showTagPicker&&(
          <div style={{position:"fixed",bottom:0,left:0,right:0,background:"rgba(8,8,16,0.97)",border:"2px solid rgba(255,200,100,0.6)",borderBottom:"none",padding:"16px",zIndex:30,display:"flex",flexDirection:"column",gap:12}}>
            <span style={{fontSize:8,color:"rgba(255,200,100,0.9)"}}>// pick your tag</span>
            <div style={{display:"flex",gap:10,flexWrap:"wrap"}}>
              {["😺","😸","😹","😻","😼","😽","🙀","😿","😾","🐱","🐈","✨","💀","👻","🔥","💫","🌙","⭐","❤️","💔"].map(e=>(
                <button key={e} onClick={()=>{
                  setMyTag(e);
                  setShowTagPicker(false);
                  const s=gs.current;
                  const myCat=s.cats.find(c=>c.id===s.myId);
                  if(myCat){
                    myCat._tag=e;
                    channelRef.current?.publish("tag",{tag:e});
                  }
                }} style={{fontSize:20,background:"rgba(255,255,255,0.06)",border:"1px solid rgba(255,200,100,0.2)",padding:"6px",cursor:"pointer",borderRadius:4}}>
                  {e}
                </button>
              ))}
            </div>
            <div style={{display:"flex",gap:8,justifyContent:"flex-end"}}>
              {myTag&&<button onClick={()=>{
                setMyTag("");setShowTagPicker(false);
                const s=gs.current;
                const myCat=s.cats.find(c=>c.id===s.myId);
                if(myCat){myCat._tag="";channelRef.current?.publish("tag",{tag:""});}
              }} style={{background:"transparent",border:"1px solid rgba(255,100,100,0.3)",color:"rgba(255,100,100,0.5)",fontFamily:ff,fontSize:7,padding:"6px 10px",cursor:"pointer"}}>remove tag</button>}
              <button onClick={()=>setShowTagPicker(false)} style={{background:"transparent",border:"1px solid rgba(255,255,255,0.15)",color:"rgba(255,255,255,0.35)",fontFamily:ff,fontSize:7,padding:"6px 10px",cursor:"pointer"}}>cancel</button>
            </div>
          </div>
        )}

      {showLetterInput&&('''

if old6 in content:
    content = content.replace(old6, new6)
    print('Tag picker panel added')
else:
    print('FAILED - tag picker')

open('src/App.jsx', 'w', encoding='utf-8').write(content)