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

    def send(self, chat_id: int, text: str, attachment: Optional[dict] = None) -> str:
        from .client import _is_fastapi_server_running, FASTAPI_BASE_URL, _server_state
        import httpx
        import backend_fastapi as api

        chat = self.get(chat_id)
        if not chat.messages and chat.title == DEFAULT_TITLE:
            clean_title = (
                text.replace("📎 **Attached File:**", "")
                .replace("📹 **Attached Video:**", "")
                .replace("[Attached File:", "")
                .strip()
            )
            chat.title = clean_title[:32] + ("..." if len(clean_title) > 32 else "")

        att_payload = None
        if attachment and attachment.get("path"):
            try:
                import base64, mimetypes, os
                fpath = attachment["path"]
                fname = attachment.get("name") or os.path.basename(fpath)
                ext = os.path.splitext(fname)[1].lower()

                VIDEO_EXTS = {
                    ".mp4": "video/mp4", ".mov": "video/quicktime", ".avi": "video/x-msvideo",
                    ".webm": "video/webm", ".mkv": "video/x-matroska", ".flv": "video/x-flv",
                    ".wmv": "video/x-ms-wmv", ".3gp": "video/3gpp", ".m4v": "video/x-m4v",
                    ".mpeg": "video/mpeg", ".mpg": "video/mpeg",
                }
                if ext in VIDEO_EXTS:
                    mime = VIDEO_EXTS[ext]
                else:
                    mime, _ = mimetypes.guess_type(fname)
                    if not mime:
                        mime = "application/octet-stream"

                fsize = os.path.getsize(fpath) if os.path.exists(fpath) else 0
                att_payload = {
                    "filename": fname,
                    "mime_type": mime,
                    "file_path": fpath,
                }
                # For files up to 25MB, include base64
                if 0 < fsize <= 25 * 1024 * 1024:
                    with open(fpath, "rb") as f:
                        raw_bytes = f.read()
                    att_payload["file_data_base64"] = base64.b64encode(raw_bytes).decode("utf-8")
            except Exception as err:
                print("Error reading attachment:", err)

        reply = None
        if _is_fastapi_server_running():
            try:
                with httpx.Client(timeout=180.0) as client:
                    resp = client.post(
                        f"{FASTAPI_BASE_URL}/api/assistant/ask",
                        json={
                            "user_id": CURRENT_USER_ID,
                            "chat_id": chat.id,
                            "question": text,
                            "attachment": att_payload,
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        reply = data.get("answer", "")
                        chat.id = data.get("chat_id", chat.id)
            except Exception:
                _server_state["online"] = False

        if reply is None:
            att_obj = api.FileAttachment(**att_payload) if att_payload else None
            data = api.ask_assistant(
                api.AskQuestionRequest(
                    user_id=CURRENT_USER_ID,
                    chat_id=chat.id,
                    question=text,
                    attachment=att_obj,
                )
            )
            reply = data["answer"]
            chat.id = data["chat_id"]

        from .math_formatter import format_scientific_text
        reply = format_scientific_text(reply)
        chat.messages.append({"role": "user", "text": text})
        chat.messages.append({"role": "assistant", "text": reply})
        return reply

    def save_api_key(self, key: str) -> bool:
        import backend_fastapi as api
        return api.save_gemini_api_key(key)
