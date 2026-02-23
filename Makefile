SHELL := /bin/bash

.PHONY: data dbt-build analyze clean

data:
	python src/generate_data.py --out_dir data --n_creators 75000 --days 180 --seed 7
	python src/load_duckdb.py --db_path warehouse.duckdb --data_dir data

dbt-build:
	cd dbt && dbt deps
	cd dbt && dbt seed
	cd dbt && dbt build

analyze:
	python src/run_analyses.py --db_path warehouse.duckdb --out_dir outputs

clean:
	rm -rf data outputs warehouse.duckdb dbt/target dbt/logs dbt/dbt_packages
