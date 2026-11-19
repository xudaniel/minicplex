// 进阶例子 08：最小化最大值——公平分配
//
// 6 件任务分给 3 个人，用时分别是 5、4、3、3、2、1 小时。每件任务只给一个人。
// 目标：让最忙的那个人尽量不忙（所有人尽早一起下班）。
//
// 技巧：“最大值”不能直接写进目标。新建一个变量 T 表示“最忙的人的工作量”，
// 要求每个人的工作量都 ≤ T，然后最小化 T。最优时 T 就等于真正的最大值。
package minicplex.examples;

import minicplex.*;

public class Basics08MinMax {
    public static void main(String[] args) {
        Fmt.useUtf8Output();
        double[] hours = {5, 4, 3, 3, 2, 1};
        int tasks = hours.length, people = 3;

        Model m = new Model();
        // give[t][p] = 1 表示任务 t 交给第 p 个人
        Var[][] give = new Var[tasks][people];
        for (int t = 0; t < tasks; ++t)
            for (int p = 0; p < people; ++p)
                give[t][p] = m.addVar(0, 1, VarType.BINARY, "give_" + t + "_" + p);
        Var T = m.addVar(0, Model.INF, VarType.CONTINUOUS, "T");  // 最忙的人的工作量

        for (int t = 0; t < tasks; ++t) {  // 每件任务正好给一个人
            LinExpr once = new LinExpr();
            for (int p = 0; p < people; ++p) once = once.plus(give[t][p]);
            m.addConstr(once.eq(1), "task" + t);
        }
        for (int p = 0; p < people; ++p) {  // 每个人的工作量 ≤ T
            LinExpr load = new LinExpr();
            for (int t = 0; t < tasks; ++t) load = load.plus(hours[t], give[t][p]);
            m.addConstr(load.le(T), "load" + p);
        }
        m.setObjective(LinExpr.of(T), ObjSense.MINIMIZE);

        Result r = Solver.solve(m);
        System.out.printf("最忙的人工作 %.0f 小时%n", r.objective);
        for (int p = 0; p < people; ++p) {
            double load = 0;
            System.out.printf("第 %d 个人：", p + 1);
            for (int t = 0; t < tasks; ++t)
                if (r.value(give[t][p]) > 0.5) {
                    System.out.printf("%.0f 小时任务 ", hours[t]);
                    load += hours[t];
                }
            System.out.printf("→ 共 %.0f 小时%n", load);
        }
    }
}
