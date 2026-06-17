# IMDb Movies Analytics Dashboard

**A production-grade Business Intelligence dashboard** that transforms 120+ years of movie data into actionable insights. Built with Python, Plotly Dash, and scikit-learn — featuring interactive visualizations, K-Means clustering, PCA dimensionality reduction, and a dark/light mode UI.

![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white) ![Dash](https://img.shields.io/badge/Dash-4.2.0-008DE4?logo=plotly&logoColor=white) ![Plotly](https://img.shields.io/badge/Plotly-6.8.0-3F4F75?logo=plotly&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-3.0.3-150458?logo=pandas&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-1.17.1-F7931E?logo=scikit-learn&logoColor=white) ![NumPy](https://img.shields.io/badge/NumPy-2.4.6-013243?logo=numpy&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-green)

---

## Project Overview

### The Problem

The film industry invests billions annually in content production with no centralized, data-driven framework to evaluate what drives success. Critical questions — which genres yield the best returns, whether budget correlates with quality, and how market trends evolve — are too often answered by intuition rather than evidence.

### The Solution

This project builds a **complete analytics pipeline** from raw IMDb data to an interactive BI dashboard, answering:

- Which genres deliver the highest critical and commercial returns?
- Does spending more on a movie actually improve its quality?
- What distinguishes a blockbuster from a commercial failure?
- How has the industry evolved across 120+ years of filmmaking?
- Can movies be segmented into meaningful business categories using machine learning?

### The Result

A **4-tab interactive dashboard** with global cross-filtering (year, genre, rating), 8 real-time KPI cards, 7+ interactive Plotly charts, K-Means clustering, PCA projections, and executive insight panels — all wrapped in a production-grade dark/light theme.

---

## Dataset Overview

| Metric | Value |
|--------|-------|
| **Total Movies** | 9,660 |
| **Year Range** | 1903 – 2023 (121 years) |
| **Genres** | 20 |
| **Countries** | 59 |
| **Languages** | 54 |
| **Features (Cleaned)** | 12 |
| **Features (Engineered)** | 20 |
| **Average IMDb Score** | 64.9 / 100 |
| **Median IMDb Score** | 66.0 / 100 |
| **Score Range** | 10 – 100 |
| **Average Budget** | $65.7M |
| **Median Budget** | $51.4M |
| **Average Revenue** | $257.7M |
| **Median Revenue** | $162.8M |
| **Total Revenue** | $2.48 Trillion |
| **Highly Rated (Score ≥ 70)** | 3,146 movies |
| **Hidden Gems (Score ≥ 70, Budget < Median)** | 1,675 movies |
| **Production Peak** | 2022 — 941 movies |
| **Budget-Revenue Correlation** | r ≈ 0.67 |
| **Budget-Score Correlation** | r ≈ 0.06 (negligible) |

---

## Business Questions Answered

### Which genres perform best?

| Genre | Movies | Avg Score | Verdict |
|-------|--------|-----------|---------|
| Music | 292 | 70.1 | Highest rated |
| History | 284 | 70.0 | Consistently strong |
| War | 186 | 69.9 | Niche but high quality |
| Animation | 265 | 69.5 | Broad appeal, high scores |
| Documentary | 581 | 69.4 | Critical darling |
| Drama | 3,609 | 67.1 | Volume leader |
| Horror | 1,320 | 60.2 | Lowest performer (excluding Unknown) |

**Insight:** Genre is a statistically significant predictor of ratings (ANOVA, p < 0.001). The highest-volume genres (Drama, Comedy, Action) do not produce the highest-quality films. Prestige lies in niche categories.

### Does budget buy quality?

**No.** The Pearson correlation between budget and IMDb score is **r ≈ 0.06** — effectively zero. A high budget is not a path to critical acclaim. In fact, many of the most expensive productions in history failed to recoup their budgets.

### What drives commercial success?

Budget-revenue correlation (r ≈ 0.67) shows that spending increases revenue potential, but with enormous variance. The **Pareto principle** holds: the top 20% of movies generate over 50% of all revenue.

### How has the industry changed?

Movie production has grown **92×** from the 1950s (61 movies) to the 2020s (5,768+ through 2023). Yet average ratings have remained **remarkably stable** — hovering between 64–66 across every decade since the 1970s. The industry scaled without sacrificing quality.

### Can movies be segmented?

**Yes.** K-Means clustering (K=4, silhouette = 0.32) identifies four natural segments: **Blockbusters** (high budget, high revenue), **Critically Acclaimed** (high score, moderate budget), **Hidden Gems** (high score, low budget), and **Standard Films**. PCA confirms that 3 principal components capture ~90% of the variance.

---

## Analytical Workflow

```
┌─────────────────┐
│   Raw Dataset   │  10,178 rows × 12 columns
│   imdb_movies   │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Data Cleaning  │  Removed 518 duplicates, handled 0.12% missing values
│                 │  Standardized column names, parsed dates, validated ranges
└────────┬────────┘
         ▼
┌─────────────────┐
│        EDA      │  Univariate, bivariate & multivariate analysis
│                 │  Correlation matrices, distribution plots, temporal trends
└────────┬────────┘
         ▼
┌─────────────────┐
│     Feature     │  Log transforms (budget, revenue), decade bins,
│   Engineering   │  primary genre extraction, ROI calculation, age features
└────────┬────────┘
         ▼
┌─────────────────┐
│   Statistical   │  T-Test (high vs low budget, p<0.001)
│    Analysis     │  ANOVA (genre effect, p<0.001)
│                 │  Pearson/Spearman correlation matrices
└────────┬────────┘
         ▼
┌─────────────────┐
│    Machine      │  K-Means Clustering (K=4, silhouette=0.32)
│    Learning     │  PCA (3 components, ~90% variance)
│                 │  4-way business segmentation
└────────┬────────┘
         ▼
┌─────────────────┐
│   Interactive   │  4 tabs, 7+ charts, 8 KPIs, global filters
│   Dashboard     │  Dark/light theme, responsive layout, insight panels
└────────┬────────┘
         ▼
┌─────────────────┐
│     Business    │  Portfolio recommendations, greenlight criteria,
│    Insights     │  genre strategy, risk assessment framework
└─────────────────┘
```

---

## Key Findings

### Finding 1: The Industry Scaled Without Sacrificing Quality

Despite a **92× increase** in annual production volume (from 61 movies in the 1950s to 941 in 2022), average IMDb scores have remained **stable at ~65/100** across every decade since the 1970s. This disproves the "quality dilution" hypothesis.

> **Business Implication:** The market can absorb increased production without degrading average quality. Growth strategies should focus on pipeline efficiency and portfolio diversification rather than quality gate tightening.

### Finding 2: Budget Does Not Buy Critical Acclaim

The correlation between budget and IMDb score is **r ≈ 0.06** — statistically negligible. Some of the highest-scoring films in the dataset were made on modest budgets. Conversely, **10 of the 20 most expensive productions** failed to generate an ROI above 1×.

> **Business Implication:** Budget allocation should be decoupled from quality expectations. Stage-gate funding models with creative benchmarks reduce risk on large productions.

### Finding 3: Genre Is the Strongest Predictor of Ratings

ANOVA confirms genre has a **significant effect on ratings** (p < 0.001). Music (70.1), History (70.0), and War (69.9) consistently outperform Horror (60.2) and Sci-Fi (64.0) — regardless of budget.

> **Business Implication:** Genre selection is a strategic portfolio decision. A balanced mix of prestige genres (Documentary, History) and commercial genres (Action, Animation) optimizes both quality and revenue.

### Finding 4: The Pareto Principle Governs Revenue

The top 20% of movies by revenue generate **more than 50% of total industry revenue**. The revenue distribution is heavily right-skewed with a log-normal pattern. Median revenue ($162.8M) is well below the mean ($257.7M), confirming that a small number of blockbusters dominate.

> **Business Implication:** A portfolio approach is essential — 20% of productions should target blockbuster outcomes while 80% should be optimized for risk-adjusted returns.

### Finding 5: K-Means Reveals Four Natural Movie Segments

| Segment | Profile | Strategy |
|---------|---------|----------|
| **Blockbusters** | High budget, high revenue, moderate scores | Franchise/IP-driven; high risk, high reward |
| **Critically Acclaimed** | High scores, moderate budget, moderate revenue | Prestige productions; awards-focused |
| **Hidden Gems** | High scores, low budget, variable revenue | Best risk-adjusted returns; under-marketed |
| **Standard Films** | Average across all dimensions | Volume filler; requires differentiation |

> **Business Implication:** Hidden Gems offer the best risk-adjusted investment profile. Funding models should specifically incentivize this segment.

---

## Dashboard Features

### Executive Overview

The first tab presents a **prime-time dashboard** designed for executive decision-makers:

- **8 KPI cards** with semantic color coding (ratings = blue, revenue = green, volume = purple, warning = amber)
- **Rating Distribution** histogram with mean/median markers
- **Year Trends** bar + line chart (production volume vs. average rating, 1950+)
- **Revenue Analysis** dual-panel: revenue distribution + budget vs. revenue scatter
- **Genre Distribution** horizontal bar with rating overlay
- **Executive Summary** with four insight quadrants (Key Findings, Opportunities, Risks, Recommendations)
- **Dynamic insight cards** that respond to filter changes

### Movie Performance

A drill-down view of individual movie performance:

- **Top 10 by Score** — interactive DataTable with search, sort, and pagination
- **Top 10 by Revenue** — formatted currency columns with sortable headers
- **Top 10 by ROI** — calculated return multiples with budget context
- **Top 20 Highest Rated** — horizontal bar chart color-mapped by score
- **Budget vs. Rating Bubble Chart** — size = revenue, color = genre, log scale

### Genre Analytics

Strategic view of genre-level performance:

- **Genre Volume vs. Rating** — dual-axis chart (bar + scatter)
- **Revenue by Genre** — log-scale box plots showing distribution, median, and outliers (top 12 genres by median revenue)
- **Rating Distribution** — histogram for filtered genre set
- **Genre Insights** — automated best/worst genre identification with recommendations

### Advanced Analytics

Machine learning and statistical analysis for data scientists:

- **Correlation Heatmap** — interactive Pearson correlation matrix (score, budget, revenue, year)
- **K-Means Clustering** — 4-segment scatter plot (budget vs. score, colored by segment, sized by revenue)
- **PCA Visualization** — 3-component projection (colored by budget tier, sized by revenue, with explained variance annotations)
- **Movie Segmentation Pie Chart** — rule-based 4-way breakdown: Blockbusters, Hidden Gems, Critically Acclaimed, Standard Films
- **Data Storytelling Narrative** — 4-chapter guided analysis with business recommendations

### Theme & Interaction

- **Dark/Light Mode Toggle** — one-click theme switch, persisted across tabs
- **Global Filter Panel** — year range slider, genre dropdown, rating range slider
- **Cross-tab Filtering** — all filters apply across all four tabs
- **Reset Filters** — one-click restoration of default state
- **Responsive Layout** — adapts to desktop, tablet, and mobile viewports
- **Sticky Header** — navigation always accessible during scrolling
- **Interactive Charts** — zoom, pan, hover tooltips, PNG export via Plotly modebar

---

## Dashboard Preview

### Executive Overview
![Executive Overview](reports/screenshots/1.png)
*8 KPI cards, executive summary, rating distribution, year trends, genre volume vs. rating*

### Movie Performance
![Movie Performance](reports/screenshots/2.png)
*Top 10 tables (score/revenue/ROI), top 20 horizontal bar chart, budget vs. rating bubble chart*

### Genre Analytics
![Genre Analytics](reports/screenshots/3.png)
*Genre distribution dual-axis chart, revenue by genre box plots, rating histogram, insight cards*

### Advanced Analytics
![Advanced Analytics](reports/screenshots/4.png)
*Correlation heatmap, K-Means clustering, PCA projection, segmentation pie chart, data storytelling*

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Data Processing** | Pandas 3.0.3, NumPy 2.4.6 | Data manipulation, cleaning, feature engineering |
| **Statistical Analysis** | SciPy 1.11 | T-Test, ANOVA, correlation matrices |
| **Machine Learning** | scikit-learn 1.17.1 | K-Means (K=4, silhouette=0.32), PCA (3 components, ~90% variance), StandardScaler |
| **Interactive Visualization** | Plotly 6.8.0 | All dashboard charts: scatter, bar, histogram, box, heatmap, pie, bubble |
| **Dashboard Framework** | Dash 4.2.0 | Web application, callbacks, component layout, DataTables |
| **Styling** | Dash Bootstrap Components 2.0.4, CSS Custom Properties | Dark/light theme, responsive grid, semantic colors |
| **Static Charts (Notebook)** | Matplotlib 3.7, Seaborn 0.13 | EDA visualizations, correlation heatmaps, distribution plots |

---

## Project Structure

```
imdb-movies-dashboard/
│
├── dashboard/                        # Interactive dashboard application
│   ├── app.py                        # Dash application — run with `python dashboard/app.py`
│   ├── imdb_dashboard.html           # Standalone HTML dashboard (1.0 MB)
│   └── assets/
│       └── style.css                 # Design tokens, dark/light theme, responsive layout
│
├── data/
│   ├── raw/
│   │   └── imdb_movies.csv           # Original dataset (10,178 rows × 12 columns)
│   └── processed/
│       ├── cleaned_imdb_movies.csv   # After cleaning & deduplication (9,660 rows)
│       └── feature_engineered_imdb_movies.csv  # With engineered features (20 columns)
│
├── notebooks/
│   └── 01_data_cleaning.ipynb        # Complete analysis pipeline (236 cells, 140 code, 0 errors)
│
├── scripts/
│   ├── build/                        # Dashboard build scripts
│   │   ├── build_dashboard.py        # Dash app builder
│   │   ├── build_dashboard_html.py   # Standalone HTML builder
│   │   └── executor.py               # Build pipeline executor
│   ├── debug/                        # Debugging and diagnostic scripts
│   ├── utilities/                     # Refactoring and report generation
│   └── verification/                  # End-to-end verification and testing
│
├── reports/
│   ├── analysis_summary/             # Analysis summaries
│   ├── exports/                      # Exported reports and data
│   └── screenshots/                  # Dashboard preview images
│
├── docs/                             # Additional documentation
├── logs/                             # Application logs
├── requirements.txt                  # Python dependencies
├── LICENSE                           # MIT License
└── README.md                         # This file
```

---

## How to Run

### Prerequisites

- **Python 3.10+** (developed on 3.14)
- **pip** package manager

### 1. Clone the Repository

```bash
git clone https://github.com/firoz671/imdb-movies-dashboard.git
cd imdb-movies-dashboard
```

### 2. Create a Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Dashboard

```bash
python dashboard/app.py
```

### 5. Access the Dashboard

Open your browser and navigate to:

```
http://127.0.0.1:8050/
```

The dashboard will display the **Executive Overview** tab with all 8 KPI cards loaded. Use the filter panel to explore data by year range, genre, and rating threshold. Navigate tabs to explore specific analytical dimensions.

### Running the Analysis Notebook

To explore the full analysis pipeline:

```bash
pip install jupyter
jupyter notebook notebooks/01_data_cleaning.ipynb
```

The notebook contains 236 cells (140 code, 96 markdown) covering data loading, quality assessment, cleaning, EDA, feature engineering, statistical testing, and machine learning.

---

## Future Improvements

- **Real-time Data Pipeline**: Integrate with TMDB or OMDb APIs to fetch live data on new releases
- **Revenue Prediction Model**: Train a regression model (XGBoost, Random Forest) to predict box office revenue from pre-release features
- **Recommendation Engine**: Build a content-based or collaborative filtering system using genre, crew, and overview text
- **Cloud Deployment**: Deploy to AWS Elastic Beanstalk, Heroku, or Render for public access
- **User Authentication**: Add login system for personalized portfolio tracking
- **Export Engine**: PDF report generation with executive summaries, charts, and raw data tables
- **A/B Testing Module**: Compare performance across custom movie portfolios
- **NLP Analysis**: Topic modeling and sentiment analysis on plot overviews

---

## Author

<div style="display: flex; align-items: center; gap: 16px;">
  <div>
    <strong>Firoz Al Mahmud</strong><br>
    Data Analyst · BI Developer · Python Engineer
  </div>
</div>

- **LinkedIn**: [firoz-al-mahmud-264982243](https://www.linkedin.com/in/firoz-al-mahmud-264982243/)
- **GitHub**: [firoz671](https://github.com/firoz671)

This project was built as part of a portfolio demonstrating end-to-end data analytics capabilities — from raw data ingestion to production-grade dashboard deployment. For questions, collaboration opportunities, or hiring inquiries, please connect via LinkedIn.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

*Built with Python, Plotly Dash, and scikit-learn — powered by 121 years of movie history.*
