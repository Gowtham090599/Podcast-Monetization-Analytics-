from __future__ import annotations
import duckdb
from pathlib import Path

def connect(db_path: str | Path) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(db_path))

def exec_sql(con: duckdb.DuckDBPyConnection, sql: str):
    return con.execute(sql)

def read_df(con: duckdb.DuckDBPyConnection, sql: str):
    return con.execute(sql).df()
