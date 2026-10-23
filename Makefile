# Run `make all` to build the whole pipeline on the sample data.
PY = python

setup:
	pip install -r requirements.txt

sample-data:
	$(PY) scripts/make_sample_data.py

ingest:
	$(PY) -m ingest.load_csv

transform:
	cd dbt && dbt seed --profiles-dir . && dbt run --profiles-dir . && dbt test --profiles-dir .

ratings:
	$(PY) -m ratings.run_elo
	$(PY) -m ratings.compare_rankings

model:
	$(PY) -m models.train

dashboard:
	streamlit run dashboard/app.py

test:
	pytest -q

all: ingest transform ratings model

.PHONY: setup sample-data ingest transform ratings model dashboard test all
