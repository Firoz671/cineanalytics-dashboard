import json, re

with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
code_cells = [(i, c) for i, c in enumerate(cells) if c['cell_type'] == 'code']

# Extract all Plotly chart HTMLs and KPI info
charts = []
kpi_html = None

for ci, (cell_idx, cell) in enumerate(code_cells):
    src = '\n'.join(cell['source'])
    outputs = cell.get('outputs', [])
    
    for o in outputs:
        data = o.get('data', {})
        
        # Capture Plotly chart HTML
        if 'text/html' in data:
            html = data['text/html']
            if 'Plotly' in html or 'plotly' in html:
                # Determine chart title from nearby source or output
                chart_info = {'html': html, 'title': f'Chart {len(charts)+1}'}
                
                # Try to extract title from HTML
                m = re.search(r'title[^<>]*>([^<]+)', html)
                if m:
                    chart_info['title'] = m.group(1).strip()
                
                # Look at source for context
                src_lines = src.split('\n')
                for line in src_lines:
                    line_stripped = line.strip()
                    if 'title=' in line_stripped:
                        m2 = re.search(r"title='([^']+)'", line_stripped)
                        if not m2:
                            m2 = re.search(r'title="([^"]+)"', line_stripped)
                        if m2:
                            chart_info['title'] = m2.group(1)
                            break
                
                charts.append(chart_info)
                print(f"Chart {len(charts)}: {chart_info['title'][:60]}")
        
        # Capture KPI HTML
        if 'text/html' in data and 'kpi' not in str(data.get('text/plain', '')).lower():
            html_content = data['text/html']
            if any(css_class in html_content for css_class in ['gradient', 'flex-wrap', 'linear-gradient']):
                if 'Total Movies' in html_content or 'Avg Rating' in html_content:
                    kpi_html = html_content
                    print(f"\nKPI HTML captured (len={len(kpi_html)})")

print(f"\nTotal Plotly charts extracted: {len(charts)}")
print(f"KPI HTML found: {kpi_html is not None}")
