.PHONY: data test app

data:
	python -m src.pipeline

test:
	pytest -q

app:
	streamlit run app.py
