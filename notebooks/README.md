# Notebooks

Use notebooks for exploring, not for pipeline code. Once something works, move it into `ingest/`, `ratings/`, or `models/`.

Suggested notebooks:
- `01_data_exploration.ipynb`: match counts, result types, weight class changes
- `02_elo_tuning.ipynb`: try different K values and season regression, compare accuracy
- `03_model_analysis.ipynb`: where the model is wrong and why

Clear outputs before committing large notebooks.
