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

Every sorting level starts from the same row, `[8, 2, 5, 1, 3, 7, 4, 6]`, so you can compare the scores:

| level | compares | swaps |
|---|---|---|
| bubble sort | 22 | 13 |
| selection sort | 28 | 5 |

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
    counters={"compares": lambda line: line.startswith("if row[j] < row[smallest]")},
)

if __name__ == "__main__":
    play(LEVEL)
```

`python3 arcade.py` finds it, and `test_levels.py` checks it against `sorted()` on hundreds of inputs.
Levels that are not about a list of numbers (search on a grid, graph traversal) add their own drawing to
`VIEWS` in `arcade.py` and set `view=` on their `Level`.

## License

MIT, see `LICENSE`.
