"""Arcadia frontend built with Flet (Python).

Run:  python arcadia_flet.py
Chat logic lives in backend.py.
"""
from __future__ import annotations

import sys

import flet as ft

from pages import backend

# ---------------------------------------------------------------- colours
TEAL = "#12766a"
TEAL_HOVER = "#0f685d"
TEAL_SOFT = "#e5f2ef"
TEAL_DISABLED = "#8cc4ba"
INK = "#111827"
TEXT = "#1f2937"
MUTED = "#4b5563"
LIGHT = "#6b7280"
LINE = "#e5e7eb"
BG = "#f4f5f7"
CHIP = "#f3f4f6"
WHITE = "#ffffff"

FONT = "Inter"
INTER_URL = "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf"

SIDEBAR_W = 312
CONTENT_MAX_W = 1212

# ---------------------------------------------------------------- icons (SVG)
LOGO_SVG = """<svg viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg">
<rect width="44" height="44" rx="9" fill="#1d2840"/>
<rect x="13.5" y="10" width="15" height="22" rx="2.4" fill="#d9363e" transform="rotate(-8 21 21)"/>
<rect x="15.5" y="11" width="15" height="22" rx="2.4" fill="#ffffff"/>
<path d="M23 17.2c1.6 1.9 3.6 3.1 3.6 4.9 0 1.2-1 2-2 2-.6 0-1.1-.3-1.4-.6l.5 2h-1.4l.5-2c-.3.3-.8.6-1.4.6-1 0-2-.8-2-2 0-1.8 2-3 3.6-4.9z" fill="#1d2840"/>
</svg>"""

_STROKE = ('<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="none" '
           'stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')

ICONS = {
    "sparkles": (1.7, '<path d="M9.9 15.5a2 2 0 0 0-1.4-1.4L2.4 12.5a.5.5 0 0 1 0-1l6.1-1.6a2 2 0 0 0 1.4-1.4l1.6-6.1a.5.5 0 0 1 1 0l1.6 6.1a2 2 0 0 0 1.4 1.4l6.1 1.6a.5.5 0 0 1 0 1l-6.1 1.6a2 2 0 0 0-1.4 1.4l-1.6 6.1a.5.5 0 0 1-1 0z"/><path d="M20 3v4M22 5h-4M4 17v2M5 18H3"/>'),
    "layers": (1.7, '<path d="M12.8 2.2a2 2 0 0 0-1.6 0L2.6 6.1a1 1 0 0 0 0 1.8l8.6 3.9a2 2 0 0 0 1.6 0l8.6-3.9a1 1 0 0 0 0-1.8z"/><path d="m2 12 9.2 4.2a2 2 0 0 0 1.6 0L22 12"/><path d="m2 17 9.2 4.2a2 2 0 0 0 1.6 0L22 17"/>'),
    "calendar": (1.6, '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01M16 18h.01"/>'),
    "timer": (1.7, '<path d="M10 2h4M12 14l3-3"/><circle cx="12" cy="14" r="8"/>'),
    "chat": (1.7, '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'),
    "sync": (2, '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>'),
    "plus": (3, '<path d="M12 4v16M4 12h16"/>'),
    "close": (2.4, '<path d="M18 6 6 18M6 6l12 12"/>'),
    "arrow": (2.4, '<path d="M12 19V5M5 12l7-7 7 7"/>'),
}


def svg(name: str, size: float, color: str = INK) -> ft.Image:
    if name == "logo":
        markup = LOGO_SVG
    else:
        width, body = ICONS[name]
        markup = _STROKE.format(color=color, w=width, body=body)
    return ft.Image(src=markup.encode(), width=size, height=size)


def text(value: str, size: float, color: str = TEXT, weight=ft.FontWeight.W_400, **kw) -> ft.Text:
    return ft.Text(value, size=size, color=color, weight=weight, font_family=FONT, **kw)


def clickable(control: ft.Control) -> ft.GestureDetector:
    """Show the hand cursor over a control."""
    return ft.GestureDetector(content=control, mouse_cursor=ft.MouseCursor.CLICK)


def hover_bg(normal: str | None, hover: str):
    def handler(e):
        e.control.bgcolor = hover if e.data else normal
        e.control.update()
    return handler


# ---------------------------------------------------------------- app
class ArcadiaApp:
    def __init__(self, page: ft.Page, auto_mount: bool = True):
        self.page = page
        self.store = backend.ChatStore()
        self.current = self.store.chats[0]

        page.title = "Arcadia"
        page.padding = 0
        page.spacing = 0
        page.bgcolor = BG
        page.fonts = {FONT: INTER_URL}
        page.theme = ft.Theme(font_family=FONT)
        page.window.width = 1918
        page.window.height = 935
        page.window.min_width = 900
        page.window.min_height = 600
        page.window.maximized = True
        page.on_resize = self._on_resize

        self.chat_list = ft.Column(spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)
        self.title = text(self.current.title, 24, INK, ft.FontWeight.W_600)
        self.empty = self._empty_state()
        self.messages = ft.Column(spacing=14, visible=False)
        self.chips = self._chips()
        self.input = ft.TextField(
            hint_text="Ask Arcadia anything about your notes...",
            hint_style=ft.TextStyle(color=MUTED, size=17, font_family=FONT),
            text_style=ft.TextStyle(color=INK, size=17, font_family=FONT),
            border=ft.NoInputBorder(),
            content_padding=0,
            dense=True,
            multiline=True,
            min_lines=1,
            max_lines=8,
            shift_enter=True,  # Enter sends, Shift+Enter adds a new line
            cursor_color=TEAL,
            on_change=self._on_input_change,
            on_submit=self._on_submit,
        )
        self.send_btn = ft.Container(
            content=svg("arrow", 20, WHITE),
            width=48, height=48, border_radius=10,
            bgcolor=TEAL_DISABLED, alignment=ft.Alignment.CENTER,
            on_click=self._on_submit,
        )
        self.bottom = ft.Container(content=self._bottom_area(), width=CONTENT_MAX_W)
        self.messages_box = ft.Container(content=self.messages, width=CONTENT_MAX_W,
                                         padding=ft.Padding.only(top=32, bottom=16))

        self.root_row = ft.Row(
            [self._sidebar(), self._main()],
            spacing=0, expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        if auto_mount:
            page.add(self.root_row)

        self._render_chats()
        self._on_resize(update=auto_mount)

    # ------------------------------------------------------------ sidebar
    def _sidebar(self) -> ft.Control:
        brand = ft.Container(
            padding=ft.Padding.only(left=10),
            content=ft.Row(
                [
                    ft.Container(
                        content=svg("logo", 44), border_radius=9,
                        shadow=ft.BoxShadow(blur_radius=6, offset=ft.Offset(0, 2),
                                            color="#33111827"),
                    ),
                    text("Arcadia", 26, INK, ft.FontWeight.W_700),
                ],
                spacing=12,
            ),
        )

        new_chat = clickable(ft.Container(
            height=53, border_radius=12, bgcolor=TEAL,
            alignment=ft.Alignment.CENTER,
            on_click=self._new_chat,
            on_hover=hover_bg(TEAL, TEAL_HOVER),
            content=ft.Row(
                [svg("plus", 16, WHITE), text("New study chat", 16, WHITE, ft.FontWeight.W_600)],
                spacing=14, alignment=ft.MainAxisAlignment.CENTER,
            ),
        ))

        nav = ft.Column([self._nav_item(item) for item in backend.NAV_ITEMS], spacing=7)

        sync = ft.Container(
            padding=ft.Padding.only(left=15, right=24),
            content=ft.Row(
                [
                    ft.Container(svg("sync", 15, MUTED), padding=ft.Padding.only(top=3)),
                    text("To-do list and calendar stay in sync", 13, MUTED, expand=True),
                ],
                spacing=9, vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )

        user = backend.USER
        user_card = clickable(ft.Container(
            height=77, border_radius=12, bgcolor=WHITE,
            border=ft.Border.all(1, LINE),
            padding=ft.Padding.symmetric(horizontal=15),
            on_hover=hover_bg(WHITE, "#fafafa"),
            on_click=lambda e: None,
            content=ft.Row(
                [
                    ft.Container(
                        width=43, height=43, border_radius=22, bgcolor="#f1f2f4",
                        alignment=ft.Alignment.CENTER,
                        content=text(user["initials"], 15, INK, ft.FontWeight.W_700),
                    ),
                    ft.Column(
                        [text(user["name"], 16, INK, ft.FontWeight.W_500),
                         text("View profile", 11, MUTED)],
                        spacing=1, alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                spacing=12,
            ),
        ))

        return ft.Container(
            width=SIDEBAR_W,
            bgcolor=WHITE,
            border=ft.Border.only(right=ft.BorderSide(1, LINE)),
            padding=ft.Padding.only(left=19, top=34, right=20, bottom=16),
            content=ft.Column(
                [
                    brand,
                    ft.Container(height=36),
                    new_chat,
                    ft.Container(height=28),
                    nav,
                    ft.Container(height=14),
                    sync,
                    ft.Container(height=52),
                    text("RECENT CHATS", 14, MUTED, ft.FontWeight.W_600),
                    ft.Container(height=9),
                    self.chat_list,
                    ft.Container(height=8),
                    user_card,
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )

    def _nav_item(self, item: dict) -> ft.Control:
        active = item["key"] == "assistant"
        icon_color = TEAL if active or item["key"] == "flashcards" else MUTED
        row = [
            svg(item["icon"], 21, icon_color),
            text(item["label"], 17, TEAL if active else INK,
                 ft.FontWeight.W_600 if active else ft.FontWeight.W_500),
        ]
        if item.get("badge"):
            row.append(ft.Container(
                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                border_radius=999, bgcolor=CHIP, border=ft.Border.all(1, LINE),
                content=text(item["badge"], 9.5, MUTED, ft.FontWeight.W_500),
            ))
        normal = TEAL_SOFT if active else None
        return clickable(ft.Container(
            height=53, border_radius=12, bgcolor=normal,
            padding=ft.Padding.symmetric(horizontal=15),
            on_hover=None if active else hover_bg(normal, "#f6f7f8"),
            on_click=lambda e: None,
            content=ft.Row(row, spacing=11),
        ))

    def _chat_row(self, chat: backend.Chat) -> ft.Control:
        active = chat.id == self.current.id
        normal = "#f2f3f5" if active else None
        close = clickable(ft.Container(
            width=22, height=22, border_radius=6, alignment=ft.Alignment.CENTER,
            content=svg("close", 12, "#9ca3af"),
            on_hover=hover_bg(None, LINE),
            on_click=lambda e, cid=chat.id: self._delete_chat(cid),
            tooltip="Delete chat",
        ))
        return clickable(ft.Container(
            height=50, border_radius=10, bgcolor=normal,
            padding=ft.Padding.only(left=14, right=12),
            on_hover=None if active else hover_bg(normal, "#f8f9fa"),
            on_click=lambda e, cid=chat.id: self._open_chat(cid),
            content=ft.Row(
                [
                    svg("chat", 20, MUTED),
                    text(chat.title, 16, INK if active else LIGHT, expand=True,
                         max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    close,
                ],
                spacing=11,
            ),
        ))

    # ------------------------------------------------------------ main area
    def _main(self) -> ft.Control:
        header = ft.Container(
            height=106, bgcolor=WHITE,
            border=ft.Border.only(bottom=ft.BorderSide(1, LINE)),
            padding=ft.Padding.only(left=48, top=22, right=48),
            content=ft.Column([self.title, text("AI study assistant", 16, MUTED)], spacing=4),
        )
        conversation = ft.Column(
            [self.empty, self.messages_box],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            auto_scroll=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )
        return ft.Container(
            expand=True,
            content=ft.Column(
                [
                    header,
                    conversation,
                    ft.Row([self.bottom], alignment=ft.MainAxisAlignment.CENTER),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )

    def _empty_state(self) -> ft.Control:
        return ft.Container(
            padding=ft.Padding.only(top=93),
            content=ft.Column(
                [
                    svg("logo", 58),
                    ft.Container(height=22),
                    text("What are you studying?", 27, INK, ft.FontWeight.W_700),
                    ft.Container(height=10),
                    ft.Container(
                        width=470,
                        content=text("Ask a question, build a study plan, or turn your "
                                     "notes into practice material.", 17, MUTED,
                                     text_align=ft.TextAlign.CENTER),
                    ),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def _chips(self) -> ft.Control:
        def chip(label: str) -> ft.Control:
            return clickable(ft.Container(
                height=47, border_radius=24, bgcolor=WHITE,
                border=ft.Border.all(1, LINE),
                padding=ft.Padding.symmetric(horizontal=18),
                on_hover=hover_bg(WHITE, "#fafafa"),
                on_click=lambda e, t=label: self._use_suggestion(t),
                content=ft.Row([text(label, 14, INK)], tight=True,
                               vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ))
        return ft.Container(
            padding=ft.Padding.only(bottom=21),
            content=ft.Row([chip(s) for s in backend.SUGGESTIONS], spacing=12, wrap=True),
        )

    def _bottom_area(self) -> ft.Control:
        def tool(glyph: str, tip: str, color: str = "#374151") -> ft.Control:
            return clickable(ft.Container(
                width=48, height=48, border_radius=10, bgcolor=CHIP,
                alignment=ft.Alignment.CENTER, tooltip=tip,
                on_hover=hover_bg(CHIP, "#e9ebee"),
                on_click=lambda e: None,
                content=text(glyph, 14, color),
            ))

        composer = ft.Container(
            bgcolor=WHITE, border_radius=16, border=ft.Border.all(1, LINE),
            padding=ft.Padding.only(left=20, top=19, right=19, bottom=19),
            shadow=ft.BoxShadow(blur_radius=2, offset=ft.Offset(0, 1), color="#08111827"),
            content=ft.Column(
                [
                    self.input,
                    ft.Container(height=18),
                    ft.Row(
                        [
                            tool("⌕", "Search"),
                            tool("▧", "Attach image"),
                            tool("♩", "Audio", TEAL),
                            ft.Container(expand=True),
                            clickable(self.send_btn),
                        ],
                        spacing=8,
                    ),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )
        return ft.Container(
            padding=ft.Padding.only(bottom=15),
            content=ft.Column(
                [
                    self.chips,
                    composer,
                    ft.Container(height=23),
                    ft.Row(
                        [text("Arcadia can make mistakes. Check important facts with your "
                              "course material.", 12, MUTED)],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                spacing=0,
            ),
        )

    # ------------------------------------------------------------ rendering
    def _on_resize(self, e=None, update: bool = True) -> None:
        """Keep the content column centred with a max width, like CSS max-width."""
        width = (self.page.width or 1918) - SIDEBAR_W - 32
        w = max(320, min(CONTENT_MAX_W, width))
        self.bottom.width = w
        self.messages_box.width = w
        if update:
            self.page.update()

    def _render_chats(self) -> None:
        self.chat_list.controls = [self._chat_row(c) for c in self.store.chats]

    def _render_messages(self) -> None:
        self.messages.controls = [self._bubble(m["role"], m["text"]) for m in self.current.messages]
        has = bool(self.current.messages)
        self.empty.visible = not has
        self.messages.visible = has
        self.chips.visible = not has
        self.title.value = self.current.title

    def _bubble(self, role: str, value: str) -> ft.Control:
        user = role == "user"
        bubble = ft.Container(
            content=ft.Text(value, size=15, color=WHITE if user else TEXT,
                            font_family=FONT, selectable=True),
            bgcolor=TEAL if user else WHITE,
            border=None if user else ft.Border.all(1, LINE),
            border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            max_width=820,
        )
        return ft.Row(
            [bubble],
            alignment=ft.MainAxisAlignment.END if user else ft.MainAxisAlignment.START,
        )

    def _refresh(self) -> None:
        self._render_chats()
        self._render_messages()
        self.page.update()

    # ------------------------------------------------------------ actions
    def _new_chat(self, e=None) -> None:
        self.current = self.store.new_chat()
        self._refresh()

    def _open_chat(self, chat_id: int) -> None:
        self.current = self.store.get(chat_id)
        self._refresh()

    def _delete_chat(self, chat_id: int) -> None:
        nxt = self.store.delete(chat_id)
        if self.current not in self.store.chats:
            self.current = nxt
        self._refresh()

    def _use_suggestion(self, value: str) -> None:
        self.input.value = value
        self._on_input_change()
        self.page.run_task(self.input.focus)

    def _on_input_change(self, e=None) -> None:
        self.send_btn.bgcolor = TEAL if (self.input.value or "").strip() else TEAL_DISABLED
        self.page.update()

    def _on_submit(self, e=None) -> None:
        value = (self.input.value or "").strip()
        if not value:
            return
        self.input.value = ""
        self.store.send(self.current.id, value)
        self._on_input_change()
        self._refresh()
        self.page.run_task(self.input.focus)


def get_view(page: ft.Page) -> ft.View:
    app = ArcadiaApp(page, auto_mount=False)
    return ft.View(
        route="/ai-assistant",
        padding=0,
        bgcolor=BG,
        controls=[app.root_row],
    )


async def main(page: ft.Page) -> None:
    app = ArcadiaApp(page)

    if "--screenshot" in sys.argv:
        import asyncio
        args = sys.argv[sys.argv.index("--screenshot") + 1:]
        page.window.maximized = False
        page.window.left, page.window.top = 0, 0
        page.window.width, page.window.height = 1280, 760
        page.window.always_on_top = True
        page.update()
        if len(args) > 1:
            app._use_suggestion(args[1])
            app._on_submit()
        await asyncio.sleep(5)
        grab = ("from PySide6.QtWidgets import QApplication; import sys; a=QApplication([]); "
                "a.primaryScreen().grabWindow(0).save(sys.argv[1])")
        proc = await asyncio.create_subprocess_exec(sys.executable, "-c", grab, args[0])
        await proc.wait()
        await page.window.destroy()


if __name__ == "__main__":
    ft.run(main)