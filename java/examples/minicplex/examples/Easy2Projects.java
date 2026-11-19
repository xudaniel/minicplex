// 简单例子 2：0-1 整数规划（MIP）—— 投资项目选择
//
// 预算 10 万元，有 4 个项目，每个要么投、要么不投：
//   项目   投入(万)   收益(万)
//    A       5         8
//    B       4         7
//    C       3         4
//    D       2         4
// 额外规则：投 C 的前提是也投 D（C <= D）
// 问：投哪几个，总收益最大？
package minicplex.examples;

import minicplex.*;

public class Easy2Projects {
    public static void main(String[] args) {
        Fmt.useUtf8Output();
        String[] name = {"A", "B", "C", "D"};
        double[] cost = {5, 4, 3, 2};
        double[] gain = {8, 7, 4, 4};

        Model m = new Model();
        Var[] pick = new Var[name.length];
        LinExpr totalCost = new LinExpr(), totalGain = new LinExpr();
        for (int i = 0; i < name.length; ++i) {
            // 0-1 变量：1 = 投，0 = 不投
            pick[i] = m.addVar(0, 1, VarType.BINARY, name[i]);
            totalCost = totalCost.plus(cost[i], pick[i]);
            totalGain = totalGain.plus(gain[i], pick[i]);
        }

        m.addConstr(totalCost.le(10), "budget");                     // 预算
        m.addConstr(LinExpr.of(pick[2]).le(pick[3]), "C_needs_D");   // 投 C 必须投 D
        m.setObjective(totalGain, ObjSense.MAXIMIZE);

        Result r = Solver.solve(m);

        System.out.println("状态：" + r.status);
        System.out.println("最大收益：" + Fmt.g(r.objective) + " 万");
        StringBuilder sb = new StringBuilder("投资项目：");
        for (int i = 0; i < name.length; ++i)
            if (r.value(pick[i]) > 0.5) sb.append(name[i]).append(' ');
        System.out.println(sb);
        System.out.println("分支定界节点数：" + r.nodes);
    }
}
