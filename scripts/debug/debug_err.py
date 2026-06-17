import json
with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
code_cells = [(i, c) for i, c in enumerate(cells) if c['cell_type'] == 'code']

cell_idx, cell = code_cells[137]
src = '\n'.join(line.rstrip() for line in cell['source'])
print(f'Cell index: {cell_idx}, code_idx=137')
print(src[:500])
print('...')
# Find the error
for line in src.split('\n'):
    if 'update_yaxis' in line:
        print(f'ERROR LINE: {line}')
