select
  cast(episode_id as bigint) as episode_id,
  cast(podcast_id as bigint) as podcast_id,
  cast(creator_id as bigint) as creator_id,
  cast(published_at as date) as published_date,
  cast(duration_min as int) as duration_min
from raw_episodes
