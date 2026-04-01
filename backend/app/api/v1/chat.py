"""
This module provides chat endpoints for repository discussions, including
context retrieval from memory and file embeddings, persistence of chat history,
and AI-assisted responses for repository-aware conversations.
"""
from typing import List
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Request
from sqlalchemy import select

from app.core.dependencies import DatabaseDep
from app.core.rate_limit import rate_limit
from app.models.repository import Repository, RepositoryStatus
from app.models.chat import ChatMessage, MessageRole
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.services.ai_service import AIService
from app.services.memory_service import MemoryService
from app.services.embedding_service import EmbeddingService

router = APIRouter()


@router.post("/repositories/{repository_id}/chat", response_model=ChatMessageResponse)
@rate_limit(limit=60, window=60)
async def send_chat_message(
    request: Request,
    repository_id: int,
    message: ChatMessageCreate,
    db: DatabaseDep,
):
    """
    Send a chat message and get AI response.
    This is the REST endpoint for non-real-time chat.
    """
    stmt = select(Repository).where(Repository.id == repository_id)
    result = await db.execute(stmt)
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if repository.status != RepositoryStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Repository ingestion not completed. Status: {repository.status}",
        )
    
    user_message = ChatMessage(
        repository_id=repository_id,
        role=MessageRole.USER,
        content=message.content,
    )
    db.add(user_message)
    await db.flush()
    
    ai_service = AIService()
    memory_service = MemoryService()
    embedding_service = EmbeddingService()
    
    memories = await memory_service.get_relevant_memories(
        db=db,
        repository_id=repository_id,
        query=message.content,
        limit=5,
    )
    memory_texts = [f"{m.title}: {m.content}" for m in memories]
    
    query_embedding = await embedding_service.generate_embedding(message.content)
    similar_files = await embedding_service.search_similar(
        query_vector=query_embedding,
        limit=3,
        filter_dict={
            "must": [
                {"key": "type", "match": {"value": "file"}},
                {"key": "repository_id", "match": {"value": repository_id}},
            ]
        },
    )
    
    from app.models.file import File
    file_ids = [f["payload"]["file_id"] for f in similar_files]
    relevant_files = []
    if file_ids:
        stmt = select(File).where(File.id.in_(file_ids))
        result = await db.execute(stmt)
        files = result.scalars().all()
        relevant_files = [
            {
                "path": f.path,
                "content": f.content[:2000] if f.content else "",
            }
            for f in files
        ]
    
    stmt = select(ChatMessage).where(
        ChatMessage.repository_id == repository_id,
    ).order_by(ChatMessage.created_at.desc()).limit(10)
    result = await db.execute(stmt)
    history_messages = list(reversed(result.scalars().all()))
    chat_history = [
        {"role": msg.role.value, "content": msg.content}
        for msg in history_messages
    ]
    
    repo_context = f"Repository: {repository.github_full_name}\nDescription: {repository.github_description or 'N/A'}"
    
    ai_response = await ai_service.generate_chat_response(
        user_message=message.content,
        repository_context=repo_context,
        relevant_files=relevant_files,
        chat_history=chat_history,
        memories=memory_texts,
    )
    
    ai_message = ChatMessage(
        repository_id=repository_id,
        role=MessageRole.ASSISTANT,
        content=ai_response,
        context={
            "memories_used": [m.id for m in memories],
            "files_referenced": file_ids,
        },
    )
    db.add(ai_message)
    await db.commit()
    await db.refresh(ai_message)
    
    return ai_message


@router.get("/repositories/{repository_id}/chat", response_model=List[ChatMessageResponse])
async def get_chat_history(
    repository_id: int,
    db: DatabaseDep,
    skip: int = 0,
    limit: int = 100,
):
    """Get chat history for a repository."""
    stmt = select(Repository).where(Repository.id == repository_id)
    result = await db.execute(stmt)
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.repository_id == repository_id)
        .order_by(ChatMessage.created_at.asc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()
    
    return list(messages)


@router.websocket("/repositories/{repository_id}/chat")
async def websocket_chat(
    websocket: WebSocket,
    repository_id: int,
):
    """
    WebSocket endpoint for real-time chat.
    """
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass





