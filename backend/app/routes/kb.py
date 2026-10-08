# Knowledge base management. Every route has brand_id in the URL, and every query filters on it,
# so an entry of Brand A can't be read, edited or deleted through Brand B's URL.
from fastapi import APIRouter, HTTPException

from app.db import run
from app.schemas import KBEntryIn

router = APIRouter()


@router.get("/brands/{brand_id}/kb")
def list_entries(brand_id: int):
    return run(
        "select id, brand_id, category, title, content, updated_at from kb_entries where brand_id = %s order by id",
        (brand_id,),
    )


@router.post("/brands/{brand_id}/kb")
def create_entry(brand_id: int, data: KBEntryIn):
    if run("select 1 from brands where id = %s", (brand_id,), fetch="one") is None:
        raise HTTPException(404, "Brand not found")
    return run(
        """
        insert into kb_entries (brand_id, category, title, content)
        values (%s, %s, %s, %s)
        returning id, brand_id, category, title, content, updated_at
        """,
        (brand_id, data.category, data.title, data.content),
        fetch="one",
    )


@router.put("/brands/{brand_id}/kb/{entry_id}")
def update_entry(brand_id: int, entry_id: int, data: KBEntryIn):
    row = run(
        """
        update kb_entries set category = %s, title = %s, content = %s, updated_at = now()
        where id = %s and brand_id = %s
        returning id, brand_id, category, title, content, updated_at
        """,
        (data.category, data.title, data.content, entry_id, brand_id),
        fetch="one",
    )
    if row is None:
        raise HTTPException(404, "Entry not found for this brand")
    return row


@router.delete("/brands/{brand_id}/kb/{entry_id}")
def delete_entry(brand_id: int, entry_id: int):
    row = run(
        "delete from kb_entries where id = %s and brand_id = %s returning id",
        (entry_id, brand_id),
        fetch="one",
    )
    if row is None:
        raise HTTPException(404, "Entry not found for this brand")
    return {"deleted": entry_id}
