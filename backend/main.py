from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langchain_postgres import PGVector
from app import dependencies
from app.agents.node import chat_node
from app.config.constants import DB_URI, COLLECTION_NAME
from app.config.llm import embeddings_llm
from app.models.schema import ChatState
from app.routers.chat import router as chat_router
from app.config.logger import logger
from contextlib import asynccontextmanager

checkpointer: Optional[PostgresSaver] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global checkpointer

    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        checkpointer.setup()

        graph = StateGraph(ChatState)
        graph.add_node('chat_node', chat_node)
        graph.add_edge(START, 'chat_node')
        graph.add_edge('chat_node', END)
        dependencies.workflow = graph.compile(checkpointer=checkpointer)
        try:
            dependencies.vectorstore = PGVector(
                connection=DB_URI,
                embeddings=embeddings_llm,
                collection_name=COLLECTION_NAME
            )
            dependencies.retriever = dependencies.vectorstore.as_retriever()
            logger.info("Vector DB ready")
        except Exception as e:
            dependencies.retriever = None
            logger.error(f"No existing vector DB, skipping: {e}")

        yield
        # PostgresSaver cleans up automatically when 'with' block exits here


app = FastAPI(
    title="Context-Aware Conversational Agent",
    description="LangGraph-powered chatbot with Document QA and Appointment Booking",
    version="1.0.0",
    lifespan = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api", tags=["Chat"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
