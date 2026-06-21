from langchain_ollama import ChatOllama, OllamaEmbeddings

from app.config.constants import (
    OLLAMA_CHAT_MODEL,
    OLLAMA_EMBEDDING_MODEL,
    OLLAMA_CHAT_MODEL_TEMPERATURE,
)
from app.models.schema import IntentClassification, AppointmentBooking
from app.tools import llm_tools

llm = ChatOllama(model=OLLAMA_CHAT_MODEL, temperature=OLLAMA_CHAT_MODEL_TEMPERATURE)
llm_with_tools = llm.bind_tools(llm_tools)

intent_classification_structure_llm = llm.with_structured_output(IntentClassification)
appointment_booking_structure_llm = llm_with_tools.with_structured_output(
    AppointmentBooking
)
embeddings_llm = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
