"""Active session state and in-memory chat models for Arcadia."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

DEFAULT_TITLE = "New study chat"

# Active session state synced with the database
CURRENT_USER_ID: int = 1
CURRENT_DECK_ID: int = 1
CURRENT_STUDY_MODE: str = "flashcards"  # "flashcards" or "quiz"
CURRENT_CHAT_ID: Optional[int] = None

USER: Dict[str, str] = {"name": "John Doe", "initials": "JD", "email": "john.doe@example.com"}

NAV_ITEMS = [
    {"key": "assistant", "label": "AI Assistant", "icon": "sparkles"},
    {"key": "flashcards", "label": "Flashcards", "icon": "layers"},
    {"key": "planner", "label": "Study planner", "icon": "calendar", "badge": "To-do · Calendar"},
    {"key": "timer", "label": "Study timer", "icon": "timer"},
    {"key": "profile", "label": "Profile", "icon": "logo"},
]

SUGGESTIONS = ["Summarize my notes", "Make a study plan", "Create practice questions"]


@dataclass
class Chat:
    title: str = DEFAULT_TITLE
    id: int = 1
    messages: list[dict] = field(default_factory=list)


class ChatStore:
    """Keeps the list of chats synced with FastAPI and SQLite."""

    def __init__(self) -> None:
        self.chats: list[Chat] = []
        self.reload()

    def reload(self) -> None:
        from .client import _is_fastapi_server_running, FASTAPI_BASE_URL, _server_state
        import httpx
        import backend_fastapi as api

        global CURRENT_CHAT_ID
        raw_chats = None
        if _is_fastapi_server_running():
            try:
                with httpx.Client(timeout=0.5) as client:
                    resp = client.get(f"{FASTAPI_BASE_URL}/api/chats", params={"user_id": CURRENT_USER_ID})
                    if resp.status_code == 200:
                        raw_chats = resp.json()
            except Exception:
                _server_state["online"] = False
        if raw_chats is None:
            raw_chats = api.list_chats(CURRENT_USER_ID)

        self.chats = [
            Chat(
                title=c.get("title", DEFAULT_TITLE),
                id=c["chat_id"],
                messages=[
                    {"role": m.get("role", "user"), "text": m.get("text", m.get("content", ""))}
                    for m in c.get("messages", [])
                ],
            )
            for c in raw_chats
        ]
        if not self.chats:
            self.new_chat()
        if CURRENT_CHAT_ID is None or not any(c.id == CURRENT_CHAT_ID for c in self.chats):
            CURRENT_CHAT_ID = self.chats[0].id

    def get(self, chat_id: int) -> Chat:
        for c in self.chats:
            if c.id == chat_id:
                return c
        return self.chats[0]

    def new_chat(self) -> Chat:
        from .client import _is_fastapi_server_running, FASTAPI_BASE_URL, _server_state
        import httpx
        import backend_fastapi as api

        global CURRENT_CHAT_ID
        created = None
        if _is_fastapi_server_running():
            try:
                with httpx.Client(timeout=0.5) as client:
                    resp = client.post(f"{FASTAPI_BASE_URL}/api/chats", json={"user_id": CURRENT_USER_ID})
                    if resp.status_code in (200, 201):
                        created = resp.json()
            except Exception:
                _server_state["online"] = False
        if created is None:
            created = api.create_chat(api.ChatCreate(user_id=CURRENT_USER_ID))

        chat = Chat(title=created.get("title", DEFAULT_TITLE), id=created["chat_id"], messages=[])
        self.chats.insert(0, chat)
        CURRENT_CHAT_ID = chat.id
        return chat

    def delete(self, chat_id: int) -> Chat:
        from .client import _is_fastapi_server_running, FASTAPI_BASE_URL, _server_state
        import httpx
        import backend_fastapi as api

        global CURRENT_CHAT_ID
        if _is_fastapi_server_running():
            try:
                with httpx.Client(timeout=0.5) as client:
                    client.delete(f"{FASTAPI_BASE_URL}/api/chats/{chat_id}")
            except Exception:
                _server_state["online"] = False
        try:
            api.delete_chat(chat_id)
        except Exception:
            pass

        self.chats = [c for c in self.chats if c.id != chat_id]
        if not self.chats:
            self.new_chat()
        if CURRENT_CHAT_ID == chat_id or not any(c.id == CURRENT_CHAT_ID for c in self.chats):
            CURRENT_CHAT_ID = self.chats[0].id
        return self.chats[0]

    def send(self, chat_id: int, text: str) -> str:
        from .client import _is_fastapi_server_running, FASTAPI_BASE_URL, _server_state
        import httpx
        import backend_fastapi as api

        chat = self.get(chat_id)
        if not chat.messages and chat.title == DEFAULT_TITLE:
            chat.title = text

        reply = None
        if _is_fastapi_server_running():
            try:
                with httpx.Client(timeout=1.0) as client:
                    resp = client.post(
                        f"{FASTAPI_BASE_URL}/api/assistant/ask",
                        json={"user_id": CURRENT_USER_ID, "chat_id": chat.id, "question": text},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        reply = data.get("answer", "")
                        chat.id = data.get("chat_id", chat.id)
            except Exception:
                _server_state["online"] = False

        if reply is None:
            data = api.ask_assistant(
                api.AskQuestionRequest(user_id=CURRENT_USER_ID, chat_id=chat.id, question=text)
            )
            reply = data["answer"]
            chat.id = data["chat_id"]

        chat.messages.append({"role": "user", "text": text})
        chat.messages.append({"role": "assistant", "text": reply})
        return reply
