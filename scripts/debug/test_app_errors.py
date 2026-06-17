"""Start the Dash app and simulate callbacks via direct function calls"""
import sys, traceback, json
sys.path.insert(0, 'D:/MOVIES DATA/dashboard')

# Patch the app module to add logging
import builtins
original_print = builtins.print

# We'll directly test the chart functions and exec_section code
import pandas as pd, numpy as np

df = pd.read_csv('D:/MOVIES DATA/data/processed/cleaned_imdb_movies.csv', encoding='utf-8-sig',
                  parse_dates=['release_date'], low_memory=False)
df['year'] = df['release_date'].dt.year
df['decade'] = (df['year'] // 10) * 10
df['primary_genre'] = df['genre'].str.split(',').str[0].str.strip()
df['log_budget'] = np.log1p(df['budget'])
df['log_revenue'] = np.log1p(df['revenue'])
df['roi'] = np.where(df['budget'] > 0, (df['revenue'] - df['budget']) / df['budget'], 0)

YEAR_MIN, YEAR_MAX = int(df['year'].min()), int(df['year'].max())
ALL_GENRES = sorted(df['primary_genre'].dropna().unique())
TOTAL = len(df)

# Simulate the EXACT f-string from exec_section (line 305)
f = df
print("=== Testing exec_section f-strings ===")
try:
    text = f'Lowest-rated genre: {f.groupby("primary_genre")["imdb_score"].mean().idxmin()} ({f.groupby("primary_genre")["imdb_score"].mean().min():.1f}). Budget-revenue correlation: r≈{np.corrcoef(f["budget"].dropna(), f["revenue"].dropna())[0,1]:.2f}.'
    print(f'SUCCESS: {text}')
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')
    print('  This is the root cause!')

print()
print("=== Testing exec_section f-strings (FIXED) ===")
try:
    temp = f[['budget', 'revenue']].dropna()
    corr = np.corrcoef(temp['budget'], temp['revenue'])[0,1]
    text = f'Lowest-rated genre: {f.groupby("primary_genre")["imdb_score"].mean().idxmin()} ({f.groupby("primary_genre")["imdb_score"].mean().min():.1f}). Budget-revenue correlation: r≈{corr:.2f}.'
    print(f'SUCCESS: {text}')
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')

print()
print("=== Testing Advanced tab f-strings ===")
try:
    text = f'T-Test: ~2 pt difference (p<0.001). ANOVA: genre effect (p<0.001). Budget-Revenue: r≈{np.corrcoef(f["budget"].dropna(),f["revenue"].dropna())[0,1]:.2f}.'
    print(f'SUCCESS: {text}')
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')

print()
print("=== Testing kpi f-strings ===")
try:
    text = f'{len(f[(f["imdb_score"] >= 75) & (f["budget"] < f["budget"].median())]):,}'
    print(f'Hidden gems count: {text}')
except Exception as e:
    print(f'Hidden gems ERROR: {type(e).__name__}: {e}')

# Test ALL chart functions within the callback-like environment
import plotly.express as px, plotly.graph_objects as go
from plotly.subplots import make_subplots

COLORS = ['#1f6feb', '#db6d28', '#2ea043', '#8957e5', '#d29922', '#1b7c83', '#da3633']

def _layout(fig, title='', h=360):
    fig.update_layout(
        title=dict(text=f'<b>{title}</b>', font=dict(size=13), x=0, xanchor='left'),
        height=h, margin=dict(l=44, r=12, t=38, b=36),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=11), hovermode='closest',
        xaxis=dict(gridcolor='rgba(128,128,128,0.07)', zerolinecolor='rgba(128,128,128,0.1)'),
        yaxis=dict(gridcolor='rgba(128,128,128,0.07)', zerolinecolor='rgba(128,128,128,0.1)'),
        colorway=COLORS)
    return fig

def chart_genre_dist(data):
    gc = data['primary_genre'].value_counts().head(15).reset_index()
    gc.columns = ['Genre','Count']
    gr = data.groupby('primary_genre')['imdb_score'].mean().reset_index()
    gr.columns = ['Genre','Avg']
    gd = gc.merge(gr, on='Genre').sort_values('Count', ascending=True)
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Bar(x=gd['Count'], y=gd['Genre'], orientation='h', marker_color='#1f6feb',
                          opacity=0.8, text=gd['Count'], textposition='outside'), secondary_y=False)
    fig.add_trace(go.Scatter(x=gd['Avg'], y=gd['Genre'], mode='markers+lines',
                              marker=dict(color='#2ea043', size=8), line=dict(color='#2ea043', width=1.5)), secondary_y=True)
    fig.update_layout(hovermode='y unified')
    fig.update_yaxes(title_text='Avg Score', secondary_y=True, range=[50, 80], showgrid=False)
    return _layout(fig, 'Genre Volume vs Average Rating', 400)

def chart_rating_dist(data):
    s = data['imdb_score'].dropna()
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=s, nbinsx=35, marker_color='#1f6feb', opacity=0.85))
    fig.add_vline(x=s.mean(), line=dict(color='#d29922', width=2, dash='dash'))
    fig.add_vline(x=s.median(), line=dict(color='#8957e5', width=2, dash='dot'))
    return _layout(fig, 'Rating Distribution', 320)

def chart_revenue_genre(data):
    order = data.groupby('primary_genre')['revenue'].median().sort_values(ascending=False).head(12).index
    pdf = data[data['primary_genre'].isin(order)].dropna(subset=['revenue'])
    fig = px.box(pdf, x='primary_genre', y='revenue', color='primary_genre',
                  color_discrete_sequence=px.colors.sequential.Viridis_r,
                  labels={'primary_genre':'Genre','revenue':'Revenue ($)'})
    fig.update_layout(showlegend=False)
    fig.update_xaxes(categoryorder='array', categoryarray=order)
    fig.update_yaxes(type='log', title='Revenue ($, log)')
    return _layout(fig, 'Revenue by Genre (Top 12 by Median)', 360)

print()
print("=== Testing chart generation ===")
for name, fn in [('genre_dist', chart_genre_dist), ('rating_dist', chart_rating_dist), ('revenue_genre', chart_revenue_genre)]:
    try:
        fig = fn(f)
        d = fig.to_dict()
        print(f'{name}: {len(d["data"])} traces ✓')
    except Exception as e:
        print(f'{name}: ERROR: {type(e).__name__}: {e}')
        traceback.print_exc()

print()
print("=== Done ===")
