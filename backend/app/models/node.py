"""Node model"""
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Node(BaseModel):
    """Canvas node"""

    __tablename__ = "nodes"

    canvas_id = Column(Integer, ForeignKey("canvases.id"), nullable=False)
    node_type = Column(String, nullable=False)  # person, meeting, document, generic, etc.
    title = Column(String, nullable=False)

    # Node position and size
    position_x = Column(Float, nullable=False, default=0)
    position_y = Column(Float, nullable=False, default=0)
    width = Column(Integer, nullable=True)  # null = auto
    height = Column(Integer, nullable=True)  # null = auto

    # Node data (type-specific)
    data = Column(JSON, nullable=False, default=dict)

    # Status indicators
    status = Column(JSON, nullable=True)  # {warnings: [], indicators: []}

    # Context management
    exclude_from_context = Column(Integer, default=False, nullable=False)  # Boolean stored as int
    content_size = Column(Integer, nullable=True)  # Cached size in characters

    # Relationships
    canvas = relationship("Canvas", back_populates="nodes")
    chats = relationship("Chat", back_populates="node", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Node {self.title} ({self.node_type}) canvas={self.canvas_id}>"
