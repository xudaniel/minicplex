package minicplex.tutorial;

import java.util.List;

/**
 * 第 4 课练习：类和对象。
 *
 * <p>仿照 minicplex 的 VarInfo，写一个“商品”类。
 *
 * <p>运行：java/tutorial/run.sh 04
 */
public class L04Classes {

    /** 一件商品：名字、重量、价值。 */
    static class Item {
        private final String name;
        private final double weight;
        private final double value;

        /** 构造方法：把三个参数存进字段。 */
        Item(String name, double weight, double value) {
            // TODO 用 this.name = name 这样的写法给三个字段赋值
            throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
        }

        /** 重载的构造方法：没给重量时，重量当作 1。提示：用 this(...) 调用上面那个构造方法。 */
        Item(String name, double value) {
            throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
        }

        /** 复制构造方法：做一个和 o 一模一样的新对象（和 VarInfo(VarInfo o) 一样）。 */
        Item(Item o) {
            throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
        }

        String name() { return name; }
        double weight() { return weight; }
        double value() { return value; }

        /** 性价比 = 价值 ÷ 重量。 */
        double ratio() {
            throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
        }
    }

    /** 静态方法：在一堆商品里找性价比最高的那件（列表为空时返回 null）。 */
    static Item best(List<Item> items) {
        // TODO 用增强 for 循环：for (Item it : items) { ... }
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    public static void main(String[] args) {
        Check.lesson("第 4 课：类和对象");
        Check.eq("构造方法存下了名字", "茶", () -> new Item("茶", 2, 8).name());
        Check.near("性价比 = 8 / 2 = 4", 4, () -> new Item("茶", 2, 8).ratio());
        Check.near("只给价值时，重量是 1", 1, () -> new Item("糖", 5).weight());
        Check.that("复制出来的是另一个对象", () -> {
            Item a = new Item("茶", 2, 8);
            Item b = new Item(a);
            return a != b && b.name().equals("茶") && b.value() == 8;
        });
        Check.eq("性价比最高的是咖啡", "咖啡",
                () -> best(List.of(new Item("茶", 2, 8), new Item("咖啡", 1, 6), new Item("饼", 4, 10))).name());
        Check.that("空列表返回 null", () -> best(List.of()) == null);
        Check.done();
    }
}
