"""
Pydantic schemas for node endpoints.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List


class NodeCreate(BaseModel):
    """Schema for creating a node"""
    canvas_id: int = Field(..., description="Canvas ID to add node to")
    node_type: str = Field(..., description="Type of node (generic, person, meeting, etc.)")
    title: str = Field(..., min_length=1, max_length=255, description="Node title")
    position_x: float = Field(..., description="X position on canvas")
    position_y: float = Field(..., description="Y position on canvas")
    data: Optional[Dict[str, Any]] = Field(default={}, description="Node-specific data")
    width: Optional[int] = Field(None, description="Node width in pixels")
    height: Optional[int] = Field(None, description="Node height in pixels")


class NodeUpdate(BaseModel):
    """Schema for updating a node"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    exclude_from_context: Optional[bool] = None
    status: Optional[Dict[str, Any]] = None


class NodePositionUpdate(BaseModel):
    """Schema for updating just a node's position"""
    id: int
    position_x: float
    position_y: float


class BulkNodePositionUpdate(BaseModel):
    """Schema for bulk updating node positions"""
    updates: List[NodePositionUpdate]


class NodeResponse(BaseModel):
    """Schema for node response"""
    id: int
    canvas_id: int
    node_type: str
    title: str
    position_x: float
    position_y: float
    width: Optional[int]
    height: Optional[int]
    data: Dict[str, Any]
    exclude_from_context: bool
    content_size: Optional[int]
    status: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
