"""Test all chart functions and identify blank chart causes"""
import pandas as pd, numpy as np, sys
sys.path.insert(0, 'D:/MOVIES DATA/dashboard')
sys.stdout.reconfigure(encoding='utf-8')

# Load data same as app.py
df = pd.read_csv('D:/MOVIES DATA/data/processed/cleaned_imdb_movies.csv', encoding='utf-8-sig',
                  parse_dates=['release_date'], low_memory=False)
df['year'] = df['release_date'].dt.year
df['decade'] = (df['year'] // 10) * 10
df['primary_genre'] = df['genre'].str.split(',').str[0].str.strip()
df['log_budget'] = np.log1p(df['budget'])
df['log_revenue'] = np.log1p(df['revenue'])
df['roi'] = np.where(df['budget'] > 0, (df['revenue'] - df['budget']) / df['budget'], 0)

print(f'=== DATA SUMMARY ===')
print(f'Rows: {len(df):,}')
print(f'Columns: {list(df.columns)}')
print(f'primary_genre NaN: {df["primary_genre"].isna().sum()}')
print(f'imdb_score NaN: {df["imdb_score"].isna().sum()}')
print(f'budget NaN: {df["budget"].isna().sum()}')
print(f'revenue NaN: {df["revenue"].isna().sum()}')
print(f'Unique genres: {df["primary_genre"].nunique()}')
print(f'Revenue >0: {(df["revenue"]>0).sum()}')
print(f'Budget >0: {(df["budget"]>0).sum()}')

# Simulate filter
mask = (df['year'] >= df['year'].min()) & (df['year'] <= df['year'].max())
dff = df[mask].copy()
f = dff

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

def chart_rating_dist(data):
    s = data['imdb_score'].dropna()
    print(f'  rating_dist: {len(s)} scores, mean={s.mean():.1f}')
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=s, nbinsx=35, marker_color='#1f6feb', opacity=0.85))
    fig.add_vline(x=s.mean(), line=dict(color='#d29922', width=2, dash='dash'))
    fig.add_vline(x=s.median(), line=dict(color='#8957e5', width=2, dash='dot'))
    return _layout(fig, 'Rating Distribution', 320)

def chart_genre_dist(data):
    gc = data['primary_genre'].value_counts().head(15).reset_index()
    gc.columns = ['Genre','Count']
    gr = data.groupby('primary_genre')['imdb_score'].mean().reset_index()
    gr.columns = ['Genre','Avg']
    gd = gc.merge(gr, on='Genre').sort_values('Count', ascending=True)
    print(f'  genre_dist: {len(gd)} genres, count range={gd["Count"].min()}-{gd["Count"].max()}')
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Bar(x=gd['Count'], y=gd['Genre'], orientation='h', marker_color='#1f6feb',
                          opacity=0.8, text=gd['Count'], textposition='outside'), secondary_y=False)
    fig.add_trace(go.Scatter(x=gd['Avg'], y=gd['Genre'], mode='markers+lines',
                              marker=dict(color='#2ea043', size=8), line=dict(color='#2ea043', width=1.5)), secondary_y=True)
    fig.update_layout(hovermode='y unified')
    fig.update_yaxes(title_text='Avg Score', secondary_y=True, range=[50, 80], showgrid=False)
    return _layout(fig, 'Genre Volume vs Average Rating', 400)

def chart_revenue_genre(data):
    order = data.groupby('primary_genre')['revenue'].median().sort_values(ascending=False).head(12).index
    pdf = data[data['primary_genre'].isin(order)].dropna(subset=['revenue'])
    print(f'  revenue_genre: {len(pdf)} rows, {len(order)} genres in order')
    if pdf.empty:
        print('  WARNING: pdf is empty!')
        fig = go.Figure()
        fig.add_annotation(text='No revenue data available', showarrow=False, font=dict(size=16))
        return _layout(fig, 'Revenue by Genre', 360)
    fig = px.box(pdf, x='primary_genre', y='revenue', color='primary_genre',
                  color_discrete_sequence=px.colors.sequential.Viridis_r)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(categoryorder='array', categoryarray=order)
    fig.update_yaxes(type='log', title='Revenue ($, log)')
    return _layout(fig, 'Revenue by Genre (Top 12 by Median)', 360)

def chart_bubble(data):
    top8 = data['primary_genre'].value_counts().head(8).index
    bdf = data[data['primary_genre'].isin(top8)].dropna(subset=['imdb_score','budget','revenue'])
    print(f'  bubble: {len(bdf)} rows after dropna')
    if len(bdf) == 0:
        print('  WARNING: bdf is empty!')
        fig = go.Figure()
        fig.add_annotation(text='No data available for bubble chart', showarrow=False)
        return _layout(fig, 'Budget vs Rating', 400)
    sample = bdf.sample(min(2500, len(bdf)), random_state=42)
    print(f'  bubble sample: {len(sample)} rows')
    fig = px.scatter(sample, x='budget', y='imdb_score', size='revenue', color='primary_genre',
                     hover_name='movie_name', log_x=True, size_max=25, opacity=0.6,
                     color_discrete_sequence=COLORS)
    fig.update_layout(hovermode='closest')
    return _layout(fig, 'Budget vs Rating (Bubble = Revenue, Color = Genre)', 400)

# Test each chart function
print(f'\n=== TESTING CHART FUNCTIONS ===')
for name, fn in [('rating_dist', chart_rating_dist), ('genre_dist', chart_genre_dist),
                  ('revenue_genre', chart_revenue_genre), ('bubble', chart_bubble)]:
    try:
        fig = fn(f)
        traces = len(fig.data)
        print(f'  {name}: {traces} traces, layout height={fig.layout.height}')
    except Exception as e:
        print(f'  {name}: ERROR: {e}')

print(f'\n=== TESTING WITH FILTERED DATA (year>2010, genre=Drama) ===')
mask2 = (df['year'] >= 2010) & (df['primary_genre'] == 'Drama') & (df['imdb_score'] >= 50)
f2 = df[mask2].copy()
print(f'Filtered rows: {len(f2)}')
for name, fn in [('rating_dist', chart_rating_dist), ('genre_dist', chart_genre_dist),
                  ('revenue_genre', chart_revenue_genre), ('bubble', chart_bubble)]:
    try:
        fig = fn(f2)
        traces = len(fig.data)
        print(f'  {name}: {traces} traces')
    except Exception as e:
        print(f'  {name}: ERROR: {e}')

print(f'\nDone.')
