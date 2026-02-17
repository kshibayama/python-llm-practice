# python-llm-practice (Ticket Demo)

FastAPI + SQLite + SQLAlchemy + Alembic を使った「問い合わせ（ticket）」の永続化デモです。  
Day3 以降で LLM 連携（要約・分類・返信案生成）に差し替える前提で、まずは **API / DB / マイグレーション / 冪等性の土台**を作っています。

## Features

- `POST /tickets` で問い合わせを登録（SQLite 永続化）
- `GET /tickets/{id}` で問い合わせを取得
- `POST /tickets/{id}/process` で結果（summary/category/reply_draft）を生成して保存（現時点は **ダミー生成**）
  - 既に result がある場合は冪等に既存を返す
  - `force=true` で再生成（上書き）
- `GET /tickets/{id}/result` で結果を取得
- Alembic によるマイグレーション管理

## Tech Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy 2.x
- Alembic

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
│  └─ schemas/
│     ├─ ticket.py
│     └─ result.py
├─ alembic/
├─ alembic.ini
├─ requirements.txt
├─ requirements-dev.txt
└─ data/
   └─ app.db  (runtime)
```

## Setup
### 1) Create venv & install deps
```
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip

python -m pip install -r requirements.txt -r requirements-dev.txt
```

### 2) Environment variables
SQLite の DB ファイルを ./data/app.db に作ります。

```
mkdir -p data
export DATABASE_URL="sqlite+pysqlite:///./data/app.db"
```

.env を使う場合（任意）:
```
DATABASE_URL=sqlite+pysqlite:///./data/app.db
```

### 3) Run migrations
alembic upgrade head
4) Start API server
SQLite は並列ワーカーと相性が微妙なので、基本は workers=1 推奨です。
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --workers 1
```

## API
### Health check
```
curl -s localhost:8000/health
# -> {"ok":true}
```

### Create ticket
```
curl -s -X POST localhost:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{"raw_text":"I cannot login to my account. Please help.","source":"email"}'
```


Response example:
```
{
  "id": 1,
  "created_at": "2026-02-17T16:35:05",
  "source": "email",
  "raw_text": "I cannot login to my account. Please help.",
  "status": "new"
}
```

### Get ticket
```
curl -s localhost:8000/tickets/1
```

### Process ticket (dummy result)
```
curl -s -X POST localhost:8000/tickets/1/process
```
既に result がある場合、同じ結果を返します（冪等）。

強制再生成したい場合：

```
curl -s -X POST "localhost:8000/tickets/1/process?force=true"
```

### Get result
```
curl -s localhost:8000/tickets/1/result
```

## Data Model
### tickets

```
id, created_at, source, raw_text, status
```

### results

```
id, ticket_id (UNIQUE), summary, category, reply_draft, model, prompt_version, created_at
```

現時点では results は 1 ticket = 1 result の想定（ticket_id に UNIQUE 制約）。

## Development
### Create new migration (when models change)
```
alembic revision --autogenerate -m "your_message"
alembic upgrade head
```

### Reset DB (local)
```
rm -f data/app.db
alembic upgrade head
```

## Notes
created_at は SQLite の CURRENT_TIMESTAMP 相当になるため、UTC扱いになって見える場合があります。

運用では DB は UTC 保存 + 表示側でタイムゾーン変換、が一般的です。

Day3 以降で POST /tickets/{id}/process のダミー生成部分を LLM 呼び出しに差し替える予定です。

## Troubleshooting
Can't proceed with --autogenerate ... does not provide a MetaData object
Alembic が target_metadata を参照できていません。alembic/env.py に Base.metadata を設定し、models を import しているか確認してください。

Can't load plugin: sqlalchemy.dialects:driver
alembic.ini の sqlalchemy.url がテンプレの driver://... のままです。SQLite の URL に変更してください。


