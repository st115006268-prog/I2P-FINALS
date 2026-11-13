"""Arcadia backend: chat data and assistant replies (no UI code here)."""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field

_ids = itertools.count(1)

DEFAULT_TITLE = "New study chat"

USER = {"name": "John Doe", "initials": "JD"}

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
    id: int = field(default_factory=lambda: next(_ids))
    messages: list[dict] = field(default_factory=list)


class ChatStore:
    """Keeps the list of chats, newest first."""

    def __init__(self) -> None:
        self.chats: list[Chat] = [
            Chat(),
            Chat("What is E=mc²?"),
            Chat("Help with my I2P questions"),
        ]

    def get(self, chat_id: int) -> Chat:
        return next(c for c in self.chats if c.id == chat_id)

    def new_chat(self) -> Chat:
        chat = Chat()
        self.chats.insert(0, chat)
        return chat

    def delete(self, chat_id: int) -> Chat:
        """Delete a chat and return the chat to show next."""
        self.chats = [c for c in self.chats if c.id != chat_id]
        if not self.chats:
            self.chats.append(Chat())
        return self.chats[0]

    def send(self, chat_id: int, text: str) -> str:
        chat = self.get(chat_id)
        if not chat.messages and chat.title == DEFAULT_TITLE:
            chat.title = text
        chat.messages.append({"role": "user", "text": text})
        reply = assistant_reply(text)
        chat.messages.append({"role": "assistant", "text": reply})
        return reply


def assistant_reply(text: str) -> str:
    """Placeholder answer. Swap this for a real model call."""
    return (
        "Thanks! I'm a demo assistant right now. You asked: "
        f"“{text}”. Connect a model in assistant_reply() to get real answers."
    )