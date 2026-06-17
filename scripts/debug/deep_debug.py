"""Deep debug: chart serialization and Plotly version check"""
import plotly.express as px, plotly.graph_objects as go, json
import pandas as pd, numpy as np, plotly

print(f'Plotly version: {plotly.__version__}')

# Check Viridis_r length
v = px.colors.sequential.Viridis_r
print(f'Viridis_r colors: {len(v)}')

# Check if px.box works
np.random.seed(42)
test = pd.DataFrame({
    'genre': np.random.choice(['A','B','C','D','E','F','G','H','I','J','K','L'], 100),
    'revenue': np.random.exponential(100, 100)
})
fig = px.box(test, x='genre', y='revenue', color='genre',
             color_discrete_sequence=v)
print(f'px.box traces: {len(fig.data)}')

# Test serialization
try:
    json_str = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    print(f'Figure JSON size: {len(json_str)} bytes')
except Exception as e:
    print(f'SERIALIZATION ERROR: {e}')

# Test make_subplots
from plotly.subplots import make_subplots
fig2 = make_subplots(specs=[[{'secondary_y': True}]])
fig2.add_trace(go.Bar(x=[1,2,3], y=[4,5,6], orientation='h'), secondary_y=False)
fig2.add_trace(go.Scatter(x=[1,2,3], y=[7,8,9], mode='lines+markers'), secondary_y=True)
try:
    json_str2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    print(f'make_subplots JSON size: {len(json_str2)} bytes')
except Exception as e:
    print(f'SERIALIZATION ERROR: {e}')

# Verify figure has 'data' key which Dash uses
fig_dict = fig.to_dict()
print(f'Figure dict keys: {list(fig_dict.keys())}')
print(f'Figure data length: {len(fig_dict["data"])}')
layout_keys = list(fig_dict.get("layout", {}).keys())
print(f'Layout keys: {layout_keys[:10]}')

# Check for common issues with Dash figure rendering
# - Empty data array
# - Missing layout
# - Invalid axis ranges
# - NaN/Inf values
print()
print("=== Validating all chart test ===")
# Load actual data
df = pd.read_csv('D:/MOVIES DATA/data/processed/cleaned_imdb_movies.csv', encoding='utf-8-sig',
                  parse_dates=['release_date'], low_memory=False)
df['primary_genre'] = df['genre'].str.split(',').str[0].str.strip()
f = df

# Test chart_revenue_genre
order = df.groupby('primary_genre')['revenue'].median().sort_values(ascending=False).head(12).index
pdf = df[df['primary_genre'].isin(order)].dropna(subset=['revenue'])
print(f'Revenue genre chart: {len(pdf)} rows, {pdf["primary_genre"].nunique()} genres')
fig3 = px.box(pdf, x='primary_genre', y='revenue', color='primary_genre',
              color_discrete_sequence=px.colors.sequential.Viridis_r)
fig3.update_layout(showlegend=False)
fig3.update_xaxes(categoryorder='array', categoryarray=order)
fig3.update_yaxes(type='log', title='Revenue ($, log)')

# Serialize and check
json_str3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
parsed = json.loads(json_str3)
print(f'  Traces: {len(parsed["data"])}')
for i, t in enumerate(parsed["data"]):
    x_len = len(t.get("x", []))
    y_len = len(t.get("y", []))
    if x_len == 0 or y_len == 0:
        print(f'  WARNING: Trace {i} has empty x({x_len}) or y({y_len})')
    has_nan_x = any(v is None or (isinstance(v, float) and np.isnan(v)) for v in t.get("x", []) if v is not None)
    has_nan_y = any(v is None or (isinstance(v, float) and np.isnan(v)) for v in t.get("y", []) if v is not None)
    if has_nan_x or has_nan_y:
        print(f'  WARNING: Trace {i} has NaN values')

print(f'  JSON size: {len(json_str3)} bytes')
print()

# Test chart_bubble
top8 = df['primary_genre'].value_counts().head(8).index
bdf = df[df['primary_genre'].isin(top8)].dropna(subset=['imdb_score','budget','revenue'])
sample = bdf.sample(min(2500, len(bdf)), random_state=42)
fig4 = px.scatter(sample, x='budget', y='imdb_score', size='revenue', color='primary_genre',
                  hover_name='movie_name', log_x=True, size_max=25, opacity=0.6)
json_str4 = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
parsed4 = json.loads(json_str4)
print(f'Bubble chart: {len(parsed4["data"])} traces, {len(json_str4)} bytes')
for i, t in enumerate(parsed4["data"]):
    x_len = len(t.get("x", []))
    y_len = len(t.get("y", []))
    if x_len == 0 or y_len == 0:
        print(f'  WARNING: Trace {i} has empty x({x_len}) or y({y_len})')

print()
print("=== Validation complete ===")
