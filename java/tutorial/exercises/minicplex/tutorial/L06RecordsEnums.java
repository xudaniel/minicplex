package minicplex.tutorial;

import minicplex.*;

/**
 * 第 6 课练习：record 和 enum。
 *
 * <p>运行：java/tutorial/run.sh 06
 */
public class L06RecordsEnums {

    /** 一个 record：Java 自动生成构造方法、取值方法、equals、hashCode 和 toString。 */
    record Item(String name, double weight, double value) {
        /** record 里也可以写普通方法。 */
        double ratio() {
            throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
        }
    }

    /** 带字段的 enum，和 minicplex 的 Status 一样：每个常量带一个中文标签。 */
    enum Grade {
        A("优秀"), B("良好"), C("及格"), F("不及格");

        private final String label;

        Grade(String label) { this.label = label; }

        String label() { return label; }

        /** 90 分及以上 A，75 及以上 B，60 及以上 C，否则 F。 */
        static Grade of(int score) {
            throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
        }
    }

    /** 用 switch 表达式（case ... ->）把求解状态翻译成中文，和 Main.java 里解析命令行的写法一样。 */
    static String describe(Status s) {
        // TODO OPTIMAL → "找到最优解"，INFEASIBLE → "无解"，UNBOUNDED → "可以无限好"，其他 → "没算完"
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    public static void main(String[] args) {
        Check.lesson("第 6 课：record 和 enum");
        Check.near("record 的方法：性价比 4", 4, () -> new Item("茶", 2, 8).ratio());
        Check.eq("两个内容相同的 record 用 equals 比较是相等的", new Item("茶", 2, 8), () -> new Item("茶", 2, 8));
        Check.eq("record 自带好看的 toString", "Item[name=茶, weight=2.0, value=8.0]", () -> new Item("茶", 2, 8).toString());
        Check.eq("minicplex 的 Var 也是 record：new Var(3) 等于 new Var(3)", new Var(3), () -> new Var(3));
        Check.eq("95 分是 A", Grade.A, () -> Grade.of(95));
        Check.eq("75 分是 B", Grade.B, () -> Grade.of(75));
        Check.eq("59 分的标签是“不及格”", "不及格", () -> Grade.of(59).label());
        Check.eq("Grade 一共有 4 个值", 4, () -> Grade.values().length);
        Check.eq("Status.OPTIMAL 的 toString 是 Optimal（和 C++ 版输出一样）", "Optimal", () -> Status.OPTIMAL.toString());
        Check.eq("OPTIMAL → 找到最优解", "找到最优解", () -> describe(Status.OPTIMAL));
        Check.eq("INFEASIBLE → 无解", "无解", () -> describe(Status.INFEASIBLE));
        Check.eq("NODE_LIMIT → 没算完", "没算完", () -> describe(Status.NODE_LIMIT));
        Check.done();
    }
}
