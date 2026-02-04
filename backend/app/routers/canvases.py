"""Canvas management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.dependencies import get_current_user, get_current_manager
from app.models.user import User, UserRole
from app.schemas.canvas_schemas import (
    CanvasCreate,
    CanvasUpdate,
    CanvasResponse,
    CanvasListItem,
    CanvasShareCreate,
    CanvasShareInfo,
    UserInfo,
)
from app.services.canvas_service import (
    get_canvas_by_id,
    get_user_canvases,
    get_all_canvases,
    create_canvas as create_canvas_service,
    update_canvas as update_canvas_service,
    delete_canvas as delete_canvas_service,
    archive_canvas as archive_canvas_service,
    unarchive_canvas,
    can_user_access_canvas,
    can_user_write_canvas,
    share_canvas as share_canvas_service,
    unshare_canvas,
    get_canvas_shares,
)
from app.services.user_service import get_user_by_email
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/canvases")


def check_canvas_access(db: Session, user: User, canvas_id: int, require_write: bool = False):
    """
    Helper to check canvas access and return canvas.
    Raises HTTPException if access denied.
    """
    canvas = get_canvas_by_id(db, canvas_id)
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canvas not found"
        )

    if not can_user_access_canvas(db, user, canvas):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if require_write and not can_user_write_canvas(db, user, canvas):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Write access required"
        )

    return canvas


@router.get("/", response_model=List[CanvasListItem])
async def list_canvases(
    include_archived: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all canvases accessible to current user.

    - Regular users see their own canvases + shared canvases
    - Sales managers and admins see all canvases
    """
    # Sales managers and admins can see all canvases
    if current_user.role in [UserRole.ADMIN, UserRole.SALES_MANAGER]:
        canvases = get_all_canvases(db, include_archived=include_archived)
    else:
        canvases = get_user_canvases(db, current_user, include_archived=include_archived)

    # Build response with additional metadata
    result = []
    for canvas in canvases:
        is_owner = canvas.owner_id == current_user.id
        is_shared = not is_owner
        can_write = can_user_write_canvas(db, current_user, canvas)
        node_count = len(canvas.nodes) if hasattr(canvas, 'nodes') else 0

        result.append(CanvasListItem(
            id=canvas.id,
            name=canvas.name,
            description=canvas.description,
            owner_id=canvas.owner_id,
            owner_email=canvas.owner.email,
            is_archived=canvas.is_archived,
            created_at=canvas.created_at,
            updated_at=canvas.updated_at,
            is_owner=is_owner,
            can_write=can_write,
            is_shared=is_shared,
            node_count=node_count,
        ))

    return result


@router.post("/", response_model=CanvasResponse, status_code=status.HTTP_201_CREATED)
async def create_canvas(
    canvas_data: CanvasCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new canvas.

    The current user becomes the owner.
    """
    canvas = create_canvas_service(
        db,
        owner=current_user,
        name=canvas_data.name,
        description=canvas_data.description,
    )

    return CanvasResponse(
        id=canvas.id,
        name=canvas.name,
        description=canvas.description,
        owner_id=canvas.owner_id,
        is_archived=canvas.is_archived,
        viewport=canvas.viewport,
        created_at=canvas.created_at,
        updated_at=canvas.updated_at,
        is_owner=True,
        can_write=True,
        is_shared=False,
    )


@router.get("/{canvas_id}", response_model=CanvasResponse)
async def get_canvas(
    canvas_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get canvas details.

    User must have access to the canvas.
    """
    canvas = check_canvas_access(db, current_user, canvas_id)

    is_owner = canvas.owner_id == current_user.id
    can_write = can_user_write_canvas(db, current_user, canvas)

    return CanvasResponse(
        id=canvas.id,
        name=canvas.name,
        description=canvas.description,
        owner_id=canvas.owner_id,
        is_archived=canvas.is_archived,
        viewport=canvas.viewport,
        created_at=canvas.created_at,
        updated_at=canvas.updated_at,
        is_owner=is_owner,
        can_write=can_write,
        is_shared=not is_owner,
    )


@router.put("/{canvas_id}", response_model=CanvasResponse)
async def update_canvas(
    canvas_id: int,
    canvas_data: CanvasUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update canvas details.

    User must have write access to the canvas.
    """
    canvas = check_canvas_access(db, current_user, canvas_id, require_write=True)

    canvas = update_canvas_service(
        db,
        canvas,
        name=canvas_data.name,
        description=canvas_data.description,
        viewport=canvas_data.viewport,
    )

    is_owner = canvas.owner_id == current_user.id

    return CanvasResponse(
        id=canvas.id,
        name=canvas.name,
        description=canvas.description,
        owner_id=canvas.owner_id,
        is_archived=canvas.is_archived,
        viewport=canvas.viewport,
        created_at=canvas.created_at,
        updated_at=canvas.updated_at,
        is_owner=is_owner,
        can_write=True,
        is_shared=not is_owner,
    )


@router.delete("/{canvas_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_canvas(
    canvas_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a canvas.

    Only the owner can delete a canvas.
    """
    canvas = check_canvas_access(db, current_user, canvas_id)

    # Only owner or admin can delete
    if canvas.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete a canvas"
        )

    delete_canvas_service(db, canvas)


@router.post("/{canvas_id}/archive", response_model=CanvasResponse)
async def archive_canvas(
    canvas_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Archive a canvas.

    Only the owner can archive a canvas.
    """
    canvas = check_canvas_access(db, current_user, canvas_id)

    if canvas.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can archive a canvas"
        )

    canvas = archive_canvas_service(db, canvas)

    return CanvasResponse(
        id=canvas.id,
        name=canvas.name,
        description=canvas.description,
        owner_id=canvas.owner_id,
        is_archived=canvas.is_archived,
        viewport=canvas.viewport,
        created_at=canvas.created_at,
        updated_at=canvas.updated_at,
        is_owner=True,
        can_write=True,
        is_shared=False,
    )


@router.post("/{canvas_id}/unarchive", response_model=CanvasResponse)
async def unarchive_canvas_endpoint(
    canvas_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Unarchive a canvas.

    Only the owner can unarchive a canvas.
    """
    canvas = get_canvas_by_id(db, canvas_id)
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canvas not found"
        )

    if canvas.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can unarchive a canvas"
        )

    canvas = unarchive_canvas(db, canvas)

    return CanvasResponse(
        id=canvas.id,
        name=canvas.name,
        description=canvas.description,
        owner_id=canvas.owner_id,
        is_archived=canvas.is_archived,
        viewport=canvas.viewport,
        created_at=canvas.created_at,
        updated_at=canvas.updated_at,
        is_owner=True,
        can_write=True,
        is_shared=False,
    )


@router.post("/{canvas_id}/share", response_model=CanvasShareInfo, status_code=status.HTTP_201_CREATED)
async def share_canvas(
    canvas_id: int,
    share_data: CanvasShareCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Share canvas with another user.

    Only the owner can share a canvas.
    """
    canvas = check_canvas_access(db, current_user, canvas_id)

    if canvas.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can share a canvas"
        )

    # Get user to share with
    target_user = get_user_by_email(db, share_data.user_email)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Can't share with self
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot share canvas with yourself"
        )

    share = share_canvas_service(db, canvas, target_user, share_data.can_write)

    return CanvasShareInfo(
        id=share.id,
        user=UserInfo(
            id=target_user.id,
            email=target_user.email,
            full_name=target_user.full_name,
            role=target_user.role.value,
        ),
        can_write=share.can_write,
        created_at=share.created_at,
    )


@router.delete("/{canvas_id}/share/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unshare_canvas_endpoint(
    canvas_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove canvas share for a user.

    Only the owner can unshare a canvas.
    """
    canvas = check_canvas_access(db, current_user, canvas_id)

    if canvas.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can unshare a canvas"
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    unshare_canvas(db, canvas, target_user)


@router.get("/{canvas_id}/shares", response_model=List[CanvasShareInfo])
async def list_canvas_shares(
    canvas_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all users the canvas is shared with.

    Only the owner can view shares.
    """
    canvas = check_canvas_access(db, current_user, canvas_id)

    if canvas.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can view shares"
        )

    shares = get_canvas_shares(db, canvas)

    return [
        CanvasShareInfo(
            id=share.id,
            user=UserInfo(
                id=share.user.id,
                email=share.user.email,
                full_name=share.user.full_name,
                role=share.user.role.value,
            ),
            can_write=share.can_write,
            created_at=share.created_at,
        )
        for share in shares
    ]
