content = open('src/App.jsx', encoding='utf-8').read()

# 1. Add Oracle palette and responses after PATATES_LINES
old = 'const PATATES_LINES=["thank u for taking care of me","i loved being clingy with u","my naughty days were the best days","i am okay now, dont worry","i still hear u calling my name","u gave me a good life"];'

new = old + '''
const SYS_PAL_ORACLE={ body:"#1a0a2e",shadow:"#0d0514",stripe:"#3d1a5e",inner:"#e0c0ff",eye:"#cc44ff",pupil:"#660099",nose:"#ff88ff",_name:"oracle" };
const ORACLE_RESPONSES=[
  "yes, but not yet","no, and that is okay","the stars say maybe","ask again at midnight",
  "your cat knows the answer","it has already happened","let it go","not in this session",
  "the wall holds your answer","yes, absolutely","never","only if u confess first",
];'''

if old in content:
    content = content.replace(old, new)
    print('Oracle palette added')
else:
    print('FAILED - oracle palette')

# 2. Add oracle to buildSysCats
old2 = '''    // patates - tribute cat, always present near spawn
    const pat=makeCat(cx,cy-250,SYS_PAL_PATATES,"patates",false,true,"patates");
    pat.confessions=[...PATATES_LINES];
    pat.wanderTimer=0;'''

new2 = '''    // patates - tribute cat, always present near spawn
    const pat=makeCat(cx,cy-250,SYS_PAL_PATATES,"patates",false,true,"patates");
    pat.confessions=[...PATATES_LINES];
    pat.wanderTimer=0;
    // oracle - rare, random location far from spawn
    const oraclePal={...SYS_PAL_ORACLE};
    const ocat=makeCat(
      1000+Math.random()*(WORLD_W-2000),
      1000+Math.random()*(WORLD_H-2000),
      oraclePal,"oracle",false,true,"oracle"
    );
    ocat.confessions=["i see all","i know all","ask me anything","double-tap to consult"];
    ocat._isOracle=true;'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Oracle spawn added')
else:
    print('FAILED - oracle spawn')

# 3. Add oracle to return array
old3 = '    return[pc,ac,pat];'
new3 = '    return[pc,ac,pat,ocat];'

if old3 in content:
    content = content.replace(old3, new3)
    print('Oracle in return added')
else:
    print('FAILED - oracle return')

# 4. Oracle slow mystical movement
old4 = '''        } else if(cat.sysType==="patates"){'''

new4 = '''        } else if(cat.sysType==="oracle"){
          // slow mystical drift
          cat.wanderTimer--;
          if(cat.wanderTimer<=0){
            cat.wanderAngle+=(Math.random()-0.5)*0.8;
            cat.wanderTimer=300+Math.random()*400;
            cat.state=Math.random()>0.7?"run":"sit";
          }
          if(cat.state==="run"){
            cat.vx+=Math.cos(cat.wanderAngle)*0.01;
            cat.vy+=Math.sin(cat.wanderAngle)*0.01;
            cat.flip=cat.vx<0;
          }
        } else if(cat.sysType==="patates"){'''

if old4 in content:
    content = content.replace(old4, new4)
    print('Oracle movement added')
else:
    print('FAILED - oracle movement')

# 5. Oracle can also move
old5 = "        if(!cat.isSys||cat.sysType===\"patates\"){cat.x+=cat.vx;cat.y+=cat.vy;}"
new5 = "        if(!cat.isSys||cat.sysType===\"patates\"||cat.sysType===\"oracle\"){cat.x+=cat.vx;cat.y+=cat.vy;}"

if old5 in content:
    content = content.replace(old5, new5)
    print('Oracle movement unlock added')
else:
    print('FAILED - oracle move unlock')

# 6. Oracle panel - show random response when double tapped
old6 = '''      if(cat){
      if(lastTap.current.id===cat.id&&now-lastTap.current.time<400){
        setPanel({catId:cat.id,name:cat.name,confessions:[...cat.confessions],isOwn:cat.isOwn,isSys:cat.isSys,sysType:cat.sysType,eye:cat.pal.eye});
        lastTap.current={id:null,time:0};return;
      }'''

new6 = '''      if(cat){
      if(lastTap.current.id===cat.id&&now-lastTap.current.time<400){
        if(cat.sysType==="oracle"){
          // oracle gives a random cryptic answer
          const response=ORACLE_RESPONSES[Math.floor(Math.random()*ORACLE_RESPONSES.length)];
          setPanel({catId:cat.id,name:"oracle",confessions:[response],isOwn:false,isSys:true,sysType:"oracle",eye:cat.pal.eye,isOracleResponse:true});
        } else {
          setPanel({catId:cat.id,name:cat.name,confessions:[...cat.confessions],isOwn:cat.isOwn,isSys:cat.isSys,sysType:cat.sysType,eye:cat.pal.eye});
        }
        lastTap.current={id:null,time:0};return;
      }'''

if old6 in content:
    content = content.replace(old6, new6)
    print('Oracle panel added')
else:
    print('FAILED - oracle panel')

# 7. Oracle panel accent color + special display
old7 = "  const panelAccent=panel?.isSys?(panel.sysType===\"privacy\"?\"#7777ff\":\"#44cc44\"):(panel?.isOwn?\"#ff3232\":\"rgba(120,120,255,0.7)\");"
new7 = "  const panelAccent=panel?.isSys?(panel.sysType===\"privacy\"?\"#7777ff\":panel.sysType===\"about\"?\"#44cc44\":panel.sysType===\"patates\"?\"#ffaa44\":panel.sysType===\"oracle\"?\"#cc44ff\":\"#ffffff\"):(panel?.isOwn?\"#ff3232\":\"rgba(120,120,255,0.7)\");"

if old7 in content:
    content = content.replace(old7, new7)
    print('Oracle accent added')
else:
    print('FAILED - oracle accent')

# 8. Oracle minimap dot
old8 = '''      // wall on minimap
      const wmx=MM_X+(WALL_X/WORLD_W)*MM_W;
      const wmy=MM_Y+(WALL_Y/WORLD_H)*MM_H;
      ctx.fillStyle="rgba(255,200,100,0.6)";
      ctx.fillRect(wmx-3,wmy-2,6,3);'''

new8 = '''      // wall on minimap
      const wmx=MM_X+(WALL_X/WORLD_W)*MM_W;
      const wmy=MM_Y+(WALL_Y/WORLD_H)*MM_H;
      ctx.fillStyle="rgba(255,200,100,0.6)";
      ctx.fillRect(wmx-3,wmy-2,6,3);
      // oracle on minimap
      s.cats.filter(c=>c.sysType==="oracle").forEach(c=>{
        const omx=MM_X+(c.x/WORLD_W)*MM_W;
        const omy=MM_Y+(c.y/WORLD_H)*MM_H;
        ctx.fillStyle="rgba(200,68,255,0.8)";
        ctx.beginPath();ctx.arc(omx,omy,3,0,Math.PI*2);ctx.fill();
      });'''

if old8 in content:
    content = content.replace(old8, new8)
    print('Oracle minimap added')
else:
    print('FAILED - oracle minimap')

open('src/App.jsx', 'w', encoding='utf-8').write(content)