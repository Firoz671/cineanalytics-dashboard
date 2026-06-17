import re
with open('D:\\MOVIES DATA\\imdb_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Count KPI cards by looking for card values
kpi_labels = ['Total Movies', 'Avg Rating', 'Highest Rated', 'Total Revenue', 'Genres', 'Countries', 'Median Budget', 'Median Revenue']
found_labels = [l for l in kpi_labels if l in html]
print(f"KPI labels found: {len(found_labels)}/8")
for l in found_labels:
    print(f"  - {l}")

# Count gradient backgrounds (each card has one)
gradients = html.count('linear-gradient')
print(f"\nGradient cards: {gradients}")

# Count chart plot divs
plots = len(re.findall(r'Plotly\.newPlot', html))
print(f"Plotly.newPlot calls: {plots}")

# Verify app.py imports
with open('D:\\MOVIES DATA\\app.py', 'r', encoding='utf-8') as f:
    app_py = f.read()
key_imports = ['plotly.express', 'plotly.graph_objects', 'plotly.subplots', 'dash import']
for imp in key_imports:
    print(f"  app.py contains '{imp}': {imp in app_py}")
