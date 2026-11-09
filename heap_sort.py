"""ALGO ARCADE, level 6: heap sort.

The rule: line the row up as a pyramid of bosses. The spot `boss` has two guards behind it, at 2 * boss + 1
and 2 * boss + 2, and a boss must be at least as tall as both its guards. Then the tallest of all is the
boss at the front (spot 0).

Step 1 builds the pyramid: from the last boss to the first, a boss that is shorter than its taller guard
trades places with it, and keeps sinking until it fits.
Step 2 empties it: the front boss is the tallest, so it trades places with the last spot of the pyramid.
That spot is final, and the pyramid is one shorter. The new front sinks until it fits. Again and again.

No extra row is needed, and there is no weak spot: every row costs about the same.

Play it in your terminal:   python3 heap_sort.py
Your own numbers:           python3 heap_sort.py 5 3 8 1
Slower or faster:           python3 heap_sort.py --speed 0.5
"""
from arcade import Level, play


def heap_sort(row):
    start, end = len(row) // 2, len(row)
    while end > 1:
        if start > 0:  # step 1: build the pyramid
            start -= 1
        else:  # step 2: the tallest goes to the end
            end -= 1
            row[0], row[end] = row[end], row[0]
        boss = start
        while 2 * boss + 1 < end:
            guard = 2 * boss + 1
            if guard + 1 < end:
                if row[guard + 1] > row[guard]:
                    guard += 1
            if row[boss] >= row[guard]:
                break
            row[boss], row[guard] = row[guard], row[boss]
            boss = guard
    return row


LEVEL = Level(
    func=heap_sort,
    number=6,
    title="HEAP SORT",
    demo=[8, 2, 5, 1, 3, 7, 4, 6],
    # the boss and the guard it is checked against
    highlight=lambda v: [v["boss"], v["guard"]] if "boss" in v and "guard" in v else [],
    # every spot from end on is final
    locked=lambda v, n: list(range(v["end"], n)) if "end" in v else [],
    counters={
        "compares": lambda line: line.startswith(("if row[guard + 1] > row[guard]", "if row[boss] >= row[guard]")),
        "swaps": lambda line: line.startswith(("row[0], row[end] =", "row[boss], row[guard] =")),
    },
    # how the work grows with n: about 2 n log n compares on any row; sorts in place
    time="O(n log n)",
    best="O(n log n)",
    memory="O(1)",
    extra_memory="none",
)

if __name__ == "__main__":
    play(LEVEL)
