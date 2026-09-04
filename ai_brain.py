import os

from dotenv import load_dotenv
from openai import OpenAI

from tools import (
    get_active_disruptions,
    get_affected_classes,
    generate_recovery_plan
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("FEATHERLESS_API_KEY"),
    base_url="https://api.featherless.ai/v1"
)

MODEL = "Qwen/Qwen3-32B"


# ==========================================
# ASK FEATHERLESS AI
# ==========================================

def ask_ai(prompt):

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the autonomous decision-making layer "
                    "of CampusFlow, an AI campus operations agent. "
                    "You must choose the next operational action "
                    "based on the current campus state and workflow stage."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# ==========================================
# GET AI DECISION
# ==========================================

def get_ai_decision(campus_state):

    workflow_stage = campus_state.get(
        "workflow_stage",
        "UNKNOWN"
    )

    # ==========================================
    # HARD SAFETY RULE
    # ==========================================
    #
    # If the current recovery plan is invalid,
    # CampusFlow MUST generate a new plan.
    #
    # The LLM cannot override this operational rule.
    #

    if workflow_stage == "PLAN_INVALID":

        return "GENERATE_RECOVERY_PLAN"

    # ==========================================
    # BUILD AI PROMPT
    # ==========================================

    prompt = f"""
You are controlling CampusFlow, an autonomous campus operations agent.

Your job is to choose the NEXT ACTION required to resolve a campus
disruption.

CURRENT WORKFLOW STAGE:
{workflow_stage}

CAMPUS STATE:
{campus_state}

AVAILABLE ACTIONS:

INVESTIGATE
Inspect the disruption and determine its impact.

GENERATE_RECOVERY_PLAN
Generate a feasible recovery plan using the scheduling engine.

EXECUTE_RECOVERY
Apply the validated recovery plan to the campus timetable.

VERIFY
Check whether the recovery was successfully applied.

COMPLETE
Finish the workflow because the disruption has been resolved.

FOLLOW THESE WORKFLOW RULES:

1. If the workflow stage is UNKNOWN or INITIAL:
   choose INVESTIGATE.

2. If the workflow stage is INVESTIGATED:
   choose GENERATE_RECOVERY_PLAN.

3. If the workflow stage is PLAN_GENERATED:
   choose EXECUTE_RECOVERY.

4. If the workflow stage is PLAN_INVALID:
   choose GENERATE_RECOVERY_PLAN.

5. If the workflow stage is RECOVERY_EXECUTED:
   choose VERIFY.

6. If the workflow stage is VERIFIED:
   choose COMPLETE.

7. Never choose COMPLETE before verification.

8. Never execute recovery before a recovery plan exists.

9. If the recovery plan is invalid, do not execute it.

10. When the workflow stage is PLAN_INVALID, a NEW recovery
    plan must be generated before attempting execution.

11. The scheduling engine is the source of truth for timetable
    feasibility. Do not invent timetable slots.

Return ONLY ONE exact action:

INVESTIGATE
GENERATE_RECOVERY_PLAN
EXECUTE_RECOVERY
VERIFY
COMPLETE
"""

    # ==========================================
    # ASK FEATHERLESS
    # ==========================================

    response = ask_ai(prompt)

    # ==========================================
    # CLEAN RESPONSE
    # ==========================================

    response = response.strip().upper()

    valid_actions = [
        "INVESTIGATE",
        "GENERATE_RECOVERY_PLAN",
        "EXECUTE_RECOVERY",
        "VERIFY",
        "COMPLETE"
    ]

    for action in valid_actions:

        if action in response:

            return action

    # ==========================================
    # FALLBACK
    # ==========================================

    return "INVESTIGATE"


# ==========================================
# TEST AI BRAIN
# ==========================================

if __name__ == "__main__":

    disruptions = get_active_disruptions()

    affected_classes = get_affected_classes()

    recovery_plan = generate_recovery_plan()

    campus_state = {
        "disruptions": disruptions,
        "affected_classes": affected_classes,
        "recovery_plan": recovery_plan,
        "workflow_stage": "PLAN_GENERATED"
    }

    print("\n=== CAMPUSFLOW AI ===")

    decision = get_ai_decision(
        campus_state
    )

    print("\nAI NEXT ACTION")
    print("--------------")
    print(decision)