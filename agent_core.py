from datetime import datetime

from tools import (
    reset_timetable,
    get_active_disruptions,
    get_affected_classes,
    generate_recovery_plan,
    validate_recovery_plan,
    generate_replan,
    apply_recovery_plan,
    get_timetable
)

from ai_brain import get_ai_decision


def create_event(label, detail, status="done"):
    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "label": label,
        "detail": detail,
        "status": status
    }


def run_agent():

    events = []
    # =================================
    # RESET DEMO STATE
    # =================================

    reset_timetable()

    print("Timetable reset to original state.")

    print("\n================================")
    print("       CAMPUSFLOW AGENT")
    print("================================\n")

    # =================================
    # 1. DETECT DISRUPTION
    # =================================

    disruptions = get_active_disruptions()

    events.append(
        create_event(
            "DISRUPTION DETECTED",
            f"{len(disruptions)} active disruption(s)"
        )
    )

    print("1. DISRUPTION DETECTED")
    print(disruptions)

    # =================================
    # 2. INVESTIGATE IMPACT
    # =================================

    affected_classes = get_affected_classes()

    events.append(
        create_event(
            "IMPACT INVESTIGATED",
            f"{len(affected_classes)} classes affected"
        )
    )

    print(f"\n2. AFFECTED CLASSES: {len(affected_classes)}")

    for class_info in affected_classes:
        print(
            f"   - {class_info['id']}: "
            f"{class_info['subject']} "
            f"({class_info['faculty']})"
        )

    # =================================
    # 3. GENERATE INITIAL PLAN
    # =================================

    events.append(
        create_event(
            "RECOVERY PLANNING",
            "Evaluating faculty, room, time and priority constraints",
            "active"
        )
    )

    print("\n3. GENERATING RECOVERY PLAN...")

    recovery_plan = generate_recovery_plan()

    events[-1]["status"] = "done"

    events.append(
        create_event(
            "RECOVERY PLAN GENERATED",
            f"{len(recovery_plan)} recovery actions created"
        )
    )

    print("\nRECOVERY PLAN")

    for item in recovery_plan:
        print(
            f"   - {item['subject']} -> "
            f"{item['recommended_day']} "
            f"{item['recommended_slot']} "
            f"(Priority {item['priority']})"
        )

    # =================================
    # 4. BUILD CAMPUS STATE
    # =================================

    campus_state = {
        "disruptions": disruptions,
        "affected_classes": affected_classes,
        "recovery_plan": recovery_plan,
        "workflow_stage": "PLAN_GENERATED"
    }

    # =================================
    # 5. INITIAL VALIDATION
    # =================================

    print("\nVALIDATING RECOVERY PLAN...")

    validation = validate_recovery_plan(
        recovery_plan
    )

    campus_state["validation"] = validation

    if validation["valid"]:

        events.append(
            create_event(
                "PLAN VALIDATED",
                "Recovery plan satisfies current campus constraints"
            )
        )

        print("PLAN VALID: YES")

    else:

        events.append(
            create_event(
                "PLAN VALIDATION FAILED",
                f"{len(validation['conflicts'])} conflict(s) detected",
                "error"
            )
        )

        print("PLAN VALID: NO")

        for conflict in validation["conflicts"]:
            print(
                f"   - {conflict['class_id']}: "
                f"{conflict['reason']}"
            )

        campus_state["workflow_stage"] = "PLAN_INVALID"

    # =================================
    # 6. AUTONOMOUS AI LOOP
    # =================================

    print("\n================================")
    print("       AUTONOMOUS AI LOOP")
    print("================================")

    max_iterations = 7

    for iteration in range(max_iterations):

        print(
            f"\nAI DECISION CYCLE "
            f"{iteration + 1}/{max_iterations}"
        )

        # ---------------------------------
        # Ask Featherless
        # ---------------------------------

        events.append(
            create_event(
                "AI DECISION",
                f"Decision cycle {iteration + 1}",
                "active"
            )
        )

        action = get_ai_decision(
            campus_state
        )

        events[-1]["status"] = "done"

        events.append(
            create_event(
                "AI SELECTED ACTION",
                action
            )
        )

        print(f"AI DECISION: {action}")

        # =================================
        # INVESTIGATE
        # =================================

        if action == "INVESTIGATE":

            print("\nAI requested investigation.")

            affected_classes = get_affected_classes()

            campus_state["affected_classes"] = (
                affected_classes
            )

            campus_state["workflow_stage"] = (
                "INVESTIGATED"
            )

            events.append(
                create_event(
                    "INVESTIGATION COMPLETED",
                    f"{len(affected_classes)} affected classes confirmed"
                )
            )

        # =================================
        # GENERATE PLAN / REPLAN
        # =================================

        elif action == "GENERATE_RECOVERY_PLAN":

            # ---------------------------------
            # If the previous plan was invalid,
            # generate an alternative plan.
            # ---------------------------------

            if (
                campus_state["workflow_stage"]
                == "PLAN_INVALID"
            ):

                print(
                    "\nAI requested replanning."
                )

                events.append(
                    create_event(
                        "REPLANNING",
                        "Generating alternatives after plan validation failure",
                        "active"
                    )
                )

                replanned = generate_replan(
                    campus_state["recovery_plan"]
                )

                events[-1]["status"] = "done"

                if replanned:

                    recovery_plan = replanned

                    campus_state["recovery_plan"] = (
                        replanned
                    )

                    # Validate the new plan immediately.
                    revalidation = validate_recovery_plan(
                        replanned
                    )

                    campus_state["validation"] = (
                        revalidation
                    )

                    if revalidation["valid"]:

                        campus_state["workflow_stage"] = (
                            "PLAN_GENERATED"
                        )

                        events.append(
                            create_event(
                                "REPLAN GENERATED",
                                f"{len(replanned)} alternative action(s) created"
                            )
                        )

                        events.append(
                            create_event(
                                "REPLAN VALIDATED",
                                "Alternative recovery plan is feasible"
                            )
                        )

                        print(
                            "\nREPLAN VALID: YES"
                        )

                        for item in replanned:
                            print(
                                f"   - {item['subject']} -> "
                                f"{item['recommended_day']} "
                                f"{item['recommended_slot']}"
                            )

                    else:

                        campus_state["workflow_stage"] = (
                            "PLAN_INVALID"
                        )

                        events.append(
                            create_event(
                                "REPLAN FAILED",
                                "Alternative plan still contains conflicts",
                                "error"
                            )
                        )

                        print(
                            "\nREPLAN VALID: NO"
                        )

                else:

                    events.append(
                        create_event(
                            "REPLAN FAILED",
                            "No feasible alternative found",
                            "error"
                        )
                    )

            # ---------------------------------
            # Normal plan generation
            # ---------------------------------

            else:

                print(
                    "\nAI requested recovery-plan generation."
                )

                recovery_plan = generate_recovery_plan()

                campus_state["recovery_plan"] = (
                    recovery_plan
                )

                campus_state["workflow_stage"] = (
                    "PLAN_GENERATED"
                )

                events.append(
                    create_event(
                        "RECOVERY PLAN GENERATED",
                        f"{len(recovery_plan)} actions created"
                    )
                )

        # =================================
        # EXECUTE RECOVERY
        # =================================

        elif action == "EXECUTE_RECOVERY":

            print("\nEXECUTING RECOVERY PLAN...")

            # ---------------------------------
            # ALWAYS validate immediately before
            # executing.
            # ---------------------------------

            validation = validate_recovery_plan(
                recovery_plan
            )

            campus_state["validation"] = validation

            if not validation["valid"]:

                print(
                    "\nRECOVERY PLAN IS INVALID."
                )

                events.append(
                    create_event(
                        "RECOVERY BLOCKED",
                        f"{len(validation['conflicts'])} conflict(s) detected before execution",
                        "error"
                    )
                )

                campus_state["workflow_stage"] = (
                    "PLAN_INVALID"
                )

                continue

            events.append(
                create_event(
                    "EXECUTING RECOVERY",
                    "Applying validated recovery plan",
                    "active"
                )
            )

            result = apply_recovery_plan(
                recovery_plan
            )

            events[-1]["status"] = "done"

            campus_state["workflow_stage"] = (
                "RECOVERY_EXECUTED"
            )

            events.append(
                create_event(
                    "RECOVERY EXECUTED",
                    "Recovery plan applied to campus timetable"
                )
            )

            print(
                "Recovery plan executed successfully."
            )

        # =================================
        # VERIFY
        # =================================

        elif action == "VERIFY":

            print(
                "\nVERIFYING CAMPUS STATE..."
            )

            events.append(
                create_event(
                    "VERIFYING CAMPUS STATE",
                    "Checking updated timetable",
                    "active"
                )
            )

            verified_timetable = get_timetable()

            events[-1]["status"] = "done"

            print(
                f"Classes in timetable: "
                f"{len(verified_timetable['classes'])}"
            )

            campus_state["workflow_stage"] = (
                "VERIFIED"
            )

            events.append(
                create_event(
                    "CAMPUS STATE VERIFIED",
                    f"{len(verified_timetable['classes'])} classes checked"
                )
            )

        # =================================
        # COMPLETE
        # =================================

        elif action == "COMPLETE":

            print(
                "\nCAMPUSFLOW: TASK COMPLETE"
            )

            events.append(
                create_event(
                    "RECOVERY COMPLETED",
                    "CampusFlow determined that the disruption was resolved"
                )
            )

            return {
                "action": action,
                "status": "completed",
                "message": "Autonomous recovery completed successfully.",
                "recovery_plan": recovery_plan,
                "events": events
            }

        # =================================
        # UNKNOWN ACTION
        # =================================

        else:

            print(
                "\nAI returned an unknown action."
            )

            events.append(
                create_event(
                    "UNKNOWN AI ACTION",
                    action,
                    "error"
                )
            )

            return {
                "action": action,
                "status": "error",
                "message": "AI returned an unknown action.",
                "events": events
            }

    # =================================
    # MAX ITERATIONS
    # =================================

    events.append(
        create_event(
            "AGENT STOPPED",
            "Maximum decision cycles reached",
            "error"
        )
    )

    return {
        "action": "MAX_ITERATIONS",
        "status": "error",
        "message": "Agent reached the maximum number of decision cycles.",
        "recovery_plan": recovery_plan,
        "events": events
    }


if __name__ == "__main__":
    run_agent()