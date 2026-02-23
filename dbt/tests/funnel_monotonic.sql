-- funnel steps should be monotonic: signup >= eligible >= enroll >= first_payout at aggregate level
with agg as (
  select
    sum(did_signup) as signup,
    sum(did_eligible) as eligible,
    sum(did_enroll) as enroll,
    sum(did_first_payout) as first_payout
  from {{ ref('fct_creator_funnel') }}
)
select *
from agg
where not (signup >= eligible and eligible >= enroll and enroll >= first_payout)
