# patch_w1_core.py - world step 1 of 3: the machinery for several worlds, with NO visible change yet.
# - one world id (starts as "malkuth", which keeps today's channel name "fikfuk-main" and today's exact world seeds)
# - every random seed (objects, spawns, black hole, paths, secret rooms) also depends on the world id
# - joinWorld(id) swaps worlds on the same cat: new channel, fresh world state, cat keeps its confessions
# - the leaking page listeners (added again on every reconnect) are replaced by ones that remove the old copy
# - debug helpers: __fikfukGo("yesod") to hop worlds from the console, __fikfukWorld() to read the current one
# Needs the earlier patches first (wipe, rooms, sync). All-or-nothing, idempotent, safe on Windows files.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in src else "\n"

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "channelFor" in src:
    print("Already patched. Nothing written."); sys.exit(0)
for need, name in (("_srEpoch", "patch_rooms"), ("_syncSeen", "patch_sync"), ("_wipeLocal", "patch_wipe")):
    if need not in src:
        print(f"ABORT: apply {name}.py first. Nothing written."); sys.exit(1)

SALT = '(WORLD_ID==="malkuth"?"":":w:"+WORLD_ID)'
src = swap(src, 'const CHANNEL   = "fikfuk-main";',
    'const CHANNEL   = "fikfuk-main";let WORLD_ID="malkuth";function channelFor(id){return id==="malkuth"?CHANNEL:"fikfuk:"+id;}', "world id + channel name")
src = swap(src, 'hashStr("fikfuk:"+getEpoch()+":"+tag)', 'hashStr("fikfuk:"+getEpoch()+":"+tag+' + SALT + ')', "seed: world objects")
src = swap(src, 'hashStr("fikfuk:spawn:"+type+":"+slotNow)', 'hashStr("fikfuk:spawn:"+type+":"+slotNow+' + SALT + ')', "seed: spawns")
src = swap(src, 'hashStr("fikfuk:bh:"+slot)', 'hashStr("fikfuk:bh:"+slot+' + SALT + ')', "seed: black hole")
src = swap(src, 'hashStr("path:"+obj.id)', 'hashStr("path:"+obj.id+' + SALT + ')', "seed: paths")
src = swap(src, "const seed=getEpoch();", 'const seed=getEpoch()+(WORLD_ID==="malkuth"?0:hashStr(WORLD_ID)%997);', "seed: secret rooms")
src = swap(src, "const e=getEpoch();if(e!==_srEpoch){", 'const e=getEpoch()+"|"+WORLD_ID;if(e!==_srEpoch){', "secret room cache key")
src = swap(src, "const channel=ably.channels.get(CHANNEL);", "const channel=ably.channels.get(channelFor(WORLD_ID));", "channel per world")
src = swap(src, 'window.addEventListener("beforeunload",()=>channel.presence.leave());',
    'if(window.__fkUnload)window.removeEventListener("beforeunload",window.__fkUnload);'
    'window.__fkUnload=()=>{try{channel.presence.leave();}catch(e){}};window.addEventListener("beforeunload",window.__fkUnload);', "unload listener")
src = swap(src, 'document.addEventListener("visibilitychange",()=>{',
    'if(window.__fkVis)document.removeEventListener("visibilitychange",window.__fkVis);'
    'document.addEventListener("visibilitychange",window.__fkVis=()=>{', "visibility listener")
src = swap(src, "window.__fikfukSync=sendSync;",
    'window.__fikfukSync=sendSync;window.__fikfukGo=joinWorld;window.__fikfukWorld=()=>WORLD_ID;', "debug helpers")
src = swap(src, "s.stars=genStars();", 'WORLD_ID="malkuth";s.stars=genStars();', "every new cat starts in Malkuth")

JOIN = NL.join([
 "  function joinWorld(id){",
 "    const s=gs.current;",
 "    const me=s.cats.find(c=>c.id===s.myId);",
 "    if(!me||!s.ready||id===WORLD_ID)return;",
 "    WORLD_ID=id;",
 "    s.cats=buildSysCats();s.cats.push(me);",
 "    me._territory=null;s._myTerritory=null;me._carry=false;",
 "    s.worldObjs=generateWorldObjects();",
 "    s._worldEpoch=getEpoch();",
 "    s._initObjs=s.worldObjs.map(o=>({type:o.type,x:Math.round(o.x),y:Math.round(o.y)}));",
 "    s._dead=new Set();s._bhClosedSlot=undefined;s._spawnSlot={};s._chirps=[];s.particles=[];s._syncSeen={};s._joinAnswered={};",
 "    wallConfessions.length=0;",
 "    setOnlineCount(1);",
 "    connectAbly(me);",
 "  }",
 "",
 "  function connectAbly(myCat){"])
src = swap(src, "  function connectAbly(myCat){", JOIN, "joinWorld")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 13 edits applied. Nothing changes for players yet. Console test: __fikfukGo(\"yesod\") then __fikfukWorld().")
