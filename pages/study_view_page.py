import flet as ft
from theme import PRIMARY_TEAL, LIGHT_TEAL, TEXT_DARK, TEXT_GREY, BORDER_COLOR
from pages.sidebar import build_sidebar

CARDS = [
    ("What is the dimension of Force?", "M · L · T⁻²  (kg·m/s²)"),
    ("What is Newton's Second Law?", "F = m · a (Net force equals mass times acceleration)"),
    ("What is the SI unit of Work & Energy?", "Joule (J = N·m = kg·m²/s²)"),
    ("What is conservation of momentum?", "In a closed system with no external net force, total momentum remains constant."),
]


def build_ai_study_view(page: ft.Page, switch_tab) -> ft.Container:
    state = {"idx": 0, "revealed": False}

    badge_text = ft.Text("QUESTION", size=12, weight=ft.FontWeight.BOLD, color=PRIMARY_TEAL)
    card_main_text = ft.Text(
        CARDS[0][0],
        size=32,
        weight=ft.FontWeight.BOLD,
        color=TEXT_DARK,
        text_align=ft.TextAlign.CENTER,
    )
    card_sub_text = ft.Text(
        "Take a moment to recall the answer.",
        size=16,
        color=TEXT_GREY,
        text_align=ft.TextAlign.CENTER,
    )
    reveal_label = ft.Text("Reveal answer", color=ft.Colors.WHITE, weight=ft.FontWeight.W_600)
    progress_label = ft.Text(f"Card 1 of {len(CARDS)}", color=TEXT_GREY, size=14)
    progress_bar = ft.ProgressBar(value=1 / len(CARDS), color=PRIMARY_TEAL, bgcolor=BORDER_COLOR, height=6)
    counter_label = ft.Text(f"1 / {len(CARDS)}", color=TEXT_GREY, size=14)

    def sync_card():
        idx = state["idx"]
        q, a = CARDS[idx]
        if state["revealed"]:
            badge_text.value = "ANSWER"
            card_main_text.value = a
            card_sub_text.value = f"Question: {q}"
            reveal_label.value = "Show question"
        else:
            badge_text.value = "QUESTION"
            card_main_text.value = q
            card_sub_text.value = "Take a moment to recall the answer."
            reveal_label.value = "Reveal answer"
        progress_label.value = f"Card {idx + 1} of {len(CARDS)}"
        progress_bar.value = (idx + 1) / len(CARDS)
        counter_label.value = f"{idx + 1} / {len(CARDS)}"
        page.update()

    def toggle_reveal(_):
        state["revealed"] = not state["revealed"]
        sync_card()

    def prev_card(_):
        state["idx"] = (state["idx"] - 1) % len(CARDS)
        state["revealed"] = False
        sync_card()

    def next_card(_):
        state["idx"] = (state["idx"] + 1) % len(CARDS)
        state["revealed"] = False
        sync_card()

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
                    progress_label,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            progress_bar,
        ],
        spacing=8,
        margin=ft.Margin(0, 0, 0, 24),
    )

    flashcard = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=40,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=badge_text,
                            bgcolor=LIGHT_TEAL,
                            padding=ft.Padding(12, 6, 12, 6),
                            border_radius=16,
                        ),
                        ft.Text("General Physics", size=14, color=TEXT_GREY),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=60),
                card_main_text,
                card_sub_text,
                ft.Container(height=60),
                ft.Row(
                    [
                        ft.Button(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.VISIBILITY, color=ft.Colors.WHITE, size=18),
                                    reveal_label,
                                ],
                                spacing=8,
                            ),
                            bgcolor=PRIMARY_TEAL,
                            style=ft.ButtonStyle(padding=16, shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=toggle_reveal,
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
                on_click=prev_card,
            ),
            counter_label,
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
                on_click=next_card,
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


def get_view(page: ft.Page) -> ft.View:
    route_map = {
        "assistant": "/ai-assistant",
        "flashcards": "/flashcards",
        "planner": "/studyplanner",
        "timer": "/studytimer",
        "profile": "/profile",
        "studyview": "/studyview",
    }

    def switch_tab(tab: str):
        target = route_map.get(tab, "/")
        if target != page.route:
            page.run_task(page.push_route, target)

    return ft.View(
        route="/studyview",
        padding=0,
        controls=[
            ft.Row(
                [
                    ft.Container(width=260, padding=20, content=build_sidebar("flashcards", switch_tab)),
                    build_ai_study_view(page, switch_tab),
                ],
                expand=True,
                spacing=0,
            )
        ],
    )