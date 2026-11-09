"""Every level must give the same answer as Python's sorted(), and the arcade must be able to record it.

    python3 -m unittest -v
"""
import random
import unittest

from arcade import counts, levels, record


class TestLevels(unittest.TestCase):
    def test_every_level_sorts(self):
        rng = random.Random(7)
        cases = [[], [1], [2, 1], [3, 3, 1], list(range(10)), list(range(10, 0, -1))]
        cases += [[rng.randint(-50, 50) for _ in range(rng.randint(0, 30))] for _ in range(200)]
        for number, name, level in levels():
            for data in cases + [level.demo]:
                with self.subTest(level=name, data=data):
                    self.assertEqual(list(level.func(list(data))), sorted(data))

    def test_every_level_records_and_counts(self):
        for number, name, level in levels():
            with self.subTest(level=name):
                steps, result = record(level.func, level.demo)
                self.assertEqual(list(result), sorted(level.demo))
                self.assertTrue(steps)
                self.assertEqual(set(counts(level, steps)[-1]), set(level.counters))

    def test_bubble_sort_demo_numbers(self):
        # the numbers shown at the end of the level 1 reel
        level = dict((n, lv) for n, _, lv in levels())[1]
        steps, _ = record(level.func, level.demo)
        self.assertEqual(counts(level, steps)[-1], {"compares": 22, "swaps": 13})


if __name__ == "__main__":
    unittest.main()
