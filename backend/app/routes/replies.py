from typing import Optional

from fastapi import APIRouter, HTTPException

from app.db import run
from app.schemas import ApproveIn
from app.services import reply_service
from app.services.llm import LLMError

router = APIRouter()


@router.post("/conversations/{conversation_id}/generate")
def generate(conversation_id: int):
    """'Generate Reply' and 'Regenerate' both call this."""
    try:
        return reply_service.generate_reply(conversation_id)
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    except LLMError as e:
        print("LLM error:", e)  # real reason goes to the server log
        raise HTTPException(502, "AI service failed. Try again, or write the reply manually.")


@router.post("/generations/{generation_id}/approve")
def approve(generation_id: int, data: ApproveIn):
    try:
        return reply_service.approve_generation(generation_id, data.final_reply)
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/generations")
def list_generations(conversation_id: Optional[int] = None):
    """The log: customer message, retrieved context, AI reply, edited reply, final reply, timestamp."""
    return run(
        """
        select g.id, g.conversation_id, m.body as customer_message, g.retrieved_context,
               g.ai_reply, g.edited_reply, g.final_reply, g.confidence, g.status, g.created_at
        from ai_generations g
        join messages m on m.id = g.customer_message_id
        where (%s::int is null or g.conversation_id = %s::int)
        order by g.id desc
        limit 50
        """,
        (conversation_id, conversation_id),
    )
