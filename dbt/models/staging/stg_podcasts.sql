select
  cast(podcast_id as bigint) as podcast_id,
  cast(creator_id as bigint) as creator_id,
  category,
  cast(created_at as timestamp) as created_at
from raw_podcasts
