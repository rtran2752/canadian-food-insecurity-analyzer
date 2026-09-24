# Canadian Food Insecurity & Food-Bank Demand Analyzer

An interactive Python and Streamlit analysis of provincial food-bank usage,
food insecurity, and client demographics using public Canadian data.

## Key findings

- **Ontario recorded the largest absolute increase** among comparable provinces:
  March food-bank visits rose from 339,613 in 2019 to 763,756 in 2025—an
  increase of **424,143 visits (+124.9%)**.
- **Alberta recorded the largest percentage increase:** visits rose from 89,821
  to 210,541, an increase of **120,720 visits (+134.4%)**.
- **Saskatchewan had the largest increase in food insecurity:** the share of
  people living in food-insecure households increased from 17.2% in 2019 to
  30.6% in 2024, a rise of **13.4 percentage points**.
- **Alberta had the highest reported food-insecurity rate in 2024 at 30.9%**, while
  Quebec had the lowest among the ten provinces at 19.8%.
- Employment as the main source of income rose from 12.1% of food-bank clients
  in 2019 to 19.4% in 2025, while reliance primarily on social assistance fell
  from 40.1% to 28.7%.

These are descriptive comparisons, not causal claims. Manitoba is excluded
from 2019–2025 visit rankings because Food Banks Canada marks that comparison
as non-comparable.

## What the project delivers

- Reproducible validation and ETL pipeline for three public datasets
- Ranked provincial change tables with absolute and percentage differences
- Interactive dashboard with headline findings, filters, charts, and tables
- PostgreSQL schema and analytical queries for reproducible exploration
- Tests covering source reconciliation, data validity, and headline results

## Why this version is credible

- Every analytical value traces to Food Banks Canada or Statistics Canada
  estimates republished by PROOF.
- Raw values are preserved in human-readable CSV files.
- HungerCount is correctly modelled as an annual March snapshot—not invented
  monthly data.
- Manitoba's non-comparable 2019 trend is suppressed in the pipeline.
- Food-bank visits and food insecurity are kept as distinct concepts.
- The dashboard explicitly documents coverage, reporting, and inference limits.

## Data included

| Dataset | Years | Grain |
|---|---:|---|
| HungerCount provincial visits | 2019, 2024, 2025 | province × March snapshot |
| People in food-insecure households | 2019–2024 | province × year |
| National food-bank client profile | 2019, 2024, 2025 | Canada × year |

The ten-province visit totals exclude the combined territorial row. The app
does not silently compare the provincial sum with the published Canada total.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.pipeline
streamlit run app.py
```

Tests: `pytest -q`

## Structure

```text
app.py                     interactive Streamlit dashboard
data/raw/                  transcribed/downloaded public-source values
data/processed/            reproducible pipeline outputs
data/source_manifest.csv   source URLs, report pages, retrieval date
src/pipeline.py            validation, joins, metrics, suppressions
sql/                       PostgreSQL schema and analysis queries
tests/                     source-reconciliation and validation tests
```

## Questions answered

- How did March food-bank visits change from 2019 to 2025?
- Which provinces experienced the largest increase?
- How has food insecurity changed across provinces since 2019?
- How do food insecurity and reported food-bank visits differ as measures?
- How has the national client profile changed?

The dashboard presents the answers directly; generated tables are also saved in
`data/processed/provincial_visit_change_2019_2025.csv` and
`data/processed/provincial_food_insecurity_change_2019_2024.csv`.

## What this project intentionally does not do

It does not train a forecasting model. Three annual HungerCount snapshots are
not enough for a defensible provincial forecast, and interpolating them into
monthly observations would create false data. A future model should use genuine
monthly operational records from participating food-bank networks.

## Sources

- [Food Banks Canada — HungerCount 2025](https://foodbankscanada.ca/hunger-in-canada/hungercount/)
- [HungerCount 2024 PDF](https://content.foodbankscanada.ca/wordpress/2024/10/hungercount-2024-en.pdf)
- [HungerCount 2019 PDF](https://content.foodbankscanada.ca/wordpress/2025/07/HungerCount-2019_FINAL.pdf)
- [PROOF food-insecurity reporting](https://proof.utoronto.ca/)

See `data/source_manifest.csv` for field-level provenance.

## License

MIT for original code. Source data retain their original terms and attribution.
