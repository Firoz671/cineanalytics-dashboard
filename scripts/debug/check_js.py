with open('D:\\MOVIES DATA\\imdb_dashboard.html','r',encoding='utf-8') as f:
    html = f.read()
idx = html.find('// Tab switching')
if idx > 0:
    end = html.find('</script>', idx)
    js = html[idx:end]
    print(f'Tab switching JS found, length: {len(js)}')
    for c in ['querySelectorAll', 'forEach', 'addEventListener', 'classList.remove', 'classList.add', 'Plots.resize']:
        print(f'  Contains "{c}": {c in js}')
else:
    print('Tab switching JS NOT FOUND!')
