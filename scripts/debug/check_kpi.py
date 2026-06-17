import json, re, os

with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
code_cells = [(i, c) for i, c in enumerate(cells) if c['cell_type'] == 'code']

kpi_html = None
for ci, (cell_idx, cell) in enumerate(code_cells):
    src = '\n'.join(cell['source'])
    outputs = cell.get('outputs', [])
    for o in outputs:
        if 'text/html' in o.get('data', {}):
            html = o['data']['text/html']
            if 'Total Movies' in html and 'Avg Rating' in html:
                kpi_html = html
                break
    if kpi_html:
        break

print(f"KPI HTML length: {len(kpi_html) if kpi_html else 0}")
if kpi_html:
    # Check how many cards are in it
    print(f"Total Movies count: {kpi_html.count('Total Movies')}")
    print(f"Gradient occurrences: {kpi_html.count('gradient')}")
    print(f"Cards found: {kpi_html.count('min-width:')}")
    # Extract values
    import re
    values = re.findall(r'<div style="font-size:(?:28|22|16|20)px; font-weight:bold;">([^<]+)</div>', kpi_html)
    print(f"KPI values found: {values}")
