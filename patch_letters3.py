content = open('src/App.jsx', encoding='utf-8').read()

old = '''            ctx.font="16px serif";ctx.fillText("✉",sx-8,sy+8);'''

new = '''            // pixel envelope instead of emoji
            ctx.fillStyle="rgba(150,180,255,0.8)";
            ctx.fillRect(sx-8,sy-6,16,12);
            ctx.strokeStyle="rgba(100,130,220,0.9)";ctx.lineWidth=1;
            ctx.strokeRect(sx-8,sy-6,16,12);
            // envelope flap lines
            ctx.beginPath();ctx.moveTo(sx-8,sy-6);ctx.lineTo(sx,sy+1);ctx.lineTo(sx+8,sy-6);
            ctx.stroke();'''

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Letter icon fixed')
else:
    print('FAILED')
    idx = content.find('serif')
    print(repr(content[idx-20:idx+60]))