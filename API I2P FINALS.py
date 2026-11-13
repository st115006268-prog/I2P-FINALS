from contextlib import asynccontextmanager
from fastapi import FastAPI
import flet as ft
import flet.fastapi as flet_fastapi
import httpx # Used for the Flet UI to make async API calls

# 1. Manage the background tasks for Flet (like cleaning up inactive user sessions)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await flet_fastapi.app_manager.start()
    yield
    await flet_fastapi.app_manager.shutdown()

# 2. Initialize the FastAPI server
app = FastAPI(lifespan=lifespan)

# ==========================================
# 3. YOUR FASTAPI BACKEND (REST ENDPOINTS)
# ==========================================
@app.get("/api/data")
async def get_data():
    return {
        "status": "success", 
        "message": "Flet 1.0 and FastAPI are working together!"
    }

# ==========================================
# 4. YOUR FLET 1.0 FRONTEND UI
# ==========================================
async def main(page: ft.Page):
    page.title = "Flet 1.0 + FastAPI"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    api_result = ft.Text("Press the button to call the /api/data endpoint")

    async def call_our_api(e):
        api_result.value = "Fetching..."
        page.update()
        
        # Use httpx to call our own FastAPI endpoint asynchronously
        async with httpx.AsyncClient() as client:
            # We use localhost since the API and UI are on the same server
            response = await client.get("http://127.0.0.1:8000/api/data")
            data = response.json()
            
            api_result.value = f"API Response:\n{data['message']}"
            page.update()

    # Build the UI
    page.add(
        ft.Text("Full-Stack Flet 1.0 App", size=24, weight=ft.FontWeight.BOLD),
        ft.ElevatedButton("Call My Local API", on_click=call_our_api),
        api_result
    )

# 5. Mount the Flet UI to the FastAPI app
# CRITICAL: Mount this LAST, after all your custom /api/ routes!
app.mount("/", flet_fastapi.app(main))