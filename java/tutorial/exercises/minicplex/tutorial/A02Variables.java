package minicplex.tutorial;

/**
 * 入门 A2：变量和计算。
 *
 * <p>运行：java/tutorial/run.sh A02
 */
public class A02Variables {

    /** 买 apples 个苹果，每个 pricePerApple 元，一共多少钱？ */
    static int total(int apples, int pricePerApple) {
        // TODO 乘法用 *
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 带了 money 元，花了 cost 元，找回多少？ */
    static int change(int money, int cost) {
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** money 元钱，每个 price 元，最多买几个？（整数相除，小数部分自动丢掉） */
    static int howMany(int money, int price) {
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 买完最多的个数后，还剩几元？（% 是“除完剩下的余数”） */
    static int leftover(int money, int price) {
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 两个整数的平均数，要保留小数：average(7, 8) 是 7.5。 */
    static double average(int a, int b) {
        // TODO 小心：(a + b) / 2 是整数除法，7 和 8 会得到 7。除以 2.0 才对
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    public static void main(String[] args) {
        Check.lesson("入门 A2：变量和计算");
        Check.eq("3 个苹果、每个 2 元：6 元", 6, () -> total(3, 2));
        Check.eq("带 10 元花 6 元：找回 4 元", 4, () -> change(10, 6));
        Check.eq("10 元、3 元一个：最多 3 个", 3, () -> howMany(10, 3));
        Check.eq("10 元、3 元一个：还剩 1 元", 1, () -> leftover(10, 3));
        Check.near("7 和 8 的平均数是 7.5", 7.5, () -> average(7, 8));
        Check.that("提醒：Java 里 7 / 2 等于 3，不是 3.5", () -> 7 / 2 == 3);
        Check.done();
    }
}
