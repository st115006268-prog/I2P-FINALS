import flet as ft
from theme import PRIMARY_TEAL, LIGHT_TEAL, TEXT_DARK, TEXT_GREY, BORDER_COLOR


def build_ai_study_view(switch_tab) -> ft.Container:
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
                    content=ft.Text("+ AI suggested deck", color=PRIMARY_TEAL, weight=ft.FontWeight.W_600),
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
                padding=ft.Padding(16, 8, 16, 8),
                border=ft.Border(bottom=ft.BorderSide(2, PRIMARY_TEAL)),
            ),
            ft.Container(
                content=ft.Text("Quiz", color=TEXT_GREY),
                padding=ft.Padding(16, 8, 16, 8),
            ),
            ft.Container(expand=True),
            ft.Button(
                content=ft.Row([
                    ft.Icon(ft.Icons.ARROW_BACK, size=16, color=TEXT_GREY),
                    ft.Text("Back to decks", color=TEXT_GREY),
                ]),
                bgcolor=ft.Colors.TRANSPARENT,
                on_click=lambda _: switch_tab("flashcards"),
            ),
        ],
        margin=ft.Margin(0, 24, 0, 24),
    )

    deck_title = ft.Column(
        [
            ft.Text("GEN PHYS", size=20, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
            ft.Row(
                [
                    ft.Text("General Physics · Flashcard study", color=TEXT_GREY, size=14),
                    ft.Text("Card 1 of 4", color=TEXT_GREY, size=14),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.ProgressBar(value=0.25, color=PRIMARY_TEAL, bgcolor=BORDER_COLOR, height=6),
        ],
        spacing=8,
        margin=ft.Margin(0, 0, 0, 24),
    )

    flashcard = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border=ft.Border(
            top=ft.BorderSide(1, BORDER_COLOR),
            bottom=ft.BorderSide(1, BORDER_COLOR),
            left=ft.BorderSide(1, BORDER_COLOR),
            right=ft.BorderSide(1, BORDER_COLOR),
        ),
        border_radius=16,
        padding=40,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text("QUESTION", size=12, weight=ft.FontWeight.BOLD, color=PRIMARY_TEAL),
                            bgcolor=LIGHT_TEAL,
                            padding=ft.Padding(12, 6, 12, 6),
                            border_radius=16,
                        ),
                        ft.Text("General Physics", size=14, color=TEXT_GREY),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=60),
                ft.Text(
                    "What is the dimension of Force?",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_DARK,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Take a moment to recall the answer.",
                    size=16,
                    color=TEXT_GREY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=60),
                ft.Row(
                    [
                        ft.Button(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.VISIBILITY, color=ft.Colors.WHITE, size=18),
                                    ft.Text("Reveal answer", color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                                ],
                                spacing=8,
                            ),
                            bgcolor=PRIMARY_TEAL,
                            style=ft.ButtonStyle(padding=16, shape=ft.RoundedRectangleBorder(radius=8)),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    card_navigation = ft.Row(
        [
            ft.Button(
                content=ft.Row([
                    ft.Icon(ft.Icons.ARROW_BACK, size=18, color=PRIMARY_TEAL),
                    ft.Text("Previous", color=PRIMARY_TEAL),
                ]),
                bgcolor=LIGHT_TEAL,
                style=ft.ButtonStyle(padding=16, shape=ft.RoundedRectangleBorder(radius=8)),
            ),
            ft.Text("1 / 4", color=TEXT_GREY, size=14),
            ft.Button(
                content=ft.Row(
                    [
                        ft.Text("Next", color=ft.Colors.WHITE),
                        ft.Icon(ft.Icons.ARROW_FORWARD, size=18, color=ft.Colors.WHITE),
                    ],
                    spacing=4,
                ),
                bgcolor=PRIMARY_TEAL,
                style=ft.ButtonStyle(padding=16, shape=ft.RoundedRectangleBorder(radius=8)),
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        margin=ft.Margin(0, 24, 0, 0),
    )

    footer_text = ft.Text(
        "Recall first, then reveal. Go at your own pace.",
        color=TEXT_GREY,
        size=13,
        text_align=ft.TextAlign.CENTER,
    )

    return ft.Container(
        padding=40,
        expand=True,
        content=ft.Column(
            [
                header_row,
                tabs_row,
                deck_title,
                flashcard,
                card_navigation,
                ft.Container(content=footer_text, alignment=ft.Alignment.CENTER, margin=ft.Margin(0, 24, 0, 0)),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )