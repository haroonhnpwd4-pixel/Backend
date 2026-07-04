create table if not exists public.file_chunks (
    id uuid primary key default gen_random_uuid(),
    file_id uuid not null references public.files(id) on delete cascade,
    chunk_index integer not null,
    content text not null,
    created_at timestamptz not null default now(),
    unique (file_id, chunk_index)
);

create index if not exists idx_file_chunks_file_id on public.file_chunks(file_id);
