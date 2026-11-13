import flet as ft
from theme import PRIMARY_TEAL, LIGHT_TEAL, TEXT_DARK, TEXT_GREY, BORDER_COLOR


def build_sidebar(active_tab: str, switch_tab) -> ft.Column:
    def nav_item(icon, text, tab_name, badges=None):
        is_active = active_tab == tab_name
        content_row = [
            ft.Icon(icon, color=PRIMARY_TEAL if is_active else TEXT_GREY, size=20),
            ft.Text(
                text,
                weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_500,
                color=PRIMARY_TEAL if is_active else TEXT_DARK,
                size=14,
            ),
        ]
        if badges:
            content_row.append(
                ft.Container(
                    content=ft.Text(badges, size=10, color=TEXT_GREY),
                    bgcolor=BORDER_COLOR,
                    padding=ft.Padding(6, 2, 6, 2),
                    border_radius=10,
                    margin=ft.Margin(8, 0, 0, 0),
                )
            )
        return ft.Container(
            content=ft.Row(content_row),
            bgcolor=LIGHT_TEAL if is_active else ft.Colors.TRANSPARENT,
            padding=ft.Padding(12, 10, 12, 10),
            border_radius=8,
            margin=ft.Margin(0, 0, 0, 4),
            ink=True,
            on_click=lambda _: switch_tab(tab_name),
        )

    def chat_item(text):
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=16, color=TEXT_GREY),
                ft.Text(text, size=13, color=TEXT_GREY, no_wrap=True),
            ]),
            padding=ft.Padding(12, 8, 12, 8),
        )

    return ft.Column([
        ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.MENU_BOOK, color=ft.Colors.WHITE, size=20),
                    bgcolor="#1E293B",
                    padding=6,
                    border_radius=6,
                ),
                ft.Text("Arcadia", size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
            ],
            margin=ft.Margin(0, 0, 0, 24),
        ),
        ft.Button(
            content=ft.Text("+ New study chat", color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            bgcolor=PRIMARY_TEAL,
            width=float("inf"),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=16),
            on_click=lambda _: switch_tab("ai"),
        ),
        ft.Divider(height=24, color=ft.Colors.TRANSPARENT),
        nav_item(ft.Icons.AUTO_AWESOME, "AI Assistant", "ai"),
        nav_item(ft.Icons.STYLE, "Flashcards", "flashcards"),
        nav_item(ft.Icons.CALENDAR_TODAY, "Study planner", "planner", badges="To-do · Calendar"),
        nav_item(ft.Icons.TIMER, "Study timer", "timer"),
        nav_item(ft.Icons.PERSON, "Profile", "profile"),
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SYNC, size=14, color=TEXT_GREY),
                ft.Text("To-do list and calendar stay in\nsync", size=11, color=TEXT_GREY),
            ]),
            margin=ft.Margin(0, 16, 0, 24),
        ),
        ft.Text(
            "RECENT CHATS",
            size=11,
            weight=ft.FontWeight.BOLD,
            color=TEXT_GREY,
            margin=ft.Margin(12, 0, 0, 8),
        ),
        ft.Column(
            [
                chat_item("New study chat"),
                chat_item("New study chat"),
                chat_item("New study chat"),
                chat_item("What is E=mc²?"),
                chat_item("Help with my I2P question"),
            ],
            spacing=0,
            expand=True,
        ),
        ft.Container(
            content=ft.Row([
                ft.CircleAvatar(
                    content=ft.Text("JD", size=12, color=TEXT_DARK),
                    bgcolor=BORDER_COLOR,
                    radius=18,
                ),
                ft.Column(
                    [
                        ft.Text("John Doe", size=14, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                        ft.Text("View profile", size=12, color=TEXT_GREY),
                    ],
                    spacing=0,
                ),
            ]),
            padding=12,
            border=ft.Border(
                top=ft.BorderSide(1, BORDER_COLOR),
                bottom=ft.BorderSide(1, BORDER_COLOR),
                left=ft.BorderSide(1, BORDER_COLOR),
                right=ft.BorderSide(1, BORDER_COLOR),
            ),
            border_radius=12,
        ),
    ])