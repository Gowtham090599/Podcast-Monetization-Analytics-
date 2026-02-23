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
from sklearn.ensemble import RandomForestClassifier
from src.utils.db import connect, read_df

# churn label: no episodes in last 30 days (proxy)
SQL = r"""
WITH last_day AS (
  SELECT max(published_at::DATE) AS max_ds FROM raw_episodes
),
episodes_30d AS (
  SELECT
    e.creator_id,
    count(*) AS episodes_last_30d
  FROM raw_episodes e
  CROSS JOIN last_day d
  WHERE e.published_at::DATE >= d.max_ds - INTERVAL 30 DAY
  GROUP BY 1
),
episodes_180d AS (
  SELECT creator_id, count(*) AS episodes_180d
  FROM raw_episodes
  GROUP BY 1
),
listens_180d AS (
  SELECT creator_id, sum(listens) AS listens_180d
  FROM raw_listening_events
  GROUP BY 1
)
SELECT
  c.creator_id,
  c.tier,
  c.country,
  c.experiment_group,
  coalesce(e30.episodes_last_30d,0) AS episodes_last_30d,
  coalesce(e180.episodes_180d,0) AS episodes_180d,
  coalesce(l180.listens_180d,0) AS listens_180d,
  CASE WHEN coalesce(e30.episodes_last_30d,0)=0 THEN 1 ELSE 0 END AS label_churn
FROM raw_creators c
LEFT JOIN episodes_30d e30 USING(creator_id)
LEFT JOIN episodes_180d e180 USING(creator_id)
LEFT JOIN listens_180d l180 USING(creator_id);
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db_path", type=str, default="warehouse.duckdb")
    ap.add_argument("--out_dir", type=str, default="outputs")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    con = connect(args.db_path)
    df = read_df(con, SQL)
    con.close()

    y = df["label_churn"].astype(int)
    X = df.drop(columns=["label_churn"])

    cat_cols = ["tier", "country", "experiment_group"]
    num_cols = ["episodes_last_30d", "episodes_180d", "listens_180d"]

    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ("num", "passthrough", num_cols),
    ])

    clf = RandomForestClassifier(
        n_estimators=250, random_state=7, n_jobs=-1, max_depth=10, min_samples_leaf=20
    )
    pipe = Pipeline([("pre", pre), ("clf", clf)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=7, stratify=y)

    pipe.fit(X_train, y_train)
    proba = pipe.predict_proba(X_test)[:,1]
    auc = roc_auc_score(y_test, proba)
    preds = (proba >= 0.5).astype(int)
    report = classification_report(y_test, preds, output_dict=False)

    (out_dir / "churn_model_report.txt").write_text(
        f"ROC-AUC: {auc:.4f}\n\n{report}\n", encoding="utf-8"
    )

    df["p_churn"] = pipe.predict_proba(X)[:,1]
    df.sort_values("p_churn", ascending=False).head(2000).to_csv(out_dir / "top_at_risk_creators_churn.csv", index=False)

    print(f"Churn model ROC-AUC: {auc:.4f}")
    print(f"Wrote: {out_dir/'churn_model_report.txt'}")

if __name__ == "__main__":
    main()
