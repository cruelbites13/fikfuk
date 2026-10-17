content = open('src/App.jsx', encoding='utf-8').read()

old = '''      if(s.frame%300===0&&myCat){
        const sess=loadSession();
        if(sess)saveSession({...sess,x:myCat.x,y:myCat.y,confessions:myCat.confessions});
      }'''

new = '''      if(s.frame%300===0&&myCat){
        const sess=loadSession();
        if(sess)saveSession({...sess,x:myCat.x,y:myCat.y,confessions:myCat.confessions});
        if(myCat._territory&&myCat._updatePresence)myCat._updatePresence();
      }'''

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Territory broadcast added')
else:
    print('FAILED')
    idx = content.find('s.frame%300===0')
    print(repr(content[idx:idx+200]))