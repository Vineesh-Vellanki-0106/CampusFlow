# CampusFlow

### Autonomous AI Campus Operations Agent

> **CampusFlow autonomously investigates campus disruptions, plans recovery actions, executes them, verifies the result, and replans when necessary.**

CampusFlow is an AI-powered campus operations system designed around **autonomous multi-step workflows** rather than simple chatbot interactions.

It demonstrates how an AI agent can reason about a real-world college disruption, use operational tools, make a decision, execute that decision, and verify the outcome.

---

## 🚨 Problem

College operations frequently depend on static schedules and manual coordination.

For example, when an unexpected holiday or college suspension occurs:

- Multiple classes are missed.
- High-priority subjects may fall behind.
- Faculty availability may conflict with recovery plans.
- Rooms may already be occupied.
- Administrators must manually coordinate a new timetable.
- A change in one resource can create additional conflicts.

A simple timetable generator cannot continuously reason about these constraints.

**CampusFlow treats this as an autonomous operations problem.**

---

## 💡 Solution

CampusFlow introduces an autonomous AI agent that manages campus disruptions through a closed-loop workflow:

```text
Disruption
    ↓
Investigation
    ↓
Impact Analysis
    ↓
Recovery Planning
    ↓
Plan Validation
    ↓
Replanning if Required
    ↓
Execution
    ↓
Verification
    ↓
Task Completion

## Architecture

CampusFlow separates **reasoning** from **feasibility**. This is deliberate.

| Layer | File | Responsibility |
|---|---|---|
| Reasoning | `ai_brain.py` | Featherless AI (`Qwen/Qwen3-32B`) selects the next workflow action |
| Orchestration | `agent_core.py` | Closed-loop state machine, iteration guard, event log |
| Constraints | `tools.py` | Deterministic scheduling, validation, conflict detection, replanning |
| API | `api.py` | FastAPI endpoints consumed by the React frontend |
| Data | `data/*.json` | Synthetic campus state (timetable, faculty, rooms, priorities) |

The language model never writes a timetable slot. It chooses *which operation to
perform next*; `tools.py` decides what is feasible and is the sole source of truth
for the schedule. This makes hallucinated or conflicting timetables structurally
impossible rather than merely unlikely.

Replanning on an invalid plan is a hard guardrail in code, not a model decision —
the agent is never permitted to skip validation.

## Running locally

Requires Python 3.10+ and Node 18+.

### Backend

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then add your Featherless key
uvicorn api:app --reload --port 8001
```

Run from the repository root — `tools.py` resolves `data/` relatively.

### Frontend

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

The frontend falls back to `http://127.0.0.1:8001` when `VITE_API_URL` is unset.

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/timetable` | Current timetable |
| GET | `/disruptions` | Active disruptions |
| GET | `/campus-state` | Timetable, disruptions, affected classes, current plan |
| POST | `/run-agent` | Execute the full autonomous recovery workflow |
| POST | `/reset` | Restore the pre-disruption demo state |

Quick check:

```bash
curl http://127.0.0.1:8001/campus-state
curl -X POST http://127.0.0.1:8001/run-agent
```

## Data

The prototype runs on **synthetic campus data** in `data/`. No real institutional
data is integrated. The tool interfaces in `tools.py` are the seam: swapping the
JSON loaders for institutional timetable, faculty-availability, room-availability
and academic-priority feeds requires no change to the agent loop.

## Team

**CertainX** — Track 4, Autonomous AI Workflows