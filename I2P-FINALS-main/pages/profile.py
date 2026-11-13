"""Arcadia - Profile page (Flet 1.x).

Run:  python arcadia_profile.py
Web:  set ARCADIA_WEB=1 and run, then open http://localhost:8550
"""

from __future__ import annotations

import os

import flet as ft

from styles import (
    TEAL,
    TEAL_DARK,
    TEAL_TEXT,
    TEAL_SOFT,
    TEAL_TINT,
    NAVY,
    INK,
    TEXT,
    MUTED,
    SUBTLE,
    BORDER,
    BORDER_TEAL,
    PAGE_BG,
    WHITE,
)
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
    from pages.sidebar import build_unified_sidebar
    return build_unified_sidebar(page=page, active_tab="profile")


# ---------------------------------------------------------------- main area
def hero_card(page: ft.Page, prof: dict | None = None, on_edit=None):
    from pages import backend
    p = prof or backend.api_get_user_profile()
    name = p.get("name", "John Doe")
    parts = [w[0].upper() for w in name.split() if w]
    initials = "".join(parts[:2]) or "JD"
    major_year = f"{p.get('major', 'Computer Science')} · {p.get('year', 'Second year')}"

    avatar = ft.Container(
        width=100, height=100, border_radius=50, bgcolor=WHITE,
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(blur_radius=18, color="#2216756A", offset=ft.Offset(0, 4)),
        content=ft.Container(
            width=88, height=88, border_radius=44, bgcolor=TEAL,
            alignment=ft.Alignment.CENTER,
            content=txt(initials, 28, WHITE, ft.FontWeight.W_600),
        ),
    )

    def handle_logout(e):
        try:
            from pages import backend, study_timer
            backend.CURRENT_CHAT_ID = None
            study_timer.reset_timer_state()
        except Exception:
            pass
        page.go("/")

    edit_btn = ft.Container(
        content=txt("Edit profile", 16, WHITE, ft.FontWeight.W_600),
        height=48, padding=ft.Padding.symmetric(horizontal=18),
        bgcolor=TEAL, border_radius=10, alignment=ft.Alignment.CENTER,
        on_click=on_edit,
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
                        txt(name, 32, INK, ft.FontWeight.W_600, spacing=-0.5),
                        ft.Container(height=10),
                        txt(major_year, 15, MUTED),
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


def personal_info_card(prof: dict | None = None):
    from pages import backend
    p = prof or backend.api_get_user_profile()

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
                            content=txt(f"Member since {p.get('member_since', 'October 2026')}", 11, MUTED),
                            bgcolor="#F2F4F5", border_radius=14,
                            padding=ft.Padding.symmetric(horizontal=11, vertical=6),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Container(height=20),
                ft.Divider(height=1, thickness=1, color=BORDER),
                pair(info_field("Full name", p.get("name", "John Doe")),
                     info_field("Email address", p.get("email", "john.doe@example.com"))),
                pair(info_field("School", p.get("school", "Arcadia University")),
                     info_field("Major or course", p.get("major", "Computer Science"))),
                pair(info_field("Year of study", p.get("year", "Second year")),
                     info_field("Daily study goal", f"{p.get('daily_goal_min', 90)} minutes")),
                ft.Container(
                    content=ft.Column(
                        [txt("About me", 12, MUTED),
                         ft.Container(height=14),
                         txt(p.get("bio", "Building consistent study habits and working toward stronger problem-solving skills."), 15, TEXT)],
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


def pref_row(title, subtitle, value, key_name=None):
    from pages import backend

    def on_toggle(e):
        if key_name:
            try:
                backend.api_update_user_profile({key_name: bool(e.control.value)})
            except Exception:
                pass

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
                    on_change=on_toggle,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(top=20, bottom=20),
        border=ft.Border.only(top=ft.BorderSide(1, BORDER)),
    )


def preferences_card(prof: dict | None = None):
    from pages import backend
    p = prof or backend.api_get_user_profile()
    return card(
        ft.Column(
            [
                txt("Study preferences", 20, INK, ft.FontWeight.W_600),
                ft.Container(height=12),
                txt("Choose how Arcadia keeps you on track.", 12, MUTED),
                ft.Container(height=20),
                pref_row("Study reminders", "Receive reminders for planned tasks.", p.get("reminders", True), "reminders"),
                pref_row("Weekly summary", "Get a recap of your study activity.", p.get("weekly_summary", True), "weekly_summary"),
            ],
            spacing=0,
        ),
        padding=ft.Padding.only(left=30, right=28, top=30, bottom=8),
        radius=18,
    )


def daily_goal_card(done=0, goal=90):
    ratio = min(1.0, done / goal) if goal > 0 else 0.0
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
                ft.ProgressBar(value=ratio, color=GOAL_BAR, bgcolor=GOAL_TRACK,
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
    from pages import backend
    prof = backend.api_get_user_profile()
    stats = backend.api_get_user_stats()
    body_host = ft.Container(expand=True)

    active_dlg: list[ft.AlertDialog] = []

    def close_edit_dialog(e=None):
        if active_dlg:
            d = active_dlg.pop()
            d.open = False
            try:
                page.close(d)
            except Exception:
                pass
            try:
                page.pop_dialog(d)
            except Exception:
                pass
            try:
                d.update()
            except Exception:
                pass
            try:
                page.update()
            except Exception:
                pass

    def open_edit_dialog(e=None):
        name_tf = ft.TextField(label="Full name", value=prof.get("name", "Student"))
        email_tf = ft.TextField(label="Email address", value=prof.get("email", ""))
        school_tf = ft.TextField(label="School", value=prof.get("school", "Arcadia University"))
        major_tf = ft.TextField(label="Major or course", value=prof.get("major", "Computer Science"))
        year_tf = ft.TextField(label="Year of study", value=prof.get("year", "First year"))
        goal_tf = ft.TextField(label="Daily goal (minutes)", value=str(prof.get("daily_goal_min", 90)))
        bio_tf = ft.TextField(label="About me", value=prof.get("bio", ""), multiline=True)

        def save_profile(_):
            nonlocal prof, stats
            try:
                goal_val = int(goal_tf.value or 90)
            except ValueError:
                goal_val = 90
            new_name = (name_tf.value or "Student").strip()
            updates = {
                "name": new_name,
                "email": (email_tf.value or "").strip(),
                "school": (school_tf.value or "").strip(),
                "major": (major_tf.value or "").strip(),
                "year": (year_tf.value or "").strip(),
                "daily_goal_min": goal_val,
                "bio": (bio_tf.value or "").strip(),
            }
            prof = backend.api_update_user_profile(updates)
            stats = backend.api_get_user_stats()
            close_edit_dialog()
            render_body()
            try:
                from pages import sidebar
                sidebar.refresh_all_sidebars()
            except Exception:
                pass
            page.update()

        dlg = ft.AlertDialog(
            title=txt("Edit Profile", 20, INK, ft.FontWeight.W_600),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    [name_tf, email_tf, school_tf, major_tf, year_tf, goal_tf, bio_tf],
                    spacing=10,
                    tight=True,
                ),
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_edit_dialog),
                ft.FilledButton("Save Changes", bgcolor=TEAL, color=WHITE, on_click=save_profile),
            ],
        )
        active_dlg.clear()
        active_dlg.append(dlg)
        page.show_dialog(dlg)

    def render_body():
        body_host.content = ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            hero_card(page, prof, on_edit=open_edit_dialog),
                            ft.Row(
                                [stat_card(str(stats.get("sessions_this_week", 0)), "Study sessions", "This week"),
                                 stat_card(str(stats.get("focus_hours_str", "0.0h")), "Focus time", "This week"),
                                 stat_card(str(stats.get("active_decks", 0)), "Active decks", "Flashcards"),
                                 stat_card(str(stats.get("tasks_completed_pct", "0%")), "Tasks completed", "This month")],
                                spacing=20,
                            ),
                            ft.Row(
                                [
                                    personal_info_card(prof),
                                    ft.Container(
                                        width=442,
                                        content=ft.Column(
                                            [
                                                preferences_card(prof),
                                                daily_goal_card(
                                                    done=stats.get("done_today_min", prof.get("done_today_min", 0)),
                                                    goal=stats.get("daily_goal_min", prof.get("daily_goal_min", 90)),
                                                ),
                                            ],
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

    render_body()

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

    return ft.Container(
        content=ft.Column([header, body_host], spacing=0, expand=True,
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
        ft.app(main, view=ft.AppView.WEB_BROWSER, port=8550)
    else:
        ft.app(main)
