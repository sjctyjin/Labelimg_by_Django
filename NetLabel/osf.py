import os

dir = os.listdir('static/userdata/jim')

user_dirs = []
for i in dir:
    y = i.split('-')[0].split('_')[0][0:4]
    m = i.split('-')[0].split('_')[0][4:6]
    d = i.split('-')[0].split('_')[0][6:8]
    h = i.split('-')[0].split('_')[1][0:2]
    min = i.split('-')[0].split('_')[1][2:4]
    s = i.split('-')[0].split('_')[1][4:6]
    user_dirs.append([i, f'{y}-{m}-{d} {h}:{min}:{s}'])
    print(f'{y}-{m}-{d} {h}:{min}:{s}')


for a in user_dirs:
    print(a[0])
    print(a[1])
