"""ALGO ARCADE, level 2: selection sort.

The rule: look at every value that is not placed yet and remember where the smallest one is (min_i).
Then swap it to the front of the unplaced part. That spot is now final (locked), so the next round
starts one place further right. It always looks at every pair once, but it moves each value at most once.

Play it in your terminal:   python3 selection_sort.py
Your own numbers:           python3 selection_sort.py 5 3 8 1
Slower or faster:           python3 selection_sort.py --speed 0.5
"""
from arcade import Level, play


def selection_sort(row):
    n = len(row)
    for i in range(n - 1):
        min_i = i
        for j in range(i + 1, n):
            if row[j] < row[min_i]:
                min_i = j
        if min_i != i:
            row[i], row[min_i] = row[min_i], row[i]
    return row


LEVEL = Level(
    func=selection_sort,
    number=2,
    title="SELECTION SORT",
    demo=[8, 2, 5, 1, 3, 7, 4, 6],
    # the value being checked (j) and the smallest one found so far (min_i)
    highlight=lambda v: [v["j"], v["min_i"]] if "j" in v and "min_i" in v else [],
    # the left end is final: one more value after every round
    locked=lambda v, n: list(range(0, v.get("i", 0))),
    # how the work grows with n: compares grow with n squared; already sorted input costs the same; sorts in place
    time="O(n²)",
    best="O(n²)",
    memory="O(1)",
    counters={
        "compares": lambda line: line.startswith("if row[j] < row[min_i]"),
        "swaps": lambda line: line.startswith("row[i], row[min_i] ="),
    },
)

if __name__ == "__main__":
    play(LEVEL)
