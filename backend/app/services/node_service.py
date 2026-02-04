"""
Node management service.
"""
from sqlalchemy.orm import Session
from app.models.node import Node
from app.models.canvas import Canvas
from typing import List
import logging

logger = logging.getLogger(__name__)


def get_node_by_id(db: Session, node_id: int) -> Node | None:
    """
    Get node by ID.

    Args:
        db: Database session
        node_id: Node ID

    Returns:
        Node object or None
    """
    return db.query(Node).filter(Node.id == node_id).first()


def get_canvas_nodes(db: Session, canvas: Canvas) -> List[Node]:
    """
    Get all nodes for a canvas.

    Args:
        db: Database session
        canvas: Canvas object

    Returns:
        List of Node objects
    """
    return db.query(Node).filter(Node.canvas_id == canvas.id).all()


def create_node(
    db: Session,
    canvas: Canvas,
    node_type: str,
    title: str,
    position_x: float,
    position_y: float,
    data: dict | None = None,
    width: int | None = None,
    height: int | None = None,
) -> Node:
    """
    Create a new node.

    Args:
        db: Database session
        canvas: Canvas to add node to
        node_type: Type of node (generic, person, meeting, etc.)
        title: Node title
        position_x: X position on canvas
        position_y: Y position on canvas
        data: Node-specific data
        width: Node width (optional)
        height: Node height (optional)

    Returns:
        Created Node object
    """
    node = Node(
        canvas_id=canvas.id,
        node_type=node_type,
        title=title,
        position_x=position_x,
        position_y=position_y,
        data=data or {},
        width=width,
        height=height,
        exclude_from_context=False,
        status=None,
    )

    db.add(node)
    db.commit()
    db.refresh(node)

    # Calculate and update content size
    update_node_content_size(db, node)

    logger.info(f"Node created: {node.id} ({node_type}) on canvas {canvas.id}")
    return node


def update_node(
    db: Session,
    node: Node,
    title: str | None = None,
    position_x: float | None = None,
    position_y: float | None = None,
    width: int | None = None,
    height: int | None = None,
    data: dict | None = None,
    exclude_from_context: bool | None = None,
    status: dict | None = None,
) -> Node:
    """
    Update node details.

    Args:
        db: Database session
        node: Node object to update
        title: New title (optional)
        position_x: New X position (optional)
        position_y: New Y position (optional)
        width: New width (optional)
        height: New height (optional)
        data: New data (optional)
        exclude_from_context: Exclude from AI context (optional)
        status: Status indicators (optional)

    Returns:
        Updated Node object
    """
    if title is not None:
        node.title = title
    if position_x is not None:
        node.position_x = position_x
    if position_y is not None:
        node.position_y = position_y
    if width is not None:
        node.width = width
    if height is not None:
        node.height = height
    if data is not None:
        node.data = data
    if exclude_from_context is not None:
        node.exclude_from_context = exclude_from_context
    if status is not None:
        node.status = status

    db.commit()
    db.refresh(node)

    # Recalculate content size if data changed
    if data is not None:
        update_node_content_size(db, node)

    logger.info(f"Node updated: {node.id}")
    return node


def delete_node(db: Session, node: Node) -> None:
    """
    Delete a node.

    Args:
        db: Database session
        node: Node to delete
    """
    node_id = node.id
    db.delete(node)
    db.commit()

    logger.info(f"Node deleted: {node_id}")


def update_node_content_size(db: Session, node: Node) -> Node:
    """
    Calculate and update the content size of a node.

    Args:
        db: Database session
        node: Node object

    Returns:
        Updated Node object
    """
    # Calculate size based on node data
    size = len(node.title)

    if node.data:
        # Add size of all string values in data
        for key, value in node.data.items():
            if isinstance(value, str):
                size += len(value)
            elif isinstance(value, (list, dict)):
                # Rough estimate for complex data
                size += len(str(value))

    node.content_size = size
    db.commit()
    db.refresh(node)

    return node


def get_node_context_string(node: Node, summarize: bool = False) -> str:
    """
    Get node content as a string for AI context.

    Args:
        node: Node object
        summarize: Whether to summarize if content is large

    Returns:
        String representation of node content
    """
    if node.exclude_from_context:
        return ""

    # Build context string
    context = f"# {node.title} ({node.node_type})\n\n"

    if node.data:
        for key, value in node.data.items():
            if isinstance(value, str):
                context += f"**{key}**: {value}\n"
            elif isinstance(value, (list, dict)):
                context += f"**{key}**: {str(value)}\n"

    # TODO: Add summarization logic if content is too large
    # For now, just return as-is
    return context


def bulk_update_node_positions(
    db: Session,
    updates: List[dict]
) -> List[Node]:
    """
    Update positions of multiple nodes at once.
    Useful for efficient canvas updates.

    Args:
        db: Database session
        updates: List of dicts with {id, position_x, position_y}

    Returns:
        List of updated Node objects
    """
    updated_nodes = []

    for update in updates:
        node = get_node_by_id(db, update['id'])
        if node:
            node.position_x = update.get('position_x', node.position_x)
            node.position_y = update.get('position_y', node.position_y)
            updated_nodes.append(node)

    db.commit()

    for node in updated_nodes:
        db.refresh(node)

    logger.info(f"Bulk updated {len(updated_nodes)} node positions")
    return updated_nodes
