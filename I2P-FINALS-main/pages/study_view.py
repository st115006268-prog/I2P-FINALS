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

DISTRACTORS = [
    "O(n²) quadratic time complexity",
    "Depends only on ambient temperature",
    "Equal to the derivative of velocity with respect to distance",
    "Only applies in non-inertial reference frames",
]


def build_ai_study_view(page: ft.Page, switch_tab) -> ft.Container:
    from pages import backend

    all_decks = backend.api_get_decks()
    active_deck = next((d for d in all_decks if d.get("deck_id") == backend.CURRENT_DECK_ID), None)
    if not active_deck and all_decks:
        active_deck = all_decks[0]
        backend.CURRENT_DECK_ID = active_deck.get("deck_id", 1)

    deck_id = active_deck.get("deck_id", 1) if active_deck else 1
    deck_name_str = active_deck["title"] if active_deck else "Untitled Deck"
    subject_str = active_deck.get("subject", "General Study") if active_deck else "General Study"
    deck_sub_str = f"{subject_str} · Flashcard study"

    db_cards = backend.api_get_deck_cards(deck_id) if active_deck else []
    active_cards: list[dict] = (
        [{"card_id": c.get("card_id"), "question": c["question"], "answer": c["answer"]} for c in db_cards]
        if db_cards
        else []
    )

    initial_idx = int(active_deck.get("last_card_idx", 0)) if active_deck else 0
    if active_cards:
        initial_idx = max(0, min(initial_idx, len(active_cards) - 1))
    else:
        initial_idx = 0

    initial_mode = getattr(backend, "CURRENT_STUDY_MODE", "flashcards")
    if initial_mode not in ("flashcards", "quiz"):
        initial_mode = "flashcards"

    state = {
        "mode": initial_mode,
        "idx": initial_idx,
        "revealed": False,
        "max_idx": initial_idx,
        # Quiz state
        "quiz_idx": 0,
        "quiz_selected": None,
        "quiz_score": 0,
        "quiz_answered": {},  # quiz_idx -> (selected_answer, is_correct)
    }

    def persist_progress():
        """Save last_card_idx and progress to SQLite for the active deck."""
        if not active_deck or not active_cards:
            return
        total = max(1, len(active_cards))
        cur_i = max(0, min(state["idx"], total - 1))
        state["max_idx"] = max(state["max_idx"], cur_i)
        prog = round(( cur_i + 1 ) / total, 2)
        try:
            backend.CURRENT_DECK_ID = deck_id
            backend.api_update_deck(deck_id, progress=prog, last_card_idx=cur_i)
        except Exception:
            pass

    # Persist initial visit so "Continue studying" on /flashcards reflects the last opened deck & card
    persist_progress()

    has_cards = len(active_cards) > 0
    cur_q = active_cards[state["idx"]]["question"] if has_cards else "No flashcards in this deck yet"
    cur_sub = "Take a moment to recall the answer." if has_cards else "Click '+ Add card' above to create cards for this deck."

    badge_text = ft.Text("QUESTION" if has_cards else "EMPTY DECK", size=12, weight=ft.FontWeight.BOLD, color=PRIMARY_TEAL)
    card_subject_text = ft.Text(subject_str, size=14, color=TEXT_GREY)
    card_main_text = ft.Text(
        cur_q,
        size=32,
        weight=ft.FontWeight.BOLD,
        color=TEXT_DARK,
        text_align=ft.TextAlign.CENTER,
    )
    card_sub_text = ft.Text(
        cur_sub,
        size=16,
        color=TEXT_GREY,
        text_align=ft.TextAlign.CENTER,
    )
    reveal_label = ft.Text("Reveal answer" if has_cards else "Add card", color=ft.Colors.WHITE, weight=ft.FontWeight.W_600)
    progress_label = ft.Text(
        f"Card {state['idx'] + 1} of {len(active_cards)}" if has_cards else "0 cards", color=TEXT_GREY, size=14
    )
    progress_bar = ft.ProgressBar(
        value=(state["idx"] + 1) / max(1, len(active_cards)) if has_cards else 0.0,
        color=PRIMARY_TEAL,
        bgcolor=BORDER_COLOR,
        height=6,
    )
    counter_label = ft.Text(f"{state['idx'] + 1} / {len(active_cards)}" if has_cards else "0 / 0", color=TEXT_GREY, size=14)


    def sync_card(update: bool = True):
        if not active_cards:
            badge_text.value = "EMPTY DECK"
            card_main_text.value = "No flashcards in this deck yet"
            card_sub_text.value = "Click '+ Add card' above to create cards for this deck."
            reveal_label.value = "Add card"
            progress_label.value = "0 cards"
            progress_bar.value = 0.0
            counter_label.value = "0 / 0"
            if update:
                page.update()
            return
        idx = max(0, min(state["idx"], len(active_cards) - 1))
        state["idx"] = idx
        card_obj = active_cards[idx]
        q, a = card_obj["question"], card_obj["answer"]
        if state["revealed"]:
            badge_text.value = "ANSWER"
            card_main_text.value = a
            card_sub_text.value = f"Question: {q}"
            reveal_label.value = "Show question"
        else:
            badge_text.value = "QUESTION"
            card_main_text.value = q
            card_sub_text.value = "Take a moment to recall the answer."
            reveal_label.value = "Reveal answer"
        progress_label.value = f"Card {idx + 1} of {len(active_cards)}"
        progress_bar.value = (idx + 1) / max(1, len(active_cards))
        counter_label.value = f"{idx + 1} / {len(active_cards)}"
        persist_progress()
        if update:
            page.update()

    def toggle_reveal(_):
        if not active_cards:
            open_add_card_dialog()
            return
        state["revealed"] = not state["revealed"]
        sync_card()

    def prev_card(_):
        if not active_cards:
            return
        state["idx"] = (state["idx"] - 1) % len(active_cards)
        state["revealed"] = False
        sync_card()

    def next_card(_):
        if not active_cards:
            return
        state["idx"] = (state["idx"] + 1) % len(active_cards)
        state["revealed"] = False
        sync_card()

    def open_add_card_dialog(_=None):
        q_tf = ft.TextField(label="Question", autofocus=True)
        a_tf = ft.TextField(label="Answer")

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

        def save_card(_e):
            q_val = (q_tf.value or "").strip()
            a_val = (a_tf.value or "").strip()
            if not q_val or not a_val:
                return
            created_card = backend.api_add_flashcard(deck_id, q_val, a_val)
            active_cards.append({
                "card_id": created_card.get("card_id"),
                "question": q_val,
                "answer": a_val,
            })
            if len(active_cards) == 1:
                state["idx"] = 0
            else:
                state["idx"] = max(0, min(state["idx"], len(active_cards) - 2))
            state["revealed"] = False
            close_dialog()
            sync_card()
            render_quiz(update=False)
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Add Card to {deck_name_str}", weight=ft.FontWeight.BOLD),
            content=ft.Container(width=380, content=ft.Column([q_tf, a_tf], spacing=12, tight=True)),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("Save Card", bgcolor=PRIMARY_TEAL, color=ft.Colors.WHITE, on_click=save_card),
            ],
        )
        page.show_dialog(dlg)

    def open_edit_current_card_dialog(_=None):
        if not active_cards:
            open_add_card_dialog()
            return
        idx = max(0, min(state["idx"], len(active_cards) - 1))
        card_obj = active_cards[idx]
        q_tf = ft.TextField(label="Question", value=card_obj["question"], autofocus=True)
        a_tf = ft.TextField(label="Answer", value=card_obj["answer"])

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

        def save_edited_card(_e):
            q_val = (q_tf.value or "").strip()
            a_val = (a_tf.value or "").strip()
            if not q_val or not a_val:
                return
            cid = card_obj.get("card_id")
            if cid is not None:
                backend.api_update_flashcard(cid, question=q_val, answer=a_val)
            card_obj["question"] = q_val
            card_obj["answer"] = a_val
            close_dialog()
            sync_card()
            render_quiz(update=False)
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Edit Card #{idx + 1}", weight=ft.FontWeight.BOLD),
            content=ft.Container(width=380, content=ft.Column([q_tf, a_tf], spacing=12, tight=True)),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("Save Changes", bgcolor=PRIMARY_TEAL, color=ft.Colors.WHITE, on_click=save_edited_card),
            ],
        )
        page.show_dialog(dlg)

    # ------------------------------------------------------------------ Quiz view inside Study View
    quiz_host = ft.Container(visible=(state["mode"] == "quiz"))

    def build_quiz_options(q_idx: int) -> list[str]:
        if not active_cards or q_idx >= len(active_cards):
            return ["Option 1", "Option 2", "Option 3", "Option 4"]
        correct = active_cards[q_idx]["answer"]
        other_answers = [c["answer"] for i, c in enumerate(active_cards) if i != q_idx and c["answer"] != correct]
        for d in DISTRACTORS:
            if len(other_answers) >= 3:
                break
            if d != correct and d not in other_answers:
                other_answers.append(d)
        opts = other_answers[:3]
        # Deterministic insertion position based on q_idx so options don't jump on re-render
        insert_pos = (q_idx * 7 + len(correct)) % (len(opts) + 1)
        opts.insert(insert_pos, correct)
        return opts

    def render_quiz(update: bool = True):
        if not active_cards:
            quiz_host.content = ft.Container(
                padding=60,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.QUIZ_OUTLINED, size=48, color=TEXT_GREY),
                        ft.Text("No flashcards in this deck yet", size=18, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                        ft.Text("Add cards using '+ Add card' above to start testing your knowledge.", size=14, color=TEXT_GREY),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
            )
            if update:
                page.update()
            return
        total_q = max(1, len(active_cards))
        q_idx = max(0, min(state["quiz_idx"], total_q - 1))
        state["quiz_idx"] = q_idx
        current_card = active_cards[q_idx]
        correct_ans = current_card["answer"]
        options = build_quiz_options(q_idx)
        answered_info = state["quiz_answered"].get(q_idx)


        def select_option(opt_text: str):
            if q_idx in state["quiz_answered"]:
                return
            is_corr = (opt_text == correct_ans)
            state["quiz_answered"][q_idx] = (opt_text, is_corr)
            if is_corr:
                state["quiz_score"] += 1
            # Also sync deck progress when answering quiz questions
            state["idx"] = q_idx
            persist_progress()
            render_quiz(update=True)

        def prev_q(_):
            state["quiz_idx"] = (state["quiz_idx"] - 1) % total_q
            render_quiz(update=True)

        def next_q(_):
            state["quiz_idx"] = (state["quiz_idx"] + 1) % total_q
            render_quiz(update=True)

        def reset_quiz(_):
            state["quiz_idx"] = 0
            state["quiz_score"] = 0
            state["quiz_answered"] = {}
            render_quiz(update=True)

        option_controls = []
        for i, opt in enumerate(options):
            letter = ["A", "B", "C", "D"][i % 4]
            bg = ft.Colors.WHITE
            border_c = BORDER_COLOR
            txt_c = TEXT_DARK
            if answered_info is not None:
                chosen_opt, _ = answered_info
                if opt == correct_ans:
                    bg = "#E6F4EA"
                    border_c = "#16A34A"
                    txt_c = "#14532D"
                elif opt == chosen_opt:
                    bg = "#FEE2E2"
                    border_c = "#DC2626"
                    txt_c = "#7F1D1D"

            option_controls.append(
                ft.Container(
                    bgcolor=bg,
                    border=ft.Border.all(1.5, border_c),
                    border_radius=12,
                    padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                    ink=True,
                    on_click=lambda _, o=opt: select_option(o),
                    content=ft.Row(
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=32,
                                height=32,
                                border_radius=8,
                                bgcolor=LIGHT_TEAL,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(letter, weight=ft.FontWeight.BOLD, color=PRIMARY_TEAL),
                            ),
                            ft.Text(opt, size=15, color=txt_c, weight=ft.FontWeight.W_500, expand=True),
                        ],
                    ),
                )
            )

        feedback_banner = ft.Container(visible=False)
        if answered_info is not None:
            _, is_corr = answered_info
            feedback_banner = ft.Container(
                visible=True,
                bgcolor="#E6F4EA" if is_corr else "#FEE2E2",
                border_radius=10,
                padding=ft.Padding.symmetric(horizontal=18, vertical=12),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Correct! Great recall." if is_corr else f"Not quite. Correct answer: {correct_ans}",
                            color="#15803D" if is_corr else "#B91C1C",
                            weight=ft.FontWeight.W_600,
                            size=14,
                        ),
                        ft.Text(
                            f"Score: {state['quiz_score']} / {len(state['quiz_answered'])}",
                            color=TEXT_DARK,
                            weight=ft.FontWeight.BOLD,
                            size=13,
                        ),
                    ],
                ),
            )

        quiz_host.content = ft.Column(
            spacing=18,
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(f"{deck_name_str} · Practice Quiz", size=20, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                    ft.Text(
                                        f"Score: {state['quiz_score']} / {total_q}",
                                        color=PRIMARY_TEAL,
                                        weight=ft.FontWeight.BOLD,
                                        size=15,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Row(
                                [
                                    ft.Text(f"{subject_str} · Multiple-choice recall", color=TEXT_GREY, size=14),
                                    ft.Text(f"Question {q_idx + 1} of {total_q}", color=TEXT_GREY, size=14),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.ProgressBar(value=(q_idx + 1) / total_q, color=PRIMARY_TEAL, bgcolor=BORDER_COLOR, height=6),
                        ],
                        spacing=8,
                    ),
                ),
                ft.Container(
                    bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(1, BORDER_COLOR),
                    border_radius=16,
                    padding=32,
                    content=ft.Column(
                        spacing=20,
                        controls=[
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text("MULTIPLE CHOICE", size=12, weight=ft.FontWeight.BOLD, color=PRIMARY_TEAL),
                                        bgcolor=LIGHT_TEAL,
                                        padding=ft.Padding(12, 6, 12, 6),
                                        border_radius=16,
                                    ),
                                    ft.TextButton("Reset quiz", on_click=reset_quiz),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(
                                current_card["question"],
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_DARK,
                            ),
                            ft.Column(spacing=12, controls=option_controls),
                            feedback_banner,
                        ],
                    ),
                ),
                ft.Row(
                    [
                        ft.Button(
                            content=ft.Row([
                                ft.Icon(ft.Icons.ARROW_BACK, size=18, color=PRIMARY_TEAL),
                                ft.Text("Previous Question", color=PRIMARY_TEAL),
                            ]),
                            bgcolor=LIGHT_TEAL,
                            style=ft.ButtonStyle(padding=16, shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=prev_q,
                        ),
                        ft.Text(f"{q_idx + 1} / {total_q}", color=TEXT_GREY, size=14),
                        ft.Button(
                            content=ft.Row([
                                ft.Text("Next Question", color=ft.Colors.WHITE),
                                ft.Icon(ft.Icons.ARROW_FORWARD, size=18, color=ft.Colors.WHITE),
                            ], spacing=4),
                            bgcolor=PRIMARY_TEAL,
                            style=ft.ButtonStyle(padding=16, shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=next_q,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
        )
        if update:
            page.update()

    header_row = ft.Row(
        [
            ft.Column(
                [
                    ft.Text("Flashcards", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                    ft.Text("Your decks and quizzes", size=14, color=TEXT_GREY),
                ],
                spacing=4,
            ),
            ft.Row([
                ft.Button(
                    content=ft.Text("Edit card", color=PRIMARY_TEAL, weight=ft.FontWeight.W_600),
                    bgcolor=LIGHT_TEAL,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=12),
                    on_click=open_edit_current_card_dialog,
                ),
                ft.Button(
                    content=ft.Text("+ Add card", color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                    bgcolor=PRIMARY_TEAL,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=12),
                    on_click=open_add_card_dialog,
                ),
            ], spacing=10),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    fc_tab_btn = ft.Container(
        padding=ft.Padding(16, 8, 16, 8),
        ink=True,
        on_click=lambda _: set_mode("flashcards"),
    )
    quiz_tab_btn = ft.Container(
        padding=ft.Padding(16, 8, 16, 8),
        ink=True,
        on_click=lambda _: set_mode("quiz"),
    )

    tabs_row = ft.Container(
        content=ft.Row(
            [
                fc_tab_btn,
                quiz_tab_btn,
                ft.Container(expand=True),
                ft.Button(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ARROW_BACK, size=16, color=TEXT_GREY),
                        ft.Text("Back to decks", color=TEXT_GREY),
                    ]),
                    bgcolor=ft.Colors.TRANSPARENT,
                    on_click=lambda _: switch_tab("flashcards"),
                ),
            ],
        ),
        margin=ft.Margin(0, 24, 0, 24),
    )

    deck_title = ft.Container(
        content=ft.Column(
            [
                ft.Text(deck_name_str, size=20, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Row(
                    [
                        ft.Text(deck_sub_str, color=TEXT_GREY, size=14),
                        progress_label,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                progress_bar,
            ],
            spacing=8,
        ),
        margin=ft.Margin(0, 0, 0, 24),
    )

    flashcard = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=40,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=badge_text,
                            bgcolor=LIGHT_TEAL,
                            padding=ft.Padding(12, 6, 12, 6),
                            border_radius=16,
                        ),
                        card_subject_text,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=60),
                card_main_text,
                card_sub_text,
                ft.Container(height=60),
                ft.Row(
                    [
                        ft.Button(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.VISIBILITY, color=ft.Colors.WHITE, size=18),
                                    reveal_label,
                                ],
                                spacing=8,
                            ),
                            bgcolor=PRIMARY_TEAL,
                            style=ft.ButtonStyle(padding=16, shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=toggle_reveal,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    card_navigation = ft.Container(
        content=ft.Row(
            [
                ft.Button(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ARROW_BACK, size=18, color=PRIMARY_TEAL),
                        ft.Text("Previous", color=PRIMARY_TEAL),
                    ]),
                    bgcolor=LIGHT_TEAL,
                    style=ft.ButtonStyle(padding=16, shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=prev_card,
                ),
                counter_label,
                ft.Button(
                    content=ft.Row(
                        [
                            ft.Text("Next", color=ft.Colors.WHITE),
                            ft.Icon(ft.Icons.ARROW_FORWARD, size=18, color=ft.Colors.WHITE),
                        ],
                        spacing=4,
                    ),
                    bgcolor=PRIMARY_TEAL,
                    style=ft.ButtonStyle(padding=16, shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=next_card,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        margin=ft.Margin(0, 24, 0, 0),
    )

    footer_text = ft.Text(
        "Recall first, then reveal. Go at your own pace.",
        color=TEXT_GREY,
        size=13,
        text_align=ft.TextAlign.CENTER,
    )

    flashcards_study_section = ft.Column(
        visible=(state["mode"] == "flashcards"),
        spacing=0,
        controls=[
            deck_title,
            flashcard,
            card_navigation,
            ft.Container(content=footer_text, alignment=ft.Alignment.CENTER, margin=ft.Margin(0, 24, 0, 0)),
        ],
    )

    def sync_mode_tabs(update: bool = True):
        is_fc = state["mode"] == "flashcards"
        fc_tab_btn.content = ft.Text(
            "Flashcards",
            color=PRIMARY_TEAL if is_fc else TEXT_GREY,
            weight=ft.FontWeight.W_600 if is_fc else ft.FontWeight.W_500,
        )
        fc_tab_btn.border = ft.Border(bottom=ft.BorderSide(2, PRIMARY_TEAL)) if is_fc else None

        quiz_tab_btn.content = ft.Text(
            "Quiz",
            color=PRIMARY_TEAL if not is_fc else TEXT_GREY,
            weight=ft.FontWeight.W_600 if not is_fc else ft.FontWeight.W_500,
        )
        quiz_tab_btn.border = ft.Border(bottom=ft.BorderSide(2, PRIMARY_TEAL)) if not is_fc else None

        flashcards_study_section.visible = is_fc
        quiz_host.visible = not is_fc
        if update:
            page.update()

    def set_mode(new_mode: str):
        state["mode"] = new_mode
        backend.CURRENT_STUDY_MODE = new_mode
        sync_mode_tabs(update=True)

    render_quiz(update=False)
    sync_mode_tabs(update=False)

    top_header = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.only(bottom=ft.BorderSide(1, BORDER_COLOR)),
        padding=ft.Padding.symmetric(horizontal=36, vertical=20),
        content=header_row,
    )

    body = ft.Container(
        padding=ft.Padding.symmetric(horizontal=40, vertical=24),
        expand=True,
        content=ft.Column(
            [
                tabs_row,
                flashcards_study_section,
                quiz_host,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )

    return ft.Container(
        expand=True,
        bgcolor="#F6F8FA",
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
        route="/studyview",
        padding=0,
        bgcolor="#F6F8FA",
        controls=[
            ft.Row(
                [
                    build_sidebar("flashcards", switch_tab, page),
                    build_ai_study_view(page, switch_tab),
                ],
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        ],
    )
