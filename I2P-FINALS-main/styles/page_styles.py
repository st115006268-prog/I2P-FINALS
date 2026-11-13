"""Arcadia Page Styles & Component Helpers."""
from __future__ import annotations

from typing import Optional
import flet as ft
from .theme import BORDER_COLOR, PRIMARY_TEAL, WHITE, PAGE_BG, NAVY

# Common BoxShadows
CARD_SHADOW = ft.BoxShadow(
    blur_radius=6,
    color="#08111827",
    offset=ft.Offset(0, 2),
)

MODAL_SHADOW = ft.BoxShadow(
    blur_radius=20,
    color="#15000000",
    offset=ft.Offset(0, 6),
)

# Border Radiuses
RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 16
RADIUS_FULL = 999


def card_container(content: ft.Control, **kwargs) -> ft.Container:
    """Helper for standard white rounded cards with soft borders."""
    return ft.Container(
        bgcolor=kwargs.pop("bgcolor", WHITE),
        border=kwargs.pop("border", ft.Border.all(1, BORDER_COLOR)),
        border_radius=kwargs.pop("border_radius", RADIUS_LG),
        padding=kwargs.pop("padding", 24),
        shadow=kwargs.pop("shadow", CARD_SHADOW),
        content=content,
        **kwargs,
    )


LOGO_SVG = """<svg viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg">
<rect width="44" height="44" rx="9" fill="#1d2840"/>
<rect x="13.5" y="10" width="15" height="22" rx="2.4" fill="#d9363e" transform="rotate(-8 21 21)"/>
<rect x="15.5" y="11" width="15" height="22" rx="2.4" fill="#ffffff"/>
<path d="M23 17.2c1.6 1.9 3.6 3.1 3.6 4.9 0 1.2-1 2-2 2-.6 0-1.1-.3-1.4-.6l.5 2h-1.4l.5-2c-.3.3-.8.6-1.4.6-1 0-2-.8-2-2 0-1.8 2-3 3.6-4.9z" fill="#1d2840"/>
</svg>"""


def arcadia_logo(size: float = 44) -> ft.Container:
    """Official Arcadia playing card brand mark used across navigation and login."""
    k = size / 44.0
    return ft.Container(
        width=size,
        height=size,
        bgcolor=NAVY,
        border_radius=max(4, 10 * k),
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(blur_radius=6, color="#33111827", offset=ft.Offset(0, 2)) if size >= 36 else None,
        content=ft.Container(
            width=18 * k,
            height=26 * k,
            bgcolor=WHITE,
            border_radius=max(2, 3 * k),
            alignment=ft.Alignment.CENTER,
            border=ft.Border.all(max(1, 1.2 * k), "#E5484D"),
            content=ft.Text("♠", size=max(8, 11 * k), color=NAVY, weight=ft.FontWeight.BOLD),
        ),
    )

