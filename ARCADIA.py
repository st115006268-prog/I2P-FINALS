import flet as ft
import traceback

from pages import (
    login_frontend, 
    profile_backend_dalem, 
    studyplanner_backend_dalem, 
    studytimer_backend_dalem, 
    study_view_page, 
    flashcards_page, 
    AI_Assistant
)

async def main(page: ft.Page):
    page.title = "ARCADIA"
    page.theme_mode = ft.ThemeMode.LIGHT

    async def route_change(e):
        page.views.clear()
        
        try:
            page.views.append(login_frontend.get_view(page))

            if page.route == "/profile":
                page.views.append(profile_backend_dalem.get_view(page))
            elif page.route == "/studyplanner":
                page.views.append(studyplanner_backend_dalem.get_view(page))
            elif page.route == "/studytimer":
                page.views.append(studytimer_backend_dalem.get_view(page))
            elif page.route == "/studyview":
                page.views.append(study_view_page.get_view(page))
            elif page.route == "/flashcards":
                page.views.append(flashcards_page.get_view(page))
            elif page.route == "/ai-assistant":
                page.views.append(AI_Assistant.get_view(page))
                
        except Exception:
            error_trace = traceback.format_exc()
            page.views.append(
                ft.View(
                    route="/error",
                    controls=[
                        ft.Text("ERROR FOUND!", color=ft.Colors.RED, size=24, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(error_trace, selectable=True, size=12),
                            bgcolor=ft.Colors.GREY_200,
                            padding=15,
                            border_radius=8
                        )
                    ]
                )
            )
            
        page.update()

    async def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Render the initial view directly instead of waiting for push_route("/")
    if not page.route:
        page.route = "/"
    await route_change(None)

if __name__ == "__main__":
    ft.run(main)