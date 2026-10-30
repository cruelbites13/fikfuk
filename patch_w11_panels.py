# patch_w11_panels.py - the pop-ups get the same calm glass look as the buttons:
# - confession / letter / tag sheets: rounded top, frosted background, centred and capped in width on big screens,
#   slide up when they open; bigger comfortable text field; rounded buttons that brighten on hover
# - the cat's panel (tap a cat): frosted backdrop, rounded card that pops in, rounded emoji buttons
# - confession bubbles above cats: rounder, softly glowing in their accent colour, with a faint top highlight
# Same text, same behaviour, same colours per type (red cats, amber Patates, blue letters). Safe to run twice.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
if "/*_ui11*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "/*_ui10*/" not in src:
    print("ABORT: apply patch_w10_ui.py first. Nothing written."); sys.exit(1)
def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written."); sys.exit(1)
    return text.replace(old, new)

CSS = ("/*_ui11*/.sheet{border-radius:18px 18px 0 0!important;border-width:1px!important;background:rgba(10,10,24,0.84)!important;"
 "backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);width:min(100%,560px);left:50%!important;right:auto!important;"
 "animation:sheetup .22s ease-out both;box-shadow:0 -12px 40px rgba(0,0,0,0.5)}"
 "@keyframes sheetup{from{opacity:0;transform:translate(-50%,24px)}to{opacity:1;transform:translate(-50%,0)}}"
 ".sheet input{padding:10px 2px!important;font-size:10px!important;caret-color:#fff}"
 ".sheet button{transition:filter .15s,transform .12s;border-radius:10px!important}"
 ".sheet button[style*='font-size: 7px']{padding:9px 14px!important}"
 ".sheet button:hover,.card button:hover{filter:brightness(1.4)}.sheet button:active,.card button:active{transform:scale(.96)}"
 ".scrim{backdrop-filter:blur(5px);-webkit-backdrop-filter:blur(5px);animation:fadein .18s ease-out both}"
 "@keyframes fadein{from{opacity:0}to{opacity:1}}"
 ".card{border-radius:16px!important;border-width:1px!important;background:linear-gradient(180deg,#15152c,#0b0b1a)!important;animation:pop .2s ease-out both}"
 "@keyframes pop{from{opacity:0;transform:scale(.95) translateY(8px)}to{opacity:1;transform:none}}"
 ".card button{border-radius:10px!important}")
src = swap(src, ".hbtn:active{transform:translateY(1px) scale(.98);filter:brightness(1.1);}",
           ".hbtn:active{transform:translateY(1px) scale(.98);filter:brightness(1.1);}" + CSS, "css")

SH = '<div style={{position:"fixed",bottom:0,left:0,right:0,background:"rgba(8,8,16,0.97)",border:"2px solid '
for tail, label in (('rgba(255,200,100,0.6)",borderBottom', "tag sheet"), ('rgba(100,150,255,0.6)",borderBottom', "letter sheet"), ('#ff3232",borderBottom', "confess sheet")):
    src = swap(src, SH + tail, '<div className="sheet" style={{position:"fixed",bottom:0,left:0,right:0,background:"rgba(8,8,16,0.97)",border:"2px solid ' + tail, label)

src = swap(src, '<div style={{position:"fixed",inset:0,zIndex:200,display:"flex",alignItems:"center",justifyContent:"center",background:"rgba(0,0,0,0.65)"}} onClick={()=>setPanel(null)}>',
           '<div className="scrim" style={{position:"fixed",inset:0,zIndex:200,display:"flex",alignItems:"center",justifyContent:"center",background:"rgba(0,0,0,0.65)"}} onClick={()=>setPanel(null)}>', "scrim")
src = swap(src, '<div onClick={e=>e.stopPropagation()} style={{background:"#0d0d1a",border:',
           '<div className="card" onClick={e=>e.stopPropagation()} style={{background:"#0d0d1a",border:', "card")

src = swap(src, 'ctx.fillStyle="rgba(0,0,0,0.45)";rrect(ctx,bx+2,by+2,bw,bh,4);ctx.fill();',
 'ctx.fillStyle="rgba(0,0,0,0.30)";rrect(ctx,bx+1,by+4,bw,bh,9);ctx.fill();'
 'ctx.strokeStyle=accent;ctx.globalAlpha*=0.14;ctx.lineWidth=6;rrect(ctx,bx,by,bw,bh,9);ctx.stroke();ctx.globalAlpha/=0.14;', "bubble shadow and glow")
src = swap(src, 'ctx.fillStyle="#1a140d";ctx.strokeStyle=accent;ctx.lineWidth=1.5;', 'ctx.fillStyle="rgba(22,16,30,0.95)";ctx.strokeStyle=accent;ctx.lineWidth=1.2;', "bubble fill")
src = swap(src, "rrect(ctx,bx,by,bw,bh,4);ctx.fill();ctx.stroke();",
 'rrect(ctx,bx,by,bw,bh,9);ctx.fill();ctx.stroke();ctx.fillStyle="rgba(255,255,255,0.06)";rrect(ctx,bx+2,by+2,bw-4,bh/2-2,7);ctx.fill();', "bubble shape")
src = swap(src, 'ctx.fillStyle="#1a140d";ctx.fill();', 'ctx.fillStyle="rgba(22,16,30,0.95)";ctx.fill();', "bubble tail")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 11 edits applied (sheets, cat panel, bubbles).")
