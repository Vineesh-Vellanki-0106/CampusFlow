import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from agent_core import run_agent
from tools import (
    get_timetable,
    get_active_disruptions,
    get_affected_classes,
    generate_recovery_plan
)


app = FastAPI(
    title="CampusFlow API",
    description="Autonomous AI Campus Operations Agent",
    version="1.0.0"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "https://campusflow-1-pbo8.onrender.com",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# ROOT
# ==========================================

@app.get("/")
def root():

    return {
        "application": "CampusFlow",
        "status": "online",
        "message": "Autonomous campus operations agent is running."
    }


# ==========================================
# TIMETABLE
# ==========================================

@app.get("/timetable")
def timetable():

    return get_timetable()
class TimetableUpdate(BaseModel):
    classes: list[dict]


@app.post("/timetable")
def update_timetable(data: TimetableUpdate):
    with open("data/timetable.json", "w") as file:
        json.dump({"classes": data.classes}, file, indent=2)

    return {
        "status": "updated",
        "message": "Timetable updated successfully.",
        "timetable": {"classes": data.classes}
    }


# ==========================================
# DISRUPTIONS
# ==========================================

@app.get("/disruptions")
def disruptions():

    return {
        "disruptions": get_active_disruptions()
    }


# ==========================================
# CAMPUS STATE
# ==========================================

@app.get("/campus-state")
def campus_state():

    affected = get_affected_classes()

    plan = generate_recovery_plan()

    return {
        "affected_classes": affected,
        "recovery_plan": plan,
        "disruptions": get_active_disruptions(),
        "timetable": get_timetable()
    }


# ==========================================
# AUTONOMOUS AGENT
# ==========================================

@app.post("/run-agent")
def run_campusflow_agent():

    result = run_agent()

    return result
# ==========================================
# RESET DEMO SCENARIO
# ==========================================

@app.post("/reset")
def reset_demo():

    with open(
        "data/original_timetable.json",
        "r"
    ) as file:

        original = json.load(file)

    with open(
        "data/timetable.json",
        "w"
    ) as file:

        json.dump(
            original,
            file,
            indent=2
        )

    return {
        "status": "reset",
        "message": "CampusFlow demo scenario reset successfully.",
        "timetable": original
    }