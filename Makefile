-include secrets.mk

export OLLAMA_BASE_URL
export CHROMA_HOST
export BASE_URL

run:
	. venv/bin/activate && streamlit run src/app.py

test: 
	. venv/bin/activate && python3 src/rag.py

ingest: 
	. venv/bin/activate && python3 src/ingester.py > ingester_logs.txt

setup: setup_local_ollama
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

setup_local_ollama: 
	. venv/bin/activate && curl -fsSL https://ollama.com/install.sh | sh
	. venv/bin/activate && ollama pull llama3.1:8b
	. venv/bin/activate && ollama pull nomic-embed-text

api:
	. venv/bin/activate && python3 src/api.py
