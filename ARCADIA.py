import flet as ft
from theme import BORDER_COLOR, BG_LIGHT
from pages.sidebar import build_sidebar
from pages.flashcards_page import build_flashcards_view
from pages.study_view_page import build_ai_study_view


def main(page: ft.Page):
    page.title = "Arcadia Study App"
    page.padding = 0
    page.bgcolor = BG_LIGHT
    page.theme_mode = ft.ThemeMode.LIGHT

    active_tab = "flashcards"
    main_content_container = ft.Container(expand=True)
    sidebar_container = ft.Container(
        width=260,
        bgcolor=ft.Colors.WHITE,
        padding=20,
        border=ft.Border(right=ft.BorderSide(1, BORDER_COLOR)),
    )

    def switch_tab(tab_name: str):
        nonlocal active_tab
        active_tab = tab_name
        sidebar_container.content = build_sidebar(active_tab, switch_tab)

        if active_tab == "flashcards":
            main_content_container.content = build_flashcards_view(switch_tab)
        else:
            main_content_container.content = build_ai_study_view(switch_tab)

        page.update()

    # Initial Render
    sidebar_container.content = build_sidebar(active_tab, switch_tab)
    main_content_container.content = build_flashcards_view(switch_tab)

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.QUESTION_MARK,
        bgcolor="#374151",
        shape=ft.CircleBorder(),
        mini=True,
    )

    page.add(ft.Row([sidebar_container, main_content_container], expand=True, spacing=0))


if __name__ == "__main__":
    ft.run(main)