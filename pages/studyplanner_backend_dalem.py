"""Arcadia - Study planner (frontend only), built with Flet 1.x.

Run:  python study_planner.py
"""
import calendar as pycal
from datetime import date, timedelta

import flet as ft
import flet.canvas as cv

# --------------------------------------------------------------------------- #
# Design tokens
# --------------------------------------------------------------------------- #
TEAL = "#13766B"
TEAL_LIGHT = "#E4F2EF"
TEAL_FAINT = "#F2F9F7"
BG = "#F3F5F6"
WHITE = "#FFFFFF"
BORDER = "#E5E7EB"
GRID = "#ECEEF1"
TEXT = "#111827"
TEXT_2 = "#1F2937"
MUTED = "#6B7280"
NAVY = "#1F2A4D"
SEG_BG = "#F1F3F5"

PALETTE = {
    "teal":   {"dot": "#13766B", "bg": "#E9F5F2", "edge": "#13766B", "line": "#CDE6E0", "text": "#0E6157"},
    "purple": {"dot": "#6A5FCF", "bg": "#EFEEFB", "edge": "#7168C9", "line": "#DCD9F4", "text": "#5A52B5"},
    "orange": {"dot": "#E0782A", "bg": "#FCF1E7", "edge": "#E5893D", "line": "#F6DCC4", "text": "#D16A1C"},
    "gray":   {"dot": "#9CA3AF", "bg": "#F3F4F6", "edge": "#C3C8CF", "line": "#E5E7EB", "text": "#8A919C"},
}

HOUR_START, HOUR_END = 8, 18
HOUR_H = 49            # pixel height of one hour in the week grid
TIME_COL_W = 54        # width of the time-label column
TODO_W = 406           # width of the To-do card


def fmt(h: float) -> str:
    return f"{int(h):02d}:{int(round((h % 1) * 60)):02d}"


def fmt_short(h: float) -> str:
    return f"{int(h)}:{int(round((h % 1) * 60)):02d}"


def T(value, size=14, weight=None, color=TEXT, **kw):
    return ft.Text(value, size=size, weight=weight, color=color, **kw)


# --------------------------------------------------------------------------- #
# App
# --------------------------------------------------------------------------- #
def main(page: ft.Page):
    page.title = "Arcadia - Study planner"
    page.padding = 0
    page.spacing = 0
    page.bgcolor = BG
    page.fonts = {
        "Inter": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Inter", color_scheme_seed=TEAL)
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1600
    page.window.height = 960
    page.window.min_width = 1400   # desktop layout, like the design (1920 wide)
    page.window.min_height = 760
    page.window.maximized = True

    today = date.today()
    monday = today - timedelta(days=today.weekday())

    S = {
        "nav": "planner",
        "tab": "today",
        "view": "week",
        "anchor": today,          # date the calendar is showing
        "next_id": 100,
        "ai_idx": 0,
        "chats": ["New study chat", "What is E=mc²?", "Help with my I2P ques..."],
        "tasks": [
            dict(id=1, title="Review flashcards", day=today, start=9, end=9.5, color="teal", done=False),
            dict(id=2, title="Study session", day=today, start=10, end=11, color="purple", done=False),
            dict(id=3, title="Finish assignment", day=today, start=12, end=13, color="orange", done=False),
            dict(id=4, title="Read chapter notes", day=today + timedelta(days=1), start=14, end=14.5, color="teal", done=False),
            dict(id=5, title="Do laundry", day=today + timedelta(days=2), start=16, end=17, color="gray", done=False),
        ],
    }

    # ------------------------------------------------------------------ helpers
    def toast(msg):
        page.show_dialog(ft.SnackBar(ft.Text(msg), bgcolor=TEXT_2, duration=1800))

    def toggle(task):
        task["done"] = not task["done"]
        render()

    def go(nav):
        S["nav"] = nav
        render()

    # ------------------------------------------------------------------ sidebar
    def logo(size=44, radius=10):
        return ft.Container(
            width=size, height=size, bgcolor=NAVY, border_radius=radius,
            alignment=ft.Alignment.CENTER,
            shadow=ft.BoxShadow(blur_radius=6, color="#33000000", offset=ft.Offset(0, 2)),
            content=ft.Container(
                width=size * 0.40, height=size * 0.56, bgcolor=WHITE, border_radius=size * 0.07,
                alignment=ft.Alignment.CENTER,
                content=ft.Container(width=size * 0.13, height=size * 0.13, bgcolor="#E5484D",
                                     border_radius=2, rotate=ft.Rotate(0.785)),
            ),
        )

    def nav_item(key, label, icon=None, icon_ctrl=None, badge=None):
        sel = S["nav"] == key
        color = TEAL if sel else TEXT
        row = [
            ft.Container(width=26, alignment=ft.Alignment.CENTER,
                         content=icon_ctrl or ft.Icon(icon, size=22, color=TEAL if sel else "#4B5563")),
            T(label, 17, ft.FontWeight.W_600 if sel else ft.FontWeight.W_500, color),
        ]
        if badge:
            row.append(ft.Container(
                bgcolor="#D7EBE6", border_radius=6, padding=ft.Padding.symmetric(horizontal=6, vertical=3),
                content=T(badge, 10, ft.FontWeight.W_500, "#2F4F4A")))
        return ft.Container(
            height=52, border_radius=10, bgcolor=TEAL_LIGHT if sel else None,
            padding=ft.Padding.only(left=14, right=10),
            content=ft.Row(row, spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            on_click=lambda e, k=key: go(k),
            ink=True,
        )

    def chat_row(i, title):
        def remove(e, idx=i):
            S["chats"].pop(idx)
            render()

        return ft.Container(
            height=50, border_radius=8, padding=ft.Padding.only(left=14, right=6),
            on_click=lambda e, t=title: toast(f'Open chat: "{t}"'),
            content=ft.Row([
                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=21, color="#4B5563"),
                ft.Container(expand=True, content=T(title, 16, ft.FontWeight.W_400, "#4B5563",
                                                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.Container(width=28, height=28, alignment=ft.Alignment.CENTER, border_radius=6,
                             on_click=remove,
                             content=ft.Icon(ft.Icons.CLOSE, size=15, color="#A1A7B0")),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        )

    def new_chat(e):
        S["chats"].insert(0, "New study chat")
        render()

    def build_sidebar():
        return ft.Container(
            width=312, bgcolor=WHITE,
            border=ft.Border.only(right=ft.BorderSide(1, BORDER)),
            padding=ft.Padding.only(left=19, right=19, top=34, bottom=16),
            content=ft.Column([
                ft.Container(padding=ft.Padding.only(left=10), content=ft.Row(
                    [logo(), T("Arcadia", 26, ft.FontWeight.W_700, TEXT)], spacing=12)),
                ft.Container(height=36),
                ft.Container(
                    height=53, bgcolor=TEAL, border_radius=10, alignment=ft.Alignment.CENTER,
                    on_click=new_chat, ink=True,
                    shadow=ft.BoxShadow(blur_radius=4, color="#22000000", offset=ft.Offset(0, 1)),
                    content=ft.Row([ft.Icon(ft.Icons.ADD, color=WHITE, size=22),
                                    T("New study chat", 16, ft.FontWeight.W_700, WHITE)],
                                   spacing=12, alignment=ft.MainAxisAlignment.CENTER),
                ),
                ft.Container(height=30),
                ft.Column([
                    nav_item("ai", "AI Assistant", ft.Icons.AUTO_AWESOME_OUTLINED),
                    nav_item("flashcards", "Flashcards", ft.Icons.LAYERS_OUTLINED),
                    nav_item("planner", "Study planner", ft.Icons.CALENDAR_MONTH_OUTLINED,
                             badge="To-do · Calendar"),
                    nav_item("timer", "Study timer", ft.Icons.TIMER_OUTLINED),
                    nav_item("profile", "Profile", icon_ctrl=logo(22, 4)),
                ], spacing=8),
                ft.Container(
                    padding=ft.Padding.only(left=14, top=18, right=10),
                    content=ft.Row([
                        ft.Icon(ft.Icons.SYNC, size=17, color=MUTED),
                        ft.Container(expand=True, content=T(
                            "To-do list and calendar stay in sync", 13, color=MUTED)),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
                ),
                ft.Container(height=36),
                T("RECENT CHATS", 14, ft.FontWeight.W_600, "#4B5563"),
                ft.Container(height=8),
                ft.Column([chat_row(i, c) for i, c in enumerate(S["chats"])],
                          spacing=0, expand=True, scroll=ft.ScrollMode.AUTO),
                ft.Container(
                    border=ft.Border.all(1, BORDER), border_radius=12, height=76,
                    padding=ft.Padding.symmetric(horizontal=15), on_click=lambda e: go("profile"),
                    content=ft.Row([
                        ft.Container(width=44, height=44, border_radius=22, bgcolor="#EEF0F2",
                                     alignment=ft.Alignment.CENTER,
                                     content=T("JD", 16, ft.FontWeight.W_700, TEXT)),
                        ft.Column([T("John Doe", 16, ft.FontWeight.W_500, TEXT),
                                   T("View profile", 12, color=MUTED)],
                                  spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                    ], spacing=12),
                ),
            ], spacing=0, expand=True),
        )

    # ------------------------------------------------------------------ header
    def primary_btn(label, icon, on_click):
        return ft.Container(
            height=48, bgcolor=TEAL, border_radius=10, ink=True, on_click=on_click,
            padding=ft.Padding.symmetric(horizontal=20),
            shadow=ft.BoxShadow(blur_radius=4, color="#22000000", offset=ft.Offset(0, 1)),
            content=ft.Row([ft.Icon(icon, size=18, color=WHITE),
                            T(label, 17, ft.FontWeight.W_700, WHITE)],
                           spacing=10, tight=True),
        )

    def build_header(title="Study planner", subtitle="To-do list and calendar", actions=True):
        right = []
        if actions:
            right = [
                ft.Container(
                    border=ft.Border.all(1, BORDER), border_radius=24, height=44,
                    padding=ft.Padding.symmetric(horizontal=14),
                    content=ft.Row([
                        ft.Container(width=6, height=6, border_radius=3, bgcolor="#1A9A6C"),
                        T("Planner and calendar synced", 13.5, color=MUTED),
                    ], spacing=6, tight=True),
                ),
                primary_btn("Add task", ft.Icons.ADD, lambda e: open_add_dialog()),
                primary_btn("AI suggested task", ft.Icons.AUTO_AWESOME, ai_suggest),
            ]
        return ft.Container(
            height=106, bgcolor=WHITE,
            border=ft.Border.only(bottom=ft.BorderSide(1, BORDER)),
            padding=ft.Padding.only(left=48, right=46),
            content=ft.Row([
                ft.Column([T(title, 25, ft.FontWeight.W_700, TEXT),
                           T(subtitle, 16, color=MUTED)],
                          spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                ft.Row(right, spacing=14),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        )

    # ------------------------------------------------------------------ to-do card
    def checkbox(task):
        done = task["done"]
        return ft.Container(
            width=21, height=21, border_radius=5,
            bgcolor=TEAL if done else WHITE,
            border=ft.Border.all(1.2, TEAL if done else "#CBD0D7"),
            alignment=ft.Alignment.CENTER,
            on_click=lambda e, t=task: toggle(t),
            content=ft.Icon(ft.Icons.CHECK, size=15, color=WHITE) if done else None,
        )

    def todo_item(task):
        p = PALETTE[task["color"]]
        done = task["done"]
        deco = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if done else None
        when = fmt(task["start"]) + " – " + fmt(task["end"])
        if task["day"] != today:
            when = task["day"].strftime("%a, %b ") + str(task["day"].day) + " · " + when
        return ft.Container(
            height=67, bgcolor=WHITE, border_radius=12, border=ft.Border.all(1, BORDER),
            padding=ft.Padding.only(left=14, right=16),
            opacity=0.6 if done else 1,
            content=ft.Row([
                checkbox(task),
                ft.Column([
                    T(task["title"], 15, ft.FontWeight.W_500, TEXT_2, style=deco),
                    T(when, 13, color=MUTED),
                ], spacing=1, expand=True, alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(width=7, height=7, border_radius=4, bgcolor=p["dot"]),
            ], spacing=13, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        )

    def segmented(options, current, on_pick, item_w=None, height=40, text_size=14):
        items = []
        for key, label in options:
            sel = key == current
            items.append(ft.Container(
                expand=item_w is None, width=item_w, height=height, border_radius=9,
                alignment=ft.Alignment.CENTER,
                bgcolor=WHITE if sel else None,
                shadow=ft.BoxShadow(blur_radius=3, color="#1A000000", offset=ft.Offset(0, 1)) if sel else None,
                on_click=lambda e, k=key: on_pick(k),
                content=T(label, text_size, ft.FontWeight.W_600 if sel else ft.FontWeight.W_400,
                          TEAL if sel else MUTED),
            ))
        return ft.Container(bgcolor=SEG_BG, border_radius=12, padding=4,
                            content=ft.Row(items, spacing=0, tight=item_w is not None))

    def dashed_add_button():
        w, h = TODO_W - 2 - 48, 52
        return ft.Stack([
            ft.Container(width=w, height=h, bgcolor=TEAL_FAINT, border_radius=12),
            cv.Canvas(width=w, height=h, shapes=[
                cv.Rect(0.5, 0.5, w - 1, h - 1, border_radius=12, paint=ft.Paint(
                    color=TEAL, stroke_width=1, style=ft.PaintingStyle.STROKE,
                    stroke_dash_pattern=[4, 3])),
            ]),
            ft.Container(
                width=w, height=h, border_radius=12, alignment=ft.Alignment.CENTER,
                on_click=lambda e: open_add_dialog(), ink=True,
                content=ft.Row([ft.Icon(ft.Icons.ADD, size=16, color=TEAL),
                                T("Add a task", 15, ft.FontWeight.W_600, TEAL)],
                               spacing=8, alignment=ft.MainAxisAlignment.CENTER),
            ),
        ], width=w, height=h)

    def pick_tab(k):
        S["tab"] = k
        render()

    def build_todo():
        tasks = S["tasks"]
        done_n = sum(t["done"] for t in tasks)
        key = lambda t: (t["day"], t["start"])
        if S["tab"] == "today":
            shown = sorted([t for t in tasks if t["day"] == today], key=key)
        elif S["tab"] == "upcoming":
            shown = sorted([t for t in tasks if t["day"] > today and not t["done"]], key=key)
        else:
            shown = sorted([t for t in tasks if t["done"]], key=key)

        if shown:
            items = [todo_item(t) for t in shown]
        else:
            msg = {"today": "Nothing planned for today.",
                   "upcoming": "No upcoming tasks.",
                   "done": "No completed tasks yet."}[S["tab"]]
            items = [ft.Container(height=67, alignment=ft.Alignment.CENTER, content=T(msg, 14, color=MUTED))]

        return ft.Container(
            width=TODO_W, bgcolor=WHITE, border_radius=20, border=ft.Border.all(1, BORDER),
            padding=ft.Padding.only(left=24, right=24, top=24, bottom=24),
            content=ft.Column([
                ft.Row([
                    T("To-do", 22, ft.FontWeight.W_700, TEXT),
                    ft.Container(bgcolor=TEAL_LIGHT, border_radius=20,
                                 padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                                 content=T(f"{done_n} of {len(tasks)} done", 13.5, ft.FontWeight.W_600, TEAL)),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=22),
                segmented([("today", "Today"), ("upcoming", "Upcoming"), ("done", "Done")],
                          S["tab"], pick_tab),
                ft.Container(height=24),
                ft.Column(items, spacing=12),
                ft.Container(height=24),
                dashed_add_button(),
            ], spacing=0, tight=True),
        )

    # ------------------------------------------------------------------ calendar card
    def event_block(task):
        p = PALETTE[task["color"]]
        done = task["done"]
        h = max((task["end"] - task["start"]) * HOUR_H - 2, 34)
        deco = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if done else None
        lines = [T(task["title"], 12.5, ft.FontWeight.W_600, p["text"], style=deco,
                   max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)]
        if h >= 44:
            lines.append(T(fmt(task["start"]) + " – " + fmt(task["end"]), 10, color=p["text"], opacity=0.75))
        return ft.Container(
            top=(task["start"] - HOUR_START) * HOUR_H + 1, left=5, right=5, height=h,
            bgcolor=p["bg"], border_radius=6, border=ft.Border.all(1, p["line"]),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            opacity=0.55 if done else 1,
            tooltip=("Mark as not done" if done else "Mark complete"),
            on_click=lambda e, t=task: toggle(t),
            content=ft.Row([
                ft.Container(width=2.5, bgcolor=p["edge"]),
                ft.Container(expand=True, padding=ft.Padding.only(left=6, top=7, right=4),
                             content=ft.Column(lines, spacing=3)),
            ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.STRETCH),
        )

    def nav_btn(icon, on_click):
        return ft.Container(width=36, height=36, border_radius=8, border=ft.Border.all(1, BORDER),
                            alignment=ft.Alignment.CENTER, on_click=on_click,
                            content=ft.Icon(icon, size=16, color=TEXT_2))

    def shift(direction):
        a, v = S["anchor"], S["view"]
        if v == "week":
            S["anchor"] = a + timedelta(days=7 * direction)
        elif v == "day":
            S["anchor"] = a + timedelta(days=direction)
        else:
            m = a.month - 1 + direction
            S["anchor"] = date(a.year + m // 12, m % 12 + 1, 1)
        render()

    def go_today(e):
        S["anchor"] = today
        render()

    def pick_view(k):
        S["view"] = k
        render()

    def range_label():
        a = S["anchor"]
        if S["view"] == "week":
            ws = a - timedelta(days=a.weekday())
            we = ws + timedelta(days=6)
            return f"{ws:%b} {ws.day} – {we:%b} {we.day}, {we.year}"
        if S["view"] == "day":
            return f"{a:%A, %b} {a.day}, {a.year}"
        return f"{a:%B %Y}"

    def time_grid(days):
        grid_h = (HOUR_END - HOUR_START) * HOUR_H + 14
        n_hours = HOUR_END - HOUR_START

        # header row with day names / numbers
        head = [ft.Container(width=TIME_COL_W)]
        for d in days:
            is_today = d == today
            c = TEAL if is_today else "#374151"
            w = ft.FontWeight.W_700 if is_today else ft.FontWeight.W_400
            head.append(ft.Container(expand=1, content=ft.Column([
                T(f"{d:%a}", 13, w, c), ft.Container(height=10), T(str(d.day), 13, w, c),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)))

        # time labels
        labels = ft.Stack([
            ft.Container(top=i * HOUR_H + 1, left=0, content=T(fmt_short(HOUR_START + i), 11.5, color="#4B5563"))
            for i in range(n_hours + 1)
        ], width=TIME_COL_W, height=grid_h)

        cols = [labels]
        for d in days:
            lines = [ft.Container(top=i * HOUR_H, left=0, right=0, height=1, bgcolor=GRID)
                     for i in range(n_hours)]
            evs = [event_block(t) for t in sorted(S["tasks"], key=lambda t: t["start"]) if t["day"] == d]
            cols.append(ft.Container(
                expand=1, height=grid_h,
                border=ft.Border.only(left=ft.BorderSide(1, GRID)),
                content=ft.Stack(lines + evs, clip_behavior=ft.ClipBehavior.NONE),
            ))
        return ft.Column([
            ft.Row(head, spacing=0),
            ft.Container(height=22),
            ft.Row(cols, spacing=0, vertical_alignment=ft.CrossAxisAlignment.START),
        ], spacing=0)

    def month_grid():
        a = S["anchor"]
        weeks = pycal.Calendar(firstweekday=0).monthdatescalendar(a.year, a.month)
        head = ft.Row([ft.Container(expand=1, alignment=ft.Alignment.CENTER, content=T(n, 13, color="#374151"))
                       for n in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]], spacing=0)
        rows = []
        for wk in weeks:
            cells = []
            for d in wk:
                is_today = d == today
                chips = []
                for t in sorted([t for t in S["tasks"] if t["day"] == d], key=lambda t: t["start"]):
                    p = PALETTE[t["color"]]
                    chips.append(ft.Container(
                        bgcolor=p["bg"], border_radius=4, padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                        opacity=0.55 if t["done"] else 1, on_click=lambda e, t=t: toggle(t),
                        content=T(t["title"], 10.5, ft.FontWeight.W_600, p["text"], max_lines=1,
                                  overflow=ft.TextOverflow.ELLIPSIS)))
                cells.append(ft.Container(
                    expand=1, height=100, padding=6,
                    border=ft.Border.only(left=ft.BorderSide(1, GRID), top=ft.BorderSide(1, GRID)),
                    opacity=1 if d.month == a.month else 0.4,
                    content=ft.Column([
                        T(str(d.day), 12.5, ft.FontWeight.W_700 if is_today else ft.FontWeight.W_400,
                          TEAL if is_today else TEXT_2),
                        *chips[:3],
                    ], spacing=3)))
            rows.append(ft.Row(cells, spacing=0))
        return ft.Column([head, ft.Container(height=14), *rows], spacing=0)

    def build_calendar():
        a = S["anchor"]
        if S["view"] == "week":
            ws = a - timedelta(days=a.weekday())
            body = time_grid([ws + timedelta(days=i) for i in range(7)])
        elif S["view"] == "day":
            body = time_grid([a])
        else:
            body = month_grid()

        return ft.Container(
            expand=True, bgcolor=WHITE, border_radius=20, border=ft.Border.all(1, BORDER),
            padding=ft.Padding.only(left=24, right=24, top=32, bottom=34),
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        nav_btn(ft.Icons.CHEVRON_LEFT, lambda e: shift(-1)),
                        nav_btn(ft.Icons.CHEVRON_RIGHT, lambda e: shift(1)),
                        ft.Container(height=36, border_radius=8, border=ft.Border.all(1, BORDER),
                                     padding=ft.Padding.symmetric(horizontal=12),
                                     alignment=ft.Alignment.CENTER, on_click=go_today,
                                     content=T("Today", 13, ft.FontWeight.W_600, TEAL)),
                        ft.Container(width=4),
                        T(range_label(), 21, ft.FontWeight.W_700, TEXT),
                    ], spacing=10),
                    ft.Container(
                        bgcolor=SEG_BG, border_radius=10, padding=4,
                        content=ft.Row([
                            ft.Container(
                                height=36, border_radius=8,
                                padding=ft.Padding.symmetric(horizontal=16),
                                alignment=ft.Alignment.CENTER,
                                bgcolor=WHITE if S["view"] == k else None,
                                shadow=ft.BoxShadow(blur_radius=3, color="#1A000000", offset=ft.Offset(0, 1))
                                if S["view"] == k else None,
                                on_click=lambda e, k=k: pick_view(k),
                                content=T(lbl, 13, ft.FontWeight.W_600 if S["view"] == k else ft.FontWeight.W_400,
                                          TEAL if S["view"] == k else MUTED))
                            for k, lbl in [("day", "Day"), ("week", "Week"), ("month", "Month")]
                        ], spacing=0, tight=True)),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=36),
                body,
                ft.Container(height=26),
                ft.Row([
                    ft.Row([ft.Container(width=7, height=7, border_radius=4, bgcolor=TEAL),
                            T("Planner task", 11, color=TEAL)], spacing=5, tight=True),
                    T("Click a calendar task to mark it complete", 11, color="#5A52B5"),
                ], spacing=22),
            ], spacing=0, tight=True),
        )

    # ------------------------------------------------------------------ actions
    def add_task(title, day, start, end, color):
        S["tasks"].append(dict(id=S["next_id"], title=title, day=day, start=start,
                               end=end, color=color, done=False))
        S["next_id"] += 1
        render()

    def open_add_dialog():
        week_start = S["anchor"] - timedelta(days=S["anchor"].weekday())
        day_opts = [week_start + timedelta(days=i) for i in range(7)]
        times = [HOUR_START + i * 0.5 for i in range((HOUR_END - HOUR_START) * 2 + 1)]

        title = ft.TextField(label="Task title", autofocus=True, border_radius=10)
        day_dd = ft.Dropdown(label="Day", width=200, border_radius=10,
                             value=(today if today in day_opts else day_opts[0]).isoformat(),
                             options=[ft.DropdownOption(key=d.isoformat(), text=f"{d:%a, %b} {d.day}")
                                      for d in day_opts])
        start_dd = ft.Dropdown(label="Start", width=120, border_radius=10, value="14.0",
                               options=[ft.DropdownOption(key=str(float(t)), text=fmt(t)) for t in times[:-1]])
        end_dd = ft.Dropdown(label="End", width=120, border_radius=10, value="15.0",
                             options=[ft.DropdownOption(key=str(float(t)), text=fmt(t)) for t in times[1:]])
        color_dd = ft.Dropdown(label="Colour", width=200, border_radius=10, value="teal",
                               options=[ft.DropdownOption(key=k, text=k.capitalize()) for k in PALETTE])
        err = T("", 12, color="#DC2626")

        def save(e):
            s, en = float(start_dd.value), float(end_dd.value)
            if not (title.value or "").strip():
                err.value = "Please enter a title."
            elif en <= s:
                err.value = "End time must be after start time."
            else:
                page.pop_dialog()
                add_task(title.value.strip(), date.fromisoformat(day_dd.value), s, en, color_dd.value)
                return
            err.update()

        page.show_dialog(ft.AlertDialog(
            modal=True, bgcolor=WHITE, shape=ft.RoundedRectangleBorder(radius=16),
            title=T("Add task", 20, ft.FontWeight.W_700),
            content=ft.Container(width=420, content=ft.Column([
                title,
                ft.Row([day_dd, color_dd], spacing=12),
                ft.Row([start_dd, end_dd], spacing=12),
                err,
            ], spacing=14, tight=True)),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Add task", on_click=save, bgcolor=TEAL),
            ],
        ))

    AI_IDEAS = [("Practice quiz", "purple"), ("Summarise lecture notes", "teal"),
                ("Spaced-repetition review", "teal"), ("Past paper question", "orange")]

    def ai_suggest(e):
        title, color = AI_IDEAS[S["ai_idx"] % len(AI_IDEAS)]
        S["ai_idx"] += 1
        for offset in range(7):
            d = today + timedelta(days=offset)
            busy = [(t["start"], t["end"]) for t in S["tasks"] if t["day"] == d]
            h = HOUR_START if offset else max(HOUR_START, 9)
            while h + 1 <= HOUR_END:
                if all(h + 1 <= s or h >= en for s, en in busy):
                    add_task(title, d, h, h + 1, color)
                    toast(f"AI suggested: {title} · {d:%a} {fmt(h)} – {fmt(h + 1)}")
                    return
                h += 0.5
        toast("No free slot found this week.")

    # ------------------------------------------------------------------ layout
    def build_placeholder():
        names = {"ai": "AI Assistant", "flashcards": "Flashcards", "timer": "Study timer", "profile": "Profile"}
        name = names[S["nav"]]
        return ft.Column([
            build_header(name, "Coming soon", actions=False),
            ft.Container(expand=True, alignment=ft.Alignment.CENTER,
                         content=T(f"{name} screen isn't part of this design yet.", 16, color=MUTED)),
        ], spacing=0, expand=True)

    def build_root():
        if S["nav"] == "planner":
            main_area = ft.Column([
                build_header(),
                ft.Column([
                    ft.Container(
                        padding=ft.Padding.only(left=48, right=46, top=40, bottom=30),
                        content=ft.Row([build_todo(), build_calendar()], spacing=30,
                                       vertical_alignment=ft.CrossAxisAlignment.START),
                    ),
                ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0),
            ], spacing=0, expand=True)
        else:
            main_area = build_placeholder()
        return ft.Row([build_sidebar(), main_area], spacing=0, expand=True,
                      vertical_alignment=ft.CrossAxisAlignment.STRETCH)

    def render():
        page.controls.clear()
        page.add(build_root())

    render()

def get_view(page: ft.Page) -> ft.View:
    # Clear any existing controls temporarily so main() can build onto a clean slate
    old_controls = list(page.controls)
    page.controls.clear()
    
    # Run the file's existing main() setup
    main(page)
    
    # Capture what main() added to page, then restore page.controls
    view_controls = list(page.controls)
    page.controls.clear()
    page.controls.extend(old_controls)
    
    return ft.View(
        route=page.route,
        padding=0,
        controls=view_controls,
    )
def get_view(page: ft.Page) -> ft.View:
    # Clear any existing controls temporarily so main() can build onto a clean slate
    old_controls = list(page.controls)
    page.controls.clear()
    
    # Run the file's existing main() setup
    main(page)
    
    # Capture what main() added to page, then restore page.controls
    view_controls = list(page.controls)
    page.controls.clear()
    page.controls.extend(old_controls)
    
    return ft.View(
        route=page.route,
        padding=0,
        controls=view_controls,
    )
if __name__ == "__main__":
    ft.run(main)
