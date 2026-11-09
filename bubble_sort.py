"""ALGO ARCADE, level 1: bubble sort.

The rule: walk the row from left to right and compare each value with its right neighbour.
If the left one is bigger, swap them. After one walk (a "pass") the biggest value has bubbled
to the right end and is locked in place, so the next pass can stop one value earlier.
If a whole pass makes no swap, the row is already sorted and the level ends early.

Play it in your terminal:   python3 bubble_sort.py
Your own numbers:           python3 bubble_sort.py 5 3 8 1
Slower or faster:           python3 bubble_sort.py --speed 0.5
"""
from arcade import Level, play


def bubble_sort(row):
    n = len(row)
    for sorted_count in range(n - 1):
        swapped = False
        for i in range(n - 1 - sorted_count):
            if row[i] > row[i + 1]:
                row[i], row[i + 1] = row[i + 1], row[i]
                swapped = True
        if not swapped:
            break
    return row


LEVEL = Level(
    func=bubble_sort,
    number=1,
    title="BUBBLE SORT",
    demo=[8, 2, 5, 1, 3, 7, 4, 6],
    # the two neighbours being compared right now
    highlight=lambda v: [v["i"], v["i"] + 1] if "i" in v else [],
    # the right end is final: one more value after every finished pass
    locked=lambda v, n: list(range(n - v.get("sorted_count", 0), n)),
    # how the work grows with n: compares grow with n squared; already sorted input costs n; sorts in place
    time="O(n²)",
    best="O(n)",
    memory="O(1)",
    counters={
        "compares": lambda line: line.startswith("if row[i] > row[i + 1]"),
        "swaps": lambda line: line.startswith("row[i], row[i + 1] ="),
    },
)

if __name__ == "__main__":
    play(LEVEL)
