from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Loading the datas
# loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
loader = WebBaseLoader("https://www.automatebusiness.com/")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

OLLAMA_BASE_URL = "http://100.68.93.4:11434"

# Using embedding model
local_embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)
vectorstore = Chroma.from_documents(documents=all_splits, embedding=local_embeddings)

# question = "What are the approaches to Task Decomposition?"
# docs = vectorstore.similarity_search(question)
# print(len(docs))
# print(docs[0])

# # Using main LLM
model = ChatOllama(model="llama3.1:8b", base_url=OLLAMA_BASE_URL)
# response_message = model.invoke(
#     "Simulate a rap battle between Stephen Colbert and John Oliver"
# )

# print(response_message.content)

# Q&A with retrieval
RAG_TEMPLATE = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

<context>
{context}
</context>

Answer the following question:

{question}"""

rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

retriever = vectorstore.as_retriever()

# Convert loaded documents into strings by concatenating their content
# and ignoring metadata
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | model
    | StrOutputParser()
)

question = "How can I accelerate business growth?"

answer = qa_chain.invoke(question)
print(answer)