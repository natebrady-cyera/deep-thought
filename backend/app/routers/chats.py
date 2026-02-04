"""Chat endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.chat import Chat, ChatMessage
from app.services.canvas_service import get_canvas_by_id, can_user_access_canvas
from app.services.node_service import get_canvas_nodes
from app.services.claude_service import (
    chat_with_claude,
    build_canvas_context,
    create_sales_assistant_prompt,
    create_whats_next_prompt,
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chats")


class ChatCreate(BaseModel):
    canvas_id: int
    name: str
    chat_type: str  # 'sales_assistant' or 'whats_next'
    node_id: Optional[int] = None  # For node-level chats


class MessageCreate(BaseModel):
    content: str
    include_canvas_context: Optional[bool] = True  # Whether to include full canvas context


class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime
    token_count: Optional[int] = None

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    id: int
    name: str
    canvas_id: int
    chat_type: str
    created_at: datetime
    message_count: int


@router.get("/canvas/{canvas_id}", response_model=List[ChatResponse])
async def list_canvas_chats(
    canvas_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all chats for a canvas"""
    canvas = get_canvas_by_id(db, canvas_id)
    if not canvas:
        raise HTTPException(status_code=404, detail="Canvas not found")

    if not can_user_access_canvas(db, current_user, canvas):
        raise HTTPException(status_code=403, detail="Access denied")

    chats = db.query(Chat).filter(Chat.canvas_id == canvas_id, Chat.node_id == None).all()

    return [
        ChatResponse(
            id=chat.id,
            name=chat.name,
            canvas_id=chat.canvas_id,
            chat_type=chat.chat_type,
            created_at=chat.created_at,
            message_count=len(chat.messages),
        )
        for chat in chats
    ]


@router.get("/node/{node_id}", response_model=List[ChatResponse])
async def list_node_chats(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all chats for a specific node"""
    from app.models.node import Node

    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    canvas = get_canvas_by_id(db, node.canvas_id)
    if not can_user_access_canvas(db, current_user, canvas):
        raise HTTPException(status_code=403, detail="Access denied")

    chats = db.query(Chat).filter(Chat.node_id == node_id).all()

    return [
        ChatResponse(
            id=chat.id,
            name=chat.name,
            canvas_id=chat.canvas_id,
            chat_type=chat.chat_type,
            created_at=chat.created_at,
            message_count=len(chat.messages),
        )
        for chat in chats
    ]


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new chat session"""
    canvas = get_canvas_by_id(db, chat_data.canvas_id)
    if not canvas:
        raise HTTPException(status_code=404, detail="Canvas not found")

    if not can_user_access_canvas(db, current_user, canvas):
        raise HTTPException(status_code=403, detail="Access denied")

    # Create chat
    chat = Chat(
        name=chat_data.name,
        canvas_id=chat_data.canvas_id,
        chat_type=chat_data.chat_type,
        node_id=chat_data.node_id,
        parent_chat_id=None,
        context_snapshot=None,  # Will be built on first message
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    logger.info(f"Chat created: {chat.id} for canvas {canvas.id}")

    return ChatResponse(
        id=chat.id,
        name=chat.name,
        canvas_id=chat.canvas_id,
        chat_type=chat.chat_type,
        created_at=chat.created_at,
        message_count=0,
    )


@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all messages in a chat"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    canvas = get_canvas_by_id(db, chat.canvas_id)
    if not can_user_access_canvas(db, current_user, canvas):
        raise HTTPException(status_code=403, detail="Access denied")

    return chat.messages


@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message and get Claude's response"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    canvas = get_canvas_by_id(db, chat.canvas_id)
    if not can_user_access_canvas(db, current_user, canvas):
        raise HTTPException(status_code=403, detail="Access denied")

    # Build context from canvas or node
    if not message_data.include_canvas_context and chat.node_id:
        # Only include this specific node's context
        from app.models.node import Node
        node = db.query(Node).filter(Node.id == chat.node_id).first()
        if node:
            nodes_data = [
                {
                    'title': node.title,
                    'node_type': node.node_type,
                    'data': node.data,
                    'exclude_from_context': False,
                }
            ]
            canvas_data = {
                'name': canvas.name,
                'description': f"Focus: {node.title}",
            }
        else:
            nodes_data = []
            canvas_data = {'name': canvas.name, 'description': canvas.description}
    else:
        # Include full canvas context
        nodes = get_canvas_nodes(db, canvas)
        nodes_data = [
            {
                'title': n.title,
                'node_type': n.node_type,
                'data': n.data,
                'exclude_from_context': n.exclude_from_context,
            }
            for n in nodes
        ]
        canvas_data = {
            'name': canvas.name,
            'description': canvas.description,
        }

    canvas_context = build_canvas_context(canvas_data, nodes_data)

    # Build system prompt based on chat type
    if chat.chat_type == 'sales_assistant':
        system_prompt = create_sales_assistant_prompt(canvas_context)
    elif chat.chat_type == 'whats_next':
        system_prompt = create_whats_next_prompt(canvas_context)
    else:
        system_prompt = canvas_context

    # Save user message
    user_message = ChatMessage(
        chat_id=chat.id,
        role='user',
        content=message_data.content,
        token_count=None,
    )
    db.add(user_message)
    db.commit()

    # Build messages for Claude (conversation history)
    previous_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat.id, ChatMessage.role.in_(['user', 'assistant']))
        .order_by(ChatMessage.created_at)
        .all()
    )

    claude_messages = [
        {'role': msg.role, 'content': msg.content}
        for msg in previous_messages
    ]

    try:
        # Call Claude
        response = chat_with_claude(
            messages=claude_messages,
            system_prompt=system_prompt,
            max_tokens=4096,
        )

        # Save assistant response
        assistant_message = ChatMessage(
            chat_id=chat.id,
            role='assistant',
            content=response['content'],
            token_count=response.get('usage', {}).get('output_tokens'),
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        logger.info(f"Chat message processed: chat={chat.id}, tokens={assistant_message.token_count}")

        return assistant_message

    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get AI response: {str(e)}"
        )


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a chat"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    canvas = get_canvas_by_id(db, chat.canvas_id)
    if not can_user_access_canvas(db, current_user, canvas):
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(chat)
    db.commit()

    logger.info(f"Chat deleted: {chat_id}")


@router.put("/{chat_id}/rename")
async def rename_chat(
    chat_id: int,
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rename a chat"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    canvas = get_canvas_by_id(db, chat.canvas_id)
    if not can_user_access_canvas(db, current_user, canvas):
        raise HTTPException(status_code=403, detail="Access denied")

    chat.name = name
    db.commit()

    return {"message": "Chat renamed successfully"}
