import flet as ft
from theme import PRIMARY_TEAL, LIGHT_TEAL, TEXT_DARK, TEXT_GREY, BORDER_COLOR, DARK_BANNER


def build_flashcards_view(switch_tab) -> ft.Container:
    def deck_card(accent_color, title, subtitle, progress_val):
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border=ft.Border(
                top=ft.BorderSide(1, BORDER_COLOR),
                bottom=ft.BorderSide(1, BORDER_COLOR),
                left=ft.BorderSide(1, BORDER_COLOR),
                right=ft.BorderSide(1, BORDER_COLOR),
            ),
            border_radius=16,
            padding=20,
            content=ft.Column([
                ft.Container(
                    width=32,
                    height=4,
                    bgcolor=accent_color,
                    border_radius=2,
                    margin=ft.Margin(0, 0, 0, 16),
                ),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(subtitle, size=13, color=TEXT_GREY, margin=ft.Margin(0, 0, 0, 16)),
                ft.ProgressBar(value=progress_val, color=accent_color, bgcolor="#F3F4F6", height=6),
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Button(
                            content=ft.Text("Study", color=ft.Colors.WHITE, size=13, weight=ft.FontWeight.W_600),
                            bgcolor=PRIMARY_TEAL,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding(16, 8, 16, 8),
                            ),
                            on_click=lambda _: switch_tab("ai"),
                        ),
                        ft.Button(
                            content=ft.Text("Quiz", color=PRIMARY_TEAL, size=13, weight=ft.FontWeight.W_600),
                            bgcolor=ft.Colors.TRANSPARENT,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, BORDER_COLOR),
                                padding=ft.Padding(14, 8, 14, 8),
                            ),
                        ),
                        ft.Button(
                            content=ft.Text("Edit", color=PRIMARY_TEAL, size=13, weight=ft.FontWeight.W_600),
                            bgcolor=ft.Colors.TRANSPARENT,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, BORDER_COLOR),
                                padding=ft.Padding(14, 8, 14, 8),
                            ),
                        ),
                    ],
                    spacing=8,
                ),
            ]),
        )

    def create_deck_card():
        return ft.Container(
            bgcolor=LIGHT_TEAL,
            border=ft.Border(
                top=ft.BorderSide(1, PRIMARY_TEAL),
                bottom=ft.BorderSide(1, PRIMARY_TEAL),
                left=ft.BorderSide(1, PRIMARY_TEAL),
                right=ft.BorderSide(1, PRIMARY_TEAL),
            ),
            border_radius=16,
            padding=20,
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.ADD, color=PRIMARY_TEAL, size=24),
                        bgcolor=ft.Colors.WHITE,
                        shape=ft.BoxShape.CIRCLE,
                        width=40,
                        height=40,
                        alignment=ft.Alignment.CENTER,
                        margin=ft.Margin(0, 0, 0, 16),
                    ),
                    ft.Text("Create new deck", size=16, weight=ft.FontWeight.BOLD, color=PRIMARY_TEAL),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment.CENTER,
            ink=True,
        )

    header_row = ft.Row(
        [
            ft.Column(
                [
                    ft.Text("Flashcards", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                    ft.Text("Your decks and quizzes", size=14, color=TEXT_GREY),
                ],
                spacing=4,
            ),
            ft.Row([
                ft.Container(
                    content=ft.TextField(
                        hint_text="Search decks",
                        prefix_icon=ft.Icons.SEARCH,
                        text_size=14,
                        border=ft.InputBorder.NONE,
                        bgcolor=ft.Colors.TRANSPARENT,
                        height=36,
                        content_padding=10,
                    ),
                    bgcolor="#F3F4F6",
                    border_radius=8,
                    width=240,
                    height=40,
                ),
                ft.Button(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.AUTO_AWESOME, size=16, color=PRIMARY_TEAL),
                            ft.Text("AI suggested deck", color=PRIMARY_TEAL, weight=ft.FontWeight.W_600),
                        ],
                        spacing=6,
                    ),
                    bgcolor=LIGHT_TEAL,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=12),
                ),
                ft.Button(
                    content=ft.Text("+ New deck", color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                    bgcolor=PRIMARY_TEAL,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=12),
                ),
            ]),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    tabs_row = ft.Row(
        [
            ft.Container(
                content=ft.Text("Flashcards", color=PRIMARY_TEAL, weight=ft.FontWeight.W_600),
                bgcolor=ft.Colors.WHITE,
                padding=ft.Padding(20, 10, 20, 10),
                border_radius=8,
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color="#0000000D"),
            ),
            ft.Container(
                content=ft.Text("Quiz", color=TEXT_GREY, weight=ft.FontWeight.W_500),
                padding=ft.Padding(20, 10, 20, 10),
                border_radius=8,
            ),
        ],
        margin=ft.Margin(0, 24, 0, 24),
    )

    hero_banner = ft.Container(
        bgcolor=DARK_BANNER,
        border_radius=16,
        padding=28,
        margin=ft.Margin(0, 0, 0, 32),
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Continue studying", size=14, color="#9CA3AF"),
                        ft.Text("GEN PHYS · 4 cards", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    spacing=8,
                ),
                ft.Button(
                    content=ft.Text("Start studying", color=DARK_BANNER, weight=ft.FontWeight.BOLD),
                    bgcolor=LIGHT_TEAL,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding(20, 12, 20, 12),
                    ),
                    on_click=lambda _: switch_tab("ai"),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
    )

    decks_header = ft.Row(
        [
            ft.Text("My decks", size=20, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
            ft.Text("5 decks", size=14, color=TEXT_GREY),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        margin=ft.Margin(0, 0, 0, 16),
    )

    decks_grid = ft.GridView(
        height=550,
        runs_count=3,
        max_extent=340,
        child_aspect_ratio=1.35,
        spacing=16,
        run_spacing=16,
        controls=[
            deck_card(PRIMARY_TEAL, "GEN PHYS", "4 cards · General Physics", 0.6),
            deck_card("#6366F1", "I2P", "3 cards · Introduction to\nProgramming", 0.4),
            deck_card("#F59E0B", "Forms in Nature", "2 cards · Design Studies", 0.7),
            deck_card("#EC4899", "Deadly Elegance", "2 cards · Literature", 0.5),
            deck_card("#3B82F6", "College Chinese", "3 cards · Language", 0.3),
            create_deck_card(),
        ],
    )

    return ft.Container(
        padding=40,
        expand=True,
        content=ft.Column(
            [header_row, tabs_row, hero_banner, decks_header, decks_grid],
            scroll=ft.ScrollMode.AUTO,
        ),
    )