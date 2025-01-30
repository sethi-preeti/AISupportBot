# Script to ingest documents

from langchain_community.document_loaders import WebBaseLoader
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

def get_sub_urls(base_url):
    """Fetch the sub URLs from the base URL."""
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
    response = requests.get(base_url, headers = headers)
    if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return []  # Return an empty list if there's an error
    soup = BeautifulSoup(response.text, 'html.parser')
    urls = [urljoin(base_url, link.get('href')) for link in soup.find_all('a')]
    return urls

def ingest_website(local_embeddings):
    BASE_URL = "https://www.automatebusiness.com/"
    # urls = get_sub_urls(BASE_URL)
    # urls.append(BASE_URL)
    urls = [BASE_URL]
    for url in urls:
        loader = WebBaseLoader(url)
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        all_splits = text_splitter.split_documents(data)
        print(len(all_splits))
        vectorstore = Chroma.from_documents(documents=all_splits, embedding=local_embeddings, persist_directory="vectordb")
        
if __name__=="__main__":
    OLLAMA_BASE_URL = "http://100.68.93.4:11434"
    local_embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)
    ingest_website(local_embeddings)