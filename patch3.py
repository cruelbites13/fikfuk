content = open('src/App.jsx', encoding='utf-8').read()

old = '    return[pc,ac];'
new = '    return[pc,ac,pat];'

if old in content:
    content = content.replace(old, new)
    open('src/App.jsx', 'w', encoding='utf-8').write(content)
    print('Patates added to return array')
else:
    print('FAILED')