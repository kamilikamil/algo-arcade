# ALGO ARCADE

Algorithms you can watch, then run. Every level is one Python file with the plain algorithm in it.
Run the file and the same level plays in your terminal: the values as towers, the pair being looked at,
the line of code that is running, and live counters.

```sh
python3 bubble_sort.py              # play level 1
python3 bubble_sort.py 5 3 8 1      # with your own numbers
python3 bubble_sort.py --speed 0.5  # slower
python3 arcade.py                   # list every level
python3 -m unittest -v              # check every level against sorted()
```

Python 3.8 or newer, nothing to install.

## Levels

| level | file | the rule in one line |
|---|---|---|
| 1 | `bubble_sort.py` | compare two neighbours, swap if the left one is bigger; stop when a whole pass makes no swap |
| 2 | `selection_sort.py` | find the smallest unplaced value, swap it to the front; every value moves at most once |
| 3 | `insertion_sort.py` | keep the left part sorted; each new value steps left until its neighbour is not bigger |
| 4 | `merge_sort.py` | merge sorted squads of 1 into 2, 4, 8: take the smaller front each time; needs a second row |
| 5 | `quick_sort.py` | pick a pivot, move everything smaller to its left; the pivot is now final; repeat on both sides |

Every sorting level starts from the same row, `[8, 2, 5, 1, 3, 7, 4, 6]`, so you can compare the scores:

| level | compares | swaps | time | best case | extra memory |
|---|---|---|---|---|---|
| bubble sort | 22 | 13 | O(n²) | O(n), already sorted | O(1) |
| selection sort | 28 | 5 | O(n²) | O(n²), always | O(1) |
| insertion sort | 18 | 13 | O(n²) | O(n), already sorted | O(1) |
| merge sort | 24 | 24 writes | O(n log n) | O(n log n) | O(n) |
| quick sort | 15 | 15 | O(n log n), O(n²) on a sorted row | O(n log n) | O(log n) |

In plain words: all three get slow on big rows. 10 times more numbers takes about 100 times longer, because the work
grows with the square of the row (that is what O(n²) means). None of them needs extra memory: they sort inside the
row itself (O(1)). Race them on your own computer:

```sh
python3 arcade.py --race 10000
```

On our laptop, 10,000 shuffled numbers took: bubble 4.0 s, insertion 3.2 s, selection 1.6 s, merge 0.016 s.
Merge sort is about 250 times faster than bubble sort here, but it needs a second row as big as the first (O(n)
extra memory). Its work grows with n log n: 10 times more numbers is only about 13 times more work.
Quick sort is the fastest here (0.011 s) with almost no extra memory, but it has a weak spot: with the last value as
pivot, an already sorted row is its worst case (100 sorted numbers: 4,950 compares, shuffled: about 700).

More levels are on the way.

## How it works

`arcade.py` runs the algorithm with `sys.settrace` and records every line it executes, with the list and the
loop variables at that moment. Nothing in the algorithm is changed for the show: the function you read is
the function that runs.

## Add a level

Make one new file, for example `selection_sort.py`:

```python
from arcade import Level, play

def selection_sort(row):
    ...                      # the plain algorithm, working on the list it is given
    return row

LEVEL = Level(
    func=selection_sort,
    number=2,
    title="SELECTION SORT",
    demo=[8, 2, 5, 1, 3, 7, 4, 6],
    highlight=lambda v: [...],          # indexes being looked at, read from the loop variables
    locked=lambda v, n: [...],          # indexes already in their final place
    counters={"compares": lambda line: line.startswith("if row[j] < row[min_i]")},
)

if __name__ == "__main__":
    play(LEVEL)
```

`python3 arcade.py` finds it, and `test_levels.py` checks it against `sorted()` on hundreds of inputs.
Levels that are not about a list of numbers (search on a grid, graph traversal) add their own drawing to
`VIEWS` in `arcade.py` and set `view=` on their `Level`.

## License

MIT, see `LICENSE`.
