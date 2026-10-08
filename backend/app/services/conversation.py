# Loads a conversation with everything the agent screen (and the AI) needs.
from app.db import run


def get_conversation(conversation_id):
    """Returns the conversation (customer, brand, order, messages) or None if not found."""
    row = run(
        """
        select c.id, c.brand_id, b.name as brand_name,
               cu.name as customer_name, cu.email as customer_email,
               o.id as order_id, o.product, o.amount, o.status as order_status, o.delivered_at
        from conversations c
        join brands b     on b.id  = c.brand_id
        join customers cu on cu.id = c.customer_id
        left join orders o on o.id = c.order_id
        where c.id = %s
        """,
        (conversation_id,),
        fetch="one",
    )
    if row is None:
        return None

    messages = run(
        "select id, sender, body, sent_by_ai, created_at from messages where conversation_id = %s order by id",
        (conversation_id,),
    )
    customer_messages = [m for m in messages if m["sender"] == "customer"]

    order = None
    if row["order_id"]:
        order = {
            "id": row["order_id"],
            "product": row["product"],
            "amount": row["amount"],
            "status": row["order_status"],
            "delivered_at": row["delivered_at"],
        }

    return {
        "id": row["id"],
        "brand": {"id": row["brand_id"], "name": row["brand_name"]},
        "customer": {"name": row["customer_name"], "email": row["customer_email"]},
        "order": order,
        "messages": messages,
        "latest_customer_message": customer_messages[-1] if customer_messages else None,
    }
