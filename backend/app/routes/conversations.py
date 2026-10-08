from fastapi import APIRouter, HTTPException

from app.db import run
from app.schemas import MessageIn
from app.services.conversation import get_conversation

router = APIRouter()


@router.get("/brands")
def list_brands():
    return run("select id, name from brands order by id")


@router.get("/conversations")
def list_conversations():
    return run(
        """
        select c.id, b.name as brand_name, cu.name as customer_name,
               (select body from messages m where m.conversation_id = c.id order by m.id desc limit 1) as last_message
        from conversations c
        join brands b     on b.id  = c.brand_id
        join customers cu on cu.id = c.customer_id
        order by c.id
        """
    )


@router.get("/conversations/{conversation_id}")
def read_conversation(conversation_id: int):
    convo = get_conversation(conversation_id)
    if convo is None:
        raise HTTPException(404, "Conversation not found")
    return convo


@router.post("/conversations/{conversation_id}/messages")
def send_message(conversation_id: int, data: MessageIn):
    """Used for both sides: sender='customer' (test as customer) or 'agent' (manual reply)."""
    if get_conversation(conversation_id) is None:
        raise HTTPException(404, "Conversation not found")
    if not data.body.strip():
        raise HTTPException(400, "Message cannot be empty")

    return run(
        """
        insert into messages (conversation_id, sender, body)
        values (%s, %s, %s)
        returning id, sender, body, sent_by_ai, created_at
        """,
        (conversation_id, data.sender, data.body.strip()),
        fetch="one",
    )
