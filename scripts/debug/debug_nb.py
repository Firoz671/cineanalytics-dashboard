import json
with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
code_cells = [(i, c) for i, c in enumerate(cells) if c['cell_type'] == 'code']

# Show cells around the error range
for ci, (cell_idx, cell) in enumerate(code_cells[62:82]):
    src = ''.join(cell['source'])
    print(f'=== Code cell index={cell_idx}, code_idx={ci+62} ===')
    print(f'Source (first 200 chars): {src[:200]}')
    print(f'Has outputs: {bool(cell.get("outputs"))}')
    print()
