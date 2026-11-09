"""ALGO ARCADE, level 9: depth first search (DFS).

Almost the same code as BFS (level 8), but the waiting line is a stack: the next room comes from the BACK of
the line (stack.pop()) instead of the front. So the hero always explores the room it found last: it runs down one
corridor as deep as it goes, and only turns back at a dead end.

DFS can find the treasure after exploring only a few rooms, but the path it finds is just the first one it
tried, not the shortest. Good for "is there any way out?", not for "what is the best way?".

Play it in your terminal:   python3 dfs.py
Slower or faster:           python3 dfs.py --speed 0.5
"""
from arcade import Level, find, neighbours, path_back, play
from bfs import DUNGEON


def dfs(grid):
    start, goal = find(grid, "S"), find(grid, "T")
    came_from = {start: None}
    stack = [start]
    while stack:
        room = stack.pop()
        if room == goal:
            break
        for step in neighbours(grid, room):
            if step not in came_from:
                came_from[step] = room
                stack.append(step)
    return path_back(came_from, goal)


LEVEL = Level(
    func=dfs,
    number=9,
    title="DFS",
    demo=DUNGEON,
    view="map",
    lists=("came_from", "stack"),
    counters={"rooms": lambda line: line.startswith("if room == goal")},
    time="O(V + E)",
    best="O(1)",
    memory="O(V)",
    extra_memory="1 note per room",
)

if __name__ == "__main__":
    play(LEVEL)
