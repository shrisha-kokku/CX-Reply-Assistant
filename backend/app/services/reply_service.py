# The AI reply flow: load conversation -> retrieve KB -> ask LLM -> apply guardrails -> log.
from datetime import datetime, timezone

from psycopg2.extras import Json

from app.db import run
from app.services.conversation import get_conversation
from app.services.llm import call_llm, parse_json
from app.services.retrieval import find_relevant_entries

# Used when the KB has nothing on the question. We don't even call the LLM in that case.
HOLDING_REPLY = (
    "Thank you for reaching out. I'm checking this with our team "
    "and will get back to you shortly."
)

SYSTEM_PROMPT = """You draft replies for a human customer support agent.

Rules:
1. Use ONLY the policies given below. Do not use outside knowledge and do not guess.
2. Different policies have different time windows (for example reporting damage vs requesting a refund). Check the time since delivery against EACH window separately, and use the window written in the policy that fits the customer's situation. If any relevant window has passed, or two policies point in different directions, say so politely and use confidence "low".
3. Never promise a refund, replacement or exception unless the policy clearly allows it for THIS order.
   If the customer is outside a time window, or the policy is unclear, politely say what the policy says
   and that the team will review it.
4. If the policies do not answer the question, say you will check with the team and use confidence "low".
5. When quoting a time window, say it as the policy states it (for example "within 48 hours of delivery"). Never restart or extend it.
6. Keep the reply under 80 words.
7. Keep it short and polite. Address the customer by first name. Do not sign off with a name.

Return ONLY a JSON object, nothing else:
{"reply": "text for the customer",
 "confidence": "high" or "low",
 "used_entry_ids": [ids of the policies you used],
 "note": "one line telling the agent why you answered this way"}
Use "high" only when a policy clearly answers the question and the order facts clearly fit it."""


def _time_since(moment):
    """'1 day 3 hours (27 hours total)'. Done in code so the LLM never has to do date maths."""
    if moment is None:
        return "not delivered yet / unknown"
    hours = int((datetime.now(timezone.utc) - moment).total_seconds() // 3600)
    return f"{hours // 24} days {hours % 24} hours ({hours} hours total)"


def _build_user_prompt(convo, entries):
    order = convo["order"]
    if order:
        order_text = (
            f"{order['product']}, amount {order['amount']}, status {order['status']}, "
            f"delivered {_time_since(order['delivered_at'])} ago"
        )
    else:
        order_text = "no order linked"

    policies = "\n".join(f"[id {e['id']}] {e['title']}: {e['content']}" for e in entries)
    history = "\n".join(f"{m['sender'].capitalize()}: {m['body']}" for m in convo["messages"][-10:])

    return (
        f"Brand: {convo['brand']['name']}\n"
        f"Customer: {convo['customer']['name']}\n"
        f"Order: {order_text}\n\n"
        f"Policies:\n{policies}\n\n"
        f"Conversation so far:\n{history}\n\n"
        "Write the next agent reply to the customer's latest message."
    )


def _ask_llm(convo, entries):
    """Returns (reply, confidence, used_ids, note). Falls back safely if the model misbehaves."""
    text = call_llm(SYSTEM_PROMPT, _build_user_prompt(convo, entries))
    data = parse_json(text)

    if not data or not str(data.get("reply", "")).strip():
        # model ignored the format: keep its text but force low confidence
        return text.strip(), "low", [], "Model did not follow the output format. Please review carefully."

    confidence = data.get("confidence") if data.get("confidence") in ("high", "low") else "low"
    valid_ids = {e["id"] for e in entries}
    used_ids = [i for i in data.get("used_entry_ids", []) if i in valid_ids]  # drop made-up ids
    return str(data["reply"]).strip(), confidence, used_ids, str(data.get("note", ""))


def generate_reply(conversation_id):
    """Runs the full flow for the latest customer message and logs the result."""
    convo = get_conversation(conversation_id)
    if convo is None:
        raise LookupError("Conversation not found")
    latest = convo["latest_customer_message"]
    if latest is None:
        raise ValueError("There is no customer message to reply to")

    # The brand comes from the conversation itself, never from the request.
    entries = find_relevant_entries(convo["brand"]["id"], latest["body"])

    if not entries:
        reply, confidence, used_ids = HOLDING_REPLY, "none", []
        note = "No knowledge base entry matches this question. Check with the brand and edit before sending."
    else:
        reply, confidence, used_ids, note = _ask_llm(convo, entries)

    needs_review = confidence != "high"
    context = [{**e, "used": e["id"] in used_ids} for e in entries]

    # A new generation replaces the previous suggestion (this is also how "Regenerate" works)
    run(
        "update ai_generations set status = 'discarded' where conversation_id = %s and status = 'generated'",
        (conversation_id,),
        fetch=None,
    )
    row = run(
        """
        insert into ai_generations
            (conversation_id, customer_message_id, retrieved_context, ai_reply, confidence, needs_review)
        values (%s, %s, %s, %s, %s, %s)
        returning id, status, ai_reply, confidence, needs_review, retrieved_context, created_at
        """,
        (conversation_id, latest["id"], Json(context), reply, confidence, needs_review),
        fetch="one",
    )
    row["note"] = note  # shown to the agent, not stored
    return row


def approve_generation(generation_id, final_reply):
    """Agent approves (original or edited text). Sends it into the chat and logs it."""
    final_reply = final_reply.strip()
    if not final_reply:
        raise ValueError("Reply cannot be empty")

    gen = run("select * from ai_generations where id = %s", (generation_id,), fetch="one")
    if gen is None:
        raise LookupError("Generation not found")
    if gen["status"] != "generated":
        raise ValueError("This suggestion was already approved or replaced")

    message = run(
        """
        insert into messages (conversation_id, sender, body, sent_by_ai)
        values (%s, 'agent', %s, true)
        returning id, sender, body, sent_by_ai, created_at
        """,
        (gen["conversation_id"], final_reply),
        fetch="one",
    )

    # edited_reply is only filled when the agent actually changed the AI text
    edited = final_reply if final_reply != gen["ai_reply"] else None
    run(
        "update ai_generations set edited_reply = %s, final_reply = %s, status = 'approved' where id = %s",
        (edited, final_reply, generation_id),
        fetch=None,
    )
    return message
