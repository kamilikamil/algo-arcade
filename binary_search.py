"""ALGO ARCADE, level 7: binary search.

The corridor is sorted: every enemy is stronger than the one before it. To find one value, do not walk the
corridor one by one. Check the enemy in the middle. Too small? Then everything left of it is too small as
well: that whole half is gone. Too big? The right half is gone. Check the middle of what is left, again and
again. Every check throws away half the corridor, so even a million enemies take only 20 checks.

It only works on a sorted row. That is what the sorting levels were for.

Play it in your terminal:   python3 binary_search.py
Find another number:        python3 binary_search.py 21
Slower or faster:           python3 binary_search.py --speed 0.5
"""
from arcade import Level, play


def binary_search(row, target):
    lo, hi = 0, len(row) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if row[mid] == target:
            return mid
        if row[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


LEVEL = Level(
    func=binary_search,
    number=7,
    title="BINARY SEARCH",
    demo=[3, 8, 12, 17, 21, 26, 30, 35, 41, 47, 52, 58, 63, 69, 74, 80],
    find=63,
    view="corridor",
    # the enemy being checked
    highlight=lambda v: [v["mid"]] if "mid" in v else [],
    # everything outside lo..hi is ruled out
    dark=lambda v, n: [i for i in range(n) if "lo" in v and not v["lo"] <= i <= v["hi"]],
    counters={"checks": lambda line: line.startswith("mid = ")},
    # how the work grows with n: one check halves the corridor, so about log2(n) checks; no extra memory
    time="O(log n)",
    best="O(1)",
    memory="O(1)",
    extra_memory="none",
)

if __name__ == "__main__":
    play(LEVEL)
