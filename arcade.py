"""ALGO ARCADE engine: runs an algorithm, records every line it executes, and plays it back in your terminal.

You do not need to read this file to learn the algorithms. Each level file (bubble_sort.py, ...) holds the
algorithm itself plus a LEVEL that says what to light up; this file only watches the function run
(sys.settrace) and draws it.

    python3 arcade.py              list every level in this folder
    python3 bubble_sort.py         play one level
    python3 bubble_sort.py 5 3 8   play it with your own numbers
    python3 bubble_sort.py --speed 0.5

Python 3.8+, standard library only.
"""
import importlib
import inspect
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List


@dataclass
class Level:
    """Everything the arcade needs to play one algorithm.

    func       the algorithm. It takes one list and works on it (in place or not) and returns the result.
    number     level number, title  the name on screen, demo  the default input.
    highlight  vars -> list of indexes being looked at right now (lit white).
    locked     (vars, n) -> list of indexes already in their final place (lit green).
    counters   name -> test on a stripped source line; the counter goes up each time such a line runs.
    view       how the data is drawn: "towers" (a list of numbers). Graph and grid levels add their own view.
    """
    func: Callable
    number: int
    title: str
    demo: List[int]
    highlight: Callable[[dict], List[int]] = lambda v: []
    locked: Callable[[dict, int], List[int]] = lambda v, n: []
    counters: Dict[str, Callable[[str], bool]] = field(default_factory=dict)
    view: str = "towers"


def record(func, data):
    """Run func on a copy of data. Return one step per executed line of func:
    {"line": line number inside func (0 = the def line), "row": the list at that moment,
     "vars": the function's numbers and flags at that moment, "event": "line" or "return"}.
    """
    row = list(data)
    code = func.__code__
    steps = []

    def watch(frame, event, arg):
        if frame.f_code is not code:
            return None
        if event in ("line", "return"):
            loc = frame.f_locals
            steps.append({
                "line": frame.f_lineno - code.co_firstlineno,
                "row": list(row),
                "vars": {k: v for k, v in loc.items() if isinstance(v, (int, bool))},
                "event": event,
            })
        return watch

    sys.settrace(watch)
    try:
        result = func(row)
    finally:
        sys.settrace(None)
    return steps, result


def source_lines(func):
    return inspect.getsource(func).rstrip("\n").split("\n")


def counts(level, steps):
    """Running totals per counter, one dict per step (a line counts when it runs)."""
    lines = source_lines(level.func)
    total = {name: 0 for name in level.counters}
    out = []
    for s in steps:
        text = lines[s["line"]].strip()
        if s["event"] == "line":
            for name, test in level.counters.items():
                if test(text):
                    total[name] += 1
        out.append(dict(total))
    return out


COLORS = {"tower": "\033[36m", "hot": "\033[97m", "locked": "\033[32m", "code": "\033[33m", "off": "\033[0m"}


def draw_towers(level, lines, step, totals, hot, done):
    row = step["row"]
    tallest = max(row)
    width = max(len(str(v)) for v in row) + 2
    out = []
    for height in range(tallest, 0, -1):
        cells = []
        for i, value in enumerate(row):
            color = COLORS["hot"] if i in hot else COLORS["locked"] if i in done else COLORS["tower"]
            cells.append(color + ("█" * width if value >= height else " " * width) + COLORS["off"])
        out.append("  " + " ".join(cells))
    out.append("  " + " ".join(f"{v:^{width}}" for v in row))
    return out


VIEWS = {"towers": draw_towers}


def frame(level, lines, step, totals, hot, done):
    score = "   ".join(f"{name.upper()} {n:03d}" for name, n in totals.items())
    out = ["\033[H\033[2J", f"  ALGO ARCADE  LEVEL {level.number}  {level.title}   {score}", ""]
    out += VIEWS[level.view](level, lines, step, totals, hot, done)
    out.append("")
    for n, text in enumerate(lines):
        mark = COLORS["code"] + " >" if n == step["line"] else "  "
        out.append(f"{mark} {text}{COLORS['off']}")
    print("\n".join(out), flush=True)


def play(level, args=None):
    args = list(sys.argv[1:] if args is None else args)
    speed = 1.0
    if "--speed" in args:
        k = args.index("--speed")
        speed = float(args[k + 1])
        del args[k:k + 2]
    data = [int(x) for x in args] or level.demo
    steps, result = record(level.func, data)
    lines = source_lines(level.func)
    totals = counts(level, steps)
    for s, t in zip(steps, totals):
        frame(level, lines, s, t, set(level.highlight(s["vars"])), set(level.locked(s["vars"], len(data))))
        time.sleep(0.25 / speed)
    last = dict(steps[-1], row=list(result))
    frame(level, lines, last, totals[-1], set(), set(range(len(data))))
    score = ", ".join(f"{n} {name}" for name, n in totals[-1].items())
    print(f"\n  STAGE CLEAR   {data} -> {list(result)}   {score}\n")


def levels():
    """Every LEVEL in the .py files next to this one, by level number."""
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    found = []
    for path in sorted(here.glob("*.py")):
        if path.stem in ("arcade",) or path.stem.startswith("test_"):
            continue
        level = getattr(importlib.import_module(path.stem), "LEVEL", None)
        # duck-typed: when arcade.py runs as a script, level files import a second copy of this module
        if level is not None and type(level).__name__ == "Level":
            found.append((level.number, path.name, level))
    return sorted(found, key=lambda x: x[0])


if __name__ == "__main__":
    print("\n  ALGO ARCADE levels:\n")
    for number, name, level in levels():
        print(f"  {number:>2}  {level.title:<20} python3 {name}")
    print()
