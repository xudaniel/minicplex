# 旅行行程 agent 的测试，中英文各一套：python3 -m unittest -v test_itinerary_agent
# Tests for the itinerary agent in Chinese and English. Needs OR-Tools; skipped otherwise.
import unittest

try:
    import itinerary_agent as A
except ImportError:
    A = None


def q(text, **kw):
    return A.run(text, quiet=True, **kw)


@unittest.skipIf(A is None, "需要 pip install ortools")
class Chinese(unittest.TestCase):
    def setUp(self): A.LANG = "zh"

    def test_base(self):
        r = A.solve(A.BASE)
        self.assertEqual(r["score"], 60)
        self.assertIn((14 * 60, "天守阁"), r["plan"][2])          # 票上的时间 / the ticketed slot

    def test_sleep_in(self):                                       # 主角：没少玩，但行程重排
        log = q("第三天想睡懒觉，十点前别安排")
        self.assertEqual(log["guard"], "ok")
        self.assertEqual(log["result"]["score"], 60)
        self.assertTrue(all(a >= 10 * 60 for a, _ in log["result"]["plan"][3]))
        self.assertEqual(log["approver"], "自己定就行")

    def test_back_early(self):
        log = q("第二天下午五点前要回酒店")
        self.assertEqual(log["result"]["score"], 53)
        self.assertEqual(log["approver"], "同行的人一起商量")

    def test_guard(self):
        self.assertEqual(q("环球影城一定要去")["guard"], "ask")
        self.assertEqual(q("第五天十点前别安排")["guard"], "reject")
        self.assertEqual(q("美术馆一定要去，美术馆不去了")["guard"], "ask")
        self.assertEqual(q("天守阁不去了")["guard"], "confirm")

    def test_ticket_refund(self):
        log = q("天守阁不去了", confirmed=True)
        self.assertEqual(log["result"]["score"], 56)
        self.assertEqual(log["approver"], "出钱的人批（要退改门票）")

    def test_lunch_rule(self):                                     # 😈 拿掉午饭：多玩 6 分，但老师傅亮灯
        log = q("第三天想睡懒觉，十点前别安排", override={"lunch_rule": False})
        self.assertEqual(log["result"]["score"], 66)
        self.assertTrue(any("午" in f for f in log["flags"]))

    def test_zone_rule(self):                                      # 😈 拿掉「每天最多两个区」
        self.assertEqual(q("动物园一定要去")["result"]["score"], 58)
        log = q("动物园一定要去", override={"zone_rule": False})
        self.assertEqual(log["result"]["score"], 59)
        self.assertTrue(any("3 个区" in f for f in log["flags"]))

    def test_every_stop_is_valid(self):                            # 每一站都在开门时间内、间隔够 30 分钟
        r = q("第三天想睡懒觉，十点前别安排")["result"]
        days = A.apply(A.parse("第三天想睡懒觉，十点前别安排"))["days"]
        for d, items in r["plan"].items():
            for i, (a, s) in enumerate(items):
                _, _, _, dur, op, cl = A.SIGHTS[s]
                self.assertTrue(max(op, days[d][0]) <= a and a + dur <= min(cl, days[d][1]))
                if i: self.assertGreaterEqual(a - items[i - 1][0] - A.SIGHTS[items[i - 1][1]][3], A.TRAVEL)


@unittest.skipIf(A is None, "需要 pip install ortools")
class English(unittest.TestCase):
    def setUp(self): A.LANG = "en"
    def tearDown(self): A.LANG = "zh"

    def test_same_numbers(self):
        S = A.SENT["en"]
        self.assertEqual(q(S["main"])["result"]["score"], 60)
        self.assertEqual(q(S["back"])["result"]["score"], 53)
        self.assertEqual(q(S["unknown"])["guard"], "ask")
        self.assertEqual(q(S["day9"])["guard"], "reject")
        self.assertEqual(q(S["both"])["guard"], "ask")
        self.assertEqual(q(S["ticket"])["guard"], "confirm")
        log = q(S["ticket"], confirmed=True)
        self.assertEqual(log["result"]["score"], 56)
        self.assertEqual(log["approver"], "whoever paid signs (tickets must be changed)")
        self.assertEqual(q(S["zoo"])["result"]["score"], 58)

    def test_english_words(self):
        r = q("I want to sleep in on day three, nothing before ten")["result"]
        line = A.explain(r, A.solve(A.BASE), [], "your call")
        self.assertIn("Seaside Market", line)
        self.assertNotIn("海边", line)


if __name__ == "__main__":
    unittest.main()
