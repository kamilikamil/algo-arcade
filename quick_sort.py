"""ALGO ARCADE, level 5: quick sort.

The rule: pick one value, the pivot (here: the last one in the range). Walk the range and move every
value smaller than the pivot to the left side. Then put the pivot right after them: it is now exactly
where it belongs and never moves again. Do the same to the part left of it and the part right of it.

Its weak spot: with the last value as pivot, a row that is already sorted makes every split lopsided,
and quick sort slows down to bubble sort speed. Real libraries pick the pivot more cleverly.

Play it in your terminal:   python3 quick_sort.py
Your own numbers:           python3 quick_sort.py 5 3 8 1
Slower or faster:           python3 quick_sort.py --speed 0.5
"""
from arcade import Level, play


def quick_sort(row, lo=0, hi=None):
    if hi is None:
        hi = len(row) - 1
    if lo >= hi:
        return row
    pivot = row[hi]
    p = lo
    for i in range(lo, hi):
        if row[i] < pivot:
            row[i], row[p] = row[p], row[i]
            p += 1
    row[hi], row[p] = row[p], row[hi]
    quick_sort(row, lo, p - 1)
    quick_sort(row, p + 1, hi)
    return row


LEVEL = Level(
    func=quick_sort,
    number=5,
    title="QUICK SORT",
    demo=[8, 2, 5, 1, 3, 7, 4, 6],
    # the value being checked (i) and the pivot (hi)
    highlight=lambda v: [v["i"], v["hi"]] if "i" in v and "hi" in v else [],
    # a pivot is final once placed, but that is known across calls, not from one call's variables
    locked=lambda v, n: [],
    counters={
        "compares": lambda line: line.startswith("if row[i] < pivot"),
        "swaps": lambda line: line.startswith(("row[i], row[p] =", "row[hi], row[p] =")),
    },
    # how the work grows with n: n log n on shuffled rows, n squared on an already sorted row (its weak spot);
    # extra memory is the stack of unfinished calls, about log n
    time="O(n log n)",
    best="O(n log n)",
    memory="O(log n)",
    extra_memory="tiny",
)

if __name__ == "__main__":
    play(LEVEL)
