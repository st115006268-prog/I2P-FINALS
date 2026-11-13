# Arcadia

**Arcadia** is an all-in-one desktop application for studying and schedule organizing, built to make learning quick and efficient. Designed for students and lifelong learners, Arcadia compiles learning materials and automatically structures study schedules so users can focus on mastering their subjects rather than spending time organizing.

---

## Table of Contents
- [Features](#features)
  - [Core Features (MVP)](#core-features-mvp)
  - [Additional Features](#additional-features)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [API Documentation & Database](#api-documentation--database)
- [Team (Group 24)](#team-group-24)

---

## Features

### Core Features (MVP)
* **AI Study Assistant:** An interactive conversational assistant that helps break down complex academic topics, compile study materials, draft study plans, and generate sample questions and explanations.
* **Flashcards & Quizzes:** Supports active-recall spaced repetition flashcard decks with card-flip animations, custom deck/card creation, and interactive multiple-choice practice quizzes to test retention.
* **AI Study Planner:** Automatically schedules study sessions into an organized weekly timetable grid with to-do lists, priority tracking, and calendar time blocks based on upcoming tasks and exam deadlines.

### Additional Features
* **Study Timer (Pomodoro):** Tracks and records focus sessions (duration, subject, and break intervals) with customizable study/break intervals and a live session log.
* **Google Calendar Sync:** Sync token integration and calendar schema ready to synchronize planned study blocks directly with Google Calendar.
* **User Profile & Personalization:** Allows users to customize their academic details (major, school, academic year, daily study goals) and notification preferences with real-time statistics.
* **Authentication & Multi-User Support:** Secure sign-in and sign-up with password verification and isolated user data stored in SQLite.

---

## Architecture & Tech Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | [Flet](https://flet.dev/) (Flutter for Python) `0.28.x` | Native cross-platform desktop UI with reactive components and design system tokens. |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) | Asynchronous RESTful API backend handling data validation, business logic, and routing. |
| **Database** | SQLite 3 (`database/my_database.db`) | Relational database with persistent storage for users, chats, messages, decks, tasks, and timer logs. |
| **HTTP Client** | [HTTPX](https://www.python-httpx.org/) | High-performance HTTP client connecting the Flet desktop client to the FastAPI backend. |
| **Language** | Python 3.9+ | Primary runtime environment for both backend and frontend. |

---

## Project Structure

```text
├── ARCADIA.py             # Main Flet application entrypoint
├── backend_fastapi.py     # FastAPI backend server with SQLite persistence
├── flet_compat.py         # Cross-version compatibility layer for Flet 0.28
├── requirements.txt       # Project Python dependencies
├── README.md              # Project documentation
│
├── database/
│   └── my_database.db     # SQLite relational database (auto-generated)
│
├── pages/                 # Modular page views
│   ├── login.py           # Sign-in & sign-up authentication page
│   ├── ai_assistant.py    # AI study chat assistant interface
│   ├── flashcards.py      # Flashcard decks and interactive quiz page
│   ├── study_planner.py   # Weekly timetable and task planner
│   ├── study_timer.py     # Pomodoro focus timer with session logs
│   ├── study_view.py      # Study materials overview
│   ├── profile.py         # User profile and academic settings
│   ├── sidebar.py         # Unified responsive navigation sidebar
│   │
│   └── backend/           # Frontend-to-backend communication
│       ├── client.py      # REST API client with local fallback
│       └── state.py       # Global session & active user state
│
└── styles/                # Centralized design system
    ├── theme.py           # Color palette, spacing, and typography
    └── page_styles.py     # Card containers, shadows, and brand logo
```

---

## Getting Started

### Prerequisites
* **Python 3.9** (or 3.9+) installed on your machine.
* `pip` package manager.
* A working Internet connection (for loading Google web fonts on first launch).

### Installation

1. Clone or download this repository:
   ```bash
   git clone https://github.com/your-username/arcadia.git
   cd arcadia
   ```

2. (Optional but recommended) Create and activate a virtual environment:
   * **Windows (PowerShell):**
     ```powershell
     py -3.9 -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **macOS / Linux:**
     ```bash
     python3.9 -m venv venv
     source venv/bin/activate
     ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   *Alternatively, install them manually:*
   ```bash
   pip install "flet>=0.28.0,<0.29.0" "fastapi>=0.110.0" "uvicorn[standard]>=0.28.0" "pydantic>=2.0.0" "httpx>=0.25.0"
   ```

---

### Running the Application

Arcadia runs with a decoupled client-server architecture. You will need two terminal windows:

#### Step 1: Start the FastAPI Backend
In your first terminal, navigate to the project directory and run:
* **Windows:**
  ```powershell
  py -3.9 backend_fastapi.py
  ```
* **macOS / Linux:**
  ```bash
  python3 backend_fastapi.py
  ```

> The backend server will automatically initialize the database schema and start listening at `http://127.0.0.1:8000`.

#### Step 2: Launch the Arcadia Desktop App
In your second terminal, navigate to the project directory and run:
* **Windows:**
  ```powershell
  py -3.9 ARCADIA.py
  ```
* **macOS / Linux:**
  ```bash
  python3 ARCADIA.py
  ```

Once launched, the Arcadia login page will appear. You can sign up with a new account or sign in with an existing user.

---

## API Documentation & Database

* **Interactive API Docs (Swagger UI):** When the backend is running, open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to view all available endpoints, test requests, and view request/response schemas.
* **Alternative API Docs (ReDoc):** Available at [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).
* **Database File:** Stored at `database/my_database.db`. Tables and schema migrations are verified and created on every backend launch.

---

## Team (Group 24)

* **林家民** — Team Leader, Backend, Google Calendar Sync, Meeting Minutes
* **李嘉昌** — Frontend, UI/UX Design, Flashcards, Study Timer
* **黃志忠** — GitHub Manager, Study Planner, AI Study Assistant
