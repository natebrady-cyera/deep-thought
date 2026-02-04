"""Node management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.node_schemas import (
    NodeCreate,
    NodeUpdate,
    NodeResponse,
    BulkNodePositionUpdate,
)
from app.services.node_service import (
    get_node_by_id,
    get_canvas_nodes,
    create_node as create_node_service,
    update_node as update_node_service,
    delete_node as delete_node_service,
    bulk_update_node_positions,
)
from app.services.canvas_service import (
    get_canvas_by_id,
    can_user_access_canvas,
    can_user_write_canvas,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/nodes")


def check_node_access(db: Session, user: User, node_id: int, require_write: bool = False):
    """
    Helper to check node access via canvas permissions.
    Raises HTTPException if access denied.
    """
    node = get_node_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    canvas = get_canvas_by_id(db, node.canvas_id)
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

    return node, canvas


@router.get("/types")
async def list_node_types():
    """
    List available node types.

    For MVP, we only have generic nodes.
    Future: person, meeting, document, salesforce, etc.
    """
    return {
        "node_types": [
            {
                "type": "generic",
                "label": "Generic Note",
                "description": "Freeform text note",
                "icon": "📝"
            },
            # Future node types
            # {
            #     "type": "person",
            #     "label": "Person",
            #     "description": "Key stakeholder or contact",
            #     "icon": "👤"
            # },
        ]
    }


@router.get("/canvas/{canvas_id}", response_model=List[NodeResponse])
async def list_canvas_nodes(
    canvas_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all nodes for a canvas.

    User must have access to the canvas.
    """
    canvas = get_canvas_by_id(db, canvas_id)
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canvas not found"
        )

    if not can_user_access_canvas(db, current_user, canvas):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    nodes = get_canvas_nodes(db, canvas)
    return nodes


@router.post("/", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    node_data: NodeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new node.

    User must have write access to the canvas.
    """
    canvas = get_canvas_by_id(db, node_data.canvas_id)
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canvas not found"
        )

    if not can_user_write_canvas(db, current_user, canvas):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Write access required"
        )

    node = create_node_service(
        db,
        canvas=canvas,
        node_type=node_data.node_type,
        title=node_data.title,
        position_x=node_data.position_x,
        position_y=node_data.position_y,
        data=node_data.data,
        width=node_data.width,
        height=node_data.height,
    )

    return node


@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get node details.

    User must have access to the canvas.
    """
    node, canvas = check_node_access(db, current_user, node_id)
    return node


@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: int,
    node_data: NodeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update node details.

    User must have write access to the canvas.
    """
    node, canvas = check_node_access(db, current_user, node_id, require_write=True)

    node = update_node_service(
        db,
        node,
        title=node_data.title,
        position_x=node_data.position_x,
        position_y=node_data.position_y,
        width=node_data.width,
        height=node_data.height,
        data=node_data.data,
        exclude_from_context=node_data.exclude_from_context,
        status=node_data.status,
    )

    return node


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a node.

    User must have write access to the canvas.
    """
    node, canvas = check_node_access(db, current_user, node_id, require_write=True)
    delete_node_service(db, node)


@router.post("/bulk-update-positions", response_model=List[NodeResponse])
async def bulk_update_positions(
    bulk_update: BulkNodePositionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update positions of multiple nodes at once.

    Useful for efficient canvas updates when dragging multiple nodes.
    User must have write access to all nodes' canvases.
    """
    # Verify access to all nodes
    for update in bulk_update.updates:
        node, canvas = check_node_access(db, current_user, update.id, require_write=True)

    # Perform bulk update
    updated_nodes = bulk_update_node_positions(
        db,
        [{"id": u.id, "position_x": u.position_x, "position_y": u.position_y}
         for u in bulk_update.updates]
    )

    return updated_nodes
