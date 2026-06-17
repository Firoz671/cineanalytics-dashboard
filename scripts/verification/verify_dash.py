import json
with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
code_cells = [(i, c) for i, c in enumerate(cells) if c['cell_type'] == 'code']

# Check specific dashboard cells
for ci in [130, 131, 132, 133, 134, 135, 136, 137, 138, 139]:
    if ci < len(code_cells):
        cell_idx, cell = code_cells[ci]
        outputs = cell.get('outputs', [])
        print(f'=== Code cell {ci} (cell_idx={cell_idx}) ===')
        src = ''.join(cell['source'])[:80]
        print(f'Source: {src}...')
        print(f'Outputs: {len(outputs)}')
        for oi, o in enumerate(outputs):
            otype = o['output_type']
            if otype == 'stream':
                text = ''.join(o.get('text', ['']))[:100]
                print(f'  Output {oi}: stream -> {text}')
            elif otype == 'display_data':
                data = o.get('data', {})
                has_png = 'image/png' in data
                has_html = 'text/html' in data
                has_text = 'text/plain' in data
                print(f'  Output {oi}: display_data -> png={has_png} html={has_html} text={has_text}')
            elif otype == 'error':
                print(f'  Output {oi}: ERROR -> {o.get("evalue", "")[:100]}')
            else:
                print(f'  Output {oi}: {otype}')
        print()
