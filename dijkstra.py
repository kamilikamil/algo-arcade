"""ALGO ARCADE, level 10: Dijkstra's algorithm.

BFS (level 8) counts steps. Dijkstra counts what the steps cost: a floor room costs 1, mud costs 5. It
always explores the room that is cheapest to reach so far. A heap hands out that cheapest room. cost
remembers the cheapest known way to reach each room; finding a cheaper way replaces it.

So when the treasure comes out of the heap, no cheaper path to it can exist. Here it walks around the mud:
2 more steps, but far less effort.

Play it in your terminal:   python3 dijkstra.py
Slower or faster:           python3 dijkstra.py --speed 0.5
"""
from heapq import heappop, heappush

from arcade import Level, find, neighbours, path_back, play, step_cost
from bfs import DUNGEON


def dijkstra(grid):
    start, goal = find(grid, "S"), find(grid, "T")
    came_from = {start: None}
    cost = {start: 0}
    heap = [(0, start)]
    while heap:
        spent, room = heappop(heap)
        if spent > cost[room]:
            continue
        if room == goal:
            break
        for step in neighbours(grid, room):
            new = spent + step_cost(grid, step)
            if step not in cost or new < cost[step]:
                cost[step] = new
                came_from[step] = room
                heappush(heap, (new, step))
    return path_back(came_from, goal)


LEVEL = Level(
    func=dijkstra,
    number=10,
    title="DIJKSTRA",
    demo=DUNGEON,
    view="map",
    lists=("came_from", "cost", "heap"),
    counters={"rooms": lambda line: line.startswith("if room == goal")},
    # with a heap: (V + E) log V
    time="O((V + E) log V)",
    best="O(1)",
    memory="O(V + E)",
    extra_memory="1 note per room",
)

if __name__ == "__main__":
    play(LEVEL)
