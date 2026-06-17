import os, re

print("=" * 60)
print("VERIFICATION REPORT")
print("=" * 60)

# 1. Check files exist
files = ['imdb_dashboard.html', 'app.py', 'README.md']
for f in files:
    path = os.path.join('D:\\MOVIES DATA', f)
    exists = os.path.exists(path)
    size = os.path.getsize(path) / 1024 if exists else 0
    status = 'OK' if exists else 'MISSING'
    print(f"  {f:<30} {status} ({size:.1f} KB)")

print()

# 2. Validate HTML structure
with open('D:\\MOVIES DATA\\imdb_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

checks = [
    ('DOCTYPE', '<!DOCTYPE html>' in html),
    ('Plotly.js script', 'plotly' in html.lower()),
    ('Closing html tag', '</html>' in html),
    ('KPI section', 'Total Movies' in html),
    ('KPI cards (8)', html.count('kpi-card') >= 8),
    ('All 7 charts embedded', html.count('plot-container') >= 7),
    ('Chart divs with IDs', html.count('chart-') >= 7),
    ('Responsive meta tag', 'viewport' in html),
    ('Dark background', '#0d1117' in html),
    ('Footer section', 'footer' in html.lower()),
    ('Insights section', 'Key Insights' in html),
    ('No broken chart divs', html.count('<div class="chart-card') >= 7),
]
print("HTML Dashboard Validation:")
for name, passed in checks:
    print(f"  {'[PASS]' if passed else '[FAIL]'} {name}")

# Count Plotly chart divs
plotly_divs = re.findall(r'<div id="[^"]*"[^>]*class="plotly-graph-div"', html)
print(f"\n  Plotly chart divs found: {len(plotly_divs)}")

# Extract chart titles from the HTML
titles = re.findall(r'<h3>([^<]+)</h3>', html)
print(f"  Chart titles in cards: {len(titles)}")
for t in titles:
    print(f"    - {t}")

print()

# 3. Validate app.py syntax
try:
    import py_compile
    py_compile.compile('D:\\MOVIES DATA\\app.py', doraise=True)
    print("app.py: [PASS] No syntax errors")
except py_compile.PyCompileError as e:
    print(f"app.py: [FAIL] {e}")

print()

# 4. Check notebook still clean
import json
with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
errors = sum(1 for c in code_cells if any(o['output_type'] == 'error' for o in c.get('outputs', [])))
print(f"Notebook: {len(code_cells)} code cells, {errors} errors")

# 5. Check CSV files exist
csvs = ['cleaned_imdb_movies.csv', 'feature_engineered_imdb_movies.csv']
for csv_name in csvs:
    path = os.path.join('D:\\MOVIES DATA', csv_name)
    if os.path.exists(path):
        size_mb = os.path.getsize(path) / 1e6
        print(f"  {csv_name:<40} {size_mb:.1f} MB")
    else:
        print(f"  {csv_name:<40} MISSING")

print()
print("=" * 60)
print("VERIFICATION COMPLETE")
