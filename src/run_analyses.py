from __future__ import annotations
import argparse
from pathlib import Path
from src.analyses import funnel, ab_test, monitoring
from src.modeling import train_propensity, train_churn

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db_path", type=str, default="warehouse.duckdb")
    p.add_argument("--out_dir", type=str, default="outputs")
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    funnel.run(args.db_path, out_dir)
    ab_test.run(args.db_path, out_dir)
    monitoring.run(args.db_path, out_dir)

    # Train models (optional but impressive for interviews)
    train_propensity.main()
    train_churn.main()

if __name__ == "__main__":
    main()
