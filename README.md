# Podcast Monetization Analytics & Creator Growth Optimization (Production Portfolio)

A Spotify-aligned **Data Scientist / Analytics Engineer** portfolio project focused on **creator monetization**:
- creator lifecycle + monetization funnel analysis
- KPI dashboards + monitoring tables
- A/B experiment design + analysis
- predictive modeling (monetization propensity / churn risk)
- analytics engineering workflow using **dbt** (star schema marts, tests, docs)

> **Local-first**: Runs end-to-end with **DuckDB + dbt-duckdb** (no cloud account needed).  
> **Cloud-ready**: dbt models are written in portable SQL so you can switch to **BigQuery** by changing the adapter/profile.

---

## Project Goals

1. Understand where creators drop off in the monetization funnel
2. Define + monitor metrics (activation, retention, revenue per creator, publish frequency)
3. Quantify feature impact using experiments (A/B testing)
4. Build a model to predict monetization activation and churn risk
5. Produce actionable product recommendations

---

## Tech Stack

- **Python**: data generation, analysis, modeling
- **SQL**: transformations + marts
- **dbt**: analytics engineering, tests, docs
- **DuckDB**: local warehouse (swap to BigQuery/Snowflake later)
- **Tableau (spec)**: leadership dashboard design (fields + charts)

---

## Repository Structure

```
podcast-monetization-analytics/
├─ README.md
├─ Makefile
├─ requirements.txt
├─ .gitignore
├─ data/                  # generated locally (gitignored)
├─ outputs/               # metrics exports (gitignored)
├─ src/
│  ├─ generate_data.py
│  ├─ load_duckdb.py
│  ├─ run_analyses.py
│  ├─ analyses/
│  │  ├─ funnel.py
│  │  ├─ ab_test.py
│  │  └─ monitoring.py
│  ├─ modeling/
│  │  ├─ train_propensity.py
│  │  └─ train_churn.py
│  └─ utils/
│     ├─ db.py
│     └─ stats.py
├─ dbt/
│  ├─ dbt_project.yml
│  ├─ profiles.yml.example
│  ├─ models/
│  │  ├─ staging/
│  │  ├─ marts/
│  │  └─ metrics/
│  └─ tests/
├─ docs/
│  ├─ metric_definitions.md
│  ├─ experiment_design.md
│  └─ insights_recommendations.md
└─ dashboards/
   └─ tableau_dashboard_spec.md
```

---

## Quickstart (Local)

### 1) Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Generate data + load warehouse
```bash
make data
```

### 3) Build dbt models (staging → marts → metrics)
```bash
make dbt-build
```

### 4) Run analyses + export outputs
```bash
make analyze
```

Outputs land in `outputs/` as CSVs you can feed into Tableau/Looker.

---

 in dbt commands

Models already use portable SQL patterns.

---

## License
MIT (for portfolio use)
