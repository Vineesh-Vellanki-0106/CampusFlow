import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import (
    get_timetable,
    get_active_disruptions,
    get_affected_classes,
    get_subject_priority,
    generate_recovery_plan,
    apply_recovery_plan
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("FEATHERLESS_API_KEY"),
    base_url="https://api.featherless.ai/v1"
)

MODEL = "Qwen/Qwen3-32B"
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_timetable",
            "description": "Get the current college timetable.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_active_disruptions",
            "description": "Get all currently active campus disruptions.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "get_affected_classes",
        "description": "Get all timetable classes affected by the active disruptions.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "get_subject_priority",
        "description": "Get the recovery priority and reason for a specific subject.",
        "parameters": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "The subject whose recovery priority should be checked."
                }
            },
            "required": ["subject"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "generate_recovery_plan",
        "description": "Generate a feasible recovery plan for all classes affected by the current disruption. The plan prioritizes important classes and avoids scheduling conflicts.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "apply_recovery_plan",
        "description": "Apply the best feasible recovery plan to the campus timetable.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
},
]


def ask_agent(message):
    messages = [
        {
            "role": "system",
            "content": (
                "You are CampusFlow, an autonomous campus operations agent. "
                "Investigate campus disruptions using the available tools. "
                "Use tools to gather information and make decisions. "
                "Do not invent timetable data."
            )
        },
        {
            "role": "user",
            "content": message
        }
    ]

    for _ in range(10):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools
        )

        assistant_message = response.choices[0].message

        # If the model has finished using tools, return its answer.
        if not assistant_message.tool_calls:
            return assistant_message.content

        # Convert the assistant message into a normal dictionary.
        assistant_message_dict = {
            "role": "assistant",
            "content": assistant_message.content or ""
        }

        tool_calls = []

        for tool_call in assistant_message.tool_calls:
            function_data = {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments or "{}"
            }

            tool_calls.append({
                "id": tool_call.id,
                "type": "function",
                "function": function_data
            })

        assistant_message_dict["tool_calls"] = tool_calls
        messages.append(assistant_message_dict)

        # Execute each requested tool.
        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name
            print(f"Agent called tool: {tool_name}")
            if tool_name == "get_active_disruptions":
                result = get_active_disruptions()
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
                continue
            arguments = tool_call.function.arguments or "{}"

            if tool_name == "get_timetable":
                result = get_timetable()

            elif tool_name == "get_active_disruptions":
                result = get_active_disruptions()

            elif tool_name == "get_affected_classes":
                result = get_affected_classes()

            elif tool_name == "get_subject_priority":
                parsed_arguments = json.loads(arguments)
                subject = parsed_arguments["subject"]
                result = get_subject_priority(subject)

            elif tool_name == "generate_recovery_plan":
                result = generate_recovery_plan()

            elif tool_name == "apply_recovery_plan":
                result = apply_recovery_plan()

        return "Agent stopped after reaching the maximum number of tool calls."

if __name__ == "__main__":
    result = ask_agent(
    "Handle the current campus disruption autonomously. "
    "Investigate the active disruption, identify affected classes, "
    "check their priorities, generate the best feasible recovery plan, "
    "and then apply that recovery plan to the timetable. "
    "Do not merely recommend a plan. Execute it."
)
    print("CampusFlow Agent")
    print("----------------")
    print(result)