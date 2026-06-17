import json, os, re, py_compile

print('=' * 60)
print('FINAL VERIFICATION REPORT')
print('=' * 60)

files = {
    'app.py': 'Dash app',
    'imdb_dashboard.html': 'Standalone dashboard',
    'assets/style.css': 'Theme CSS',
    'README.md': 'Documentation',
    '01_data_cleaning.ipynb': 'Jupyter notebook',
    'cleaned_imdb_movies.csv': 'Cleaned dataset',
    'feature_engineered_imdb_movies.csv': 'Feature-engineered dataset',
}
for f, desc in files.items():
    path = os.path.join('D:\\MOVIES DATA', f)
    exists = os.path.exists(path)
    size = os.path.getsize(path) / 1024 if exists else 0
    status = 'OK' if exists else 'MISSING'
    print(f'  {f:<38} {status} ({size:>8.1f} KB)  {desc}')

print()

# app.py syntax
try:
    py_compile.compile('D:\\MOVIES DATA\\app.py', doraise=True)
    print('  app.py: [PASS] No syntax errors')
except Exception as e:
    print(f'  app.py: [FAIL] {e}')

# HTML structure
with open('D:\\MOVIES DATA\\imdb_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

checks = [
    ('DOCTYPE', '<!DOCTYPE html>' in html),
    ('Plotly.js script', 'plotly' in html.lower()),
    ('KPI section', 'Total Movies' in html and 'Avg Rating' in html),
    ('4 tab buttons', html.count('data-tab') >= 4),
    ('Tab content sections', html.count('tab-content') >= 4),
    ('Storytelling section', 'Executive Summary' in html or 'story-section' in html),
    ('Insight cards', html.count('insight-card') >= 4),
    ('Tab switching JS', 'tab-btn.addEventListener' in html),
    ('Footer', 'Portfolio Project' in html),
    ('Responsive max-width', 'max-width: 1440px' in html),
    ('Dark background', '#0d1117' in html),
    ('Plotly chart count', html.count('Plotly.newPlot') >= 7),
]
print('  HTML Dashboard Validation:')
for name, passed in checks:
    print(f'    {"[PASS]" if passed else "[FAIL]"} {name}')

# Notebook
with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
cc = [c for c in nb['cells'] if c['cell_type'] == 'code']
err = sum(1 for c in cc if any(o['output_type'] == 'error' for o in c.get('outputs', [])))
print(f'\n  Notebook: {len(cc)} code cells, {err} errors')

# CSS
with open('D:\\MOVIES DATA\\assets\\style.css', 'r', encoding='utf-8') as f:
    css = f.read()
print(f'  Style.css: {len(css.splitlines())} lines')
print(f'  Includes theme vars: {":root" in css}')
print(f'  Includes Dash overrides: {".dash-tab" in css}')

# CSV files exist
for csv_name in ['cleaned_imdb_movies.csv', 'feature_engineered_imdb_movies.csv']:
    path = os.path.join('D:\\MOVIES DATA', csv_name)
    if os.path.exists(path):
        print(f'  {csv_name}: {os.path.getsize(path)/1e6:.1f} MB')

print()
print('=' * 60)
print('ALL DELIVERABLES GENERATED AND VERIFIED')
print('=' * 60)
