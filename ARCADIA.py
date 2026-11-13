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

    async def route_change(e):
        try:
            page.on_resize = None
            route = page.route or "/"
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
                new_view = login.get_view(page)

            if inspect.isawaitable(new_view):
                new_view = await new_view

            page.views.clear()
            page.views.append(new_view)
        except Exception:
            error_trace = traceback.format_exc()
            page.views.clear()
            page.views.append(
                ft.View(
                    route="/error",
                    controls=[
                        ft.Text(
                            "ERROR FOUND!",
                            color=ft.Colors.RED,
                            size=24,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(
                            content=ft.Text(error_trace, selectable=True, size=12),
                            bgcolor=ft.Colors.GREY_200,
                            padding=15,
                            border_radius=8,
                        ),
                    ],
                )
            )
        page.update()

    async def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)
        else:
            page.go("/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    if not page.route:
        page.route = "/"
    await route_change(None)


if __name__ == "__main__":
    ft.app(main)
