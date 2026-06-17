"""Simulate the Dash callback environment to find the bug"""
import pandas as pd, numpy as np, sys, traceback, json
import plotly.express as px, plotly.graph_objects as go
from plotly.subplots import make_subplots

# Same data loading as app.py
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
    fig = px.box(pdf, x='primary_genre', y='revenue', color='primary_genre',
                  color_discrete_sequence=px.colors.sequential.Viridis_r,
                  labels={'primary_genre':'Genre','revenue':'Revenue ($)'})
    fig.update_layout(showlegend=False)
    fig.update_xaxes(categoryorder='array', categoryarray=order)
    fig.update_yaxes(type='log', title='Revenue ($, log)')
    return _layout(fig, 'Revenue by Genre (Top 12 by Median)', 360)

def chart_bubble(data):
    top8 = data['primary_genre'].value_counts().head(8).index
    bdf = data[data['primary_genre'].isin(top8)].dropna(subset=['imdb_score','budget','revenue'])
    sample = bdf.sample(min(2500, len(bdf)), random_state=42)
    fig = px.scatter(sample, x='budget', y='imdb_score', size='revenue', color='primary_genre',
                     hover_name='movie_name', log_x=True, size_max=25, opacity=0.6,
                     color_discrete_sequence=COLORS,
                     labels={'budget':'Budget ($)','imdb_score':'Score','primary_genre':'Genre'})
    fig.update_layout(hovermode='closest')
    return _layout(fig, 'Budget vs Rating (Bubble = Revenue, Color = Genre)', 400)

# Simulate the exact same callback logic
def render_tab(tab, years, genre_filter, rating_range):
    print(f'\n=== render_tab(tab={tab!r}) ===')
    mask = (df['year'] >= years[0]) & (df['year'] <= years[1])
    if genre_filter != 'ALL':
        mask &= (df['primary_genre'] == genre_filter)
    mask &= (df['imdb_score'] >= rating_range[0]) & (df['imdb_score'] <= rating_range[1])
    dff = df[mask].copy()
    n = len(dff)
    print(f'Filtered: {n} rows')
    if n == 0:
        return
    f = dff

    # KPI generation (simplified - just check it doesn't crash)
    best = f['imdb_score'].max()
    top_g = f['primary_genre'].value_counts().index[0]
    try:
        r = np.corrcoef(f['budget'].dropna(), f['revenue'].dropna())[0,1]
        print(f'Budget-Revenue corr: {r:.2f}')
    except Exception as e:
        print(f'Corr ERROR: {e}')

    if tab == 'overview':
        charts = [
            ('rating_dist', lambda: chart_rating_dist(f)),
            ('year_trends', lambda: chart_genre_dist(f)),  # Note: simplified
            ('revenue_genre', lambda: chart_revenue_genre(f)),
        ]
    elif tab == 'performance':
        charts = [
            ('top_movies', lambda: chart_rating_dist(f)),  # simplified
            ('bubble', lambda: chart_bubble(f)),
        ]
    elif tab == 'genres':
        charts = [
            ('genre_dist', lambda: chart_genre_dist(f)),
            ('revenue_genre', lambda: chart_revenue_genre(f)),
            ('rating_dist', lambda: chart_rating_dist(f)),
        ]
    elif tab == 'advanced':
        charts = [
            ('bubble', lambda: chart_bubble(f)),
        ]
    else:
        charts = []

    for name, fn in charts:
        try:
            fig = fn()
            traces = len(fig.data)
            fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            print(f'  {name}: {traces} traces, {len(fig_json)} bytes, height={fig.layout.height}')
            # Check for empty traces
            if traces == 0:
                print(f'  *** WARNING: {name} has 0 traces!')
            invalid = False
            for i, t in enumerate(traces):
                x = t.get('x', [])
                y = t.get('y', [])
                if hasattr(x, '__len__') and hasattr(y, '__len__'):
                    if len(x) == 0 and len(y) == 0:
                        print(f'  *** WARNING: Trace {i} in {name} has empty x and y!')
                        invalid = True
            # Check if fig.to_dict() has empty data
            d = fig.to_dict()
            if len(d.get('data', [])) == 0:
                print(f'  *** CRITICAL: to_dict() data empty for {name}!')
        except Exception as e:
            print(f'  *** ERROR in {name}: {e}')
            traceback.print_exc()

# Test each tab
for tab in ['overview', 'performance', 'genres', 'advanced']:
    render_tab(tab, [YEAR_MIN, YEAR_MAX], 'ALL', [0, 100])

print('\n=== Done ===')
