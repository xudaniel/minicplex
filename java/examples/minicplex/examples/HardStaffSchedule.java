// 复杂例子 2：餐厅一周员工排班（0-1 整数规划）
//
// 8 名员工（4 名全职、4 名兼职），一周 7 天，每天早班、晚班各一个（每班 8 小时）。
// 决策：x[员工][天][班] = 1 表示该员工这天上这个班。
// 规则：
//   1. 每个班的人数 ≥ 需求（周末和周五晚上更忙）
//   2. 每个班至少 1 名老员工坐镇
//   3. 每人每天最多上 1 个班
//   4. 上完晚班，第二天不能接早班（保证休息）
//   5. 全职每周 4~5 天，兼职每周 2~4 天
//   6. 员工请假 / 不可用的日子不排班（例如兼职小刘只有周五到周日有空）
//   7. 全职员工周末两天最多上 1 天（轮流休周末）——店长除外；兼职可两天都上
//   8. 每人连续上班不超过 3 天（任意连续 4 天里至少休 1 天）
//   9. 新人小刘、小孙上班时，同一班必须有师傅（小李或小陈）带
//  10. 小王和小张合不来，不排在同一个班
// 目标：工资 + 员工偏好惩罚（不喜欢的班次）总和最小。
//
// 规模：112 个 0-1 变量（其中 21 个因不可用被固定为 0），183 条约束。
// 运行时会把模型写到 hard_staff_schedule.lp，可用 CPLEX / HiGHS 对照验证。
package minicplex.examples;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import minicplex.*;

public class HardStaffSchedule {
    record Staff(String name, String id, boolean fullTime, boolean senior, boolean manager,
                 double wage,             // 时薪（元）
                 int minDays, int maxDays,
                 int[] unavailable,       // 不可用的日子（0 = 周一）
                 boolean noMorning,       // 不能上早班
                 double penaltyEvening,   // 每上一个晚班的“不喜欢”惩罚
                 double penaltyWeekend) {}  // 每上一个周末班的惩罚

    public static void main(String[] args) throws IOException {
        Fmt.useUtf8Output();
        final int D = 7, S = 2;  // 7 天，早 / 晚两班
        String[] dayName = {"周一", "周二", "周三", "周四", "周五", "周六", "周日"};
        String[] shiftName = {"早", "晚"};
        final double hoursPerShift = 8;
        // 每班需求人数 need[天][班]
        int[][] need = {{2, 2}, {2, 2}, {2, 2}, {2, 2}, {2, 3}, {3, 3}, {3, 3}};

        List<Staff> staff = List.of(
            //        姓名    id       全职   老员工 店长   时薪  天数   不可用                不上早 晚班罚 周末罚
            new Staff("小王", "wang",  true,  true,  true,  32, 4, 5, new int[] {},           false, 0,  40),
            new Staff("小李", "li",    true,  true,  false, 28, 4, 5, new int[] {},           false, 0,  0),
            new Staff("小张", "zhang", true,  true,  false, 26, 4, 5, new int[] {2},          false, 30, 0),
            new Staff("小陈", "chen",  true,  true,  false, 26, 4, 5, new int[] {},           false, 0,  20),
            new Staff("小刘", "liu",   false, false, false, 20, 2, 4, new int[] {0, 1, 2, 3}, false, 0,  0),
            new Staff("小赵", "zhao",  false, false, false, 20, 2, 4, new int[] {},           true,  0,  0),
            new Staff("小周", "zhou",  false, false, false, 21, 2, 4, new int[] {2, 3},       false, 15, 0),
            new Staff("小孙", "sun",   false, false, false, 19, 2, 4, new int[] {0},          false, 0,  25));
        final int E = staff.size();

        Model m = new Model();
        Var[][][] x = new Var[E][D][S];
        LinExpr cost = new LinExpr();
        for (int e = 0; e < E; ++e)
            for (int d = 0; d < D; ++d)
                for (int s = 0; s < S; ++s) {
                    Staff st = staff.get(e);
                    boolean off = false;
                    for (int u : st.unavailable()) off |= (u == d);
                    if (st.noMorning() && s == 0) off = true;
                    // 规则 6：不可用 → 上界设为 0（变量被固定，求解时自动去掉）
                    x[e][d][s] = m.addVar(0, off ? 0 : 1, VarType.BINARY, st.id() + "_d" + (d + 1) + (s == 0 ? "_am" : "_pm"));
                    double c = st.wage() * hoursPerShift;
                    if (s == 1) c += st.penaltyEvening();
                    if (d >= 5) c += st.penaltyWeekend();
                    cost = cost.plus(c, x[e][d][s]);
                }

        for (int d = 0; d < D; ++d)
            for (int s = 0; s < S; ++s) {
                String tag = "_d" + (d + 1) + (s == 0 ? "_am" : "_pm");
                LinExpr all = new LinExpr(), seniors = new LinExpr();
                for (int e = 0; e < E; ++e) {
                    all = all.plus(x[e][d][s]);
                    if (staff.get(e).senior()) seniors = seniors.plus(x[e][d][s]);
                }
                m.addConstr(all.ge(need[d][s]), "cover" + tag);  // 规则 1
                m.addConstr(seniors.ge(1), "senior" + tag);      // 规则 2
            }

        for (int e = 0; e < E; ++e) {
            Staff st = staff.get(e);
            LinExpr days = new LinExpr(), weekend = new LinExpr();
            for (int d = 0; d < D; ++d) {
                m.addConstr(LinExpr.of(x[e][d][0]).plus(x[e][d][1]).le(1), st.id() + "_one_d" + (d + 1));  // 规则 3
                if (d + 1 < D)  // 规则 4：晚班后不接早班
                    m.addConstr(LinExpr.of(x[e][d][1]).plus(x[e][d + 1][0]).le(1), st.id() + "_rest_d" + (d + 1));
                days = days.plus(x[e][d][0]).plus(x[e][d][1]);
                if (d >= 5) weekend = weekend.plus(x[e][d][0]).plus(x[e][d][1]);
            }
            for (int d = 0; d + 3 < D; ++d) {  // 规则 8：连续 4 天最多上 3 天
                LinExpr window = new LinExpr();
                for (int k = d; k < d + 4; ++k) window = window.plus(x[e][k][0]).plus(x[e][k][1]);
                m.addConstr(window.le(3), st.id() + "_streak_d" + (d + 1));
            }
            m.addConstr(days.ge(st.minDays()), st.id() + "_mindays");  // 规则 5
            m.addConstr(days.le(st.maxDays()), st.id() + "_maxdays");
            if (st.fullTime() && !st.manager()) m.addConstr(weekend.le(1), st.id() + "_weekend");  // 规则 7
        }
        // 规则 9：新人（小刘=4、小孙=7）上班时必须有师傅（小李=1 或小陈=3）在同一班
        for (int rookie : new int[] {4, 7})
            for (int d = 0; d < D; ++d)
                for (int s = 0; s < S; ++s)
                    m.addConstr(LinExpr.of(x[rookie][d][s]).le(LinExpr.of(x[1][d][s]).plus(x[3][d][s])),
                                staff.get(rookie).id() + "_mentor_d" + (d + 1) + (s == 1 ? "_pm" : "_am"));
        // 规则 10：小王（0）和小张（2）不排同一个班
        for (int d = 0; d < D; ++d)
            for (int s = 0; s < S; ++s)
                m.addConstr(LinExpr.of(x[0][d][s]).plus(x[2][d][s]).le(1), "apart_d" + (d + 1) + (s == 1 ? "_pm" : "_am"));

        m.setObjective(cost, ObjSense.MINIMIZE);

        Files.writeString(Path.of("hard_staff_schedule.lp"), m.toLP(), StandardCharsets.UTF_8);
        System.out.printf("模型：%d 个变量（%d 个 0-1），%d 条约束%n%n", m.numVars(), m.numIntegers(), m.numConstrs());

        Params prm = new Params();
        prm.verbose = true;
        prm.logEvery = 200;
        Result r = Solver.solve(m, prm);
        if (!r.hasSolution) {
            System.out.printf("没有找到可行解：%s%n", r.status);
            System.exit(1);
        }

        System.out.printf("%n状态：%s   总成本：%.0f 元   节点：%d   用时：%.2f 秒%n%n", r.status, r.objective, r.nodes,
                          r.seconds);
        System.out.printf("排班表（早 / 晚 / 休）%n");
        System.out.printf("员工     ");
        for (int d = 0; d < D; ++d) System.out.printf("%s  ", dayName[d]);
        System.out.printf("天数   工资%n");
        double wages = 0;
        for (int e = 0; e < E; ++e) {
            Staff st = staff.get(e);
            System.out.printf("%s%s  ", st.name(), st.senior() ? "★" : "  ");
            int days = 0;
            for (int d = 0; d < D; ++d) {
                String c = "休";
                for (int s = 0; s < S; ++s)
                    if (r.value(x[e][d][s]) > 0.5) { c = shiftName[s]; ++days; }
                System.out.printf("  %s  ", c);
            }
            double w = days * hoursPerShift * st.wage();
            wages += w;
            System.out.printf("%4d %6.0f%n", days, w);
        }
        System.out.printf("%n每班人数（实际/需求）%n");
        for (int s = 0; s < S; ++s) {
            System.out.printf("%s班      ", shiftName[s]);
            for (int d = 0; d < D; ++d) {
                int k = 0;
                for (int e = 0; e < E; ++e) if (r.value(x[e][d][s]) > 0.5) ++k;
                System.out.printf(" %d/%d  ", k, need[d][s]);
            }
            System.out.printf("%n");
        }
        System.out.printf("%n工资 %.0f 元 + 偏好惩罚 %.0f = 目标值 %.0f%n", wages, r.objective - wages, r.objective);
        System.out.printf("★ = 老员工    可行性自检：%s%n", Solver.checkFeasible(m, r.x) ? "通过" : "失败");
    }
}
