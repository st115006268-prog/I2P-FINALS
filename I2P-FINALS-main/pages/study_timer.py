"""Arcadia - Study timer page (front end only), built with Flet.

Requirements:  pip install flet
Run:           python studytimer_backend_dalem.py          (desktop window)
               flet run --web studytimer_backend_dalem.py  (in the browser)
"""
from __future__ import annotations

import asyncio

import flet as ft

from styles import (
    PRIMARY_TEAL as PRIMARY,
    TEAL_HOVER as PRIMARY_HOVER,
    TEAL_SOFT as PRIMARY_SOFT,
    TEXT,
    TEXT_MUTED,
    BORDER,
    INPUT_BORDER,
    BG,
    SURFACE,
    NAVY,
)
PRIMARY_SOFT_TEXT = "#5FA69B"
RING_TRACK = "#E3EFEC"

PRESETS = [10, 15, 25, 45]
MAX_MINUTES = 180
DEFAULT_HINT = "Choose a preset or enter your own session length."


def fmt(seconds: int) -> str:
    m, s = divmod(max(0, seconds), 60)
    return f"{m:02d}:{s:02d}"


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
def logo(size: int = 44) -> ft.Container:
    k = size / 44
    return ft.Container(
        width=size, height=size, bgcolor=NAVY, border_radius=10 * k,
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=18 * k, height=26 * k, bgcolor=SURFACE, border_radius=3 * k,
            alignment=ft.Alignment.CENTER,
            border=ft.Border.all(max(1, 1.2 * k), "#E5484D"),
            content=ft.Text("♠", size=11 * k, color=NAVY, weight=ft.FontWeight.BOLD),
        ),
    )


def hoverable(container: ft.Container, normal: str | None, hover: str) -> ft.Container:
    def on_hover(e):
        container.bgcolor = hover if e.data in (True, "true") else normal
        container.update()
    container.on_hover = on_hover
    return container


def nav_item(label: str, icon, active: bool = False, badge: str | None = None,
             icon_control: ft.Control | None = None, on_click=None) -> ft.Container:
    color = PRIMARY if active else TEXT
    row = [
        icon_control or ft.Icon(icon, size=21, color=PRIMARY if active else "#3C6F69"),
        ft.Text(label, size=17, color=color, no_wrap=True,
                weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_500),
    ]
    if badge:
        row.append(ft.Container(
            content=ft.Text(badge, size=10, color=TEXT_MUTED, no_wrap=True),
            bgcolor="#F3F4F6", border=ft.Border.all(1, BORDER), border_radius=999,
            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
        ))
    normal = PRIMARY_SOFT if active else None
    return hoverable(ft.Container(
        content=ft.Row(row, spacing=12),
        height=53, padding=ft.Padding.symmetric(horizontal=15),
        border_radius=10, bgcolor=normal,
        on_click=on_click,
        ink=on_click is not None,
    ), normal, PRIMARY_SOFT if active else "#F3F6F5")


def build_sidebar(page: ft.Page) -> ft.Container:
    from pages.sidebar import build_unified_sidebar
    return build_unified_sidebar(page=page, active_tab="timer")


# ---------------------------------------------------------------------
# Background persistent timer state (survives route / tab changes)
# ---------------------------------------------------------------------
TIMER_STATE = {
    "minutes": 25,
    "total": 25 * 60,
    "remaining": 25 * 60,
    "running": False,
    "hint": DEFAULT_HINT,
    "pill": "FOCUS",
    "loop_started": False,
    "active_instance": None,
}


def reset_timer_state():
    """Completely resets the study timer state to default (25 min, fresh session, not running)."""
    TIMER_STATE["minutes"] = 25
    TIMER_STATE["total"] = 25 * 60
    TIMER_STATE["remaining"] = 25 * 60
    TIMER_STATE["running"] = False
    TIMER_STATE["hint"] = DEFAULT_HINT
    TIMER_STATE["pill"] = "FOCUS"
    inst = TIMER_STATE.get("active_instance")
    if inst is not None:
        try:
            inst.sync_presets()
            inst.sync_controls()
            if inst.page is not None:
                inst.page.update()
        except Exception:
            pass



# ---------------------------------------------------------------------
# Study timer card
# ---------------------------------------------------------------------
class StudyTimer:
    def __init__(self, page: ft.Page):
        self.page = page
        TIMER_STATE["active_instance"] = self

        # --- controls ---
        self.pill_text = ft.Text(TIMER_STATE["pill"], size=13, weight=ft.FontWeight.BOLD, color=PRIMARY)
        self.time_text = ft.Text(fmt(TIMER_STATE["remaining"]), size=72, weight=ft.FontWeight.BOLD, color=TEXT)
        self.sub_text = ft.Text(f"of {TIMER_STATE['minutes']} min", size=16, color=TEXT_MUTED)
        self.ring = ft.ProgressRing(
            value=TIMER_STATE["remaining"] / TIMER_STATE["total"] if TIMER_STATE["total"] else 0,
            width=290, height=290, stroke_width=6,
            color=PRIMARY, bgcolor=RING_TRACK, stroke_cap=ft.StrokeCap.ROUND,
        )

        self.start_icon = ft.Icon(ft.Icons.PLAY_ARROW, color=SURFACE, size=24)
        self.start_label = ft.Text("Start", color=SURFACE, size=18, weight=ft.FontWeight.W_600)
        self.start_btn = ft.Container(
            width=150, height=58, bgcolor=PRIMARY, border_radius=12,
            alignment=ft.Alignment.CENTER,
            shadow=ft.BoxShadow(blur_radius=8, color="#1A000000", offset=ft.Offset(0, 2)),
            on_click=lambda _: self.toggle(),
            content=ft.Row([self.start_icon, self.start_label],
                           alignment=ft.MainAxisAlignment.CENTER, spacing=6),
        )
        self.reset_btn = ft.Container(
            width=125, height=58, bgcolor=SURFACE,
            border=ft.Border.all(1.2, INPUT_BORDER), border_radius=12,
            alignment=ft.Alignment.CENTER,
            on_click=lambda _: self.reset(),
            content=ft.Row([
                ft.Icon(ft.Icons.REFRESH, color=TEXT_MUTED, size=21),
                ft.Text("Reset", color=TEXT_MUTED, size=18, weight=ft.FontWeight.W_500),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
        )

        self.preset_buttons: dict[int, tuple[ft.Container, ft.Text]] = {}
        for m in PRESETS:
            lbl = ft.Text(f"{m} min", size=16, weight=ft.FontWeight.W_500)
            btn = ft.Container(
                width=105, height=50, border_radius=12, alignment=ft.Alignment.CENTER,
                on_click=lambda _, mins=m: self.set_duration(mins), content=lbl,
            )
            self.preset_buttons[m] = (btn, lbl)

        self.custom = ft.TextField(
            hint_text="Min", hint_style=ft.TextStyle(color="#9CA3AF", size=15),
            width=145, height=50, text_size=15, color=TEXT,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_color=INPUT_BORDER, focused_border_color=PRIMARY, border_radius=10,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            on_submit=lambda _: self.apply_custom(),
        )
        self.set_btn = hoverable(ft.Container(
            width=82, height=50, bgcolor=PRIMARY_SOFT, border_radius=10,
            alignment=ft.Alignment.CENTER, on_click=lambda _: self.apply_custom(),
            content=ft.Text("Set", size=16, weight=ft.FontWeight.W_600, color=PRIMARY_SOFT_TEXT),
        ), PRIMARY_SOFT, "#D4EAE4")
        self.hint = ft.Text(TIMER_STATE["hint"], size=15, color=TEXT_MUTED)

        self.sync_presets()
        self.sync_controls()

    @property
    def minutes(self) -> int:
        return TIMER_STATE["minutes"]

    @minutes.setter
    def minutes(self, val: int):
        TIMER_STATE["minutes"] = val

    @property
    def total(self) -> int:
        return TIMER_STATE["total"]

    @total.setter
    def total(self, val: int):
        TIMER_STATE["total"] = val

    @property
    def remaining(self) -> int:
        return TIMER_STATE["remaining"]

    @remaining.setter
    def remaining(self, val: int):
        TIMER_STATE["remaining"] = val

    @property
    def running(self) -> bool:
        return TIMER_STATE["running"]

    @running.setter
    def running(self, val: bool):
        TIMER_STATE["running"] = val

    def build(self) -> ft.Container:
        pill = ft.Container(
            bgcolor=PRIMARY_SOFT, border_radius=999,
            padding=ft.Padding.symmetric(horizontal=18, vertical=7),
            content=self.pill_text,
        )
        dial = ft.Stack([
            self.ring,
            ft.Container(
                width=290, height=290, alignment=ft.Alignment.CENTER,
                content=ft.Column([pill, self.time_text, self.sub_text],
                                  alignment=ft.MainAxisAlignment.CENTER,
                                  horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            ),
        ], width=290, height=290)

        return ft.Container(
            width=580, bgcolor=SURFACE,
            border=ft.Border.all(1, BORDER), border_radius=20,
            padding=ft.Padding.symmetric(horizontal=44, vertical=44),
            content=ft.Column([
                dial,
                ft.Container(height=28),
                ft.Row([self.start_btn, self.reset_btn],
                       alignment=ft.MainAxisAlignment.CENTER, spacing=16),
                ft.Container(height=34),
                ft.Divider(height=1, thickness=1, color=BORDER),
                ft.Container(height=26),
                ft.Text("PRESET DURATIONS", size=14, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                ft.Container(height=16),
                ft.Row([b for b, _ in self.preset_buttons.values()],
                       alignment=ft.MainAxisAlignment.CENTER, spacing=12),
                ft.Container(height=22),
                ft.Row([
                    ft.Text("Custom length:", size=16, color="#4B5563"),
                    self.custom, self.set_btn,
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
                ft.Container(height=24),
                self.hint,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
        )

    # --- state updates ---
    def sync_presets(self):
        for m, (btn, lbl) in self.preset_buttons.items():
            selected = m == self.minutes
            btn.bgcolor = PRIMARY_SOFT if selected else SURFACE
            btn.border = ft.Border.all(1.5 if selected else 1.2,
                                       PRIMARY if selected else INPUT_BORDER)
            lbl.color = PRIMARY if selected else TEXT
            lbl.weight = ft.FontWeight.W_600 if selected else ft.FontWeight.W_500

    def sync_controls(self):
        self.time_text.value = fmt(self.remaining)
        self.sub_text.value = f"of {self.minutes} min"
        self.ring.value = self.remaining / self.total if self.total else 0
        self.start_icon.name = ft.Icons.PAUSE if self.running else ft.Icons.PLAY_ARROW
        self.start_label.value = "Pause" if self.running else (
            "Resume" if 0 < self.remaining < self.total else "Start"
        )
        self.start_btn.bgcolor = PRIMARY_HOVER if self.running else PRIMARY
        if self.remaining > 0:
            TIMER_STATE["pill"] = "FOCUSING" if self.running else "FOCUS"
        self.pill_text.value = TIMER_STATE["pill"]
        self.hint.value = TIMER_STATE["hint"]

    def refresh(self):
        self.sync_controls()
        if self.time_text.page is not None:
            try:
                self.page.update()
            except Exception:
                pass

    def notify(self, message: str):
        try:
            self.page.show_dialog(ft.SnackBar(ft.Text(message)))
        except Exception:
            pass

    def set_duration(self, minutes: int):
        self.running = False
        self.minutes = minutes
        self.total = self.remaining = minutes * 60
        TIMER_STATE["hint"] = DEFAULT_HINT
        TIMER_STATE["pill"] = "FOCUS"
        self.sync_presets()
        self.refresh()

    def reset(self):
        self.running = False
        self.remaining = self.total
        TIMER_STATE["hint"] = DEFAULT_HINT
        TIMER_STATE["pill"] = "FOCUS"
        self.refresh()

    def apply_custom(self):
        raw = (self.custom.value or "").strip()
        if not raw.isdigit() or not (1 <= int(raw) <= MAX_MINUTES):
            self.notify(f"Enter a number between 1 and {MAX_MINUTES} minutes.")
            return
        minutes = int(raw)
        self.custom.value = ""
        self.set_duration(minutes)

    def toggle(self):
        if self.remaining <= 0:
            self.remaining = self.total
        self.running = not self.running
        TIMER_STATE["hint"] = "Stay focused - you got this!" if self.running else "Paused. Resume when ready."
        self.refresh()

    async def tick_loop(self):
        if TIMER_STATE["loop_started"]:
            return
        TIMER_STATE["loop_started"] = True
        try:
            while True:
                await asyncio.sleep(1)
                if not TIMER_STATE["running"]:
                    continue
                TIMER_STATE["remaining"] -= 1
                inst: StudyTimer | None = TIMER_STATE.get("active_instance")
                if TIMER_STATE["remaining"] <= 0:
                    TIMER_STATE["remaining"] = 0
                    TIMER_STATE["running"] = False
                    TIMER_STATE["pill"] = "DONE"
                    TIMER_STATE["hint"] = "Session complete. Take a short break!"
                    try:
                        from pages import backend
                        backend.api_log_timer(TIMER_STATE["minutes"])
                    except Exception:
                        pass
                    if inst is not None:
                        inst.notify("Focus session complete 🎉 (Logged to DB)")
                if inst is not None:
                    inst.refresh()
        finally:
            TIMER_STATE["loop_started"] = False


# ---------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------
def build_timer_root(page: ft.Page) -> ft.Row:
    timer = StudyTimer(page)

    header = ft.Container(
        bgcolor=SURFACE, border=ft.Border.only(bottom=ft.BorderSide(1, BORDER)),
        padding=ft.Padding.symmetric(horizontal=48, vertical=24),
        content=ft.Column([
            ft.Text("Study timer", size=24, weight=ft.FontWeight.W_600, color=TEXT),
            ft.Text("Focus session", size=15, color=TEXT_MUTED),
        ], spacing=4),
    )

    content = ft.Container(
        expand=True,
        padding=ft.Padding.symmetric(horizontal=24, vertical=48),
        content=ft.Column(
            [timer.build()],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    page.run_task(timer.tick_loop)

    return ft.Row(
        [
            build_sidebar(page),
            ft.Column(
                [header, content],
                spacing=0,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        ],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )


def main(page: ft.Page):
    page.title = "Arcadia - Study timer"
    page.bgcolor = BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1440
    page.window.height = 940

    page.controls.clear()
    page.add(build_timer_root(page))


def get_view(page: ft.Page) -> ft.View:
    return ft.View(
        route="/studytimer",
        padding=0,
        bgcolor=BG,
        controls=[build_timer_root(page)],
    )


if __name__ == "__main__":
    ft.app(main)
