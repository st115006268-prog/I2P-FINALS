import flet as ft
from theme import PRIMARY_TEAL, TEXT_GREY, TEXT_DARK, LIGHT_TEAL, BORDER_COLOR

LOGO_SVG = """<svg viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg">
<rect width="44" height="44" rx="9" fill="#1d2840"/>
<rect x="13.5" y="10" width="15" height="22" rx="2.4" fill="#d9363e" transform="rotate(-8 21 21)"/>
<rect x="15.5" y="11" width="15" height="22" rx="2.4" fill="#ffffff"/>
<path d="M23 17.2c1.6 1.9 3.6 3.1 3.6 4.9 0 1.2-1 2-2 2-.6 0-1.1-.3-1.4-.6l.5 2h-1.4l.5-2c-.3.3-.8.6-1.4.6-1 0-2-.8-2-2 0-1.8 2-3 3.6-4.9z" fill="#1d2840"/>
</svg>"""


def arcadia_logo(size: float = 38) -> ft.Image:
    return ft.Image(src=LOGO_SVG.encode(), width=size, height=size)


def build_sidebar(active_tab: str, switch_tab) -> ft.Column:
    def nav_item(icon, text, tab_name, badges=None):
        is_active = active_tab == tab_name
        icon_ctrl = (
            arcadia_logo(20)
            if icon == "logo"
            else ft.Icon(icon, color=PRIMARY_TEAL if is_active else TEXT_GREY, size=20)
        )
        content_row = [
            icon_ctrl,
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
                    bgcolor="#F3F4F6",
                    border=ft.Border.all(1, BORDER_COLOR),
                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                    border_radius=10,
                    margin=ft.Margin.only(left=6),
                )
            )
        return ft.Container(
            content=ft.Row(content_row, spacing=10),
            bgcolor=LIGHT_TEAL if is_active else ft.Colors.TRANSPARENT,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            border_radius=10,
            margin=ft.Margin.only(bottom=4),
            ink=True,
            on_click=lambda _: switch_tab(tab_name),
        )

    def chat_item(text):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=16, color=TEXT_GREY),
                    ft.Text(
                        text,
                        size=13,
                        color=TEXT_GREY,
                        no_wrap=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            border_radius=8,
            ink=True,
            on_click=lambda _: switch_tab("assistant"),
        )

    return ft.Column([
        ft.Row(
            [
                ft.Container(
                    content=arcadia_logo(40),
                    border_radius=9,
                    shadow=ft.BoxShadow(
                        blur_radius=6,
                        offset=ft.Offset(0, 2),
                        color="#33111827",
                    ),
                ),
                ft.Text("Arcadia", size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
            ],
            spacing=12,
            margin=ft.Margin.only(bottom=24),
        ),
        ft.Button(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=18),
                    ft.Text(
                        "New study chat",
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.W_600,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=PRIMARY_TEAL,
            width=float("inf"),
            height=46,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=0,
            ),
            on_click=lambda _: switch_tab("assistant"),
        ),
        ft.Container(height=20),
        nav_item(ft.Icons.AUTO_AWESOME_OUTLINED, "AI Assistant", "assistant"),
        nav_item(ft.Icons.LAYERS_OUTLINED, "Flashcards", "flashcards"),
        nav_item(
            ft.Icons.CALENDAR_MONTH_OUTLINED,
            "Study planner",
            "planner",
            badges="To-do · Calendar",
        ),
        nav_item(ft.Icons.TIMER_OUTLINED, "Study timer", "timer"),
        nav_item("logo", "Profile", "profile"),
        ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.SYNC, size=14, color=TEXT_GREY),
                    ft.Text(
                        "To-do list and calendar stay in\nsync",
                        size=11,
                        color=TEXT_GREY,
                    ),
                ],
                spacing=8,
            ),
            margin=ft.Margin.only(left=12, top=14, bottom=22),
        ),
        ft.Text(
            "RECENT CHATS",
            size=11,
            weight=ft.FontWeight.BOLD,
            color=TEXT_GREY,
            margin=ft.Margin.only(left=12, bottom=8),
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
            content=ft.Row(
                [
                    ft.CircleAvatar(
                        content=ft.Text(
                            "JD",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_DARK,
                        ),
                        bgcolor="#E5E7EB",
                        radius=18,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "John Doe",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=TEXT_DARK,
                            ),
                            ft.Text("View profile", size=12, color=TEXT_GREY),
                        ],
                        spacing=0,
                    ),
                ],
                spacing=12,
            ),
            padding=12,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=12,
            ink=True,
            on_click=lambda _: switch_tab("profile"),
        ),
    ])