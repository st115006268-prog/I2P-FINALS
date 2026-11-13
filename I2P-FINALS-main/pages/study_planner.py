"""Arcadia - Study planner (frontend only), built with Flet 1.x.

Run:  python studyplanner_backend_dalem.py
"""
import calendar as pycal
from datetime import date, timedelta

import flet as ft
import flet.canvas as cv
import flet_compat

from styles import (
    TEAL,
    TEAL_LIGHT,
    TEAL_FAINT,
    BG,
    WHITE,
    BORDER,
    GRID,
    TEXT,
    TEXT_2,
    MUTED,
    NAVY,
)
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

ROUTE_MAP = {
    "assistant": "/ai-assistant",
    "ai": "/ai-assistant",
    "flashcards": "/flashcards",
    "studyview": "/studyview",
    "planner": "/studyplanner",
    "timer": "/studytimer",
    "profile": "/profile",
}


def fmt(h: float) -> str:
    return f"{int(h):02d}:{int(round((h % 1) * 60)):02d}"


def fmt_short(h: float) -> str:
    return f"{int(h)}:{int(round((h % 1) * 60)):02d}"


def T(value, size=14, weight=None, color=TEXT, **kw):
    return ft.Text(value, size=size, weight=weight, color=color, **kw)


def build_planner_root(page: ft.Page) -> ft.Container:
    from pages import backend
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    loaded_tasks = backend.api_get_tasks()
    loaded_chats = [c.get("title", "New study chat") for c in backend.api_get_chats()]

    S = {
        "nav": "planner",
        "tab": "today",
        "view": "week",
        "anchor": today,          # date the calendar is showing
        "next_id": 100,
        "ai_idx": 0,
        "chats": loaded_chats,
        "tasks": loaded_tasks,
    }

    root_host = ft.Container(expand=True)

    # ------------------------------------------------------------------ helpers
    def toast(msg):
        page.show_dialog(ft.SnackBar(ft.Text(msg), bgcolor=TEXT_2, duration=1800))

    def toggle(task):
        task["done"] = not task["done"]
        try:
            backend.api_update_task(task["id"], done=task["done"])
        except Exception:
            pass
        render()

    def go(nav):
        target = ROUTE_MAP.get(nav)
        if target and target != page.route:
            page.go(target)
        else:
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
            on_click=lambda e, t=title: go("ai"),
            ink=True,
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
        from pages.sidebar import build_unified_sidebar
        return build_unified_sidebar(page=page, active_tab="planner", switch_tab=go)

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
                ft.Container(height=18),
                segmented([("today", "Today"), ("upcoming", "Upcoming"), ("done", "Done")],
                          S["tab"], pick_tab),
                ft.Container(height=18),
                ft.Column(items, spacing=12),
                ft.Container(height=18),
                dashed_add_button(),
            ], spacing=0, tight=True),
        )

    # ------------------------------------------------------------------ calendar card
    def step_anchor(delta):
        v = S["view"]
        if v == "day":
            S["anchor"] += timedelta(days=delta)
        elif v == "week":
            S["anchor"] += timedelta(weeks=delta)
        else:
            a = S["anchor"]
            m = a.month - 1 + delta
            y, m = a.year + m // 12, m % 12 + 1
            S["anchor"] = date(y, m, min(a.day, pycal.monthrange(y, m)[1]))
        render()

    def pick_view(v):
        S["view"] = v
        render()

    def build_cal_header():
        a, v = S["anchor"], S["view"]
        wk_mon = a - timedelta(days=a.weekday())
        wk_sun = wk_mon + timedelta(days=6)
        if v == "day":
            title = a.strftime("%B ") + str(a.day) + a.strftime(", %Y")
            sub = a.strftime("%A") + (" · Today" if a == today else "")
        elif v == "week":
            title = wk_mon.strftime("%B %Y")
            end = f"{wk_sun.day}" if wk_mon.month == wk_sun.month else wk_sun.strftime("%b ") + str(wk_sun.day)
            sub = f"Week of {wk_mon.strftime('%b')} {wk_mon.day}–{end}"
        else:
            title = a.strftime("%B %Y")
            sub = "Month overview"

        def nav_btn(icon, delta):
            return ft.Container(
                width=42, height=40, border_radius=12, border=ft.Border.all(1, BORDER), bgcolor=WHITE,
                alignment=ft.Alignment.CENTER, ink=True, on_click=lambda e, d=delta: step_anchor(d),
                content=ft.Icon(icon, size=18, color="#374151"),
            )

        return ft.Row([
            ft.Column([T(title, 22, ft.FontWeight.W_700, TEXT),
                       T(sub, 14, color=MUTED)], spacing=1),
            ft.Row([
                segmented([("day", "Day"), ("week", "Week"), ("month", "Month")],
                          v, pick_view, item_w=66, height=34, text_size=13.5),
                ft.Container(width=4),
                nav_btn(ft.Icons.CHEVRON_LEFT, -1),
                nav_btn(ft.Icons.CHEVRON_RIGHT, 1),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def event_block(task, top, height):
        p = PALETTE[task["color"]]
        done = task["done"]
        deco = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if done else None
        compact = height < 34
        return ft.Container(
            left=4, right=4, top=top, height=height,
            bgcolor=p["bg"], border_radius=8, opacity=0.6 if done else 1,
            border=ft.Border(
                left=ft.BorderSide(3, p["edge"]),
                top=ft.BorderSide(0.8, p["line"]),
                right=ft.BorderSide(0.8, p["line"]),
                bottom=ft.BorderSide(0.8, p["line"]),
            ),
            padding=ft.Padding.only(left=8, right=6, top=3 if compact else 7, bottom=2),
            on_click=lambda e, t=task: toggle(t),
            content=ft.Column([
                T(task["title"], 12.5, ft.FontWeight.W_600, p["text"],
                  max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, style=deco),
                *([T(fmt_short(task["start"]), 11, color=p["text"])] if not compact else []),
            ], spacing=1),
        )

    def build_week_or_day(days):
        hours = list(range(HOUR_START, HOUR_END + 1))
        total_h = (HOUR_END - HOUR_START + 1) * HOUR_H

        # day-name header strip
        hdr = [ft.Container(width=TIME_COL_W)]
        for d in days:
            is_today = d == today
            hdr.append(ft.Container(
                expand=True, height=58,
                bgcolor=TEAL_FAINT if is_today else None,
                border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
                alignment=ft.Alignment.CENTER,
                content=ft.Column([
                    T(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"][d.weekday()],
                      11.5, ft.FontWeight.W_600, TEAL if is_today else MUTED),
                    T(str(d.day), 18, ft.FontWeight.W_700, TEAL if is_today else TEXT),
                ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   alignment=ft.MainAxisAlignment.CENTER),
            ))

        # time labels column
        time_col = ft.Column(
            [ft.Container(height=HOUR_H, alignment=ft.Alignment.TOP_RIGHT,
                          padding=ft.Padding.only(right=14),
                          content=T(f"{h:02d}:00", 12, color=MUTED))
             for h in hours],
            spacing=0, width=TIME_COL_W,
        )

        # day columns
        day_cols = []
        for idx, d in enumerate(days):
            is_today = d == today
            lines = ft.Column(
                [ft.Container(height=HOUR_H, border=ft.Border.only(top=ft.BorderSide(1, GRID)))
                 for _ in hours],
                spacing=0,
            )
            events = []
            for t in S["tasks"]:
                if t["day"] == d and HOUR_START <= t["start"] <= HOUR_END:
                    top = (t["start"] - HOUR_START) * HOUR_H + 1
                    h_px = max(23, (t["end"] - t["start"]) * HOUR_H - 2)
                    events.append(event_block(t, top, h_px))
            day_cols.append(ft.Container(
                expand=True, height=total_h,
                bgcolor=TEAL_FAINT if is_today else None,
                border=ft.Border.only(left=ft.BorderSide(1, GRID)) if idx else None,
                content=ft.Stack([lines, *events]),
            ))

        return ft.Column([
            ft.Row(hdr, spacing=0),
            ft.Container(height=10),
            ft.Row([time_col, *day_cols], spacing=0, vertical_alignment=ft.CrossAxisAlignment.START),
        ], spacing=0)

    def build_month():
        a = S["anchor"]
        cal = pycal.Calendar(firstweekday=0)
        weeks = cal.monthdatescalendar(a.year, a.month)
        hdr = ft.Row([
            ft.Container(expand=True, alignment=ft.Alignment.CENTER, padding=ft.Padding.only(bottom=8),
                         content=T(n, 12, ft.FontWeight.W_600, MUTED))
            for n in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        ], spacing=6)
        rows = [hdr]
        for wk in weeks:
            cells = []
            for d in wk:
                in_m = d.month == a.month
                is_t = d == today
                day_tasks = [t for t in S["tasks"] if t["day"] == d]
                pills = [
                    ft.Container(
                        bgcolor=PALETTE[t["color"]]["bg"], border_radius=5,
                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                        content=T(t["title"], 11, ft.FontWeight.W_600, PALETTE[t["color"]]["text"],
                                  max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    )
                    for t in day_tasks[:2]
                ]
                cells.append(ft.Container(
                    expand=True, height=96, border_radius=10, padding=7,
                    bgcolor=TEAL_FAINT if is_t else (WHITE if in_m else "#FAFAFB"),
                    border=ft.Border.all(1.3 if is_t else 1, TEAL if is_t else BORDER),
                    on_click=lambda e, day=d: (S.update(anchor=day, view="day"), render()),
                    content=ft.Column([
                        T(str(d.day), 13, ft.FontWeight.W_700 if is_t else ft.FontWeight.W_500,
                          TEAL if is_t else (TEXT if in_m else "#B0B5BD")),
                        *pills,
                    ], spacing=3),
                ))
            rows.append(ft.Row(cells, spacing=6))
        return ft.Column(rows, spacing=6)

    def build_calendar():
        a, v = S["anchor"], S["view"]
        if v == "day":
            body = build_week_or_day([a])
        elif v == "week":
            wk_mon = a - timedelta(days=a.weekday())
            body = build_week_or_day([wk_mon + timedelta(days=i) for i in range(7)])
        else:
            body = build_month()

        return ft.Container(
            expand=True, bgcolor=WHITE, border_radius=20, border=ft.Border.all(1, BORDER),
            padding=ft.Padding.only(left=28, right=28, top=26, bottom=24),
            content=ft.Column([
                build_cal_header(),
                ft.Container(height=24),
                body,
            ], spacing=0, tight=True),
        )

    # ------------------------------------------------------------------ dialogs & actions
    def open_add_dialog():
        title_f = ft.TextField(label="Task title", hint_text="e.g. Practice calculus problems", autofocus=True)
        day_opts = [(today + timedelta(days=i)).isoformat() for i in range(-1, 7)]
        day_dd = ft.Dropdown(
            label="Day", value=today.isoformat(),
            options=[ft.dropdown.Option(d, "Today" if d == today.isoformat()
                                        else date.fromisoformat(d).strftime("%a, %b %d")) for d in day_opts],
        )
        hours_opts = [ft.dropdown.Option(str(h), fmt(h)) for h in [8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5,
                                                                   12, 13, 14, 14.5, 15, 16, 17]]
        start_dd = ft.Dropdown(label="Start", value="14", options=hours_opts, expand=True)
        dur_dd = ft.Dropdown(label="Duration", value="1", expand=True, options=[
            ft.dropdown.Option("0.5", "30 min"),
            ft.dropdown.Option("1", "1 hour"),
            ft.dropdown.Option("1.5", "1 hr 30 min"),
            ft.dropdown.Option("2", "2 hours"),
        ])
        color_dd = ft.Dropdown(label="Category", value="teal", options=[
            ft.dropdown.Option("teal", "Study / Review"),
            ft.dropdown.Option("purple", "Deep work"),
            ft.dropdown.Option("orange", "Assignment"),
            ft.dropdown.Option("gray", "Personal"),
        ])

        def close_dialog(e=None):
            dlg.open = False
            try:
                page.close(dlg)
            except Exception:
                pass
            try:
                page.pop_dialog(dlg)
            except Exception:
                pass
            try:
                dlg.update()
            except Exception:
                pass
            try:
                page.update()
            except Exception:
                pass

        def save(e):
            name = (title_f.value or "").strip()
            if not name:
                title_f.error_text = "Please enter a title"
                title_f.update()
                return
            st = float(start_dd.value)
            en = min(18.5, st + float(dur_dd.value))
            task_day = date.fromisoformat(day_dd.value)
            created = backend.api_create_task(
                title=name, day=task_day, start=st, end=en, color=color_dd.value, done=False
            )
            S["tasks"].append(created)
            close_dialog()
            render()
            toast(f'Added "{name}" (Saved to DB)')

        dlg = ft.AlertDialog(
            title=T("New task", 20, ft.FontWeight.W_700),
            content=ft.Container(width=380, content=ft.Column(
                [title_f, day_dd, ft.Row([start_dd, dur_dd], spacing=10), color_dd],
                spacing=12, tight=True)),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("Add task", bgcolor=TEAL, color=WHITE, on_click=save),
            ],
        )
        page.show_dialog(dlg)

    SUGGESTIONS = [
        ("Spaced-repetition quiz", 11, 11.5, "teal"),
        ("Summarize lecture slides", 15, 16, "purple"),
        ("Practice past exam Qs", 13, 14, "orange"),
        ("Outline essay draft", 16, 17, "purple"),
    ]

    def ai_suggest(e):
        title, st, en, col = SUGGESTIONS[S["ai_idx"] % len(SUGGESTIONS)]
        S["ai_idx"] += 1
        created = backend.api_create_task(
            title=title, day=today, start=float(st), end=float(en), color=col, done=False
        )
        S["tasks"].append(created)
        S["tab"] = "today"
        S["anchor"] = today
        render()
        toast(f'AI scheduled "{title}" ({fmt(st)}–{fmt(en)})')

    # ------------------------------------------------------------------ layout & render
    def build_placeholder():
        name = {
            "assistant": "AI Assistant",
            "ai": "AI Assistant",
            "flashcards": "Flashcards",
            "studyview": "Study View",
            "planner": "Study planner",
            "timer": "Study timer",
            "profile": "Profile",
        }.get(S["nav"], "Study planner")
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

    def render(update: bool = True):
        root_host.content = build_root()
        if update:
            page.update()

    render(update=False)
    return root_host


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
    page.window.min_width = 1400
    page.window.min_height = 760
    page.window.maximized = True

    page.controls.clear()
    page.add(build_planner_root(page))


def get_view(page: ft.Page) -> ft.View:
    return ft.View(
        route="/studyplanner",
        padding=0,
        bgcolor=BG,
        controls=[build_planner_root(page)],
    )


if __name__ == "__main__":
    ft.app(main)
