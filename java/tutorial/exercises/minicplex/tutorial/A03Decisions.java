package minicplex.tutorial;

/**
 * 入门 A3：做判断（if / else）。
 *
 * <p>运行：java/tutorial/run.sh A03
 */
public class A03Decisions {

    /** 钱够不够？money 不少于 cost 就够。 */
    static boolean canAfford(int money, int cost) {
        // TODO 比较大小：>= 表示“大于或等于”
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 根据气温给建议：低于 10 度 "冷"，低于 25 度 "舒服"，否则 "热"。 */
    static String weather(int temp) {
        // TODO if (temp < 10) { return "冷"; } else if (...) { ... } else { ... }
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 运费：买满 99 元包邮（运费 0），否则 10 元。 */
    static int shipping(int total) {
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 是不是周末？day 是 "Sat" 或 "Sun" 就是。比较文字要用 equals，不用 ==。 */
    static boolean isWeekend(String day) {
        // TODO “或”写成 ||
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    public static void main(String[] args) {
        Check.lesson("入门 A3：做判断");
        Check.that("10 元买 8 元的东西：够", () -> canAfford(10, 8));
        Check.that("10 元买 10 元的东西：刚好够", () -> canAfford(10, 10));
        Check.that("5 元买 8 元的东西：不够", () -> !canAfford(5, 8));
        Check.eq("3 度：冷", "冷", () -> weather(3));
        Check.eq("18 度：舒服", "舒服", () -> weather(18));
        Check.eq("25 度：热", "热", () -> weather(25));
        Check.eq("买 120 元：包邮", 0, () -> shipping(120));
        Check.eq("买 50 元：运费 10 元", 10, () -> shipping(50));
        Check.that("Sun 是周末", () -> isWeekend("Sun"));
        Check.that("Mon 不是周末", () -> !isWeekend("Mon"));
        Check.done();
    }
}
