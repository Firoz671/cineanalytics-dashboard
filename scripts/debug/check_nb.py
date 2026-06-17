import json, sys
sys.stdout.reconfigure(encoding='utf-8')

nb = json.load(open('D:\\MOVIES DATA\\01_data_cleaning.ipynb','r',encoding='utf-8'))
cells = nb['cells']
code_cells = [c for c in cells if c['cell_type'] == 'code']
md_cells = [c for c in cells if c['cell_type'] == 'markdown']
print(f'Total cells: {len(cells)}')
print(f'Code cells: {len(code_cells)}')
print(f'Markdown cells: {len(md_cells)}')
print(f'Last 3 cell types: {[c["cell_type"] for c in cells[-3:]]}')

# Show what the first few code cells contain (to understand setup)
for c in cells[:5]:
    if c['cell_type'] == 'code':
        src = ''.join(c['source'])
        print(f'\nCode cell (first 150 chars): {src[:150]}')
        break
