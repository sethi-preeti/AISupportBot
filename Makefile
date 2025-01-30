run: 
	. venv/bin/activate && python3 rag.py

ingest: 
	. venv/bin/activate && python3 ingester.py

setup:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && curl -fsSL https://ollama.com/install.sh | sh
	. venv/bin/activate && ollama pull llama3.1:8b
	. venv/bin/activate && ollama pull nomic-embed-text