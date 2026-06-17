import json
with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
code_cells = [(i, c) for i, c in enumerate(cells) if c['cell_type'] == 'code']

# Count error outputs
error_count = sum(1 for _, c in code_cells if any(o['output_type'] == 'error' for o in c.get('outputs', [])))
empty_output = sum(1 for _, c in code_cells if not c.get('outputs'))
with_image = sum(1 for _, c in code_cells if any(o['output_type'] == 'display_data' for o in c.get('outputs', [])))

print(f"Total code cells: {len(code_cells)}")
print(f"With errors: {error_count}")
print(f"With empty output: {empty_output}")
print(f"With images: {with_image}")

# Check last few cells for export and summary
last_cells = cells[-10:]
print(f"\nLast 10 cells:")
for i, c in enumerate(last_cells):
    ctype = c['cell_type']
    if ctype == 'code':
        src = ''.join(c['source'])[:100]
        has_err = any(o['output_type'] == 'error' for o in c.get('outputs', []))
        has_img = any(o['output_type'] == 'display_data' for o in c.get('outputs', []))
        has_html = any('text/html' in o.get('data', {}) for o in c.get('outputs', []))
        print(f"  {ctype}: {src[:80]}... | err={has_err} img={has_img} html={has_html}")
    else:
        src = ''.join(c['source'])[:100]
        print(f"  {ctype}: {src[:80]}...")
