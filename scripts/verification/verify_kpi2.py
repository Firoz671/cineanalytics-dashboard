import json
with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
code_cells = [(i, c) for i, c in enumerate(cells) if c['cell_type'] == 'code']

# Find KPI cell
for ci, (cell_idx, cell) in enumerate(code_cells):
    src = '\n'.join(cell['source'])
    if 'kpi_html' in src:
        print(f'KPI cell index: {ci}')
        outputs = cell.get('outputs', [])
        print(f'Outputs: {len(outputs)}')
        for oi, o in enumerate(outputs):
            print(f'  Output {oi}: type={o["output_type"]}')
            if 'text/html' in o.get('data', {}):
                html = o['data']['text/html']
                print(f'  HTML length: {len(html)}')
                print(f'  First 200 chars: {html[:200]}')
            elif o['output_type'] == 'stream':
                print(f'  Text: {"".join(o.get("text", [""]))[:200]}')
        break

# Count outputs by type
html_count = 0
png_count = 0
error_count = 0
for ci, (cell_idx, cell) in enumerate(code_cells):
    for o in cell.get('outputs', []):
        if 'text/html' in o.get('data', {}):
            html_count += 1
        if 'image/png' in o.get('data', {}):
            png_count += 1
        if o['output_type'] == 'error':
            error_count += 1

print(f'\nHTML outputs: {html_count}')
print(f'PNG outputs: {png_count}')
print(f'Error outputs: {error_count}')

# Final structure
print(f'\nTotal cells: {len(cells)}')
print(f'Code cells: {len(code_cells)}')
