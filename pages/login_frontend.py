"""Arcadia sign-in page — frontend only, built with Flet. One file, no backend.

Run it:  python login_frontend.py

The form only checks the input on screen (valid email, password of at
least 6 characters). Nothing is saved or sent anywhere. To connect a
real backend later, replace the code marked "CONNECT YOUR BACKEND HERE".
"""
import asyncio
import re

import flet as ft
import flet.canvas as cv

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
MIN_PASSWORD_LENGTH = 6

# ======================================================================
# DESIGN TOKENS: colours, fonts, static content
# ======================================================================
NAVY_1, NAVY_2, NAVY_3 = "#1b2a4e", "#131d3d", "#0f1834"
TEAL, TEAL_DARK, TEAL_LIGHT = "#167a6e", "#116258", "#5fcfbf"
INK, MUTED, BORDER, PAGE_BG = "#0f1a2e", "#5b6678", "#dfe4ea", "#f7f9fb"
ERROR_RED = "#d64545"

# Static font files (one family name per weight so Flutter picks the exact cut)
FONT_CDN = "https://cdn.jsdelivr.net/fontsource/fonts"
FONTS = {
    "Inter": f"{FONT_CDN}/inter@latest/latin-400-normal.ttf",
    "Inter Medium": f"{FONT_CDN}/inter@latest/latin-500-normal.ttf",
    "Inter SemiBold": f"{FONT_CDN}/inter@latest/latin-600-normal.ttf",
    "Jakarta Bold": f"{FONT_CDN}/plus-jakarta-sans@latest/latin-700-normal.ttf",
}

FEATURES = [
    ("01", "Plan with clarity", "Keep tasks and study sessions in one place."),
    ("02", "Practice actively", "Turn your material into decks and quizzes."),
    ("03", "Stay consistent", "Build routines with focused timers and goals."),
]


# ======================================================================
# SMALL REUSABLE PIECES
# ======================================================================


def txt(value, size=14, color=INK, font="Inter", spacing=None, height=None, align=None, weight=None):
    return ft.Text(
        value,
        text_align=align,
        style=ft.TextStyle(
            size=size, color=color, font_family=font, letter_spacing=spacing,
            height=height, weight=weight,
        ),
    )


def eyebrow(value, color, size=13):
    return txt(value.upper(), size=size, color=color, font="Inter SemiBold", spacing=size * 0.15)


def field_label(value):
    return ft.Container(padding=ft.Padding.only(bottom=8),
                        content=txt(value, 13.5, "#1c2638", "Inter SemiBold"))


def _outline(color, width):
    return ft.OutlineInputBorder(side=ft.BorderSide(width, color), border_radius=11)


def text_input(hint, **kwargs):
    return ft.TextField(
        hint_text=hint,
        hint_style=ft.TextStyle(color="#8a94a3", size=15, font_family="Inter"),
        text_style=ft.TextStyle(color=INK, size=15, font_family="Inter"),
        filled=True,
        fill_color="#f8fafb",
        focused_bgcolor=ft.Colors.WHITE,
        border={
            ft.ControlState.DEFAULT: _outline(BORDER, 1),
            ft.ControlState.FOCUSED: _outline(TEAL, 1.5),
            ft.ControlState.ERROR: _outline(ERROR_RED, 1),
        },
        cursor_color=TEAL,
        content_padding=ft.Padding.symmetric(horizontal=15, vertical=17),
        error_style=ft.TextStyle(color="#c53b3b", size=12.5, font_family="Inter"),
        **kwargs,
    )


def primary_button(label_control, **kwargs):
    return ft.FilledButton(
        content=label_control, height=55,
        style=ft.ButtonStyle(
            bgcolor={ft.ControlState.HOVERED: TEAL_DARK, ft.ControlState.DEFAULT: TEAL},
            shape=ft.RoundedRectangleBorder(radius=11),
            elevation=0,
        ),
        **kwargs,
    )


# ======================================================================
# LEFT SIDE: brand panel
# ======================================================================


def _feature_row(num, title, desc):
    return ft.Row(
        spacing=17,
        controls=[
            ft.Container(
                width=39, height=39, border_radius=9,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ft.Colors.WHITE)),
                alignment=ft.Alignment.CENTER,
                content=txt(num, 12, "#e8edf5", "Inter SemiBold"),
            ),
            ft.Column(
                spacing=1,
                controls=[
                    txt(title, 14, ft.Colors.WHITE, "Inter SemiBold"),
                    txt(desc, 13, "#c3cbdb"),
                ],
            ),
        ],
    )


def _ring(size, offset):
    return ft.Container(
        width=size, height=size, right=-300 + offset, bottom=-330 + offset,
        shape=ft.BoxShape.CIRCLE,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.WHITE)),
    )


def brand_panel():
    # Website name only (no logo icon)
    logo = ft.Container(
        height=50,
        alignment=ft.Alignment.CENTER_LEFT,
        content=txt("Arcadia", 27, ft.Colors.WHITE, "Jakarta Bold", spacing=-0.5),
    )

    hero = ft.Column(
        spacing=0,
        controls=[
            eyebrow("Your study space", TEAL_LIGHT),
            ft.Container(height=26),
            ft.Container(
                width=600,
                content=txt("Make every study session count.", 68, ft.Colors.WHITE,
                            "Jakarta Bold", spacing=-3, height=1.12),
            ),
            ft.Container(height=26),
            ft.Container(
                width=560,
                content=txt("Plan focused work, review with flashcards, and get help "
                            "whenever a difficult topic slows you down.",
                            18, "#c9d2e3", height=1.68),
            ),
            ft.Container(height=44),
            ft.Column(spacing=20, controls=[_feature_row(*f) for f in FEATURES]),
        ],
    )

    content = ft.Container(
        padding=ft.Padding.only(left=92, right=60, top=48, bottom=46),
        content=ft.Column(
            spacing=0,
            controls=[
                logo,
                ft.Container(expand=1),
                hero,
                ft.Container(expand=1),
                txt("“Small, focused sessions become meaningful progress.”", 12.5, "#8f9bb3"),
            ],
        ),
    )

    return ft.Container(
        expand=45,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER,
            colors=[NAVY_1, NAVY_2, NAVY_3], stops=[0.0, 0.6, 1.0],
        ),
        content=ft.Stack(
            expand=True,
            controls=[
                # reddish glow near the top
                ft.Container(
                    expand=True, left=0, top=0, right=0, bottom=0,
                    gradient=ft.RadialGradient(
                        center=ft.Alignment(0.56, -0.74), radius=0.75,
                        colors=[ft.Colors.with_opacity(0.55, "#781c3a"),
                                ft.Colors.with_opacity(0.22, "#501a3c"),
                                ft.Colors.with_opacity(0.0, NAVY_1)],
                        stops=[0.0, 0.3, 0.75],
                    ),
                ),
                _ring(720, 0),
                _ring(504, 108),
                ft.Container(left=0, top=0, right=0, bottom=0, content=content),
            ],
        ),
    )


# ======================================================================
# RIGHT SIDE: sign-in card
# ======================================================================


def _grid_background(cell=52, w=2600, h=1800):
    paint = ft.Paint(color=ft.Colors.with_opacity(0.035, INK), stroke_width=1)
    shapes = [cv.Line(x, 0, x, h, paint) for x in range(0, w, cell)]
    shapes += [cv.Line(0, y, w, y, paint) for y in range(0, h, cell)]
    return cv.Canvas(shapes=shapes, width=w, height=h, left=0, top=0)


def form_panel(page: ft.Page):
    card = ft.Container(
        width=528,
        bgcolor=ft.Colors.WHITE,
        border_radius=24,
        border=ft.Border.all(1, "#e6eaef"),
        padding=ft.Padding.only(left=46, right=46, top=50, bottom=40),
        shadow=[
            ft.BoxShadow(blur_radius=60, spread_radius=-24, offset=ft.Offset(0, 24),
                         color=ft.Colors.with_opacity(0.14, INK)),
            ft.BoxShadow(blur_radius=6, offset=ft.Offset(0, 2),
                         color=ft.Colors.with_opacity(0.03, INK)),
        ],
    )

    # ---------------------------------------------------------- sign-in view
    email = text_input("you@example.com", autofocus=True,
                       keyboard_type=ft.KeyboardType.EMAIL)
    toggle_label = txt("Show", 13, TEAL, "Inter SemiBold")
    password = text_input("Enter your password", password=True)
    password.suffix_icon = ft.Container(
        content=toggle_label, width=62, padding=ft.Padding.only(right=15),
        alignment=ft.Alignment.CENTER_RIGHT, on_click=lambda e: toggle_password(),
    )
    remember = ft.Checkbox(
        label="Remember me", value=True,
        label_style=ft.TextStyle(size=13, color=MUTED, font_family="Inter"),
        active_color=TEAL, check_color=ft.Colors.WHITE,
        shape=ft.RoundedRectangleBorder(radius=4),
        border_side=ft.BorderSide(1.5, "#c3cbd5"),
    )
    submit_label = txt("Sign in", 15, ft.Colors.WHITE, "Inter SemiBold")
    submit = primary_button(submit_label)

    def toggle_password():
        password.password = not password.password
        toggle_label.value = "Show" if password.password else "Hide"
        page.update()

    def clear_error(field):
        if field.error:
            field.error = None
            page.update()

    email.on_change = lambda e: clear_error(email)
    password.on_change = lambda e: clear_error(password)

    async def handle_sign_in(e):
        email_value = (email.value or "").strip()
        password_value = password.value or ""

        # Check the input on screen
        email.error = None if EMAIL_RE.match(email_value) else "Please enter a valid email address."
        password.error = (None if len(password_value) >= MIN_PASSWORD_LENGTH
                          else f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        if email.error or password.error:
            page.update()
            return

        submit.disabled = True
        submit_label.value = "Signing in…"
        page.update()

        # CONNECT YOUR BACKEND HERE: replace this pause with a real sign-in call
        await asyncio.sleep(0.6)

        submit.disabled = False
        submit_label.value = "Sign in"
        show_welcome(email_value)
        page.update()

    submit.on_click = handle_sign_in
    password.on_submit = handle_sign_in
    email.on_submit = lambda e: password.focus()

    link_style = ft.TextStyle(size=13, color=TEAL, font_family="Inter SemiBold")

    sign_in_view = ft.Column(
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            eyebrow("Welcome back", TEAL, 12.5),
            ft.Container(height=18),
            txt("Sign in to your account", 33, INK, "Jakarta Bold", spacing=-1.1),
            ft.Container(height=14),
            txt("Continue where you left off and get back to studying.", 14, MUTED),
            ft.Container(height=36),
            field_label("Email address"),
            email,
            ft.Container(height=22),
            field_label("Password"),
            password,
            ft.Container(height=14),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Container(margin=ft.Margin.only(left=-10), content=remember),
                    ft.Text(spans=[ft.TextSpan("Forgot password?", style=link_style)]),
                ],
            ),
            ft.Container(height=16),
            submit,
            ft.Container(height=24),
            ft.Container(
                bgcolor="#eef7f5", border_radius=11,
                padding=ft.Padding.symmetric(vertical=13, horizontal=14),
                content=ft.Column(spacing=3, controls=[
                    txt("Design preview", 12, TEAL, "Inter SemiBold"),
                    txt("Use any valid email and a password of at least 6 characters.", 11.5, "#4e5a6b"),
                ]),
            ),
            ft.Container(height=28),
            ft.Text(
                text_align=ft.TextAlign.CENTER,
                spans=[
                    ft.TextSpan("New to Arcadia? ",
                                style=ft.TextStyle(size=13, color=MUTED, font_family="Inter")),
                    ft.TextSpan("Create an account", style=link_style),
                ],
            ),
        ],
    )

    # ---------------------------------------------------------- signed-in view
    welcome_text = txt("", 14, MUTED)

    def sign_out(e):
        password.value = ""
        card.content = sign_in_view
        page.update()

    welcome_view = ft.Column(
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            eyebrow("Signed in", TEAL, 12.5),
            ft.Container(height=18),
            txt("Welcome back", 33, INK, "Jakarta Bold", spacing=-1.1),
            ft.Container(height=14),
            welcome_text,
            ft.Container(height=30),
            primary_button(txt("Sign out", 15, ft.Colors.WHITE, "Inter SemiBold"), on_click=sign_out),
        ],
    )

    def show_welcome(user_email):
        welcome_text.value = f"You're signed in as {user_email}."
        card.content = welcome_view

    card.content = sign_in_view

    centered = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(padding=ft.Padding.symmetric(vertical=48, horizontal=16), content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=22,
                controls=[
                    card,
                    txt("By continuing, you agree to Arcadia’s Terms of Service and Privacy Policy.",
                        10.5, "#8e98a7", align=ft.TextAlign.CENTER),
                ],
            )),
        ],
    )

    return ft.Container(
        expand=55,
        bgcolor=PAGE_BG,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            expand=True,
            controls=[
                _grid_background(),
                ft.Container(left=0, top=0, right=0, bottom=0, content=centered),
            ],
        ),
    )


# ======================================================================
# PAGE: puts everything together
# ======================================================================

def main(page: ft.Page):
    page.title = "Arcadia — Sign in"
    page.padding = 0
    page.spacing = 0
    page.bgcolor = PAGE_BG
    page.fonts = FONTS
    page.theme = ft.Theme(font_family="Inter", color_scheme_seed=TEAL)
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1440
    page.window.height = 900
    page.window.min_width = 420
    page.window.min_height = 640

    left = brand_panel()
    right = form_panel(page)

    def on_resize(e=None):
        # Hide the brand panel on narrow windows
        left.visible = (page.width or 1440) >= 900
        page.update()

    page.on_resize = on_resize
    page.add(ft.Row(expand=True, spacing=0, controls=[left, right],
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH))
    on_resize()


if __name__ == "__main__":
    import sys

    if "--web" in sys.argv:  # optional: python login_frontend.py --web
        ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)
    else:
        ft.run(main)
