from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from uuid import uuid4

from langchain_core.messages import HumanMessage
from app.agents.graph import workflow

router = APIRouter()




@router.post("/chat")
async def chat(message: str, conversation_id: Optional[str] = None):
    """Main chat endpoint — routes through the LangGraph agent."""
    try:
        conversation_id = conversation_id if conversation_id else uuid4().hex
        initial_state = {
            'messages': [HumanMessage(content=message)]
        }
        config = {"configurable": {"thread_id": conversation_id}}
        result = workflow.invoke(initial_state, config=config)
        return {"result": result, "conversation_id": conversation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a text or PDF document for RAG indexing."""
    allowed = {".txt", ".pdf", ".md"}
    # based on uploaded file, index the document into vector store
    pass


