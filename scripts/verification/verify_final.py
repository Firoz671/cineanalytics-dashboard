import json
with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
code_cells = [(i, c) for i, c in enumerate(cells) if c['cell_type'] == 'code']

# Check all display_data outputs
html_count = 0
png_count = 0
for ci, (cell_idx, cell) in enumerate(code_cells):
    outputs = cell.get('outputs', [])
    for o in outputs:
        data = o.get('data', {})
        if 'text/html' in data:
            html_count += 1
            if html_count <= 5:
                print(f'Cell {ci}: HTML output (len={len(data["text/html"])})')
        if 'image/png' in data:
            png_count += 1
            if png_count <= 3:
                print(f'Cell {ci}: PNG output (len={len(data["image/png"])})')

print(f'\nTotal HTML outputs: {html_count}')
print(f'Total PNG outputs: {png_count}')

# Check KPI cell
kpi_src = None
for ci, (cell_idx, cell) in enumerate(code_cells):
    src = '\n'.join(cell['source'])
    if 'kpi_html' in src:
        print(f'\nKPI cell index: {ci}')
        print(f'Outputs: {len(cell.get("outputs", []))}')
        for o in cell.get('outputs', []):
            print(f'  type={o["output_type"]}')
            if 'text/html' in o.get('data', {}):
                html = o['data']['text/html']
                print(f'  HTML length: {len(html)}')
                print(f'  Preview: {html[:200]}')
        break

# Check export CSV exists
import os
csv_path = 'D:\\MOVIES DATA\\feature_engineered_imdb_movies.csv'
if os.path.exists(csv_path):
    size = os.path.getsize(csv_path)
    print(f'\nFeature-engineered CSV exists: {csv_path} ({size/1e6:.1f} MB)')
else:
    print(f'\nFeature-engineered CSV NOT found!')
