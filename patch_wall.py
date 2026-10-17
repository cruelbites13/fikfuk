content = open('src/App.jsx', encoding='utf-8').read()

# 1. Add wall confession store after SPAWN_LIMITS
old = 'const SPAWN_LIMITS = { ufo:2, fossil:3, wildcat:3, mouse:5, human:1, diablo:1 };'
new = '''const SPAWN_LIMITS = { ufo:2, fossil:3, wildcat:3, mouse:5, human:1, diablo:1 };

// ── Confession Wall ───────────────────────────────────────────────────────────
const WALL_X = 5000; // center of world
const WALL_Y = 1800; // north of spawn
const WALL_W = 600;
const WALL_H = 300;
// shared wall confessions (synced via Ably)
const wallConfessions = []; // {text, x, y, alpha, id}
function addToWall(text){
  if(wallConfessions.length>=20) wallConfessions.shift();
  wallConfessions.push({
    text: text.slice(0,28),
    x: 20+Math.random()*(WALL_W-160),
    y: 30+Math.random()*(WALL_H-50),
    alpha: 0,
    id: Date.now()+"_"+Math.random().toString(36).slice(2,6),
  });
}'''

if old in content:
    content = content.replace(old, new)
    print('Wall constants added')
else:
    print('FAILED - wall constants')

# 2. Draw the wall in world objects section
old2 = '''      s.worldObjs.forEach(obj=>{
        const{sx,sy}=w2s(obj.x,obj.y);
        if(sx<-100||sx>W+100||sy<-100||sy>H+200)return;'''

new2 = '''      // ── Draw Confession Wall ──
      const wallSx=WALL_X-cam.x-WALL_W/2;
      const wallSy=WALL_Y-cam.y-WALL_H/2;
      if(wallSx>-WALL_W&&wallSx<W&&wallSy>-WALL_H&&wallSy<H){
        ctx.save();
        // stone wall base
        ctx.fillStyle="#1a1510";
        ctx.fillRect(wallSx,wallSy,WALL_W,WALL_H);
        // stone texture lines
        ctx.strokeStyle="#2a2018";ctx.lineWidth=1;
        for(let wy=0;wy<WALL_H;wy+=30) ctx.strokeRect(wallSx,wallSy+wy,WALL_W,30);
        for(let wx=0;wx<WALL_W;wx+=60) ctx.strokeRect(wallSx+wx,wallSy,60,WALL_H);
        // border
        ctx.strokeStyle="#3a3028";ctx.lineWidth=3;
        ctx.strokeRect(wallSx,wallSy,WALL_W,WALL_H);
        // title
        ctx.font=`7px ${ff}`;ctx.fillStyle="rgba(255,200,100,0.5)";
        ctx.fillText("// wall of confessions",wallSx+10,wallSy+14);
        // confessions on wall
        ctx.font=`6px ${ff}`;
        wallConfessions.forEach(wc=>{
          wc.alpha=Math.min(1,wc.alpha+0.01);
          ctx.globalAlpha=wc.alpha*0.75;
          ctx.fillStyle=`hsl(${30+Math.random()*20},60%,70%)`;
          ctx.fillText(wc.text,wallSx+wc.x,wallSy+wc.y);
        });
        ctx.restore();
        // label above wall
        ctx.save();
        ctx.font=`8px ${ff}`;ctx.fillStyle="rgba(255,200,100,0.4)";
        const labelW=ctx.measureText("the wall").width;
        ctx.fillText("the wall",wallSx+WALL_W/2-labelW/2,wallSy-10);
        ctx.restore();
      }

      s.worldObjs.forEach(obj=>{
        const{sx,sy}=w2s(obj.x,obj.y);
        if(sx<-100||sx>W+100||sy<-100||sy>H+200)return;'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Wall draw added')
else:
    print('FAILED - wall draw')

# 3. When user submits confession, also add to wall and broadcast
old3 = '''    if(myCat._updatePresence)myCat._updatePresence();
    setInputVal("");setShowInput(false);
    startCooldown();'''

new3 = '''    if(myCat._updatePresence)myCat._updatePresence();
    // add to confession wall
    const wallEntry={text:inputVal.trim().slice(0,28),x:20+Math.random()*440,y:30+Math.random()*250,alpha:0,id:Date.now()+"_"+Math.random().toString(36).slice(2,6)};
    addToWall(wallEntry.text);
    // broadcast to all players
    channelRef.current?.publish("wall",{entry:wallEntry});
    setInputVal("");setShowInput(false);
    startCooldown();'''

if old3 in content:
    content = content.replace(old3, new3)
    print('Wall broadcast added')
else:
    print('FAILED - wall broadcast')

# 4. Subscribe to wall messages from others
old4 = '''    channel.subscribe("reset",()=>{'''

new4 = '''    channel.subscribe("wall",(msg)=>{
      if(msg.clientId===clientId.current)return;
      addToWall(msg.data.entry.text);
    });

    channel.subscribe("reset",()=>{'''

if old4 in content:
    content = content.replace(old4, new4)
    print('Wall subscribe added')
else:
    print('FAILED - wall subscribe')

# 5. Show wall on minimap
old5 = '''        if(obj.type==="diablo"){
          ctx.fillStyle="rgba(255,0,0,0.9)";
          ctx.beginPath();ctx.arc(mx,my,3,0,Math.PI*2);ctx.fill();
        }'''

new5 = '''        if(obj.type==="diablo"){
          ctx.fillStyle="rgba(255,0,0,0.9)";
          ctx.beginPath();ctx.arc(mx,my,3,0,Math.PI*2);ctx.fill();
        }'''  + '''
      // wall on minimap
      const wmx=MM_X+(WALL_X/WORLD_W)*MM_W;
      const wmy=MM_Y+(WALL_Y/WORLD_H)*MM_H;
      ctx.fillStyle="rgba(255,200,100,0.6)";
      ctx.fillRect(wmx-3,wmy-2,6,3);'''

if old5 in content:
    content = content.replace(old5, new5)
    print('Wall minimap dot added')
else:
    print('FAILED - minimap')

open('src/App.jsx', 'w', encoding='utf-8').write(content)