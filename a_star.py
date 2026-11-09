"""ALGO ARCADE, level 11: A* (A star).

Dijkstra (level 10) with a sense of direction. It still adds up what each step costs, but it sorts the heap
by cost so far PLUS a guess of what is left: the distance to the treasure if there were no walls and no mud.
That guess never says more than the real cost, so A* still finds the cheapest path, but it stops wasting
time on rooms that lead away from the treasure.

Same path as Dijkstra here, with far fewer rooms explored. Games use it to move characters around maps.

Play it in your terminal:   python3 a_star.py
Slower or faster:           python3 a_star.py --speed 0.5
"""
from heapq import heappop, heappush

from arcade import Level, find, neighbours, path_back, play, step_cost
from bfs import DUNGEON


def distance(room, goal):
    return abs(room[0] - goal[0]) + abs(room[1] - goal[1])


def a_star(grid):
    start, goal = find(grid, "S"), find(grid, "T")
    came_from = {start: None}
    cost = {start: 0}
    heap = [(distance(start, goal), 0, start)]
    while heap:
        guess, spent, room = heappop(heap)
        if spent > cost[room]:
            continue
        if room == goal:
            break
        for step in neighbours(grid, room):
            new = spent + step_cost(grid, step)
            if step not in cost or new < cost[step]:
                cost[step] = new
                came_from[step] = room
                guess = new + distance(step, goal)
                heappush(heap, (guess, new, step))
    return path_back(came_from, goal)


LEVEL = Level(
    func=a_star,
    number=11,
    title="A STAR",
    demo=DUNGEON,
    view="map",
    lists=("came_from", "cost", "heap"),
    counters={"rooms": lambda line: line.startswith("if room == goal")},
    time="O((V + E) log V)",
    best="O(1)",
    memory="O(V + E)",
    extra_memory="1 note per room",
)

if __name__ == "__main__":
    play(LEVEL)
