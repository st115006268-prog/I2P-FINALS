from __future__ import annotations

import flet as ft
from styles import (
    PRIMARY_TEAL,
    LIGHT_TEAL,
    TEXT_DARK,
    TEXT_GREY,
    BORDER_COLOR,
    PAGE_BG,
    HERO_BG,
    MINT_BTN,
)
from pages.sidebar import build_sidebar


def build_flashcards_view(switch_tab, page: ft.Page | None = None) -> ft.Container:
    from pages import backend

    active_subtab = {"value": "flashcards"}
    search_query = {"value": ""}
    decks_list = backend.api_get_decks()

    def reload_decks():
        nonlocal decks_list
        decks_list = backend.api_get_decks()

    def get_active_hero_deck() -> dict | None:
        if not decks_list:
            return None
        found = next((d for d in decks_list if d.get("deck_id") == backend.CURRENT_DECK_ID), None)
        return found if found is not None else decks_list[0]

    def study_deck(deck_id: int | None, mode: str = "flashcards"):
        if deck_id is not None:
            backend.CURRENT_DECK_ID = deck_id
        backend.CURRENT_STUDY_MODE = mode
        switch_tab("studyview")

    def open_new_deck_dialog(e=None):
        if page is None:
            return
        title_tf = ft.TextField(label="Deck Title", hint_text="e.g. Calculus II", autofocus=True)
        subj_tf = ft.TextField(label="Subject", hint_text="e.g. Mathematics")
        q_tf = ft.TextField(label="First Card Question", hint_text="e.g. What is the fundamental theorem?")
        a_tf = ft.TextField(label="First Card Answer", hint_text="e.g. Links differentiation and integration.")

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

        def save_deck(_):
            t_val = (title_tf.value or "").strip()
            if not t_val:
                title_tf.error_text = "Please enter a deck title"
                title_tf.update()
                return
            s_val = (subj_tf.value or "General Study").strip()
            created = backend.api_create_deck(title=t_val, subject=s_val, accent="#13766B", progress=0.0)
            q_val = (q_tf.value or "").strip()
            a_val = (a_tf.value or "").strip()
            if q_val and a_val and "deck_id" in created:
                backend.api_add_flashcard(created["deck_id"], q_val, a_val)
            if "deck_id" in created:
                backend.CURRENT_DECK_ID = created["deck_id"]
            reload_decks()
            close_dialog()
            render_decks(update=True)

        dlg = ft.AlertDialog(
            title=ft.Text("Create New Deck", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=420,
                content=ft.Column([title_tf, subj_tf, q_tf, a_tf], spacing=12, tight=True),
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("Create Deck", bgcolor=PRIMARY_TEAL, color=ft.Colors.WHITE, on_click=save_deck),
            ],
        )
        page.show_dialog(dlg)


    def open_edit_deck_dialog(deck_data: dict):
        if page is None:
            return
        did = deck_data.get("deck_id", 1)
        title_tf = ft.TextField(label="Deck Title", value=deck_data.get("title", ""), expand=True)
        subj_tf = ft.TextField(label="Subject", value=deck_data.get("subject", "General Study"), expand=True)

        cards_data = backend.api_get_deck_cards(did)
        card_fields: list[dict] = []
        cards_col = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=260)

        def rebuild_card_rows():
            rows = []
            for idx, cf in enumerate(card_fields):
                if cf.get("deleted"):
                    continue
                q_input = cf["q"]
                a_input = cf["a"]

                def make_delete_handler(item_ref):
                    def _del(_e):
                        item_ref["deleted"] = True
                        rebuild_card_rows()
                        page.update()
                    return _del

                rows.append(
                    ft.Container(
                        bgcolor="#F9FAFB",
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=10,
                        padding=10,
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(f"Card #{idx + 1}", size=12, weight=ft.FontWeight.BOLD, color=PRIMARY_TEAL),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            icon_size=18,
                                            icon_color="#DC2626",
                                            tooltip="Delete card",
                                            on_click=make_delete_handler(cf),
                                        ),
                                    ],
                                ),
                                q_input,
                                a_input,
                            ],
                        ),
                    )
                )
            if not rows:
                rows.append(
                    ft.Text("No cards yet. Add a new card below!", size=13, color=TEXT_GREY)
                )
            cards_col.controls = rows

        for c in cards_data:
            card_fields.append({
                "card_id": c.get("card_id"),
                "q": ft.TextField(label="Question", value=c.get("question", ""), dense=True),
                "a": ft.TextField(label="Answer", value=c.get("answer", ""), dense=True),
                "deleted": False,
            })

        rebuild_card_rows()

        new_q_tf = ft.TextField(label="New Card Question", hint_text="Enter question...", dense=True, expand=True)
        new_a_tf = ft.TextField(label="New Card Answer", hint_text="Enter answer...", dense=True, expand=True)

        def add_card_inline(_):
            nq = (new_q_tf.value or "").strip()
            na = (new_a_tf.value or "").strip()
            if not nq or not na:
                return
            card_fields.append({
                "card_id": None,
                "q": ft.TextField(label="Question", value=nq, dense=True),
                "a": ft.TextField(label="Answer", value=na, dense=True),
                "deleted": False,
            })
            new_q_tf.value = ""
            new_a_tf.value = ""
            rebuild_card_rows()
            page.update()

        def save_changes(_):
            new_t = (title_tf.value or "").strip() or deck_data.get("title", "Untitled Deck")
            new_s = (subj_tf.value or "").strip() or deck_data.get("subject", "General Study")

            # Also save any text sitting in the "New Card" inputs if the user typed it and clicked Save directly
            pending_q = (new_q_tf.value or "").strip()
            pending_a = (new_a_tf.value or "").strip()
            if pending_q and pending_a:
                card_fields.append({
                    "card_id": None,
                    "q": ft.TextField(value=pending_q),
                    "a": ft.TextField(value=pending_a),
                    "deleted": False,
                })

            for cf in card_fields:
                cid = cf.get("card_id")
                if cf.get("deleted"):
                    if cid is not None:
                        backend.api_delete_flashcard(cid)
                    continue
                qv = (cf["q"].value or "").strip()
                av = (cf["a"].value or "").strip()
                if not qv or not av:
                    continue
                if cid is not None:
                    backend.api_update_flashcard(cid, question=qv, answer=av)
                else:
                    backend.api_add_flashcard(did, qv, av)

            # Recompute progress safely with updated card count
            updated_cards = backend.api_get_deck_cards(did)
            total_c = len(updated_cards)
            if total_c == 0:
                last_idx = 0
                new_prog = 0.0
            else:
                old_prog = float(deck_data.get("progress", 0.0))
                orig_last = int(deck_data.get("last_card_idx", 0))
                last_idx = max(0, min(orig_last, total_c - 1))
                if old_prog == 0.0:
                    new_prog = 0.0
                else:
                    new_prog = round(min(1.0, (last_idx + 1) / total_c), 2)

            backend.api_update_deck(did, title=new_t, subject=new_s, progress=new_prog, last_card_idx=last_idx)
            backend.CURRENT_DECK_ID = did
            reload_decks()
            close_dialog()
            render_decks(update=True)

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

        dlg = ft.AlertDialog(
            title=ft.Text(f"Edit Deck · {deck_data.get('title', '')}", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=520,
                content=ft.Column(
                    spacing=12,
                    tight=True,
                    controls=[
                        ft.Row([title_tf, subj_tf], spacing=10),
                        ft.Divider(height=1, color=BORDER_COLOR),
                        ft.Text("Cards in this deck", size=14, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                        cards_col,
                        ft.Divider(height=1, color=BORDER_COLOR),
                        ft.Text("Add a new card", size=13, weight=ft.FontWeight.W_600, color=PRIMARY_TEAL),
                        ft.Row([new_q_tf, new_a_tf], spacing=8),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.TextButton(
                                    "+ Add card to list",
                                    on_click=add_card_inline,
                                )
                            ],
                        ),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("Save Changes", bgcolor=PRIMARY_TEAL, color=ft.Colors.WHITE, on_click=save_changes),
            ],
        )
        page.show_dialog(dlg)

    def create_ai_suggested_deck(e=None):
        created = backend.api_create_deck(
            title=f"AI Review #{len(decks_list) + 1}",
            subject="AI Generated · Active Recall",
            accent="#5B5BD6",
            progress=0.33,
        )
        if "deck_id" in created:
            did = created["deck_id"]
            backend.api_add_flashcard(
                did,
                "What is active recall?",
                "Actively stimulating memory during the learning process.",
            )
            backend.api_add_flashcard(
                did,
                "What is spaced repetition?",
                "Reviewing information at systematically increasing intervals.",
            )
            backend.api_add_flashcard(
                did,
                "Why is interleaving effective?",
                "Mixing different topics strengthens concept discrimination and long-term transfer.",
            )
            backend.CURRENT_DECK_ID = did
        reload_decks()
        render_decks(update=True)

    def deck_card(deck_data: dict) -> ft.Container:
        accent_color = deck_data.get("accent", "#13766B")
        title = deck_data.get("title", "Untitled Deck")
        subtitle = deck_data.get("subtitle", "")
        progress_val = float(deck_data.get("progress", 0.0))
        deck_id = deck_data.get("deck_id")
        card_count = int(deck_data.get("card_count", 0))
        last_idx = int(deck_data.get("last_card_idx", 0))
        if card_count > 0 and last_idx + 1 < card_count and progress_val >= 1.0:
            progress_val = round((last_idx + 1) / card_count, 2)
        pct_str = f"{int(round(progress_val * 100))}%"
        if card_count == 0:
            card_pos_str = "0 cards · 0%"
        else:
            cur_card = min(last_idx + 1, card_count)
            card_pos_str = f"Card {cur_card} of {card_count} · {pct_str}"

        return ft.Container(
            expand=True,
            height=238,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=16,
            padding=24,
            shadow=ft.BoxShadow(
                blur_radius=6,
                color="#08111827",
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                width=34,
                                height=4,
                                bgcolor=accent_color,
                                border_radius=2,
                            ),
                            ft.Text(card_pos_str, size=11.5, color=TEXT_GREY, weight=ft.FontWeight.W_500),
                        ],
                    ),
                    ft.Container(height=14),
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                    ft.Container(height=6),
                    ft.Container(
                        height=36,
                        alignment=ft.Alignment.TOP_LEFT,
                        content=ft.Text(subtitle, size=13, color=TEXT_GREY),
                    ),
                    ft.Container(height=10),
                    ft.ProgressBar(
                        value=progress_val,
                        color=accent_color,
                        bgcolor="#E5E7EB",
                        height=6,
                        border_radius=3,
                    ),
                    ft.Container(expand=True),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Button(
                                content=ft.Text(
                                    "Study",
                                    color=ft.Colors.WHITE,
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                ),
                                bgcolor=PRIMARY_TEAL,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.Padding.symmetric(horizontal=18, vertical=10),
                                    elevation=0,
                                ),
                                on_click=lambda _, did=deck_id: study_deck(did, "flashcards"),
                            ),
                            ft.Button(
                                content=ft.Text(
                                    "Quiz",
                                    color=PRIMARY_TEAL,
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                ),
                                bgcolor=ft.Colors.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, "#D1D5DB"),
                                    padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                                    elevation=0,
                                ),
                                on_click=lambda _, did=deck_id: study_deck(did, "quiz"),
                            ),
                            ft.Button(
                                content=ft.Text(
                                    "Edit",
                                    color=PRIMARY_TEAL,
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                ),
                                bgcolor=ft.Colors.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    side=ft.BorderSide(1, "#D1D5DB"),
                                    padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                                    elevation=0,
                                ),
                                on_click=lambda _, d=deck_data: open_edit_deck_dialog(d),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def create_deck_card() -> ft.Container:
        return ft.Container(
            expand=True,
            height=238,
            bgcolor="#E7F4F1",
            border=ft.Border.all(1.5, "#8EC5BE"),
            border_radius=16,
            padding=24,
            alignment=ft.Alignment.CENTER,
            ink=True,
            on_click=open_new_deck_dialog,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.ADD, color=PRIMARY_TEAL, size=22),
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        width=44,
                        height=44,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Text(
                        "Create new deck",
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY_TEAL,
                    ),
                ],
            ),
        )

    decks_count_text = ft.Text(f"{len(decks_list)} decks", size=14, color=TEXT_GREY)
    decks_rows = ft.Column(spacing=20)
    quiz_decks_rows = ft.Column(spacing=14)

    hero_title_text = ft.Text("", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    hero_sub_text = ft.Text("Continue studying", size=13, color="#A7C4BE")
    hero_btn_label = ft.Text("Continue studying", size=14, color=HERO_BG, weight=ft.FontWeight.BOLD)

    def on_hero_click(_):
        hd = get_active_hero_deck()
        if hd and hd.get("deck_id"):
            study_deck(hd.get("deck_id"), "flashcards")
        else:
            open_new_deck_dialog()

    hero_btn = ft.Button(
        bgcolor=MINT_BTN,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.Padding.symmetric(horizontal=22, vertical=14),
            elevation=0,
        ),
        content=hero_btn_label,
        on_click=on_hero_click,
    )

    def sync_hero_banner():
        hd = get_active_hero_deck()
        if not hd:
            hero_title_text.value = "No flashcard decks yet"
            hero_sub_text.value = "Create your first deck to practice active recall with spaced repetition"
            hero_btn_label.value = "Create deck"
            return
        c_cnt = int(hd.get("card_count", 0))
        last_i = int(hd.get("last_card_idx", 0))
        prog_val = float(hd.get("progress", 0.0))
        if c_cnt > 0 and last_i + 1 < c_cnt and prog_val >= 1.0:
            prog_val = round((last_i + 1) / c_cnt, 2)
        c_word = "card" if c_cnt == 1 else "cards"
        hero_title_text.value = f"{hd.get('title', 'Untitled')} · {c_cnt} {c_word}"
        if c_cnt == 0:
            hero_sub_text.value = "No cards in this deck yet · Add cards to begin studying"
            hero_btn_label.value = "Add cards"
        else:
            cur_card = min(last_i + 1, c_cnt)
            hero_sub_text.value = (
                f"Continue studying · Last on card {cur_card} of {c_cnt} "
                f"({int(round(prog_val * 100))}% complete)"
            )
            hero_btn_label.value = "Continue studying"

    def render_decks(update: bool = True):
        sync_hero_banner()
        q = search_query["value"].strip().lower()
        filtered = [
            d
            for d in decks_list
            if not q or q in d["title"].lower() or q in d["subtitle"].lower()
        ]
        decks_count_text.value = (
            f"{len(filtered)} deck" if len(filtered) == 1 else f"{len(filtered)} decks"
        )

        cards: list[ft.Control] = [deck_card(d) for d in filtered]
        cards.append(create_deck_card())

        rows = []
        for i in range(0, len(cards), 3):
            row_items = cards[i : i + 3]
            while len(row_items) < 3:
                row_items.append(ft.Container(expand=True))
            rows.append(ft.Row(spacing=20, controls=row_items))

        decks_rows.controls = rows

        # Also populate the Quiz subtab list so users can launch any deck's quiz from the Quiz tab
        q_rows = []
        for d in filtered:
            did = d.get("deck_id")
            q_rows.append(
                ft.Container(
                    bgcolor="#F9FAFB",
                    border=ft.Border.all(1, BORDER_COLOR),
                    border_radius=12,
                    padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(d["title"], size=16, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                    ft.Text(d["subtitle"], size=13, color=TEXT_GREY),
                                ],
                            ),
                            ft.Button(
                                bgcolor=PRIMARY_TEAL,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    padding=ft.Padding.symmetric(horizontal=18, vertical=10),
                                ),
                                content=ft.Text(
                                    f"Start {d['title']} Quiz",
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.W_600,
                                ),
                                on_click=lambda _, deck_id=did: study_deck(deck_id, "quiz"),
                            ),
                        ],
                    ),
                )
            )
        if not q_rows:
            q_rows = [
                ft.Container(
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.LAYERS_OUTLINED, size=40, color=TEXT_GREY),
                            ft.Text("No decks available for quiz yet.", size=16, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                            ft.Text("Create a deck with cards to start quizzing!", size=13, color=TEXT_GREY),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                )
            ]
        quiz_decks_rows.controls = q_rows

        if update and page is not None:
            page.update()

    def on_search(e: ft.ControlEvent):
        search_query["value"] = e.control.value or ""
        render_decks(update=True)

    # Top white header bar
    top_header = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.only(bottom=ft.BorderSide(1, BORDER_COLOR)),
        padding=ft.Padding.symmetric(horizontal=36, vertical=20),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Flashcards",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_DARK,
                        ),
                        ft.Text(
                            "Your decks and quizzes", size=14, color=TEXT_GREY
                        ),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=240,
                            height=42,
                            bgcolor="#F9FAFB",
                            border=ft.Border.all(1, BORDER_COLOR),
                            border_radius=10,
                            padding=ft.Padding.symmetric(horizontal=12),
                            content=ft.Row(
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.SEARCH, size=18, color=TEXT_GREY
                                    ),
                                    ft.TextField(
                                        hint_text="Search decks",
                                        text_size=14,
                                        hint_style=ft.TextStyle(
                                            size=14, color=TEXT_GREY
                                        ),
                                        border=ft.InputBorder.NONE,
                                        bgcolor=ft.Colors.TRANSPARENT,
                                        dense=True,
                                        expand=True,
                                        content_padding=ft.Padding.symmetric(
                                            vertical=10
                                        ),
                                        on_change=on_search,
                                    ),
                                ],
                            ),
                        ),
                        ft.Button(
                            height=42,
                            bgcolor=LIGHT_TEAL,
                            on_click=create_ai_suggested_deck,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=ft.Padding.symmetric(horizontal=16),
                                elevation=0,
                            ),
                            content=ft.Row(
                                spacing=6,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.AUTO_AWESOME,
                                        size=16,
                                        color=PRIMARY_TEAL,
                                    ),
                                    ft.Text(
                                        "AI suggested deck",
                                        size=14,
                                        color=PRIMARY_TEAL,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ],
                            ),
                        ),
                        ft.Button(
                            height=42,
                            bgcolor=PRIMARY_TEAL,
                            on_click=open_new_deck_dialog,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=ft.Padding.symmetric(horizontal=18),
                                elevation=0,
                            ),
                            content=ft.Row(
                                spacing=6,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.ADD,
                                        size=18,
                                        color=ft.Colors.WHITE,
                                    ),
                                    ft.Text(
                                        "New deck",
                                        size=14,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    flashcards_tab = ft.Container(
        padding=ft.Padding.symmetric(horizontal=24, vertical=10),
        border_radius=10,
        ink=True,
        on_click=lambda _: set_subtab("flashcards"),
    )
    quiz_tab = ft.Container(
        padding=ft.Padding.symmetric(horizontal=24, vertical=10),
        border_radius=10,
        ink=True,
        on_click=lambda _: set_subtab("quiz"),
    )

    tabs_row = ft.Row(spacing=8, controls=[flashcards_tab, quiz_tab])

    hero_banner = ft.Container(
        bgcolor=HERO_BG,
        border_radius=18,
        padding=ft.Padding.symmetric(horizontal=32, vertical=28),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=8,
                    controls=[
                        hero_sub_text,
                        hero_title_text,
                    ],
                ),
                hero_btn,
            ],
        ),
    )

    decks_header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(
                "My decks", size=20, weight=ft.FontWeight.BOLD, color=TEXT_DARK
            ),
            decks_count_text,
        ],
    )

    quiz_placeholder = ft.Container(
        visible=False,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=32,
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Text(
                    "Practice Quizzes",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_DARK,
                ),
                ft.Text(
                    "Select any deck below to launch an interactive multiple-choice quiz generated from your cards.",
                    size=14,
                    color=TEXT_GREY,
                ),
                ft.Container(height=6),
                quiz_decks_rows,
            ],
        ),
    )

    flashcards_section = ft.Column(
        spacing=0,
        controls=[
            hero_banner,
            ft.Container(height=28),
            decks_header,
            ft.Container(height=16),
            decks_rows,
        ],
    )

    def sync_tabs(update: bool = True):
        is_fc = active_subtab["value"] == "flashcards"

        flashcards_tab.bgcolor = ft.Colors.WHITE if is_fc else ft.Colors.TRANSPARENT
        flashcards_tab.border = ft.Border.all(1, BORDER_COLOR) if is_fc else None
        flashcards_tab.content = ft.Text(
            "Flashcards",
            size=14,
            color=PRIMARY_TEAL if is_fc else TEXT_GREY,
            weight=ft.FontWeight.W_600 if is_fc else ft.FontWeight.W_500,
        )

        quiz_tab.bgcolor = ft.Colors.WHITE if not is_fc else ft.Colors.TRANSPARENT
        quiz_tab.border = ft.Border.all(1, BORDER_COLOR) if not is_fc else None
        quiz_tab.content = ft.Text(
            "Quiz",
            size=14,
            color=PRIMARY_TEAL if not is_fc else TEXT_GREY,
            weight=ft.FontWeight.W_600 if not is_fc else ft.FontWeight.W_500,
        )

        flashcards_section.visible = is_fc
        quiz_placeholder.visible = not is_fc

        if update and page is not None:
            page.update()

    def set_subtab(val: str):
        active_subtab["value"] = val
        sync_tabs(update=True)

    render_decks(update=False)
    sync_tabs(update=False)

    body = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
        controls=[
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=36, vertical=24),
                content=ft.Column(
                    spacing=0,
                    controls=[
                        tabs_row,
                        ft.Container(height=22),
                        flashcards_section,
                        quiz_placeholder,
                    ],
                ),
            )
        ],
    )

    return ft.Container(
        expand=True,
        bgcolor=PAGE_BG,
        content=ft.Column(
            spacing=0,
            expand=True,
            controls=[top_header, body],
        ),
    )


def get_view(page: ft.Page) -> ft.View:
    route_map = {
        "assistant": "/ai-assistant",
        "flashcards": "/flashcards",
        "planner": "/studyplanner",
        "timer": "/studytimer",
        "profile": "/profile",
        "studyview": "/studyview",
    }

    def switch_tab(tab: str):
        target = route_map.get(tab, "/")
        if target != page.route:
            page.go(target)

    return ft.View(
        route="/flashcards",
        padding=0,
        bgcolor=PAGE_BG,
        controls=[
            ft.Row(
                [
                    build_sidebar("flashcards", switch_tab, page),
                    build_flashcards_view(switch_tab, page),
                ],
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        ],
    )
