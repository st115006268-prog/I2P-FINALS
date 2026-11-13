"""Backend client and state package for Arcadia pages."""
from .state import (
    DEFAULT_TITLE,
    CURRENT_USER_ID,
    CURRENT_DECK_ID,
    CURRENT_STUDY_MODE,
    CURRENT_CHAT_ID,
    USER,
    NAV_ITEMS,
    SUGGESTIONS,
    Chat,
    ChatStore,
)
from .client import (
    FASTAPI_BASE_URL,
    _is_fastapi_server_running,
    _sync_user_dict,
    api_login,
    api_register,
    api_get_user_profile,
    api_update_user_profile,
    api_get_user_stats,
    api_log_timer,
    api_get_decks,
    api_create_deck,
    api_get_deck_cards,
    api_add_flashcard,
    api_update_deck,
    api_delete_deck,
    api_update_flashcard,
    api_delete_flashcard,
    api_get_tasks,
    api_create_task,
    api_update_task,
    api_delete_task,
    api_get_chats,
    api_create_chat,
    api_delete_chat,
)

# Load initial user info on import
try:
    api_get_user_profile(1)
except Exception:
    pass
