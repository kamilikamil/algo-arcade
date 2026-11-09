"""ALGO ARCADE, level 2: selection sort.

The rule: look at every value that is not placed yet and remember the smallest one.
Then swap it to the front of the unplaced part. That spot is now final (locked), so the next round
starts one place further right. It always looks at every pair once, but it moves each value at most once.

Play it in your terminal:   python3 selection_sort.py
Your own numbers:           python3 selection_sort.py 5 3 8 1
Slower or faster:           python3 selection_sort.py --speed 0.5
"""
from arcade import Level, play


def selection_sort(row):
    n = len(row)
    for start in range(n - 1):
        smallest = start
        for j in range(start + 1, n):
            if row[j] < row[smallest]:
                smallest = j
        if smallest != start:
            row[start], row[smallest] = row[smallest], row[start]
    return row


LEVEL = Level(
    func=selection_sort,
    number=2,
    title="SELECTION SORT",
    demo=[8, 2, 5, 1, 3, 7, 4, 6],
    # the value being checked and the smallest one found so far
    highlight=lambda v: [v["j"], v["smallest"]] if "j" in v and "smallest" in v else [],
    # the left end is final: one more value after every round
    locked=lambda v, n: list(range(0, v.get("start", 0))),
    counters={
        "compares": lambda line: line.startswith("if row[j] < row[smallest]"),
        "swaps": lambda line: line.startswith("row[start], row[smallest] ="),
    },
)

if __name__ == "__main__":
    play(LEVEL)
