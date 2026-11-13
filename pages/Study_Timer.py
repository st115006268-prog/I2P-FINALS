"""Arcadia - Study timer page (front end only), built with Flet.

Requirements:  pip install flet
Run:           python study_timer.py          (desktop window)
               flet run --web study_timer.py  (in the browser)
"""
import asyncio

import flet as ft

# ---------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------
PRIMARY = "#11786B"
PRIMARY_HOVER = "#0D665B"
PRIMARY_SOFT = "#E6F2EF"
PRIMARY_SOFT_TEXT = "#5FA69B"
TEXT = "#111827"
TEXT_MUTED = "#6B7280"
BORDER = "#E5E7EB"
INPUT_BORDER = "#D9DDE3"
BG = "#F4F5F7"
SURFACE = "#FFFFFF"
NAVY = "#1E2340"
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


def hoverable(container: ft.Container, normal: str, hover: str) -> ft.Container:
    def on_hover(e):
        container.bgcolor = hover if e.data in (True, "true") else normal
        container.update()
    container.on_hover = on_hover
    return container


def nav_item(label: str, icon, active: bool = False, badge: str | None = None,
             icon_control: ft.Control | None = None) -> ft.Container:
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
    ), normal, PRIMARY_SOFT if active else "#F3F6F5")


def build_sidebar(page: ft.Page) -> ft.Container:
    chats = ["New study chat", "What is E=mc²?", "Help with my I2P questions"]
    chat_column = ft.Column(spacing=0)

    def render_chats():
        chat_column.controls = [chat_row(i, t) for i, t in enumerate(chats)]

    def remove_chat(index: int):
        chats.pop(index)
        render_chats()
        chat_column.update()

    def chat_row(index: int, title: str) -> ft.Container:
        return hoverable(ft.Container(
            height=50, padding=ft.Padding.symmetric(horizontal=15), border_radius=8,
            content=ft.Row([
                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=20, color=TEXT_MUTED),
                ft.Text(title, size=16, color=TEXT_MUTED, expand=True,
                        no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Container(
                    content=ft.Icon(ft.Icons.CLOSE, size=16, color="#B0B5BD"),
                    on_click=lambda _, i=index: remove_chat(i), border_radius=4, padding=2,
                ),
            ], spacing=12),
        ), None, "#F6F7F8")

    def new_chat(_):
        chats.insert(0, "New study chat")
        render_chats()
        chat_column.update()
        page.show_dialog(ft.SnackBar(ft.Text("New study chat created")))

    render_chats()

    new_chat_btn = hoverable(ft.Container(
        height=53, bgcolor=PRIMARY, border_radius=10, alignment=ft.Alignment.CENTER,
        on_click=new_chat,
        content=ft.Row([
            ft.Icon(ft.Icons.ADD, color=SURFACE, size=22),
            ft.Text("New study chat", color=SURFACE, size=16, weight=ft.FontWeight.W_600),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
    ), PRIMARY, PRIMARY_HOVER)

    user_card = hoverable(ft.Container(
        padding=16, border=ft.Border.all(1, BORDER), border_radius=12,
        content=ft.Row([
            ft.Container(
                width=42, height=42, border_radius=21, bgcolor="#EEF0F2",
                alignment=ft.Alignment.CENTER,
                content=ft.Text("JD", size=16, weight=ft.FontWeight.W_600, color=TEXT),
            ),
            ft.Column([
                ft.Text("John Doe", size=16, weight=ft.FontWeight.W_500, color=TEXT),
                ft.Text("View profile", size=11, color=TEXT_MUTED),
            ], spacing=0),
        ], spacing=12),
    ), None, "#FAFAFA")

    return ft.Container(
        width=312, bgcolor=SURFACE,
        border=ft.Border.only(right=ft.BorderSide(1, BORDER)),
        padding=ft.Padding.only(left=19, right=19, top=32, bottom=18),
        content=ft.Column([
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=10),
                content=ft.Row([
                    logo(),
                    ft.Text("Arcadia", size=26, weight=ft.FontWeight.BOLD, color=TEXT),
                ], spacing=12),
            ),
            ft.Container(height=22),
            new_chat_btn,
            ft.Container(height=22),
            nav_item("AI Assistant", ft.Icons.AUTO_AWESOME),
            nav_item("Flashcards", ft.Icons.LAYERS_OUTLINED),
            nav_item("Study planner", ft.Icons.CALENDAR_MONTH_OUTLINED, badge="To-do · Calendar"),
            nav_item("Study timer", ft.Icons.TIMER_OUTLINED, active=True),
            nav_item("Profile", None, icon_control=logo(20)),
            ft.Container(
                padding=ft.Padding.only(left=15, top=8),
                content=ft.Row([
                    ft.Icon(ft.Icons.SYNC, size=16, color=TEXT_MUTED),
                    ft.Text("To-do list and calendar stay in sync", size=13,
                            color=TEXT_MUTED, expand=True),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
            ),
            ft.Container(height=36),
            ft.Text("RECENT CHATS", size=14, weight=ft.FontWeight.W_600, color="#4B5563"),
            chat_column,
            ft.Container(expand=True),
            user_card,
        ], spacing=7, expand=True),
    )


# ---------------------------------------------------------------------
# Study timer card
# ---------------------------------------------------------------------
class StudyTimer:
    def __init__(self, page: ft.Page):
        self.page = page
        self.minutes = 25
        self.total = self.remaining = self.minutes * 60
        self.running = False

        # --- controls ---
        self.pill_text = ft.Text("FOCUS", size=13, weight=ft.FontWeight.BOLD, color=PRIMARY)
        self.ring = ft.ProgressRing(
            value=1.0, width=298, height=298, stroke_width=14,
            color=PRIMARY, bgcolor=RING_TRACK, stroke_cap=ft.StrokeCap.ROUND,
        )
        self.time_text = ft.Text(fmt(self.remaining), size=72, weight=ft.FontWeight.W_600, color=TEXT)
        self.session_text = ft.Text("25 minutes session", size=13, color="#4B5563")

        self.preset_buttons: dict[int, ft.Container] = {}
        for m in PRESETS:
            self.preset_buttons[m] = ft.Container(
                expand=True, height=46, border_radius=9, alignment=ft.Alignment.CENTER,
                on_click=lambda _, m=m: self.set_duration(m),
                content=ft.Text(f"{m} min", size=13, weight=ft.FontWeight.W_600),
            )

        self.custom = ft.TextField(
            hint_text="Minutes", expand=True, height=48, text_size=14,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=INPUT_BORDER, focused_border_color=PRIMARY, border_radius=9,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            on_change=lambda _: self.refresh(), on_submit=lambda _: self.set_custom(),
        )
        self.set_btn_text = ft.Text("Set timer", size=16, weight=ft.FontWeight.W_500)
        self.set_btn = ft.Container(
            width=107, height=48, border_radius=9, bgcolor=PRIMARY_SOFT,
            alignment=ft.Alignment.CENTER, content=self.set_btn_text,
            on_click=lambda _: self.set_custom(),
        )

        self.start_text = ft.Text("Start focus", size=16, weight=ft.FontWeight.W_600, color=SURFACE)
        self.start_btn = hoverable(ft.Container(
            width=168, height=48, bgcolor=PRIMARY, border_radius=10,
            alignment=ft.Alignment.CENTER, content=self.start_text,
            on_click=lambda _: self.toggle(),
        ), PRIMARY, PRIMARY_HOVER)
        self.reset_btn = ft.Container(
            content=ft.Text("Reset", size=16, color="#4B5563"),
            padding=8, on_click=lambda _: self.set_duration(self.minutes),
        )
        self.hint = ft.Text(DEFAULT_HINT, size=16, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER)

        self.refresh(update=False)

    # --- layout ---
    def build(self) -> ft.Container:
        return ft.Container(
            width=622, bgcolor=SURFACE, border_radius=22,
            border=ft.Border.all(1, "#ECEEF1"),
            padding=ft.Padding.only(left=50, right=50, top=48, bottom=50),
            shadow=ft.BoxShadow(blur_radius=3, color="#0A101828", offset=ft.Offset(0, 1)),
            content=ft.Column([
                ft.Container(
                    content=self.pill_text, bgcolor=PRIMARY_SOFT, border_radius=999,
                    padding=ft.Padding.symmetric(horizontal=16, vertical=7),
                ),
                ft.Container(height=14),
                ft.Stack([
                    ft.Container(self.ring, padding=7),
                    ft.Container(
                        width=312, height=312, alignment=ft.Alignment.CENTER,
                        content=ft.Column([self.time_text, self.session_text],
                                          spacing=0, tight=True,
                                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ),
                ], width=312, height=312),
                ft.Container(height=16),
                ft.Row(list(self.preset_buttons.values()), spacing=10),
                ft.Container(height=10),
                ft.Row([ft.Text("Custom duration", size=13, weight=ft.FontWeight.W_600, color=TEXT)]),
                ft.Row([self.custom, self.set_btn], spacing=10),
                ft.Container(height=12),
                ft.Row([self.start_btn, self.reset_btn], spacing=26,
                       alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=14),
                self.hint,
            ], spacing=8, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        )

    # --- behaviour ---
    def refresh(self, update: bool = True):
        self.time_text.value = fmt(self.remaining)
        self.ring.value = self.remaining / self.total if self.total else 0
        self.session_text.value = f"{self.minutes} minutes session"
        if self.running:
            self.start_text.value = "Pause"
        elif 0 < self.remaining < self.total:
            self.start_text.value = "Resume"
        else:
            self.start_text.value = "Start focus"

        for m, btn in self.preset_buttons.items():
            active = m == self.minutes
            btn.bgcolor = PRIMARY_SOFT if active else SURFACE
            btn.border = ft.Border.all(1, PRIMARY if active else INPUT_BORDER)
            btn.content.color = PRIMARY if active else "#374151"

        has_value = bool((self.custom.value or "").strip())
        self.set_btn_text.color = PRIMARY if has_value else PRIMARY_SOFT_TEXT
        if update:
            self.page.update()

    def notify(self, message: str):
        self.page.show_dialog(ft.SnackBar(ft.Text(message)))

    def set_duration(self, minutes: int):
        self.running = False
        self.minutes = minutes
        self.total = self.remaining = minutes * 60
        self.pill_text.value = "FOCUS"
        self.hint.value = DEFAULT_HINT
        self.refresh()

    def set_custom(self):
        try:
            minutes = int(float(self.custom.value))
        except (TypeError, ValueError):
            self.notify("Enter a number of minutes")
            return
        if not 1 <= minutes <= MAX_MINUTES:
            self.notify(f"Pick between 1 and {MAX_MINUTES} minutes")
            return
        self.custom.value = ""
        self.set_duration(minutes)

    def toggle(self):
        if self.remaining <= 0:
            self.remaining = self.total
        self.running = not self.running
        self.hint.value = "Stay focused - you got this!" if self.running else "Paused. Resume when ready."
        self.refresh()

    async def tick_loop(self):
        while True:
            await asyncio.sleep(1)
            if not self.running:
                continue
            self.remaining -= 1
            if self.remaining <= 0:
                self.remaining = 0
                self.running = False
                self.pill_text.value = "DONE"
                self.hint.value = "Session complete. Take a short break!"
                self.notify("Focus session complete 🎉")
            self.refresh()


# ---------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------
def main(page: ft.Page):
    page.title = "Arcadia - Study timer"
    page.bgcolor = BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1440
    page.window.height = 940

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

    page.add(ft.Row([
        build_sidebar(page),
        ft.Column([header, content], spacing=0, expand=True,
                  horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
    ], spacing=0, expand=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH))

    page.run_task(timer.tick_loop)


if __name__ == "__main__":
    ft.run(main)
