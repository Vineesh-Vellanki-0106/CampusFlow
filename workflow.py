from tools import (
    get_active_disruptions,
    get_affected_classes,
    generate_recovery_plan,
    apply_recovery_plan,
    get_timetable
)


def run_campusflow():

    print("\n=== CAMPUSFLOW AUTONOMOUS WORKFLOW ===\n")

    # 1. Detect disruption
    disruptions = get_active_disruptions()

    print("1. Disruption detected:")
    print(disruptions)

    # 2. Investigate impact
    affected = get_affected_classes()

    print(f"\n2. Affected classes: {len(affected)}")

    for class_info in affected:
        print(
            f"   - {class_info['id']}: "
            f"{class_info['subject']} "
            f"({class_info['faculty']})"
        )

    # 3. Generate recovery plan
    plan = generate_recovery_plan()

    print("\n3. Recovery plan generated:")

    for item in plan:
        print(
            f"   - {item['subject']}: "
            f"{item['recommended_day']} "
            f"{item['recommended_slot']} "
            f"(Priority {item['priority']})"
        )

    # 4. Execute the decision
    print("\n4. Executing recovery plan...")

    apply_result = apply_recovery_plan()

    print("   Recovery plan applied successfully.")

    # 5. Verify
    print("\n5. Verification:")

    verified_timetable = get_timetable()

    for class_info in verified_timetable["classes"]:
        print(
            f"   - {class_info['id']}: "
            f"{class_info['subject']} -> "
            f"{class_info['day']} "
            f"{class_info['slot']}"
        )

    print("\n=== CAMPUSFLOW WORKFLOW COMPLETE ===")


if __name__ == "__main__":
    run_campusflow()