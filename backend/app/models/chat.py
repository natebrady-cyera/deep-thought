"""Chat models"""
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Chat(BaseModel):
    """Chat session"""

    __tablename__ = "chats"

    name = Column(String, nullable=False)  # User-renameable
    canvas_id = Column(Integer, ForeignKey("canvases.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=True)  # None = deal-level chat
    parent_chat_id = Column(Integer, ForeignKey("chats.id"), nullable=True)  # For "continue from"

    # Chat type: 'persona' (with node), 'sales_assistant', 'whats_next'
    chat_type = Column(String, nullable=False)

    # Canvas context snapshot (at chat creation)
    context_snapshot = Column(JSON, nullable=True)

    # Relationships
    canvas = relationship("Canvas", back_populates="chats")
    node = relationship("Node", back_populates="chats")
    parent_chat = relationship("Chat", remote_side="Chat.id")
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chat {self.name} ({self.chat_type}) canvas={self.canvas_id}>"


class ChatMessage(BaseModel):
    """Individual message in a chat"""

    __tablename__ = "chat_messages"

    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)  # For cost tracking

    # Relationships
    chat = relationship("Chat", back_populates="messages")

    def __repr__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<ChatMessage {self.role}: {preview}>"
