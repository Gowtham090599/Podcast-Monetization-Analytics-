from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from src.utils.db import connect, read_df
from src.utils.stats import diff_in_proportions

AB_SQL = r"""
WITH eligible AS (
  SELECT
    c.creator_id,
    c.experiment_group,
    c.eligible,
    c.enrolled
  FROM raw_creators c
)
SELECT
  experiment_group,
  count(*) AS n_creators,
  sum(eligible) AS n_eligible,
  sum(CASE WHEN eligible=1 AND enrolled=1 THEN 1 ELSE 0 END) AS n_enrolled_given_eligible
FROM eligible
GROUP BY 1;
"""

def run(db_path: str, out_dir: Path):
    con = connect(db_path)
    df = read_df(con, AB_SQL)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "ab_summary_counts.csv", index=False)

    # Compute enrollment rate among eligible (primary metric)
    ctrl = df[df["experiment_group"]=="control"].iloc[0]
    trt = df[df["experiment_group"]=="treatment"].iloc[0]

    p1 = ctrl["n_enrolled_given_eligible"] / max(ctrl["n_eligible"], 1)
    p2 = trt["n_enrolled_given_eligible"] / max(trt["n_eligible"], 1)

    diff, (lo, hi) = diff_in_proportions(p1, int(ctrl["n_eligible"]), p2, int(trt["n_eligible"]))
    out = pd.DataFrame([{
        "metric": "enroll_rate_given_eligible",
        "control_rate": round(float(p1), 6),
        "treatment_rate": round(float(p2), 6),
        "diff_treat_minus_control": round(float(diff), 6),
        "ci95_low": round(float(lo), 6),
        "ci95_high": round(float(hi), 6),
    }])
    out.to_csv(out_dir / "ab_effect_estimate.csv", index=False)
    con.close()
