"""
Pydantic schemas for canvas endpoints.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CanvasCreate(BaseModel):
    """Schema for creating a canvas"""
    name: str = Field(..., min_length=1, max_length=255, description="Canvas name")
    description: Optional[str] = Field(None, max_length=1000, description="Canvas description")


class CanvasUpdate(BaseModel):
    """Schema for updating a canvas"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Canvas name")
    description: Optional[str] = None
    viewport: Optional[dict] = None


class CanvasShareCreate(BaseModel):
    """Schema for sharing a canvas"""
    user_email: str = Field(..., description="Email of user to share with")
    can_write: bool = Field(False, description="Grant write access")


class UserInfo(BaseModel):
    """User information"""
    id: int
    email: str
    full_name: Optional[str]
    role: str


class CanvasShareInfo(BaseModel):
    """Canvas share information"""
    id: int
    user: UserInfo
    can_write: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CanvasResponse(BaseModel):
    """Schema for canvas response"""
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    is_archived: bool
    viewport: Optional[dict]
    created_at: datetime
    updated_at: datetime
    is_owner: bool = Field(..., description="Whether current user is the owner")
    can_write: bool = Field(..., description="Whether current user can write")
    is_shared: bool = Field(..., description="Whether canvas is shared with current user")

    class Config:
        from_attributes = True


class CanvasListItem(BaseModel):
    """Schema for canvas list item"""
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    owner_email: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    is_owner: bool
    can_write: bool
    is_shared: bool
    node_count: int = 0

    class Config:
        from_attributes = True
