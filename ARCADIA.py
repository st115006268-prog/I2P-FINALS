import flet as ft
from theme import BORDER_COLOR, BG_LIGHT
from pages.sidebar import build_sidebar
from pages.flashcards_page import build_flashcards_view
from pages.study_view_page import build_ai_study_view

# Import AI_Assistant dari folder pages
from pages import AI_Assistant

def _build_assistant_only(page: ft.Page) -> ft.Control:
    orig_add = page.add
    page.add = lambda *args, **kwargs: None
    try:
        assistant_app = AI_Assistant.ArcadiaApp(page)
    finally:
        page.add = orig_add

    def _resize(e=None):
        width = (page.width or 1440) - 260 - 48
        w = max(320, min(AI_Assistant.CONTENT_MAX_W, width))
        assistant_app.bottom.width = w
        assistant_app.messages_box.width = w
        page.update()

    page.on_resize = _resize
    _resize()
    return assistant_app._main()


def main(page: ft.Page):
    page.title = "Arcadia Study App"
    page.padding = 0
    page.bgcolor = BG_LIGHT
    page.theme_mode = ft.ThemeMode.LIGHT

    page.fonts = {
        "Inter": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf"
    }

    # Variabel utama untuk melacak halaman saat ini
    active_tab = "assistant"
    
    main_content_container = ft.Container(expand=True)
    sidebar_container = ft.Container(
        width=260,
        bgcolor=ft.Colors.WHITE,
        padding=20,
        border=ft.Border(right=ft.BorderSide(1, BORDER_COLOR)),
    )

    def switch_tab(tab_name: str):
        print(f"DEBUG: Berpindah ke tab -> {tab_name}") # Akan muncul di terminal/CMD untuk mengecek jika ada yang salah klik
        nonlocal active_tab
        active_tab = tab_name
        sidebar_container.content = build_sidebar(active_tab, switch_tab)

        # PENCOCOKAN HALAMAN
        if active_tab == "flashcards":
            main_content_container.content = build_flashcards_view(switch_tab)
            
        elif active_tab == "assistant":
            main_content_container.content = _build_assistant_only(page)
            
        elif active_tab == "planner":
            main_content_container.content = ft.Container(
                content=ft.Text("Halaman Study Planner", size=20, weight="bold"),
                alignment=ft.Alignment.CENTER, expand=True
            )
            
        elif active_tab == "timer":
            main_content_container.content = ft.Container(
                content=ft.Text("Halaman Study Timer", size=20, weight="bold"),
                alignment=ft.Alignment.CENTER, expand=True
            )
            
        elif active_tab == "profile":
            main_content_container.content = ft.Container(
                content=ft.Text("Halaman Profile", size=20, weight="bold"),
                alignment=ft.Alignment.CENTER, expand=True
            )
            
        else:
            # Halaman default Gen Phys
            main_content_container.content = build_ai_study_view(switch_tab)

        page.update()

    # Buka halaman AI assistant secara otomatis saat pertama kali dibuka
    switch_tab("assistant")

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.QUESTION_MARK,
        bgcolor="#374151",
        shape=ft.CircleBorder(),
        mini=True,
    )

    page.add(ft.Row([sidebar_container, main_content_container], expand=True, spacing=0))

if __name__ == "__main__":
    ft.run(main)