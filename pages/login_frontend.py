"""Arcadia sign-in page — frontend only, built with Flet."""
import asyncio
import re

import flet as ft
import flet.canvas as cv

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
MIN_PASSWORD_LENGTH = 6

# ---------------------------------------------------------------- design tokens
TEAL = "#16756A"
TEAL_LIGHT = "#6CC9B8"
NAVY_1 = "#111827"
NAVY_2 = "#162033"
NAVY_3 = "#1B2337"
INK = "#111827"
MUTED = "#6B7280"
PAGE_BG = "#F7F9FA"

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
def txt(value, size, color, family="Inter", spacing=None, height=None, align=None):
    weight = (
        ft.FontWeight.W_700
        if "Bold" in family and "Semi" not in family
        else ft.FontWeight.W_600
        if "SemiBold" in family
        else ft.FontWeight.W_400
    )
    style = ft.TextStyle(letter_spacing=spacing, height=height) if (spacing is not None or height is not None) else None
    return ft.Text(
        value,
        size=size,
        color=color,
        font_family=family,
        weight=weight,
        style=style,
        text_align=align,
    )


def eyebrow(label, color, size=12):
    return txt(label.upper(), size, color, "Inter SemiBold", spacing=1.6)


def field_label(label):
    return ft.Container(
        padding=ft.Padding.only(bottom=8),
        content=txt(label, 13, INK, "Inter SemiBold"),
    )


def text_input(hint, autofocus=False, keyboard_type=None, password=False):
    return ft.TextField(
        hint_text=hint,
        autofocus=autofocus,
        keyboard_type=keyboard_type,
        password=password,
        text_style=ft.TextStyle(size=14, color=INK, font_family="Inter"),
        hint_style=ft.TextStyle(size=14, color="#9CA3AF", font_family="Inter"),
        bgcolor="#F9FAFB",
        border_color="#D7DEE6",
        focused_border_color=TEAL,
        border_radius=11,
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=15),
    )


def primary_button(content, on_click=None):
    return ft.Button(
        content=content,
        on_click=on_click,
        height=48,
        bgcolor=TEAL,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=11),
            elevation=0,
        ),
    )


# ======================================================================
# LEFT SIDE: brand panel
# ======================================================================


def _feature_row(num, title, desc):
    return ft.Row(
        spacing=14,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
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
                content=txt(
                    "Make every study session count.",
                    68,
                    ft.Colors.WHITE,
                    "Jakarta Bold",
                    spacing=-3,
                    height=1.12,
                ),
            ),
            ft.Container(height=26),
            ft.Container(
                width=560,
                content=txt(
                    "Plan focused work, review with flashcards, and get help "
                    "whenever a difficult topic slows you down.",
                    18,
                    "#c9d2e3",
                    height=1.68,
                ),
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
        expand=45