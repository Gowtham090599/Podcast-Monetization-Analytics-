select
  creator_id,
  created_at,
  tier,
  country,
  experiment_group,
  eligible,
  enrolled,
  first_payout
from {{ ref('stg_creators') }}
