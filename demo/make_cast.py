#!/usr/bin/env python3
"""Build an asciinema v3 cast replaying a real LLM tool-calling run.

The [tool] lines and answers are the genuine output captured on 2026-10-12 from
llm_file_assistant_openrouter.py (OpenRouter, model
nvidia/nemotron-3-super-120b-a12b:free). This generator assigns explicit
timestamps so the cast plays back with clean pacing regardless of terminal/TTY.

    python demo/make_cast.py          # writes demo/demo.cast
"""

import json

COLS, ROWS = 100, 32
events = []       # (time, "o", text)
t = 0.0


def emit(text: str, dt: float = 0.05) -> None:
    """Advance the clock by dt, then output one line (CRLF for the terminal)."""
    global t
    t += dt
    events.append([round(t, 3), "o", text + "\r\n"])


def banner(title: str, dt: float = 1.6) -> None:
    emit("", dt)
    emit("=" * 66, 0.05)
    emit(f"  {title}", 0.05)
    emit("=" * 66, 0.05)


def query(q: str) -> None:
    emit("", 1.0)
    emit(f">> QUERY: {q}", 0.2)
    emit("-" * 66, 0.1)
    emit("(using OpenRouter model: nvidia/nemotron-3-super-120b-a12b:free)", 0.8)


FILES = [
    "resume_aisha_khan.txt", "resume_chen_wei.docx", "resume_david_mueller.txt",
    "resume_emma_wilson.txt", "resume_jane_smith.docx", "resume_john_doe.pdf",
    "resume_liam_oconnor.txt", "resume_maria_garcia.txt", "resume_raj_patel.txt",
    "resume_sofia_rossi.pdf",
]

# ---- intro ----
banner("LLM File Assistant - tool calling demo  (replay)")
emit("The assistant has 4 tools: list_files, read_file, search_in_file, write_file.", 0.3)
emit("Watch the [tool] lines - those are the LLM deciding which tool to call.", 0.3)

# ---- 1) sample data ----
banner("1) Sample resumes (TXT, DOCX, PDF)")
for f in FILES:
    emit(f, 0.12)

# ---- 2) list_files ----
banner("2) list_files - show the resumes")
query("List all resume files in the resumes folder with their sizes.")
emit('[tool] list_files({"directory": "./resumes"})', 1.2)
emit("", 0.8)
emit("[assistant] Here are the resume files in ./resumes with their sizes (bytes):", 0.4)
for line in [
    "",
    "| File                     | Size (bytes) |",
    "|--------------------------|--------------|",
    "| resume_aisha_khan.txt    | 348          |",
    "| resume_chen_wei.docx     | 36,881       |",
    "| resume_david_mueller.txt | 374          |",
    "| resume_emma_wilson.txt   | 371          |",
    "| resume_jane_smith.docx   | 36,877       |",
    "| resume_john_doe.pdf      | 1,467        |",
    "| resume_liam_oconnor.txt  | 367          |",
    "| resume_maria_garcia.txt  | 389          |",
    "| resume_raj_patel.txt     | 394          |",
    "| resume_sofia_rossi.pdf   | 1,446        |",
]:
    emit(line, 0.08)

# ---- 3) search ----
banner("3) list_files + search_in_file - keyword search across formats")
query("Find resumes mentioning Python experience and tell me how many match.")
emit('[tool] list_files({"directory": "./resumes"})', 0.9)
for f in FILES:
    emit(f'[tool] search_in_file({{"filepath": "./resumes/{f}", "keyword": "Python"}})', 0.55)
emit("", 0.8)
for line in [
    '[assistant] I searched all 10 resumes for "Python" (case-insensitive):',
    "",
    "Mention Python:",
    "  1. resume_chen_wei.docx     - 1 match",
    "  2. resume_david_mueller.txt - 1 match",
    "  3. resume_emma_wilson.txt   - 2 matches",
    "  4. resume_jane_smith.docx   - 2 matches",
    "  5. resume_john_doe.pdf      - 2 matches",
    "  6. resume_liam_oconnor.txt  - 1 match",
    "  7. resume_maria_garcia.txt  - 2 matches",
    "",
    "No Python mention:",
    "  - resume_aisha_khan.txt",
    "  - resume_raj_patel.txt",
    "  - resume_sofia_rossi.pdf",
    "",
    "Summary: 7 of 10 resumes mention Python (11 total mentions).",
]:
    emit(line, 0.09)

# ---- 4) read + write ----
banner("4) read_file + write_file - summarize a PDF to a new file")
query("Read resume_john_doe.pdf and write a 3-line summary to summaries/john_doe.txt.")
emit('[tool] read_file({"filepath": "./resumes/resume_john_doe.pdf"})', 1.1)
emit('[tool] write_file({"filepath": "./summaries/john_doe.txt", "content": "..."})', 1.1)
emit('[tool] read_file({"filepath": "./summaries/john_doe.txt"})', 1.1)
emit("", 0.8)
emit("[assistant] Read the PDF, wrote a 3-line summary, and read it back to confirm.", 1.2)
emit("", 0.4)
emit(">> Generated file (summaries/john_doe.txt):", 0.3)
emit("-" * 66, 0.1)
for line in [
    "John Doe is a Senior Backend Engineer with 8 years building distributed systems.",
    "Skilled in Python, Django, PostgreSQL, Redis, AWS, and Docker.",
    "Scaled payments to 10k rps at Acme Corp; built REST APIs in Python/Flask at Beta Inc.",
]:
    emit(line, 0.15)

banner("Done - all four tools were called by the LLM", 2.0)
emit("", 1.5)

header = {
    "version": 3,
    "term": {"cols": COLS, "rows": ROWS},
    "idle_time_limit": 2.0,
    "title": "LLM File Assistant - tool calling (replay)",
}
with open("demo/demo.cast", "w", encoding="utf-8") as out:
    out.write(json.dumps(header) + "\n")
    for ev in events:
        out.write(json.dumps(ev) + "\n")

print(f"wrote demo/demo.cast ({len(events)} events, {events[-1][0]:.1f}s)")
