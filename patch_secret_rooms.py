content = open('src/App.jsx', encoding='utf-8').read()

# 1. Generate secret rooms as world constants
old = '''// ── Confession Wall ───────────────────────────────────────────────────────────
const WALL_X = 5000;'''

new = '''// ── Secret Rooms ─────────────────────────────────────────────────────────────
// fixed positions per epoch so all players share them
function getSecretRooms(){
  const rooms=[];
  const seed=Math.floor((Date.now()-1700000000000)/(3*60*60*1000));
  // deterministic positions based on session seed
  for(let i=0;i<8;i++){
    const angle=(seed*7+i*137.5)%360*(Math.PI/180);
    const dist=1500+((seed*13+i*97)%3000);
    rooms.push({
      x:WORLD_W/2+Math.cos(angle)*dist,
      y:WORLD_H/2+Math.sin(angle)*dist,
      radius:80,
      confession:NPC_CONFESSIONS[(seed*3+i*7)%NPC_CONFESSIONS.length],
    });
  }
  return rooms;
}
const SECRET_ROOMS=getSecretRooms();

// ── Confession Wall ───────────────────────────────────────────────────────────
const WALL_X = 5000;'''

if old in content:
    content = content.replace(old, new)
    print('Secret rooms constants added')
else:
    print('FAILED - secret rooms constants')

# 2. Draw secret rooms and detect entry
old2 = '''      // ── Draw Confession Wall ──'''

new2 = '''      // ── Secret Rooms ──
      const myCatSR=gs.current.cats.find(c=>c.id===gs.current.myId);
      SECRET_ROOMS.forEach((room,i)=>{
        const rsx=room.x-cam.x;
        const rsy=room.y-cam.y;
        if(rsx<-room.radius||rsx>W+room.radius||rsy<-room.radius||rsy>H+room.radius)return;
        // check if player is inside
        const inside=myCatSR&&Math.hypot(myCatSR.x-room.x,myCatSR.y-room.y)<room.radius;
        ctx.save();
        if(inside){
          // full reveal
          ctx.globalAlpha=0.85;
          ctx.fillStyle="rgba(0,0,0,0.7)";
          ctx.beginPath();ctx.arc(rsx,rsy,room.radius,0,Math.PI*2);ctx.fill();
          ctx.strokeStyle="rgba(200,150,255,0.4)";ctx.lineWidth=1;ctx.stroke();
          // confession text
          ctx.font=`7px ${ff}`;
          const tw=ctx.measureText(room.confession).width;
          ctx.fillStyle="rgba(220,180,255,0.9)";
          ctx.fillText(room.confession,rsx-tw/2,rsy);
          ctx.font=`6px ${ff}`;
          ctx.fillStyle="rgba(180,140,255,0.5)";
          ctx.fillText("secret room",rsx-22,rsy+16);
        } else {
          // subtle hint from outside
          ctx.globalAlpha=0.15+Math.sin(s.frame*0.03+i)*0.05;
          ctx.fillStyle="rgba(150,100,255,0.3)";
          ctx.beginPath();ctx.arc(rsx,rsy,room.radius,0,Math.PI*2);ctx.fill();
        }
        ctx.restore();
      });

      // ── Draw Confession Wall ──'''

if old2 in content:
    content = content.replace(old2, new2)
    print('Secret rooms draw added')
else:
    print('FAILED - secret rooms draw')

open('src/App.jsx', 'w', encoding='utf-8').write(content)