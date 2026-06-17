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
        print(f'Outputs: {len(cell.get("outputs", []))}')
        for oi, o in enumerate(cell.get('outputs', [])):
            print(f'  Output {oi}: type={o["output_type"]}')
            if 'text/html' in o.get('data', {}):
                html = o['data']['text/html']
                print(f'  HTML length: {len(html)}')
                print(f'  Preview: {html[:300]}')
            elif o['output_type'] == 'stream':
                print(f'  Text: {"".join(o.get("text", [""]))[:200]}')
        break

# Count HTML vs text vs error outputs
html_count = 0
for ci, (cell_idx, cell) in enumerate(code_cells):
    for o in cell.get('outputs', []):
        if 'text/html' in o.get('data', {}):
            html_count += 1
print(f'\nTotal HTML outputs: {html_count}')
