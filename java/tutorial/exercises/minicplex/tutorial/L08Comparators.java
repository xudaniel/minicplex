package minicplex.tutorial;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.PriorityQueue;

/**
 * 第 8 课练习：lambda、比较器和优先队列。
 *
 * <p>运行：java/tutorial/run.sh 08
 */
public class L08Comparators {

    /** 分支定界里的一个节点（简化版）：界、深度、放入顺序。 */
    record Node(String name, double bound, int depth, long seq) {}

    /**
     * minicplex 选下一个节点的规则：界小的先（最有希望）；界一样，深的先；还一样，后放进去的先。
     * 用 Comparator.comparingDouble(...).thenComparing(...) 链式写出来。
     */
    static Comparator<Node> nodeOrder() {
        // TODO 提示：Comparator.comparingDouble(Node::bound)
        //      .thenComparing(Node::depth, Comparator.reverseOrder()) …
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 把所有节点放进优先队列，再一个个取出来，返回取出的名字顺序。 */
    static List<String> pollOrder(List<Node> nodes) {
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 按分数从高到低排序，分数相同的保持原来的先后（List.sort 是稳定排序）。返回名字。 */
    static List<String> sortByScore(List<String> names, List<Double> scores) {
        // TODO 先做一个下标列表 0..n−1，用 lambda 比较 scores.get(i)，排好后取名字
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    public static void main(String[] args) {
        Check.lesson("第 8 课：lambda、比较器和优先队列");
        List<Node> nodes = List.of(
                new Node("甲", 10, 1, 1),
                new Node("乙", 8, 1, 2),
                new Node("丙", 8, 3, 3),
                new Node("丁", 8, 3, 4),
                new Node("戊", 12, 5, 5));
        Check.eq("界最小的先出；界相同深的先；再相同新的先", List.of("丁", "丙", "乙", "甲", "戊"), () -> pollOrder(nodes));
        Check.that("比较器认为“丁”排在“丙”前面", () -> nodeOrder().compare(nodes.get(3), nodes.get(2)) < 0);
        Check.eq("稳定排序：同分的“乙”“丙”保持原顺序", List.of("丁", "乙", "丙", "甲"),
                () -> sortByScore(List.of("甲", "乙", "丙", "丁"), List.of(1.0, 5.0, 5.0, 9.0)));
        Check.done();
    }
}
