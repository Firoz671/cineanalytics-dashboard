"""
Comprehensive end-to-end test for all 4 dashboard tabs.
Starts the dashboard, triggers callbacks, and verifies chart rendering.
"""
import requests, json, sys, time, re

BASE = 'http://127.0.0.1:8050'

def call_dash(tab, years=None, genre='ALL', rating=None):
    """Simulate a Dash callback POST request for the render_tab function."""
    if years is None:
        years = [1950, 2025]
    if rating is None:
        rating = [0, 100]
    
    payload = {
        'output': 'tab-content.children',
        'inputs': [
            {'id': 'tabs', 'property': 'value', 'value': tab},
            {'id': 'year-slider', 'property': 'value', 'value': years},
            {'id': 'genre-dropdown', 'property': 'value', 'value': genre},
            {'id': 'rating-slider', 'property': 'value', 'value': rating},
        ]
    }
    
    resp = requests.post(f'{BASE}/_dash-update-component', json=payload)
    if resp.status_code != 200:
        print(f'  ❌ HTTP {resp.status_code}: {resp.text[:200]}')
        return None
    
    data = resp.json()
    response_data = data.get('response', data)
    
    # The response contains the rendered HTML as a multi-part response
    # Extract chart info from the response
    html_str = json.dumps(response_data)
    return response_data, html_str

def count_charts(html_str):
    """Count dcc.Graph components in the response."""
    return html_str.count('dash-graph') + html_str.count('"type":"Graph"') + html_str.count('figure":')

def check_chart_content(response_data):
    """Check if response contains actual graph content."""
    if response_data is None:
        return False, 'No response data'
    
    # Navigate to find graph references
    html_str = json.dumps(response_data)
    
    # Look for Plotly figure data
    has_data = '"data"' in html_str
    has_traces = '"type"' in html_str and ('"scatter"' in html_str.lower() or '"bar"' in html_str.lower() or '"histogram"' in html_str.lower() or '"box"' in html_str.lower() or '"heatmap"' in html_str.lower() or '"pie"' in html_str.lower())
    has_layout = '"layout"' in html_str
    has_graph = '"type":"Graph"' in html_str or 'dash-graph' in html_str
    has_error = 'Failed to render' in html_str or 'ERROR' in html_str
    
    score = sum([has_data, has_traces, has_layout, has_graph])
    
    issues = []
    if not has_data:
        issues.append('no figure data')
    if not has_traces:
        issues.append('no traces')
    if not has_layout:
        issues.append('no layout')
    if not has_graph:
        issues.append('no Graph component')
    if has_error:
        issues.append('CONTAINS ERROR MESSAGES')
    
    return score >= 3, issues, {'has_data': has_data, 'has_traces': has_traces, 
                                 'has_layout': has_layout, 'has_graph': has_graph,
                                 'has_error': has_error}

def test_tab(tab, label):
    print(f'\n═══ Testing {label} tab ═══')
    
    # Call with default filters
    result = call_dash(tab)
    if result is None:
        print(f'  ❌ Callback failed (no response)')
        return False
    
    response_data, html_str = result
    ok, issues, details = check_chart_content(response_data)
    
    graph_count = html_str.count('"type":"Graph"')
    print(f'  Graph components: {graph_count}')
    print(f'  Has figure data: {details["has_data"]}')
    print(f'  Has traces: {details["has_traces"]}')
    print(f'  Has layout: {details["has_layout"]}')
    print(f'  Error messages: {details["has_error"]}')
    
    # Check for specific trace types in the response
    for ttype in ['scatter', 'bar', 'histogram', 'box', 'heatmap', 'pie']:
        count = html_str.lower().count(f'"type":"{ttype}"')
        if count > 0:
            print(f'  {ttype.title()} traces: {count}')
    
    if issues:
        print(f'  ⚠️  Issues: {", ".join(issues)}')
    
    if ok:
        print(f'  ✅ PASSED')
    else:
        print(f'  ❌ FAILED')
    
    return ok

def run_full_test():
    print('[START] Starting comprehensive dashboard test...')
    
    # Wait for server
    for i in range(10):
        try:
            r = requests.get(BASE, timeout=2)
            if r.status_code == 200:
                print(f'✅ Server is up at {BASE}')
                break
        except:
            pass
        time.sleep(1)
    else:
        print('❌ Server did not start')
        return
    
    results = {}
    for tab, label in [('overview', 'Overview'), ('performance', 'Movie Performance'),
                        ('genres', 'Genre Analytics'), ('advanced', 'Advanced')]:
        results[tab] = test_tab(tab, label)
    
    print('\n' + '═' * 50)
    print('📊 RESULTS SUMMARY')
    print('═' * 50)
    all_pass = True
    for tab, label in [('overview', 'Overview'), ('performance', 'Movie Performance'),
                        ('genres', 'Genre Analytics'), ('advanced', 'Advanced')]:
        status = '✅' if results.get(tab) else '❌'
        all_pass = all_pass and results.get(tab, False)
        print(f'{status} {label}')
    
    if all_pass:
        print('\n🎉 ALL TESTS PASSED')
    else:
        print('\n⚠️  SOME TESTS FAILED')
    
    return all_pass

if __name__ == '__main__':
    run_full_test()
