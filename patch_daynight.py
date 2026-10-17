content = open('src/App.jsx', encoding='utf-8').read()

# 1. Add day/night constants after EPOCH_ANCHOR
old = 'const EPOCH_ANCHOR = 1700000000000;'
new = '''const EPOCH_ANCHOR = 1700000000000;
const DAY_CYCLE_MS = 30 * 60 * 1000; // 30 min full cycle
function getDayProgress(){
  // 0.0 = midnight, 0.5 = noon, 1.0 = midnight again
  return ((Date.now()-EPOCH_ANCHOR) % DAY_CYCLE_MS) / DAY_CYCLE_MS;
}
function isNight(){
  const p=getDayProgress();
  return p<0.25||p>0.75; // night = first and last quarter
}
function getSkyColor(){
  const p=getDayProgress();
  // 0=midnight #080810, 0.25=dawn #1a0f2e, 0.5=noon #0d1a2e, 0.75=dusk #2e0f1a
  if(p<0.25){
    const t=p/0.25;
    return blendColor([8,8,16],[26,15,46],t);
  } else if(p<0.5){
    const t=(p-0.25)/0.25;
    return blendColor([26,15,46],[13,26,46],t);
  } else if(p<0.75){
    const t=(p-0.5)/0.25;
    return blendColor([13,26,46],[46,15,26],t);
  } else {
    const t=(p-0.75)/0.25;
    return blendColor([46,15,26],[8,8,16],t);
  }
}
function blendColor(a,b,t){
  const r=Math.round(a[0]+(b[0]-a[0])*t);
  const g=Math.round(a[1]+(b[1]-a[1])*t);
  const bl=Math.round(a[2]+(b[2]-a[2])*t);
  return `rgb(${r},${g},${bl})`;
}'''

if old in content:
    content = content.replace(old, new)
    print('Day/night constants added')
else:
    print('FAILED - constants')

# 2. Replace static background with dynamic sky
old2 = '      ctx.fillStyle="#080810";ctx.fillRect(0,0,W,H);'
new2 = '''      const skyCol=getSkyColor();
      ctx.fillStyle=skyCol;ctx.fillRect(0,0,W,H);
      // night overlay - more stars visible at night
      if(isNight()){
        ctx.fillStyle="rgba(0,0,10,0.15)";ctx.fillRect(0,0,W,H);
      }'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Dynamic sky added')
else:
    print('FAILED - sky')

# 3. Make stars brighter at night
old3 = '''      s.stars.forEach(st=>{
        const sx=(st.x-cam.x*0.3+W*10)%W;
        const sy=(st.y-cam.y*0.3+H*10)%H;
        ctx.beginPath();ctx.arc(sx,sy,st.r,0,Math.PI*2);
        ctx.fillStyle=`rgba(200,200,255,${st.a+Math.sin(s.frame*st.speed)*0.12})`;ctx.fill();
      });'''

new3 = '''      const nightBoost=isNight()?0.4:0;
      s.stars.forEach(st=>{
        const sx=(st.x-cam.x*0.3+W*10)%W;
        const sy=(st.y-cam.y*0.3+H*10)%H;
        ctx.beginPath();ctx.arc(sx,sy,st.r,0,Math.PI*2);
        ctx.fillStyle=`rgba(200,200,255,${Math.min(1,st.a+nightBoost+Math.sin(s.frame*st.speed)*0.12)})`;ctx.fill();
      });'''

if old3 in content:
    content = content.replace(old3, new3)
    print('Stars brightness added')
else:
    print('FAILED - stars')

# 4. Make Diablo faster at night
old4 = '''          obj.vx+=Math.cos(obj.wanderAngle)*0.015;
          obj.vy+=Math.sin(obj.wanderAngle)*0.015;
          obj.vx*=0.98;obj.vy*=0.98;'''

new4 = '''          const diabloSpd=isNight()?0.028:0.015;
          obj.vx+=Math.cos(obj.wanderAngle)*diabloSpd;
          obj.vy+=Math.sin(obj.wanderAngle)*diabloSpd;
          obj.vx*=0.98;obj.vy*=0.98;'''

if old4 in content:
    content = content.replace(old4, new4)
    print('Diablo night boost added')
else:
    print('FAILED - diablo')

# 5. Add day/night indicator to HUD
old5 = '''          <div style={{display:"flex",gap:12,alignItems:"center"}}>
            <span style={{fontSize:7,color:"rgba(255,255,255,0.3)"}}>🐾 {onlineCount} online</span>
            <span style={{fontSize:7,color:"rgba(255,255,255,0.22)"}}>resets {fmtCountdown(resetIn)}</span>
          </div>'''

new5 = '''          <div style={{display:"flex",gap:12,alignItems:"center"}}>
            <span style={{fontSize:7,color:"rgba(255,255,255,0.3)"}}>🐾 {onlineCount} online</span>
            <span style={{fontSize:7,color:"rgba(255,255,255,0.22)"}}>resets {fmtCountdown(resetIn)}</span>
            <span style={{fontSize:7,color:"rgba(255,255,255,0.22)"}}>{Math.floor(getDayProgress()*100)<25||Math.floor(getDayProgress()*100)>75?"🌙":"☀️"}</span>
          </div>'''

if old5 in content:
    content = content.replace(old5, new5)
    print('HUD day/night icon added')
else:
    print('FAILED - HUD')

open('src/App.jsx', 'w', encoding='utf-8').write(content)