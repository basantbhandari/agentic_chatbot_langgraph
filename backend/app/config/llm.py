from langchain_ollama import ChatOllama, OllamaEmbeddings

llm = ChatOllama(
    model="llama3.1",
    temperature=0.2
)

embeddings_llm = OllamaEmbeddings(model="nomic-embed-text")

