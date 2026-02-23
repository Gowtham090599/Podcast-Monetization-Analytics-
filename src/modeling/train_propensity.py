from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from src.utils.db import connect, read_df

FEATURE_SQL = r"""
WITH listens AS (
  SELECT creator_id, sum(listens) AS listens_180d
  FROM raw_listening_events
  GROUP BY 1
),
episodes AS (
  SELECT creator_id, count(*) AS episodes_180d
  FROM raw_episodes
  GROUP BY 1
),
rev AS (
  SELECT creator_id, sum(revenue_usd) AS revenue_180d
  FROM raw_revenue_events
  GROUP BY 1
)
SELECT
  c.creator_id,
  c.tier,
  c.country,
  c.experiment_group,
  coalesce(e.episodes_180d,0) AS episodes_180d,
  coalesce(l.listens_180d,0) AS listens_180d,
  coalesce(r.revenue_180d,0) AS revenue_180d,
  c.eligible,
  c.enrolled AS label_enrolled
FROM raw_creators c
LEFT JOIN listens l USING(creator_id)
LEFT JOIN episodes e USING(creator_id)
LEFT JOIN rev r USING(creator_id);
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db_path", type=str, default="warehouse.duckdb")
    ap.add_argument("--out_dir", type=str, default="outputs")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    con = connect(args.db_path)
    df = read_df(con, FEATURE_SQL)
    con.close()

    # Only eligible creators for propensity-to-enroll modeling
    df = df[df["eligible"]==1].copy()
    y = df["label_enrolled"].astype(int)
    X = df.drop(columns=["label_enrolled"])

    cat_cols = ["tier", "country", "experiment_group"]
    num_cols = ["episodes_180d", "listens_180d", "revenue_180d"]

    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ("num", "passthrough", num_cols),
    ])

    clf = LogisticRegression(max_iter=200, n_jobs=None)
    pipe = Pipeline([("pre", pre), ("clf", clf)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=7, stratify=y)

    pipe.fit(X_train, y_train)
    proba = pipe.predict_proba(X_test)[:,1]
    auc = roc_auc_score(y_test, proba)

    preds = (proba >= 0.5).astype(int)

    report = classification_report(y_test, preds, output_dict=False)
    (out_dir / "propensity_model_report.txt").write_text(
        f"ROC-AUC: {auc:.4f}\n\n{report}\n", encoding="utf-8"
    )

    # Export scored creators for targeting demo
    df["p_enroll"] = pipe.predict_proba(X)[:,1]
    scored = df[["creator_id","tier","country","experiment_group","episodes_180d","listens_180d","revenue_180d","p_enroll"]].sort_values("p_enroll", ascending=False)
    scored.head(2000).to_csv(out_dir / "top_target_creators_propensity.csv", index=False)

    print(f"Propensity model ROC-AUC: {auc:.4f}")
    print(f"Wrote: {out_dir/'propensity_model_report.txt'}")

if __name__ == "__main__":
    main()
