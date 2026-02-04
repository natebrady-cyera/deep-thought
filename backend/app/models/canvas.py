"""Canvas model"""
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Canvas(BaseModel):
    """Deal canvas"""

    __tablename__ = "canvases"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    # Canvas state (node positions, zoom, etc.)
    viewport = Column(JSON, nullable=True)  # {x, y, zoom}

    # Relationships
    owner = relationship("User", backref="canvases")
    nodes = relationship("Node", back_populates="canvas", cascade="all, delete-orphan")
    shares = relationship("CanvasShare", back_populates="canvas", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="canvas", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Canvas {self.name} (owner={self.owner_id})>"


class CanvasShare(BaseModel):
    """Canvas sharing permissions"""

    __tablename__ = "canvas_shares"

    canvas_id = Column(Integer, ForeignKey("canvases.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    can_write = Column(Boolean, default=False, nullable=False)  # False = read-only

    # Relationships
    canvas = relationship("Canvas", back_populates="shares")
    user = relationship("User")

    def __repr__(self):
        access = "read-write" if self.can_write else "read-only"
        return f"<CanvasShare canvas={self.canvas_id} user={self.user_id} ({access})>"
