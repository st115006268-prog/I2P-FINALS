"""FastAPI backend application for Arcadia.

Provides full RESTful API endpoints and SQLite persistence for:
- Authentication & User Profile
- AI Assistant & Chats / Messages
- Flashcards & Decks (with default deck seeding)
- Study Planner & Tasks (with calendar day/start/end/color/done metadata)
- Study Materials & Summaries
- Study Timer / Focus Session Logs

Integrated with SQLite database at database/my_database.db.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "my_database.db")


def hash_password(password: str) -> str:
    """Deterministic secure hash for passwords."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verifies plain password against stored hash with backward compatibility."""
    if not stored_hash:
        return False
    # Backward compatibility with existing plain seeded hashes "hash_<pwd>"
    if stored_hash == f"hash_{plain_password}":
        return True
    return hash_password(plain_password) == stored_hash


def seed_starter_data_for_user(conn: sqlite3.Connection, user_id: int, user_name: str) -> None:
    """Creates a clean welcome chat for a new user without any placeholder decks or tasks."""
    cur = conn.cursor()
    cur.execute("INSERT INTO Chats (user_id) VALUES (?)", (user_id,))
    welcome_chat_id = cur.lastrowid
    welcome_msg = (
        f"Welcome to Arcadia, {user_name}! I'm your AI study assistant. "
        "Ask me questions about your notes, build a study plan, or turn your notes into practice questions."
    )
    cur.execute(
        "INSERT INTO Messages (chat_id, sender, content) VALUES (?, 'AI', ?)",
        (welcome_chat_id, welcome_msg),
    )
    conn.commit()


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db_and_seed():
    """Ensure tables exist, migrate profile columns to Users, and maintain database schema."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(255) DEFAULT 'Student',
                school VARCHAR(255) DEFAULT 'Arcadia University',
                major VARCHAR(255) DEFAULT 'Computer Science',
                year VARCHAR(100) DEFAULT 'First year',
                daily_goal_min INT DEFAULT 90,
                done_today_min INT DEFAULT 0,
                sessions_this_week INT DEFAULT 0,
                focus_minutes_this_week INT DEFAULT 0,
                bio TEXT DEFAULT '',
                reminders BOOLEAN DEFAULT 1,
                weekly_summary BOOLEAN DEFAULT 1,
                member_since VARCHAR(100) DEFAULT 'October 2026',
                gcal_sync_token VARCHAR(255)
            )
        """)
        # Run PRAGMA migration to ensure all profile columns exist on existing database
        existing_cols = {col[1] for col in conn.execute("PRAGMA table_info(Users)").fetchall()}
        col_defs = [
            ("name", "VARCHAR(255) DEFAULT 'Student'"),
            ("school", "VARCHAR(255) DEFAULT 'Arcadia University'"),
            ("major", "VARCHAR(255) DEFAULT 'Computer Science'"),
            ("year", "VARCHAR(100) DEFAULT 'First year'"),
            ("daily_goal_min", "INT DEFAULT 90"),
            ("done_today_min", "INT DEFAULT 0"),
            ("sessions_this_week", "INT DEFAULT 0"),
            ("focus_minutes_this_week", "INT DEFAULT 0"),
            ("bio", "TEXT DEFAULT ''"),
            ("reminders", "BOOLEAN DEFAULT 1"),
            ("weekly_summary", "BOOLEAN DEFAULT 1"),
            ("member_since", "VARCHAR(100) DEFAULT 'October 2026'"),
        ]
        for col_name, col_type in col_defs:
            if col_name not in existing_cols:
                conn.execute(f"ALTER TABLE Users ADD COLUMN {col_name} {col_type}")
        conn.commit()

        conn.execute("""
            CREATE TABLE IF NOT EXISTS Chats (
                chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INT REFERENCES Chats(chat_id) ON DELETE CASCADE,
                sender VARCHAR(50) CHECK (sender IN ('User', 'AI')),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS StudyMaterials (
                material_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                summary_content TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Decks (
                deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
                deck_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Flashcards (
                card_id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INT REFERENCES Decks(deck_id) ON DELETE CASCADE,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                is_multiple_choice BOOLEAN DEFAULT FALSE,
                next_review_date TIMESTAMP,
                repetition_interval INT DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
                task_name VARCHAR(255) NOT NULL,
                exam_date TIMESTAMP,
                scheduled_time TIMESTAMP,
                status VARCHAR(50) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Completed')),
                gcal_event_id VARCHAR(255)
            )
        """)
        conn.commit()

        # Ensure demo user exists with clean initial profile
        demo_user = conn.execute("SELECT * FROM Users WHERE LOWER(email) = 'john.doe@example.com'").fetchone()
        if not demo_user:
            conn.execute(
                """
                INSERT INTO Users (
                    email, password_hash, name, school, major, year,
                    daily_goal_min, done_today_min, sessions_this_week,
                    focus_minutes_this_week, bio, reminders, weekly_summary, member_since
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "john.doe@example.com", hash_password("password123"), "John Doe",
                    "Arcadia University", "Computer Science", "Second year",
                    90, 0, 0, 0,
                    "Building consistent study habits and working toward stronger problem-solving skills.",
                    1, 1, "October 2026",
                ),
            )
            conn.commit()


# Initialize database & seed on module load
init_db_and_seed()


app = FastAPI(
    title="Arcadia API",
    description="FastAPI Backend for Arcadia Study Assistant & Productivity Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Pydantic Schemas
# ============================================================================

class UserRegister(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    user_id: int
    email: str
    profile: Dict[str, Any]


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    year: Optional[str] = None
    daily_goal_min: Optional[int] = None
    done_today_min: Optional[int] = None
    bio: Optional[str] = None
    reminders: Optional[bool] = None
    weekly_summary: Optional[bool] = None
    member_since: Optional[str] = None


class ChatCreate(BaseModel):
    user_id: int = 1


class ChatWithMessagesResponse(BaseModel):
    chat_id: int
    user_id: int
    title: str
    created_at: Optional[str] = None
    messages: List[Dict[str, Any]] = []


class MessageCreate(BaseModel):
    sender: str = Field(..., pattern="^(User|AI)$")
    content: str


class AskQuestionRequest(BaseModel):
    user_id: int = 1
    chat_id: Optional[int] = None
    question: str


class AskQuestionResponse(BaseModel):
    chat_id: int
    question: str
    answer: str


class DeckCreate(BaseModel):
    user_id: int = 1
    title: str
    subject: str = "General Study"
    accent: str = "#13766B"
    progress: float = 0.0
    last_card_idx: int = 0


class DeckUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    accent: Optional[str] = None
    progress: Optional[float] = None
    last_card_idx: Optional[int] = None


class FlashcardCreate(BaseModel):
    question: str
    answer: str
    is_multiple_choice: bool = False
    repetition_interval: int = 0


class FlashcardUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    is_multiple_choice: Optional[bool] = None
    repetition_interval: Optional[int] = None


class TaskCreate(BaseModel):
    user_id: int = 1
    title: str
    day: str  # ISO date YYYY-MM-DD
    start: float = 9.0
    end: float = 10.0
    color: str = "teal"
    done: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    day: Optional[str] = None
    start: Optional[float] = None
    end: Optional[float] = None
    color: Optional[str] = None
    done: Optional[bool] = None


class StudyMaterialCreate(BaseModel):
    user_id: int = 1
    title: str
    summary_content: Optional[str] = None


class TimerLogRequest(BaseModel):
    user_id: int = 1
    minutes: int


# ============================================================================
# Helper utilities
# ============================================================================

def _parse_user_profile(row: sqlite3.Row) -> Dict[str, Any]:
    keys = row.keys()
    name = row["name"] if "name" in keys and row["name"] else None
    school = row["school"] if "school" in keys and row["school"] else None
    major = row["major"] if "major" in keys and row["major"] else None
    year = row["year"] if "year" in keys and row["year"] else None
    daily_goal_min = int(row["daily_goal_min"]) if "daily_goal_min" in keys and row["daily_goal_min"] is not None else None
    done_today_min = int(row["done_today_min"]) if "done_today_min" in keys and row["done_today_min"] is not None else 0
    sessions_this_week = int(row["sessions_this_week"]) if "sessions_this_week" in keys and row["sessions_this_week"] is not None else 0
    focus_minutes_this_week = int(row["focus_minutes_this_week"]) if "focus_minutes_this_week" in keys and row["focus_minutes_this_week"] is not None else 0
    bio = row["bio"] if "bio" in keys and row["bio"] is not None else None
    reminders = bool(row["reminders"]) if "reminders" in keys and row["reminders"] is not None else None
    weekly_summary = bool(row["weekly_summary"]) if "weekly_summary" in keys and row["weekly_summary"] is not None else None
    member_since = row["member_since"] if "member_since" in keys and row["member_since"] else None

    # Support JSON in gcal_sync_token if legacy/fallback fields exist
    raw = row["gcal_sync_token"] if "gcal_sync_token" in keys else None
    if raw:
        try:
            stored = json.loads(raw)
            if isinstance(stored, dict):
                if not name and "name" in stored:
                    name = stored["name"]
                if not school and "school" in stored:
                    school = stored["school"]
                if not major and "major" in stored:
                    major = stored["major"]
                if not year and "year" in stored:
                    year = stored["year"]
                if bio is None and "bio" in stored:
                    bio = stored["bio"]
                if daily_goal_min is None and "daily_goal_min" in stored:
                    daily_goal_min = int(stored["daily_goal_min"])
                if reminders is None and "reminders" in stored:
                    reminders = bool(stored["reminders"])
                if weekly_summary is None and "weekly_summary" in stored:
                    weekly_summary = bool(stored["weekly_summary"])
        except Exception:
            pass

    email = row["email"] if "email" in keys else ""
    if not name:
        name = " ".join(w.capitalize() for w in email.split("@")[0].replace(".", " ").replace("_", " ").split()) or "Student"
    if not school:
        school = "Arcadia University"
    if not major:
        major = "Computer Science"
    if not year:
        year = "First year"
    if daily_goal_min is None:
        daily_goal_min = 90
    if bio is None:
        bio = f"Hi! I'm {name}, studying with Arcadia."
    if reminders is None:
        reminders = True
    if weekly_summary is None:
        weekly_summary = True
    if not member_since:
        member_since = "October 2026"

    return {
        "name": name,
        "email": email,
        "school": school,
        "major": major,
        "year": year,
        "daily_goal_min": daily_goal_min,
        "done_today_min": done_today_min,
        "sessions_this_week": sessions_this_week,
        "focus_minutes_this_week": focus_minutes_this_week,
        "bio": bio,
        "reminders": reminders,
        "weekly_summary": weekly_summary,
        "member_since": member_since,
    }


def _encode_deck_name(title: str, subject: str, accent: str, progress: float, last_card_idx: int = 0) -> str:
    return f"{title}||{subject}||{accent}||{progress}||{last_card_idx}"


def _decode_deck_name(raw_name: str, card_count: int) -> Dict[str, Any]:
    parts = (raw_name or "").split("||")
    title = parts[0] if len(parts) > 0 else "Untitled Deck"
    subject = parts[1] if len(parts) > 1 else "Study Deck"
    accent = parts[2] if len(parts) > 2 else "#13766B"
    try:
        progress = float(parts[3]) if len(parts) > 3 else 0.25
    except ValueError:
        progress = 0.25
    try:
        last_card_idx = int(parts[4]) if len(parts) > 4 else 0
    except ValueError:
        last_card_idx = 0
    if card_count > 0:
        last_card_idx = max(0, min(last_card_idx, card_count - 1))
        if last_card_idx + 1 < card_count and progress >= 1.0:
            progress = round((last_card_idx + 1) / card_count, 2)
    else:
        last_card_idx = 0
        progress = 0.0
    card_word = "card" if card_count == 1 else "cards"
    subtitle = f"{card_count} {card_word} · {subject}"
    return {
        "title": title,
        "subject": subject,
        "accent": accent,
        "progress": progress,
        "last_card_idx": last_card_idx,
        "subtitle": subtitle,
        "card_count": card_count,
    }


def _row_to_task_dict(row: sqlite3.Row) -> Dict[str, Any]:
    day_str = row["exam_date"] or date.today().isoformat()
    if "T" in day_str:
        day_str = day_str.split("T")[0]
    try:
        start_val = float(row["scheduled_time"]) if row["scheduled_time"] is not None else 9.0
    except ValueError:
        start_val = 9.0

    meta = row["gcal_event_id"] or ""
    if "|" in meta:
        end_s, color = meta.split("|", 1)
        try:
            end_val = float(end_s)
        except ValueError:
            end_val = start_val + 1.0
    else:
        end_val = start_val + 1.0
        color = meta if meta in ("teal", "purple", "orange", "gray") else "teal"

    done = (row["status"] == "Completed")
    return {
        "id": row["task_id"],
        "task_id": row["task_id"],
        "user_id": row["user_id"],
        "title": row["task_name"],
        "task_name": row["task_name"],
        "day": day_str,
        "start": start_val,
        "end": end_val,
        "color": color,
        "done": done,
        "status": row["status"],
    }


# ============================================================================
# General / Health Endpoints
# ============================================================================

@app.get("/")
def root():
    return {
        "app": "Arcadia",
        "backend": "FastAPI",
        "status": "online",
        "docs_url": "/docs",
    }


@app.get("/api/health")
def health_check():
    with get_db() as conn:
        conn.execute("SELECT 1").fetchone()
    return {"status": "healthy", "database": "connected"}


# ============================================================================
# Authentication & User Profile Endpoints
# ============================================================================

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister):
    email = (user_data.email or "").strip().lower()
    pwd = user_data.password or ""
    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")
    if len(pwd) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    with get_db() as conn:
        existing = conn.execute("SELECT user_id FROM Users WHERE LOWER(email) = ?", (email,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="An account with this email already exists. Please sign in.")

        local_name = (user_data.name or "").strip()
        if not local_name:
            local_name = " ".join(
                w.capitalize() for w in email.split("@")[0].replace(".", " ").replace("_", " ").split()
            ) or "Student"

        profile_data = {
            "name": local_name,
            "school": "Arcadia University",
            "major": "Computer Science",
            "year": "First year",
            "daily_goal_min": 90,
            "done_today_min": 0,
            "sessions_this_week": 0,
            "focus_minutes_this_week": 0,
            "bio": f"Hi! I'm {local_name}, studying with Arcadia.",
            "reminders": True,
            "weekly_summary": True,
        }
        password_hash = hash_password(pwd)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Users (
                email, password_hash, name, school, major, year,
                daily_goal_min, done_today_min, sessions_this_week, focus_minutes_this_week,
                bio, reminders, weekly_summary, member_since, gcal_sync_token
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email,
                password_hash,
                local_name,
                "Arcadia University",
                "Computer Science",
                "First year",
                90,
                0,
                0,
                0,
                f"Hi! I'm {local_name}, studying with Arcadia.",
                1,
                1,
                date.today().strftime("%B %Y"),
                json.dumps(profile_data),
            ),
        )
        conn.commit()
        user_id = cur.lastrowid

        row = conn.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,)).fetchone()
        return {"user_id": user_id, "email": row["email"], "profile": _parse_user_profile(row)}


@app.post("/api/auth/login", response_model=UserResponse)
def login(login_data: UserLogin):
    email = (login_data.email or "").strip().lower()
    pwd = login_data.password or ""
    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")
    if not pwd:
        raise HTTPException(status_code=400, detail="Password is required.")

    with get_db() as conn:
        user = conn.execute("SELECT * FROM Users WHERE LOWER(email) = ?", (email,)).fetchone()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="Account not found. Please check your email or click 'Sign up' to create an account.",
            )

        if not verify_password(pwd, user["password_hash"]):
            raise HTTPException(
                status_code=401,
                detail="Incorrect password. Please try again.",
            )

        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "profile": _parse_user_profile(user),
        }


@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    with get_db() as conn:
        user = conn.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,)).fetchone()
        if not user:
            user = conn.execute("SELECT * FROM Users LIMIT 1").fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "profile": _parse_user_profile(user),
        }


@app.put("/api/users/{user_id}/profile", response_model=UserResponse)
def update_user_profile(user_id: int, update: ProfileUpdate):
    with get_db() as conn:
        user = conn.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        data = update.dict(exclude_unset=True)
        set_clauses = []
        params = []
        allowed = (
            "name", "email", "school", "major", "year", "daily_goal_min",
            "done_today_min", "sessions_this_week", "focus_minutes_this_week",
            "bio", "reminders", "weekly_summary", "member_since"
        )
        for col in allowed:
            if col in data:
                set_clauses.append(f"{col} = ?")
                params.append(data[col])
        if set_clauses:
            curr_prof = _parse_user_profile(user)
            curr_prof.update({k: v for k, v in data.items() if k in allowed})
            set_clauses.append("gcal_sync_token = ?")
            params.append(json.dumps(curr_prof))
            params.append(user_id)
            conn.execute(f"UPDATE Users SET {', '.join(set_clauses)} WHERE user_id = ?", tuple(params))
            conn.commit()

        updated = conn.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,)).fetchone()
        return {
            "user_id": updated["user_id"],
            "email": updated["email"],
            "profile": _parse_user_profile(updated),
        }


@app.get("/api/users/{user_id}/stats")
def get_user_stats(user_id: int):
    with get_db() as conn:
        user = conn.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,)).fetchone()
        prof = _parse_user_profile(user) if user else {}
        deck_count = conn.execute("SELECT COUNT(*) FROM Decks WHERE user_id = ?", (user_id,)).fetchone()[0]
        total_tasks = conn.execute("SELECT COUNT(*) FROM Tasks WHERE user_id = ?", (user_id,)).fetchone()[0]
        done_tasks = conn.execute(
            "SELECT COUNT(*) FROM Tasks WHERE user_id = ? AND status = 'Completed'", (user_id,)
        ).fetchone()[0]
        pct = int(round((done_tasks / total_tasks) * 100)) if total_tasks > 0 else 0
        focus_min = prof.get("focus_minutes_this_week", 0)
        hours = round(focus_min / 60.0, 1)
        return {
            "sessions_this_week": prof.get("sessions_this_week", 0),
            "focus_minutes_this_week": focus_min,
            "focus_hours_str": f"{hours}h",
            "active_decks": deck_count,
            "tasks_completed_pct": f"{pct}%",
            "done_today_min": prof.get("done_today_min", 0),
            "daily_goal_min": prof.get("daily_goal_min", 90),
        }


@app.post("/api/timer/log")
def log_timer_session(req: TimerLogRequest):
    with get_db() as conn:
        user = conn.execute("SELECT * FROM Users WHERE user_id = ?", (req.user_id,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        conn.execute(
            """
            UPDATE Users
            SET sessions_this_week = COALESCE(sessions_this_week, 0) + 1,
                focus_minutes_this_week = COALESCE(focus_minutes_this_week, 0) + ?,
                done_today_min = COALESCE(done_today_min, 0) + ?
            WHERE user_id = ?
            """,
            (req.minutes, req.minutes, req.user_id),
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM Users WHERE user_id = ?", (req.user_id,)).fetchone()
        return {"status": "logged", "profile": _parse_user_profile(updated)}


# ============================================================================
# AI Assistant & Chat Endpoints
# ============================================================================

def assistant_generate_reply(prompt: str) -> str:
    """Generate helpful study assistant responses."""
    prompt_lower = prompt.lower()
    if "summarize" in prompt_lower:
        return (
            "Here is a concise summary of your material:\n"
            "• Core Concept: Highlights essential formulas, definitions, and principles.\n"
            "• Key Takeaway: Focus on foundational axioms and practical problem-solving.\n"
            "• Review Tip: Use active recall flashcards to reinforce long-term retention."
        )
    elif "plan" in prompt_lower:
        return (
            "Recommended Study Plan (Saved to your session):\n"
            "1. 25 min: Core reading & active note-taking.\n"
            "2. 5 min: Short rest break.\n"
            "3. 25 min: Practice problems & Flashcard deck review.\n"
            "4. 10 min: Summarize key mistakes."
        )
    elif "question" in prompt_lower or "practice" in prompt_lower or "quiz" in prompt_lower:
        return (
            "Practice Questions for Active Recall:\n"
            "1. Explain the difference between mutable and immutable types in Python.\n"
            "2. How does Newton's Second Law relate net force, mass, and acceleration?\n"
            "3. What is the time complexity of binary search on a sorted array?"
        )
    elif "e=mc" in prompt_lower:
        return "E = mc² expresses mass-energy equivalence: Energy (E) equals mass (m) multiplied by the speed of light squared (c²)."
    else:
        return (
            f"Great question about “{prompt}”! "
            "To master this topic:\n"
            "1. Break the concept into fundamental definitions.\n"
            "2. Create flashcards in the Flashcards tab for active recall.\n"
            "3. Schedule a 25-minute focus session in the Study Timer."
        )


@app.get("/api/chats", response_model=List[ChatWithMessagesResponse])
def list_chats(user_id: int = 1):
    with get_db() as conn:
        chats = conn.execute(
            "SELECT chat_id, user_id, strftime('%Y-%m-%dT%H:%M:%SZ', created_at) as created_at "
            "FROM Chats WHERE user_id = ? ORDER BY chat_id ASC",
            (user_id,),
        ).fetchall()
        result = []
        for c in chats:
            msgs = conn.execute(
                "SELECT message_id, chat_id, sender, content, strftime('%Y-%m-%dT%H:%M:%SZ', created_at) as created_at "
                "FROM Messages WHERE chat_id = ? ORDER BY message_id ASC",
                (c["chat_id"],),
            ).fetchall()
            formatted_msgs = [
                {
                    "message_id": m["message_id"],
                    "role": "user" if m["sender"] == "User" else "assistant",
                    "sender": m["sender"],
                    "text": m["content"],
                    "content": m["content"],
                }
                for m in msgs
            ]
            first_user_msg = next((m["text"] for m in formatted_msgs if m["role"] == "user"), None)
            title = first_user_msg if first_user_msg else "New study chat"
            result.append({
                "chat_id": c["chat_id"],
                "user_id": c["user_id"],
                "title": title,
                "created_at": c["created_at"],
                "messages": formatted_msgs,
            })
        return result


@app.post("/api/chats", response_model=ChatWithMessagesResponse, status_code=status.HTTP_201_CREATED)
def create_chat(chat_data: ChatCreate):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO Chats (user_id) VALUES (?)", (chat_data.user_id,))
        conn.commit()
        chat_id = cur.lastrowid
        chat = conn.execute(
            "SELECT chat_id, user_id, strftime('%Y-%m-%dT%H:%M:%SZ', created_at) as created_at FROM Chats WHERE chat_id = ?",
            (chat_id,),
        ).fetchone()
        return {
            "chat_id": chat["chat_id"],
            "user_id": chat["user_id"],
            "title": "New study chat",
            "created_at": chat["created_at"],
            "messages": [],
        }


@app.delete("/api/chats/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(chat_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM Messages WHERE chat_id = ?", (chat_id,))
        conn.execute("DELETE FROM Chats WHERE chat_id = ?", (chat_id,))
        conn.commit()
    return None


@app.get("/api/chats/{chat_id}/messages")
def get_chat_messages(chat_id: int):
    with get_db() as conn:
        messages = conn.execute(
            "SELECT message_id, chat_id, sender, content, strftime('%Y-%m-%dT%H:%M:%SZ', created_at) as created_at "
            "FROM Messages WHERE chat_id = ? ORDER BY message_id ASC",
            (chat_id,),
        ).fetchall()
        return [
            {
                "message_id": m["message_id"],
                "chat_id": m["chat_id"],
                "sender": m["sender"],
                "role": "user" if m["sender"] == "User" else "assistant",
                "content": m["content"],
                "text": m["content"],
                "created_at": m["created_at"],
            }
            for m in messages
        ]


@app.post("/api/assistant/ask", response_model=AskQuestionResponse)
def ask_assistant(req: AskQuestionRequest):
    """Saves User question to SQLite, generates AI reply, saves AI reply to SQLite, and returns it."""
    with get_db() as conn:
        chat_id = req.chat_id
        if not chat_id or not conn.execute("SELECT 1 FROM Chats WHERE chat_id = ?", (chat_id,)).fetchone():
            cur = conn.cursor()
            cur.execute("INSERT INTO Chats (user_id) VALUES (?)", (req.user_id,))
            conn.commit()
            chat_id = cur.lastrowid

        conn.execute(
            "INSERT INTO Messages (chat_id, sender, content) VALUES (?, 'User', ?)",
            (chat_id, req.question),
        )
        answer = assistant_generate_reply(req.question)
        conn.execute(
            "INSERT INTO Messages (chat_id, sender, content) VALUES (?, 'AI', ?)",
            (chat_id, answer),
        )
        conn.commit()
        return {
            "chat_id": chat_id,
            "question": req.question,
            "answer": answer,
        }


# ============================================================================
# Flashcards & Decks Endpoints
# ============================================================================

@app.get("/api/decks")
def get_decks(user_id: int = 1):
    with get_db() as conn:
        decks = conn.execute(
            """
            SELECT d.deck_id, d.user_id, d.deck_name,
                   strftime('%Y-%m-%dT%H:%M:%SZ', d.created_at) as created_at,
                   COUNT(f.card_id) as card_count
            FROM Decks d
            LEFT JOIN Flashcards f ON d.deck_id = f.deck_id
            WHERE d.user_id = ?
            GROUP BY d.deck_id
            ORDER BY d.deck_id ASC
            """,
            (user_id,),
        ).fetchall()
        result = []
        for d in decks:
            parsed = _decode_deck_name(d["deck_name"], d["card_count"])
            cards = conn.execute(
                "SELECT card_id, question, answer, is_multiple_choice, repetition_interval FROM Flashcards WHERE deck_id = ? ORDER BY card_id ASC",
                (d["deck_id"],),
            ).fetchall()
            result.append({
                "deck_id": d["deck_id"],
                "user_id": d["user_id"],
                "title": parsed["title"],
                "subject": parsed["subject"],
                "accent": parsed["accent"],
                "progress": parsed["progress"],
                "last_card_idx": parsed["last_card_idx"],
                "subtitle": parsed["subtitle"],
                "card_count": d["card_count"],
                "created_at": d["created_at"],
                "cards": [dict(c) for c in cards],
            })
        return result


@app.post("/api/decks", status_code=status.HTTP_201_CREATED)
def create_deck(deck: DeckCreate):
    with get_db() as conn:
        encoded = _encode_deck_name(deck.title, deck.subject, deck.accent, deck.progress, deck.last_card_idx)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Decks (user_id, deck_name) VALUES (?, ?)",
            (deck.user_id, encoded),
        )
        conn.commit()
        deck_id = cur.lastrowid
        parsed = _decode_deck_name(encoded, 0)
        return {
            "deck_id": deck_id,
            "user_id": deck.user_id,
            **parsed,
        }


@app.patch("/api/decks/{deck_id}")
def update_deck(deck_id: int, update: DeckUpdate):
    with get_db() as conn:
        row = conn.execute("SELECT deck_id, user_id, deck_name FROM Decks WHERE deck_id = ?", (deck_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Deck not found")
        card_count = conn.execute("SELECT COUNT(*) FROM Flashcards WHERE deck_id = ?", (deck_id,)).fetchone()[0]
        parsed = _decode_deck_name(row["deck_name"], card_count)
        new_title = update.title if update.title is not None else parsed["title"]
        new_subject = update.subject if update.subject is not None else parsed["subject"]
        new_accent = update.accent if update.accent is not None else parsed["accent"]
        new_progress = update.progress if update.progress is not None else parsed["progress"]
        new_last_idx = update.last_card_idx if update.last_card_idx is not None else parsed["last_card_idx"]
        if card_count > 0:
            new_last_idx = max(0, min(new_last_idx, card_count - 1))
            if new_last_idx + 1 < card_count and new_progress >= 1.0:
                new_progress = round((new_last_idx + 1) / card_count, 2)
        else:
            new_last_idx = 0
            new_progress = 0.0
        encoded = _encode_deck_name(new_title, new_subject, new_accent, new_progress, new_last_idx)
        conn.execute("UPDATE Decks SET deck_name = ? WHERE deck_id = ?", (encoded, deck_id))
        conn.commit()
        new_parsed = _decode_deck_name(encoded, card_count)
        return {
            "deck_id": deck_id,
            "user_id": row["user_id"],
            **new_parsed,
        }


@app.delete("/api/decks/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck(deck_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM Flashcards WHERE deck_id = ?", (deck_id,))
        conn.execute("DELETE FROM Decks WHERE deck_id = ?", (deck_id,))
        conn.commit()
    return None


@app.get("/api/decks/{deck_id}/cards")
def get_flashcards(deck_id: int):
    with get_db() as conn:
        cards = conn.execute(
            """
            SELECT card_id, deck_id, question, answer, is_multiple_choice,
                   strftime('%Y-%m-%dT%H:%M:%SZ', next_review_date) as next_review_date,
                   repetition_interval
            FROM Flashcards
            WHERE deck_id = ?
            ORDER BY card_id ASC
            """,
            (deck_id,),
        ).fetchall()
        return [dict(c) for c in cards]


@app.post("/api/decks/{deck_id}/cards", status_code=status.HTTP_201_CREATED)
def add_flashcard(deck_id: int, card: FlashcardCreate):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Flashcards (deck_id, question, answer, is_multiple_choice, repetition_interval)
            VALUES (?, ?, ?, ?, ?)
            """,
            (deck_id, card.question, card.answer, card.is_multiple_choice, card.repetition_interval),
        )
        conn.commit()
        card_id = cur.lastrowid
        row = conn.execute(
            "SELECT card_id, deck_id, question, answer, is_multiple_choice, repetition_interval FROM Flashcards WHERE card_id = ?",
            (card_id,),
        ).fetchone()
        return dict(row)


@app.patch("/api/flashcards/{card_id}")
def update_flashcard(card_id: int, update: FlashcardUpdate):
    with get_db() as conn:
        row = conn.execute(
            "SELECT card_id, deck_id, question, answer, is_multiple_choice, repetition_interval FROM Flashcards WHERE card_id = ?",
            (card_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        new_q = update.question if update.question is not None else row["question"]
        new_a = update.answer if update.answer is not None else row["answer"]
        new_mc = update.is_multiple_choice if update.is_multiple_choice is not None else row["is_multiple_choice"]
        new_rep = update.repetition_interval if update.repetition_interval is not None else row["repetition_interval"]
        conn.execute(
            "UPDATE Flashcards SET question = ?, answer = ?, is_multiple_choice = ?, repetition_interval = ? WHERE card_id = ?",
            (new_q, new_a, new_mc, new_rep, card_id),
        )
        conn.commit()
        updated = conn.execute(
            "SELECT card_id, deck_id, question, answer, is_multiple_choice, repetition_interval FROM Flashcards WHERE card_id = ?",
            (card_id,),
        ).fetchone()
        return dict(updated)


@app.delete("/api/flashcards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flashcard(card_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM Flashcards WHERE card_id = ?", (card_id,))
        conn.commit()
    return None


# ============================================================================
# Tasks & Study Planner Endpoints
# ============================================================================

@app.get("/api/tasks")
def get_tasks(user_id: int = 1, status_filter: Optional[str] = None):
    with get_db() as conn:
        query = "SELECT * FROM Tasks WHERE user_id = ?"
        params: List[Any] = [user_id]
        if isinstance(status_filter, str) and status_filter:
            query += " AND status = ?"
            params.append(status_filter)
        query += " ORDER BY task_id ASC"
        rows = conn.execute(query, tuple(params)).fetchall()
        return [_row_to_task_dict(r) for r in rows]


@app.post("/api/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    with get_db() as conn:
        status_str = "Completed" if task.done else "Pending"
        meta = f"{task.end}|{task.color}"
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Tasks (user_id, task_name, exam_date, scheduled_time, status, gcal_event_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (task.user_id, task.title, task.day, str(task.start), status_str, meta),
        )
        conn.commit()
        task_id = cur.lastrowid
        row = conn.execute("SELECT * FROM Tasks WHERE task_id = ?", (task_id,)).fetchone()
        return _row_to_task_dict(row)


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    with get_db() as conn:
        existing = conn.execute("SELECT * FROM Tasks WHERE task_id = ?", (task_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Task not found")
        current = _row_to_task_dict(existing)

        new_title = update.title if update.title is not None else current["title"]
        new_day = update.day if update.day is not None else current["day"]
        new_start = update.start if update.start is not None else current["start"]
        new_end = update.end if update.end is not None else current["end"]
        new_color = update.color if update.color is not None else current["color"]
        new_done = update.done if update.done is not None else current["done"]

        status_str = "Completed" if new_done else "Pending"
        meta = f"{new_end}|{new_color}"

        conn.execute(
            """
            UPDATE Tasks
            SET task_name = ?, exam_date = ?, scheduled_time = ?, status = ?, gcal_event_id = ?
            WHERE task_id = ?
            """,
            (new_title, new_day, str(new_start), status_str, meta, task_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM Tasks WHERE task_id = ?", (task_id,)).fetchone()
        return _row_to_task_dict(row)


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM Tasks WHERE task_id = ?", (task_id,))
        conn.commit()
    return None


# ============================================================================
# Study Materials Endpoints
# ============================================================================

@app.get("/api/materials")
def get_study_materials(user_id: int = 1):
    with get_db() as conn:
        materials = conn.execute(
            "SELECT material_id, user_id, title, summary_content FROM StudyMaterials WHERE user_id = ?",
            (user_id,),
        ).fetchall()
        return [dict(m) for m in materials]


@app.post("/api/materials", status_code=status.HTTP_201_CREATED)
def create_study_material(material: StudyMaterialCreate):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO StudyMaterials (user_id, title, summary_content) VALUES (?, ?, ?)",
            (material.user_id, material.title, material.summary_content),
        )
        conn.commit()
        material_id = cur.lastrowid
        row = conn.execute(
            "SELECT material_id, user_id, title, summary_content FROM StudyMaterials WHERE material_id = ?",
            (material_id,),
        ).fetchone()
        return dict(row)


# ============================================================================
# Run standalone
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend_fastapi:app", host="127.0.0.1", port=8000, reload=True)
