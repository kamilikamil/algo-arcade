"""Checks for the World 2 levels: python3 -m unittest -v (inside world2/)."""
import unittest

import agent_loop as al
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


class AgentLoop(unittest.TestCase):
    def test_level(self):
        d = al.level()
        self.assertEqual([e["event"] for e in d["log"]], ["ran", "ran", "ran", "ran", "denied", "done"])
        self.assertEqual([e["result"] for e in d["log"] if e.get("tool") == "run_tests"], ["1 FAILED", "PASSED"])
        self.assertTrue(d["totals"]["prod_db_safe"])

    def test_denied_tool_never_runs(self):
        self.assertNotIn("delete_file", al.ALLOWED)


if __name__ == "__main__":
    unittest.main()
