// 进阶例子 09：绝对值——选址让总距离最短
//
// 一条路上有 5 户人家，位置分别是 1、3、8、10、20（公里）。
// 要在路上建一个快递点，让它到所有人家的距离之和最小。建在哪里？
//
// 技巧：距离是绝对值 |x − 位置|，不能直接写成线性限制。为每户人家新建一个变量 d，
// 要求  d ≥ x − 位置  并且  d ≥ 位置 − x，然后最小化所有 d 的和。
// 求最小时，d 会自动被压到两者中较大的那个，也就是绝对值。
package minicplex.examples;

import minicplex.*;

public class Basics09AbsoluteValue {
    public static void main(String[] args) {
        Fmt.useUtf8Output();
        double[] home = {1, 3, 8, 10, 20};

        Model m = new Model();
        Var x = m.addVar(-Model.INF, Model.INF, VarType.CONTINUOUS, "x");  // 快递点位置
        LinExpr total = new LinExpr();
        Var[] d = new Var[home.length];
        for (int i = 0; i < home.length; ++i) {
            d[i] = m.addVar(0, Model.INF, VarType.CONTINUOUS, "d" + i);  // 到第 i 户的距离
            m.addConstr(LinExpr.of(d[i]).ge(LinExpr.of(x).minus(home[i])), "right" + i);           // d ≥ x − 位置
            m.addConstr(LinExpr.of(d[i]).ge(LinExpr.constant(home[i]).minus(x)), "left" + i);      // d ≥ 位置 − x
            total = total.plus(d[i]);
        }
        m.setObjective(total, ObjSense.MINIMIZE);

        Result r = Solver.solve(m);
        System.out.printf("快递点建在 %.0f 公里处，总距离 %.0f 公里%n", r.value(x), r.objective);
        for (int i = 0; i < home.length; ++i)
            System.out.printf("  到位置 %2.0f 的人家：%.0f 公里%n", home[i], r.value(d[i]));
        // 对比：如果建在平均位置（很多人的第一反应），总距离是多少？
        double mean = 0, distMean = 0;
        for (double h : home) mean += h / home.length;
        for (double h : home) distMean += Math.abs(h - mean);
        System.out.printf("对比：建在平均位置 %.1f，总距离 %.1f 公里，反而更远。最优位置是中位数，不是平均数。%n", mean,
                          distMean);
    }
}
