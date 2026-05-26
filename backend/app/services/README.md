# Services

Business logic lives here, one module per concern, so that:

1. Tests can exercise it without spinning up FastAPI.
2. Routes in `app/api/*` stay thin (parse request → call service → format response).
3. External providers are wrapped in adapters that can be mocked.

## Planned modules (added per sprint — see `docs/03_Project_Plan.docx`)

| Module                | Sprint  | Purpose                                                    |
|-----------------------|---------|------------------------------------------------------------|
| `auth.py`             | 1       | Password hashing, JWT issue / verify.                      |
| `llm_client.py`       | 2       | Single adapter wrapping Claude (primary) + OpenAI (fallback). |
| `books_client.py`     | 2       | Google Books API adapter.                                  |
| `movies_client.py`    | 2       | TMDb / OMDb adapter.                                       |
| `articles_client.py`  | 2       | Guardian / News API adapter.                               |
| `youtube_client.py`   | 2       | YouTube Data API adapter (trailers).                       |
| `recommender.py`      | 2       | Builds a primary pick + similar items per media type.      |
| `chatbot.py`          | 3       | Multi-turn onboarding + general chat orchestration.        |
| `memory.py`           | 3 / 4   | Preference store, embedding rebuild, returning-user greeting. |

Each module must:

- Be unit-testable without network access (use fakes or recorded fixtures).
- Raise typed exceptions defined in `app/core/exceptions.py` (to be added).
- Log a single line per external call with provider name, duration, and outcome.
