# DevNexus AI Chat Board Backend

FastAPI backend for the DevNexus AI Chat Board module. It supports JWT authentication, conversation history, file uploads, document processing, RAG document Q&A, Ollama/OpenAI chat, blog generation, social post generation, and learning plan generation.

## Features

- JWT authentication with register, login, and current-user APIs
- Conversation and message history
- Supabase PostgreSQL database integration
- Supabase Storage file uploads
- PDF, DOCX, TXT, and CSV document text extraction
- Document chunking and chunk storage
- RAG document chat with semantic embeddings
- Ollama support for local chat and local embeddings
- Optional OpenAI support for chat and embeddings
- Blog, social post, and learning assistant generation APIs

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy async
- Supabase PostgreSQL
- Supabase Storage
- Ollama
- OpenAI SDK
- scikit-learn
- pypdf
- python-docx

## Project Structure

```text
Backend/
├── app/
│   ├── ai/
│   ├── api/
│   │   └── routes/
│   ├── auth/
│   ├── core/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── database/
│   ├── schema.sql
│   ├── file_chunks.sql
│   └── file_chunk_embeddings.sql
├── .env.example
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11 or newer
- Supabase project
- Supabase Storage bucket
- Ollama installed locally, if using local AI
- Git

## Installation

### 1. Clone Repository

```powershell
git clone https://github.com/finalyearpjt2025-bit/Chat-Board-Backend
cd Backend
```

### 2. Create Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Create Environment File

Copy the example file:

```powershell
copy .env.example .env
```

Open `.env` and fill in your real values.

## Environment Variables
### first create the .env file in the app folder

Example:

```env
DEVNEXUS_APP_NAME="DevNexus AI Chat Board API"
DEVNEXUS_APP_VERSION="0.1.0"
DEVNEXUS_API_PREFIX="/api/v1"
DEVNEXUS_ENVIRONMENT="development"
DEVNEXUS_DEBUG=true

DEVNEXUS_SUPABASE_URL="https://your-project-ref.supabase.co"
DEVNEXUS_SUPABASE_ANON_KEY="your-supabase-anon-or-publishable-key"
DEVNEXUS_SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-role-or-secret-key"
DEVNEXUS_DATABASE_URL="postgresql+asyncpg://postgres.your-project-ref:your-password@your-pooler-host.supabase.com:6543/postgres?pgbouncer=true"

DEVNEXUS_JWT_SECRET_KEY="replace-this-with-a-long-random-secret-minimum-32-characters"
DEVNEXUS_JWT_ALGORITHM="HS256"
DEVNEXUS_ACCESS_TOKEN_EXPIRE_MINUTES=60

DEVNEXUS_OPENAI_API_KEY="your-openai-api-key"
DEVNEXUS_OPENAI_MODEL="gpt-4o-mini"
DEVNEXUS_EMBEDDING_PROVIDER="ollama"
DEVNEXUS_OPENAI_EMBEDDING_MODEL="text-embedding-3-small"

DEVNEXUS_OLLAMA_HOST="http://localhost:11434"
DEVNEXUS_OLLAMA_API_KEY=""
DEVNEXUS_OLLAMA_MODEL="tinyllama:latest"
DEVNEXUS_OLLAMA_EMBEDDING_MODEL="nomic-embed-text"

DEVNEXUS_SUPABASE_STORAGE_BUCKET="devnexus-files"
DEVNEXUS_MAX_UPLOAD_SIZE_MB=20
```

Do not commit your real `.env` file to GitHub.

## Supabase Setup

### 1. Create Project

1. Go to Supabase.
2. Create a new project.
3. Save your database password.
4. Wait for the project to finish provisioning.

### 2. Get Project Values

In Supabase dashboard:

- Get project URL from project settings.
- Get anon/publishable key.
- Get service role/secret key.
- Open **Connect** and copy the **Session pooler** database URL.

For SQLAlchemy async, the database URL must start with:

```text
postgresql+asyncpg://
```

### 3. Run Database Schema

Open Supabase SQL Editor and run:

```sql
-- database/schema.sql
```

The full SQL is available in `database/schema.sql`.

It creates:

- `users`
- `conversations`
- `messages`
- `files`
- `usage_logs`
- `file_chunks`
- `file_chunk_embeddings`

### 4. Create Storage Bucket

In Supabase dashboard:

1. Go to **Storage**.
2. Create a bucket named:

```text
devnexus-files
```

3. Keep it private.

## Ollama Setup

Install Ollama from:

```text
https://ollama.com/download
```

Check installation:

```powershell
ollama --version
```

Start Ollama:

```powershell
ollama serve
```

In another terminal, pull the chat model:

```powershell
ollama pull tinyllama:latest
```

Pull the embedding model:

```powershell
ollama pull nomic-embed-text
```

Check installed models:

```powershell
ollama list
```

Test Ollama server:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

## Run Backend

From the backend root folder:

```powershell
python -m uvicorn app.main:app --reload
```

Open Swagger docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/api/v1/health
```

## API Overview

### Auth

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### Conversations

```text
GET    /api/v1/conversations
POST   /api/v1/conversations
GET    /api/v1/conversations/{conversation_id}
PATCH  /api/v1/conversations/{conversation_id}
DELETE /api/v1/conversations/{conversation_id}
```

### Messages

```text
GET  /api/v1/messages/{conversation_id}
POST /api/v1/messages
```

### AI

```text
POST /api/v1/ai/chat
POST /api/v1/ai/generate-blog
POST /api/v1/ai/generate-post
POST /api/v1/ai/learn
```

### Files

```text
POST   /api/v1/files/upload
GET    /api/v1/files
DELETE /api/v1/files/{file_id}
```

### Documents

```text
POST /api/v1/documents/{file_id}/process
GET  /api/v1/documents/{file_id}/chunks
```

### RAG

```text
POST /api/v1/rag/files/{file_id}/embeddings
POST /api/v1/rag/chat
```

## Testing Flow

### 1. Register

```json
{
  "name": "user",
  "email": "user@example.com",
  "password": "password123"
}
```

### 2. Login

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Copy the returned `access_token`.

### 3. Authorize Swagger

Click **Authorize** in Swagger and enter:

```text
Bearer your_access_token_here
```

### 4. Create Conversation

```json
{
  "title": "My First Chat",
  "model": "tinyllama:latest"
}
```

### 5. Chat With AI

```json
{
  "conversation_id": "paste-conversation-id-here",
  "provider": "ollama",
  "model": "tinyllama:latest",
  "message": "Explain FastAPI in simple words."
}
```

### 6. Upload File

Use Swagger `POST /api/v1/files/upload` and select a supported file:

- PDF
- DOCX
- TXT
- CSV
- PNG
- JPG
- JPEG

### 7. Process Document

```text
POST /api/v1/documents/{file_id}/process
```

### 8. Build Embeddings

```text
POST /api/v1/rag/files/{file_id}/embeddings
```

This creates semantic vectors for document chunks using Ollama model `nomic-embed-text`.

### 9. Ask Document Question

```json
{
  "file_id": "paste-file-id-here",
  "question": "What is this document about?",
  "provider": "ollama",
  "model": "tinyllama:latest",
  "top_k": 5
}
```

`top_k` means how many relevant document chunks are sent to the AI model as context.

## Content Generation Examples

### Blog

```json
{
  "topic": "AI tools for developers",
  "audience": "developers",
  "tone": "clear and practical",
  "word_count": 700,
  "provider": "ollama",
  "model": "tinyllama:latest"
}
```

### Social Post

```json
{
  "topic": "AI tools for developers",
  "platform": "linkedin",
  "tone": "professional",
  "provider": "ollama",
  "model": "tinyllama:latest"
}
```

### Learning Plan

```json
{
  "topic": "FastAPI",
  "level": "beginner",
  "duration": "2 weeks",
  "provider": "ollama",
  "model": "tinyllama:latest"
}
```

## Common Issues

### `ModuleNotFoundError: No module named 'app'`

Run Uvicorn from the backend root folder:

```powershell
cd enter-the-path-of-your-cloned-repo
python -m uvicorn app.main:app --reload
```

Do not run it from inside the `app` folder.

### Supabase Database Connection Error

Use the Supabase **Session pooler** connection string and make sure it starts with:

```text
postgresql+asyncpg://
```

### Ollama Connection Error

Make sure Ollama is running:

```powershell
ollama serve
```

Check:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

### Embeddings Error

Make sure the embedding model is installed:

```powershell
ollama pull nomic-embed-text
```

### Weak RAG Answers

Try:

- Better answer model than `tinyllama:latest`
- Lower `top_k` for small models, such as `2` or `3`
- Cleaner source documents
- Re-process document and rebuild embeddings

## Development Checks

Compile Python files:

```powershell
python -m compileall app
```

Run server:

```powershell
python -m uvicorn app.main:app --reload
```

## Notes

- `.env` contains secrets and should not be committed.
- `.env.example` should contain placeholders only.
- Local Ollama does not require an API key.
- OpenAI is optional unless you choose `provider: "openai"` or `DEVNEXUS_EMBEDDING_PROVIDER="openai"`.

