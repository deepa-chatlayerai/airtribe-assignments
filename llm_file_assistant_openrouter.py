"""LLM file assistant via OpenRouter (OpenAI-compatible API).

Same behavior as llm_file_assistant.py, but talks to OpenRouter using the
OpenAI SDK (OpenRouter serves the OpenAI chat-completions format, not the
Anthropic Messages format). The four tools from fs_tools.py are reused via the
shared dispatch table; the Anthropic-style tool schemas are converted to
OpenAI function-tool schemas at import time.

Setup:
    pip install -r requirements.txt
    echo 'OPENROUTER_API_KEY=sk-or-...' > .env     # (gitignored)
    # optional: OPENROUTER_MODEL=anthropic/claude-sonnet-4.5

Usage:
    python llm_file_assistant_openrouter.py "Find resumes mentioning Python experience"
    python llm_file_assistant_openrouter.py            # interactive REPL
"""

from __future__ import annotations

import json
import os
import sys

from openai import OpenAI

from llm_file_assistant import SYSTEM_PROMPT, TOOLS, _run_tool

BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-sonnet-4.5"
MAX_TOKENS = int(os.environ.get("OPENROUTER_MAX_TOKENS", "1024"))
MAX_ITERATIONS = 25


def _load_env_file(path: str = ".env") -> None:
    """Minimal .env loader (KEY=VALUE per line); no external dependency."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def _to_openai_tools(anthropic_tools: list) -> list:
    """Convert Anthropic tool schemas to OpenAI function-tool schemas."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            },
        }
        for tool in anthropic_tools
    ]


OPENAI_TOOLS = _to_openai_tools(TOOLS)


def run_query(client: OpenAI, model: str, user_query: str, verbose: bool = True) -> str:
    """Run one query through the OpenAI-format tool-calling loop."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    for _ in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=OPENAI_TOOLS,
            tool_choice="auto",
            max_tokens=MAX_TOKENS,
        )
        message = response.choices[0].message

        if verbose and message.content:
            print(f"\n[assistant] {message.content.strip()}")

        if not message.tool_calls:
            return (message.content or "").strip()

        # Echo the assistant turn (with tool_calls) back into the history.
        messages.append(message.model_dump(exclude_none=True))

        for call in message.tool_calls:
            name = call.function.name
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError as exc:
                output, _ = {"error": f"bad tool arguments: {exc}"}, True
            else:
                if verbose:
                    print(f"[tool] {name}({json.dumps(args)})")
                output, _ = _run_tool(name, args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(output, default=str),
                }
            )

    return "[stopped: reached maximum tool-use iterations]"


def main() -> None:
    _load_env_file()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(
            "Missing OPENROUTER_API_KEY. Put it in a .env file "
            "(OPENROUTER_API_KEY=sk-or-...) or export it.",
            file=sys.stderr,
        )
        sys.exit(1)

    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
    client = OpenAI(
        base_url=BASE_URL,
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://github.com/airtribe-assignments",
            "X-Title": "LLM File Assistant",
        },
    )
    print(f"(using OpenRouter model: {model})")

    if len(sys.argv) > 1:
        answer = run_query(client, model, " ".join(sys.argv[1:]))
        print(f"\n=== Final answer ===\n{answer}")
        return

    print("LLM file assistant (OpenRouter). Type a request (or 'quit').")
    while True:
        try:
            query = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if query.lower() in {"quit", "exit", "q"}:
            break
        if not query:
            continue
        answer = run_query(client, model, query)
        print(f"\n=== Final answer ===\n{answer}")


if __name__ == "__main__":
    main()
