package minicplex.tutorial;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import minicplex.*;

/**
 * 第 5 课练习：封装和不可变对象。
 *
 * <p>仿照 minicplex 的 LinExpr，写一个“不可变”的表达式：每次运算都返回新对象，原来的永远不变。
 *
 * <p>运行：java/tutorial/run.sh 05
 */
public class L05Immutable {

    /** 不可变表达式：变量名 → 系数。 */
    static final class Expr {
        private final TreeMap<String, Double> terms;

        Expr() { this.terms = new TreeMap<>(); }

        private Expr(TreeMap<String, Double> terms) { this.terms = terms; }

        /** 返回“原表达式 + coef × name”的新表达式。原表达式不能被改动！ */
        Expr plus(String name, double coef) {
            // TODO 先复制一份 terms（new TreeMap<>(terms)），在副本上 merge，再用副本 new 一个 Expr
            // >>>
            TreeMap<String, Double> copy = new TreeMap<>(terms);
            copy.merge(name, coef, Double::sum);
            return new Expr(copy);
            // <<<
        }

        /** 把所有项交给外面看，但外面不能修改：返回只读视图。 */
        Map<String, Double> terms() {
            // TODO 提示：Collections.unmodifiableMap
            // >>>
            return Collections.unmodifiableMap(terms);
            // <<<
        }
    }

    /** 深复制：复制列表，也复制列表里的每个数组（clone）。和 Model(Model o) 的思路一样。 */
    static List<double[]> deepCopy(List<double[]> rows) {
        // >>>
        List<double[]> out = new ArrayList<>();
        for (double[] r : rows) out.add(r.clone());
        return out;
        // <<<
    }

    public static void main(String[] args) {
        Check.lesson("第 5 课：封装和不可变对象");
        Check.that("plus 返回新对象，原表达式不变", () -> {
            Expr a = new Expr().plus("x", 2);
            Expr b = a.plus("y", 3);
            return a.terms().size() == 1 && b.terms().size() == 2;
        });
        Check.near("同一个变量的系数会合并：2x + 5x = 7x", 7, () -> new Expr().plus("x", 2).plus("x", 5).terms().get("x"));
        Check.throwsA("从外面改 terms() 会报错", UnsupportedOperationException.class,
                () -> new Expr().plus("x", 1).terms().put("y", 9.0));
        Check.throwsA("minicplex 的 LinExpr.terms() 同样是只读的", UnsupportedOperationException.class, () -> {
            Model m = new Model();
            Var x = m.addVar();
            LinExpr.of(2, x).terms().put(x.id(), 100.0);
        });
        Check.that("深复制后改副本，原数据不受影响", () -> {
            List<double[]> orig = new ArrayList<>(List.of(new double[] {1, 2}));
            List<double[]> copy = deepCopy(orig);
            copy.get(0)[0] = 99;
            return orig.get(0)[0] == 1 && copy.get(0) != orig.get(0);
        });
        Check.that("对比：浅复制（只复制列表）会把原数据一起改掉", () -> {
            List<double[]> orig = new ArrayList<>(List.of(new double[] {1, 2}));
            List<double[]> shallow = new ArrayList<>(orig);
            shallow.get(0)[0] = 99;
            return orig.get(0)[0] == 99;
        });
        Check.done();
    }
}
