import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

from tools.csv_tool import analyze_csv
from tools.gmail_tool import send_email, read_emails
from tools.calendar_tool import schedule_event, get_upcoming_events

load_dotenv()

# Map function names to actual python functions
EXECUTABLES = {
    "analyze_csv": analyze_csv,
    "send_email": send_email,
    "read_emails": read_emails,
    "schedule_event": schedule_event,
    "get_upcoming_events": get_upcoming_events,
}

# OpenAI tool definitions (function calling schema)
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_csv",
            "description": "Analyzes CSV data based on a natural language query. Leave csv_content_or_path empty to use the default system sales data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What the user wants to know about the CSV data."},
                    "csv_content_or_path": {"type": "string", "description": "Optional. CSV content or file path. Leave empty to use default sales data."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Sends an email using Gmail integration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address."},
                    "subject": {"type": "string", "description": "Email subject line."},
                    "message": {"type": "string", "description": "Email body text."},
                },
                "required": ["to", "subject", "message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_emails",
            "description": "Reads recent emails from the Gmail inbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Optional search query to filter emails."},
                    "limit": {"type": "integer", "description": "Maximum number of emails to return."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_event",
            "description": "Schedules an event on Google Calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the calendar event."},
                    "date_time": {"type": "string", "description": "Start date and time in ISO format, e.g. '2026-04-17T15:00:00'."},
                    "duration_minutes": {"type": "integer", "description": "Duration in minutes. Defaults to 60."},
                },
                "required": ["title", "date_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_events",
            "description": "Gets upcoming events from Google Calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of events to return."},
                },
                "required": [],
            },
        },
    },
]


def _convert_history(raw_history: list) -> list:
    """Convert our internal history format to OpenAI messages format."""
    messages = []
    for turn in raw_history:
        role = turn.get("role", "user")
        # Map 'model' role to 'assistant' for OpenAI
        if role == "model":
            role = "assistant"

        parts = turn.get("parts", [])
        if not parts:
            continue

        # Handle text messages
        if "text" in parts[0]:
            messages.append({"role": role, "content": parts[0]["text"]})

        # Handle function calls (assistant → tool_calls)
        elif "functionCall" in parts[0]:
            tool_calls = []
            for p in parts:
                if "functionCall" in p:
                    tool_calls.append({
                        "id": f"call_{p['functionCall']['name']}",
                        "type": "function",
                        "function": {
                            "name": p["functionCall"]["name"],
                            "arguments": json.dumps(p["functionCall"]["args"]),
                        },
                    })
            messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})

        # Handle function responses (tool results)
        elif "functionResponse" in parts[0]:
            for p in parts:
                if "functionResponse" in p:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": f"call_{p['functionResponse']['name']}",
                        "content": json.dumps(p["functionResponse"]["response"]),
                    })

    return messages


async def process_message(user_message: str, history: list):
    """
    Main entry point for handling the chat turn.
    Returns a dict with updated history, a standard text response, and an execution log.
    """
    import datetime
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    api_key = os.environ.get("OPENAI_API_KEY", "")
    client = OpenAI(api_key=api_key)

    logs = []
    updated_history = list(history)

    # Append user message
    updated_history.append({
        "role": "user",
        "parts": [{"text": user_message}],
    })

    model_id = "gpt-4o-mini"

    system_message = f"You are a helpful Workflow Automation Agent. The current date and time is {current_time}. You have access to tools for Gmail, Google Calendar, and CSV analysis. Always use the tools when the user asks you to perform actions. If the user mentions 'tomorrow', calculate the correct date. Do not ask for confirmation — just execute the tools."

    max_loops = 5
    loops = 0
    final_text = ""

    while loops < max_loops:
        loops += 1

        # Convert history to OpenAI format
        openai_messages = [{"role": "system", "content": system_message}]
        openai_messages.extend(_convert_history(updated_history))

        # Retry logic
        max_retries = 3
        retry_delay = 2
        response = None

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model_id,
                    messages=openai_messages,
                    tools=TOOL_DEFINITIONS,
                    temperature=0.2,
                )
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logs.append({"step": "API Error", "details": str(e), "status": "error"})
                    final_text = f"Error communicating with the service after {max_retries} attempts."
                    response = None
                    break
                time.sleep(retry_delay)
                retry_delay *= 2

        if not response:
            break

        choice = response.choices[0]
        msg = choice.message

        # If the model returned text
        if msg.content:
            final_text = msg.content

        # If the model made tool calls
        if msg.tool_calls:
            model_parts = []
            if msg.content:
                model_parts.append({"text": msg.content})
            for tc in msg.tool_calls:
                model_parts.append({
                    "functionCall": {
                        "name": tc.function.name,
                        "args": json.loads(tc.function.arguments),
                    }
                })
            updated_history.append({"role": "model", "parts": model_parts})

            # Execute each tool call
            func_response_parts = []
            for tc in msg.tool_calls:
                func_name = tc.function.name
                args = json.loads(tc.function.arguments)

                logs.append({"step": f"Calling Tool: {func_name}", "details": f"Args: {args}", "status": "running"})

                if func_name in EXECUTABLES:
                    try:
                        result = EXECUTABLES[func_name](**args)
                        response_dict = {"result": result}
                        logs.append({"step": f"Tool Result: {func_name}", "details": f"Result: {result}", "status": "success"})
                    except Exception as e:
                        response_dict = {"error": str(e)}
                        logs.append({"step": f"Tool Failed: {func_name}", "details": str(e), "status": "error"})
                else:
                    response_dict = {"error": "Function not found"}

                func_response_parts.append({
                    "functionResponse": {
                        "name": func_name,
                        "response": response_dict,
                    }
                })

            updated_history.append({"role": "user", "parts": func_response_parts})
        else:
            # No tool calls — model is done
            updated_history.append({"role": "model", "parts": [{"text": final_text}]})
            break

    return {
        "response": final_text,
        "history": updated_history,
        "logs": logs,
    }
