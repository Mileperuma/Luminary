-- Run automatically by the Postgres container on first boot
-- (via /docker-entrypoint-initdb.d). Enables the pgvector extension
-- so embedding columns can use the `vector` type.

CREATE EXTENSION IF NOT EXISTS vector;
