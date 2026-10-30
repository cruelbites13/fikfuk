# patch_w2_content.py - world step 2 of 3: what each world looks like and how it plays. Still no way to travel yet
# (that is step 3), so players only see this if they hop with the console helper.
# Worlds: malkuth = "Malkuth Gate" (today's world), yesod = "Glass Garden" (chirps carry 1.5x as far),
#         netzach = "Root Archive" (purr circles form at 170 instead of 130).
# - sky tint per world (Malkuth keeps today's sky exactly), the world name in the top bar
# - the policy, about and Patates cats live only in Malkuth; the other worlds get the Oracle instead
#   (so Malkuth loses its Oracle: that is the one visible change for today's players)
# - catching a mouse only means "carry it to Patates" in Malkuth; elsewhere it is just a speed boost
# Needs patch_w1_core first. All-or-nothing, idempotent, safe on Windows files.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "const WORLDS=" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "channelFor" not in src:
    print("ABORT: apply patch_w1_core.py first. Nothing written."); sys.exit(1)

CH = '((WORLDS[WORLD_ID]||{}).chirpRadius||1)'
PR = '((WORLDS[WORLD_ID]||{}).purrRadius||130)'
src = swap(src, 'function channelFor(id){return id==="malkuth"?CHANNEL:"fikfuk:"+id;}',
    'function channelFor(id){return id==="malkuth"?CHANNEL:"fikfuk:"+id;}'
    'const WORLDS={malkuth:{name:"Malkuth Gate",sky:["#0B0B18","#1A1A3A"]},'
    'yesod:{name:"Glass Garden",sky:["#2A2440","#B8A8E0"],chirpRadius:1.5},'
    'netzach:{name:"Root Archive",sky:["#0D2318","#2E5A3A"],purrRadius:170}};', "world table")
src = swap(src, "const [onlineCount, setOnlineCount] = useState(0);",
    'const [onlineCount, setOnlineCount] = useState(0);const [worldName,setWorldName]=useState("Malkuth Gate");', "world name state")
src = swap(src, "if(!me||!s.ready||id===WORLD_ID)return;", "if(!me||!s.ready||id===WORLD_ID||!WORLDS[id])return;", "unknown world guard")
src = swap(src, "WORLD_ID=id;", "WORLD_ID=id;setWorldName(WORLDS[id].name);", "name on hop")
src = swap(src, 'WORLD_ID="malkuth";s.stars=genStars();', 'WORLD_ID="malkuth";setWorldName(WORLDS.malkuth.name);s.stars=genStars();', "name on spawn")
src = swap(src, "return[pc,ac,pat,ocat];", 'return WORLD_ID==="malkuth"?[pc,ac,pat]:[ocat];', "system cats per world")
src = swap(src, "myCat._carry=true;", 'myCat._carry=(WORLD_ID==="malkuth");', "carry only in Malkuth")
src = swap(src, "if(!s._carryHint){", 'if(!s._carryHint&&WORLD_ID==="malkuth"){', "carry hint only in Malkuth")
src = swap(src, "if(Math.hypot(c.x-x,c.y-y)<250&&c.confessions.length){", "if(Math.hypot(c.x-x,c.y-y)<250*" + CH + "&&c.confessions.length){", "chirp radius")
src = swap(src, "ctx.arc(rcx,rcy,prog*250,0,Math.PI*2);ctx.stroke();", "ctx.arc(rcx,rcy,prog*250*" + CH + ",0,Math.PI*2);ctx.stroke();", "chirp ripple")
src = swap(src, "sit.filter(o=>o!==c&&Math.hypot(o.x-c.x,o.y-c.y)<130).length>=2", "sit.filter(o=>o!==c&&Math.hypot(o.x-c.x,o.y-c.y)<" + PR + ").length>=2", "purr radius")
src = swap(src, "ctx.arc(ppx+5.5*P,ppy+5*P,48,0,Math.PI*2);ctx.fill();", "ctx.arc(ppx+5.5*P,ppy+5*P,48*(" + PR + "/130),0,Math.PI*2);ctx.fill();", "purr circle size")
src = swap(src, "ctx.fillStyle=skyCol;ctx.fillRect(0,0,W,H);",
    "ctx.fillStyle=skyCol;ctx.fillRect(0,0,W,H);"
    '{const _w=WORLDS[WORLD_ID];if(_w&&WORLD_ID!=="malkuth"){const _g=ctx.createLinearGradient(0,0,0,H);_g.addColorStop(0,_w.sky[0]);_g.addColorStop(1,_w.sky[1]);'
    "ctx.save();ctx.globalAlpha=isNight()?0.55:0.8;ctx.fillStyle=_g;ctx.fillRect(0,0,W,H);ctx.restore();}}", "world sky")
src = swap(src, '<span style={{fontSize:7,color:"rgba(255,255,255,0.3)"}}>\U0001F43E {onlineCount} online</span>',
    '<span style={{fontSize:7,color:"rgba(255,255,255,0.45)"}}>{worldName}</span>'
    '<span style={{fontSize:7,color:"rgba(255,255,255,0.3)"}}>\U0001F43E {onlineCount} online</span>', "world name in top bar")
src = swap(src, "window.__fikfukWorld=()=>WORLD_ID;",
    "window.__fikfukWorld=()=>WORLD_ID;window.__fikfukSys=()=>gs.current.cats.filter(c=>c.isSys).map(c=>c.sysType);", "debug helper")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 15 edits applied. Console test: __fikfukGo(\"yesod\") (sky changes, name shows, only the oracle cat), __fikfukGo(\"netzach\"), __fikfukGo(\"malkuth\").")
