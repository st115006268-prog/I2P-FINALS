"""Arcadia Pages Package."""
from . import login
from . import ai_assistant
from . import flashcards
from . import study_view
from . import study_planner
from . import study_timer
from . import profile
from . import sidebar
from . import backend

# Backwards compatibility aliases
login_frontend = login
AI_Assistant = ai_assistant
flashcards_page = flashcards
study_view_page = study_view
studyplanner_backend_dalem = study_planner
studytimer_backend_dalem = study_timer
profile_backend_dalem = profile
