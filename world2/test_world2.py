"""Checks for the World 2 levels: python3 -m unittest -v (inside world2/)."""
import unittest

import agent_loop as al
import context_window as cw
import token_bucket as tb


class ContextWindow(unittest.TestCase):
    def test_estimate(self):
        self.assertEqual(cw.count_tokens("hi"), 1)
        self.assertEqual(cw.count_tokens("my name is sam"), 4)

    def test_plain_drops_the_oldest(self):
        r = cw.level()["rounds"][0]["events"]
        self.assertEqual([e["text"] for e in r if e["event"] == "drop"], ["my name is sam"])
        self.assertEqual(r[-1]["text"], "?")
        self.assertTrue(all(e["used"] <= e["window"] for e in r if e["event"] != "add"))

    def test_compact_keeps_the_name(self):
        r = cw.level()["rounds"][1]["events"]
        self.assertFalse([e for e in r if e["event"] == "drop"])
        self.assertEqual([e["event"] for e in r].count("compact"), 1)
        self.assertEqual(r[-1]["text"], "SAM")
        self.assertLessEqual(r[-1]["used"], r[-1]["window"])

    def test_pinned_never_dropped(self):
        win = cw.Window(8, pinned=["my name is sam"])
        for m in ["aaaaaaaa", "bbbbbbbb", "cccc"]:
            win.add(m)
        self.assertEqual(cw.answer(win, "?"), "SAM")


class AgentLoop(unittest.TestCase):
    def test_level(self):
        d = al.level()
        self.assertEqual([e["event"] for e in d["log"]], ["ran", "ran", "ran", "ran", "denied", "done"])
        self.assertEqual([e["result"] for e in d["log"] if e.get("tool") == "run_tests"], ["1 FAILED", "PASSED"])
        self.assertTrue(d["totals"]["prod_db_safe"])

    def test_denied_tool_never_runs(self):
        self.assertNotIn("delete_file", al.ALLOWED)


class TokenBucketLevel(unittest.TestCase):
    def test_level(self):
        t = tb.level()["totals"]
        self.assertEqual((t["sent"], t["through"], t["bounced"], t["burst_through"], t["waited"]), (7, 7, 3, 5, 2.0))

    def test_refill_is_continuous_and_capped(self):
        b = tb.TokenBucket(5, 1.0)
        for _ in range(5):
            self.assertTrue(b.allow(0.0)[0])
        self.assertEqual(b.allow(0.0), (False, 1))
        self.assertTrue(b.allow(1.0)[0])
        b.refill(100.0)
        self.assertEqual(b.coins, 5)

    def test_retry_after(self):
        self.assertEqual(tb.retry_after_seconds("120"), 120)
        self.assertEqual(tb.retry_after_seconds("Wed, 21 Oct 2015 07:28:00 GMT", now=1445412470), 10)
        replies = iter([(429, {"retry-after": "2"}, ""), (200, {}, "ok")])
        waits = []
        self.assertEqual(tb.call_with_retry(lambda: next(replies), sleep=waits.append)[0], 200)
        self.assertEqual(waits, [2])


if __name__ == "__main__":
    unittest.main()
