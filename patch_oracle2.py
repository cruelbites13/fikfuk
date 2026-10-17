content = open('src/App.jsx', encoding='utf-8').read()

old = '''if(lastTap.current.id===cat.id&&now-lastTap.current.time<400){
        setPanel({catId:cat.id,name:cat.name,confessions:[...cat.confessions],isOwn:cat.isOwn,isSys:cat.isSys,sysType:cat.sysType,eye:cat.pal.eye});
        lastTap.current={id:null,time:0};return;
      }'''

new = '''if(lastTap.current.id===cat.id&&now-lastTap.current.time<400){
        if(cat.sysType==="oracle"){
          const response=ORACLE_RESPONSES[Math.floor(Math.random()*ORACLE_RESPONSES.length)];
          setPanel({catId:cat.id,name:"oracle",confessions:[response],isOwn:false,isSys:true,sysType:"oracle",eye:cat.pal.eye,isOracleResponse:true});
        } else {
          setPanel({catId:cat.id,name:cat.name,confessions:[...cat.confessions],isOwn:cat.isOwn,isSys:cat.isSys,sysType:cat.sysType,eye:cat.pal.eye});
        }
        lastTap.current={id:null,time:0};return;
      }'''

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Oracle panel fixed')
else:
    print('FAILED')
    idx = content.find('lastTap.current.id===cat.id')
    print(repr(content[idx:idx+200]))