"""Chat endpoints"""
from fastapi import APIRouter

router = APIRouter(prefix="/chats")


@router.get("/canvas/{canvas_id}")
async def list_canvas_chats(canvas_id: int):
    """List all chats for a canvas"""
    # TODO: Implement chat listing
    return {"chats": []}


@router.post("/")
async def create_chat():
    """Create a new chat session"""
    # TODO: Implement chat creation
    return {"message": "Create chat endpoint"}


@router.get("/{chat_id}")
async def get_chat(chat_id: int):
    """Get chat details and messages"""
    # TODO: Implement chat retrieval
    return {"chat_id": chat_id}


@router.put("/{chat_id}")
async def update_chat(chat_id: int):
    """Update chat (e.g., rename)"""
    # TODO: Implement chat update
    return {"chat_id": chat_id}


@router.delete("/{chat_id}")
async def delete_chat(chat_id: int):
    """Delete chat"""
    # TODO: Implement chat deletion
    return {"chat_id": chat_id}


@router.post("/{chat_id}/messages")
async def send_message(chat_id: int):
    """Send a message in a chat"""
    # TODO: Implement message sending and Claude response
    return {"message": "Send message endpoint"}


@router.post("/whats-next")
async def whats_next():
    """Generate 'What's Next' recommendations"""
    # TODO: Implement what's next generation
    return {"message": "What's next endpoint"}
