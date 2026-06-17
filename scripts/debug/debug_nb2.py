import json
with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
code_cells = [(i, c) for i, c in enumerate(cells) if c['cell_type'] == 'code']

# Show detailed source of cell 110 (code_idx=64)  
cell_idx, cell = code_cells[64]
src_lines = cell['source']
print(f'=== Cell index {cell_idx}, code_idx=64 ===')
print(f'Lines: {len(src_lines)}')
for i, line in enumerate(src_lines):
    print(f'  L{i}: {repr(line)[:120]}')
print()

# Also check cell 104 (code_idx=62) 
cell_idx2, cell2 = code_cells[62]
src_lines2 = cell2['source']
print(f'=== Cell index {cell_idx2}, code_idx=62 ===')
print(f'Lines: {len(src_lines2)}')
for i, line in enumerate(src_lines2):
    print(f'  L{i}: {repr(line)[:120]}')
print ()

# Check what join produces for cell 110
joined = ''.join(src_lines)
print(f'Joined cell 110 (first 200): {repr(joined[:200])}')
print()
joined2 = ''.join(src_lines2)
print(f'Joined cell 104 (first 200): {repr(joined2[:200])}')
