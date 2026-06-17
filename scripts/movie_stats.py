import csv
import statistics
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")

CSV_PATH = r"D:\MOVIES DATA\data\processed\cleaned_imdb_movies.csv"

def load_data():
    rows = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def safe_float(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None

def main():
    rows = load_data()
    total = len(rows)

    years = []
    scores = []
    budgets = []
    revenues = []
    genres_all = []
    languages_all = []
    countries_all = []

    for r in rows:
        # year
        date = r.get("release_date", "")
        if date:
            try:
                y = int(date.split("-")[0])
                years.append(y)
            except:
                pass

        # score
        s = safe_float(r.get("imdb_score"))
        if s is not None:
            scores.append(s)

        # budget
        b = safe_float(r.get("budget"))
        if b is not None and b > 0:
            budgets.append(b)

        # revenue
        rev = safe_float(r.get("revenue"))
        if rev is not None and rev > 0:
            revenues.append(rev)

        # genres
        g = r.get("genre", "")
        if g:
            for genre in g.split(","):
                g_clean = genre.strip()
                if g_clean:
                    genres_all.append(g_clean)

        # language
        lang = r.get("language", "").strip()
        if lang:
            languages_all.append(lang)

        # country
        country = r.get("country", "").strip()
        if country:
            countries_all.append(country)

    # 1
    print(f"1. Total movies: {total}")

    # 2
    print(f"2. Year range: {min(years)} - {max(years)}")

    # 3
    unique_genres = set(genres_all)
    print(f"3. Unique genres: {len(unique_genres)}")

    # 4
    unique_countries = set(countries_all)
    print(f"4. Unique countries: {len(unique_countries)}")

    # 5
    unique_languages = set(languages_all)
    print(f"5. Unique languages: {len(unique_languages)}")

    # 6
    avg_score = statistics.mean(scores) if scores else 0
    print(f"6. Average IMDb score: {avg_score}")

    # 7
    med_score = statistics.median(scores) if scores else 0
    print(f"7. Median IMDb score: {med_score}")

    # 8
    print(f"8. Min IMDb score: {min(scores):.1f}, Max IMDb score: {max(scores):.1f}")

    # 9
    avg_budget = statistics.mean(budgets) if budgets else 0
    med_budget = statistics.median(budgets) if budgets else 0
    print(f"9. Average budget: {avg_budget:.2f}, Median budget: {med_budget:.2f}")

    # 10
    avg_revenue = statistics.mean(revenues) if revenues else 0
    med_revenue = statistics.median(revenues) if revenues else 0
    print(f"10. Average revenue: {avg_revenue:.2f}, Median revenue: {med_revenue:.2f}")

    # 11
    print(f"11. Total revenue: {sum(revenues):.2f}")

    # 12
    genre_count = Counter(genres_all)
    genre_score_sum = defaultdict(float)
    genre_score_cnt = defaultdict(int)
    for r in rows:
        g = r.get("genre", "")
        s = safe_float(r.get("imdb_score"))
        if g and s is not None:
            for genre in g.split(","):
                g_clean = genre.strip()
                if g_clean:
                    genre_score_sum[g_clean] += s
                    genre_score_cnt[g_clean] += 1
    genre_avg_scores = {g: genre_score_sum[g] / genre_score_cnt[g] for g in genre_score_cnt}
    top5_count = genre_count.most_common(5)
    print("12. Top 5 genres by count with avg scores:")
    for g, cnt in top5_count:
        print(f"    {g}: count={cnt}, avg_score={genre_avg_scores.get(g, 0):.4f}")

    # 13
    sorted_by_avg = sorted(genre_avg_scores.items(), key=lambda x: x[1], reverse=True)
    print("13. Top 5 genres by average score:")
    for g, sc in sorted_by_avg[:5]:
        print(f"    {g}: {sc:.4f}")

    # 14
    print("14. Bottom 5 genres by average score:")
    for g, sc in sorted_by_avg[-5:]:
        print(f"    {g}: {sc:.4f}")

    # 15
    high_rated = sum(1 for s in scores if s >= 70)
    print(f"15. Movies with score >= 70: {high_rated}")

    # 16
    # hidden gems: score >= 70 AND budget < median budget
    med_budget_val = statistics.median(budgets) if budgets else 0
    hidden_gems = 0
    for r in rows:
        s = safe_float(r.get("imdb_score"))
        b = safe_float(r.get("budget"))
        if s is not None and s >= 70 and b is not None and b > 0 and b < med_budget_val:
            hidden_gems += 1
    print(f"16. Hidden gems (score>=70, budget<median): {hidden_gems}")

    # 17 Pearson correlation budget-revenue
    pairs = []
    for r in rows:
        b = safe_float(r.get("budget"))
        rev = safe_float(r.get("revenue"))
        if b is not None and rev is not None and b > 0 and rev > 0:
            pairs.append((b, rev))
    n = len(pairs)
    if n > 1:
        sum_x = sum(p[0] for p in pairs)
        sum_y = sum(p[1] for p in pairs)
        sum_xy = sum(p[0] * p[1] for p in pairs)
        sum_x2 = sum(p[0] ** 2 for p in pairs)
        sum_y2 = sum(p[1] ** 2 for p in pairs)
        numer = n * sum_xy - sum_x * sum_y
        denom = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
        corr = numer / denom if denom != 0 else 0
    else:
        corr = 0
    print(f"17. Budget-Revenue Pearson correlation: {corr:.6f}")

    # 18 Top 5 highest-grossing
    rev_sorted = sorted([(r.get("movie_name", ""), safe_float(r.get("revenue")) or 0) for r in rows], key=lambda x: x[1], reverse=True)
    print("18. Top 5 highest-grossing movies:")
    for name, rev in rev_sorted[:5]:
        print(f"    {name}: {rev:.2f}")

    # 19 Top 5 highest-rated
    score_sorted = sorted([(r.get("movie_name", ""), safe_float(r.get("imdb_score")) or 0) for r in rows], key=lambda x: x[1], reverse=True)
    print("19. Top 5 highest-rated movies:")
    for name, sc in score_sorted[:5]:
        print(f"    {name}: {sc}")

    # 20 Year with most movies
    year_count = Counter(years)
    top_year, top_year_cnt = year_count.most_common(1)[0]
    print(f"20. Year with most movies: {top_year} ({top_year_cnt} movies)")

    # 21 Average rating per decade
    decade_scores = defaultdict(list)
    for r in rows:
        date = r.get("release_date", "")
        s = safe_float(r.get("imdb_score"))
        if date and s is not None:
            try:
                y = int(date.split("-")[0])
                decade = (y // 10) * 10
                decade_scores[decade].append(s)
            except:
                pass
    print("21. Average rating per decade:")
    for dec in sorted(decade_scores):
        avg = statistics.mean(decade_scores[dec])
        print(f"    {dec}s: {avg:.4f} (n={len(decade_scores[dec])})")

    # 22 Movies per decade
    decade_movies = defaultdict(int)
    for y in years:
        dec = (y // 10) * 10
        decade_movies[dec] += 1
    print("22. Number of movies per decade:")
    for dec in sorted(decade_movies):
        print(f"    {dec}s: {decade_movies[dec]}")

    # 23 Most common language
    lang_count = Counter(languages_all)
    top_lang, top_lang_cnt = lang_count.most_common(1)[0]
    print(f"23. Most common language: {top_lang} ({top_lang_cnt} movies)")

    # 24 Most common country
    country_count = Counter(countries_all)
    top_country, top_country_cnt = country_count.most_common(1)[0]
    print(f"24. Most common country: {top_country} ({top_country_cnt} movies)")

if __name__ == "__main__":
    main()
