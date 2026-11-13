"""Shared in-memory state for Arcadia across all routes."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Flashcard:
    question: str
    answer: str
    choices: list[str] = field(default_factory=list)


@dataclass
class Deck:
    id: str
    title: str
    subject: str
    color: str
    progress: float
    cards: list[Flashcard] = field(default_factory=list)


class ArcadiaState:
    def __init__(self) -> None:
        today = date.today()
        self.logged_in: bool = False
        self.user: dict = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "school": "Arcadia University",
            "major": "Computer Science",
            "year": "Second year",
            "daily_goal_min": 90,
            "done_today_min": 65,
            "bio": "Building consistent study habits and working toward stronger problem-solving skills.",
            "reminders": True,
            "weekly_summary": True,
        }
        self.sessions_this_week: int = 7
        self.focus_minutes_this_week: int = 270  # 4.5h

        self.tasks: list[dict] = [
            dict(id=1, title="Review flashcards", day=today, start=9.0, end=9.5, color="teal", done=False),
            dict(id=2, title="Study session", day=today, start=10.0, end=11.0, color="purple", done=False),
            dict(id=3, title="Finish assignment", day=today, start=12.0, end=13.0, color="orange", done=False),
            dict(id=4, title="Read chapter notes", day=today + timedelta(days=1), start=14.0, end=14.5, color="teal", done=False),
            dict(id=5, title="Do laundry", day=today + timedelta(days=2), start=16.0, end=17.0, color="gray", done=False),
        ]
        self.next_task_id: int = 100

        self.decks: list[Deck] = [
            Deck(
                id="gen-phys",
                title="GEN PHYS",
                subject="General Physics",
                color="#0F7A71",
                progress=0.6,
                cards=[
                    Flashcard("What is the dimension of Force?", "[M L T⁻²] (kg·m/s²)", ["[M L T⁻²]", "[M L² T⁻²]", "[M L⁻¹ T⁻²]", "[M T⁻²]"]),
                    Flashcard("State Newton's Second Law.", "F = m · a (Net force equals mass times acceleration).", ["F = m · a", "F = m · v", "p = m / v", "W = F / d"]),
                    Flashcard("What is the SI unit of Work and Energy?", "Joule (J = N·m)", ["Joule (J)", "Watt (W)", "Pascal (Pa)", "Newton (N)"]),
                    Flashcard("Define conservation of linear momentum.", "Total momentum of an isolated system remains constant when net external force is zero.", ["Constant when F_ext = 0", "Always increases with time", "Equals kinetic energy", "Applies only to elastic collisions"]),
                ],
            ),
            Deck(
                id="i2p",
                title="I2P",
                subject="Introduction to Programming",
                color="#6366F1",
                progress=0.4,
                cards=[
                    Flashcard("What is the time complexity of binary search?", "O(log n) on a sorted list.", ["O(log n)", "O(n)", "O(n²)", "O(1)"]),
                    Flashcard("Difference between a list and a tuple in Python?", "Lists are mutable [...]; tuples are immutable (...).", ["Lists are mutable; tuples are immutable", "Tuples are faster to sort in-place", "Lists cannot hold mixed types", "No difference"]),
                    Flashcard("What does a base case do in recursion?", "Stops recursive calls so the function terminates.", ["Stops recursive calls", "Doubles stack memory", "Loops infinitely", "Imports modules"]),
                ],
            ),
            Deck(
                id="forms-nature",
                title="Forms in Nature",
                subject="Design Studies",
                color="#F59E0B",
                progress=0.7,
                cards=[
                    Flashcard("What is biomimicry in design?", "Emulating natural patterns and systems to solve human design challenges.", ["Emulating natural systems", "Using only wood materials", "Minimalist monochrome color", "3D wireframe rendering"]),
                    Flashcard("Where does the Fibonacci spiral commonly appear?", "Phyllotaxis in sunflowers, pinecones, and nautilus shells.", ["Sunflower seed spirals", "Cubic crystal lattices", "Parallel river deltas", "Basalt columns"]),
                ],
            ),
            Deck(
                id="deadly-elegance",
                title="Deadly Elegance",
                subject="Literature",
                color="#EC4899",
                progress=0.5,
                cards=[
                    Flashcard("What defines a tragic flaw (hamartia)?", "A character trait or error in judgment leading to the protagonist's downfall.", ["Fatal character flaw/error", "Comic relief scene", "Deus ex machina ending", "Unreliable narrator"]),
                    Flashcard("What is dramatic irony?", "When the audience knows crucial facts that the characters do not.", ["Audience knows more than characters", "A character speaks alone on stage", "Comparing two things with 'like'", "Exaggeration for effect"]),
                ],
            ),
            Deck(
                id="college-chinese",
                title="College Chinese",
                subject="Language",
                color="#3B82F6",
                progress=0.3,
                cards=[
                    Flashcard("学习 (xuéxí) meaning?", "To study / to learn", ["To study / learn", "To rest", "Library", "Examination"]),
                    Flashcard("图书馆 (túshūguǎn) meaning?", "Library", ["Library", "Cafeteria", "Classroom", "Bookstore"]),
                    Flashcard("复习 (fùxí) meaning?", "To review / revise", ["To review / revise", "To preview", "To graduate", "To translate"]),
                ],
            ),
        ]
        self.active_deck_id: str = "gen-phys"
        self.study_mode: str = "flashcards"  # "flashcards" or "quiz"

    @property
    def initials(self) -> str:
        parts = [p[0].upper() for p in self.user["name"].split() if p]
        return "".join(parts[:2]) or "ST"

    def set_user_from_email(self, email: str) -> None:
        self.logged_in = True
        self.user["email"] = email
        local = email.split("@")[0].replace(".", " ").replace("_", " ").strip()
        if local and self.user["email"] != "john.doe@example.com":
            self.user["name"] = " ".join(w.capitalize() for w in local.split())

    def get_active_deck(self) -> Deck:
        for d in self.decks:
            if d.id == self.active_deck_id:
                return d
        return self.decks[0]

    def log_focus_minutes(self, minutes: int) -> None:
        self.sessions_this_week += 1
        self.focus_minutes_this_week += minutes
        self.user["done_today_min"] = min(
            self.user["daily_goal_min"] * 2,
            self.user["done_today_min"] + minutes,
        )


STATE = ArcadiaState()