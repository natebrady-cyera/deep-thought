"""
Canvas management service.
"""
from sqlalchemy.orm import Session
from app.models.canvas import Canvas, CanvasShare
from app.models.user import User, UserRole
from typing import List
import logging

logger = logging.getLogger(__name__)


def get_canvas_by_id(db: Session, canvas_id: int) -> Canvas | None:
    """
    Get canvas by ID.

    Args:
        db: Database session
        canvas_id: Canvas ID

    Returns:
        Canvas object or None
    """
    return db.query(Canvas).filter(Canvas.id == canvas_id).first()


def get_user_canvases(db: Session, user: User, include_archived: bool = False) -> List[Canvas]:
    """
    Get all canvases accessible to a user (owned + shared).

    Args:
        db: Database session
        user: User object
        include_archived: Include archived canvases

    Returns:
        List of Canvas objects
    """
    # Start with owned canvases
    query = db.query(Canvas).filter(Canvas.owner_id == user.id)

    if not include_archived:
        query = query.filter(Canvas.is_archived == False)

    owned_canvases = query.all()

    # Add shared canvases
    shared_query = (
        db.query(Canvas)
        .join(CanvasShare, Canvas.id == CanvasShare.canvas_id)
        .filter(CanvasShare.user_id == user.id)
    )

    if not include_archived:
        shared_query = shared_query.filter(Canvas.is_archived == False)

    shared_canvases = shared_query.all()

    # Combine and return
    all_canvases = owned_canvases + shared_canvases

    # Remove duplicates (shouldn't happen, but just in case)
    seen = set()
    unique_canvases = []
    for canvas in all_canvases:
        if canvas.id not in seen:
            seen.add(canvas.id)
            unique_canvases.append(canvas)

    return unique_canvases


def get_all_canvases(db: Session, include_archived: bool = False) -> List[Canvas]:
    """
    Get all canvases (for sales managers/admins).

    Args:
        db: Database session
        include_archived: Include archived canvases

    Returns:
        List of Canvas objects
    """
    query = db.query(Canvas)

    if not include_archived:
        query = query.filter(Canvas.is_archived == False)

    return query.all()


def create_canvas(
    db: Session,
    owner: User,
    name: str,
    description: str | None = None,
) -> Canvas:
    """
    Create a new canvas.

    Args:
        db: Database session
        owner: User who owns the canvas
        name: Canvas name
        description: Optional canvas description

    Returns:
        Created Canvas object
    """
    canvas = Canvas(
        name=name,
        description=description,
        owner_id=owner.id,
        is_archived=False,
        viewport={"x": 0, "y": 0, "zoom": 1},
    )

    db.add(canvas)
    db.commit()
    db.refresh(canvas)

    logger.info(f"Canvas created: {canvas.id} by user {owner.email}")
    return canvas


def update_canvas(
    db: Session,
    canvas: Canvas,
    name: str | None = None,
    description: str | None = None,
    viewport: dict | None = None,
) -> Canvas:
    """
    Update canvas details.

    Args:
        db: Database session
        canvas: Canvas object to update
        name: New name (optional)
        description: New description (optional)
        viewport: New viewport state (optional)

    Returns:
        Updated Canvas object
    """
    if name is not None:
        canvas.name = name
    if description is not None:
        canvas.description = description
    if viewport is not None:
        canvas.viewport = viewport

    db.commit()
    db.refresh(canvas)

    logger.info(f"Canvas updated: {canvas.id}")
    return canvas


def delete_canvas(db: Session, canvas: Canvas) -> None:
    """
    Delete a canvas and all associated data.

    Args:
        db: Database session
        canvas: Canvas to delete
    """
    canvas_id = canvas.id
    db.delete(canvas)
    db.commit()

    logger.info(f"Canvas deleted: {canvas_id}")


def archive_canvas(db: Session, canvas: Canvas) -> Canvas:
    """
    Archive a canvas.

    Args:
        db: Database session
        canvas: Canvas to archive

    Returns:
        Archived Canvas object
    """
    canvas.is_archived = True
    db.commit()
    db.refresh(canvas)

    logger.info(f"Canvas archived: {canvas.id}")
    return canvas


def unarchive_canvas(db: Session, canvas: Canvas) -> Canvas:
    """
    Unarchive a canvas.

    Args:
        db: Database session
        canvas: Canvas to unarchive

    Returns:
        Unarchived Canvas object
    """
    canvas.is_archived = False
    db.commit()
    db.refresh(canvas)

    logger.info(f"Canvas unarchived: {canvas.id}")
    return canvas


def can_user_access_canvas(db: Session, user: User, canvas: Canvas) -> bool:
    """
    Check if user has any access to canvas.

    Args:
        db: Database session
        user: User object
        canvas: Canvas object

    Returns:
        True if user can access canvas
    """
    # Owner can always access
    if canvas.owner_id == user.id:
        return True

    # Sales managers and admins can access all canvases
    if user.role in [UserRole.ADMIN, UserRole.SALES_MANAGER]:
        return True

    # Check if canvas is shared with user
    share = (
        db.query(CanvasShare)
        .filter(
            CanvasShare.canvas_id == canvas.id,
            CanvasShare.user_id == user.id,
        )
        .first()
    )

    return share is not None


def can_user_write_canvas(db: Session, user: User, canvas: Canvas) -> bool:
    """
    Check if user has write access to canvas.

    Args:
        db: Database session
        user: User object
        canvas: Canvas object

    Returns:
        True if user can write to canvas
    """
    # Owner can always write
    if canvas.owner_id == user.id:
        return True

    # Admins can write to all canvases
    if user.role == UserRole.ADMIN:
        return True

    # Check if canvas is shared with write access
    share = (
        db.query(CanvasShare)
        .filter(
            CanvasShare.canvas_id == canvas.id,
            CanvasShare.user_id == user.id,
            CanvasShare.can_write == True,
        )
        .first()
    )

    return share is not None


def share_canvas(
    db: Session,
    canvas: Canvas,
    user: User,
    can_write: bool = False,
) -> CanvasShare:
    """
    Share canvas with a user.

    Args:
        db: Database session
        canvas: Canvas to share
        user: User to share with
        can_write: Grant write access

    Returns:
        Created CanvasShare object
    """
    # Check if already shared
    existing_share = (
        db.query(CanvasShare)
        .filter(
            CanvasShare.canvas_id == canvas.id,
            CanvasShare.user_id == user.id,
        )
        .first()
    )

    if existing_share:
        # Update existing share
        existing_share.can_write = can_write
        db.commit()
        db.refresh(existing_share)
        logger.info(f"Canvas share updated: {canvas.id} with user {user.email}")
        return existing_share

    # Create new share
    share = CanvasShare(
        canvas_id=canvas.id,
        user_id=user.id,
        can_write=can_write,
    )

    db.add(share)
    db.commit()
    db.refresh(share)

    logger.info(f"Canvas shared: {canvas.id} with user {user.email}")
    return share


def unshare_canvas(db: Session, canvas: Canvas, user: User) -> None:
    """
    Remove canvas share for a user.

    Args:
        db: Database session
        canvas: Canvas to unshare
        user: User to remove access from
    """
    share = (
        db.query(CanvasShare)
        .filter(
            CanvasShare.canvas_id == canvas.id,
            CanvasShare.user_id == user.id,
        )
        .first()
    )

    if share:
        db.delete(share)
        db.commit()
        logger.info(f"Canvas unshared: {canvas.id} from user {user.email}")


def get_canvas_shares(db: Session, canvas: Canvas) -> List[CanvasShare]:
    """
    Get all shares for a canvas.

    Args:
        db: Database session
        canvas: Canvas object

    Returns:
        List of CanvasShare objects
    """
    return (
        db.query(CanvasShare)
        .filter(CanvasShare.canvas_id == canvas.id)
        .all()
    )
