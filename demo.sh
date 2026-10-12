#!/usr/bin/env bash
#
# Paced demo of LLM tool calling for screen recording (~2-3 min).
# Each query makes Claude (via OpenRouter) choose and call the fs_tools.
#
# Usage:
#   ./demo.sh                 # uses a free tool-capable model (no credits)
#   OPENROUTER_MODEL=anthropic/claude-sonnet-4.5 ./demo.sh
#
# Requires: .env with OPENROUTER_API_KEY, and `python generate_samples.py` run.

set -euo pipefail
cd "$(dirname "$0")"

PY=".venv/bin/python"
[ -x "$PY" ] || PY="python"
export OPENROUTER_MODEL="${OPENROUTER_MODEL:-nvidia/nemotron-3-super-120b-a12b:free}"

banner() {
  echo
  echo "=================================================================="
  echo "  $1"
  echo "=================================================================="
  sleep 1
}

run() {
  echo
  echo ">> QUERY: $1"
  echo "------------------------------------------------------------------"
  sleep 1
  "$PY" llm_file_assistant_openrouter.py "$1"
  sleep 2
}

banner "LLM File Assistant — tool calling demo"
echo "Model: $OPENROUTER_MODEL"
echo "The assistant has 4 tools: list_files, read_file, search_in_file, write_file."
echo "Watch the [tool] lines — those are the LLM deciding which tool to call."
sleep 2

banner "1) Sample resumes (TXT, DOCX, PDF)"
ls -1 resumes
sleep 2

banner "2) list_files — show the resumes"
run "List all resume files in the resumes folder with their sizes."

banner "3) list_files + search_in_file — keyword search across formats"
run "Find resumes mentioning Python experience and tell me how many match."

banner "4) read_file + write_file — summarize a PDF to a new file"
run "Read resume_john_doe.pdf in the resumes folder and write a 3-line summary to summaries/john_doe.txt."
echo
echo ">> Generated file (summaries/john_doe.txt):"
echo "------------------------------------------------------------------"
cat summaries/john_doe.txt 2>/dev/null || echo "(not created)"

banner "Done — all four tools were called by the LLM"
