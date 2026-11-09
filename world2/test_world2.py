"""Checks for the World 2 levels: python3 -m unittest -v (inside world2/)."""
import unittest

import context_window as cw


class ContextWindow(unittest.TestCase):
    def test_estimate(self):
        self.assertEqual(cw.count_tokens("hi"), 1)
        self.assertEqual(cw.count_tokens("my name is sam"), 4)

    def test_plain_bag_drops_the_oldest(self):
        r = cw.level()["rounds"][0]["events"]
        self.assertEqual([e["text"] for e in r if e["event"] == "drop"], ["my name is sam"])
        self.assertEqual(r[-1]["text"], "?")
        self.assertTrue(all(e["used"] <= e["window"] for e in r if e["event"] != "add"))

    def test_three_fixes_keep_the_name(self):
        r = cw.level()["rounds"][1]["events"]
        self.assertFalse([e for e in r if e["event"] == "drop"])
        self.assertEqual(r[-1]["text"], "SAM")
        self.assertLessEqual(r[-1]["used"], r[-1]["window"])

    def test_pinned_never_dropped(self):
        bag = cw.Bag(8, pinned=["my name is sam"])
        for m in ["aaaaaaaa", "bbbbbbbb", "cccc"]:
            bag.add(m)
        self.assertEqual(cw.answer(bag, "?"), "SAM")


if __name__ == "__main__":
    unittest.main()
