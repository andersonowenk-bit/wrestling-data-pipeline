rank:
	python -m teams.rank

fetch:
	python -m teams.fetch

dashboard:
	streamlit run dashboard/app.py

test:
	pytest -q

.PHONY: rank fetch dashboard test
