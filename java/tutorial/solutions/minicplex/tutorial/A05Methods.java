package minicplex.tutorial;

/**
 * 入门 A5：自己写方法。
 *
 * <p>运行：java/tutorial/run.sh A05
 */
public class A05Methods {

    /** 长方形面积 = 宽 × 高。 */
    static double area(double width, double height) {
        // >>>
        return width * height;
        // <<<
    }

    /** 两个数里大的那个。 */
    static int max(int a, int b) {
        // >>>
        if (a > b) return a;
        return b;
        // <<<
    }

    /** 三个数里最大的。提示：调用上面写好的 max，不用重写比较。 */
    static int maxOfThree(int a, int b, int c) {
        // TODO return max(max(a, b), c);
        // >>>
        return max(max(a, b), c);
        // <<<
    }

    /** 摄氏度转华氏度：F = C × 9 / 5 + 32。 */
    static double fahrenheit(double celsius) {
        // >>>
        return celsius * 9 / 5 + 32;
        // <<<
    }

    /**
     * 把 v 夹在 [lo, hi] 之间：比 lo 小就返回 lo，比 hi 大就返回 hi，否则原样返回。
     * minicplex 里每个变量都有下界和上界，就是这个意思。
     */
    static int clamp(int v, int lo, int hi) {
        // >>>
        if (v < lo) return lo;
        if (v > hi) return hi;
        return v;
        // <<<
    }

    public static void main(String[] args) {
        Check.lesson("入门 A5：自己写方法");
        Check.near("3 × 4 的长方形面积 12", 12, () -> area(3, 4));
        Check.eq("max(3, 9) = 9", 9, () -> max(3, 9));
        Check.eq("max(-1, -5) = -1", -1, () -> max(-1, -5));
        Check.eq("maxOfThree(4, 11, 7) = 11", 11, () -> maxOfThree(4, 11, 7));
        Check.near("100 摄氏度 = 212 华氏度", 212, () -> fahrenheit(100));
        Check.near("0 摄氏度 = 32 华氏度", 32, () -> fahrenheit(0));
        Check.eq("clamp(15, 0, 10) = 10", 10, () -> clamp(15, 0, 10));
        Check.eq("clamp(-3, 0, 10) = 0", 0, () -> clamp(-3, 0, 10));
        Check.eq("clamp(6, 0, 10) = 6", 6, () -> clamp(6, 0, 10));
        Check.done();
    }
}
