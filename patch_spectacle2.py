content = open('src/App.jsx', encoding='utf-8').read()

old = '''    cats:[], worldObjs:[],
    laser:{sx:-999,sy:-999,active:false}, // screen coords
    trail:[], stars:[], frame:0,
    drag:null, laserOn:false, myId:null, ready:false,
    // camera: world position of top-left corner
    cam:{x:0,y:0},
    // drag camera
    camDrag:null,
  });'''

new = '''    cats:[], worldObjs:[],
    laser:{sx:-999,sy:-999,active:false}, // screen coords
    trail:[], stars:[], frame:0,
    drag:null, laserOn:false, myId:null, ready:false,
    // camera: world position of top-left corner
    cam:{x:0,y:0},
    // drag camera
    camDrag:null,
    // reset spectacle particles
    particles:[],
  });'''

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Particles array added')
else:
    print('FAILED')
    idx = content.find('cats:[], worldObjs')
    print(repr(content[idx:idx+200]))