# patch_w20_weather.py - sky events: meteor showers, auroras and drifting petals/spores.
# Every 10 minutes each world rolls the dice (same result for everybody, from the shared clock, no messages needed):
# about 4 times in 10 a 90-second sky event happens, fading in and out. A small label names it for the first few seconds.
#   Malkuth Gate: meteor shower or aurora (green/blue)     Glass Garden: drifting petals or aurora (pink/blue)
#   Root Archive: drifting spores or meteor shower
# They are drawn in the sky layer behind the cats and objects, so they never block anything. Day is dimmer than night.
# Test any of them instantly from the console: window.__wxForce="meteors" (or "aurora", "drift"); set it to null to stop.
# Rain (all three worlds, slanted streaks, a darker sky, a soft rain sound that fades in and out, and now and then a lightning flash
# with distant thunder) is one of the events. Needs patch_w19_pages.py first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_wx*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_pages*/" not in src:
    print("ABORT: apply patch_w19_pages.py first. Nothing written."); sys.exit(1)

MOD = r'''/*_wx*/
const WX_LIST={malkuth:["meteors","aurora","rain"],yesod:["drift","aurora","rain"],netzach:["drift","meteors","rain"]};
const WX_RAIN={malkuth:"170,200,255",yesod:"205,190,255",netzach:"150,230,190"};
const WX_AUR={malkuth:["80,255,170","90,160,255"],yesod:["255,140,220","150,200,255"],netzach:["120,255,150","200,255,120"]};
const WX_DRIFT={malkuth:"255,170,90",yesod:"255,170,220",netzach:"170,255,150"};
const WX_NAME={meteors:"meteor shower",aurora:"aurora",rain:"rain",drift:{malkuth:"embers",yesod:"petal drift",netzach:"spore drift"}};
let _wxKey="",_wxEv=null;const WXM=[],WXP=[],WXR=[];let _wxFl=0;
function wxCurrent(){
  const f=typeof window!=="undefined"?window.__wxForce:null;
  if(f)return{type:f,start:Date.now()-60000,end:1e15,a:1,forced:true};
  const now=sharedNow(),slot=Math.floor(now/600000),key=slot+"|"+WORLD_ID;
  if(key!==_wxKey){_wxKey=key;_wxEv=null;const r=mulberry32(hashStr(key+"|wx"));
    if(r()<0.4){const l=WX_LIST[WORLD_ID]||WX_LIST.malkuth,start=slot*600000+Math.floor(r()*480000);_wxEv={type:l[Math.floor(r()*l.length)],start,end:start+90000};}}
  if(!_wxEv||now<_wxEv.start||now>_wxEv.end)return null;
  return{..._wxEv,a:Math.max(0,Math.min(1,(now-_wxEv.start)/6000,(_wxEv.end-now)/6000)),now};
}
function drawWeather(ctx,W,H,f,night){
  const ev=wxCurrent();if(!ev){if(WXM.length)WXM.length=0;if(WXP.length)WXP.length=0;if(WXR.length)WXR.length=0;FKAudio.rain(0);return;}
  const a=ev.a*(night?1:0.55),w=WORLD_ID;
  FKAudio.rain(ev.type==="rain"?ev.a:0);
  if(ev.type==="rain"){ctx.fillStyle=`rgba(0,10,30,${0.2*ev.a})`;ctx.fillRect(0,0,W,H);}
  ctx.save();ctx.globalCompositeOperation="lighter";
  if(ev.type==="aurora"){
    const cols=WX_AUR[w]||WX_AUR.malkuth;
    cols.forEach((col,ci)=>{for(let x=0;x<W;x+=6){const k=x*0.012+f*0.012*(ci?1.4:1)+ci*2;
      const top=H*(0.06+0.12*Math.sin(k)+0.06*Math.sin(k*2.3+f*0.01)+ci*0.08),h=H*(0.3+0.1*Math.sin(k*1.7+1));
      const g=ctx.createLinearGradient(0,top,0,top+h);g.addColorStop(0,`rgba(${col},0)`);g.addColorStop(0.3,`rgba(${col},${0.30*a*(0.6+0.4*Math.sin(x*0.05+f*0.02))})`);g.addColorStop(1,`rgba(${col},0)`);
      ctx.fillStyle=g;ctx.fillRect(x,top,6,h);}});
  }else if(ev.type==="meteors"){
    if(Math.random()<0.07*a&&WXM.length<14){WXM.push({x:W*(0.25+Math.random()*0.9),y:-20,vx:-(5+Math.random()*3),vy:2.5+Math.random()*2,l:0});}
    for(let i=WXM.length-1;i>=0;i--){const m=WXM[i];m.x+=m.vx;m.y+=m.vy;m.l++;if(m.y>H*0.8||m.x<-100||m.l>200){WXM.splice(i,1);continue;}
      const tx=m.x-m.vx*14,ty=m.y-m.vy*14,g=ctx.createLinearGradient(m.x,m.y,tx,ty);g.addColorStop(0,`rgba(255,250,230,${0.9*a})`);g.addColorStop(1,"rgba(255,220,160,0)");
      ctx.strokeStyle=g;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(m.x,m.y);ctx.lineTo(tx,ty);ctx.stroke();ctx.fillStyle=`rgba(255,255,255,${a})`;ctx.fillRect(Math.round(m.x)-1,Math.round(m.y)-1,3,3);}
  }else if(ev.type==="rain"){
    const col=WX_RAIN[w]||WX_RAIN.malkuth,k=ev.a*0.8;
    for(let n=0;n<5&&WXR.length<260;n++)WXR.push({x:Math.random()*(W+120),y:-20,v:15+Math.random()*7,l:9+Math.random()*8});
    ctx.lineWidth=2;ctx.strokeStyle=`rgba(${col},${0.75*k})`;ctx.beginPath();
    for(let i=WXR.length-1;i>=0;i--){const d=WXR[i];d.y+=d.v;d.x-=d.v*0.18;if(d.y>H+10){WXR.splice(i,1);continue;}ctx.moveTo(d.x,d.y);ctx.lineTo(d.x+d.l*0.18,d.y-d.l);}
    ctx.stroke();
    if(ev.a>0.9&&_wxFl<=0&&Math.random()<0.0012){_wxFl=14;setTimeout(()=>{try{FKAudio.thunder();}catch(e){}},500+Math.random()*900);}
  }else if(ev.type==="drift"){
    const col=WX_DRIFT[w]||WX_DRIFT.malkuth;
    if(Math.random()<0.8*a&&WXP.length<90)WXP.push({x:Math.random()*W*1.2,y:-10,s:0.6+Math.random()*1.2,ph:Math.random()*6.28,sz:3+Math.floor(Math.random()*3)});
    for(let i=WXP.length-1;i>=0;i--){const p=WXP[i];p.y+=p.s;p.x-=0.5*p.s;p.ph+=0.03;if(p.y>H+10||p.x<-20){WXP.splice(i,1);continue;}
      ctx.fillStyle=`rgba(${col},${0.9*a})`;ctx.fillRect(Math.round(p.x+Math.sin(p.ph)*14),Math.round(p.y),p.sz,p.sz);}
  }
  ctx.restore();
  if(_wxFl>0){ctx.fillStyle=`rgba(220,230,255,${_wxFl/14*0.26})`;ctx.fillRect(0,0,W,H);_wxFl--;}
  const age=ev.forced?(f%600):(ev.now-ev.start)/1000*60;
  if(age<330){const nm=typeof WX_NAME[ev.type]==="object"?WX_NAME[ev.type][w]:WX_NAME[ev.type];ctx.save();ctx.font="8px "+ff;ctx.textAlign="center";ctx.fillStyle=`rgba(255,255,255,${Math.min(0.6,(330-age)/120)*0.9})`;ctx.fillText(nm||"",W/2,H*0.16);ctx.restore();}
}
let uid=100;'''

src = swap(src, "let uid=100;", MOD, "weather module")
AUD = ('blip(587,1175,0.4,0.05,"sine"),160);},')
src = swap(src, AUD, AUD +
 'rain(v){if(!ctx||muted)return;let R=FKAudio._r;if(!R){if(!(v>0))return;const len=ctx.sampleRate*2,buf=ctx.createBuffer(1,len,ctx.sampleRate),d=buf.getChannelData(0);for(let i=0;i<len;i++)d[i]=Math.random()*2-1;'
 'const mk=(ft,fq,q)=>{const s=ctx.createBufferSource();s.buffer=buf;s.loop=true;const f=ctx.createBiquadFilter();f.type=ft;f.frequency.value=fq;f.Q.value=q;const g=ctx.createGain();g.gain.value=0;s.connect(f);f.connect(g);g.connect(master);s.start(0,Math.random()*1.5);return g;};'
 'R=FKAudio._r={hi:mk("bandpass",4200,0.6),lo:mk("bandpass",1400,0.8),rum:mk("lowpass",260,0.5),v:-1};}'
 'if(Math.abs(R.v-v)<0.02)return;R.v=v;const t=ctx.currentTime;R.hi.gain.setTargetAtTime(0.09*v,t,0.8);R.lo.gain.setTargetAtTime(0.08*v,t,0.8);R.rum.gain.setTargetAtTime(0.05*v,t,1.2);},'
 'thunder(){blip(75,28,2.2,0.22,"sine");setTimeout(()=>blip(130,40,1.6,0.12,"triangle"),250);},', "rain sound")
src = swap(src, "drawSky(ctx,W,H,cam,s.frame,WORLD_ID,skyCol,isNight());", "drawSky(ctx,W,H,cam,s.frame,WORLD_ID,skyCol,isNight());drawWeather(ctx,W,H,s.frame,isNight());", "draw weather")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 3 edits applied.")
