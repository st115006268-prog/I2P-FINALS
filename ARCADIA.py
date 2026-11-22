import inspect
import traceback
import flet as ft
import flet_compat  # ensures cross-version compatibility for ft.Alignment, ft.Padding, ft.Border, etc.

from pages import (
    ai_assistant,
    flashcards,
    login,
    profile,
    study_planner,
    study_timer,
    study_view,
)


# Cross-fade duration (ms) when switching pages.
PAGE_FADE_MS = 220


async def main(page: ft.Page):
    page.title = "ARCADIA"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#F4F5F7"
    page.fonts = {
        "Inter": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
        "Inter SemiBold": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
        "Jakarta Bold": "https://raw.githubusercontent.com/google/fonts/main/ofl/plusjakartasans/PlusJakartaSans%5Bwght%5D.ttf",
    }
    page.theme = ft.Theme(font_family="Inter", color_scheme_seed="#13766B")
    try:
        page.window.width = 1440
        page.window.height = 920
        page.window.min_width = 960
        page.window.min_height = 640
    except Exception:
        pass

    # One persistent View for the whole app. Page content is cross-faded inside it with
    # an AnimatedSwitcher, instead of replacing page.views (which makes Flutter play its
    # own route animation with the old and new views overlapping / zooming).
    switcher = ft.AnimatedSwitcher(
        content=ft.Container(expand=True),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=PAGE_FADE_MS,
        reverse_duration=PAGE_FADE_MS,
        expand=True,
    )
    shell = ft.View(
        route="/",
        padding=0,
        spacing=0,
        bgcolor="#F4F5F7",
        controls=[switcher],
    )

    def wrap_page_content(view: ft.View, route: str) -> ft.Control:
        """Turn a page's ft.View into a keyed container the switcher can animate."""
        return ft.Container(
            key=route,  # a new key per route is what makes AnimatedSwitcher animate
            expand=True,
            bgcolor=getattr(view, "bgcolor", None) or "#F4F5F7",
            padding=getattr(view, "padding", 0) or 0,
            content=ft.Column(list(view.controls), spacing=0, expand=True),
        )

    def cleanup_previous_view():
        """Drop everything the previous page left attached to the page itself.

        Overlays (FilePickers, dialogs) and sidebar listeners live outside the view,
        so swapping content does not remove them. Without this they pile up on every
        navigation and can leave stale dialogs / duplicate pickers on the next page.
        """
        page.on_resize = None
        try:
            page.overlay.clear()
        except Exception:
            pass
        try:
            page.dialog = None
        except Exception:
            pass
        try:
            from pages import sidebar as _sidebar
            _sidebar._SIDEBAR_LISTENERS.clear()
        except Exception:
            pass

    def build_error_content(error_trace: str) -> ft.Control:
        return ft.Container(
            key="/error",
            expand=True,
            padding=24,
            content=ft.Column(
                [
                    ft.Text("ERROR FOUND!", color=ft.Colors.RED, size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Text(error_trace, selectable=True, size=12),
                        bgcolor=ft.Colors.GREY_200,
                        padding=15,
                        border_radius=8,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
        )

    async def route_change(e):
        route = page.route or "/"
        try:
            cleanup_previous_view()
            if route == "/":
                new_view = login.get_view(page)
            elif route == "/ai-assistant":
                new_view = ai_assistant.get_view(page)
            elif route == "/flashcards":
                new_view = flashcards.get_view(page)
            elif route == "/studyview":
                new_view = study_view.get_view(page)
            elif route == "/studyplanner":
                new_view = study_planner.get_view(page)
            elif route == "/studytimer":
                new_view = study_timer.get_view(page)
            elif route == "/profile":
                new_view = profile.get_view(page)
            else:
                route = "/"
                new_view = login.get_view(page)

            if inspect.isawaitable(new_view):
                new_view = await new_view

            switcher.content = wrap_page_content(new_view, route)
        except Exception:
            switcher.content = build_error_content(traceback.format_exc())

        shell.bgcolor = getattr(switcher.content, "bgcolor", None) or "#F4F5F7"
        page.update()

    async def view_pop(e):
        page.go("/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.views.clear()
    page.views.append(shell)

    if not page.route:
        page.route = "/"
    await route_change(None)


if __name__ == "__main__":
    ft.app(main)