"""LLM file assistant: lets Claude operate on the local filesystem via tools.

Claude is given four tools (read_file, list_files, write_file, search_in_file)
backed by fs_tools.py. It decides which to call based on a natural-language
request, we execute them locally, feed results back, and loop until Claude has a
final answer.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...        # or `ant auth login`
    python llm_file_assistant.py "Read all resumes in the resumes folder"
    python llm_file_assistant.py               # interactive REPL

Example queries:
    "Read all resumes in the resumes folder"
    "Find resumes mentioning Python experience"
    "Create a summary file for resume_john_doe.pdf"
"""

from __future__ import annotations

import json
import sys

import anthropic

import fs_tools

MODEL = "claude-opus-4-8"
MAX_TOKENS = 4096
MAX_ITERATIONS = 25  # safety cap on the agentic loop

SYSTEM_PROMPT = (
    "You are a file assistant that helps users work with resume files on the "
    "local filesystem. Use the provided tools to read, list, search, and write "
    "files. Resumes live in the ./resumes directory unless the user says "
    "otherwise. When a tool reports an error, read it and adapt rather than "
    "guessing. Be concise in your final answer and summarize what you did."
)

# Tool schemas exposed to Claude. Each maps 1:1 to a function in fs_tools.
TOOLS = [
    {
        "name": "read_file",
        "description": (
            "Read a resume file (PDF, TXT, or DOCX) and return its extracted "
            "text content plus metadata (size, modified time)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to read.",
                }
            },
            "required": ["filepath"],
        },
    },
    {
        "name": "list_files",
        "description": (
            "List files in a directory with metadata (name, size, modified "
            "date). Optionally filter by extension such as '.pdf' or '.txt'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory to list, e.g. './resumes'.",
                },
                "extension": {
                    "type": "string",
                    "description": "Optional extension filter, e.g. '.pdf'.",
                },
            },
            "required": ["directory"],
        },
    },
    {
        "name": "write_file",
        "description": (
            "Write text content to a file, creating parent directories if "
            "needed. Use this to save summaries or extracted data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path of the file to write.",
                },
                "content": {
                    "type": "string",
                    "description": "Text content to write.",
                },
            },
            "required": ["filepath", "content"],
        },
    },
    {
        "name": "search_in_file",
        "description": (
            "Case-insensitive search for a keyword within a file's text "
            "content. Returns matches with surrounding context and line numbers."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to search.",
                },
                "keyword": {
                    "type": "string",
                    "description": "Keyword or phrase to search for.",
                },
            },
            "required": ["filepath", "keyword"],
        },
    },
]

# Dispatch table: tool name -> fs_tools function.
TOOL_DISPATCH = {
    "read_file": fs_tools.read_file,
    "list_files": fs_tools.list_files,
    "write_file": fs_tools.write_file,
    "search_in_file": fs_tools.search_in_file,
}


def _run_tool(name: str, tool_input: dict):
    """Execute a tool by name, returning (result, is_error)."""
    func = TOOL_DISPATCH.get(name)
    if func is None:
        return {"error": f"Unknown tool: {name}"}, True
    try:
        return func(**tool_input), False
    except TypeError as exc:
        # Bad / missing arguments from the model.
        return {"error": f"Invalid arguments for {name}: {exc}"}, True
    except Exception as exc:  # pragma: no cover - defensive
        return {"error": f"{type(exc).__name__}: {exc}"}, True


def run_query(client: anthropic.Anthropic, user_query: str, verbose: bool = True) -> str:
    """Run one user query through the agentic tool-use loop; return final text."""
    messages = [{"role": "user", "content": user_query}]

    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Surface any text the model emitted this turn.
        for block in response.content:
            if block.type == "text" and verbose and block.text.strip():
                print(f"\n[assistant] {block.text.strip()}")

        if response.stop_reason != "tool_use":
            final = "".join(b.text for b in response.content if b.type == "text")
            return final.strip()

        # Append the assistant turn (with its tool_use blocks) verbatim.
        messages.append({"role": "assistant", "content": response.content})

        # Execute every requested tool and collect results into one user turn.
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if verbose:
                print(f"[tool] {block.name}({json.dumps(block.input)})")
            output, is_error = _run_tool(block.name, block.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(output, default=str),
                    "is_error": is_error,
                }
            )
        messages.append({"role": "user", "content": tool_results})

    return "[stopped: reached maximum tool-use iterations]"


def main() -> None:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY or an ant profile

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        answer = run_query(client, query)
        print(f"\n=== Final answer ===\n{answer}")
        return

    print("LLM file assistant. Type a request (or 'quit' to exit).")
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
        answer = run_query(client, query)
        print(f"\n=== Final answer ===\n{answer}")


if __name__ == "__main__":
    main()
