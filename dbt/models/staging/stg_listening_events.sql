select
  cast(event_date as date) as event_date,
  cast(episode_id as bigint) as episode_id,
  cast(podcast_id as bigint) as podcast_id,
  cast(creator_id as bigint) as creator_id,
  cast(listens as bigint) as listens
from raw_listening_events
