import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from uuid import uuid4
from langchain_postgres import PGVector
from langchain_core.messages import HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.constants import (
    TEXT_SPLITTER_CHUNK_SIZE,
    TEXT_SPLITTER_CHUNK_OVERLAP,
    KNOWLEDGE_DIR, COLLECTION_NAME, DB_URI,
)
from app.config.llm import embeddings_llm
from app.utils.helper import load_documents

router = APIRouter()


@router.post("/chat")
async def chat(message: str, conversation_id: Optional[str] = None):
    """Main chat endpoint — routes through the LangGraph agent."""
    try:
        conversation_id = conversation_id if conversation_id else uuid4().hex
        initial_state = {"messages": [HumanMessage(content=message)]}
        config = {"configurable": {"thread_id": conversation_id}}
        from app.dependencies import workflow

        result = workflow.invoke(initial_state, config=config)
        return {"result": result, "conversation_id": conversation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a text or PDF document for RAG indexing."""

    # 1. Validate filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    # 2. Ensure upload directory exists
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

    # 3. Safe file extension handling
    if "." not in file.filename:
        raise HTTPException(status_code=400, detail="File has no extension")

    file_name = Path(file.filename)
    file_ext = file_name.suffix

    # restrict file types
    if file_ext not in {".pdf", ".txt", ".md"}:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {file_ext}"
        )

    file_name_no_ext = file_name.stem

    # 4. Create safe filename
    updated_filename = f"{file_name_no_ext}_{uuid4()}{file_ext}"
    file_path = os.path.join(KNOWLEDGE_DIR, updated_filename)

    # 5. Save file safely
    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    # 6. Load document
    documents = load_documents(file_path)

    if not documents:
        raise HTTPException(status_code=400, detail="Failed to parse document")

    # 7. Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=TEXT_SPLITTER_CHUNK_SIZE, chunk_overlap=TEXT_SPLITTER_CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)

    # 8. Store in vector DB
    from app.dependencies import vectorstore

    vectorstore.add_documents(chunks)

    return {
        "message": "Document uploaded successfully",
        "chunks": len(chunks),
        "file_path": file_path,
    }


@router.delete("/reset-knowledgebase")
async def reset_knowledgebase():
    """
    Deletes ALL files + ALL vector index + collection reset
    """
    knowledge_base_dir = Path(KNOWLEDGE_DIR)
    # 1. Delete all files from disk
    if knowledge_base_dir.exists():
        shutil.rmtree(knowledge_base_dir)
        knowledge_base_dir.mkdir(parents=True, exist_ok=True)

    # 2. Reset vector store completely
    try:
        from app import dependencies
        dependencies.vectorstore.delete_collection()
        dependencies.vectorstore = PGVector(
            connection=DB_URI,
            embeddings=embeddings_llm,
            collection_name=COLLECTION_NAME,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Files deleted but vector reset failed: {str(e)}"
        )

    return {"message": "Knowledge base fully reset (files + vectors + collection)"}
