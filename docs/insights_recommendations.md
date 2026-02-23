# Insights & Recommendations (Template)

Use this file after running `make analyze` and reviewing outputs.

## Funnel findings
- Where are the largest drop-offs?
- Which segments (tier/category/country) show different patterns?

## Experiment findings
- Did treatment increase enrollment among eligible creators?
- Are guardrails stable?

## Recommendations (example format)
1) **Improve eligibility-to-enroll conversion** for Small creators by simplifying enrollment steps.
   - Expected impact: +X% enroll rate among eligible
   - Evidence: funnel segment table + experiment lift

2) **Target high-intent creators** using propensity scores (top decile).
   - Expected impact: improve activation efficiency, reduce CAC
   - Evidence: `top_target_creators_propensity.csv`

3) **Retention interventions** for churn-risk creators
   - Expected impact: reduce churn by Y%
   - Evidence: `top_at_risk_creators_churn.csv`
