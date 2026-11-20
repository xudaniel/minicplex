package minicplex.tutorial;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import minicplex.*;

/**
 * 第 7 课练习：List 和 Map。
 *
 * <p>运行：java/tutorial/run.sh 07
 */
public class L07Collections {

    /** 名字 → 编号（第几个），和 Model 里的 index 一样。名字重复时抛 IllegalArgumentException。 */
    static Map<String, Integer> buildIndex(List<String> names) {
        // TODO 用 HashMap；containsKey 判断重复
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /**
     * 合并同类项：ids[k] 是变量编号，coefs[k] 是系数。同一个编号的系数加起来，加完是 0 的去掉。
     * 返回按编号从小到大排好的 TreeMap（LinExpr 就是这么存的）。
     */
    static TreeMap<Integer, Double> mergeTerms(int[] ids, double[] coefs) {
        // TODO 提示：map.merge(key, value, Double::sum)；最后用 values().removeIf(v -> v == 0.0)
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 求解后，按变量顺序列出取值不为 0 的变量名（|值| &gt; 1e-9）。 */
    static List<String> nonzeroNames(Model m, Result r) {
        // TODO m.vars 是 List<VarInfo>，r.x[j] 是第 j 个变量的取值
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    public static void main(String[] args) {
        Check.lesson("第 7 课：List 和 Map");
        Check.eq("“乙”的编号是 1", 1, () -> buildIndex(List.of("甲", "乙", "丙")).get("乙"));
        Check.that("找不到的名字返回 null", () -> buildIndex(List.of("甲")).get("丁") == null);
        Check.throwsA("名字重复会报错", IllegalArgumentException.class, () -> buildIndex(List.of("甲", "甲")));
        Check.eq("合并同类项：2x₃ + 1x₁ + 5x₃ − 1x₁ = 7x₃", Map.of(3, 7.0),
                () -> mergeTerms(new int[] {3, 1, 3, 1}, new double[] {2, 1, 5, -1}));
        Check.eq("TreeMap 按编号排好序", List.of(1, 4, 9),
                () -> new ArrayList<>(mergeTerms(new int[] {9, 1, 4}, new double[] {1, 1, 1}).keySet()));
        Check.eq("面包店整数版只做蛋糕", List.of("cake"), () -> {
            Model m = LpReader.readString("""
                    Maximize
                     profit: 5 cake + 4 bread
                    Subject To
                     flour: 6 cake + 4 bread <= 24
                     labor: cake + 2 bread <= 6
                    General
                     cake bread
                    End
                    """);
            return nonzeroNames(m, Solver.solve(m));
        });
        Check.done();
    }
}
