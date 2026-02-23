with listens as (
  select
    event_date as ds,
    creator_id,
    sum(listens) as listens
  from {{ ref('stg_listening_events') }}
  group by 1,2
),
revenue as (
  select
    event_date as ds,
    creator_id,
    sum(revenue_usd) as revenue_usd
  from {{ ref('stg_revenue_events') }}
  group by 1,2
),
episodes as (
  select
    published_date as ds,
    creator_id,
    count(*) as episodes_published
  from {{ ref('stg_episodes') }}
  group by 1,2
)
select
  coalesce(l.ds, r.ds, e.ds) as ds,
  coalesce(l.creator_id, r.creator_id, e.creator_id) as creator_id,
  coalesce(episodes_published, 0) as episodes_published,
  coalesce(listens, 0) as listens,
  coalesce(revenue_usd, 0.0) as revenue_usd
from listens l
full join revenue r
  on l.ds=r.ds and l.creator_id=r.creator_id
full join episodes e
  on coalesce(l.ds,r.ds)=e.ds and coalesce(l.creator_id,r.creator_id)=e.creator_id
