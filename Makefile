.PHONY: install serve ingest brief resume clean

PYTHON ?= python3

install:
	$(PYTHON) -m pip install -e .

serve:
	PYTHONPATH=src uvicorn ato_copilot.api.main:app --reload --port 8000

ingest:
	PYTHONPATH=src $(PYTHON) -m ato_copilot.rag.ingest --query "approved technology list cloud database"

brief:
	$(PYTHON) scripts/build_brief_pdf.py

resume:
	$(PYTHON) scripts/build_resume_pdf.py

clean:
	rm -rf .venv .pytest_cache traces
	find . -name __pycache__ -type d -exec rm -rf {} +
