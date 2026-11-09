"""ALGO ARCADE, level 3: insertion sort.

The rule: the left part of the row is always sorted. Take the next value (i) and let it step left,
swapping with its left neighbour, until the neighbour is not bigger. Then it fits, and the sorted part
is one longer. An already sorted row costs almost nothing: every new value fits at once.

Play it in your terminal:   python3 insertion_sort.py
Your own numbers:           python3 insertion_sort.py 5 3 8 1
Slower or faster:           python3 insertion_sort.py --speed 0.5
"""
from arcade import Level, play


def insertion_sort(row):
    for i in range(1, len(row)):
        j = i
        while j > 0:
            if row[j - 1] <= row[j]:
                break
            row[j - 1], row[j] = row[j], row[j - 1]
            j -= 1
    return row


LEVEL = Level(
    func=insertion_sort,
    number=3,
    title="INSERTION SORT",
    demo=[8, 2, 5, 1, 3, 7, 4, 6],
    # the value being inserted (j) and its left neighbour
    highlight=lambda v: [v["j"] - 1, v["j"]] if v.get("j", 0) > 0 else [],
    # nothing is final until the end: a later value can still step in front of any of them
    locked=lambda v, n: [],
    # how the work grows with n: compares grow with n squared; already sorted input costs n; sorts in place
    time="O(n²)",
    best="O(n)",
    memory="O(1)",
    counters={
        "compares": lambda line: line.startswith("if row[j - 1] <= row[j]"),
        "swaps": lambda line: line.startswith("row[j - 1], row[j] ="),
    },
)

if __name__ == "__main__":
    play(LEVEL)
