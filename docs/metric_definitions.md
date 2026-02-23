# Metric Definitions (Spotify-style)

## Primary Metrics
- **Monetization Activation Rate (Enroll Rate Given Eligible)**  
  `enrolled_creators / eligible_creators`

- **Revenue per Active Creator (RPAC)**  
  `revenue_usd / active_creators`

- **Creator Retention (Proxy)**  
  *Portfolio proxy:* churn model label = no episodes in last 30 days.

## Secondary Metrics
- Episodes published per day
- Total listens per day
- First payout creators (proxy for monetization success)

## Guardrails
- Data quality: missing keys, invalid categories, relationships tests
- Anomaly monitoring: daily KPIs exported to `outputs/daily_monitoring.csv`
