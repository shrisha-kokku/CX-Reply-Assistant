
# CX Reply Assistant

A small tool that helps a customer support agent reply to a customer. The agent clicks **Generate Reply**, the app finds that brand's policies, and an LLM drafts an answer using only those policies. The agent can edit, regenerate, approve, or write a manual reply.

- **Live app:** https://cx-reply-assistant-gamma.vercel.app
- **API (Swagger docs):** https://cx-reply-assistant-z4wa.onrender.com/docs

> The backend runs on a free Render plan and sleeps when idle. The first request can take 30-50 seconds. The AI uses a free OpenRouter model, which has daily request limits, so if a reply fails, wait a minute and try again.

## What it does

- Conversation view: customer name, brand, order info, full chat history, latest customer message
- Customer / Agent toggle, so you can send a message as the customer and then reply as the agent
- Two brands (Aurelle Skincare, HydraPure Bottles) with different policies (return, refund, shipping, cancellation)
- Knowledge base screen: create, edit, delete entries per brand
- Generate Reply shows the suggestion, a confidence label, a note for the agent, and the knowledge it used
- Edit, Regenerate, Approve, and manual send
- Logs screen: customer message, retrieved knowledge, AI reply, edited reply, final reply, timestamp

## Tech stack

| Part     | Choice                                 |
| -------- | -------------------------------------- |
| Frontend | React (Vite), plain CSS                |
| Backend  | Python, FastAPI, raw SQL with psycopg2 |
| Database | PostgreSQL on Supabase                 |
| LLM      | OpenRouter (free model)                |
| Hosting  | Vercel (frontend), Render (backend)    |

## Folder structure

```
backend/
  app/
    main.py            starts the app
    config.py          reads .env
    db.py              one run() helper for all SQL
    schemas.py         request validation
    routes/            conversations.py, kb.py, replies.py   (HTTP only)
    services/          conversation.py, retrieval.py, llm.py, reply_service.py   (the logic)
db/
  schema.sql           tables
  seed.sql             2 brands, policies, customers, orders, chats
frontend/
  src/                 App.jsx, api.js, components/
```

## Run it locally

**1. Database**
Create a Supabase project. In the SQL Editor run `db/schema.sql`, then `db/seed.sql`.
Copy the **Session pooler** connection string (Connect > Direct > Session pooler > URI).

**2. Backend**

```
cd backend
python -m venv venv
venv\Scripts\activate          (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill it in (see below), then:

```
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

**3. Frontend**

```
cd frontend
npm install
```

Copy `.env.example` to `.env` (default points to http://localhost:8000), then:

```
npm run dev
```

## Environment variables

| Variable               | Where             | Meaning                                                         |
| ---------------------- | ----------------- | --------------------------------------------------------------- |
| `DATABASE_URL`       | backend           | Postgres connection string (Supabase session pooler)            |
| `OPENROUTER_API_KEY` | backend           | OpenRouter key                                                  |
| `OPENROUTER_MODEL`   | backend           | Model id, for example`nvidia/nemotron-3-ultra-550b-a55b:free` |
| `CORS_ORIGINS`       | backend, optional | Allowed frontend URLs, default`*`                             |
| `VITE_API_URL`       | frontend          | Backend URL                                                     |

## How to test it

1. **Happy path (Aurelle):** Agent view > Priya > Generate Reply. The reply should follow Aurelle's policy.
2. **Brand isolation:** Agent view > Rahul > Generate Reply. Only HydraPure policies appear under "Knowledge used". Never Aurelle's.
3. **No promise outside the window:** Rahul's order was delivered 20 days ago and HydraPure only takes damage reports within 7 days. The reply must not promise a replacement, and confidence is Low.
4. **No knowledge:** Customer view > send "Do you sell vegan lip balm in Delhi?" > Agent view > Generate Reply. The AI is not called. The agent sees a holding reply and a "no knowledge found" warning.
5. **Back and forth:** approve a reply, then send another message as the customer and generate again.
6. **Change a policy without touching code:** Knowledge base > pick a brand > edit the refund policy > go back and regenerate. The answer follows the new text.

Note: seed data sets Priya's delivery to "1 day ago" at seed time. To reset it, run in the Supabase SQL Editor:

```sql
update orders set delivered_at = now() - interval '1 day' where id = 1;
```

## How a reply is generated

1. Load the conversation. The brand comes from the conversation, never from the request.
2. Retrieve that brand's policies that match the customer's message (`WHERE brand_id = ...`).
3. If nothing matches, stop here: no LLM call, return a safe holding reply with confidence `none`.
4. Build the prompt: brand, customer, order facts (time since delivery is calculated in code), the policies, and recent chat.
5. The LLM returns JSON: reply, confidence (high / low), policy ids used, and a note for the agent.
6. Validate the output, then save everything to `ai_generations`.

## Guardrails

- The prompt tells the model to use only the given policies and never to promise a refund, replacement, or exception unless the policy clearly allows it for this order.
- Time windows are calculated in code and given to the model as facts.
- No matching policy: the LLM is skipped and the agent is warned.
- Unusable model output (not JSON, or empty): confidence is forced to low.
- Policy ids returned by the model that were not retrieved are dropped.
- Anything that is not high confidence is shown to the agent as "Needs review".
- If the AI service fails, the API returns a clear error and the agent can still write manually.

## Key decisions

- **Plain Python, no LangChain.** The flow is a straight line, so a framework adds nothing.
- **Keyword retrieval, not embeddings.** Each brand has only a handful of entries. Keyword matching is predictable and easy to explain, and the brand filter is a plain SQL condition. Refund and return categories are linked, because a refund question often depends on the return policy (found while testing). At larger scale I would move to Qdrant with a `brand_id` filter.
- **Brand isolation in the queries.** Every KB read and write filters on `brand_id`. Editing Brand A's entry through Brand B's URL returns 404.
- **Raw SQL with one helper.** Small project, so no ORM. Every query is visible.
- **Everything is logged** in `ai_generations`, including the original AI text, the agent's edit, and the final text.
- **Row Level Security is on** in Supabase as a second layer. The backend connects directly with the database user.

## Known limitations (with more time)

- No login. I would add Supabase Auth and tie each agent to their brands.
- Keyword retrieval can miss unusual wording. I would add vector search and an evaluation set of tricky questions.
- A prompt alone cannot guarantee correct time-window logic. I would add a code-level policy check.
- No retries or timeouts beyond a single call. At scale I would use a queue, retries, and a fallback model.
- Free LLM models can disappear or be rate limited.
