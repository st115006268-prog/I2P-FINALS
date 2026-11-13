import flet as ft
from theme import PRIMARY_TEAL, LIGHT_TEAL, TEXT_DARK, TEXT_GREY, BORDER_COLOR
from pages.sidebar import build_sidebar

PAGE_BG = "#F6F8FA"
HERO_BG = "#12322C"
MINT_BTN = "#D5ECE7"

INITIAL_DECKS = [
    {
        "accent": "#13766B",
        "title": "GEN PHYS",
        "subtitle": "4 cards · General Physics",
        "progress": 0.56,
    },
    {
        "accent": "#5B5BD6",
        "title": "I2P",
        "subtitle": "3 cards · Introduction to\nProgramming",
        "progress": 0.38,
    },
    {
        "accent": "#D97706",
        "title": "Forms in Nature",
        "subtitle": "2 cards · Design Studies",
        "progress": 0.24,
    },
    {
        "accent": "#C85A7C",
        "title": "Deadly Elegance",
        "subtitle": "2 cards · Literature",
        "progress": 0.50,
    },
    {
        "accent": "#3B82F6",
        "title": "College Chinese",
        "subtitle": "3 cards · Language",
        "progress": 0.36,
    },
]


def build_flashcards_view(switch_tab, page: ft.Page | None = None) -> ft.Container:
    active_subtab = {"value": "flashcards"}
    search_query = {"value": ""}

    def deck_card(
        accent_color: str, title: str, subtitle: str, progress_val: float
    ) -> ft.Container:
        return ft.Container(
            expand=True,
            height=228,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=16,
            padding=24,
            shadow=ft.BoxShadow(
                blur_radius=6,
                color="#08111827",
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        width=34,
                        height=4,
                        bgcolor=accent_color,
                        border_radius=2,
                    ),
                    ft.Container(height=16),
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                    ft.Container(height=6),
                    ft.Container(
                        height=38,
                        alignment=ft.Alignment.TOP_LEFT,
                        content=ft.Text(subtitle, size=13, color=TEXT_GREY),
                    ),
                    ft.Container(height=10),
                    ft.ProgressBar(
                        value=progress_val,
                        color=accent_color,
                        bgcolor="#E5E7EB",
                        height=6,
                        border_radius=3,
                    ),
                    ft.Container(expand=True),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Button(
                                content=ft.Text(
                                    "Study",
                                    color=ft.Colors.WHITE,
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                ),
                                bgcolor=PRIMARY_TEAL,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.Padding.symmetric(
                                        horizontal=18, vertical=10
                                    ),
                                    elevation=0,
                                ),
                                on_click=lambda _: switch_tab("studyview"),
                            ),
                            ft.Button(
                                content=ft.Text(
                                    "Quiz",
                                    color=PRIMARY_TEAL,
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                ),
                                bgcolor=ft.Colors.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, "#D1D5DB"),
                                    padding=ft.Padding.symmetric(
                                        horizontal=16, vertical=10
                                    ),
                                    elevation=0,
                                ),
                                on_click=lambda _: set_subtab("quiz"),
                            ),
                            ft.Button(
                                content=ft.Text(
                                    "Edit",
                                    color=PRIMARY_TEAL,
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                ),
                                bgcolor=ft.Colors.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, "#D1D5DB"),
                                    padding=ft.Padding.symmetric(
                                        horizontal=16, vertical=10
                                    ),
                                    elevation=0,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def create_deck_card() -> ft.Container:
        return ft.Container(
            expand=True,
            height=228,
            bgcolor="#E7F4F1",
            border=ft.Border.all(1.5, "#8EC5BE"),
            border_radius=16,
            padding=24,
            alignment=ft.Alignment.CENTER,
            ink=True,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.ADD, color=PRIMARY_TEAL, size=22),
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        width=44,
                        height=44,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Text(
                        "Create new deck",
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY_TEAL,
                    ),
                ],
            ),
        )

    decks_count_text = ft.Text(
        f"{len(INITIAL_DECKS)} decks", size=14, color=TEXT_GREY
    )
    decks_rows = ft.Column(spacing=20)

    def render_decks(update: bool = True):
        q = search_query["value"].strip().lower()
        filtered = [
            d
            for d in INITIAL_DECKS
            if not q or q in d["title"].lower() or q in d["subtitle"].lower()
        ]
        decks_count_text.value = (
            f"{len(filtered)} deck" if len(filtered) == 1 else f"{len(filtered)} decks"
        )

        cards: list[ft.Control] = [
            deck_card(d["accent"], d["title"], d["subtitle"], d["progress"])
            for d in filtered
        ]
        cards.append(create_deck_card())

        rows = []
        for i in range(0, len(cards), 3):
            row_items = cards[i : i + 3]
            while len(row_items) < 3:
                row_items.append(ft.Container(expand=True))
            rows.append(ft.Row(spacing=20, controls=row_items))

        decks_rows.controls = rows
        if update and page is not None:
            page.update()

    def on_search(e: ft.ControlEvent):
        search_query["value"] = e.control.value or ""
        render_decks(update=True)

    # Top white header bar
    top_header = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.only(bottom=ft.BorderSide(1, BORDER_COLOR)),
        padding=ft.Padding.symmetric(horizontal=36, vertical=20),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Flashcards",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_DARK,
                        ),
                        ft.Text(
                            "Your decks and quizzes", size=14, color=TEXT_GREY
                        ),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=240,
                            height=42,
                            bgcolor="#F9FAFB",
                            border=ft.Border.all(1, BORDER_COLOR),
                            border_radius=10,
                            padding=ft.Padding.symmetric(horizontal=12),
                            content=ft.Row(
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.SEARCH, size=18, color=TEXT_GREY
                                    ),
                                    ft.TextField(
                                        hint_text="Search decks",
                                        text_size=14,
                                        hint_style=ft.TextStyle(
                                            size=14, color=TEXT_GREY
                                        ),
                                        border=ft.InputBorder.NONE,
                                        bgcolor=ft.Colors.TRANSPARENT,
                                        dense=True,
                                        expand=True,
                                        content_padding=ft.Padding.symmetric(
                                            vertical=10
                                        ),
                                        on_change=on_search,
                                    ),
                                ],
                            ),
                        ),
                        ft.Button(
                            height=42,
                            bgcolor=LIGHT_TEAL,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=ft.Padding.symmetric(horizontal=16),
                                elevation=0,
                            ),
                            content=ft.Row(
                                spacing=6,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.AUTO_AWESOME,
                                        size=16,
                                        color=PRIMARY_TEAL,
                                    ),
                                    ft.Text(
                                        "AI suggested deck",
                                        size=14,
                                        color=PRIMARY_TEAL,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ],
                            ),
                        ),
                        ft.Button(
                            height=42,
                            bgcolor=PRIMARY_TEAL,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=ft.Padding.symmetric(horizontal=18),
                                elevation=0,
                            ),
                            content=ft.Row(
                                spacing=6,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.ADD,
                                        size=18,
                                        color=ft.Colors.WHITE,
                                    ),
                                    ft.Text(
                                        "New deck",
                                        size=14,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    flashcards_tab = ft.Container(
        padding=ft.Padding.symmetric(horizontal=24, vertical=10),
        border_radius=10,
        ink=True,
        on_click=lambda _: set_subtab("flashcards"),
    )
    quiz_tab = ft.Container(
        padding=ft.Padding.symmetric(horizontal=24, vertical=10),
        border_radius=10,
        ink=True,
        on_click=lambda _: set_subtab("quiz"),
    )

    tabs_row = ft.Row(spacing=8, controls=[flashcards_tab, quiz_tab])

    hero_banner = ft.Container(
        bgcolor=HERO_BG,
        border_radius=18,
        padding=ft.Padding.symmetric(horizontal=32, vertical=28),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(
                            "Continue studying", size=13, color="#A7C4BE"
                        ),
                        ft.Text(
                            "GEN PHYS · 4 cards",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                ),
                ft.Button(
                    bgcolor=MINT_BTN,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding.symmetric(horizontal=22, vertical=14),
                        elevation=0,
                    ),
                    content=ft.Text(
                        "Start studying",
                        size=14,
                        color=HERO_BG,
                        weight=ft.FontWeight.BOLD,
                    ),
                    on_click=lambda _: switch_tab("studyview"),
                ),
            ],
        ),
    )

    decks_header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(
                "My decks", size=20, weight=ft.FontWeight.BOLD, color=TEXT_DARK
            ),
            decks_count_text,
        ],
    )

    quiz_placeholder = ft.Container(
        visible=False,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=36,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "Practice Quizzes",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_DARK,
                ),
                ft.Text(
                    "Select a deck to launch a multiple-choice quiz generated from your cards.",
                    size=14,
                    color=TEXT_GREY,
                ),
                ft.Container(height=8),
                ft.Button(
                    bgcolor=PRIMARY_TEAL,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding.symmetric(horizontal=20, vertical=12),
                    ),
                    content=ft.Text(
                        "Start GEN PHYS Quiz",
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.W_600,
                    ),
                    on_click=lambda _: switch_tab("studyview"),
                ),
            ],
        ),
    )

    flashcards_section = ft.Column(
        spacing=0,
        controls=[
            hero_banner,
            ft.Container(height=28),
            decks_header,
            ft.Container(height=16),
            decks_rows,
        ],
    )

    def sync_tabs(update: bool = True):
        is_fc = active_subtab["value"] == "flashcards"

        flashcards_tab.bgcolor = ft.Colors.WHITE if is_fc else ft.Colors.TRANSPARENT
        flashcards_tab.border = ft.Border.all(1, BORDER_COLOR) if is_fc else None
        flashcards_tab.content = ft.Text(
            "Flashcards",
            size=14,
            color=PRIMARY_TEAL if is_fc else TEXT_GREY,
            weight=ft.FontWeight.W_600 if is_fc else ft.FontWeight.W_500,
        )

        quiz_tab.bgcolor = ft.Colors.WHITE if not is_fc else ft.Colors.TRANSPARENT
        quiz_tab.border = ft.Border.all(1, BORDER_COLOR) if not is_fc else None
        quiz_tab.content = ft.Text(
            "Quiz",
            size=14,
            color=PRIMARY_TEAL if not is_fc else TEXT_GREY,
            weight=ft.FontWeight.W_600 if not is_fc else ft.FontWeight.W_500,
        )

        flashcards_section.visible = is_fc
        quiz_placeholder.visible = not is_fc

        if update and page is not None:
            page.update()

    def set_subtab(val: str):
        active_subtab["value"] = val
        sync_tabs(update=True)

    render_decks(update=False)
    sync_tabs(update=False)

    body = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
        controls=[
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=36, vertical=24),
                content=ft.Column(
                    spacing=0,
                    controls=[
                        tabs_row,
                        ft.Container(height=22),
                        flashcards_section,
                        quiz_placeholder,
                    ],
                ),
            )
        ],
    )

    return ft.Container(
        expand=True,
        bgcolor=PAGE_BG,
        content=ft.Column(
            spacing=0,
            expand=True,
            controls=[top_header, body],
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
        route="/flashcards",
        padding=0,
        bgcolor=PAGE_BG,
        controls=[
            ft.Row(
                [
                    ft.Container(
                        width=280,
                        bgcolor=ft.Colors.WHITE,
                        border=ft.Border.only(right=ft.BorderSide(1, BORDER_COLOR)),
                        padding=20,
                        content=build_sidebar("flashcards", switch_tab),
                    ),
                    build_flashcards_view(switch_tab, page),
                ],
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        ],
    )