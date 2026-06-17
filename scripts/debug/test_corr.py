"""Test if np.corrcoef crashes with different-length dropna arrays"""
import pandas as pd, numpy as np, sys
sys.stdout.reconfigure(encoding='utf-8')
print(f'numpy: {np.__version__}')
print(f'pandas: {pd.__version__}')

df = pd.read_csv('D:/MOVIES DATA/data/processed/cleaned_imdb_movies.csv', encoding='utf-8-sig',
                  parse_dates=['release_date'], low_memory=False)
df['year'] = df['release_date'].dt.year
df['primary_genre'] = df['genre'].str.split(',').str[0].str.strip()

b = df['budget'].dropna()
r = df['revenue'].dropna()
print(f'budget len: {len(b)}, revenue len: {len(r)}')
print(f'budget NaN in df: {df["budget"].isna().sum()}')
print(f'revenue NaN in df: {df["revenue"].isna().sum()}')

try:
    corr = np.corrcoef(b, r)
    print(f'corrcoef result: {corr}')
except Exception as e:
    print(f'corrcoef ERROR: {type(e).__name__}: {e}')

# Try the corrcoef with the full exec_section string interpolation
try:
    result = f'Budget-revenue correlation: r≈{np.corrcoef(df["budget"].dropna(), df["revenue"].dropna())[0,1]:.2f}.'
    print(f'f-string result: {result}')
except Exception as e:
    print(f'f-string ERROR: {type(e).__name__}: {e}')
