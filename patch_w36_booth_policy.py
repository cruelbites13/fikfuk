# patch_w36_booth_policy.py - the donation booth, PayPal, and the rewritten policy.
# 1) The donation cat (the green "about" cat) now sits in a proper fixed tip booth by the spawn: a striped awning with a
#    "tips" sign, wooden posts, a table with a glowing tip jar and two little tokens (PayPal blue, Solana purple), and a
#    warm lantern at night. It stays exactly where it is. Double-tap the cat and the card now offers a "tip with paypal"
#    button (opens paypal.me/cruelbites in a new tab) and, below it, the Solana address (tap to copy, it says "copied!").
# 2) The policy cat now tells the truth about the place: a cat & chill place, no accounts or emails, what is shared and
#    what is not stored, what your device remembers, what the hosts can see (the old "no tracking" line was not accurate,
#    because the site uses anonymous page-speed stats), and a short be-kind rule. The donation and policy cards no longer repeat the short lines as a numbered list (they still float as speech bubbles). Cards on small phones scroll if long.
# Needs patch_w35_patates_grave.py first. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_booth*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_grave*/" not in src:
    print("ABORT: apply patch_w35_patates_grave.py first. Nothing written."); sys.exit(1)

MOD = r'''/*_booth*/
function drawBooth(ctx,cam,W,H,f){
  if(WORLD_ID!=="malkuth")return;
  const sx=Math.round(5300-cam.x),sy=Math.round(5200-cam.y);
  if(sx<-120||sx>W+200||sy<-100||sy>H+100)return;
  const night=isNight(),pu=0.5+0.5*Math.sin(f*0.05);
  ctx.save();
  ctx.fillStyle="rgba(30,18,8,0.45)";ctx.beginPath();ctx.ellipse(sx+30,sy+46,100,22,0,0,6.2832);ctx.fill();
  ctx.fillStyle="#6b4220";ctx.fillRect(sx-52,sy-40,6,88);ctx.fillRect(sx+112,sy-40,6,88);ctx.fillStyle="#9a6a38";ctx.fillRect(sx-52,sy-40,3,88);ctx.fillRect(sx+112,sy-40,3,88);
  for(let i=0;i<8;i++){ctx.fillStyle=i%2?"#fff0cc":"#e8b84e";ctx.fillRect(sx-58+i*22,sy-60,22,22);ctx.fillStyle=i%2?"#e2d3a8":"#c99a30";ctx.fillRect(sx-58+i*22,sy-42,22,4);
    ctx.fillStyle=i%2?"#fff0cc":"#e8b84e";ctx.fillRect(sx-58+i*22+4,sy-38,14,6);}
  ctx.fillStyle="#3a2410";ctx.fillRect(sx+10,sy-56,64,14);ctx.fillStyle="#ffd96b";ctx.textAlign="center";ctx.textBaseline="middle";ctx.font="7px 'Press Start 2P',monospace";ctx.fillText("TIPS",sx+42,sy-48);ctx.textAlign="left";ctx.textBaseline="alphabetic";
  ctx.fillStyle="#7a4f24";ctx.fillRect(sx+54,sy+24,54,22);ctx.fillStyle="#5a3818";ctx.fillRect(sx+54,sy+24,54,3);ctx.fillRect(sx+56,sy+46,5,6);ctx.fillRect(sx+101,sy+46,5,6);
  ctx.fillStyle="#b07a3c";ctx.fillRect(sx+52,sy+16,58,8);ctx.fillStyle="#cf9650";ctx.fillRect(sx+52,sy+16,58,3);
  ctx.fillStyle="rgba(210,235,255,0.38)";ctx.fillRect(sx+60,sy-6,16,22);ctx.fillStyle="rgba(235,248,255,0.6)";ctx.fillRect(sx+60,sy-6,3,22);ctx.fillRect(sx+58,sy-9,20,4);
  ctx.fillStyle="#e8b84e";ctx.fillRect(sx+62,sy+10,12,6);ctx.fillStyle="#ffd96b";ctx.fillRect(sx+62,sy+7,12,3);ctx.fillRect(sx+64,sy+4,8,3);
  ctx.fillStyle="#1e5fd8";ctx.fillRect(sx+84,sy+6,11,11);ctx.fillStyle="#fff";ctx.font="6px 'Press Start 2P',monospace";ctx.fillText("P",sx+86,sy+14);
  ctx.fillStyle="#7b3fd6";ctx.fillRect(sx+97,sy+6,11,11);ctx.fillStyle="#14f195";ctx.fillRect(sx+99,sy+14,7,2);ctx.fillStyle="#ffffff";ctx.fillRect(sx+99,sy+9,7,2);
  ctx.globalCompositeOperation="lighter";
  ctx.fillStyle="rgba(255,215,110,"+(0.07+0.05*pu).toFixed(3)+")";ctx.beginPath();ctx.ellipse(sx+68,sy+8,30,20,0,0,6.2832);ctx.fill();
  const tw=Math.sin(f*0.09);if(tw>0.4){ctx.fillStyle="rgba(255,255,255,"+(tw).toFixed(3)+")";ctx.fillRect(sx+66,sy-2-Math.round(tw*4),3,3);}
  if(night){const fl=0.8+0.2*Math.sin(f*0.2);ctx.fillStyle="rgba(255,190,90,"+(0.16*fl).toFixed(3)+")";ctx.beginPath();ctx.ellipse(sx-36,sy-22,40,28,0,0,6.2832);ctx.fill();ctx.fillStyle="rgba(255,225,150,"+fl.toFixed(3)+")";ctx.fillRect(sx-39,sy-26,6,8);}
  ctx.restore();
}
let uid=100;'''

PAYPAL = ('<div style={{fontSize:7,color:"#ffd96b",lineHeight:1.9}}>fikfuk is free and runs on tips. every coin keeps the servers purring.</div>'
  '<button onClick={()=>{try{window.open("https://paypal.me/cruelbites","_blank","noopener,noreferrer");}catch(e){}}} style={{background:"rgba(30,95,216,0.2)",border:"1px solid #3b82f6",color:"#9cc4ff",fontFamily:ff,fontSize:8,padding:"10px 12px",cursor:"pointer",boxShadow:"0 0 10px rgba(59,130,246,0.3)"}}>tip with paypal</button>'
  '<div style={{fontSize:7,color:"#44cc44"}}>or tip with solana</div>')
COPY_OLD = 'onClick={()=>navigator.clipboard?.writeText("3oDULkLmFSXppKGyKLQjE32MSSmDcyAcZL2jWy94rbp2")}'
COPY_NEW = 'onClick={e=>{try{navigator.clipboard?.writeText("3oDULkLmFSXppKGyKLQjE32MSSmDcyAcZL2jWy94rbp2");}catch(x){}const n=e.currentTarget.nextElementSibling;if(n){n.textContent="copied!";setTimeout(()=>{n.textContent="tap to copy";},1500);}}}'
POLICY = ('{panel.sysType==="privacy"&&(<div style={{display:"flex",flexDirection:"column",gap:10,marginTop:4}}>'
  + "".join('<div style={{fontSize:7,color:"rgba(200,200,255,0.85)",lineHeight:2}}>%s</div>' % t for t in [
    "fikfuk.wtf is a cat &amp; chill place. wander, chirp, sit with strangers, leave a confession under the night sky. that is all it is.",
    "no accounts, no emails, no passwords. you pick a name and a coat and you are in.",
    "what you type (names, confessions, letters) is shared live with the people in the world. we keep no database of it, and the world wipes every 3 hours.",
    "your device remembers small things (sound settings, your cat, a random anonymous id) so the place feels the same when you come back.",
    "like any website, our hosts (vercel and ably) see basic technical info such as your ip address, and we use anonymous page-speed stats.",
    "be kind. no hate, no threats, no adult or illegal stuff, no real names or private info. if the place gets abused, text may be turned off."])
  + '</div>)}')

CRLF = "\r\n" in src
if CRLF: src = src.replace("\r\n", "\n")
n = 0
def S(old, new, label):
    global src, n
    src = swap(src, old, new, label); n += 1
S("let uid=100;", MOD, "booth module")
S('const ABOUT_LINES  =["fikfuk.wtf","a canvas of strangers","& their pixel cats","built by cruelbites","donate via solana","double-tap to donate"];',
  'const ABOUT_LINES  =["fikfuk.wtf","a cat & chill place","built by cruelbites","tips keep it alive","paypal or solana","double-tap to tip"];', "about lines")
S('const PRIVACY_LINES=["anonymous","no accounts","no emails","confessions live 3hrs","then wiped forever","no tracking · ever"];',
  'const PRIVACY_LINES=["a cat & chill place","no accounts · no emails","be kind to strangers","everything fades every 3 hrs"];', "policy lines")
S('<div style={{fontSize:7,color:"#44cc44"}}>donate via solana</div>', PAYPAL, "paypal button")
S(COPY_OLD, COPY_NEW, "copy feedback")
S("{panel&&!panel.isOwn&&!panel.isSys&&(", POLICY + "{panel&&!panel.isOwn&&!panel.isSys&&(", "policy text")
S('padding:"20px",minWidth:280,maxWidth:"90vw",display:"flex",flexDirection:"column",gap:12}}>', 'padding:"20px",minWidth:280,maxWidth:"90vw",maxHeight:"86vh",overflowY:"auto",display:"flex",flexDirection:"column",gap:12}}>', "scrollable card")
S("drawGrave(ctx,cam,W,H,s.frame);", "drawBooth(ctx,cam,W,H,s.frame);drawGrave(ctx,cam,W,H,s.frame);", "draw booth")
S("{!panel.confessions.length", '{panel.sysType==="privacy"||panel.sysType==="about"?null:!panel.confessions.length', "hide duplicate list")
if CRLF: src = src.replace("\n", "\r\n")
open(P, "w", encoding="utf-8", newline="").write(src)
print(f"OK: {n} edits applied.")
