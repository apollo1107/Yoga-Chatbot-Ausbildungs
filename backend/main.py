from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from pydantic import BaseModel
from backend.chat_logic import *
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ASSISTANT_ID = os.getenv("YOGA_ASSISTANT_ID")  # Set this after running assistant_setup.py

class ChatInput(BaseModel):
    session_id: str | None = None
    message: str

SESSION_TIMEOUT = timedelta(minutes=30)

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
def chat_route(input: ChatInput):
    session_id = input.session_id or str(uuid.uuid4())
    message = input.message

    now = datetime.utcnow()
    expired = [sid for sid, s in user_sessions.items() if now - s.get("last_active", now) > SESSION_TIMEOUT]
    for sid in expired:
        del user_sessions[sid]

    if session_id not in user_sessions:
        thread_id = init_thread(ASSISTANT_ID)
        user_sessions[session_id] = {"step": 0, "answers": [], "thread_id": thread_id}

    session = user_sessions[session_id]
    session["last_active"] = datetime.utcnow()

    if session["step"] < len(QUESTIONS):
        valid, suggestion = validate_answer(session["step"], message)
        if not valid:
            return {"reply": suggestion, "session_id": session_id}
        
        send_user_message(session["thread_id"], message)
        session["answers"].append(message)
        session["step"] += 1
        q = next_question(session["step"])
        if q:
            return {"reply": q, "session_id": session_id}
        else:
            send_user_message(session["thread_id"], "Bitte empfehle einen passenden Kurs.")
            answer = run_assistant(session["thread_id"], ASSISTANT_ID)
            return {"reply": answer, "session_id": session_id, "done": True}
    else:
        send_user_message(session["thread_id"], message)
        answer = run_assistant(session["thread_id"], ASSISTANT_ID)
        return {"reply": answer, "session_id": session_id}
