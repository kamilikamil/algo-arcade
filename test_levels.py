"""Every level must give the same answer as Python's sorted(), and the arcade must be able to record it.

    python3 -m unittest -v
"""
import random
import unittest

from arcade import counts, levels, record


def sorting_levels():
    return [x for x in levels() if x[2].find is None]


def search_levels():
    return [x for x in levels() if x[2].find is not None]


class TestLevels(unittest.TestCase):
    def test_every_level_sorts(self):
        rng = random.Random(7)
        cases = [[], [1], [2, 1], [3, 3, 1], list(range(10)), list(range(10, 0, -1))]
        cases += [[rng.randint(-50, 50) for _ in range(rng.randint(0, 30))] for _ in range(200)]
        for number, name, level in sorting_levels():
            for data in cases + [level.demo]:
                with self.subTest(level=name, data=data):
                    self.assertEqual(list(level.func(list(data))), sorted(data))

    def test_every_level_records_and_counts(self):
        for number, name, level in levels():
            with self.subTest(level=name):
                args = () if level.find is None else (level.find,)
                steps, result = record(level.func, level.demo, level.lists, args)
                if level.find is None:
                    self.assertEqual(list(result), sorted(level.demo))
                else:
                    self.assertEqual(level.demo[result], level.find)
                self.assertTrue(steps)
                self.assertEqual(set(counts(level, steps)[-1]), set(level.counters))

    def test_growth_matches_the_level_labels(self):
        # 4 times more shuffled items: an O(n²) level does about 16 times the compares, an O(n log n) level about 5,
        # and a level labelled best O(n) does n - 1 compares on sorted input
        for number, name, level in sorting_levels():
            with self.subTest(level=name):
                work = lambda data: counts(level, record(level.func, data)[0])[-1]["compares"]
                shuffled = lambda n: random.Random(n).sample(range(n), n)
                ratio = work(shuffled(400)) / work(shuffled(100))
                if level.time == "O(n²)":
                    self.assertTrue(14 < ratio < 18, ratio)
                if level.time == "O(n log n)":
                    self.assertTrue(4 < ratio < 6, ratio)
                if level.best == "O(n)":
                    self.assertEqual(work(list(range(100))), 99)

    def test_search_levels_find_or_say_missing(self):
        rng = random.Random(11)
        for number, name, level in search_levels():
            for _ in range(300):
                row = sorted(rng.sample(range(200), rng.randint(0, 40)))
                for target in rng.sample(range(-5, 205), 10) + row[:3] + row[-3:]:
                    with self.subTest(level=name, row=row, target=target):
                        got = level.func(list(row), target)
                        self.assertEqual(got, row.index(target) if target in row else -1)

    def test_search_checks_grow_with_log_n(self):
        # a million sorted numbers: never more than 20 checks (2 to the 20th is just over a million)
        for number, name, level in search_levels():
            row = list(range(1_000_000))
            for target in (0, 1, 499_999, 999_999, -1, 1_000_000, 123_456):
                with self.subTest(level=name, target=target):
                    steps, _ = record(level.func, row, (), (target,))
                    self.assertLessEqual(counts(level, steps)[-1]["checks"], 20)

    def test_bubble_sort_demo_numbers(self):
        # the numbers shown at the end of the level 1 reel
        level = dict((n, lv) for n, _, lv in levels())[1]
        steps, _ = record(level.func, level.demo)
        self.assertEqual(counts(level, steps)[-1], {"compares": 22, "swaps": 13})


if __name__ == "__main__":
    unittest.main()
