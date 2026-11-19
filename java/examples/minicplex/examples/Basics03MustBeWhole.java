// 入门例子 03：必须是整数
//
// 问题（面包店）：蛋糕每个赚 5 元，面包每个赚 4 元。
//   - 面粉只有 24 公斤：蛋糕用 6 公斤，面包用 4 公斤
//   - 人工只有 6 小时：蛋糕用 1 小时，面包用 2 小时
// 不能卖半个，怎么做最赚钱？
//
// 这个例子会算两遍：先允许做半个，再要求整数，看看有什么不同。
package minicplex.examples;

import minicplex.*;

public class Basics03MustBeWhole {
    public static void main(String[] args) {
        Fmt.useUtf8Output();
        Model m = new Model();
        // VarType.INTEGER 表示“必须是整数”
        Var cake = m.addVar(0, Model.INF, VarType.INTEGER, "cake");
        Var bread = m.addVar(0, Model.INF, VarType.INTEGER, "bread");
        m.addConstr(LinExpr.of(6, cake).plus(4, bread).le(24), "flour");
        m.addConstr(LinExpr.of(1, cake).plus(2, bread).le(6), "labor");
        m.setObjective(LinExpr.of(5, cake).plus(4, bread), ObjSense.MAXIMIZE);

        // 第一遍：暂时忽略“必须是整数”（relaxIntegrality = 放松整数要求）
        Params relaxed = new Params();
        relaxed.relaxIntegrality = true;
        Result a = Solver.solve(m, relaxed);
        System.out.println("允许做半个：蛋糕 " + Fmt.g(a.value(cake)) + "，面包 " + Fmt.g(a.value(bread))
                           + "，赚 " + Fmt.g(a.objective) + " 元");

        // 很多人会想：把小数部分去掉不就行了？
        double c = Math.floor(a.value(cake)), b = Math.floor(a.value(bread));
        System.out.println("直接去掉小数：蛋糕 " + Fmt.g(c) + "，面包 " + Fmt.g(b) + "，赚 " + Fmt.g(5 * c + 4 * b) + " 元");

        // 第二遍：真正的整数规划
        Result r = Solver.solve(m);
        System.out.println("整数最优解：  蛋糕 " + Fmt.g(r.value(cake)) + "，面包 " + Fmt.g(r.value(bread))
                           + "，赚 " + Fmt.g(r.objective) + " 元");
        System.out.println("结论：整数最优解不是“去掉小数”那么简单，需要分支定界来找。");
    }
}
