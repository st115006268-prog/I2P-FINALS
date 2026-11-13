import inspect
import traceback
import flet as ft

from pages import (
    AI_Assistant,
    flashcards_page,
    login_frontend,
    profile_backend_dalem,
    study_view_page,
    studyplanner_backend_dalem,
    studytimer_backend_dalem,
)


async def main(page: ft.Page):
    page.title = "ARCADIA"
    page.theme_mode = ft.ThemeMode.LIGHT

    async def route_change(e):
        try:
            route = page.route or "/"
            if route == "/":
                new_view = login_frontend.get_view(page)
            elif route == "/ai-assistant":
                new_view = AI_Assistant.get_view(page)
            elif route == "/flashcards":
                new_view = flashcards_page.get_view(page)
            elif route == "/studyview":
                new_view = study_view_page.get_view(page)
            elif route == "/studyplanner":
                new_view = studyplanner_backend_dalem.get_view(page)
            elif route == "/studytimer":
                new_view = studytimer_backend_dalem.get_view(page)
            elif route == "/profile":
                new_view = profile_backend_dalem.get_view(page)
            else:
                new_view = login_frontend.get_view(page)

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
            await page.push_route(page.views[-1].route)
        else:
            await page.push_route("/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    if not page.route:
        page.route = "/"
    await route_change(None)


if __name__ == "__main__":
    ft.run(main)