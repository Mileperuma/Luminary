"""Re-export every model so Alembic's autogenerate sees them all.

If you add a new model, import it here too.
"""

from app.models.chat import ChatMessage, ChatRole, ChatSession, ChatSessionType
from app.models.preference import MediaType, Preference, PreferenceSource
from app.models.preference_embedding import EMBEDDING_DIM, PreferenceEmbedding
from app.models.recommendation import Feedback, FeedbackKind, Recommendation
from app.models.user import User

__all__ = [
    "ChatMessage",
    "ChatRole",
    "ChatSession",
    "ChatSessionType",
    "EMBEDDING_DIM",
    "Feedback",
    "FeedbackKind",
    "MediaType",
    "Preference",
    "PreferenceEmbedding",
    "PreferenceSource",
    "Recommendation",
    "User",
]
