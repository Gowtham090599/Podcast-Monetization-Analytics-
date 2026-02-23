from __future__ import annotations
from pathlib import Path
import pandas as pd
from src.utils.db import connect, read_df

FUNNEL_SQL = r"""
WITH stages AS (
  SELECT
    creator_id,
    max(CASE WHEN event_name='signup' THEN 1 ELSE 0 END) AS did_signup,
    max(CASE WHEN event_name='eligible' THEN 1 ELSE 0 END) AS did_eligible,
    max(CASE WHEN event_name='enroll' THEN 1 ELSE 0 END) AS did_enroll,
    max(CASE WHEN event_name='first_payout' THEN 1 ELSE 0 END) AS did_first_payout
  FROM raw_creator_events
  GROUP BY 1
)
SELECT
  sum(did_signup) AS signup,
  sum(did_eligible) AS eligible,
  sum(did_enroll) AS enroll,
  sum(did_first_payout) AS first_payout
FROM stages;
"""

def run(db_path: str, out_dir: Path):
    con = connect(db_path)
    df = read_df(con, FUNNEL_SQL)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "funnel_summary.csv", index=False)

    # segment funnel by tier and experiment group (more interview-relevant)
    seg_sql = r"""
    WITH stages AS (
      SELECT
        e.creator_id,
        max(CASE WHEN e.event_name='signup' THEN 1 ELSE 0 END) AS did_signup,
        max(CASE WHEN e.event_name='eligible' THEN 1 ELSE 0 END) AS did_eligible,
        max(CASE WHEN e.event_name='enroll' THEN 1 ELSE 0 END) AS did_enroll,
        max(CASE WHEN e.event_name='first_payout' THEN 1 ELSE 0 END) AS did_first_payout
      FROM raw_creator_events e
      GROUP BY 1
    )
    SELECT
      c.tier,
      c.experiment_group,
      count(*) AS creators,
      sum(did_eligible) AS eligible,
      sum(did_enroll) AS enroll,
      sum(did_first_payout) AS first_payout,
      round(sum(did_enroll)*1.0/nullif(sum(did_eligible),0), 4) AS enroll_rate_given_eligible,
      round(sum(did_first_payout)*1.0/nullif(sum(did_enroll),0), 4) AS payout_rate_given_enroll
    FROM stages s
    JOIN raw_creators c USING(creator_id)
    GROUP BY 1,2
    ORDER BY 1,2;
    """
    seg = read_df(con, seg_sql)
    seg.to_csv(out_dir / "funnel_by_tier_experiment.csv", index=False)
    con.close()
