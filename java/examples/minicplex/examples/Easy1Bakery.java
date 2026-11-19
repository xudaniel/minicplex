// 简单例子 1：线性规划（LP）—— 面包店生产计划
//
// 面包店每天做蛋糕和面包：
//   蛋糕：每个利润 5 元，用面粉 6 kg、人工 1 小时
//   面包：每个利润 4 元，用面粉 4 kg、人工 2 小时
//   每天最多 24 kg 面粉、6 小时人工
// 问：各做多少，利润最大？（这里允许做半个，所以是连续变量）
package minicplex.examples;

import minicplex.*;

public class Easy1Bakery {
    public static void main(String[] args) {
        Fmt.useUtf8Output();
        Model m = new Model();

        // 1. 决策变量：做多少个（>= 0，连续）
        Var cake = m.addVar(0, Model.INF, VarType.CONTINUOUS, "cake");
        Var bread = m.addVar(0, Model.INF, VarType.CONTINUOUS, "bread");

        // 2. 约束
        m.addConstr(LinExpr.of(6, cake).plus(4, bread).le(24), "flour");  // 面粉
        m.addConstr(LinExpr.of(1, cake).plus(2, bread).le(6), "labor");   // 人工

        // 3. 目标：利润最大
        m.setObjective(LinExpr.of(5, cake).plus(4, bread), ObjSense.MAXIMIZE);

        // 4. 求解
        Result r = Solver.solve(m);

        System.out.println("状态：" + r.status);
        System.out.println("最大利润：" + Fmt.g(r.objective) + " 元");
        System.out.println("蛋糕：" + Fmt.g(r.value(cake)) + " 个");
        System.out.println("面包：" + Fmt.g(r.value(bread)) + " 个");
    }
}
