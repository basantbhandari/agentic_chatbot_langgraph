from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from uuid import uuid4

from langchain_core.messages import HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.utils.helper import load_documents

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
        from app.dependencies import workflow
        result = workflow.invoke(initial_state,
                                 config=config)
        return {"result": result, "conversation_id": conversation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a text or PDF document for RAG indexing."""
    documents = load_documents(file)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)
    vectorstore.add_documents(chunks)
    retriever = vectorstore.as_retriever()
    return {
        "message": "Document uploaded successfully",
        "chunks": len(chunks)
    }


