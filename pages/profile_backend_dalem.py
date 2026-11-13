"""Arcadia - Profile page (Flet 1.x).

Run:  python arcadia_profile.py
Web:  set ARCADIA_WEB=1 and run, then open http://localhost:8550
"""

import os

import flet as ft

# ---------------------------------------------------------------- design tokens
TEAL = "#16756A"          # primary (buttons, avatar, numbers)
TEAL_DARK = "#0F5E55"
TEAL_TEXT = "#14786C"     # accent text
TEAL_SOFT = "#E4F2EF"     # selected nav background
TEAL_TINT = "#EEF7F5"     # hero gradient start
NAVY = "#1B2337"          # logo tile
INK = "#111827"           # headings
TEXT = "#1F2937"          # body text
MUTED = "#6B7280"         # secondary text
SUBTLE = "#9CA3AF"
BORDER = "#E3E8EB"
BORDER_TEAL = "#D5E9E5"
PAGE_BG = "#F7F9FA"
WHITE = "#FFFFFF"
DANGER = "#C0392B"
DANGER_BORDER = "#F1C9C4"
GOAL_BG = "#123B36"
GOAL_TRACK = "#2C5550"
GOAL_BAR = "#6CC9B8"

FONT = "Inter"


def txt(value, size=14, color=TEXT, weight=ft.FontWeight.W_400, spacing=None, **kw):
    style = ft.TextStyle(letter_spacing=spacing) if spacing is not None else None
    return ft.Text(value, size=size, color=color, weight=weight, font_family=FONT,
                   style=style, **kw)


def card(content, padding=28, radius=18, bgcolor=WHITE, border=BORDER, **kw):
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=bgcolor,
        border_radius=radius,
        border=ft.Border.all(1, border) if border else None,
        **kw,
    )


def hover_fill(control, normal, hover):
    def on_hover(e):
        control.bgcolor = hover if e.data in (True, "true") else normal
        control.update()
    control.on_hover = on_hover
    return control


# ---------------------------------------------------------------- logo
def logo_tile(size=44, radius=10):
    """Navy tile with a little white playing card and a red pip."""
    return ft.Container(
        width=size, height=size, bgcolor=NAVY, border_radius=radius,
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(blur_radius=6, color="#33000000", offset=ft.Offset(0, 2)),
        content=ft.Container(
            width=size * 0.36, height=size * 0.5, bgcolor=WHITE,
            border_radius=size * 0.06, alignment=ft.Alignment.CENTER,
            content=ft.Container(width=size * 0.1, height=size * 0.1,
                                 bgcolor="#E5484D", rotate=0.785,
                                 border_radius=1),
        ),
    )


# ---------------------------------------------------------------- sidebar
def build_sidebar(page: ft.Page):
    nav_items = [
        (ft.Icons.AUTO_AWESOME_OUTLINED, "AI Assistant", None),
        (ft.Icons.LAYERS_OUTLINED, "Flashcards", None),
        (ft.Icons.CALENDAR_MONTH_OUTLINED, "Study planner", "To-do · Calendar"),
        (ft.Icons.TIMER_OUTLINED, "Study timer", None),
        ("profile", "Profile", None),
    ]
    selected = {"label": "Profile"}
    nav_column = ft.Column(spacing=4)

    route_map = {
        "AI Assistant": "/ai-assistant",
        "Flashcards": "/flashcards",
        "Study planner": "/studyplanner",
        "Study timer": "/studytimer",
        "Profile": "/profile",
    }

    def nav_icon(icon, active):
        if icon == "profile":
            return ft.Container(
                width=20, height=20, bgcolor=NAVY if not active else "#1B2337",
                border_radius=4, alignment=ft.Alignment.CENTER,
                content=ft.Container(width=7, height=10, bgcolor=WHITE, border_radius=1.5),
            )
        return ft.Icon(icon, size=22, color="#4B5563")

    async def select(label):
        target = route_map.get(label)
        if target and target != page.route:
            await page.push_route(target)
        else:
            selected["label"] = label
            render_nav()
            nav_column.update()

    def render_nav():
        nav_column.controls.clear()
        for icon, label, badge in nav_items:
            active = selected["label"] == label
            row = [
                nav_icon(icon, active),
                txt(label, 17, TEAL_TEXT if active else INK,
                    ft.FontWeight.W_600 if active else ft.FontWeight.W_500),
            ]
            if badge:
                row.append(ft.Container(
                    content=txt(badge, 9, MUTED),
                    bgcolor="#F1F3F5", border_radius=6,
                    padding=ft.Padding.symmetric(horizontal=5, vertical=3),
                ))
            item = ft.Container(
                content=ft.Row(row, spacing=12,
                               vertical_alignment=ft.CrossAxisAlignment.CENTER),
                height=52,
                padding=ft.Padding.only(left=16, right=12),
                border_radius=12,
                bgcolor=TEAL_SOFT if active else None,
                on_click=lambda e, l=label: page.run_task(select, l),
                data=label,
            )
            if not active:
                hover_fill(item, None, "#F3F6F7")
            nav_column.controls.append(item)

    render_nav()

    # recent chats ---------------------------------------------------------
    chats_column = ft.Column(spacing=4)

    def remove_chat(row):
        chats_column.controls.remove(row)
        chats_column.update()

    for title in ["New study chat", "What is E=mc²?", "Help with my I2P ques..."]:
        row = ft.Container(
            height=46,
            padding=ft.Padding.only(left=16, right=16),
            border_radius=10,
        )
        row.content = ft.Row(
            [
                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=20, color="#4B5563"),
                ft.Container(txt(title, 16, MUTED, max_lines=1,
                                 overflow=ft.TextOverflow.ELLIPSIS), expand=True),
                ft.Container(
                    content=ft.Icon(ft.Icons.CLOSE, size=16, color=SUBTLE),
                    on_click=lambda e, r=row: remove_chat(r),
                    padding=2, border_radius=6,
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        hover_fill(row, None, "#F3F6F7")
        chats_column.controls.append(row)

    new_chat_btn = ft.Container(
        content=ft.Row(
            [ft.Icon(ft.Icons.ADD, color=WHITE, size=22),
             txt("New study chat", 16, WHITE, ft.FontWeight.W_600)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=12,
        ),
        height=52, bgcolor=TEAL, border_radius=12,
        shadow=ft.BoxShadow(blur_radius=10, color="#2216756A", offset=ft.Offset(0, 3)),
        on_click=lambda e: page.run_task(page.push_route, "/ai-assistant"),
    )
    hover_fill(new_chat_btn, TEAL, TEAL_DARK)

    user_card = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    width=42, height=42, border_radius=21, bgcolor="#E5ECEB",
                    alignment=ft.Alignment.CENTER,
                    content=txt("JD", 15, INK, ft.FontWeight.W_700),
                ),
                ft.Column(
                    [txt("John Doe", 16, INK, ft.FontWeight.W_500),
                     txt("View profile", 12, MUTED)],
                    spacing=0, alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=14,
        ),
        padding=ft.Padding.symmetric(horizontal=16, vertical=0),
        height=76, bgcolor="#F2F8F7", border_radius=12,
        border=ft.Border.all(1, BORDER_TEAL),
    )

    return ft.Container(
        width=312,
        bgcolor=WHITE,
        border=ft.Border.only(right=ft.BorderSide(1, BORDER)),
        padding=ft.Padding.only(left=20, right=20, top=34, bottom=18),
        content=ft.Column(
            [
                ft.Row([logo_tile(), txt("Arcadia", 26, INK, ft.FontWeight.W_700, spacing=-0.5)],
                       spacing=14),
                ft.Container(height=36),
                new_chat_btn,
                ft.Container(height=26),
                nav_column,
                ft.Container(
                    padding=ft.Padding.only(left=14, top=12, right=20),
                    content=ft.Row(
                        [ft.Icon(ft.Icons.SYNC, size=16, color=MUTED),
                         ft.Container(txt("To-do list and calendar stay in sync", 13, MUTED),
                                      expand=True)],
                        spacing=8, vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                ),
                ft.Container(height=26),
                ft.Container(txt("RECENT CHATS", 14, "#4B5563", ft.FontWeight.W_600, spacing=0.6),
                             padding=ft.Padding.only(left=0, bottom=8)),
                chats_column,
                ft.Container(expand=True),
                user_card,
            ],
            spacing=0,
            expand=True,
        ),
    )


# ---------------------------------------------------------------- main area
def hero_card(page: ft.Page):
    avatar = ft.Container(
        width=100, height=100, border_radius=50, bgcolor=WHITE,
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(blur_radius=18, color="#2216756A", offset=ft.Offset(0, 4)),
        content=ft.Container(
            width=88, height=88, border_radius=44, bgcolor=TEAL,
            alignment=ft.Alignment.CENTER,
            content=txt("JD", 28, WHITE, ft.FontWeight.W_600),
        ),
    )

    async def handle_logout(e):
        await page.push_route("/")

    edit_btn = ft.Container(
        content=txt("Edit profile", 16, WHITE, ft.FontWeight.W_600),
        height=48, padding=ft.Padding.symmetric(horizontal=18),
        bgcolor=TEAL, border_radius=10, alignment=ft.Alignment.CENTER,
    )
    hover_fill(edit_btn, TEAL, TEAL_DARK)

    logout_btn = ft.Container(
        content=txt("Log out", 16, DANGER, ft.FontWeight.W_500),
        height=48, padding=ft.Padding.symmetric(horizontal=19),
        bgcolor=WHITE, border_radius=10, alignment=ft.Alignment.CENTER,
        border=ft.Border.all(1, DANGER_BORDER),
        on_click=handle_logout,
    )
    hover_fill(logout_btn, WHITE, "#FDF3F2")

    return ft.Container(
        content=ft.Row(
            [
                avatar,
                ft.Container(width=20),
                ft.Column(
                    [
                        txt("STUDENT PROFILE", 12, TEAL_TEXT, ft.FontWeight.W_700, spacing=1.6),
                        ft.Container(height=6),
                        txt("John Doe", 32, INK, ft.FontWeight.W_600, spacing=-0.5),
                        ft.Container(height=10),
                        txt("Computer Science · Second year", 15, MUTED),
                    ],
                    spacing=0, expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                edit_btn,
                ft.Container(width=12),
                logout_btn,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(left=36, right=36, top=36, bottom=36),
        border_radius=20,
        border=ft.Border.all(1, BORDER_TEAL),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT, end=ft.Alignment.CENTER_RIGHT,
            colors=[TEAL_TINT, WHITE, WHITE],
            stops=[0.0, 0.55, 1.0],
        ),
    )


def stat_card(value, title, sub):
    return card(
        ft.Row(
            [
                txt(value, 28, TEAL_TEXT, ft.FontWeight.W_500),
                ft.Column(
                    [txt(title, 13, INK, ft.FontWeight.W_600),
                     txt(sub, 11, MUTED)],
                    spacing=2, alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=22),
        radius=16, height=102, expand=True,
    )


def info_field(label, value, divider=True):
    return ft.Container(
        content=ft.Column(
            [txt(label, 12, MUTED), txt(value, 15, INK, ft.FontWeight.W_500)],
            spacing=10,
        ),
        padding=ft.Padding.only(top=22, bottom=20),
        border=ft.Border.only(bottom=ft.BorderSide(1, BORDER)) if divider else None,
        expand=True,
    )


def personal_info_card():
    def pair(a, b):
        return ft.Row([a, ft.Container(width=38), b],
                      vertical_alignment=ft.CrossAxisAlignment.START, spacing=0)

    return card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [txt("Personal information", 20, INK, ft.FontWeight.W_600),
                             txt("Keep your account and academic details up to date.", 12, MUTED)],
                            spacing=12, expand=True,
                        ),
                        ft.Container(
                            content=txt("Member since October 2026", 11, MUTED),
                            bgcolor="#F2F4F5", border_radius=14,
                            padding=ft.Padding.symmetric(horizontal=11, vertical=6),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Container(height=20),
                ft.Divider(height=1, thickness=1, color=BORDER),
                pair(info_field("Full name", "John Doe"),
                     info_field("Email address", "john.doe@example.com")),
                pair(info_field("School", "Arcadia University"),
                     info_field("Major or course", "Computer Science")),
                pair(info_field("Year of study", "Second year"),
                     info_field("Daily study goal", "90 minutes")),
                ft.Container(
                    content=ft.Column(
                        [txt("About me", 12, MUTED),
                         ft.Container(height=14),
                         txt("Building consistent study habits and working toward "
                             "stronger problem-solving skills.", 15, TEXT)],
                        spacing=0,
                    ),
                    padding=ft.Padding.only(top=26, bottom=4),
                ),
            ],
            spacing=0,
        ),
        padding=ft.Padding.only(left=30, right=30, top=30, bottom=24),
        radius=18, expand=True,
    )


def pref_row(title, subtitle, value):
    return ft.Container(
        content=ft.Row(
            [
                ft.Column([txt(title, 13, INK, ft.FontWeight.W_600),
                           txt(subtitle, 11, MUTED)], spacing=6, expand=True),
                ft.Switch(
                    value=value,
                    active_color=WHITE,
                    active_track_color=TEAL,
                    inactive_thumb_color=WHITE,
                    inactive_track_color="#D1D5DB",
                    track_outline_color={ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(top=20, bottom=20),
        border=ft.Border.only(top=ft.BorderSide(1, BORDER)),
    )


def preferences_card():
    return card(
        ft.Column(
            [
                txt("Study preferences", 20, INK, ft.FontWeight.W_600),
                ft.Container(height=12),
                txt("Choose how Arcadia keeps you on track.", 12, MUTED),
                ft.Container(height=20),
                pref_row("Study reminders", "Receive reminders for planned tasks.", True),
                pref_row("Weekly summary", "Get a recap of your study activity.", True),
            ],
            spacing=0,
        ),
        padding=ft.Padding.only(left=30, right=28, top=30, bottom=8),
        radius=18,
    )


def daily_goal_card(done=65, goal=90):
    return ft.Container(
        content=ft.Column(
            [
                txt("DAILY GOAL", 11, "#B9D6D1", ft.FontWeight.W_600, spacing=1.5),
                ft.Container(height=18),
                txt(f"{goal} min", 34, WHITE, ft.FontWeight.W_700, spacing=-0.5),
                ft.Container(height=14),
                txt("Keep a steady routine by meeting your focus target each day.",
                    12, "#E3EFED", ft.FontWeight.W_500),
                ft.Container(height=22),
                ft.ProgressBar(value=done / goal, color=GOAL_BAR, bgcolor=GOAL_TRACK,
                               bar_height=6, border_radius=3),
                ft.Container(height=12),
                txt(f"{done} of {goal} minutes today", 11, "#B9D6D1"),
            ],
            spacing=0,
        ),
        padding=ft.Padding.only(left=30, right=30, top=36, bottom=30),
        bgcolor=GOAL_BG,
        border_radius=18,
    )


def build_main(page: ft.Page):
    header = ft.Container(
        content=ft.Column(
            [txt("Profile", 24, INK, ft.FontWeight.W_600, spacing=-0.3),
             txt("Your account and study preferences", 16, MUTED)],
            spacing=6,
        ),
        padding=ft.Padding.only(left=48, top=24, bottom=24),
        bgcolor=WHITE,
        border=ft.Border.only(bottom=ft.BorderSide(1, BORDER)),
    )

    body = ft.Column(
        [
            ft.Container(
                content=ft.Column(
                    [
                        hero_card(page),
                        ft.Row(
                            [stat_card("7", "Study sessions", "This week"),
                             stat_card("4.5h", "Focus time", "This week"),
                             stat_card("5", "Active decks", "Flashcards"),
                             stat_card("68%", "Tasks completed", "This month")],
                            spacing=20,
                        ),
                        ft.Row(
                            [
                                personal_info_card(),
                                ft.Container(
                                    width=442,
                                    content=ft.Column(
                                        [preferences_card(), daily_goal_card()],
                                        spacing=24,
                                    ),
                                ),
                            ],
                            spacing=24,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                    ],
                    spacing=24,
                ),
                padding=ft.Padding.only(left=48, right=48, top=24, bottom=40),
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    return ft.Container(
        content=ft.Column([header, body], spacing=0, expand=True,
                          horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
        bgcolor=PAGE_BG,
        expand=True,
    )


# ---------------------------------------------------------------- app
def main(page: ft.Page):
    page.title = "Arcadia · Profile"
    page.padding = 0
    page.spacing = 0
    page.bgcolor = WHITE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = {
        FONT: "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
    }
    page.theme = ft.Theme(font_family=FONT, color_scheme_seed=TEAL)
    page.window.width = 1920
    page.window.height = 1000
    page.window.min_width = 1280
    page.window.min_height = 720

    page.add(
        ft.Row(
            [build_sidebar(page), build_main(page)],
            spacing=0,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )
    )


def get_view(page: ft.Page) -> ft.View:
    return ft.View(
        route="/profile",
        padding=0,
        bgcolor=WHITE,
        controls=[
            ft.Row(
                [build_sidebar(page), build_main(page)],
                spacing=0,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        ],
    )


if __name__ == "__main__":
    if os.environ.get("ARCADIA_WEB"):
        ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550)
    else:
        ft.run(main)