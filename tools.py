import json


# ==========================================
# TIMETABLE
# ==========================================

def get_timetable():
    with open("data/timetable.json", "r") as file:
        timetable = json.load(file)

    return timetable


# ==========================================
# DISRUPTIONS
# ==========================================

def get_active_disruptions():
    with open("data/disruptions.json", "r") as file:
        disruptions = json.load(file)

    return disruptions["active_disruptions"]


# ==========================================
# FIND AFFECTED CLASSES
# ==========================================

def get_affected_classes():

    timetable = get_timetable()
    disruptions = get_active_disruptions()

    affected_classes = []

    for disruption in disruptions:

        # --------------------------------------
        # College-wide suspension
        # --------------------------------------

        if disruption["type"] == "college_suspension":

            for class_info in timetable["classes"]:

                if class_info["day"] == disruption["day"]:

                    affected_classes.append(class_info)

        # --------------------------------------
        # Faculty unavailable
        # --------------------------------------

        elif disruption["type"] == "faculty_unavailable":

            for class_info in timetable["classes"]:

                if (
                    class_info["faculty"] == disruption["faculty"]
                    and class_info["day"] == disruption["day"]
                    and class_info["slot"] == disruption["slot"]
                ):

                    affected_classes.append(class_info)

    return affected_classes


# ==========================================
# SUBJECT PRIORITY
# ==========================================

def get_subject_priority(subject):

    with open("data/priorities.json", "r") as file:
        priorities = json.load(file)

    return priorities["subjects"].get(subject)


# ==========================================
# FACULTY AVAILABILITY
# ==========================================

def get_faculty_availability(faculty):

    with open("data/faculty_availability.json", "r") as file:
        availability = json.load(file)

    return availability["faculty"].get(faculty, {})


def get_available_slots(faculty):

    availability = get_faculty_availability(faculty)

    available_slots = []

    for day, slots in availability.items():

        for slot in slots:

            available_slots.append({
                "day": day,
                "slot": slot
            })

    return available_slots


# ==========================================
# ROOM AVAILABILITY
# ==========================================

def get_room_availability(room):

    with open("data/room_availability.json", "r") as file:
        availability = json.load(file)

    return availability["rooms"].get(room, {})


# ==========================================
# FIND FEASIBLE FACULTY + ROOM SLOTS
# ==========================================

def find_feasible_slots(faculty, room):

    faculty_slots = get_faculty_availability(faculty)
    room_slots = get_room_availability(room)

    feasible_slots = []

    for day, slots in faculty_slots.items():

        for slot in slots:

            if slot in room_slots.get(day, []):

                feasible_slots.append({
                    "day": day,
                    "slot": slot
                })

    return feasible_slots


# ==========================================
# GENERATE RECOVERY CANDIDATES
# ==========================================

def generate_recovery_candidates(class_info):

    faculty = class_info["faculty"]
    room = class_info["room"]

    feasible_slots = find_feasible_slots(
        faculty,
        room
    )

    priority_info = get_subject_priority(
        class_info["subject"]
    )

    candidates = []

    for slot in feasible_slots:

        candidates.append({

            "class_id": class_info["id"],

            "subject": class_info["subject"],

            "faculty": faculty,

            "room": room,

            "original_day": class_info["day"],

            "original_slot": class_info["slot"],

            "new_day": slot["day"],

            "new_slot": slot["slot"],

            "priority": priority_info["priority"],

            "priority_reason": priority_info["reason"]

        })

    return candidates


# ==========================================
# DISRUPTION SCORE
# ==========================================

def calculate_disruption_score(
    class_info,
    candidate
):

    disruption = 0

    # Changing time causes more disruption
    if class_info["slot"] != candidate["new_slot"]:

        disruption += 2

    # Changing day causes disruption
    if class_info["day"] != candidate["new_day"]:

        disruption += 1

    priority = candidate["priority"]

    final_score = (
        disruption * 10
    ) - priority

    return final_score


# ==========================================
# CHECK PLAN CONFLICTS
# ==========================================

def has_conflict(plan, candidate):

    for assigned in plan:

        if (
            assigned["recommended_day"]
            == candidate["new_day"]

            and

            assigned["recommended_slot"]
            == candidate["new_slot"]
        ):

            return True

    return False


# ==========================================
# GENERATE RECOVERY PLAN
# ==========================================

def generate_recovery_plan():

    # Load the original timetable.
    # This is the permanent source of truth for
    # where classes originally belong.
    with open("data/original_timetable.json", "r") as file:
        original_timetable = json.load(file)

    affected_classes = get_affected_classes()

    plan = []

    # --------------------------------------
    # Build recovery objects from ORIGINAL
    # timetable information
    # --------------------------------------

    recovery_classes = []

    for affected in affected_classes:

        original_class = None

        for class_info in original_timetable["classes"]:

            if class_info["id"] == affected["id"]:
                original_class = class_info
                break

        if original_class is None:
            continue

        recovery_classes.append({
            "id": original_class["id"],
            "section": original_class["section"],
            "subject": original_class["subject"],
            "faculty": original_class["faculty"],
            "room": original_class["room"],
            "day": original_class["day"],
            "slot": original_class["slot"]
        })

    # --------------------------------------
    # Remove duplicate affected classes
    # --------------------------------------

    unique_classes = {}

    for class_info in recovery_classes:

        unique_classes[class_info["id"]] = class_info

    recovery_classes = list(
        unique_classes.values()
    )

    # --------------------------------------
    # Highest priority first
    # --------------------------------------

    recovery_classes.sort(
        key=lambda c:
        get_subject_priority(
            c["subject"]
        )["priority"],
        reverse=True
    )

    # --------------------------------------
    # Generate recovery candidates
    # --------------------------------------

    for class_info in recovery_classes:

        candidates = generate_recovery_candidates(
            class_info
        )

        scored_candidates = []

        for candidate in candidates:

            if has_conflict(
                plan,
                candidate
            ):
                continue

            score = calculate_disruption_score(
                class_info,
                candidate
            )

            scored_candidates.append({

                "candidate": candidate,

                "score": score

            })

        # Lowest disruption score wins
        scored_candidates.sort(
            key=lambda x: x["score"]
        )

        if scored_candidates:

            best = scored_candidates[0]

            plan.append({

                "class_id":
                    class_info["id"],

                "subject":
                    class_info["subject"],

                "faculty":
                    class_info["faculty"],

                "room":
                    class_info["room"],

                "original_day":
                    class_info["day"],

                "original_slot":
                    class_info["slot"],

                "recommended_day":
                    best["candidate"]["new_day"],

                "recommended_slot":
                    best["candidate"]["new_slot"],

                "priority":
                    best["candidate"]["priority"],

                "priority_reason":
                    best["candidate"]["priority_reason"],

                "score":
                    best["score"]

            })

    return plan

# ==========================================
# VALIDATE RECOVERY PLAN
# ==========================================

def validate_recovery_plan(plan):

    """
    Check whether the proposed recovery plan
    is still valid under the current campus
    conditions.
    """

    disruptions = get_active_disruptions()

    conflicts = []

    for item in plan:

        faculty = item["faculty"] \
            if "faculty" in item \
            else None

        room = item["room"] \
            if "room" in item \
            else None

        day = item["recommended_day"]

        slot = item["recommended_slot"]

        # --------------------------------------
        # Faculty availability check
        # --------------------------------------

        for disruption in disruptions:

            if disruption["type"] == "faculty_unavailable":

                if (
                    faculty
                    and disruption["faculty"] == faculty
                    and disruption["day"] == day
                    and disruption["slot"] == slot
                ):

                    conflicts.append({

                        "class_id":
                            item["class_id"],

                        "subject":
                            item["subject"],

                        "type":
                            "faculty_unavailable",

                        "faculty":
                            faculty,

                        "day":
                            day,

                        "slot":
                            slot,

                        "reason":
                            disruption["reason"]

                    })

            # --------------------------------------
            # Room availability check
            # --------------------------------------

            elif disruption["type"] == "room_unavailable":

                if (
                    room
                    and disruption["room"] == room
                    and disruption["day"] == day
                    and disruption["slot"] == slot
                ):

                    conflicts.append({

                        "class_id":
                            item["class_id"],

                        "subject":
                            item["subject"],

                        "type":
                            "room_unavailable",

                        "room":
                            room,

                        "day":
                            day,

                        "slot":
                            slot,

                        "reason":
                            disruption["reason"]

                    })

    return {

        "valid":
            len(conflicts) == 0,

        "conflicts":
            conflicts

    }


# ==========================================
# APPLY RECOVERY PLAN
# ==========================================

def apply_recovery_plan(plan):

    """
    Apply the exact recovery plan supplied by
    the autonomous agent.

    The agent decides which plan should be executed.
    This function only executes that decision.
    """

    if not plan:

        return {
            "status": "failed",
            "message": "No recovery plan provided."
        }

    timetable = get_timetable()

    applied = []

    for item in plan:

        for class_info in timetable["classes"]:

            if class_info["id"] == item["class_id"]:

                # Apply the exact decision made
                # by the agent.
                class_info["day"] = (
                    item["recommended_day"]
                )

                class_info["slot"] = (
                    item["recommended_slot"]
                )

                applied.append({
                    "class_id":
                        item["class_id"],

                    "subject":
                        item["subject"],

                    "day":
                        item["recommended_day"],

                    "slot":
                        item["recommended_slot"]
                })

                break

    with open(
        "data/timetable.json",
        "w"
    ) as file:

        json.dump(
            timetable,
            file,
            indent=2
        )

    return {
        "status": "success",
        "message": "Recovery plan applied successfully.",
        "applied": applied
    }
# ==========================================
# GENERATE REPLAN
# ==========================================

def generate_replan(invalid_plan):
    """
    Generate a new recovery plan for actions that
    became invalid because campus conditions changed.
    """

    disruptions = get_active_disruptions()

    replan = []

    for item in invalid_plan:

        class_info = {
            "id": item["class_id"],
            "section": "CSE-A",
            "subject": item["subject"],
            "faculty": item["faculty"],
            "room": item["room"],
            "day": item["original_day"],
            "slot": item["original_slot"]
        }

        candidates = generate_recovery_candidates(
            class_info
        )

        scored_candidates = []

        for candidate in candidates:

            # --------------------------------------
            # Check candidate against disruptions
            # --------------------------------------

            candidate_blocked = False

            for disruption in disruptions:

                # Faculty unavailable
                if disruption["type"] == "faculty_unavailable":

                    if (
                        disruption["faculty"]
                        == candidate["faculty"]
                        and disruption["day"]
                        == candidate["new_day"]
                        and disruption["slot"]
                        == candidate["new_slot"]
                    ):

                        candidate_blocked = True

                # Room unavailable
                elif disruption["type"] == "room_unavailable":

                    if (
                        disruption["room"]
                        == candidate["room"]
                        and disruption["day"]
                        == candidate["new_day"]
                        and disruption["slot"]
                        == candidate["new_slot"]
                    ):

                        candidate_blocked = True

            if candidate_blocked:
                continue

            score = calculate_disruption_score(
                class_info,
                candidate
            )

            scored_candidates.append({

                "candidate": candidate,

                "score": score

            })

        # --------------------------------------
        # Select best valid alternative
        # --------------------------------------

        scored_candidates.sort(
            key=lambda x: x["score"]
        )

        if scored_candidates:

            best = scored_candidates[0]

            replan.append({

                "class_id":
                    class_info["id"],

                "subject":
                    class_info["subject"],

                "faculty":
                    class_info["faculty"],

                "room":
                    class_info["room"],

                "original_day":
                    class_info["day"],

                "original_slot":
                    class_info["slot"],

                "recommended_day":
                    best["candidate"]["new_day"],

                "recommended_slot":
                    best["candidate"]["new_slot"],

                "priority":
                    best["candidate"]["priority"],

                "priority_reason":
                    best["candidate"]["priority_reason"],

                "score":
                    best["score"]

            })

    return replan
# ==========================================
# RESET TIMETABLE
# ==========================================

def reset_timetable():

    """
    Restore the live timetable from the
    original timetable.

    This gives CampusFlow a clean starting
    state for every demo run.
    """

    with open(
        "data/original_timetable.json",
        "r"
    ) as file:

        original_timetable = json.load(file)

    with open(
        "data/timetable.json",
        "w"
    ) as file:

        json.dump(
            original_timetable,
            file,
            indent=2
        )

    return {
        "status": "success",
        "message": "Timetable reset successfully."
    }