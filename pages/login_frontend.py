import flet as ft

def get_view(page: ft.Page):
    async def go_profile(e):
        await page.push_route("/profile")

    return ft.View(
        route="/",
        controls=[
            ft.AppBar(title=ft.Text("Login"), bgcolor="#2196F3"),
            ft.Text("Welcome to ARCADIA!"),
            ft.Button("Login & Go to Profile", on_click=go_profile)
        ]
    )