select
  cast(creator_id as bigint) as creator_id,
  cast(created_at as timestamp) as created_at,
  tier,
  country,
  experiment_group,
  cast(eligible as int) as eligible,
  cast(enrolled as int) as enrolled,
  cast(first_payout as int) as first_payout
from raw_creators
