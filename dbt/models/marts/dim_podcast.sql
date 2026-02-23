select
  p.podcast_id,
  p.creator_id,
  p.category,
  p.created_at
from {{ ref('stg_podcasts') }} p
