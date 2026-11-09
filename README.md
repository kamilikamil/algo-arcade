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
| 6 | `heap_sort.py` | build a pyramid where every boss is taller than its two guards; the front boss is the tallest: send it to the end, repeat |
| 7 | `binary_search.py` | search, not sort: in a sorted row, check the middle; too small means the whole left half is out; repeat (`python3 binary_search.py 21`) |
| 8 | `bfs.py` | map: explore like a ripple with a queue; the first path found has the fewest steps |
| 9 | `dfs.py` | map: the same with a stack; runs as deep as it can; finds a way, not the best way |
| 10 | `dijkstra.py` | map: steps have a price (mud costs 5); always explore the cheapest room so far; cheapest path |
| 11 | `a_star.py` | map: Dijkstra plus a guess of the distance left; same cheapest path, far fewer rooms explored |

Every sorting level starts from the same row, `[8, 2, 5, 1, 3, 7, 4, 6]`, so you can compare the scores:

| level | compares | swaps | time | best case | extra memory |
|---|---|---|---|---|---|
| bubble sort | 22 | 13 | O(n²) | O(n), already sorted | O(1) |
| selection sort | 28 | 5 | O(n²) | O(n²), always | O(1) |
| insertion sort | 18 | 13 | O(n²) | O(n), already sorted | O(1) |
| merge sort | 24 | 24 writes | O(n log n) | O(n log n) | O(n) |
| quick sort | 15 | 15 | O(n log n), O(n²) on a sorted row | O(n log n) | O(log n) |
| heap sort | 24 | 17 | O(n log n), on every row | O(n log n) | O(1) |

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
Heap sort (0.025 s) is a little slower than both, but it has neither cost: no extra row, and no weak spot. Every row,
sorted or not, takes about the same work.

Level 7, binary search, finds a value in a sorted row: 63 in the 16-number demo row takes 4 checks (one by one: 13),
and a million sorted numbers take at most 20 checks (`test_levels.py` checks that).

Levels 8 to 11 walk the same dungeon map (in `bfs.py`: `#` wall, `~` mud, `S` start, `T` treasure):

| level | rooms explored | path steps | path cost |
|---|---|---|---|
| BFS | 62 | 12 | 32 (straight through the mud) |
| DFS | 21 | 20 | 20 |
| Dijkstra | 68 | 14 | 14 (around the mud) |
| A* | 28 | 14 | 14 |

`test_levels.py` checks every map level on 300 random dungeons: BFS always finds the fewest steps, Dijkstra and A*
always the cheapest path.

More levels are on the way.

## World 2: how AI and dev systems work

The `world2/` folder holds a second world: not sorting or searching, but the systems you use every day (the context
window of a chat model, an AI agent's tool calls, rate limits), each played as a dungeon level. Same rule as World 1:
one small Python file per level, standard library only, runs offline, and the file prints the same numbers the level
shows. See [world2/README.md](world2/README.md).

```sh
cd world2
python3 context_window.py           # level 2-1: why your AI "forgets"
python3 agent_loop.py               # level 2-2: how an AI agent touches your files
python3 token_bucket.py             # level 2-3: why your API says 429
```

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
