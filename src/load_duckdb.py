from __future__ import annotations
import argparse
from pathlib import Path
import duckdb

TABLES = {
    "raw_creators": "creators.csv",
    "raw_podcasts": "podcasts.csv",
    "raw_episodes": "episodes.csv",
    "raw_creator_events": "creator_events.csv",
    "raw_listening_events": "listening_events.csv",
    "raw_revenue_events": "revenue_events.csv",
}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db_path", type=str, default="warehouse.duckdb")
    p.add_argument("--data_dir", type=str, default="data")
    args = p.parse_args()

    db_path = Path(args.db_path)
    data_dir = Path(args.data_dir)

    con = duckdb.connect(str(db_path))
    con.execute("PRAGMA threads=8;")

    for table, fname in TABLES.items():
        fpath = data_dir / fname
        if not fpath.exists():
            raise FileNotFoundError(f"Missing {fpath}")
        con.execute(f"DROP TABLE IF EXISTS {table};")
        con.execute(f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto('{str(fpath).replace("'","''")}');")
        con.execute(f"CREATE OR REPLACE VIEW v_{table} AS SELECT * FROM {table};")
        print(f"Loaded {table} from {fname}")

    # Helpful indexes (DuckDB uses zone maps; still fine to add)
    con.close()
    print(f"Warehouse ready: {db_path.resolve()}")

if __name__ == "__main__":
    main()
