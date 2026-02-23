with stages as (
  select
    creator_id,
    max(case when event_name='signup' then 1 else 0 end) as did_signup,
    max(case when event_name='eligible' then 1 else 0 end) as did_eligible,
    max(case when event_name='enroll' then 1 else 0 end) as did_enroll,
    max(case when event_name='first_payout' then 1 else 0 end) as did_first_payout
  from {{ ref('stg_creator_events') }}
  group by 1
)
select
  s.creator_id,
  c.tier,
  c.country,
  c.experiment_group,
  did_signup,
  did_eligible,
  did_enroll,
  did_first_payout
from stages s
join {{ ref('dim_creator') }} c using(creator_id)
