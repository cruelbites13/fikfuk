content = open('src/App.jsx', encoding='utf-8').read()

old = '''function drawBubble(ctx,cat,p){
  if(cat.revealAlpha<=0||!cat.confessions.length)return;
  const text=cat.confessions[cat.confessions.length-1];
  const cx=cat.x+5.5*p,cy=cat.y-4;
  ctx.save();ctx.globalAlpha=cat.revealAlpha*(cat.idle?0.35:1);
  ctx.font=`${Math.max(7,p*1.8)}px ${ff}`;
  const tw=ctx.measureText(text).width,pad=10,bh=26,bw=tw+pad*2;
  const bx=cx-bw/2,by=cy-bh-12;
  ctx.fillStyle="rgba(0,0,0,0.45)";rrect(ctx,bx+2,by+2,bw,bh,4);ctx.fill();
  ctx.fillStyle="#0d0d1a";ctx.strokeStyle="#ff4444";ctx.lineWidth=1.5;
  rrect(ctx,bx,by,bw,bh,4);ctx.fill();ctx.stroke();
  ctx.beginPath();ctx.moveTo(cx-5,by+bh);ctx.lineTo(cx,by+bh+10);ctx.lineTo(cx+5,by+bh);
  ctx.fillStyle="#0d0d1a";ctx.fill();
  ctx.beginPath();ctx.moveTo(cx-5,by+bh);ctx.lineTo(cx,by+bh+10);ctx.lineTo(cx+5,by+bh);
  ctx.strokeStyle="#ff4444";ctx.lineWidth=1.5;ctx.stroke();
  ctx.fillStyle="#ff8888";ctx.fillText(text,bx+pad,by+bh-8);
  ctx.restore();
}'''

new = '''function drawBubble(ctx,cat,p){
  if(cat.revealAlpha<=0||!cat.confessions.length)return;
  const text=cat.confessions[cat.confessions.length-1];
  const cx=cat.x+5.5*p,cy=cat.y-4;
  const isPatates=cat.sysType==="patates";
  const accent=isPatates?"#ffaa44":"#ff4444";
  const textCol=isPatates?"#ffd9a0":"#ff8888";
  ctx.save();ctx.globalAlpha=cat.revealAlpha*(cat.idle?0.35:1);
  ctx.font=`${Math.max(7,p*1.8)}px ${ff}`;
  const tw=ctx.measureText(text).width,pad=10,bh=26,bw=tw+pad*2;
  const bx=cx-bw/2,by=cy-bh-12;
  ctx.fillStyle="rgba(0,0,0,0.45)";rrect(ctx,bx+2,by+2,bw,bh,4);ctx.fill();
  ctx.fillStyle="#1a140d";ctx.strokeStyle=accent;ctx.lineWidth=1.5;
  rrect(ctx,bx,by,bw,bh,4);ctx.fill();ctx.stroke();
  ctx.beginPath();ctx.moveTo(cx-5,by+bh);ctx.lineTo(cx,by+bh+10);ctx.lineTo(cx+5,by+bh);
  ctx.fillStyle="#1a140d";ctx.fill();
  ctx.beginPath();ctx.moveTo(cx-5,by+bh);ctx.lineTo(cx,by+bh+10);ctx.lineTo(cx+5,by+bh);
  ctx.strokeStyle=accent;ctx.lineWidth=1.5;ctx.stroke();
  ctx.fillStyle=textCol;ctx.fillText(text,bx+pad,by+bh-8);
  ctx.restore();
}'''

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Warm bubble for Patates added')
else:
    print('FAILED')