"""FastAPI and SQLite client operations for Arcadia."""
from __future__ import annotations

import socket
import time
from datetime import date
from typing import Any, Dict, List, Optional
import httpx

import backend_fastapi as api
from . import state

FASTAPI_BASE_URL = "http://127.0.0.1:8000"

_server_state = {"online": False, "checked_at": 0.0}


def _is_fastapi_server_running() -> bool:
    """Fast sub-millisecond check if 127.0.0.1:8000 is listening (cached for 5s)."""
    now = time.monotonic()
    if now - _server_state["checked_at"] < 5.0:
        return _server_state["online"]
    _server_state["checked_at"] = now
    try:
        with socket.create_connection(("127.0.0.1", 8000), timeout=0.05):
            _server_state["online"] = True
            return True
    except OSError:
        _server_state["online"] = False
        return False


def _sync_user_dict(user_resp: Dict[str, Any]) -> Dict[str, Any]:
    new_uid = user_resp.get("user_id", 1)
    if new_uid != state.CURRENT_USER_ID:
        try:
            from pages import study_timer
            study_timer.reset_timer_state()
        except Exception:
            try:
                from pages import studytimer_backend_dalem
                studytimer_backend_dalem.reset_timer_state()
            except Exception:
                pass
    state.CURRENT_USER_ID = new_uid
    state.CURRENT_CHAT_ID = None
    prof = user_resp.get("profile", {})
    name = prof.get("name", "Student")
    parts = [p[0].upper() for p in name.split() if p]
    initials = "".join(parts[:2]) or "ST"
    state.USER["name"] = name
    state.USER["initials"] = initials
    state.USER["email"] = user_resp.get("email", prof.get("email", "student@example.com"))
    try:
        from pages import sidebar
        sidebar.refresh_all_sidebars()
    except Exception:
        pass
    return prof


def api_login(email: str, password: str) -> Dict[str, Any]:
    """Authenticate user via FastAPI /api/auth/login and persist to SQLite."""
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.post(
                    f"{FASTAPI_BASE_URL}/api/auth/login",
                    json={"email": email, "password": password},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    _sync_user_dict(data)
                    try:
                        from pages import study_timer
                        study_timer.reset_timer_state()
                    except Exception:
                        try:
                            from pages import studytimer_backend_dalem
                            studytimer_backend_dalem.reset_timer_state()
                        except Exception:
                            pass
                    return data
                elif resp.status_code in (400, 401, 404):
                    detail = resp.json().get("detail", "Invalid email or password")
                    raise ValueError(detail)
        except ValueError:
            raise
        except Exception:
            _server_state["online"] = False
    try:
        data = api.login(api.UserLogin(email=email, password=password))
    except api.HTTPException as e:
        raise ValueError(e.detail)
    _sync_user_dict(data)
    try:
        from pages import study_timer
        study_timer.reset_timer_state()
    except Exception:
        try:
            from pages import studytimer_backend_dalem
            studytimer_backend_dalem.reset_timer_state()
        except Exception:
            pass
    return data


def api_register(email: str, password: str, name: Optional[str] = None) -> Dict[str, Any]:
    """Register a new user via FastAPI /api/auth/register and persist to SQLite."""
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.post(
                    f"{FASTAPI_BASE_URL}/api/auth/register",
                    json={"email": email, "password": password, "name": name},
                )
                if resp.status_code in (200, 201):
                    data = resp.json()
                    _sync_user_dict(data)
                    try:
                        from pages import study_timer
                        study_timer.reset_timer_state()
                    except Exception:
                        try:
                            from pages import studytimer_backend_dalem
                            studytimer_backend_dalem.reset_timer_state()
                        except Exception:
                            pass
                    return data
                elif resp.status_code in (400, 422):
                    detail = resp.json().get("detail", "Registration failed")
                    raise ValueError(detail)
        except ValueError:
            raise
        except Exception:
            _server_state["online"] = False
    try:
        data = api.register(api.UserRegister(email=email, password=password, name=name))
    except api.HTTPException as e:
        raise ValueError(e.detail)
    _sync_user_dict(data)
    try:
        from pages import study_timer
        study_timer.reset_timer_state()
    except Exception:
        try:
            from pages import studytimer_backend_dalem
            studytimer_backend_dalem.reset_timer_state()
        except Exception:
            pass
    return data


def api_get_user_profile(user_id: Optional[int] = None) -> Dict[str, Any]:
    uid = user_id or state.CURRENT_USER_ID
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.get(f"{FASTAPI_BASE_URL}/api/users/{uid}")
                if resp.status_code == 200:
                    data = resp.json()
                    return _sync_user_dict(data)
        except Exception:
            _server_state["online"] = False
    data = api.get_user(uid)
    return _sync_user_dict(data)


def api_update_user_profile(updates: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
    uid = user_id or state.CURRENT_USER_ID
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.put(f"{FASTAPI_BASE_URL}/api/users/{uid}/profile", json=updates)
                if resp.status_code == 200:
                    data = resp.json()
                    return _sync_user_dict(data)
        except Exception:
            _server_state["online"] = False
    data = api.update_user_profile(uid, api.ProfileUpdate(**updates))
    return _sync_user_dict(data)


def api_get_user_stats(user_id: Optional[int] = None) -> Dict[str, Any]:
    uid = user_id or state.CURRENT_USER_ID
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.get(f"{FASTAPI_BASE_URL}/api/users/{uid}/stats")
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            _server_state["online"] = False
    return api.get_user_stats(uid)


def api_log_timer(minutes: int, user_id: Optional[int] = None) -> Dict[str, Any]:
    uid = user_id or state.CURRENT_USER_ID
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.post(
                    f"{FASTAPI_BASE_URL}/api/timer/log",
                    json={"user_id": uid, "minutes": minutes},
                )
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            _server_state["online"] = False
    return api.log_timer_session(api.TimerLogRequest(user_id=uid, minutes=minutes))


def api_get_decks(user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    uid = user_id or state.CURRENT_USER_ID
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.get(f"{FASTAPI_BASE_URL}/api/decks", params={"user_id": uid})
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            _server_state["online"] = False
    return api.get_decks(uid)


def api_create_deck(title: str, subject: str = "General Study", accent: str = "#13766B", progress: float = 0.2, user_id: Optional[int] = None) -> Dict[str, Any]:
    uid = user_id or state.CURRENT_USER_ID
    payload = {"user_id": uid, "title": title, "subject": subject, "accent": accent, "progress": progress}
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.post(f"{FASTAPI_BASE_URL}/api/decks", json=payload)
                if resp.status_code in (200, 201):
                    return resp.json()
        except Exception:
            _server_state["online"] = False
    return api.create_deck(api.DeckCreate(**payload))


def api_get_deck_cards(deck_id: Optional[int] = None) -> List[Dict[str, Any]]:
    did = deck_id or state.CURRENT_DECK_ID
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.get(f"{FASTAPI_BASE_URL}/api/decks/{did}/cards")
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            _server_state["online"] = False
    return api.get_flashcards(did)


def api_add_flashcard(deck_id: int, question: str, answer: str) -> Dict[str, Any]:
    payload = {"question": question, "answer": answer}
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.post(f"{FASTAPI_BASE_URL}/api/decks/{deck_id}/cards", json=payload)
                if resp.status_code in (200, 201):
                    return resp.json()
        except Exception:
            _server_state["online"] = False
    return api.add_flashcard(deck_id, api.FlashcardCreate(**payload))


def api_update_deck(deck_id: int, **updates) -> Dict[str, Any]:
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.patch(f"{FASTAPI_BASE_URL}/api/decks/{deck_id}", json=updates)
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            _server_state["online"] = False
    return api.update_deck(deck_id, api.DeckUpdate(**updates))


def api_delete_deck(deck_id: int) -> None:
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.delete(f"{FASTAPI_BASE_URL}/api/decks/{deck_id}")
                if resp.status_code in (200, 204):
                    return
        except Exception:
            _server_state["online"] = False
    api.delete_deck(deck_id)


def api_update_flashcard(card_id: int, **updates) -> Dict[str, Any]:
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.patch(f"{FASTAPI_BASE_URL}/api/flashcards/{card_id}", json=updates)
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            _server_state["online"] = False
    return api.update_flashcard(card_id, api.FlashcardUpdate(**updates))


def api_delete_flashcard(card_id: int) -> None:
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.delete(f"{FASTAPI_BASE_URL}/api/flashcards/{card_id}")
                if resp.status_code in (200, 204):
                    return
        except Exception:
            _server_state["online"] = False
    api.delete_flashcard(card_id)


def _deserialize_task(t: Dict[str, Any]) -> Dict[str, Any]:
    day_val = t.get("day")
    if isinstance(day_val, str):
        try:
            day_obj = date.fromisoformat(day_val.split("T")[0])
        except ValueError:
            day_obj = date.today()
    elif isinstance(day_val, date):
        day_obj = day_val
    else:
        day_obj = date.today()
    return {
        "id": t.get("id", t.get("task_id")),
        "title": t.get("title", t.get("task_name", "")),
        "day": day_obj,
        "start": float(t.get("start", 9.0)),
        "end": float(t.get("end", 10.0)),
        "color": t.get("color", "teal"),
        "done": bool(t.get("done", False)),
    }


def api_get_tasks(user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    uid = user_id or state.CURRENT_USER_ID
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.get(f"{FASTAPI_BASE_URL}/api/tasks", params={"user_id": uid})
                if resp.status_code == 200:
                    return [_deserialize_task(t) for t in resp.json()]
        except Exception:
            _server_state["online"] = False
    return [_deserialize_task(t) for t in api.get_tasks(uid)]


def api_create_task(title: str, day: Optional[date] = None, start: float = 9.0, end: float = 10.0, color: str = "teal", done: bool = False, user_id: Optional[int] = None) -> Dict[str, Any]:
    uid = user_id or state.CURRENT_USER_ID
    day_val = day or date.today()
    payload = {
        "user_id": uid,
        "title": title,
        "day": day_val.isoformat() if isinstance(day_val, date) else str(day_val),
        "start": start,
        "end": end,
        "color": color,
        "done": done,
    }
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.post(f"{FASTAPI_BASE_URL}/api/tasks", json=payload)
                if resp.status_code in (200, 201):
                    return _deserialize_task(resp.json())
        except Exception:
            _server_state["online"] = False
    return _deserialize_task(api.create_task(api.TaskCreate(**payload)))


def api_update_task(task_id: int, **updates) -> Dict[str, Any]:
    if "day" in updates and isinstance(updates["day"], date):
        updates["day"] = updates["day"].isoformat()
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.patch(f"{FASTAPI_BASE_URL}/api/tasks/{task_id}", json=updates)
                if resp.status_code == 200:
                    return _deserialize_task(resp.json())
        except Exception:
            _server_state["online"] = False
    return _deserialize_task(api.update_task(task_id, api.TaskUpdate(**updates)))


def api_delete_task(task_id: int) -> None:
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.delete(f"{FASTAPI_BASE_URL}/api/tasks/{task_id}")
                if resp.status_code in (200, 204):
                    return
        except Exception:
            _server_state["online"] = False
    api.delete_task(task_id)


def api_get_chats(user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    uid = user_id or state.CURRENT_USER_ID
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.get(f"{FASTAPI_BASE_URL}/api/chats", params={"user_id": uid})
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            _server_state["online"] = False
    return api.list_chats(uid)


def api_create_chat(user_id: Optional[int] = None) -> Dict[str, Any]:
    uid = user_id or state.CURRENT_USER_ID
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.post(f"{FASTAPI_BASE_URL}/api/chats", json={"user_id": uid})
                if resp.status_code in (200, 201):
                    return resp.json()
        except Exception:
            _server_state["online"] = False
    return api.create_chat(api.ChatCreate(user_id=uid))


def api_delete_chat(chat_id: int) -> Dict[str, Any]:
    if _is_fastapi_server_running():
        try:
            with httpx.Client(timeout=0.5) as client:
                resp = client.delete(f"{FASTAPI_BASE_URL}/api/chats/{chat_id}")
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            _server_state["online"] = False
    return api.delete_chat(chat_id)
