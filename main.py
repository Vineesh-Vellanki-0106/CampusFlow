from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tools import (
    get_active_disruptions,
    get_affected_classes,
    get_timetable,
    generate_recovery_plan
)

from agent_core import run_agent


app = FastAPI(title="CampusFlow API")


# Allow the React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "CampusFlow API is running",
        "status": "active"
    }


@app.get("/api/campus-state")
def campus_state():
    return {
        "disruptions": get_active_disruptions(),
        "affected_classes": get_affected_classes(),
        "timetable": get_timetable()
    }


@app.post("/api/recover")
def recover_campus():
    result = run_agent()

    return result


@app.get("/api/recovery-plan")
def recovery_plan():
    return {
        "plan": generate_recovery_plan()
    }