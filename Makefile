.PHONY: all test pipeline figures report presentation run clean

all: test pipeline figures report presentation

test:
	.venv/bin/pytest src/tests || .venv/Scripts/pytest src/tests

pipeline:
	.venv/bin/python src/pipeline.py || .venv/Scripts/python src/pipeline.py

figures:
	.venv/bin/python src/generate_figures.py || .venv/Scripts/python src/generate_figures.py

report:
	.venv/bin/python src/generate_report.py || .venv/Scripts/python src/generate_report.py

presentation:
	.venv/bin/python src/generate_presentation.py || .venv/Scripts/python src/generate_presentation.py

run:
	.venv/bin/streamlit run app.py || .venv/Scripts/streamlit run app.py
