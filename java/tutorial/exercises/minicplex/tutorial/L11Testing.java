package minicplex.tutorial;

import java.util.Random;

import minicplex.*;

/**
 * 第 11 课练习：自己写测试——让暴力枚举当“标准答案”。
 *
 * <p>这正是 minicplex 的 SolverTest.testRandomVsBruteForce 的思路。
 *
 * <p>运行：java/tutorial/run.sh 11
 */
public class L11Testing {

    /** 生成一道随机的 0-1 规划：n 个 0-1 变量，m 条 ≤ 约束，系数都是 −3..9 的整数，目标随机最大化。 */
    static Model randomBinaryModel(Random rng, int n, int m) {
        Model M = new Model();
        Var[] x = new Var[n];
        for (int j = 0; j < n; ++j) x[j] = M.addVar(0, 1, VarType.BINARY, "x" + j);
        for (int i = 0; i < m; ++i) {
            LinExpr e = new LinExpr();
            for (int j = 0; j < n; ++j) e = e.plus(rng.nextInt(13) - 3, x[j]);
            M.addConstr(e.le(rng.nextInt(15)), "r" + i);
        }
        LinExpr obj = new LinExpr();
        for (int j = 0; j < n; ++j) obj = obj.plus(rng.nextInt(19) - 6, x[j]);
        M.setObjective(obj, ObjSense.MAXIMIZE);
        return M;
    }

    /**
     * 暴力求解一个“全是 0-1 变量”的最大化模型：试遍 2^n 个点，用 Solver.checkFeasible 判断可行，
     * 用 Solver.evalObjective 算目标值。没有可行点时返回 Double.NaN。
     */
    static double bruteForce(Model M) {
        // TODO 和第 3 课的背包一样用 mask 枚举；double[] x = new double[n]，x[k] = (mask >> k) & 1
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 跑 count 道随机题（种子从 seed 开始），返回求解器和暴力答案一致的题数。 */
    static int agreeCount(long seed, int count) {
        // TODO 每道题：new Random(seed + t)，n 取 3..10，m 取 1..4；Solver.solve 后比较：
        //      暴力是 NaN 时要求状态是 INFEASIBLE，否则要求 OPTIMAL 且目标值相差 ≤ 1e-6
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    public static void main(String[] args) {
        Check.lesson("第 11 课：自己写测试");
        Check.near("暴力求解一道小题：x0 + x1 ≤ 1 时最大化 3x0 + 2x1 = 3", 3, () -> {
            Model M = new Model();
            Var a = M.addVar(0, 1, VarType.BINARY, "a"), b = M.addVar(0, 1, VarType.BINARY, "b");
            M.addConstr(LinExpr.of(a).plus(b).le(1));
            M.setObjective(LinExpr.of(3, a).plus(2, b), ObjSense.MAXIMIZE);
            return bruteForce(M);
        });
        Check.that("同一个种子生成同一道题（可复现）", () ->
                randomBinaryModel(new Random(7), 5, 2).toLP().equals(randomBinaryModel(new Random(7), 5, 2).toLP()));
        Check.eq("200 道随机题全部一致", 200, () -> agreeCount(1000, 200));
        Check.done();
    }
}
