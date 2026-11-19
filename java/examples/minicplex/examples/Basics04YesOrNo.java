// 入门例子 04：选或不选（0-1 变量）
//
// 问题：周末有 8 小时空闲，有 4 件想做的事：
//   事情      用时    开心值
//   看电影    3 小时    6
//   爬山      5 小时    9
//   吃大餐    2 小时    4
//   读书      4 小时    5
// 规则：爬山和读书不能都选（太累）。选哪几件最开心？
package minicplex.examples;

import minicplex.*;

public class Basics04YesOrNo {
    public static void main(String[] args) {
        Fmt.useUtf8Output();
        String[] name = {"看电影", "爬山", "吃大餐", "读书"};
        double[] hours = {3, 5, 2, 4};
        double[] happy = {6, 9, 4, 5};

        Model m = new Model();
        Var[] pick = new Var[name.length];
        LinExpr time = new LinExpr(), fun = new LinExpr();
        for (int i = 0; i < name.length; ++i) {
            // VarType.BINARY：只能取 0（不选）或 1（选）
            pick[i] = m.addVar(0, 1, VarType.BINARY, "pick" + i);
            time = time.plus(hours[i], pick[i]);  // 总用时 = Σ 用时 × 选没选（LinExpr 不可变，plus 返回新对象）
            fun = fun.plus(happy[i], pick[i]);    // 总开心值
        }
        m.addConstr(time.le(8), "hours");                                // 时间不超过 8 小时
        m.addConstr(LinExpr.of(pick[1]).plus(pick[3]).le(1), "not_both");  // 爬山 + 读书 ≤ 1：最多选其中一个
        m.setObjective(fun, ObjSense.MAXIMIZE);

        Result r = Solver.solve(m);
        StringBuilder sb = new StringBuilder("选：");
        for (int i = 0; i < name.length; ++i)
            if (r.value(pick[i]) > 0.5) sb.append(name[i]).append(' ');
        System.out.println(sb);
        System.out.println("开心值 " + Fmt.g(r.objective));
    }
}
