from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import chromadb
import ingester
import time
import os

'''
# Loading the datas
# loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
loader = WebBaseLoader("https://www.automatebusiness.com/")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

# Using embedding model
local_embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)
vectorstore = Chroma.from_documents(documents=all_splits, embedding=local_embeddings)
'''

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL")

def get_retriever():
    # Using ingester and server db
    CHROMA_HOST = os.environ.get("CHROMA_HOST")
    CHROMA_PORT = 8000
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    local_embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)
    vector_store = Chroma(
            client=chroma_client,
            collection_name="AYB",
            embedding_function=local_embeddings,
            persist_directory="AYB_vectordb",  
        )
    # ingester.ingest_website(local_embeddings, vector_store)
    retriever = vector_store.as_retriever()
    return retriever

def setup_rag():
    # Using main LLM
    model = ChatOllama(model="llama3.1:8b", base_url=OLLAMA_BASE_URL)

    # Q&A with retrieval
    RAG_TEMPLATE = """
    You are customer support for company called Automate Your Business. 
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. 
    Use three sentences maximum and keep the answer concise.

    <context>
    {context}
    </context>

    Answer the following question:

    {question}"""

    rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

    # Convert loaded documents into strings by concatenating their content
    # and ignoring metadata
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    qa_chain = (
        {"context": get_retriever() | format_docs, "question": RunnablePassthrough()}
        | rag_prompt
        | model
        | StrOutputParser()
    )

    return qa_chain

def handle_question(question, qa_chain):
    start_time = time.time()
    answer = qa_chain.invoke(question)
    # print(answer)
    total_time = time.time()  - start_time
    print('Total Time:',round(total_time,2))
    return answer

def main():
    qa_chain = setup_rag()
    print("I am Automate Your Business Customer Support. Please ask your queries. Press Ctrl+D followed by Enter to exit.")
    while True:
        try:
            user_input = input("Question: ")
            if user_input.strip():  # Check if the input is not empty
                print('Please wait, processing message...')
                answer = handle_question(user_input, qa_chain)
                print(f"Answer: {answer}")
            else:
                print("Please enter a valid question.")
        except EOFError:
            print("\nEnd of input detected. Exiting the program.")
            break

if __name__ == "__main__":
    main()