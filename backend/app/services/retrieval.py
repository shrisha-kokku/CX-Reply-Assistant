# Finds the KB entries that are relevant to the customer's message.
#
# Approach: keyword matching, not embeddings. Why:
#  - each brand has only a handful of policies, so embeddings add cost and moving parts for no gain
#  - it's predictable: easy to see (and explain) why an entry was or wasn't picked
#  - the brand filter is plain SQL (brand_id = ...), so another brand's policy can never be returned
# At 500 brands with large KBs I would switch to vector search (Qdrant) with a brand_id filter.
import re

from app.db import run

# Words in the customer's message that point to a policy category.
# A word matches if the message contains a word that starts with it ("deliver" matches "delivered").
CATEGORY_KEYWORDS = {
    "refund": ["refund", "money", "reimburs", "broken", "damage", "defect", "faulty"],
    "return": ["return", "exchange", "replace", "broken", "damage", "defect", "faulty", "wrong", "leak"],
    "shipping": ["ship", "deliver", "arriv", "receiv", "track", "delay"],
    "cancellation": ["cancel"],
}


def _words(text):
    return re.findall(r"[a-z]+", text.lower())


def _score(entry, message_words):
    """How many of the category's keywords appear in the message."""
    if entry["category"] == "other":
        # custom entries: count shared (longer) words with the entry text
        entry_words = set(_words(entry["title"] + " " + entry["content"]))
        return len({w for w in message_words if len(w) > 4 and w in entry_words})

    keywords = CATEGORY_KEYWORDS.get(entry["category"], [])
    return sum(1 for kw in keywords if any(w.startswith(kw) for w in message_words))


def find_relevant_entries(brand_id, message, limit=3):
    """Top KB entries of THIS brand for the message. Empty list if nothing matches."""
    # The brand filter is the isolation rule: only this brand's rows are ever loaded.
    entries = run(
        "select id, category, title, content from kb_entries where brand_id = %s",
        (brand_id,),
    )
    message_words = _words(message)

    scored = [(_score(e, message_words), e) for e in entries]
    scored = [item for item in scored if item[0] > 0]
    scored.sort(key=lambda item: item[0], reverse=True)
    return [e for _, e in scored[:limit]]
