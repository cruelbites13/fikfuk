content = open('src/App.jsx', encoding='utf-8').read()

old = '''    const pc=makeCat(cx-300,cy+200,SYS_PAL_PRIVACY,"policy",false,true,"privacy");
    pc.confessions=[...PRIVACY_LINES];
    const ac=makeCat(cx+300,cy+200,SYS_PAL_ABOUT,"about",false,true,"about");
    ac.confessions=[...ABOUT_LINES];'''

new = '''    const pc=makeCat(cx-300,cy+200,SYS_PAL_PRIVACY,"policy",false,true,"privacy");
    pc.confessions=[...PRIVACY_LINES];
    const ac=makeCat(cx+300,cy+200,SYS_PAL_ABOUT,"about",false,true,"about");
    ac.confessions=[...ABOUT_LINES];
    // patates - tribute cat, always present near spawn
    const pat=makeCat(cx,cy-250,SYS_PAL_PATATES,"patates",false,true,"patates");
    pat.confessions=[...PATATES_LINES];
    pat.wanderTimer=0;'''

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Patates spawn added')
else:
    print('FAILED')