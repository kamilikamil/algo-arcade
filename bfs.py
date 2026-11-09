"""ALGO ARCADE, level 8: breadth first search (BFS).

The hero starts at S and wants the treasure at T. BFS explores the dungeon like a ripple: first every room
one step away, then every room two steps away, and so on. A queue keeps that order: new rooms join at the
back, the next room to explore comes from the front. came_from remembers how each room was reached, so once
T is found, path_back follows it from T back to S.

The first path BFS finds has the fewest steps. But it counts steps, not effort: it walks straight through
the mud, where every step costs 5.

Play it in your terminal:   python3 bfs.py
Slower or faster:           python3 bfs.py --speed 0.5
"""
from collections import deque

from arcade import Level, find, neighbours, path_back, play

DUNGEON = [
    ".............",
    ".###########.",
    ".#.........#.",
    "S...~~~~~...T",
    ".#.........#.",
    ".###########.",
    ".............",
    ".............",
]


def bfs(grid):
    start, goal = find(grid, "S"), find(grid, "T")
    came_from = {start: None}
    queue = deque([start])
    while queue:
        room = queue.popleft()
        if room == goal:
            break
        for step in neighbours(grid, room):
            if step not in came_from:
                came_from[step] = room
                queue.append(step)
    return path_back(came_from, goal)


LEVEL = Level(
    func=bfs,
    number=8,
    title="BFS",
    demo=DUNGEON,
    view="map",
    lists=("came_from", "queue"),
    counters={"rooms": lambda line: line.startswith("if room == goal")},
    # every room and every corridor at most once: rooms + corridors (V + E); the queue and came_from hold up to every room
    time="O(V + E)",
    best="O(1)",
    memory="O(V)",
    extra_memory="1 note per room",
)

if __name__ == "__main__":
    play(LEVEL)
