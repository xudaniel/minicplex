package minicplex;

import java.util.List;
import java.util.Random;

/**
 * 自带测试（不依赖 JUnit），对应 C++ 的 tests/test_solver.cpp：
 * 已知答案的 LP/MIP、LP 文件读写、Gomory 割平面有效性、影子价格有限差分、
 * 以及 500 个随机整数规划与暴力枚举对比（三套参数）。
 *
 * 运行：java -cp build/classes:build/test-classes minicplex.SolverTest
 */
public final class SolverTest {
    private static int passes = 0, fails = 0;
    private static final double INF = Model.INF;

    private static void check(boolean cond, String what) {
        if (cond) ++passes;
        else {
            ++fails;
            System.err.println("FAIL: " + what);
        }
    }

    private static boolean near(double a, double b) { return near(a, b, 1e-6); }

    private static boolean near(double a, double b, double t) { return Math.abs(a - b) <= t * (1 + Math.abs(b)); }

    private static LinExpr x(Var v) { return LinExpr.of(v); }

    private static LinExpr x(double c, Var v) { return LinExpr.of(c, v); }

    static void testClassicLP() {
        Model m = new Model();
        Var x = m.addVar(), y = m.addVar();
        m.addConstr(x(x).le(4));
        m.addConstr(x(2, y).le(12));
        m.addConstr(x(3, x).plus(2, y).le(18));
        m.setObjective(x(3, x).plus(5, y), ObjSense.MAXIMIZE);
        Result r = Solver.solve(m);
        check(r.status == Status.OPTIMAL, "classic LP status");
        check(near(r.objective, 36), "classic LP objective");
        check(near(r.x[0], 2) && near(r.x[1], 6), "classic LP solution");
    }

    static void testInfeasibleUnbounded() {
        Model a = new Model();
        Var x = a.addVar(), y = a.addVar();
        a.addConstr(x(x).plus(y).le(1));
        a.addConstr(x(x).plus(y).ge(3));
        a.setObjective(x(x).plus(y));
        check(Solver.solve(a).status == Status.INFEASIBLE, "infeasible LP");

        Model b = new Model();
        Var u = b.addVar(), v = b.addVar();
        b.addConstr(x(u).minus(v).le(1));
        b.setObjective(x(u).plus(v), ObjSense.MAXIMIZE);
        check(Solver.solve(b).status == Status.UNBOUNDED, "unbounded LP");
    }

    static void testFreeAndEquality() {
        Model m = new Model();
        Var x = m.addVar(-INF, INF), y = m.addVar(-INF, INF);
        m.addConstr(x(x).plus(y).eq(10));
        m.addConstr(x(x).minus(y).ge(-2));
        m.setObjective(x(2, x).plus(y));
        Result r = Solver.solve(m);
        check(r.status == Status.OPTIMAL && near(r.objective, 14) && near(r.x[0], 4), "free vars + equality");

        Model n = new Model();
        Var z = n.addVar(-3, 7);
        n.addConstr(x(z).ge(-10));
        n.setObjective(x(z));
        check(near(Solver.solve(n).objective, -3), "negative lower bound");
        Model k = new Model();
        Var w = k.addVar(-INF, 5);
        k.setObjective(x(w), ObjSense.MAXIMIZE);
        check(near(Solver.solve(k).objective, 5), "free below, bounded above");
    }

    static void testBealeCycling() {  // 朴素 Dantzig 规则在这里会循环
        Model m = new Model();
        Var x4 = m.addVar(), x5 = m.addVar(), x6 = m.addVar(), x7 = m.addVar();
        m.addConstr(x(0.25, x4).minus(8, x5).minus(x6).plus(9, x7).le(0));
        m.addConstr(x(0.5, x4).minus(12, x5).minus(0.5, x6).plus(3, x7).le(0));
        m.addConstr(x(x6).le(1));
        m.setObjective(x(-0.75, x4).plus(20, x5).minus(0.5, x6).plus(6, x7));
        Result r = Solver.solve(m);
        check(r.status == Status.OPTIMAL && near(r.objective, -1.25), "Beale cycling example");
    }

    static void testEngineEdgeCases() {
        // 没有约束：最优解在边界上
        Model a = new Model();
        Var x = a.addVar(-2, 5), y = a.addVar(1, 3, VarType.INTEGER);
        a.setObjective(x(x).minus(2, y).plus(1));
        Result r = Solver.solve(a);
        check(r.status == Status.OPTIMAL && near(r.objective, -2 - 6 + 1), "no constraints");

        // 没有约束，方向无界
        Model b = new Model();
        Var u = b.addVar(0, INF);
        b.setObjective(x(u), ObjSense.MAXIMIZE);
        check(Solver.solve(b).status == Status.UNBOUNDED, "no constraints, unbounded");

        // 所有变量都固定
        Model c = new Model();
        Var p = c.addVar(3, 3), q = c.addVar(-1, -1);
        c.addConstr(x(p).plus(q).ge(2));
        c.setObjective(x(p).minus(q));
        r = Solver.solve(c);
        check(r.status == Status.OPTIMAL && near(r.objective, 4), "all fixed");
        Model c2 = new Model();
        Var p2 = c2.addVar(3, 3);
        c2.addConstr(x(p2).ge(4));
        c2.setObjective(x(p2));
        check(Solver.solve(c2).status == Status.INFEASIBLE, "all fixed, infeasible");

        // 负成本的有界变量（从上界出发）、等式行
        Model d = new Model();
        Var d1 = d.addVar(0, 4), d2 = d.addVar(0, 4), d3 = d.addVar(-INF, INF);
        d.addConstr(x(d1).plus(d2).plus(d3).eq(5));
        d.addConstr(x(d3).ge(-1));
        d.setObjective(x(-1, d1).minus(d2).plus(0.5, d3));
        r = Solver.solve(d);
        check(r.status == Status.OPTIMAL && near(r.objective, -6.5), "boxed with negative costs");

        // 整数取整后上下界颠倒：0.2 <= x <= 0.8，x 为整数
        Model e = new Model();
        Var ei = e.addVar(0.2, 0.8, VarType.INTEGER);
        e.setObjective(x(ei));
        check(Solver.solve(e).status == Status.INFEASIBLE, "inverted integer bounds");
    }

    static void testPresolve() {
        // 松的 big-M：x <= 1000 y 且 x <= 20  ->  系数收紧成 -20
        {
            Model m = new Model();
            Var x = m.addVar(0, 20), y = m.addVar(0, 1, VarType.BINARY);
            m.addConstr(x(x).minus(1000, y).le(0), "link");
            m.setObjective(x(2, x).minus(30, y), ObjSense.MAXIMIZE);
            double[] lb = {0, 0}, ub = {20, 1};
            boolean[] isInt = {false, true};
            Model W = new Model(m);
            Presolve.Stats st = new Presolve.Stats();
            check(Presolve.run(W, lb, ub, isInt, st), "presolve big-M feasible");
            boolean tight = false;
            for (Constraint c : W.constraints)
                if (c.name.equals("link")) tight = Math.abs(c.coefs.get(y.id()) + 20) < 1e-9;
            check(st.coefsTightened >= 1 && tight, "big-M coefficient tightened to -20");
            Params off = new Params();
            off.presolve = false;
            off.cutRounds = 0;
            Result r1 = Solver.solve(m), r2 = Solver.solve(m, off);
            check(r1.status == Status.OPTIMAL && near(r1.objective, 10) && near(r2.objective, 10),
                  "big-M same optimum with/without presolve");
        }
        // 界传播：x >= 7 通过 link 行逼出 y = 1
        {
            Model m = new Model();
            Var x = m.addVar(0, 20), y = m.addVar(0, 1, VarType.BINARY);
            m.addConstr(x(x).minus(1000, y).le(0), "link");
            m.addConstr(x(x).ge(7), "need");
            m.setObjective(x(x).plus(50, y));
            double[] lb = {0, 0}, ub = {20, 1};
            boolean[] isInt = {false, true};
            Model W = new Model(m);
            Presolve.Stats st = new Presolve.Stats();
            check(Presolve.run(W, lb, ub, isInt, st), "presolve propagation feasible");
            check(lb[1] == 1.0 && lb[0] >= 7.0 - 1e-6, "propagation forces y = 1");
            Result r = Solver.solve(m);
            check(r.status == Status.OPTIMAL && near(r.objective, 57), "propagation optimum");
        }

        // 单靠 presolve 就能证明不可行
        Model q = new Model();
        Var a = q.addVar(0, 10, VarType.INTEGER), b = q.addVar(0, 10, VarType.INTEGER);
        q.addConstr(x(a).plus(b).le(1));
        q.addConstr(x(a).ge(2));
        q.setObjective(x(a).plus(b));
        check(Solver.solve(q).status == Status.INFEASIBLE, "presolve proves infeasible");
    }

    static void testGomoryCutsAreValid() {
        // 根节点单纯形表生成的割平面，绝不能切掉任何整数可行点
        Random rng = new Random(777);
        int checked = 0, cutsSeen = 0;
        boolean allValid = true;
        for (int t = 0; t < 200; ++t) {
            Model M = new Model();
            final int n = 4;
            for (int j = 0; j < n; ++j) M.addVar(0, 4, VarType.INTEGER);
            for (int i = 0; i < 3; ++i) {
                LinExpr e = new LinExpr();
                for (int j = 0; j < n; ++j) e = e.plus(ri(rng, -4, 6), new Var(j));
                M.addConstr(e.le(ri(rng, 3, 15)));
            }
            LinExpr obj = new LinExpr();
            for (int j = 0; j < n; ++j) obj = obj.plus(ri(rng, 1, 9), new Var(j));
            M.setObjective(obj, ObjSense.MAXIMIZE);
            LPEngine E = new LPEngine(M, -1.0);
            if (E.solve(10000) != LPEngine.LPStatus.OPTIMAL) continue;
            boolean[] allInt = new boolean[n];
            java.util.Arrays.fill(allInt, true);
            List<Constraint> cuts = E.gomoryCuts(allInt, 20);
            cutsSeen += cuts.size();
            double[] p = new double[n];
            for (int a = 0; a < 625; ++a) {  // [0,4]^4 里的每个整数点
                int k = a;
                for (int j = 0; j < n; ++j) { p[j] = k % 5; k /= 5; }
                if (!Solver.checkFeasible(M, p)) continue;
                ++checked;
                for (Constraint c : cuts) {
                    double act = 0;
                    for (var en : c.coefs.entrySet()) act += en.getValue() * p[en.getKey()];
                    if (act < c.rhs - 1e-7) allValid = false;
                }
            }
        }
        System.out.println("  gomory: " + cutsSeen + " cuts checked against " + checked + " integer points");
        check(cutsSeen > 50, "enough Gomory cuts generated");
        check(allValid, "every Gomory cut is valid");
    }

    static void testShadowPrices() {
        // 面包店 LP：手算得面粉每公斤值 0.75，工时每小时值 0.5
        Model m = new Model();
        Var cake = m.addVar(), bread = m.addVar();
        m.addConstr(x(6, cake).plus(4, bread).le(24), "flour");
        m.addConstr(x(cake).plus(2, bread).le(6), "labor");
        m.setObjective(x(5, cake).plus(4, bread), ObjSense.MAXIMIZE);
        Result r = Solver.solve(m);
        check(r.duals.length == 2 && near(r.duals[0], 0.75) && near(r.duals[1], 0.5), "bakery duals");
        check(r.reducedCosts.length == 2 && near(r.reducedCosts[0], 0) && near(r.reducedCosts[1], 0),
              "bakery reduced costs");

        // 有限差分：右端项移动 ±delta，最优值应变化 dual * delta（只在局部非退化处检查）
        Random rng = new Random(4242);
        int compared = 0;
        boolean allOk = true;
        for (int t = 0; t < 60; ++t) {
            Model M = new Model();
            final int n = 6;
            for (int j = 0; j < n; ++j) M.addVar(ri(rng, -3, 0), ri(rng, 4, 12));
            for (int i = 0; i < 5; ++i) {
                LinExpr e = new LinExpr();
                for (int j = 0; j < n; ++j) e = e.plus(ri(rng, -5, 5), new Var(j));
                int s = ri(rng, 0, 2), b = ri(rng, -6, 10);
                M.addConstr(s == 0 ? e.le(b) : s == 1 ? e.ge(b) : e.eq(b));
            }
            LinExpr obj = new LinExpr();
            for (int j = 0; j < n; ++j) obj = obj.plus(ri(rng, -6, 6), new Var(j));
            M.setObjective(obj, ri(rng, 0, 1) == 1 ? ObjSense.MAXIMIZE : ObjSense.MINIMIZE);
            Result base = Solver.solve(M);
            if (base.status != Status.OPTIMAL) continue;
            for (int i = 0; i < M.numConstrs(); ++i) {
                final double delta = 1e-4;
                Model up = new Model(M), dn = new Model(M);
                up.constraints.get(i).rhs += delta;
                dn.constraints.get(i).rhs -= delta;
                Result ru = Solver.solve(up), rd = Solver.solve(dn);
                if (ru.status != Status.OPTIMAL || rd.status != Status.OPTIMAL) continue;
                double gu = (ru.objective - base.objective) / delta;
                double gd = (base.objective - rd.objective) / delta;
                if (Math.abs(gu - gd) > 1e-6 * (1 + Math.abs(gu))) continue;  // 拐点：对偶不唯一
                ++compared;
                if (Math.abs(gu - base.duals[i]) > 1e-5 * (1 + Math.abs(gu))) allOk = false;
            }
        }
        System.out.println("  shadow prices: " + compared + " rows checked by finite differences");
        check(compared > 50, "enough rows compared");
        check(allOk, "duals match finite differences");

        // MIP 没有对偶值
        Model q = new Model();
        Var z = q.addVar(0, 5, VarType.INTEGER);
        q.addConstr(x(2, z).le(7));
        q.setObjective(x(z), ObjSense.MAXIMIZE);
        check(Solver.solve(q).duals.length == 0, "MIP has no duals");
    }

    static void testKnapsack() {
        Model m = new Model();
        double[] val = {10, 13, 7, 8}, wt = {5, 6, 4, 3};
        LinExpr obj = new LinExpr(), w = new LinExpr();
        for (int i = 0; i < 4; ++i) {
            Var v = m.addVar(0, 1, VarType.BINARY);
            obj = obj.plus(val[i], v);
            w = w.plus(wt[i], v);
        }
        m.addConstr(w.le(10));
        m.setObjective(obj, ObjSense.MAXIMIZE);
        Result r = Solver.solve(m);
        check(r.status == Status.OPTIMAL && near(r.objective, 21), "knapsack optimum");
        check(Solver.checkFeasible(m, r.x), "knapsack solution feasible");
    }

    static void testReaderRoundTrip() {
        String text = """
            \\ test model
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
            """;
        Model m = LpReader.readString(text);
        check(m.numVars() == 4 && m.numConstrs() == 3, "reader sizes");
        check(m.objSense == ObjSense.MAXIMIZE, "reader objective sense");
        check(m.vars.get(m.findVar("z")).lb == -1 && m.vars.get(m.findVar("z")).ub == 4, "reader bounds");
        check(m.vars.get(m.findVar("x")).type == VarType.INTEGER, "reader General section");
        check(m.vars.get(m.findVar("b")).type == VarType.BINARY, "reader Binary section");
        Result r1 = Solver.solve(m);
        check(r1.status == Status.OPTIMAL, "reader model solves");

        Model m2 = LpReader.readString(m.toLP());
        Result r2 = Solver.solve(m2);
        check(r2.status == Status.OPTIMAL && near(r1.objective, r2.objective), "LP write/read round trip");

        boolean threw = false;
        try {
            LpReader.readString("Minimize\n obj: x +\nSubject To\n c: x >= 1\nEnd\n");
        } catch (RuntimeException ex) {
            threw = true;
        }
        check(threw, "reader rejects a dangling operator");
    }

    /** 随机纯整数规划，逐点枚举验证。 */
    static void testRandomVsBruteForce(int instances) {
        Random rng = new Random(12345);
        int agree = 0;
        for (int t = 0; t < instances; ++t) {
            final int n = ri(rng, 2, 4), m = ri(rng, 1, 4), U = 4;
            Model M = new Model();
            Var[] x = new Var[n];
            for (int j = 0; j < n; ++j) x[j] = M.addVar(ri(rng, -2, 0), U, VarType.INTEGER);
            for (int i = 0; i < m; ++i) {
                LinExpr e = new LinExpr();
                for (int j = 0; j < n; ++j) e = e.plus(ri(rng, -5, 5), x[j]);
                int s = ri(rng, 0, 2), rhs = ri(rng, -6, 10);
                M.addConstr(s == 0 ? e.le(rhs) : s == 1 ? e.ge(rhs) : e.eq(rhs));
            }
            LinExpr obj = new LinExpr();
            for (int j = 0; j < n; ++j) obj = obj.plus(ri(rng, -6, 6), x[j]);
            M.setObjective(obj, ri(rng, 0, 1) == 1 ? ObjSense.MAXIMIZE : ObjSense.MINIMIZE);

            // 暴力枚举
            double best = Double.NaN;
            double[] pt = new double[n];
            int[] idx = new int[n];
            for (int j = 0; j < n; ++j) idx[j] = (int) M.vars.get(j).lb;
            for (;;) {
                for (int j = 0; j < n; ++j) pt[j] = idx[j];
                if (Solver.checkFeasible(M, pt)) {
                    double v = Solver.evalObjective(M, pt);
                    if (Double.isNaN(best) || (M.objSense == ObjSense.MAXIMIZE ? v > best : v < best)) best = v;
                }
                int j = 0;
                while (j < n && ++idx[j] > U) { idx[j] = (int) M.vars.get(j).lb; ++j; }
                if (j == n) break;
            }

            boolean ok = true;
            for (int cfg = 0; cfg < 3; ++cfg) {  // 默认 / 关闭全部 MIP 技巧 / 激进割平面
                Params P = new Params();
                P.mipGap = 1e-9;
                if (cfg == 1) { P.presolve = false; P.cutRounds = 0; P.branching = Branching.MOST_FRACTIONAL; }
                if (cfg == 2) P.cutRounds = 10;
                Result r = Solver.solve(M, P);
                ok = ok && (Double.isNaN(best) ? r.status == Status.INFEASIBLE
                                               : (r.status == Status.OPTIMAL && near(r.objective, best)
                                                  && Solver.checkFeasible(M, r.x)));
            }
            if (ok) ++agree;
            else System.err.println("  random instance " + t + " mismatch: brute=" + best);
        }
        System.out.println("  random IPs: " + agree + "/" + instances + " match brute force");
        check(agree == instances, "random IPs match brute force");
    }

    private static int ri(Random rng, int a, int b) { return a + rng.nextInt(b - a + 1); }

    public static void main(String[] args) {
        Fmt.useUtf8Output();
        testClassicLP();
        testInfeasibleUnbounded();
        testFreeAndEquality();
        testBealeCycling();
        testEngineEdgeCases();
        testShadowPrices();
        testPresolve();
        testGomoryCutsAreValid();
        testKnapsack();
        testReaderRoundTrip();
        testRandomVsBruteForce(500);
        System.out.println(passes + " checks passed, " + fails + " failed");
        // 失败时抛异常（而不是 System.exit），这样在 Maven 的 exec:java 里也能正确报错
        if (fails > 0) throw new AssertionError(fails + " checks failed");
    }
}
