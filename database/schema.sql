create extension if not exists "pgcrypto";

create table if not exists public.users (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    email text not null unique,
    password_hash text not null,
    created_at timestamptz not null default now()
);

create table if not exists public.conversations (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users(id) on delete cascade,
    title text not null,
    model text not null,
    created_at timestamptz not null default now()
);

create table if not exists public.messages (
    id uuid primary key default gen_random_uuid(),
    conversation_id uuid not null references public.conversations(id) on delete cascade,
    role text not null check (role in ('user', 'assistant', 'system')),
    content text not null,
    created_at timestamptz not null default now()
);

create table if not exists public.files (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users(id) on delete cascade,
    file_name text not null,
    file_type text not null,
    storage_url text not null,
    uploaded_at timestamptz not null default now()
);

create table if not exists public.usage_logs (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users(id) on delete cascade,
    model text not null,
    tokens_used integer not null default 0,
    cost numeric(12, 6) not null default 0,
    created_at timestamptz not null default now()
);

create table if not exists public.file_chunks (
    id uuid primary key default gen_random_uuid(),
    file_id uuid not null references public.files(id) on delete cascade,
    chunk_index integer not null,
    content text not null,
    created_at timestamptz not null default now(),
    unique (file_id, chunk_index)
);

create table if not exists public.file_chunk_embeddings (
    id uuid primary key default gen_random_uuid(),
    chunk_id uuid not null references public.file_chunks(id) on delete cascade,
    embedding_model text not null,
    embedding double precision[] not null,
    created_at timestamptz not null default now(),
    unique (chunk_id, embedding_model)
);

create index if not exists idx_conversations_user_id on public.conversations(user_id);
create index if not exists idx_messages_conversation_id on public.messages(conversation_id);
create index if not exists idx_files_user_id on public.files(user_id);
create index if not exists idx_usage_logs_user_id on public.usage_logs(user_id);
create index if not exists idx_file_chunks_file_id on public.file_chunks(file_id);
create index if not exists idx_file_chunk_embeddings_chunk_id on public.file_chunk_embeddings(chunk_id);
