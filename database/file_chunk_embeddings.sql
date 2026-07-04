create table if not exists public.file_chunk_embeddings (
    id uuid primary key default gen_random_uuid(),
    chunk_id uuid not null references public.file_chunks(id) on delete cascade,
    embedding_model text not null,
    embedding double precision[] not null,
    created_at timestamptz not null default now(),
    unique (chunk_id, embedding_model)
);

create index if not exists idx_file_chunk_embeddings_chunk_id
on public.file_chunk_embeddings(chunk_id);
