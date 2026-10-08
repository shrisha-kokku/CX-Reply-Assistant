-- Run this once in the Supabase SQL editor.
-- Every table that holds brand data has a brand_id, so data is always tied to one brand.

create table brands (
  id   serial primary key,
  name text not null unique
);

-- Brand knowledge base (policies). Managed from the app (create/edit/delete).
create table kb_entries (
  id         serial primary key,
  brand_id   int  not null references brands(id) on delete cascade,
  category   text not null check (category in ('return','refund','shipping','cancellation','other')),
  title      text not null,
  content    text not null,
  updated_at timestamptz not null default now()
);
create index on kb_entries (brand_id);

create table customers (
  id       serial primary key,
  brand_id int  not null references brands(id),
  name     text not null,
  email    text
);

create table orders (
  id           serial primary key,
  brand_id     int  not null references brands(id),
  customer_id  int  not null references customers(id),
  product      text not null,
  amount       numeric(10,2) not null,
  status       text not null,            -- e.g. 'delivered'
  delivered_at timestamptz
);

create table conversations (
  id          serial primary key,
  brand_id    int not null references brands(id),
  customer_id int not null references customers(id),
  order_id    int references orders(id),
  created_at  timestamptz not null default now()
);

-- The chat itself. sender is 'customer' or 'agent'.
create table messages (
  id              serial primary key,
  conversation_id int  not null references conversations(id) on delete cascade,
  sender          text not null check (sender in ('customer','agent')),
  body            text not null,
  sent_by_ai      boolean not null default false,  -- true if the agent sent an AI-suggested reply
  created_at      timestamptz not null default now()
);

-- One row per "Generate Reply" click. This is our log / audit trail.
create table ai_generations (
  id                   serial primary key,
  conversation_id      int  not null references conversations(id) on delete cascade,
  customer_message_id  int  not null references messages(id),
  retrieved_context    jsonb not null,           -- KB entries that were given to the LLM
  ai_reply             text,                     -- what the AI suggested
  confidence           text,                     -- 'high' | 'low' | 'none'
  needs_review         boolean not null default false,
  edited_reply         text,                     -- agent's edited version (if any)
  final_reply          text,                     -- what was finally sent
  status               text not null default 'generated',  -- generated | approved | discarded
  created_at           timestamptz not null default now()
);
