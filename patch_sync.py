# patch_sync.py - join sync burst fix. Before: every client answered every join (N syncs x N receivers).
# After: the 3 clients ranked highest by hash(joiner + me) answer; ranks 4-6 answer only if they have
# not seen any sync addressed to that joiner since the join (covers sleeping tabs). Run: python patch_sync.py
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written."); sys.exit(1)
    return text.replace(old, new)
if "_syncSeen" in src: print("Already patched. Nothing written."); sys.exit(0)

src = swap(src, "const sendSync=()=>{", "const sendSync=(_for)=>{", "sendSync takes a target")
src = swap(src, "bhClosed:(s._bhClosedSlot===undefined)?null:s._bhClosedSlot,",
                "bhClosed:(s._bhClosedSlot===undefined)?null:s._bhClosedSlot,for:_for||null,", "tag sync with joiner")
SEEN = ('channel.subscribe("sync",(m)=>{try{const d=m.data;if(d&&d.for){const s=gs.current;(s._syncSeen=s._syncSeen||{})[d.for]=Date.now();}}catch(e){}});\n'
        '    channel.presence.subscribe("enter",(m)=>{')
src = swap(src, 'channel.presence.subscribe("enter",(m)=>{', SEEN, "record answered joins")
RESPOND = ('{const _j=m.clientId,_me=clientId.current,_t0=Date.now(),_ja=(gs.current._joinAnswered=gs.current._joinAnswered||{});if(_j&&_j!==_me&&_t0-(_ja[_j]||0)>120000){_ja[_j]=_t0;'
  'const _hs=(x)=>{let h=2166136261;for(let i=0;i<x.length;i++){h^=x.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;};'
  'const _ids=gs.current.cats.filter(c=>!c.isOwn&&!c.isSys&&!c.isGhost&&c.id!==_j).map(c=>c.id);_ids.push(_me);'
  '_ids.sort((a,b)=>_hs(_j+":"+a)-_hs(_j+":"+b)||(a<b?-1:1));const _rank=_ids.indexOf(_me);'
  'if(_rank<3)setTimeout(()=>{try{sendSync(_j);}catch(e){}},300+Math.random()*1000);'
  'else if(_rank<6)setTimeout(()=>{const _t=(gs.current._syncSeen||{})[_j]||0;if(_t<_t0){try{sendSync(_j);}catch(e){}}},3500+Math.random()*1000);}}')
src = swap(src, "setTimeout(()=>{try{sendSync();}catch(e){}},500+Math.random()*2500);", RESPOND, "join responder")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 4 edits applied. Test: open 3 tabs; join a 4th and watch Ably publishes: about 3 syncs per join, not one per tab.")
