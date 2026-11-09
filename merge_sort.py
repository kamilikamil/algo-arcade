"""ALGO ARCADE, level 4: merge sort.

The rule: two squads that are each sorted are easy to merge: look only at the front of each squad and
take the smaller one, again and again. So start with squads of 1 (always sorted), merge them into squads
of 2, then 4, then 8, until one squad holds the whole row.

To merge, both squads are copied out to a second row first (left and right). That copy is the extra
memory merge sort needs. The inf at the end of each copy is a stopper: nothing is bigger, so once a
squad runs out, the other one wins every remaining compare.

Play it in your terminal:   python3 merge_sort.py
Your own numbers:           python3 merge_sort.py 5 3 8 1
Slower or faster:           python3 merge_sort.py --speed 0.5
"""
from math import inf

from arcade import Level, play


def merge_sort(row):
    size = 1
    while size < len(row):
        for lo in range(0, len(row), 2 * size):
            mid = min(lo + size, len(row))
            hi = min(lo + 2 * size, len(row))
            left = row[lo:mid] + [inf]
            right = row[mid:hi] + [inf]
            i = j = 0
            for k in range(lo, hi):
                if left[i] <= right[j]:
                    row[k] = left[i]
                    i += 1
                else:
                    row[k] = right[j]
                    j += 1
        size *= 2
    return row


LEVEL = Level(
    func=merge_sort,
    number=4,
    title="MERGE SORT",
    demo=[8, 2, 5, 1, 3, 7, 4, 6],
    # the spot being written in the row
    highlight=lambda v: [v["k"]] if "k" in v else [],
    # nothing is final until the last merge
    locked=lambda v, n: [],
    counters={
        "compares": lambda line: line.startswith("if left[i] <= right[j]"),
        "writes": lambda line: line.startswith("row[k] ="),
    },
    lists=("left", "right"),
    time="O(n log n)",
    best="O(n log n)",
    memory="O(n)",
    extra_memory="+1 row",
)

if __name__ == "__main__":
    play(LEVEL)
