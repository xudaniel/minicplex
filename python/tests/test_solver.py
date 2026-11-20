"""minicplex Python 版的测试（只用标准库 unittest），对应 C++ 的 tests/test_solver.cpp 和 Java 的 SolverTest：
已知答案的 LP/MIP、LP 文件读写、Gomory 割平面有效性、影子价格有限差分，
以及 500 个随机整数规划与暴力枚举对比（三套参数）。另加 Python 版特有的运算符重载测试。

运行：python3 -m unittest discover -s python/tests -v
"""
import itertools
import math
import pathlib
import random
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from minicplex import (INF, Branching, Constraint, LinExpr, LpParseError, Model, ObjSense, Params, Sense, Status,  # noqa: E402
                       Var, VarType, check_feasible, eval_objective, read_string, solve)
from minicplex import lp_engine, presolve  # noqa: E402


def near(a, b, t=1e-6):
    return abs(a - b) <= t * (1 + abs(b))


class KnownAnswers(unittest.TestCase):
    def test_classic_lp(self):
        m = Model()
        x, y = m.add_var(), m.add_var()
        m.add_constr(x <= 4)
        m.add_constr(2 * y <= 12)
        m.add_constr(3 * x + 2 * y <= 18)
        m.set_objective(3 * x + 5 * y, ObjSense.MAXIMIZE)
        r = solve(m)
        self.assertEqual(r.status, Status.OPTIMAL)
        self.assertTrue(near(r.objective, 36))
        self.assertTrue(near(r.x[0], 2) and near(r.x[1], 6))

    def test_infeasible_and_unbounded(self):
        a = Model()
        x, y = a.add_var(), a.add_var()
        a.add_constr(x + y <= 1)
        a.add_constr(x + y >= 3)
        a.set_objective(x + y)
        self.assertEqual(solve(a).status, Status.INFEASIBLE)

        b = Model()
        u, v = b.add_var(), b.add_var()
        b.add_constr(u - v <= 1)
        b.set_objective(u + v, ObjSense.MAXIMIZE)
        self.assertEqual(solve(b).status, Status.UNBOUNDED)

    def test_free_vars_and_equality(self):
        m = Model()
        x, y = m.add_var(-INF, INF), m.add_var(-INF, INF)
        m.add_constr(x + y == 10)
        m.add_constr(x - y >= -2)
        m.set_objective(2 * x + y)
        r = solve(m)
        self.assertTrue(r.status == Status.OPTIMAL and near(r.objective, 14) and near(r.x[0], 4))

        n = Model()
        z = n.add_var(-3, 7)
        n.add_constr(z >= -10)
        n.set_objective(z)
        self.assertTrue(near(solve(n).objective, -3), "negative lower bound")
        k = Model()
        w = k.add_var(-INF, 5)
        k.set_objective(w, ObjSense.MAXIMIZE)
        self.assertTrue(near(solve(k).objective, 5), "free below, bounded above")

    def test_beale_cycling(self):  # 朴素 Dantzig 规则在这里会循环
        m = Model()
        x4, x5, x6, x7 = (m.add_var() for _ in range(4))
        m.add_constr(0.25 * x4 - 8 * x5 - x6 + 9 * x7 <= 0)
        m.add_constr(0.5 * x4 - 12 * x5 - 0.5 * x6 + 3 * x7 <= 0)
        m.add_constr(x6 <= 1)
        m.set_objective(-0.75 * x4 + 20 * x5 - 0.5 * x6 + 6 * x7)
        r = solve(m)
        self.assertTrue(r.status == Status.OPTIMAL and near(r.objective, -1.25))

    def test_engine_edge_cases(self):
        a = Model()  # 没有约束：最优解在边界上
        x, y = a.add_var(-2, 5), a.add_var(1, 3, VarType.INTEGER)
        a.set_objective(x - 2 * y + 1)
        r = solve(a)
        self.assertTrue(r.status == Status.OPTIMAL and near(r.objective, -2 - 6 + 1), "no constraints")

        b = Model()  # 没有约束，方向无界
        b.set_objective(b.add_var(0, INF), ObjSense.MAXIMIZE)
        self.assertEqual(solve(b).status, Status.UNBOUNDED)

        c = Model()  # 所有变量都固定
        p, q = c.add_var(3, 3), c.add_var(-1, -1)
        c.add_constr(p + q >= 2)
        c.set_objective(p - q)
        r = solve(c)
        self.assertTrue(r.status == Status.OPTIMAL and near(r.objective, 4), "all fixed")
        c2 = Model()
        p2 = c2.add_var(3, 3)
        c2.add_constr(p2 >= 4)
        c2.set_objective(p2)
        self.assertEqual(solve(c2).status, Status.INFEASIBLE, "all fixed, infeasible")

        d = Model()  # 负成本的有界变量（从上界出发）、等式行
        d1, d2, d3 = d.add_var(0, 4), d.add_var(0, 4), d.add_var(-INF, INF)
        d.add_constr(d1 + d2 + d3 == 5)
        d.add_constr(d3 >= -1)
        d.set_objective(-1 * d1 - d2 + 0.5 * d3)
        r = solve(d)
        self.assertTrue(r.status == Status.OPTIMAL and near(r.objective, -6.5), "boxed with negative costs")

        e = Model()  # 整数取整后上下界颠倒：0.2 <= x <= 0.8，x 为整数
        e.set_objective(e.add_var(0.2, 0.8, VarType.INTEGER))
        self.assertEqual(solve(e).status, Status.INFEASIBLE, "inverted integer bounds")

    def test_knapsack(self):
        m = Model()
        val, wt = [10, 13, 7, 8], [5, 6, 4, 3]
        v = [m.add_var(0, 1, VarType.BINARY) for _ in range(4)]
        m.add_constr(sum(w * x for w, x in zip(wt, v)) <= 10)
        m.set_objective(sum(c * x for c, x in zip(val, v)), ObjSense.MAXIMIZE)
        r = solve(m)
        self.assertTrue(r.status == Status.OPTIMAL and near(r.objective, 21))
        self.assertTrue(check_feasible(m, r.x))


class Presolve(unittest.TestCase):
    def test_big_m_tightened(self):
        # 松的 big-M：x <= 1000 y 且 x <= 20  ->  系数收紧成 -20
        m = Model()
        x, y = m.add_var(0, 20), m.add_var(0, 1, VarType.BINARY)
        m.add_constr(x - 1000 * y <= 0, "link")
        m.set_objective(2 * x - 30 * y, ObjSense.MAXIMIZE)
        lb, ub = [0.0, 0.0], [20.0, 1.0]
        W, st = m.copy(), presolve.Stats()
        self.assertTrue(presolve.run(W, lb, ub, [False, True], st))
        link = next(c for c in W.constraints if c.name == "link")
        self.assertGreaterEqual(st.coefs_tightened, 1)
        self.assertLess(abs(link.coefs[y.id] + 20), 1e-9)
        r1, r2 = solve(m), solve(m, Params(presolve=False, cut_rounds=0))
        self.assertTrue(r1.status == Status.OPTIMAL and near(r1.objective, 10) and near(r2.objective, 10))

    def test_propagation(self):
        # 界传播：x >= 7 通过 link 行逼出 y = 1
        m = Model()
        x, y = m.add_var(0, 20), m.add_var(0, 1, VarType.BINARY)
        m.add_constr(x - 1000 * y <= 0, "link")
        m.add_constr(x >= 7, "need")
        m.set_objective(x + 50 * y)
        lb, ub = [0.0, 0.0], [20.0, 1.0]
        self.assertTrue(presolve.run(m.copy(), lb, ub, [False, True], presolve.Stats()))
        self.assertTrue(lb[1] == 1.0 and lb[0] >= 7.0 - 1e-6)
        r = solve(m)
        self.assertTrue(r.status == Status.OPTIMAL and near(r.objective, 57))

    def test_proves_infeasible(self):
        q = Model()
        a, b = q.add_var(0, 10, VarType.INTEGER), q.add_var(0, 10, VarType.INTEGER)
        q.add_constr(a + b <= 1)
        q.add_constr(a >= 2)
        q.set_objective(a + b)
        self.assertEqual(solve(q).status, Status.INFEASIBLE)


class Cuts(unittest.TestCase):
    def test_gomory_cuts_are_valid(self):
        """根节点单纯形表生成的割平面，绝不能切掉任何整数可行点。"""
        rng = random.Random(777)
        checked = cuts_seen = 0
        n = 4
        for _ in range(200):
            M = Model()
            for _ in range(n):
                M.add_var(0, 4, VarType.INTEGER)
            for _ in range(3):
                M.add_constr(sum((rng.randint(-4, 6) * Var(j) for j in range(n)), LinExpr()) <= rng.randint(3, 15))
            M.set_objective(sum((rng.randint(1, 9) * Var(j) for j in range(n)), LinExpr()), ObjSense.MAXIMIZE)
            E = lp_engine.LPEngine(M, -1.0)
            if E.solve(10000) != lp_engine.OPTIMAL:
                continue
            cuts = E.gomory_cuts([True] * n, 20)
            cuts_seen += len(cuts)
            for p in itertools.product(range(5), repeat=n):
                p = [float(v) for v in p]
                if not check_feasible(M, p):
                    continue
                checked += 1
                for c in cuts:
                    act = sum(a * p[k] for k, a in c.coefs.items())
                    self.assertGreaterEqual(act, c.rhs - 1e-7, "a Gomory cut removed an integer point")
        self.assertGreater(cuts_seen, 50)
        print(f"\n  gomory: {cuts_seen} cuts checked against {checked} integer points", end=" ")


class ShadowPrices(unittest.TestCase):
    def test_bakery(self):
        m = Model()
        cake, bread = m.add_var(), m.add_var()
        m.add_constr(6 * cake + 4 * bread <= 24, "flour")
        m.add_constr(cake + 2 * bread <= 6, "labor")
        m.set_objective(5 * cake + 4 * bread, ObjSense.MAXIMIZE)
        r = solve(m)
        self.assertTrue(len(r.duals) == 2 and near(r.duals[0], 0.75) and near(r.duals[1], 0.5))
        self.assertTrue(len(r.reduced_costs) == 2 and near(r.reduced_costs[0], 0) and near(r.reduced_costs[1], 0))

    def test_finite_differences(self):
        """右端项移动 ±delta，最优值应变化 dual * delta（只在局部非退化处检查）。"""
        rng = random.Random(4242)
        compared = 0
        n = 6
        for _ in range(60):
            M = Model()
            for _ in range(n):
                M.add_var(rng.randint(-3, 0), rng.randint(4, 12))
            for _ in range(5):
                e = sum((rng.randint(-5, 5) * Var(j) for j in range(n)), LinExpr())
                s, b = rng.randint(0, 2), rng.randint(-6, 10)
                M.add_constr(e <= b if s == 0 else e >= b if s == 1 else e == b)
            M.set_objective(sum((rng.randint(-6, 6) * Var(j) for j in range(n)), LinExpr()),
                            ObjSense.MAXIMIZE if rng.randint(0, 1) else ObjSense.MINIMIZE)
            base = solve(M)
            if base.status != Status.OPTIMAL:
                continue
            for i in range(M.num_constrs):
                delta = 1e-4
                up, dn = M.copy(), M.copy()
                up.constraints[i].rhs += delta
                dn.constraints[i].rhs -= delta
                ru, rd = solve(up), solve(dn)
                if ru.status != Status.OPTIMAL or rd.status != Status.OPTIMAL:
                    continue
                gu = (ru.objective - base.objective) / delta
                gd = (base.objective - rd.objective) / delta
                if abs(gu - gd) > 1e-6 * (1 + abs(gu)):
                    continue  # 拐点：对偶不唯一
                compared += 1
                self.assertLessEqual(abs(gu - base.duals[i]), 1e-5 * (1 + abs(gu)))
        self.assertGreater(compared, 50)
        print(f"\n  shadow prices: {compared} rows checked by finite differences", end=" ")

    def test_mip_has_no_duals(self):
        q = Model()
        z = q.add_var(0, 5, VarType.INTEGER)
        q.add_constr(2 * z <= 7)
        q.set_objective(z, ObjSense.MAXIMIZE)
        self.assertEqual(solve(q).duals, [])


class Reader(unittest.TestCase):
    TEXT = """\\ test model
Maximize
 obj: 3 x + 2 y - z + 0.5
Subject To
 c1: x + y + z <= 7.5
 c2: x - y >= -2
 c3: - z + 2 x = 1
Bounds
 -1 <= z <= 4
 y <= 3
General
 x
Binary
 b
End
"""

    def test_round_trip(self):
        m = read_string(self.TEXT)
        self.assertEqual((m.num_vars, m.num_constrs), (4, 3))
        self.assertEqual(m.obj_sense, ObjSense.MAXIMIZE)
        z = m.vars[m.find_var("z")]
        self.assertEqual((z.lb, z.ub), (-1, 4))
        self.assertEqual(m.vars[m.find_var("x")].type, VarType.INTEGER)
        self.assertEqual(m.vars[m.find_var("b")].type, VarType.BINARY)
        r1 = solve(m)
        self.assertEqual(r1.status, Status.OPTIMAL)
        r2 = solve(read_string(m.to_lp()))
        self.assertTrue(r2.status == Status.OPTIMAL and near(r1.objective, r2.objective))

    def test_rejects_dangling_operator(self):
        with self.assertRaises(LpParseError):
            read_string("Minimize\n obj: x +\nSubject To\n c: x >= 1\nEnd\n")


class RandomVsBruteForce(unittest.TestCase):
    def test_random_ips(self, instances=500):
        """随机纯整数规划，逐点枚举验证（默认 / 关闭全部 MIP 技巧 / 激进割平面）。"""
        rng = random.Random(12345)
        agree = 0
        U = 4
        for t in range(instances):
            n, m = rng.randint(2, 4), rng.randint(1, 4)
            M = Model()
            x = [M.add_var(rng.randint(-2, 0), U, VarType.INTEGER) for _ in range(n)]
            for _ in range(m):
                e = sum((rng.randint(-5, 5) * xj for xj in x), LinExpr())
                s, rhs = rng.randint(0, 2), rng.randint(-6, 10)
                M.add_constr(e <= rhs if s == 0 else e >= rhs if s == 1 else e == rhs)
            M.set_objective(sum((rng.randint(-6, 6) * xj for xj in x), LinExpr()),
                            ObjSense.MAXIMIZE if rng.randint(0, 1) else ObjSense.MINIMIZE)

            best = math.nan  # 暴力枚举
            for pt in itertools.product(*(range(int(v.lb), U + 1) for v in M.vars)):
                pt = [float(v) for v in pt]
                if check_feasible(M, pt):
                    v = eval_objective(M, pt)
                    if math.isnan(best) or (v > best if M.obj_sense == ObjSense.MAXIMIZE else v < best):
                        best = v

            ok = True
            for P in (Params(mip_gap=1e-9),
                      Params(mip_gap=1e-9, presolve=False, cut_rounds=0, branching=Branching.MOST_FRACTIONAL),
                      Params(mip_gap=1e-9, cut_rounds=10)):
                r = solve(M, P)
                if math.isnan(best):
                    ok = ok and r.status == Status.INFEASIBLE
                else:
                    ok = ok and r.status == Status.OPTIMAL and near(r.objective, best) and check_feasible(M, r.x)
            agree += ok
            if not ok:
                print(f"  random instance {t} mismatch: brute={best}")
        print(f"\n  random IPs: {agree}/{instances} match brute force", end=" ")
        self.assertEqual(agree, instances)


class PythonApi(unittest.TestCase):
    """Python 版特有的部分：运算符重载、表达式不可变、变量把手的相等比较。"""

    def test_operators_build_the_same_rows(self):
        m = Model()
        x, y = m.add_var(name="x"), m.add_var(name="y")
        c = 2 * x + 3 * y - 5 <= 12 - y
        self.assertEqual((c.coefs, c.sense, c.rhs), ({0: 2.0, 1: 4.0}, Sense.LE, 17.0))
        c = 10 >= x  # Python 把它翻成 x <= 10
        self.assertEqual((c.coefs, c.sense, c.rhs), ({0: 1.0}, Sense.LE, 10.0))
        c = -(x - y) / 2 == 1
        self.assertEqual((c.coefs, c.sense, c.rhs), ({0: -0.5, 1: 0.5}, Sense.EQ, 1.0))
        self.assertEqual(sum([x, y, x]).terms, {0: 2.0, 1: 1.0})

    def test_expressions_are_immutable(self):
        m = Model()
        x = m.add_var()
        e = 2 * x
        f = e + 1
        f2 = e * 3
        self.assertEqual((e.terms, e.constant), ({0: 2.0}, 0.0))
        self.assertEqual(f.constant, 1.0)
        self.assertEqual(f2.terms, {0: 6.0})

    def test_var_handles(self):
        m = Model()
        x, y = m.add_var(name="x"), m.add_var(name="y")
        self.assertTrue(x == Var(0))          # 同一个变量：在 if 里是 True
        self.assertFalse(x == y)
        self.assertEqual({x: "a", y: "b"}[Var(1)], "b")
        self.assertIn(m.var("y"), [x, y])
        self.assertIsInstance(x == y, Constraint)  # 但它本身是一条约束，可以加进模型
        with self.assertRaises(TypeError):
            bool(x + 1 <= 3)                  # 表达式比较不能当 True/False

    def test_errors(self):
        m = Model()
        m.add_var(name="x")
        with self.assertRaises(ValueError):
            m.add_var(name="x")
        with self.assertRaises(KeyError):
            m.var("nope")
        with self.assertRaises(ValueError):
            m.add_constr(Var(5) <= 1)
        with self.assertRaises(TypeError):
            m.add_constr(True)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
