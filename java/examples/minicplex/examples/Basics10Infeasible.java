// 进阶例子 10：题目无解怎么办？
//
// 复习计划：数学至少 6 小时，英语至少 5 小时，但这周总共只有 8 小时。
// 显然做不到，求解器会报 Infeasible（不可行）。可是到底差多少？先放弃哪一条？
//
// 技巧（弹性约束）：给每条“至少”加一个“缺口”变量（≥ 0），允许不满足，
// 但缺口要付代价，然后最小化总代价。代价越高，表示越不愿意放弃这一条。
package minicplex.examples;

import minicplex.*;

public class Basics10Infeasible {
    public static void main(String[] args) {
        Fmt.useUtf8Output();
        // 1. 原始问题：无解
        {
            Model m = new Model();
            Var math = m.addVar(0, Model.INF, VarType.CONTINUOUS, "math");
            Var eng = m.addVar(0, Model.INF, VarType.CONTINUOUS, "english");
            m.addConstr(LinExpr.of(math).ge(6), "math_min");
            m.addConstr(LinExpr.of(eng).ge(5), "english_min");
            m.addConstr(LinExpr.of(math).plus(eng).le(8), "time");
            m.setObjective(LinExpr.of(math).plus(eng), ObjSense.MINIMIZE);
            System.out.printf("原始问题：%s%n%n", Solver.solve(m).status);
        }
        // 2. 弹性版本：缺口可以存在，但要付代价
        for (double mathWeight : new double[] {1.0, 3.0}) {
            Model m = new Model();
            Var math = m.addVar(0, Model.INF, VarType.CONTINUOUS, "math");
            Var eng = m.addVar(0, Model.INF, VarType.CONTINUOUS, "english");
            Var shortMath = m.addVar(0, Model.INF, VarType.CONTINUOUS, "short_math");  // 数学缺了几小时
            Var shortEng = m.addVar(0, Model.INF, VarType.CONTINUOUS, "short_english");
            m.addConstr(LinExpr.of(math).plus(shortMath).ge(6), "math_min");
            m.addConstr(LinExpr.of(eng).plus(shortEng).ge(5), "english_min");
            m.addConstr(LinExpr.of(math).plus(eng).le(8), "time");  // 时间是硬限制，不能放宽
            m.setObjective(LinExpr.of(mathWeight, shortMath).plus(1.0, shortEng), ObjSense.MINIMIZE);
            Result r = Solver.solve(m);
            System.out.printf("数学缺口代价 %.0f、英语缺口代价 1：数学 %.0f 小时，英语 %.0f 小时；"
                              + "数学缺 %.0f，英语缺 %.0f，一共缺 %.0f 小时%n",
                              mathWeight, r.value(math), r.value(eng), r.value(shortMath), r.value(shortEng),
                              r.value(shortMath) + r.value(shortEng));
        }
        System.out.printf("%n结论：不管怎么分，总共都要缺 3 小时；代价决定缺口落在哪一科。%n");
    }
}
