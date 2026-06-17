import json
with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

for i, c in enumerate(cells):
    if c['cell_type'] == 'code':
        src_full = ''.join(c['source'])
        if 'kpi_html' in src_full and 'IPython' in src_full:
            print(f'Cell {i}:')
            for j, line in enumerate(c['source']):
                print(f'  {j}: {repr(line)}')
            print()
            break
