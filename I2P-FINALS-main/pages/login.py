"""Arcadia sign-in & sign-up page — built with Flet and FastAPI backend."""
from __future__ import annotations

import re
import flet as ft
import flet_compat

from styles import (
    TEAL,
    TEAL_HOVER,
    TEAL_LIGHT,
    TEAL_SOFT,
    NAVY_1,
    NAVY_2,
    NAVY_3,
    NAVY,
    INK,
    MUTED,
    BORDER_COLOR,
    PAGE_BG,
    WHITE,
    arcadia_logo,
)

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
MIN_PASSWORD_LENGTH = 6

FONTS = {
    "Inter": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
    "Inter SemiBold": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
    "Jakarta Bold": "https://raw.githubusercontent.com/google/fonts/main/ofl/plusjakartasans/PlusJakartaSans%5Bwght%5D.ttf",
}

FEATURES = [
    ("01", "AI study assistant", "Ask questions and turn notes into clear explanations."),
    ("02", "Active recall flashcards", "Review key concepts with spaced repetition decks."),
    ("03", "Synced planner & timer", "Organize tasks and stay focused in timed sessions."),
]


# ---------------------------------------------------------------- helpers
def txt(value, size, color, family="Inter", spacing=None, height=None, align=None, weight=None):
    w = (
        weight
        if weight is not None
        else (
            ft.FontWeight.W_700
            if "Bold" in family and "Semi" not in family
            else ft.FontWeight.W_600
            if "SemiBold" in family
            else ft.FontWeight.W_400
        )
    )
    style = ft.TextStyle(letter_spacing=spacing, height=height) if (spacing is not None or height is not None) else None
    return ft.Text(
        value,
        size=size,
        color=color,
        font_family=family,
        weight=w,
        text_align=align,
        style=style,
    )


def _feature_row(num: str, title: str, desc: str) -> ft.Row:
    return ft.Row(
        spacing=14,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=39,
                height=39,
                border_radius=9,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ft.Colors.WHITE)),
                alignment=ft.Alignment.CENTER,
                content=txt(num, 12, "#E8EDF5", "Inter SemiBold"),
            ),
            ft.Column(
                spacing=2,
                controls=[
                    txt(title, 14, ft.Colors.WHITE, "Inter SemiBold"),
                    txt(desc, 13, "#C3CBDB"),
                ],
            ),
        ],
    )


def _ring(size: float, offset: float) -> ft.Container:
    return ft.Container(
        width=size,
        height=size,
        right=-300 + offset,
        bottom=-330 + offset,
        shape=ft.BoxShape.CIRCLE,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.WHITE)),
    )


def eyebrow(text: str, color: str) -> ft.Container:
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=12, vertical=6),
        border_radius=999,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.WHITE)),
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
        content=txt(text.upper(), 11.5, color, "Inter SemiBold", spacing=1.2),
    )


def brand_panel() -> ft.Container:
    logo = ft.Row(
        spacing=14,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            arcadia_logo(44),
            txt("Arcadia", 26, ft.Colors.WHITE, "Jakarta Bold", spacing=-0.5),
        ],
    )

    hero = ft.Column(
        spacing=0,
        controls=[
            eyebrow("Your study space", TEAL_LIGHT),
            ft.Container(height=24),
            ft.Container(
                width=600,
                content=txt(
                    "Make every study session count.",
                    48,
                    ft.Colors.WHITE,
                    "Jakarta Bold",
                    spacing=-2.0,
                    height=1.15,
                ),
            ),
            ft.Container(height=20),
            ft.Container(
                width=540,
                content=txt(
                    "Plan focused work, review with flashcards, and get help "
                    "whenever a difficult topic slows you down.",
                    16,
                    "#C9D2E3",
                    height=1.65,
                ),
            ),
            ft.Container(height=36),
            ft.Column(spacing=18, controls=[_feature_row(*f) for f in FEATURES]),
        ],
    )

    inner = ft.Container(
        padding=ft.Padding.only(left=64, right=56, top=48, bottom=46),
        content=ft.Column(
            spacing=0,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                logo,
                ft.Container(expand=1),
                hero,
                ft.Container(expand=1),
                txt("“Small, focused sessions become meaningful progress.”", 13, "#8F9BB3"),
            ],
        ),
    )

    return ft.Container(
        expand=55,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[NAVY_1, NAVY_2, NAVY_3],
        ),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            expand=True,
            controls=[
                _ring(760, 0),
                _ring(560, 100),
                inner,
            ],
        ),
    )


def auth_panel(page: ft.Page) -> ft.Container:
    from pages import backend

    mode = {"value": "signin"}

    email_field = ft.TextField(
        label="Email address",
        hint_text="e.g. you@university.edu",
        dense=True,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        autofocus=True,
    )
    name_field = ft.TextField(
        label="Full name",
        hint_text="e.g. Jane Doe",
        dense=True,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
    )
    pass_field = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        dense=True,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
    )
    confirm_pass_field = ft.TextField(
        label="Confirm password",
        password=True,
        can_reveal_password=True,
        dense=True,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
    )

    err_text = ft.Text("", color="#DC2626", size=12, visible=False)
    success_text = ft.Text("", color="#16A34A", size=12, visible=False)

    card_container = ft.Container(
        width=420,
        bgcolor=WHITE,
        border_radius=16,
        padding=ft.Padding.symmetric(horizontal=36, vertical=32),
        border=ft.Border.all(1, BORDER_COLOR),
        shadow=ft.BoxShadow(
            blur_radius=18,
            color="#08111827",
            offset=ft.Offset(0, 4),
        ),
    )

    def switch_mode(target: str):
        mode["value"] = target
        err_text.value = ""
        err_text.visible = False
        success_text.value = ""
        success_text.visible = False
        email_field.error_text = None
        pass_field.error_text = None
        confirm_pass_field.error_text = None
        name_field.error_text = None
        render_auth_card()
        page.update()

    def handle_signin(e=None):
        email_field.error_text = None
        pass_field.error_text = None
        err_text.visible = False
        page.update()

        email = (email_field.value or "").strip().lower()
        password = pass_field.value or ""

        has_error = False
        if not email or not EMAIL_RE.match(email):
            email_field.error_text = "Please enter a valid email address."
            has_error = True
        if not password:
            pass_field.error_text = "Please enter your password."
            has_error = True

        if has_error:
            page.update()
            return

        try:
            backend.api_login(email, password)
            page.go("/ai-assistant")
        except ValueError as err:
            err_text.value = str(err)
            err_text.visible = True
            page.update()
        except Exception:
            err_text.value = "Unable to sign in. Please check your credentials or register a new account."
            err_text.visible = True
            page.update()

    def handle_signup(e=None):
        email_field.error_text = None
        name_field.error_text = None
        pass_field.error_text = None
        confirm_pass_field.error_text = None
        err_text.visible = False
        page.update()

        email = (email_field.value or "").strip().lower()
        name = (name_field.value or "").strip()
        pwd = pass_field.value or ""
        confirm_pwd = confirm_pass_field.value or ""

        has_error = False
        if not email or not EMAIL_RE.match(email):
            email_field.error_text = "Please enter a valid email address."
            has_error = True
        if not name:
            name_field.error_text = "Please enter your name."
            has_error = True
        if len(pwd) < MIN_PASSWORD_LENGTH:
            pass_field.error_text = f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
            has_error = True
        if pwd != confirm_pwd:
            confirm_pass_field.error_text = "Passwords do not match."
            has_error = True

        if has_error:
            page.update()
            return

        try:
            backend.api_register(email=email, password=pwd, name=name)
            page.go("/ai-assistant")
        except ValueError as err:
            err_text.value = str(err)
            err_text.visible = True
            page.update()
        except Exception:
            err_text.value = "Registration failed. Please try again with a different email."
            err_text.visible = True
            page.update()

    def render_auth_card():
        is_signin = mode["value"] == "signin"

        title = "Welcome back" if is_signin else "Create your account"
        subtitle = "Sign in to access your notes, flashcards, and timetable." if is_signin else "Start organizing your study routine with Arcadia."
        primary_btn_text = "Sign in" if is_signin else "Create account"
        on_primary_click = handle_signin if is_signin else handle_signup

        fields = [email_field]
        if not is_signin:
            fields.append(name_field)
        fields.append(pass_field)
        if not is_signin:
            fields.append(confirm_pass_field)

        fields_col = ft.Column(spacing=14, controls=fields)

        toggle_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                txt(
                    "Don't have an account?" if is_signin else "Already have an account?",
                    13,
                    MUTED,
                ),
                ft.TextButton(
                    content=txt("Sign up" if is_signin else "Sign in", 13, TEAL, family="Inter SemiBold"),
                    on_click=lambda _: switch_mode("signup" if is_signin else "signin"),
                ),
            ],
        )

        card_container.content = ft.Column(
            spacing=20,
            controls=[
                ft.Column(
                    spacing=6,
                    controls=[
                        txt(title, 22, INK, family="Jakarta Bold"),
                        txt(subtitle, 13, MUTED, height=1.3),
                    ],
                ),
                err_text,
                success_text,
                fields_col,
                ft.FilledButton(
                    content=txt(primary_btn_text, 14, ft.Colors.WHITE, family="Inter SemiBold"),
                    bgcolor=TEAL,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding.symmetric(vertical=16),
                    ),
                    width=420,
                    on_click=on_primary_click,
                ),
                ft.Divider(height=1, color=BORDER_COLOR),
                toggle_row,
            ],
        )

    render_auth_card()

    return ft.Container(
        expand=45,
        bgcolor=PAGE_BG,
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding.all(32),
        content=ft.Column(
            [card_container],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
    )


def get_view(page: ft.Page) -> ft.View:
    return ft.View(
        route="/",
        padding=0,
        bgcolor=PAGE_BG,
        controls=[
            ft.Row(
                [brand_panel(), auth_panel(page)],
                spacing=0,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        ],
    )


def main(page: ft.Page):
    page.title = "Arcadia — Sign in & Sign up"
    page.padding = 0
    page.spacing = 0
    page.bgcolor = PAGE_BG
    page.fonts = FONTS
    page.theme = ft.Theme(font_family="Inter", color_scheme_seed=TEAL)
    page.theme_mode = ft.ThemeMode.LIGHT
    page.add(
        ft.Row(
            [brand_panel(), auth_panel(page)],
            spacing=0,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )
    )


if __name__ == "__main__":
    ft.app(main)
