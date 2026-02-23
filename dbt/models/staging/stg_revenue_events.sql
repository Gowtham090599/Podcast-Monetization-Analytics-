select
  cast(event_date as date) as event_date,
  cast(creator_id as bigint) as creator_id,
  cast(podcast_id as bigint) as podcast_id,
  cast(episode_id as bigint) as episode_id,
  cast(revenue_usd as double) as revenue_usd
from raw_revenue_events
