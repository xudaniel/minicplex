# 核对补班 agent 的九句话和四道「考考你」：python3 -m unittest -v test_staffing_agent
# 需要 OR-Tools（pip install ortools）；没装时整组跳过。
import json, unittest

try:
    import staffing_agent as A
except ImportError:          # 没装 ortools
    A = None


@unittest.skipIf(A is None, "需要 pip install ortools")
class StaffingAgentTest(unittest.TestCase):
    def go(self, text, **kw):
        log = A.run(text, **kw)
        return log["guard"], log.get("result")

    def test_base(self):
        r = A.solve(A.BASE)
        self.assertEqual(r["cost"], 606)
        self.assertEqual(r["plan"], {"派遣": 7, "常勤加排": 8, "加急派遣": 0})

    def test_protagonist(self):                       # 主角那句话
        g, r = self.go("下周三有人请假，常勤最多只能加 4 班")
        self.assertEqual(g, "ok")
        self.assertEqual(r["plan"], {"派遣": 8, "常勤加排": 4, "加急派遣": 2})
        self.assertEqual(r["cost"], 678)
        self.assertEqual(A.approver(r, A.solve(A.BASE)), "院长批")

    def test_demand_and_price(self):
        self.assertEqual(self.go("病房说下周需求可能到 140 次")[1]["cost"], 656)
        self.assertEqual(self.go("派遣公司通知涨价 10%")[1]["cost"], 641)

    def test_guard_stops(self):                       # 门卫拦下的几句
        self.assertEqual(self.go("让小王别上太多班，大概两三班吧")[0], "ask")
        self.assertEqual(self.go("需求改成 1300 次")[0], "reject")
        self.assertEqual(self.go("派遣最多只能 10 班")[0], "reject")
        wrong = [{"type": "cost", "resource": "派遣", "value": 40, "quote": "派遣公司说加急每班 40"}]
        self.assertEqual(self.go("派遣公司说加急每班 40", changes=wrong)[0], "ask")
        self.assertEqual(self.go("派遣公司说加急每班 40")[0], "confirm")

    def test_rush_rule(self):                         # 带合同规则 600，拿掉规则 520 并亮灯
        _, r = self.go("派遣公司说加急每班 40", confirmed=True)
        self.assertEqual(r["cost"], 600)
        log = A.run("派遣公司说加急每班 40", confirmed=True, model_override={"rush_rule": False})
        self.assertEqual(log["result"]["cost"], 520)
        self.assertTrue(any("漏了合同规则" in f for f in log["flags"]))

    def test_two_changes(self):                       # 考考你 4
        _, r = self.go("常勤最多只能加 4 班，需求到 140 次")
        self.assertEqual(r["cost"], 753)
        self.assertEqual(r["plan"], {"派遣": 8, "常勤加排": 4, "加急派遣": 3})

    def test_penalty_one(self):                       # 考考你 3：罚金 1 时什么都不排
        m = json.loads(json.dumps(A.BASE)); m["shortage_penalty"] = 1
        r = A.solve(m)
        self.assertEqual(r["short"], 130)
        self.assertEqual(sum(r["plan"].values()), 0)

    def test_base_untouched(self):                    # 考考你 2：跑完任何一句，BASE 都没被改
        A.run("下周三有人请假，常勤最多只能加 4 班")
        self.assertEqual(A.BASE["resources"]["常勤加排"][2], 8)
        self.assertEqual(A.solve(A.BASE)["cost"], 606)


if __name__ == "__main__":
    unittest.main()
