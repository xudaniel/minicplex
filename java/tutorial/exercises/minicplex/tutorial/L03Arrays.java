package minicplex.tutorial;

import java.util.Random;

import minicplex.*;

/**
 * 第 3 课练习：数组和循环。
 *
 * <p>运行：java/tutorial/run.sh 03
 */
public class L03Arrays {

    /** m 行 n 列的矩阵按行存进一维数组时，第 i 行第 j 列在哪个位置？（LPEngine 的 A[i * n + j]） */
    static int flatIndex(int i, int j, int n) {
        // TODO 一行一行地排：前面有 i 整行，每行 n 个
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 一维数组 a 里存着 m 行 n 列的矩阵，求第 i 行所有元素的和。 */
    static double rowSum(double[] a, int m, int n, int i) {
        // TODO 用 for 循环，配合 flatIndex
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /**
     * 暴力解 0-1 背包：试遍所有 2^n 种选法，返回总重量不超过 cap 时的最大总价值。
     * 第 mask 种选法里，物品 k 选没选看 (mask &gt;&gt; k) &amp; 1。
     */
    static double bruteForceKnapsack(double[] weight, double[] value, double cap) {
        // TODO 外层循环 mask 从 0 到 (1 << n) − 1，内层循环 k 从 0 到 n − 1
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 用 minicplex 解同一个背包：每个物品一个 0-1 变量。返回最优总价值。 */
    static double solverKnapsack(double[] weight, double[] value, double cap) {
        // TODO 用数组 Var[] pick 存变量；在循环里累加重量表达式和价值表达式（e = e.plus(...)）
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    public static void main(String[] args) {
        Check.lesson("第 3 课：数组和循环");
        Check.eq("3 列矩阵的 (2, 1) 在位置 7", 7, () -> flatIndex(2, 1, 3));
        double[] a = {1, 2, 3, 4, 5, 6};  // 2 行 3 列：[1 2 3; 4 5 6]
        Check.near("第 0 行的和是 6", 6, () -> rowSum(a, 2, 3, 0));
        Check.near("第 1 行的和是 15", 15, () -> rowSum(a, 2, 3, 1));
        double[] wt = {5, 6, 4, 3}, val = {10, 13, 7, 8};
        Check.near("暴力背包：容量 10 时最大价值 21", 21, () -> bruteForceKnapsack(wt, val, 10));
        Check.near("求解器背包：也是 21", 21, () -> solverKnapsack(wt, val, 10));
        Check.that("20 道随机背包，暴力和求解器答案都一样", () -> {
            Random rng = new Random(2026);  // 固定种子：每次运行都是同样的 20 道题
            for (int t = 0; t < 20; ++t) {
                int n = 3 + rng.nextInt(6);
                double[] w = new double[n], v = new double[n];
                for (int k = 0; k < n; ++k) { w[k] = 1 + rng.nextInt(9); v[k] = 1 + rng.nextInt(20); }
                double cap = 5 + rng.nextInt(20);
                if (Math.abs(bruteForceKnapsack(w, v, cap) - solverKnapsack(w, v, cap)) > 1e-6) return false;
            }
            return true;
        });
        Check.done();
    }
}
