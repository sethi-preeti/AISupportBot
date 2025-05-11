# Script to ingest documents

from langchain_community.document_loaders import WebBaseLoader
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import chromadb
import time

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

def url_exists(url, vector_store):
    # Use the 'where' filter to search for the filename in metadata
    results = vector_store._collection.get(
        where={"url": url},
        include=["metadatas"]
    )
    # If results are not empty, the document exists
    return len(results["metadatas"]) > 0

def ingest_website(local_embeddings, vector_store):
    BASE_URL = "https://www.automatebusiness.com/"
    urls = get_sub_urls(BASE_URL)
    urls.append(BASE_URL)
    # urls = [BASE_URL]

    # Initialize a list to hold Document objects
    documents = []

    start_time = time.time()
    for url in urls:
        if not url_exists(url, vector_store):
            print('Ingesting url:',url)
            try:
                loader = WebBaseLoader(url)
                data = loader.load()
            except requests.exceptions.RequestException as e:
                print(f"Failed to load {url}: {e}")
                continue  # Skip to the next URL

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
            all_splits = text_splitter.split_documents(data)

            # Add filename as metadata to each chunk
            for doc in all_splits:
                doc.metadata["url"] = url
                documents.append(doc)

            # print(len(all_splits))
            vector_store.add_documents(documents=documents) 
            ingested_time = time.time() - start_time
            print('Ingested url:',url, 'in time',ingested_time)
            start_time = ingested_time
        # vectorstore = Chroma.from_documents(documents=all_splits, embedding=local_embeddings, persist_directory="vectordb")
        
if __name__=="__main__":
    OLLAMA_BASE_URL = "http://100.68.93.4:11434"
    CHROMA_HOST = "http://100.68.93.4:8000"  
    CHROMA_PORT = 8000
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    local_embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)
    vector_store = Chroma(
            client=chroma_client,
            collection_name="AYB",
            embedding_function=local_embeddings,
            persist_directory="AYB_vectordb",  # Where to save data locally, remove if not necessary
        )
    ingest_website(local_embeddings, vector_store)