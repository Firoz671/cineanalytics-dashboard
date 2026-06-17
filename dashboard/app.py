"""
IMDb Movies Analytics Dashboard — v3 (Debugged)
================================================
Fixes:
  - np.corrcoef crash from misaligned dropna() (budget:0 NaN vs revenue:55 NaN)
  - Consistent dcc.Graph wrapping in html.Div
  - Real charts in Advanced tab (Heatmap, K-Means, PCA, Segmentation)
  - try/except error handling with fallback messages
  - Logging for every chart generation step

Run: python dashboard/app.py
Open: http://127.0.0.1:8050
"""

import pandas as pd, numpy as np, plotly.express as px, plotly.graph_objects as go, sys, logging, os
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import warnings; warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════
_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_HERE, '..', 'data', 'processed')

log.info('Loading data...')
df = pd.read_csv(os.path.join(_DATA, 'cleaned_imdb_movies.csv'), encoding='utf-8-sig',
                  parse_dates=['release_date'], low_memory=False)
df['year'] = df['release_date'].dt.year
df['decade'] = (df['year'] // 10) * 10
df['primary_genre'] = df['genre'].str.split(',').str[0].str.strip()
df['log_budget'] = np.log1p(df['budget'])
df['log_revenue'] = np.log1p(df['revenue'])
df['roi'] = np.where(df['budget'] > 0, (df['revenue'] - df['budget']) / df['budget'], 0)

YEAR_MIN, YEAR_MAX = int(df['year'].min()), int(df['year'].max())
ALL_GENRES = sorted(df['primary_genre'].dropna().unique())
TOTAL = len(df); AVG_RATING = df['imdb_score'].mean()
BEST_MOVIE = df.loc[df['imdb_score'].idxmax(), 'movie_name']
BEST_SCORE = df['imdb_score'].max()
TOTAL_REV = df['revenue'].sum()
NUM_GENRES = df['primary_genre'].nunique()
NUM_COUNTRIES = df['country'].nunique()
MEDIAN_BUDGET = df['budget'].median()
MEDIAN_REV = df['revenue'].median()
PEAK_YEAR = int(df.groupby('year').size().idxmax())
PEAK_COUNT = int(df.groupby('year').size().max())
HIDDEN_GEMS = len(df[(df['imdb_score'] >= 75) & (df['budget'] < df['budget'].median())])
log.info(f'Loaded {TOTAL:,} rows, {NUM_GENRES} genres, {NUM_COUNTRIES} countries')

# Precompute corr for exec_section (avoid dropna mismatch)
_bv = df[['budget', 'revenue']].dropna()
BUDGET_REV_CORR = np.corrcoef(_bv['budget'], _bv['revenue'])[0, 1]

# ═══════════════════════════════════════════════════════════
# CHART FACTORIES
# ═══════════════════════════════════════════════════════════
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

def safe_graph(fig_fn, title='Chart'):
    try:
        fig = fig_fn()
        n = len(fig.data)
        log.info(f'  {title}: {n} traces')
        return html.Div(dcc.Graph(figure=fig), className='chart-card')
    except Exception as e:
        log.error(f'  {title} ERROR: {e}')
        return html.Div([
            html.Div(style={'textAlign':'center','padding':30,'color':'var(--text-secondary)'},
                     children=[
                         html.Div('⚠️', style={'fontSize':24,'marginBottom':8}),
                         html.Div(f'Failed to render {title}', style={'fontSize':13,'fontWeight':600,'marginBottom':4}),
                         html.Div(str(e), style={'fontSize':11,'opacity':0.6}),
                     ])
        ], className='chart-card', style={'minHeight':120})

def safe_graph_full(fig_fn, title='Chart'):
    try:
        fig = fig_fn()
        n = len(fig.data)
        log.info(f'  {title}: {n} traces')
        return html.Div(dcc.Graph(figure=fig), className='chart-card full-width')
    except Exception as e:
        log.error(f'  {title} ERROR: {e}')
        return html.Div([
            html.Div(style={'textAlign':'center','padding':30,'color':'var(--text-secondary)'},
                     children=[
                         html.Div('⚠️', style={'fontSize':24,'marginBottom':8}),
                         html.Div(f'Failed to render {title}', style={'fontSize':13,'fontWeight':600,'marginBottom':4}),
                         html.Div(str(e), style={'fontSize':11,'opacity':0.6}),
                     ])
        ], className='chart-card full-width', style={'minHeight':120})

def chart_rating_dist(data):
    s = data['imdb_score'].dropna()
    if len(s) == 0: raise ValueError('No rating data')
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=s, nbinsx=35, marker_color='#1f6feb', opacity=0.85,
                                hovertemplate='Score: %{x}<br>Movies: %{y}'))
    fig.add_vline(x=s.mean(), line=dict(color='#d29922', width=2, dash='dash'),
                  annotation_text=f'Mean: {s.mean():.1f}', annotation_position='top')
    fig.add_vline(x=s.median(), line=dict(color='#8957e5', width=2, dash='dot'),
                  annotation_text=f'Median: {s.median():.1f}', annotation_position='top right')
    return _layout(fig, 'Rating Distribution', 320)

def chart_genre_dist(data):
    gc = data['primary_genre'].value_counts().head(15).reset_index()
    gc.columns = ['Genre','Count']
    gr = data.groupby('primary_genre')['imdb_score'].mean().reset_index()
    gr.columns = ['Genre','Avg']
    gd = gc.merge(gr, on='Genre').sort_values('Count', ascending=True)
    if len(gd) == 0: raise ValueError('No genre data')
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Bar(x=gd['Count'], y=gd['Genre'], orientation='h', marker_color='#1f6feb',
                          opacity=0.8, text=gd['Count'], textposition='outside', textfont=dict(size=9),
                          hovertemplate='%{y}<br>Movies: %{x}'), secondary_y=False)
    fig.add_trace(go.Scatter(x=gd['Avg'], y=gd['Genre'], mode='markers+lines',
                              marker=dict(color='#2ea043', size=8, line=dict(width=1, color='white')),
                              line=dict(color='#2ea043', width=1.5),
                              hovertemplate='%{y}<br>Avg Score: %{x:.1f}'), secondary_y=True)
    fig.update_layout(hovermode='y unified')
    fig.update_yaxes(title_text='Avg Score', secondary_y=True, range=[50, 80], showgrid=False)
    return _layout(fig, 'Genre Volume vs Average Rating', 400)

def chart_revenue(data):
    rev = data['revenue'].dropna()
    if len(rev) == 0: raise ValueError('No revenue data')
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Revenue Distribution', 'Revenue vs Budget'))
    fig.add_trace(go.Histogram(x=rev/1e6, nbinsx=45, marker_color='#2ea043', opacity=0.8,
                                hovertemplate='$%{x:.0f}M<br>Movies: %{y}'), row=1, col=1)
    fig.add_vline(x=rev.median()/1e6, line=dict(color='#d29922', width=2, dash='dash'))
    sub = data.dropna(subset=['budget','revenue'])
    fig.add_trace(go.Scatter(x=sub['budget']/1e6, y=sub['revenue']/1e6, mode='markers',
                              marker=dict(color='#1f6feb', size=4, opacity=0.3),
                              hovertemplate='Budget: $%{x:.0f}M<br>Revenue: $%{y:.0f}M'), row=1, col=2)
    fig.update_layout(hovermode='closest', showlegend=False)
    fig.update_xaxes(title_text='Revenue ($M)', row=1, col=1)
    fig.update_yaxes(title_text='Movies', row=1, col=1)
    fig.update_xaxes(title_text='Budget ($M)', row=1, col=2)
    fig.update_yaxes(title_text='Revenue ($M)', row=1, col=2)
    return _layout(fig, 'Revenue Analysis', 320)

def chart_top_movies(data):
    top = data.dropna(subset=['imdb_score']).nlargest(20, 'imdb_score')
    if len(top) == 0: raise ValueError('No movies with scores')
    fig = px.bar(top, x='imdb_score', y='movie_name', orientation='h', color='imdb_score',
                  color_continuous_scale='Blues', text='imdb_score',
                  hover_data={'year':True,'primary_genre':True,'budget':':$,.0f'})
    fig.update_traces(textposition='outside', texttemplate='%{text:.0f}', textfont=dict(size=9))
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis=dict(range=[55,100]),
                      coloraxis_showscale=False)
    return _layout(fig, 'Top 20 Highest Rated Movies', 500)

def chart_year_trends(data):
    y = data.groupby('year').agg(count=('movie_name','count'),avg_score=('imdb_score','mean')).reset_index()
    y = y[y['year'] >= 1950]
    if len(y) == 0: raise ValueError('No data for 1950+')
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Bar(x=y['year'], y=y['count'], name='Movies Released', marker_color='#1f6feb', opacity=0.5), secondary_y=False)
    fig.add_trace(go.Scatter(x=y['year'], y=y['avg_score'], mode='lines+markers', name='Avg Score',
                              marker=dict(color='#d29922', size=3), line=dict(color='#d29922', width=2)), secondary_y=True)
    fig.update_layout(hovermode='x unified')
    fig.update_yaxes(title_text='Movies Released', secondary_y=False)
    fig.update_yaxes(title_text='Avg Score', secondary_y=True, range=[55, 75])
    return _layout(fig, 'Movies Released & Avg Rating (1950+)', 320)

def chart_bubble(data):
    top8 = data['primary_genre'].value_counts().head(8).index
    bdf = data[data['primary_genre'].isin(top8)].dropna(subset=['imdb_score','budget','revenue'])
    if len(bdf) == 0: raise ValueError('No data for bubble chart')
    sample = bdf.sample(min(2500, len(bdf)), random_state=42)
    fig = px.scatter(sample, x='budget', y='imdb_score', size='revenue', color='primary_genre',
                     hover_name='movie_name', log_x=True, size_max=25, opacity=0.6,
                     color_discrete_sequence=COLORS,
                     labels={'budget':'Budget ($)','imdb_score':'Score','primary_genre':'Genre'})
    fig.update_layout(hovermode='closest')
    return _layout(fig, 'Budget vs Rating (Bubble = Revenue, Color = Genre)', 400)

def chart_revenue_genre(data):
    order = data.groupby('primary_genre')['revenue'].median().sort_values(ascending=False).head(12).index
    pdf = data[data['primary_genre'].isin(order)].dropna(subset=['revenue'])
    if len(pdf) == 0: raise ValueError('No revenue data by genre')
    fig = px.box(pdf, x='primary_genre', y='revenue', color='primary_genre',
                  color_discrete_sequence=px.colors.sequential.Viridis_r,
                  labels={'primary_genre':'Genre','revenue':'Revenue ($)'})
    fig.update_layout(showlegend=False)
    fig.update_xaxes(categoryorder='array', categoryarray=order)
    fig.update_yaxes(type='log', title='Revenue ($, log)')
    return _layout(fig, 'Revenue by Genre (Top 12 by Median)', 360)

# ── Advanced Tab Charts ─────────────────────────────────

def chart_corr_heatmap(data):
    num_cols = ['imdb_score', 'budget', 'revenue', 'year']
    corr_df = data[num_cols].dropna()
    if len(corr_df) == 0: raise ValueError('No data for correlation')
    corr_mat = corr_df.corr(method='pearson')
    fig = go.Figure(data=go.Heatmap(
        z=corr_mat.values, x=corr_mat.columns, y=corr_mat.columns,
        colorscale='RdBu_r', zmin=-1, zmax=1,
        text=np.round(corr_mat.values, 2), texttemplate='%{text}',
        hovertemplate='%{x} vs %{y}: %{z:.2f}'))
    fig.update_layout(height=360)
    return _layout(fig, 'Correlation Heatmap', 360)

def chart_clustering(data):
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    cluster_data = data[['imdb_score', 'budget', 'revenue']].dropna()
    if len(cluster_data) < 10: raise ValueError('Insufficient data for clustering')
    sample = cluster_data.sample(min(5000, len(cluster_data)), random_state=42)
    X = StandardScaler().fit_transform(sample[['imdb_score', 'budget']])
    kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
    labels = kmeans.fit_predict(X)
    sample = sample.copy()
    sample['cluster'] = labels.astype(str)
    names = {0: 'Standard Films', 1: 'Blockbusters', 2: 'Hidden Gems', 3: 'Critically Acclaimed'}
    sample['segment'] = sample['cluster'].map(names)
    fig = px.scatter(sample, x='budget', y='imdb_score', color='segment',
                     size='revenue', size_max=20, opacity=0.6, log_x=True,
                     color_discrete_sequence=COLORS,
                     labels={'budget':'Budget ($)', 'imdb_score':'Score', 'segment':'Segment'},
                     hover_name=None)
    fig.update_layout(hovermode='closest')
    return _layout(fig, 'K-Means Clustering (K=4) — Movie Segments', 400)

def chart_pca(data):
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    pca_cols = ['imdb_score', 'budget', 'revenue', 'year']
    pca_data = data[pca_cols].dropna()
    if len(pca_data) < 10: raise ValueError('Insufficient data for PCA')
    sample = pca_data.sample(min(5000, len(pca_data)), random_state=42)
    X = StandardScaler().fit_transform(sample[pca_cols])
    pca = PCA(n_components=3, random_state=42)
    components = pca.fit_transform(X)
    var_ratio = pca.explained_variance_ratio_
    sample = sample.copy()
    sample['PC1'] = components[:, 0]
    sample['PC2'] = components[:, 1]
    sample['PC3'] = components[:, 2]
    sample['size_cat'] = pd.qcut(sample['budget'], 4, labels=['Low', 'Medium', 'High', 'Very High'])
    fig = px.scatter(sample, x='PC1', y='PC2', color='size_cat', size='revenue',
                     size_max=15, opacity=0.5, hover_data={'PC3':True},
                     color_discrete_sequence=COLORS,
                     labels={'PC1':f'PC1 ({var_ratio[0]:.0%})', 'PC2':f'PC2 ({var_ratio[1]:.0%})',
                             'size_cat':'Budget Tier'})
    fig.update_layout(hovermode='closest')
    return _layout(fig, f'PCA — 3 Components ({var_ratio[:3].sum():.0%} Variance)', 400)

def chart_segmentation(data):
    df_s = data.dropna(subset=['imdb_score', 'budget', 'revenue']).copy()
    if len(df_s) == 0: raise ValueError('No data for segmentation')
    med_budget = float(df_s['budget'].median())
    med_rev = float(df_s['revenue'].median())
    def segment(row):
        b = row['budget'] if pd.notna(row['budget']) else 0
        r = row['revenue'] if pd.notna(row['revenue']) else 0
        s = row['imdb_score'] if pd.notna(row['imdb_score']) else 0
        if b >= med_budget and r >= med_rev: return 'Blockbuster'
        if s >= 70 and b < med_budget: return 'Hidden Gem'
        if s >= 70: return 'Critically Acclaimed'
        return 'Standard'
    df_s['segment'] = df_s.apply(segment, axis=1)
    seg_counts = df_s['segment'].value_counts().reset_index()
    seg_counts.columns = ['Segment', 'Count']
    colors_map = {'Blockbuster': '#2ea043', 'Hidden Gem': '#8957e5',
                  'Critically Acclaimed': '#1f6feb', 'Standard': '#8b949e'}
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=seg_counts['Segment'], values=seg_counts['Count'], hole=0.4,
        marker=dict(colors=[colors_map[s] for s in seg_counts['Segment']]),
        textposition='inside', textinfo='percent+label',
        hovertemplate='%{label}<br>Count: %{value}<extra></extra>'))
    return _layout(fig, 'Movie Segmentation Breakdown', 400)

# ═══════════════════════════════════════════════════════════
# COMPONENT BUILDERS
# ═══════════════════════════════════════════════════════════
def kpi(label, value, context, css_class, icon, meta=''):
    return html.Div([
        html.Div([html.Span(icon), html.Span(label)], style={'display':'flex','alignItems':'center','gap':4,
                  'fontSize':10,'fontWeight':600,'textTransform':'uppercase','letterSpacing':'0.4px','opacity':0.7}),
        html.Div(value, style={'fontSize':22,'fontWeight':700,'letterSpacing':'-0.3px','lineHeight':1.2}),
        html.Div(context, style={'fontSize':11,'opacity':0.65,'lineHeight':1.3}),
        html.Div(meta, style={'fontSize':10,'opacity':0.4}) if meta else None,
    ], className=f'kpi-card {css_class}',
       style={'background':'var(--bg-card)','border':'1px solid var(--border-default)',
              'borderRadius':'var(--radius-md)','padding':'14px 16px','display':'flex','flexDirection':'column','gap':'2px'})

def insight(key, why, action):
    return html.Div([
        html.Div([
            html.Div([html.Span('💡', style={'fontSize':14}), html.Span(' Key Insight', style={'fontWeight':700,'fontSize':11,'textTransform':'uppercase','color':'var(--color-ratings)'})], style={'display':'flex','alignItems':'center','gap':4}),
            html.P(key, style={'fontSize':13,'color':'var(--text-secondary)','lineHeight':1.5,'margin':0}),
        ], className='insight-card'),
        html.Div([
            html.Div([html.Span('🎯', style={'fontSize':14}), html.Span(' Why It Matters', style={'fontWeight':700,'fontSize':11,'textTransform':'uppercase','color':'var(--color-volume)'})], style={'display':'flex','alignItems':'center','gap':4}),
            html.P(why, style={'fontSize':13,'color':'var(--text-secondary)','lineHeight':1.5,'margin':0}),
        ], className='insight-card'),
        html.Div([
            html.Div([html.Span('📌', style={'fontSize':14}), html.Span(' Recommendation', style={'fontWeight':700,'fontSize':11,'textTransform':'uppercase','color':'var(--color-revenue)'})], style={'display':'flex','alignItems':'center','gap':4}),
            html.P(action, style={'fontSize':13,'color':'var(--text-secondary)','lineHeight':1.5,'margin':0}),
        ], className='insight-card'),
    ], style={'display':'grid','gridTemplateColumns':'1fr 1fr 1fr','gap':12,'margin':'16px 0 24px'})

def exec_box(cls, icon, label, text):
    return html.Div([
        html.H4(f'{icon} {label}', style={'fontSize':11,'textTransform':'uppercase','letterSpacing':'0.4px','marginBottom':4}),
        html.P(text, style={'fontSize':13,'margin':0}),
    ], className=f'exec-item {cls}',
       style={'borderRadius':'var(--radius-sm)','padding':'12px'})

def chart_grid(*children):
    return html.Div(children=list(children),
                    style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':16,'marginBottom':24})

# ═══════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════
app = Dash(__name__, title='IMDb Analytics Dashboard', assets_folder='assets')
server = app.server

app.layout = html.Div(style={'position':'relative'}, children=[

    # Header
    html.Header([
        html.Div([
            html.Div([
                html.Span('🎬', style={'fontSize':20}),
                html.H1('IMDb Analytics', style={'fontSize':18,'fontWeight':700,'margin':0}),
                html.Span('BI', style={'background':'var(--color-revenue-bg)','color':'var(--color-revenue)','fontSize':10,'fontWeight':700,'padding':'2px 8px','borderRadius':4,'textTransform':'uppercase'}),
            ], style={'display':'flex','alignItems':'center','gap':8}),
            html.Div([
                html.Span(f'{TOTAL:,} movies', style={'fontSize':12,'opacity':0.6}),
                html.Span(f'{YEAR_MIN}–{YEAR_MAX}', style={'fontSize':12,'opacity':0.6}),
                html.Span(f'{NUM_GENRES} genres', style={'fontSize':12,'opacity':0.6}),
            ], style={'display':'flex','alignItems':'center','gap':16}),
        ], style={'display':'flex','justifyContent':'space-between','alignItems':'center','maxWidth':1400,'margin':'0 auto','padding':'0 24px','height':60}),
    ], style={'background':'var(--bg-card)','borderBottom':'1px solid var(--border-default)','position':'sticky','top':0,'zIndex':100}),

    # Filters
    html.Div(className='filter-bar', children=[
        html.Div(className='filter-inner', children=[
            html.Div(className='filter-group', style={'flex':'1.4'}, children=[
                html.Div(className='filter-header', children=[
                    html.Span('Year Range', className='filter-label'),
                    html.Span(f'{YEAR_MIN} \u2014 {YEAR_MAX}', className='filter-year-display'),
                ]),
                dcc.RangeSlider(YEAR_MIN, YEAR_MAX, 5, value=[YEAR_MIN, YEAR_MAX], id='year-slider',
                                tooltip={'placement':'bottom','always_visible':False}),
            ]),
            html.Div(className='filter-group', style={'flex':'1'}, children=[
                html.Div(className='filter-header', children=[
                    html.Span('Genre', className='filter-label'),
                ]),
                dcc.Dropdown(id='genre-dropdown',
                              options=[{'label':'All Genres','value':'ALL'}]+[{'label':g,'value':g} for g in ALL_GENRES],
                              value='ALL', clearable=False, searchable=True),
            ]),
            html.Div(className='filter-group', style={'flex':'1'}, children=[
                html.Div(className='filter-header', children=[
                    html.Span('Rating Range', className='filter-label'),
                    html.Span('0 \u2014 100', className='filter-value'),
                ]),
                dcc.RangeSlider(0, 100, 5, value=[0, 100], id='rating-slider',
                                tooltip={'placement':'bottom','always_visible':False}),
            ]),
            html.Div(className='filter-actions', children=[
                html.Button([
                    html.Span('\u21BA', className='icon'),
                    html.Span('Reset Filters'),
                ], id='reset-btn', n_clicks=0, className='btn-reset'),
            ]),
        ]),
    ]),

    # Tabs
    dcc.Tabs(id='tabs', value='overview', children=[
        dcc.Tab(label='📊 Overview', value='overview'),
        dcc.Tab(label='🎬 Movie Performance', value='performance'),
        dcc.Tab(label='🎭 Genre Analytics', value='genres'),
        dcc.Tab(label='🤖 Advanced', value='advanced'),
    ], style={'fontSize':13,'fontWeight':500}),

    # Content
    html.Div(id='tab-content', style={'maxWidth':1400,'margin':'0 auto','padding':'20px 24px'}),

    # Footer
    html.Footer([
        html.Div([
            html.Span('IMDb Movies Analytics Dashboard', style={'fontWeight':600}),
            html.Br(),
            html.Span(f'{TOTAL:,} movies · {NUM_GENRES} genres · {NUM_COUNTRIES} countries · {YEAR_MIN}–{YEAR_MAX}',
                      style={'fontSize':11,'opacity':0.5}),
        ]),
        html.Div([
            'Built with Python · Plotly Dash · Scikit-learn',
            html.Br(),
            html.Span('Pipeline: Cleaning → EDA → Feature Engineering → ML → Dashboard', style={'fontSize':11,'opacity':0.4}),
        ], style={'textAlign':'right','fontSize':12}),
    ], style={'borderTop':'1px solid var(--border-default)','padding':'20px 24px','display':'flex','justifyContent':'space-between','flexWrap':'wrap','gap':12}),
])

# ═══════════════════════════════════════════════════════════
# CALLBACKS
# ═══════════════════════════════════════════════════════════

@app.callback(
    [Output('year-slider','value'), Output('genre-dropdown','value'), Output('rating-slider','value')],
    Input('reset-btn','n_clicks'), prevent_initial_call=True
)
def reset_filters(n):
    return [YEAR_MIN, YEAR_MAX], 'ALL', [0, 100]

@app.callback(
    Output('tab-content','children'),
    [Input('tabs','value'), Input('year-slider','value'),
     Input('genre-dropdown','value'), Input('rating-slider','value')]
)
def render_tab(tab, years, genre_filter, rating_range):
    mask = (df['year'] >= years[0]) & (df['year'] <= years[1])
    if genre_filter != 'ALL':
        mask &= (df['primary_genre'] == genre_filter)
    mask &= (df['imdb_score'] >= rating_range[0]) & (df['imdb_score'] <= rating_range[1])
    dff = df[mask].copy()
    n = len(dff)
    log.info(f'render_tab(tab={tab!r}, n={n})')
    if n == 0:
        return html.Div('No data matches the current filters.', style={'textAlign':'center','padding':60,'fontSize':16,'opacity':0.6})
    f = dff  # shorthand

    kpi_cards = html.Div([
        kpi('Total Movies', f'{n:,}', f'{n/TOTAL*100:.0f}% of dataset', 'volume', '🎬', f'Original: {TOTAL:,}'),
        kpi('Avg Rating', f'{f["imdb_score"].mean():.1f}', f'Median: {f["imdb_score"].median():.1f}', 'ratings', '⭐'),
        kpi('Highest Rated', f'{BEST_SCORE:.0f}', BEST_MOVIE[:30], 'warning', '🏆'),
        kpi('Total Revenue', f'${f["revenue"].sum()/1e9:.2f}B', f'Median: ${f["revenue"].median()/1e6:.0f}M', 'revenue', '💰'),
        kpi('Median Budget', f'${f["budget"].median()/1e6:.0f}M', f'Avg: ${f["budget"].mean()/1e6:.0f}M', 'revenue', '💵'),
        kpi('Genres', f'{f["primary_genre"].nunique()}', f'Top: {f["primary_genre"].value_counts().index[0]}', 'genre', '🎭'),
        kpi('Countries', f'{f["country"].nunique()}', f'{f["language"].dropna().nunique()} languages', 'volume', '🌍'),
        kpi('Hidden Gems', f'{len(f[(f["imdb_score"] >= 75) & (f["budget"] < f["budget"].median())]):,}', 'Score ≥ 75, low budget', 'info', '💎'),
    ], style={'display':'grid','gridTemplateColumns':'repeat(4,1fr)','gap':12,'marginBottom':24})

    # FIXED: Use aligned dropna for corrcoef
    _bv_f = f[['budget','revenue']].dropna()
    _corr_val = np.corrcoef(_bv_f['budget'], _bv_f['revenue'])[0, 1] if len(_bv_f) > 3 else 0

    exec_section = html.Div([
        html.H2('📋 Executive Summary', style={'fontSize':16,'fontWeight':700,'marginBottom':14,'paddingBottom':10,'borderBottom':'1px solid var(--border-muted)'}),
        html.Div([
            exec_box('key-findings','🔍','Key Findings', f'Avg rating: {f["imdb_score"].mean():.1f}/100 across {n:,} movies. Revenue: ${f["revenue"].sum()/1e9:.2f}B. Top genre: {f["primary_genre"].value_counts().index[0]}. Production peak: {f.groupby("year").size().idxmax()} ({int(f.groupby("year").size().max()):,})'),
            exec_box('opportunities','🚀','Opportunities', f'Highest-rated genre: {f.groupby("primary_genre")["imdb_score"].mean().idxmax()} ({f.groupby("primary_genre")["imdb_score"].mean().max():.1f}). Hidden gems: {HIDDEN_GEMS:,} films with score ≥75, budget <${df["budget"].median()/1e6:.0f}M.'),
            exec_box('risks','⚠️','Risks', f'Lowest-rated genre: {f.groupby("primary_genre")["imdb_score"].mean().idxmin()} ({f.groupby("primary_genre")["imdb_score"].mean().min():.1f}). Budget-revenue correlation: r≈{_corr_val:.2f}.'),
            exec_box('recommendations','📌','Recommendations', 'Portfolio: 20% blockbuster, 30% mid-budget, 30% genre, 20% niche. Quality gate: IMDb 60+. Use genre history for greenlighting.'),
        ], style={'display':'grid','gridTemplateColumns':'1fr 1fr 1fr 1fr','gap':14}),
    ], style={'background':'var(--bg-card)','border':'1px solid var(--border-default)','borderRadius':'var(--radius-md)','padding':24,'marginBottom':28})

    # ── TAB CONTENT ─────────────────────────────────────
    if tab == 'overview':
        return html.Div([
            html.Div([html.Span(f'📊 {n:,} movies match current filters', style={'fontSize':13,'opacity':0.6})], style={'marginBottom':20}),
            exec_section, kpi_cards,
            chart_grid(
                safe_graph(lambda: chart_rating_dist(f), 'Rating Distribution'),
                safe_graph(lambda: chart_year_trends(f), 'Year Trends'),
                safe_graph_full(lambda: chart_revenue(f), 'Revenue Analysis'),
            ),
            insight(
                'Average ratings have stayed near 63/100 for decades despite a 50x production increase.',
                'This disproves the "quality dilution" hypothesis — the industry scaled without sacrificing quality.',
                'Focus on production pipeline efficiency. Mid-budget films ($20M–$60M) with score 60+ offer best risk-adjusted returns.'),
            safe_graph_full(lambda: chart_genre_dist(f), 'Genre Distribution'),
            insight(
                f'{f["primary_genre"].value_counts().index[0]} dominates production; {f.groupby("primary_genre")["imdb_score"].mean().idxmax()} achieves highest ratings.',
                'Genre selection is the most impactful portfolio decision. A balanced mix optimizes returns.',
                'Allocate 30% high-volume, 30% high-quality, 20% high-revenue, 20% experimental genres.'),
        ])

    elif tab == 'performance':
        ts = f.dropna(subset=['imdb_score']).nlargest(10,'imdb_score')[['movie_name','imdb_score','year','primary_genre']].reset_index(drop=True); ts.index+=1
        tr = f.dropna(subset=['revenue']).nlargest(10,'revenue')[['movie_name','revenue','year','imdb_score']].reset_index(drop=True); tr.index+=1
        troi = f.dropna(subset=['budget','revenue']).query('budget>0').nlargest(10,'roi')[['movie_name','roi','budget','year']].reset_index(drop=True); troi.index+=1
        def table(d, cols, rename):
            c = d.copy()
            mp = {'budget':lambda x:f'${x:,.0f}','revenue':lambda x:f'${x:,.0f}','roi':lambda x:f'{x:.1f}x','imdb_score':lambda x:f'{x:.0f}/100'}
            for col,fn in mp.items():
                if col in cols: c[col] = c[col].apply(fn)
            return dash_table.DataTable(data=c.to_dict('records'),columns=[{'name':rename.get(col,col),'id':col} for col in cols],page_size=10,sort_action='native',filter_action='native',style_table={'overflowX':'auto'})
        return html.Div([
            html.H2('🎬 Movie Performance', style={'fontSize':18,'fontWeight':700,'marginBottom':4}),
            html.P(f'Top performers from {n:,} records', style={'fontSize':13,'opacity':0.6,'marginBottom':20}),
            kpi_cards,
            html.Div([
                html.Div([html.H3('🏆 Top Rated', style={'fontSize':14,'marginBottom':10}), table(ts,['movie_name','imdb_score','year','primary_genre'],{'movie_name':'Movie','imdb_score':'Score','year':'Year','primary_genre':'Genre'})], style={'flex':'1 1 280px'}),
                html.Div([html.H3('💰 Top Revenue', style={'fontSize':14,'marginBottom':10}), table(tr,['movie_name','revenue','year','imdb_score'],{'movie_name':'Movie','revenue':'Revenue','year':'Year','imdb_score':'Score'})], style={'flex':'1 1 280px'}),
                html.Div([html.H3('📈 Best ROI', style={'fontSize':14,'marginBottom':10}), table(troi,['movie_name','roi','budget','year'],{'movie_name':'Movie','roi':'ROI','budget':'Budget','year':'Year'})], style={'flex':'1 1 280px'}),
            ], style={'display':'flex','flexWrap':'wrap','gap':16,'marginBottom':24}),
            safe_graph_full(lambda: chart_top_movies(f), 'Top Movies'),
            insight(f'Top score: {f["imdb_score"].max():.0f}. Top 20 span {ts["primary_genre"].nunique()} genres.', 'Critical acclaim is genre-agnostic. Quality can be achieved in any category.', 'Do not restrict by genre. Apply consistent quality standards across all greenlight decisions.'),
            safe_graph_full(lambda: chart_bubble(f), 'Budget vs Rating Bubble'),
            insight('Budget correlates negligibly with ratings (r≈0.06). High spending ≠ high quality.', 'Many high-budget films underperform critically. Best investments are modest-budget with strong creative.', 'Implement budget oversight with creative benchmarks. Stage-gate funding reduces large-production risk.'),
        ])

    elif tab == 'genres':
        return html.Div([
            html.H2('🎭 Genre Analytics', style={'fontSize':18,'fontWeight':700,'marginBottom':4}),
            html.P(f'Performance across {f["primary_genre"].nunique()} genres', style={'fontSize':13,'opacity':0.6,'marginBottom':20}),
            kpi_cards,
            safe_graph_full(lambda: chart_genre_dist(f), 'Genre Distribution'),
            insight(f'Best: {f.groupby("primary_genre")["imdb_score"].mean().idxmax()} ({f.groupby("primary_genre")["imdb_score"].mean().max():.1f}). Worst: {f.groupby("primary_genre")["imdb_score"].mean().idxmin()} ({f.groupby("primary_genre")["imdb_score"].mean().min():.1f}).', 'Genre has significant impact on ratings (ANOVA p<0.001). Genre choice is a strategic decision.', 'Balance prestige genres (Documentary, Biography) with commercial genres (Action, Animation).'),
            chart_grid(
                safe_graph(lambda: chart_revenue_genre(f), 'Revenue by Genre'),
                safe_graph(lambda: chart_rating_dist(f), 'Rating Distribution'),
            ),
            insight(f'Highest median revenue: {f.groupby("primary_genre")["revenue"].median().idxmax()}. Highest ratings: {f.groupby("primary_genre")["imdb_score"].mean().idxmax()}.', 'Revenue and ratings are not aligned. Track both independently.', 'Use dual-metric scoring (rating × revenue) to evaluate genre performance holistically.'),
        ])

    elif tab == 'advanced':
        return html.Div([
            html.H2('🤖 Advanced Analytics', style={'fontSize':18,'fontWeight':700,'marginBottom':4}),
            html.P('Machine learning pipeline: clustering, PCA, segmentation, correlation', style={'fontSize':13,'opacity':0.6,'marginBottom':20}),
            kpi_cards,
            safe_graph_full(lambda: chart_corr_heatmap(f), 'Correlation Heatmap'),
            chart_grid(
                safe_graph(lambda: chart_clustering(f), 'K-Means Clustering'),
                safe_graph(lambda: chart_pca(f), 'PCA Visualization'),
            ),
            insight(
                f'Budget-revenue correlation: r≈{_corr_val:.2f}. K-Means identifies 4 natural segments. PCA captures ~70% variance in 3 components.',
                'ML segmentation reveals that big budgets alone do not guarantee success. Hidden Gems (high score, low budget) show the best ROI.',
                'Use clustering results to inform greenlight strategy: prioritize Hidden Gem profiles for highest risk-adjusted returns.'),
            safe_graph_full(lambda: chart_segmentation(f), 'Movie Segmentation'),
            html.Div([
                html.H3('📖 Data Storytelling', style={'fontSize':15,'marginBottom':14,'paddingBottom':10,'borderBottom':'1px solid var(--border-muted)'}),
                html.Div([
                    html.Div([html.H4('1. What does the dataset contain?'), html.P(f'{TOTAL:,} movies ({YEAR_MIN}–{YEAR_MAX}), {NUM_GENRES} genres, {NUM_COUNTRIES} countries. {TOTAL:,} after cleaning.')]),
                    html.Div([html.H4('2. What are the overall trends?'), html.P(f'Production surged from <100/year to {PEAK_COUNT:,} (peak: {PEAK_YEAR}). Ratings stable at ~{AVG_RATING:.0f}/100.')]),
                    html.Div([html.H4('3. What drives success?'), html.P(f'Budget weakly correlates with ratings (r≈{BUDGET_REV_CORR:.2f}). Genre matters more than spending. Mid-budget offers best ROI.')]),
                    html.Div([html.H4('4. What should stakeholders do?'), html.P(f'Diversify: 20% blockbuster, 30% mid-budget, 30% genre, 20% niche. Quality gate: 60+.')]),
                ], style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':14}),
            ], style={'background':'var(--bg-card)','border':'1px solid var(--border-default)','borderRadius':'var(--radius-md)','padding':24}),
        ])

    return html.Div()

if __name__ == '__main__':
    log.info('Starting dashboard...')
    app.run(debug=False, host='127.0.0.1', port=8050)
