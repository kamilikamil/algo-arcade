"""ALGO ARCADE World 2-2: THE NOTE SLOT (how an AI agent touches your files).

The model never touches your files. It sits in a sealed room with one mail slot: it can only write a note
asking for a tool ("read_file", "run_tests", ...). YOUR code reads the note, decides if it is allowed, runs it,
and slides the result back. Then the model writes the next note. That loop is the whole agent.

Run it (Python 3.8 or newer, nothing to install, works offline, no API key):

    python3 agent_loop.py           # play the level: fix a failing test in a throwaway folder
    python3 agent_loop.py --json    # the level as JSON (the reel is drawn from this)

Everything happens in a new temporary folder with a tiny app.py and test_app.py; your own files are never used.
The "model" here is a script that plays the part, so the loop runs offline. To use a real model, replace
scripted_model() with one API call that sends the messages and the tool list and returns the model's tool call
(Anthropic: a "tool_use" block; OpenAI: a "function_call"). The loop around it stays the same.

Where the game picture stops: some providers also run certain tools on their own servers (for example a hosted
web search). The note slot is about the tools your app runs: your files, your shell, your database.
"""
import json
import os
import subprocess
import sys
import tempfile

APP = "def add(a, b):\n    return a - b\n"
TEST = ("import unittest\nfrom app import add\n\n\nclass TestAdd(unittest.TestCase):\n"
        "    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n")


# ---- the tools: plain functions that YOUR app runs --------------------------------------------------------------
def read_file(folder, path):
    with open(os.path.join(folder, path)) as f:
        return f.read()


def run_tests(folder):
    # -B: write no .pyc, so a quick edit is never hidden by a stale cached copy of app.py
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "-q"], cwd=folder, capture_output=True, text=True)
    out = r.stdout + r.stderr
    if r.returncode == 0:
        return "PASSED"
    failed = out.count("FAIL:") + out.count("ERROR:")
    return f"{failed} FAILED"


def edit_file(folder, path, old, new):
    full = os.path.join(folder, path)
    with open(full) as f:
        text = f.read()
    if old not in text:
        return "edit failed: text not found"
    with open(full, "w") as f:
        f.write(text.replace(old, new, 1))
    return "edited " + path


def delete_file(folder, path):
    os.remove(os.path.join(folder, path))
    return "deleted " + path


TOOLS = {"read_file": read_file, "run_tests": run_tests, "edit_file": edit_file, "delete_file": delete_file}
ALLOWED = {"read_file", "run_tests", "edit_file"}        # the allow list: delete_file is not on it


# ---- the model: a script that plays the part (a real API call goes here) ----------------------------------------
def scripted_model(messages):
    """Returns the next note: {"tool": name, "args": {...}} or {"done": text}. Reads only what came back."""
    results = [m["content"] for m in messages if m["role"] == "tool"]
    if not results:
        return {"tool": "read_file", "args": {"path": "test_app.py"}}
    last = results[-1]
    if last.startswith("import unittest"):
        return {"tool": "run_tests", "args": {}}
    if last.endswith("FAILED"):
        return {"tool": "edit_file", "args": {"path": "app.py", "old": "a - b", "new": "a + b"}}
    if last.startswith("edited"):
        return {"tool": "run_tests", "args": {}}
    if last == "PASSED":
        return {"tool": "delete_file", "args": {"path": "prod.db"}}     # an overeager "clean up" note
    return {"done": "The test passes now: add() used a minus sign."}


# ---- the loop ----------------------------------------------------------------------------------------------------
def agent(task, folder, model=scripted_model, max_turns=10):
    messages = [{"role": "user", "content": task}]
    log = []
    for turn in range(1, max_turns + 1):
        note = model(messages)                                   # 1. the model writes a note
        if "done" in note:
            log.append({"turn": turn, "event": "done", "text": note["done"]})
            break
        call = f'{note["tool"]}({", ".join(json.dumps(v) for v in note["args"].values())})'
        if note["tool"] not in ALLOWED:                          # 2. your app checks the allow list
            result = "DENIED: not on the allow list"
            log.append({"turn": turn, "event": "denied", "call": call, "tool": note["tool"], "result": result})
        else:                                                    # 3. your app runs it
            result = TOOLS[note["tool"]](folder, **note["args"])
            log.append({"turn": turn, "event": "ran", "call": call, "tool": note["tool"], "result": result})
        messages.append({"role": "assistant", "content": call})
        messages.append({"role": "tool", "content": result})     # 4. the result goes back through the slot
    return log


def level():
    with tempfile.TemporaryDirectory() as folder:
        for name, text in (("app.py", APP), ("test_app.py", TEST), ("prod.db", "pretend this is your database\n")):
            with open(os.path.join(folder, name), "w") as f:
                f.write(text)
        log = agent("Fix the failing test.", folder)
        still_there = os.path.exists(os.path.join(folder, "prod.db"))
    calls = [e for e in log if e["event"] in ("ran", "denied")]
    return {"task": "Fix the failing test.", "allowed": sorted(ALLOWED), "log": log,
            "totals": {"turns": len(log), "tool_calls": len(calls), "ran": sum(e["event"] == "ran" for e in log),
                       "denied": sum(e["event"] == "denied" for e in log), "prod_db_safe": still_there}}


def play():
    data = level()
    print("QUEST:", data["task"], "  allow list:", ", ".join(data["allowed"]))
    for e in data["log"]:
        if e["event"] == "done":
            print(f'turn {e["turn"]}  DONE   {e["text"]}')
            continue
        lines = e["result"].strip().splitlines()
        more = " ..." if len(lines) > 1 else ""
        print(f'turn {e["turn"]}  NOTE   {e["call"]}')
        print(f'        {"STOP  " if e["event"] == "denied" else "BACK  "} {lines[0]}{more}')
    t = data["totals"]
    print(f'\n{t["turns"]} turns, {t["tool_calls"]} tool calls, {t["ran"]} ran, {t["denied"]} denied; prod.db still there: {t["prod_db_safe"]}')


if __name__ == "__main__":
    if "--json" in sys.argv:
        print(json.dumps(level(), indent=1))
    else:
        play()
