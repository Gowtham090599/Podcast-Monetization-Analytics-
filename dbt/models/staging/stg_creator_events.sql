select
  cast(event_ts as timestamp) as event_ts,
  cast(creator_id as bigint) as creator_id,
  event_name
from raw_creator_events
