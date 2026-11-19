// 入门例子 02：两个变量、两条限制
//
// 问题：去水果店，苹果 2 元一个，香蕉 1 元一个。
//   - 你有 10 元
//   - 袋子最多装 7 个水果
//   - 你给每个苹果打 3 分（好吃），每根香蕉打 2 分
// 怎么买，总分最高？
package minicplex.examples;

import minicplex.*;

public class Basics02TwoVariables {
    public static void main(String[] args) {
        Fmt.useUtf8Output();
        Model m = new Model();
        Var apple = m.addVar(0, Model.INF, VarType.CONTINUOUS, "apple");
        Var banana = m.addVar(0, Model.INF, VarType.CONTINUOUS, "banana");

        m.addConstr(LinExpr.of(2, apple).plus(1, banana).le(10), "money");  // 钱：2×苹果 + 1×香蕉 ≤ 10
        m.addConstr(LinExpr.of(apple).plus(banana).le(7), "bag");           // 袋子：苹果 + 香蕉 ≤ 7

        m.setObjective(LinExpr.of(3, apple).plus(2, banana), ObjSense.MAXIMIZE);  // 总分 = 3×苹果 + 2×香蕉

        Result r = Solver.solve(m);
        double a = r.value(apple), b = r.value(banana);
        System.out.println("苹果 " + Fmt.g(a) + " 个，香蕉 " + Fmt.g(b) + " 根，总分 " + Fmt.g(r.objective));

        // 两条限制都刚好用满吗？算一算：
        System.out.println("花钱 " + Fmt.g(2 * a + b) + " 元（上限 10），装了 " + Fmt.g(a + b) + " 个（上限 7）");
    }
}
