# FastAPI Chat Assignment

An async chat API built with FastAPI. Users sign up, open conversations, and post messages. Studio staff (admins and sub-admins) can see every user's conversations and reply to them.

**Stack:** FastAPI · SQLAlchemy 2.0 (async) · MySQL · Alembic · Pydantic v2 · JWT auth

## Prerequisites

- Python **3.11**. The project is pinned to `>=3.11,<3.12`.
- MySQL **8.x**, running locally or reachable over the network.

## Setup

### 1. Create a virtual environment and install dependencies

```bash
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"            # app + dev tools (pytest, httpx, ruff)
# or, app only:
pip install -r requirements.txt
```

### 2. Create the database

```sql
CREATE DATABASE fastapi_chat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set at least these values:

| Variable | Description |
|---|---|
| `DATABASE_URL` | `mysql+asyncmy://USER:PASSWORD@HOST:3306/fastapi_chat`. URL-encode special characters in the password, for example `@` becomes `%40`. |
| `JWT_SECRET_KEY` | At least 32 characters. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(48))"`. |
| `ADMIN_PASSWORD`, `SUB_ADMIN_PASSWORD` | Passwords for the staff accounts the seeder creates. Each must be at least 8 characters. |

Optional settings:

| Variable | Default |
|---|---|
| `APP_ENV` | `development` (also accepts `staging` or `production`) |
| `DEBUG` | `false` |
| `LOG_LEVEL` | `INFO` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `DATABASE_ECHO` | `false`; set it to `true` to log SQL |
| `DATABASE_POOL_SIZE` | `5` |
| `DATABASE_MAX_OVERFLOW` | `10` |

### 4. Run the database migrations

```bash
alembic upgrade head
```

### 5. Seed the staff accounts

```bash
python -m app.database.seeder
```

This creates the admin and sub-admin accounts from `.env`. You can run it more than once: accounts that already exist are skipped, and only their role is corrected if it was changed.

### 6. Start the server

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## API overview

Send the token on authenticated requests as `Authorization: Bearer <access_token>`. You get a token from `POST /auth/login`.

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/auth/signup` | Public | Register a user |
| `POST` | `/auth/login` | Public | Log in and receive an access token |
| `GET` | `/users/me` | User | Current user's profile |
| `POST` | `/conversations` | User | Start a conversation, with an optional first message |
| `GET` | `/conversations` | User | List your conversations (`limit`, `offset`) |
| `GET` | `/conversations/{id}` | User | One conversation with its messages |
| `POST` | `/conversations/{id}/messages` | User | Add a message |
| `GET` | `/studio/conversations` | Admin / Sub-admin | List all conversations (`limit`, `offset`, `user_id`) |
| `GET` | `/studio/conversations/{id}` | Admin / Sub-admin | One conversation with its owner and messages |
| `POST` | `/studio/conversations/{id}/reply` | Admin / Sub-admin | Reply as studio staff |
| `GET` | `/health` | Public | App and database status |

Users only ever see their own conversations. Requesting someone else's conversation returns `404`, so the response doesn't reveal whether it exists.

## Postman

Import [postman/fastapi_chat.postman_collection.json](postman/fastapi_chat.postman_collection.json).

1. In the collection's **Variables** tab, set `base_url` (default `http://localhost:8000`), `email` and `password`.
2. Run **Auth → Signup** (first time only), then **Auth → Login**. Login saves the token, and every request uses it automatically.
3. For the Studio folder, set `admin_password` and run **Studio → Studio Login** once.

Creating a conversation stores its id in `conversation_id`, so the follow-up requests work without editing URLs.

## Project structure

```
app/
├── main.py              # App factory: routers, exception handlers, lifespan
├── config/              # Settings loaded from .env (pydantic-settings)
├── core/                # Domain exceptions and their HTTP handlers, JWT/password security, shared params
├── database/            # Async engine and session, declarative base, base repository, seeder
├── user/                # User model, repository, /users routes
├── authentication/      # Signup/login service, current-user and role dependencies
├── conversation/        # Conversation and Message models, user-facing chat routes
├── studio/              # Staff routes for viewing and replying to any conversation
└── migrations/          # Alembic migrations
```

Each feature module follows the same layout:

- `router.py`: HTTP endpoints only.
- `dependencies.py`: FastAPI dependencies, such as service providers and auth guards.
- `service.py`: business logic. Services raise domain exceptions from `app/core/exceptions.py`, not `HTTPException`.
- `repository.py`: database queries.
- `model.py`: SQLAlchemy models.
- `dto/`: Pydantic request and response schemas.

## Database migrations

After changing a model, generate a migration with a descriptive message and apply it:

```bash
alembic revision --autogenerate -m "add last_seen_at to users"
alembic upgrade head
```

New model modules must be imported in `app/migrations/env.py`. Otherwise autogenerate won't detect them.

## Linting

```bash
ruff check app
ruff check app --fix
```
