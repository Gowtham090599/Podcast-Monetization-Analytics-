# Tableau Dashboard Spec (Leadership-ready)

## Data Sources
- `outputs/daily_monitoring.csv`
- `outputs/funnel_by_tier_experiment.csv`
- `outputs/ab_effect_estimate.csv`
- `outputs/top_target_creators_propensity.csv`

## Tabs
### 1) Executive Overview
- KPIs: active_creators, revenue_usd, RPAC, listens, episodes_published
- WoW deltas and trend lines
- Callout: enroll_rate_given_eligible (funnel snapshot)

### 2) Monetization Funnel
- Funnel by tier and experiment group
- Drop-off bars: eligible → enroll → first_payout
- Filters: tier, experiment_group, country

### 3) Experiment Results
- KPI card: treatment lift + CI (from ab_effect_estimate.csv)
- Segment view: by tier
- Guardrails: episodes_published trend

### 4) Targeting & Retention
- Top creators by propensity
- At-risk creators by churn probability
- Suggested actions by segment
