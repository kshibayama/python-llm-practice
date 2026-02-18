# python-llm-practice (Ticket Demo)

A simple demo app for persisting support inquiries (“tickets”) using **FastAPI + SQLite + SQLAlchemy + Alembic**.  
It also generates and stores **summary / category / reply draft** for each ticket using an **LLM via the OpenAI API**.

This project focuses on having a solid, “production-ish” foundation:
- API + DB persistence
- Migration management
- Idempotent processing
- Prompt versioning
- Saving LLM execution metadata (request_id / latency / token usage)

## Features

- `POST /tickets`: create a ticket (persisted in SQLite)
- `GET /tickets/{id}`: fetch a ticket
- `POST /tickets/{id}/process`: run LLM processing and save results (`summary/category/reply_draft`)
  - Idempotent: if a result already exists, returns it
  - `force=true` re-runs and overwrites the result
- `GET /tickets/{id}/result`: fetch the saved result
- Alembic migrations
- Stores LLM execution metadata (`openai_request_id`, `latency_ms`, token usage)

## Tech Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy 2.x
- Alembic
- OpenAI Python SDK

## Project Structure (example)

```text
.
├─ app/
│  ├─ main.py
│  ├─ core/
│  │  └─ config.py
│  ├─ db/
│  │  ├─ base.py
│  │  ├─ models.py
│  │  └─ session.py
│  ├─ routers/
│  │  └─ tickets.py
│  ├─ schemas/
│  │  ├─ ticket.py
│  │  └─ result.py
│  └─ llm/
│     ├─ client.py
│     ├─ prompts.py
│     ├─ schemas.py
│     └─ ticket_processor.py
├─ prompts/
│  └─ v1/
│     └─ ticket_process_system.txt
├─ alembic/
├─ alembic.ini
├─ requirements.txt
├─ requirements-dev.txt
└─ data/
   └─ app.db  (runtime)
````

## Setup

### 1) Create venv & install deps

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip

python -m pip install -r requirements.txt -r requirements-dev.txt
```

### 2) Environment variables

Create the SQLite DB file at `./data/app.db`:

```bash
mkdir -p data
export DATABASE_URL="sqlite+pysqlite:///./data/app.db"
```

Set OpenAI-related env vars:

```bash
export OPENAI_API_KEY="YOUR_KEY"
export OPENAI_MODEL="gpt-4o-mini-2024-07-18"   # example (adjust to what you can access)
export PROMPT_VERSION="v1"
```

Optional `.env`:

```env
DATABASE_URL=sqlite+pysqlite:///./data/app.db
OPENAI_API_KEY=YOUR_KEY
OPENAI_MODEL=gpt-4o-mini-2024-07-18
PROMPT_VERSION=v1
```

### 3) Run migrations

```bash
alembic upgrade head
```

### 4) Start API server

SQLite doesn’t pair well with multi-worker concurrency in many setups, so `workers=1` is recommended.

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --workers 1
```

## API

### Health check

```bash
curl -s localhost:8000/health
# -> {"ok":true}
```

### Create ticket

```bash
curl -s -X POST localhost:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{"raw_text":"I cannot login to my account. Please help.","source":"email"}'
```

Response example:

```json
{
  "id": 1,
  "created_at": "2026-02-17T16:35:05",
  "source": "email",
  "raw_text": "I cannot login to my account. Please help.",
  "status": "new"
}
```

### Get ticket

```bash
curl -s localhost:8000/tickets/1
```

### Process ticket (LLM)

```bash
curl -s -X POST localhost:8000/tickets/1/process
```

* If a result already exists, it returns the existing result (idempotent).
* To force re-processing:

```bash
curl -s -X POST "localhost:8000/tickets/1/process?force=true"
```

### Get result

```bash
curl -s localhost:8000/tickets/1/result
```

## Data Model

### tickets

```text
id, created_at, source, raw_text, status
```

### results

```text
id, ticket_id (UNIQUE), summary, category, reply_draft, model, prompt_version, created_at,
openai_request_id, latency_ms, input_tokens, output_tokens, total_tokens, cached_tokens
```

Currently assumes **1 ticket = 1 result** (`ticket_id` has a UNIQUE constraint).

## Development

### Create new migration (when models change)

```bash
alembic revision --autogenerate -m "your_message"
alembic upgrade head
```

### Reset DB (local)

```bash
rm -f data/app.db
alembic upgrade head
```

## Notes

* `created_at` is similar to SQLite `CURRENT_TIMESTAMP` and may appear as UTC.
  In production, it’s common to store timestamps in UTC and convert for display.
* `POST /tickets/{id}/process` calls the OpenAI API; you need a valid `OPENAI_API_KEY` and an accessible `OPENAI_MODEL`.
* If you hit billing/usage limits, requests may fail with `insufficient_quota` errors.

## Troubleshooting

### Can't proceed with --autogenerate ... does not provide a MetaData object

Alembic cannot see `target_metadata`. Ensure `alembic/env.py` sets `target_metadata = Base.metadata` and imports your models.

### Can't load plugin: sqlalchemy.dialects:driver

Your `alembic.ini` still has the template URL `driver://...`. Change it to a SQLite URL like `sqlite+pysqlite:///./data/app.db`.

### ModuleNotFoundError: No module named 'openai'

Install the OpenAI SDK in your venv:

```bash
python -m pip install -U openai
```

Also verify `uvicorn` is running from your venv:

```bash
which python
which uvicorn
# If uvicorn is not under .venv:
python -m uvicorn app.main:app --reload --workers 1
```

```
::contentReference[oaicite:0]{index=0}
```

