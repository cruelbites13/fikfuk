# patch_wipe.py - make the 3-hour wipe reliable: every client wipes ITSELF when the epoch changes
# (works for tabs that slept through the reset), closes its old Ably connection, and nobody
# broadcasts "reset" any more (that was N clients x N receivers = a message burst at every wipe).
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "_wipeLocal" in src:
    print("Already patched. Nothing written."); sys.exit(0)

# 1. remember which epoch this cat was born in
src = swap(src, "saveSession({name,palId,confessions:myCat.confessions,x:ox,y:oy});",
           "gs.current._spawnEpoch=getEpoch();saveSession({name,palId,confessions:myCat.confessions,x:ox,y:oy});", "spawn epoch")
# 2. old clients may still broadcast reset: when it arrives, also close the old connection
src = swap(src, 'channel.subscribe("reset",()=>{',
           'channel.subscribe("reset",()=>{try{ablyRef.current.close();}catch(e){}', "reset handler close")
# 3. local wipe whenever the epoch has moved on (runs in the existing 1s timer); also empties the Confession Wall
#    (it lives in a module-level array that survived the wipe) and clears the tag button state
WIPE = ("const ms=nextResetMs();\n"
        "      /*_wipeLocal*/{const _g=gs.current;if(phaseRef.current===\"play\"&&_g._spawnEpoch!=null&&getEpoch()!==_g._spawnEpoch){"
        "localStorage.removeItem(\"fikfuk_s\");try{ablyRef.current.close();}catch(e){}"
        "_g.cats=[];_g.myId=null;_g.ready=false;_g.laserOn=false;_g.laser={sx:-999,sy:-999,active:false};_g.trail=[];_g.worldObjs=[];_g._spawnEpoch=null;"
        "wallConfessions.length=0;setMyTag(\"\");"
        "setLaserOn(false);phaseRef.current=\"onboard\";setPhase(\"onboard\");return;}}")
src = swap(src, "const ms=nextResetMs();", WIPE, "epoch check")
# 3b. when the Ably clock sync lands, the epoch may legitimately change (device clock was off):
#     the game already regenerates the world there, so just re-pin this cat's epoch instead of wiping it
src = swap(src, "clockOffset=serverT-(_t0+_t1)/2;",
           "clockOffset=serverT-(_t0+_t1)/2;if(gs.current._spawnEpoch!=null)gs.current._spawnEpoch=getEpoch();", "re-pin epoch after clock sync")
# 4. stop the N-squared reset broadcast
src = swap(src, 'channelRef.current?.publish("reset",{});', "/* reset is local now: no broadcast */", "remove broadcast")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 5 edits applied. Test: leave a tab open past a reset (or use a clock override) and it must return to onboarding.")
