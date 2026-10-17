content = open('src/App.jsx', encoding='utf-8').read()

old = '        if(!cat.isSys){cat.x+=cat.vx;cat.y+=cat.vy;}'
new = '        if(!cat.isSys||cat.sysType==="patates"){cat.x+=cat.vx;cat.y+=cat.vy;}'

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Patates can now move')
else:
    print('FAILED')