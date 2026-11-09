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
import random
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass
class Level:
    """Everything the arcade needs to play one algorithm.

    func       the algorithm. It takes one list and works on it (in place or not) and returns the result.
    number     level number, title  the name on screen, demo  the default input.
    highlight  vars -> list of indexes being looked at right now (lit white).
    locked     (vars, n) -> list of indexes already in their final place (lit green).
    counters   name -> test on a stripped source line; the counter goes up each time such a line runs.
    view       how the data is drawn: "towers" (a list of numbers). Graph and grid levels add their own view.
    time, best, memory  how the work grows with n items, for developers (big O): running time, best case, extra memory.
    extra_memory        the same extra memory in plain words, for everyone ("none" or "+1 row").
    lists      names of list variables to record as well (for example the left and right copies of merge sort).
    find       search levels only: the value to look for. The function is then called as func(row, find).
    dark       (vars, n) -> list of indexes already ruled out (drawn dim), for search levels.
    """
    func: Callable
    number: int
    title: str
    demo: List[int]
    highlight: Callable[[dict], List[int]] = lambda v: []
    locked: Callable[[dict, int], List[int]] = lambda v, n: []
    counters: Dict[str, Callable[[str], bool]] = field(default_factory=dict)
    view: str = "towers"
    time: str = ""
    best: str = ""
    memory: str = ""
    extra_memory: str = ""
    lists: tuple = ()
    find: Optional[int] = None
    dark: Callable[[dict, int], List[int]] = lambda v, n: []


def record(func, data, lists=(), args=()):
    """Run func on a copy of data (plus args, for example the value a search looks for). Return one step per executed line of func:
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
                "vars": {k: (list(v) if isinstance(v, list) else v) for k, v in loc.items()
                         if isinstance(v, (int, bool)) or (k in lists and isinstance(v, list))},
                "event": event,
            })
        return watch

    sys.settrace(watch)
    try:
        result = func(row, *args)
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


def draw_corridor(level, lines, step, totals, hot, done):
    """A search level: one line of numbers. Ruled out ones are dim, the one being checked is bright."""
    row, dark = step["row"], set(level.dark(step["vars"], len(step["row"])))
    width = max(len(str(v)) for v in row) + 2
    cells = []
    for i, value in enumerate(row):
        color = COLORS["hot"] if i in hot else COLORS["locked"] if i in done else "\033[90m" if i in dark else COLORS["tower"]
        cells.append(color + f"{value:^{width}}" + COLORS["off"])
    return [f"  FIND {level_find(level, step)}", "", "  " + " ".join(cells)]


def level_find(level, step):
    return step["vars"].get("target", level.find)


VIEWS = {"towers": draw_towers, "corridor": draw_corridor}


def frame(level, lines, step, totals, hot, done):
    score = "   ".join(f"{name.upper()} {n:03d}" for name, n in totals.items())
    grow = f"   TIME {level.time}  BEST {level.best}  MEMORY {level.memory}" if level.time else ""
    out = ["\033[H\033[2J", f"  ALGO ARCADE  LEVEL {level.number}  {level.title}   {score}{grow}", ""]
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
    if level.find is None:
        data, extra = [int(x) for x in args] or level.demo, ()
    else:  # a search level: your number is the value to find, in the level's own sorted row
        data, extra = level.demo, (int(args[0]) if args else level.find,)
    steps, result = record(level.func, data, level.lists, extra)
    lines = source_lines(level.func)
    totals = counts(level, steps)
    for s, t in zip(steps, totals):
        frame(level, lines, s, t, set(level.highlight(s["vars"])), set(level.locked(s["vars"], len(data))))
        time.sleep(0.25 / speed)
    score = ", ".join(f"{n} {name}" for name, n in totals[-1].items())
    if level.find is not None:
        frame(level, lines, steps[-1], totals[-1], set(), {result} if result >= 0 else set())
        found = f"found {extra[0]} at spot {result}" if result >= 0 else f"{extra[0]} is not in the row"
        print(f"\n  STAGE CLEAR   {found}   {score}\n")
        return
    last = dict(steps[-1], row=list(result))
    frame(level, lines, last, totals[-1], set(), set(range(len(data))))
    print(f"\n  STAGE CLEAR   {data} -> {list(result)}   {score}\n")


def race(level, n, runs=3, seed=42):
    """Seconds to sort n shuffled numbers with the plain function (no recording), median of runs. Your computer's
    speed changes the numbers, not the shape: 10 times more items costs about 100 times more for an n squared level."""
    data = random.Random(seed).sample(range(n * 10), n)
    times = []
    for _ in range(runs):
        row = list(data)
        start = time.perf_counter()
        level.func(row)
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def speed_bars(seconds_for_10000):
    """1 to 5 SPEED bars from the time to sort 10,000 numbers: the same scale for every level."""
    for bars, limit in ((5, 0.05), (4, 0.2), (3, 1.0), (2, 3.0)):
        if seconds_for_10000 <= limit:
            return bars
    return 1


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
    if "--race" in sys.argv:
        n = int(sys.argv[sys.argv.index("--race") + 1])
        print(f"\n  RACE: sorting {n:,} shuffled numbers on this computer (median of 3 runs)\n")
        for number, name, level in levels():
            if level.find is not None:  # search levels do not sort
                continue
            seconds = race(level, n)
            print(f"  {number:>2}  {level.title:<20} {seconds:8.3f} s   extra memory: {level.extra_memory}")
        print()
        sys.exit()
    print("\n  ALGO ARCADE levels:\n")
    print(f"  {'':>2}  {'':<20} {'time':<11} {'best':<11} {'memory':<8}")
    for number, name, level in levels():
        print(f"  {number:>2}  {level.title:<20} {level.time:<11} {level.best:<11} {level.memory:<8} python3 {name}")
    print("\n  Race them on your computer: python3 arcade.py --race 10000\n")
