# 第 8 课：lambda、比较器和优先队列

> **这一课学：** lambda 表达式和方法引用；`Comparator`；`PriorityQueue`；稳定排序；一个真实的“平局” bug
> **用到的代码：** [`Solver.java`](../../src/main/java/minicplex/Solver.java) 的节点队列、[`LPEngine.java`](../../src/main/java/minicplex/LPEngine.java) 的割平面排序
> **练习：** `java/tutorial/run.sh 08`

[← List 和 Map](07-collections.md) · [目录](../README.md) · 下一课：[异常 →](09-exceptions.md)

## 1. lambda：把“一段代码”当成值传来传去

排序时，排序算法本身是通用的，只有“谁排在前面”需要我们告诉它。这一小段规则就用 lambda 写：

```java
names.sort((a, b) -> a.length() - b.length());   // 按长度从短到长
```

`(a, b) -> a.length() - b.length()` 是一个“接收 a、b，返回一个数”的小函数：返回负数表示 a 在前，正数表示 b 在前，0 表示一样。

如果 lambda 只是调用一个现成的方法，可以写成**方法引用**：

```java
e.terms.merge(v.id(), coef, Double::sum);        // 等于 (x, y) -> Double.sum(x, y)
Comparator.comparingDouble(Node::bound)          // 等于 n -> n.bound()
```

## 2. 优先队列：每次取出“最好的”那个

分支定界会留下很多“待处理的节点”，每次要取出**界最小**（最有希望）的那个。用排序？每加一个节点就重新排一遍太慢。`PriorityQueue` 专门做这件事：加入和取出都只要 O(log n)。

```java
// Solver.java
final PriorityQueue<Node> open = new PriorityQueue<>((a, b) ->
        a.bound != b.bound ? Double.compare(a.bound, b.bound)       // 1. 界小的先
        : a.depth != b.depth ? Integer.compare(b.depth, a.depth)    // 2. 界一样，深的先（更快找到整数解）
        : Long.compare(b.seq, a.seq));                              // 3. 还一样，后放进去的先

open.add(sib);          // 加入
Node next = open.poll();// 取出最好的（队列空时返回 null）
```

注意第 2 条把 `a`、`b` 反过来写，就成了“从大到小”。比较 `double` 一定要用 `Double.compare`，不要写 `a.bound - b.bound` 再转成 `int`：0.3 − 0.2 转成 `int` 是 0，会被当成“相等”。

同样的规则也可以用 `Comparator` 的链式方法写，更好读：

```java
Comparator.comparingDouble(Node::bound)
        .thenComparing(Node::depth, Comparator.reverseOrder())
        .thenComparing(Node::seq, Comparator.reverseOrder());
```

## 3. 一个真实的 bug：平局时谁先？

minicplex 有 C++ 和 Java 两个版本，要求每一步都一模一样。移植时有一个例子（员工排班）两边的最优值相同，但 C++ 搜了 8 个节点、Java 搜了 11 个。一路追查，原因是**平局**：

- 根节点生成割平面后，要按“效力”从高到低排序，挑前几个。有两个割平面效力**完全相等**。
- C++ 用的 `std::sort` 是**不稳定排序**：相等的元素排完后谁前谁后，由排序算法的实现细节决定。
- Java 的 `List.sort` 是**稳定排序**：相等的元素保持原来的先后顺序。
- 两边挑中了不同的割平面，后面每一步就都不一样了。

修法是让平局有明确的规则：C++ 也改成稳定排序（`std::stable_sort`），节点队列加上第 3 条“放入顺序”（`seq`）。现在两边每一步都相同，换一个编译器或标准库也不会变。

```java
// LPEngine.java：Java 的 List.sort 本来就是稳定的
cands.sort((a, b) -> Double.compare(b.eff(), a.eff()));
```

**教训：** 写比较器时，问自己“两个元素这几项都相等时怎么办？”。如果结果会影响后续计算，就加一条能分出先后的规则。

## 4. 常见坑

- 比较器要满足“传递性”：a 在 b 前、b 在 c 前，就必须 a 在 c 前。写错了，排序可能抛 `IllegalArgumentException: Comparison method violates its general contract!`。
- `PriorityQueue` 只保证 `poll()` 取出的是最小的；直接遍历它（`for (Node n : open)`）的顺序**不是**排好序的。
- lambda 里用到的外部局部变量必须是“实际上不变的”（effectively final）。

## 5. 动手

练习 [`L08Comparators.java`](../exercises/minicplex/tutorial/L08Comparators.java)：

1. 用 `Comparator` 链式方法写出 minicplex 的节点顺序；
2. 用 `PriorityQueue` 依次取出节点；
3. 用稳定排序按分数排名，同分的保持原来的顺序。

```bash
java/tutorial/run.sh 08
```

## 6. 想一想

1. 为什么界一样时要“深的先”？
2. 节点队列为什么选“后放进去的先”，而不是“先放进去的先”？两种都能保证确定性吗？

<details>
<summary>参考答案</summary>

1. 越深的节点，固定的变量越多，离一个完整的整数解越近。先往深处走，能尽早找到一个可行的整数解，有了它就能开始剪枝。
2. 两种都能保证确定性：只要规则明确，结果就唯一。选“后放进去的先”，和“深的先”的思路一致，倾向于继续刚才那条路。

</details>

[← List 和 Map](07-collections.md) · [目录](../README.md) · 下一课：[异常 →](09-exceptions.md)
