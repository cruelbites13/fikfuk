content = open('src/App.jsx', encoding='utf-8').read()

# Fix letter draw - use direct filter instead of toRemove
old = '''        if(obj.type==="letter"){
          obj.alpha=Math.min(1,(obj.alpha||0)+0.01);
          obj.life=(obj.life||1800)-1;
          if(obj.life<=0){toRemove.add(obj.id);}
          else {'''

new = '''        if(obj.type==="letter"){
          obj.alpha=Math.min(1,(obj.alpha||0)+0.01);
          obj.life=(obj.life||1800)-1;
          if(obj.life<=0){
            s.worldObjs=s.worldObjs.filter(o=>o.id!==obj.id);
          } else {'''

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Letter draw remove fixed')
else:
    print('FAILED')
    idx = content.find('obj.type==="letter"')
    # find the second occurrence (draw section)
    idx2 = content.find('obj.type==="letter"', idx+1)
    print(repr(content[idx2:idx2+200]))