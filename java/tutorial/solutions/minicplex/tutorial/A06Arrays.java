package minicplex.tutorial;

/**
 * 入门 A6：数组，一次存一排数。
 *
 * <p>运行：java/tutorial/run.sh A06
 */
public class A06Arrays {

    /** 所有数加起来。a.length 是数组有几个数，a[i] 是第 i 个（从 0 开始数）。 */
    static int sum(int[] a) {
        // TODO for (int i = 0; i < a.length; i++) { ... a[i] ... }
        // >>>
        int s = 0;
        for (int i = 0; i < a.length; i++) s += a[i];
        return s;
        // <<<
    }

    /** 最大的数（数组至少有一个数）。先假设第一个最大，再一个个比。 */
    static int max(int[] a) {
        // >>>
        int best = a[0];
        for (int x : a) if (x > best) best = x;
        return best;
        // <<<
    }

    /** 有几个数大于 limit？ */
    static int countAbove(int[] a, int limit) {
        // >>>
        int n = 0;
        for (int x : a) if (x > limit) n++;
        return n;
        // <<<
    }

    /** 平均数，保留小数。 */
    static double average(int[] a) {
        // TODO 可以用上面的 sum；记得除以 (double) a.length，否则是整数除法
        // >>>
        return sum(a) / (double) a.length;
        // <<<
    }

    /** 倒过来：{1, 2, 3} 变成 {3, 2, 1}。先 new 一个一样长的新数组。 */
    static int[] reversed(int[] a) {
        // >>>
        int[] r = new int[a.length];
        for (int i = 0; i < a.length; i++) r[i] = a[a.length - 1 - i];
        return r;
        // <<<
    }

    public static void main(String[] args) {
        Check.lesson("入门 A6：数组");
        int[] steps = {4200, 8100, 6500, 12000, 3000};  // 一周里 5 天的步数
        Check.eq("5 天一共走了 33800 步", 33800, () -> sum(steps));
        Check.eq("走得最多的一天 12000 步", 12000, () -> max(steps));
        Check.eq("超过 6000 步的有 3 天", 3, () -> countAbove(steps, 6000));
        Check.near("平均每天 6760 步", 6760, () -> average(steps));
        Check.near("{1, 2} 的平均数是 1.5", 1.5, () -> average(new int[] {1, 2}));
        Check.eq("倒过来", "[3, 2, 1]", () -> java.util.Arrays.toString(reversed(new int[] {1, 2, 3})));
        Check.done();
    }
}
