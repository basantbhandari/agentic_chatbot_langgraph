from langchain_ollama import ChatOllama, OllamaEmbeddings

from app.config.constants import OLLAMA_CHAT_MODEL, OLLAMA_EMBEDDING_MODEL, OLLAMA_CHAT_MODEL_TEMPERATURE

llm = ChatOllama(
    model=OLLAMA_CHAT_MODEL,
    temperature=OLLAMA_CHAT_MODEL_TEMPERATURE
)

embeddings_llm = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)

