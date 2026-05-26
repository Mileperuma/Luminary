# Models

SQLModel ORM classes — one file per entity for readability.

Tables to implement (see `docs/02_Technical_Design_Document.docx` Section 4 for the ER diagram and Section 4.1 for table notes):

- `user.py` — `users`
- `preference.py` — `preferences`
- `preference_embedding.py` — `preference_embeddings` (uses pgvector `Vector` column)
- `chat_session.py` — `chat_sessions`
- `chat_message.py` — `chat_messages`
- `recommendation.py` — `recommendations`
- `feedback.py` — `feedback`

## Migrations

Migrations are managed by Alembic. Once the first model lands:

```bash
alembic init alembic
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

The pgvector extension is enabled automatically by the SQL in `backend/db/init/01_enable_pgvector.sql`, which the Postgres container runs on first boot.
