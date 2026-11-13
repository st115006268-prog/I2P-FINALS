"""Unified Sidebar component for all Arcadia pages.

Provides an identical 312px sidebar layout, typography, colors, hover states,
live recent chats (synced with SQLite via pages.backend), and active user card
across AI Assistant, Flashcards, Study View, Study Planner, Study Timer, and Profile.
"""
from __future__ import annotations

from typing import Callable, Optional
import flet as ft
from pages import backend

from styles import (
    TEAL,
    TEAL_HOVER,
    TEAL_SOFT,
    INK,
    TEXT,
    MUTED,
    LINE,
    WHITE,
    NAVY,
    arcadia_logo,
    LOGO_SVG,
)
SIDEBAR_W = 312

ROUTE_MAP = {
    "assistant": "/ai-assistant",
    "ai": "/ai-assistant",
    "flashcards": "/flashcards",
    "studyview": "/studyview",
    "planner": "/studyplanner",
    "timer": "/studytimer",
    "profile": "/profile",
}

_SIDEBAR_LISTENERS: list[Callable[[], None]] = []


def register_sidebar_listener(listener: Callable[[], None]):
    if listener not in _SIDEBAR_LISTENERS:
        _SIDEBAR_LISTENERS.append(listener)


def unregister_sidebar_listener(listener: Callable[[], None]):
    if listener in _SIDEBAR_LISTENERS:
        _SIDEBAR_LISTENERS.remove(listener)


def refresh_all_sidebars():
    """Notify all active sidebars across any page to update user initials, name, and recent chats."""
    dead = []
    for cb in list(_SIDEBAR_LISTENERS):
        try:
            cb()
        except Exception:
            dead.append(cb)
    for d in dead:
        if d in _SIDEBAR_LISTENERS:
            _SIDEBAR_LISTENERS.remove(d)


def hover_bg(normal: Optional[str], hover: str):
    """Consistent hover handler that properly resets when the cursor leaves."""
    def handler(e):
        is_hovered = e.data in (True, "true")
        e.control.bgcolor = hover if is_hovered else normal
        e.control.update()
    return handler


def build_unified_sidebar(
    page: Optional[ft.Page],
    active_tab: str,
    switch_tab: Optional[Callable[[str], None]] = None,
    chat_list_control: Optional[ft.Control] = None,
    on_new_chat: Optional[Callable] = None,
) -> ft.Container:
    """Builds the unified 312px full-height sidebar container for any page."""
    norm_active = "assistant" if active_tab in ("assistant", "ai") else (
        "flashcards" if active_tab in ("flashcards", "studyview") else active_tab
    )

    def navigate(tab_key: str):
        if switch_tab is not None:
            switch_tab(tab_key)
        elif page is not None:
            target = ROUTE_MAP.get(tab_key, "/ai-assistant")
            if page.route != target:
                page.go(target)

    def open_chat_from_sidebar(cid: int):
        backend.CURRENT_CHAT_ID = cid
        navigate("assistant")

    def handle_new_chat(e=None):
        if on_new_chat is not None:
            on_new_chat(e)
            return
        try:
            store = backend.ChatStore()
            chat = store.new_chat()
            backend.CURRENT_CHAT_ID = chat.id
        except Exception:
            pass
        navigate("assistant")

    def nav_item(key: str, label: str, icon=None, badge: Optional[str] = None) -> ft.Container:
        is_active = norm_active == key
        icon_ctrl = (
            arcadia_logo(21)
            if key == "profile"
            else ft.Icon(icon, size=21, color=TEAL if is_active else "#4B5563")
        )
        row_items: list[ft.Control] = [
            ft.Container(width=24, alignment=ft.Alignment.CENTER, content=icon_ctrl),
            ft.Text(
                label,
                size=16,
                color=TEAL if is_active else INK,
                weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_500,
                no_wrap=True,
            ),
        ]
        if badge:
            row_items.append(
                ft.Container(
                    content=ft.Text(badge, size=10, color=MUTED, weight=ft.FontWeight.W_500, no_wrap=True),
                    bgcolor="#F3F4F6",
                    border=ft.Border.all(1, LINE),
                    border_radius=999,
                    padding=ft.Padding.symmetric(horizontal=7, vertical=2),
                )
            )
        normal = TEAL_SOFT if is_active else None
        return ft.Container(
            height=50,
            border_radius=12,
            bgcolor=normal,
            padding=ft.Padding.symmetric(horizontal=14),
            on_hover=None if is_active else hover_bg(normal, "#F3F6F5"),
            on_click=lambda _, k=key: navigate(k),
            ink=True,
            content=ft.Row(row_items, spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        )

    # Build recent chats column if a custom one wasn't passed by AI_Assistant
    if chat_list_control is None:
        chats_col = ft.Column(spacing=2, expand=True, scroll=ft.ScrollMode.AUTO)

        def render_sidebar_chats():
            try:
                store = backend.ChatStore()
                chats = store.chats
            except Exception:
                chats = []

            def delete_sidebar_chat(cid: int):
                try:
                    s = backend.ChatStore()
                    s.delete(cid)
                except Exception:
                    pass
                render_sidebar_chats()
                if page is not None:
                    page.update()

            rows = []
            for c in chats:
                is_current_chat = norm_active == "assistant" and backend.CURRENT_CHAT_ID == c.id
                normal_bg = "#F2F3F5" if is_current_chat else None
                rows.append(
                    ft.Container(
                        height=46,
                        border_radius=10,
                        bgcolor=normal_bg,
                        padding=ft.Padding.only(left=14, right=10),
                        on_hover=hover_bg(normal_bg, "#F6F7F8"),
                        on_click=lambda _, cid=c.id: open_chat_from_sidebar(cid),
                        ink=True,
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=19, color=MUTED),
                                ft.Text(
                                    c.title,
                                    size=15,
                                    color=INK if is_current_chat else MUTED,
                                    expand=True,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Container(
                                    width=24,
                                    height=24,
                                    border_radius=6,
                                    alignment=ft.Alignment.CENTER,
                                    on_hover=hover_bg(None, LINE),
                                    on_click=lambda _, cid=c.id: delete_sidebar_chat(cid),
                                    content=ft.Icon(ft.Icons.CLOSE, size=14, color="#9CA3AF"),
                                ),
                            ],
                            spacing=11,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    )
                )
            chats_col.controls = rows

        render_sidebar_chats()
        chat_list_control = chats_col

    brand = ft.Container(
        padding=ft.Padding.only(left=10),
        content=ft.Row(
            [
                arcadia_logo(44),
                ft.Text("Arcadia", size=26, color=INK, weight=ft.FontWeight.W_700),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    new_chat_btn = ft.Container(
        height=52,
        border_radius=12,
        bgcolor=TEAL,
        alignment=ft.Alignment.CENTER,
        on_hover=hover_bg(TEAL, TEAL_HOVER),
        on_click=handle_new_chat,
        ink=True,
        shadow=ft.BoxShadow(blur_radius=6, color="#2213766B", offset=ft.Offset(0, 2)),
        content=ft.Row(
            [
                ft.Icon(ft.Icons.ADD, color=WHITE, size=20),
                ft.Text("New study chat", size=16, color=WHITE, weight=ft.FontWeight.W_600),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )

    nav_col = ft.Column(
        [
            nav_item("assistant", "AI Assistant", ft.Icons.AUTO_AWESOME_OUTLINED),
            nav_item("flashcards", "Flashcards", ft.Icons.LAYERS_OUTLINED),
            nav_item("planner", "Study planner", ft.Icons.CALENDAR_MONTH_OUTLINED, badge="To-do · Calendar"),
            nav_item("timer", "Study timer", ft.Icons.TIMER_OUTLINED),
            nav_item("profile", "Profile"),
        ],
        spacing=6,
    )

    sync_note = ft.Container(
        padding=ft.Padding.only(left=14, right=14, top=12),
        content=ft.Row(
            [
                ft.Icon(ft.Icons.SYNC, size=15, color=MUTED),
                ft.Text("To-do list and calendar stay in sync", size=12.5, color=MUTED, expand=True),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    user_info = backend.USER
    user_initials_ctrl = ft.Text(
        user_info.get("initials", "ST"),
        size=15,
        color=INK,
        weight=ft.FontWeight.W_700,
    )
    user_name_ctrl = ft.Text(
        user_info.get("name", "Student"),
        size=15.5,
        color=INK,
        weight=ft.FontWeight.W_600,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    def update_sidebar_user_card():
        u = backend.USER
        user_initials_ctrl.value = u.get("initials", "ST")
        user_name_ctrl.value = u.get("name", "Student")
        if user_name_ctrl.page is not None:
            try:
                user_name_ctrl.update()
                user_initials_ctrl.update()
            except Exception:
                pass
        elif page is not None:
            try:
                page.update()
            except Exception:
                pass

    register_sidebar_listener(update_sidebar_user_card)

    user_card = ft.Container(
        height=74,
        border_radius=12,
        bgcolor="#F2F8F7" if norm_active == "profile" else WHITE,
        border=ft.Border.all(1, "#D5E9E5" if norm_active == "profile" else LINE),
        padding=ft.Padding.symmetric(horizontal=15),
        on_hover=hover_bg("#F2F8F7" if norm_active == "profile" else WHITE, "#F8FAFB"),
        on_click=lambda _: navigate("profile"),
        ink=True,
        content=ft.Row(
            [
                ft.Container(
                    width=42,
                    height=42,
                    border_radius=21,
                    bgcolor="#E5ECEB",
                    alignment=ft.Alignment.CENTER,
                    content=user_initials_ctrl,
                ),
                ft.Column(
                    [
                        user_name_ctrl,
                        ft.Text("View profile", size=12, color=MUTED),
                    ],
                    spacing=1,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    return ft.Container(
        width=SIDEBAR_W,
        bgcolor=WHITE,
        border=ft.Border.only(right=ft.BorderSide(1, LINE)),
        padding=ft.Padding.only(left=19, top=32, right=19, bottom=18),
        content=ft.Column(
            [
                brand,
                ft.Container(height=30),
                new_chat_btn,
                ft.Container(height=24),
                nav_col,
                sync_note,
                ft.Container(height=32),
                ft.Container(
                    padding=ft.Padding.only(left=10, bottom=8),
                    content=ft.Text("RECENT CHATS", size=12.5, color=MUTED, weight=ft.FontWeight.W_600),
                ),
                chat_list_control,
                ft.Container(height=10),
                user_card,
            ],
            spacing=0,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
    )


def build_sidebar(active_tab: str, switch_tab: Optional[Callable[[str], None]] = None, page: Optional[ft.Page] = None) -> ft.Container:
    """Backwards-compatible entry point returning the unified 312px sidebar."""
    return build_unified_sidebar(page=page, active_tab=active_tab, switch_tab=switch_tab)
