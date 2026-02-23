from __future__ import annotations
from pathlib import Path
import pandas as pd
from src.utils.db import connect, read_df

MONITOR_SQL = r"""
WITH daily AS (
  SELECT
    event_date::DATE AS ds,
    count(DISTINCT creator_id) AS active_creators,
    sum(listens) AS listens,
    sum(r.revenue_usd) AS revenue_usd
  FROM raw_listening_events l
  LEFT JOIN raw_revenue_events r
    ON r.episode_id = l.episode_id
  GROUP BY 1
)
SELECT
  ds,
  active_creators,
  listens,
  revenue_usd,
  round(revenue_usd/nullif(active_creators,0), 2) AS rev_per_active_creator
FROM daily
ORDER BY ds;
"""

def run(db_path: str, out_dir: Path):
    con = connect(db_path)
    df = read_df(con, MONITOR_SQL)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "daily_monitoring.csv", index=False)
    con.close()
