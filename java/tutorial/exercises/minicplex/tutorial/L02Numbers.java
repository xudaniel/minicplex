package minicplex.tutorial;

/**
 * 第 2 课练习：数字和小数误差。
 *
 * <p>运行：java/tutorial/run.sh 02
 */
public class L02Numbers {

    /** a 和 b 是否“足够接近”：|a − b| ≤ tol × (1 + |b|)。这正是 minicplex 测试里 near() 的写法。 */
    static boolean near(double a, double b, double tol) {
        // TODO 用 Math.abs 写出上面的公式
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** v 是不是（在 1e-9 的误差内）一个整数？无穷大和 NaN 都不算。 */
    static boolean isIntegral(double v) {
        // TODO 先排除无穷大和 NaN（Double.isFinite），再看 v 和 Math.rint(v) 差多少
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 小数部分，永远在 [0, 1) 里：2.75 → 0.75，−1.25 → 0.75。分支定界用它判断“离整数有多远”。 */
    static double fractionalPart(double v) {
        // TODO 提示：Math.floor 是“向下取整”，−1.25 向下取整是 −2
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 四舍五入，0.5 远离 0：2.5 → 3，−2.5 → −3。（Java 的 Math.round(−2.5) 是 −2！） */
    static double roundHalfAway(double v) {
        // TODO 提示：先对 |v| + 0.5 向下取整，再把符号乘回去（Math.signum）
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    public static void main(String[] args) {
        Check.lesson("第 2 课：数字和小数误差");
        Check.that("0.1 + 0.2 和 0.3 用 == 比较居然不相等", () -> 0.1 + 0.2 != 0.3);
        Check.that("但它们是“足够接近”的", () -> near(0.1 + 0.2, 0.3, 1e-9));
        Check.that("1 和 1.001 在 1e-6 的误差下不接近", () -> !near(1, 1.001, 1e-6));
        Check.that("3.0000000001 算整数", () -> isIntegral(3.0000000001));
        Check.that("2.5 不算整数", () -> !isIntegral(2.5));
        Check.that("无穷大不算整数", () -> !isIntegral(Double.POSITIVE_INFINITY));
        Check.that("NaN 不算整数", () -> !isIntegral(Double.NaN));
        Check.near("2.75 的小数部分是 0.75", 0.75, () -> fractionalPart(2.75));
        Check.near("−1.25 的小数部分也是 0.75", 0.75, () -> fractionalPart(-1.25));
        Check.near("roundHalfAway(2.5) = 3", 3, () -> roundHalfAway(2.5));
        Check.near("roundHalfAway(−2.5) = −3", -3, () -> roundHalfAway(-2.5));
        Check.that("而 Math.round(−2.5) 是 −2：两种“四舍五入”不一样", () -> Math.round(-2.5) == -2);
        Check.done();
    }
}
