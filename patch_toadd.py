content = open('src/App.jsx', encoding='utf-8').read()

# Move toAdd and toRemove declarations before the cats loop
# First find where cats loop starts
old = '''      const toRemove=new Set();
      const toAdd=[];'''

# Check where it currently is vs where paw prints are
# Move declarations before cat loop
old2 = '''      s.cats.forEach(cat=>{
        if(cat.grabbed){cat.frame++;cat.state="sit";return;}
        cat.frame++;'''

new2 = '''      const toRemove=new Set();
      const toAdd=[];

      s.cats.forEach(cat=>{
        if(cat.grabbed){cat.frame++;cat.state="sit";return;}
        cat.frame++;'''

if old2 in content:
    # Remove old toRemove/toAdd declaration first
    content = content.replace('\n      const toRemove=new Set();\n      const toAdd=[];\n', '\n')
    # Now add them before cats loop
    content = content.replace(old2, new2)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('toAdd moved before cats loop')
else:
    print('FAILED')
    idx = content.find('s.cats.forEach(cat=>{')
    print(repr(content[idx-50:idx+50]))