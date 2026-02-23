with daily as (
  select
    ds,
    count(distinct creator_id) as active_creators,
    sum(listens) as listens,
    sum(revenue_usd) as revenue_usd,
    sum(episodes_published) as episodes_published
  from {{ ref('fct_creator_daily') }}
  group by 1
),
funnel as (
  select
    sum(did_eligible) as eligible_creators,
    sum(did_enroll) as enrolled_creators,
    sum(did_first_payout) as first_payout_creators
  from {{ ref('fct_creator_funnel') }}
)
select
  d.ds,
  d.active_creators,
  d.listens,
  d.revenue_usd,
  round(d.revenue_usd/nullif(d.active_creators,0), 4) as revenue_per_active_creator,
  d.episodes_published,
  -- funnel snapshot fields repeated daily for simple dashboard joins (ok for portfolio)
  f.eligible_creators,
  f.enrolled_creators,
  round(f.enrolled_creators*1.0/nullif(f.eligible_creators,0), 4) as enroll_rate_given_eligible,
  f.first_payout_creators
from daily d
cross join funnel f
order by d.ds
