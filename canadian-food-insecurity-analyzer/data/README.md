# Data documentation

## `raw/food_bank_visits.csv`

Provincial values transcribed from the tables in Food Banks Canada's
HungerCount 2019 (p. 11), 2024 (p. 23), and 2025 (p. 28). A visit counts each
person once each time they receive a food hamper; it does not represent a
unique client. The survey captures March of each year.

The reports also publish a combined territorial row. It is omitted here because
province-level food-insecurity comparisons focus on the ten provinces and the
territorial estimation methodology changed. Consequently, provincial sums are
slightly below the published Canada totals.

`comparable_to_2019=false` for Manitoba follows Food Banks Canada's warning
that its network structure and data-collection methods changed.

## `raw/food_insecurity_people_pct.csv`

Percent of people living in food-insecure households by province, 2019–2024.
The downloadable chart data are published by PROOF from Statistics Canada
Canadian Income Survey public tables. These are person-level prevalence
estimates—not the household-level estimates in older PROOF status reports.

## `raw/national_client_profile.csv`

Selected national percentages printed in HungerCount 2024 and 2025, including
employment income, housing, age, and household type.

## Reproducibility

`source_manifest.csv` records exact URLs, report pages, and the retrieval date.
Run `python -m src.pipeline` to validate and rebuild processed outputs.
