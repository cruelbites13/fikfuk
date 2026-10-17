content = open('src/App.jsx', encoding='utf-8').read()

old = 'const ABOUT_LINES  =["fikfuk.wtf","a canvas of strangers","& their pixel cats","built by cruelbites","donate via solana","double-tap to donate"];'

new = old + '''
const SYS_PAL_PATATES={ body:"#e07b39",shadow:"#a85a28",stripe:"#c4672f",inner:"#ffd9a0",eye:"#ffcc66",pupil:"#7a4a10",nose:"#ffb6c1",_name:"patates" };
const PATATES_LINES=["thank u for taking care of me","i loved being clingy with u","my naughty days were the best days","i am okay now, dont worry","i still hear u calling my name","u gave me a good life"];'''

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Patates palette and lines added')
else:
    print('FAILED')