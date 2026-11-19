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
#include <cstdio>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

#include "solver.hpp"

using namespace mcplex;

struct Staff {
    std::string name, id;
    bool fullTime, senior, manager;
    double wage;                 // 时薪（元）
    int minDays, maxDays;
    std::vector<int> unavailable;  // 不可用的日子（0 = 周一）
    bool noMorning;              // 不能上早班
    double penaltyEvening;       // 每上一个晚班的“不喜欢”惩罚
    double penaltyWeekend;       // 每上一个周末班的惩罚
};

int main() {
    const int D = 7, S = 2;  // 7 天，早 / 晚两班
    const char* dayName[D] = {"周一", "周二", "周三", "周四", "周五", "周六", "周日"};
    const char* shiftName[S] = {"早", "晚"};
    const double hoursPerShift = 8;
    // 每班需求人数 need[天][班]
    const int need[D][S] = {{2, 2}, {2, 2}, {2, 2}, {2, 2}, {2, 3}, {3, 3}, {3, 3}};

    const std::vector<Staff> staff = {
        //  姓名    id        全职   老员工 店长   时薪  天数    不可用   不上早 晚班罚 周末罚
        {"小王", "wang",  true,  true,  true,  32, 4, 5, {},        false, 0,  40},
        {"小李", "li",    true,  true,  false, 28, 4, 5, {},        false, 0,  0},
        {"小张", "zhang", true,  true,  false, 26, 4, 5, {2},       false, 30, 0},
        {"小陈", "chen",  true,  true,  false, 26, 4, 5, {},        false, 0,  20},
        {"小刘", "liu",   false, false, false, 20, 2, 4, {0, 1, 2, 3}, false, 0, 0},
        {"小赵", "zhao",  false, false, false, 20, 2, 4, {},        true,  0,  0},
        {"小周", "zhou",  false, false, false, 21, 2, 4, {2, 3},    false, 15, 0},
        {"小孙", "sun",   false, false, false, 19, 2, 4, {0},       false, 0,  25},
    };
    const int E = static_cast<int>(staff.size());

    Model m;
    std::vector<std::vector<std::vector<Var>>> x(E, std::vector<std::vector<Var>>(D, std::vector<Var>(S)));
    LinExpr cost;
    for (int e = 0; e < E; ++e)
        for (int d = 0; d < D; ++d)
            for (int s = 0; s < S; ++s) {
                const Staff& st = staff[e];
                bool off = false;
                for (int u : st.unavailable) off |= (u == d);
                if (st.noMorning && s == 0) off = true;
                // 规则 6：不可用 → 上界设为 0（变量被固定，求解时自动去掉）
                x[e][d][s] = m.addVar(0, off ? 0 : 1, VarType::Binary,
                                      st.id + "_d" + std::to_string(d + 1) + (s == 0 ? "_am" : "_pm"));
                double c = st.wage * hoursPerShift;
                if (s == 1) c += st.penaltyEvening;
                if (d >= 5) c += st.penaltyWeekend;
                cost += c * x[e][d][s];
            }

    for (int d = 0; d < D; ++d)
        for (int s = 0; s < S; ++s) {
            const std::string tag = std::string("_d") + std::to_string(d + 1) + (s == 0 ? "_am" : "_pm");
            LinExpr all, seniors;
            for (int e = 0; e < E; ++e) {
                all += x[e][d][s];
                if (staff[e].senior) seniors += x[e][d][s];
            }
            m.addConstr(all >= need[d][s], "cover" + tag);   // 规则 1
            m.addConstr(seniors >= 1, "senior" + tag);       // 规则 2
        }

    for (int e = 0; e < E; ++e) {
        const Staff& st = staff[e];
        LinExpr days, weekend;
        for (int d = 0; d < D; ++d) {
            m.addConstr(x[e][d][0] + x[e][d][1] <= 1, st.id + "_one_d" + std::to_string(d + 1));  // 规则 3
            if (d + 1 < D)  // 规则 4：晚班后不接早班
                m.addConstr(x[e][d][1] + x[e][d + 1][0] <= 1, st.id + "_rest_d" + std::to_string(d + 1));
            days += x[e][d][0] + x[e][d][1];
            if (d >= 5) weekend += x[e][d][0] + x[e][d][1];
        }
        for (int d = 0; d + 3 < D; ++d) {  // 规则 8：连续 4 天最多上 3 天
            LinExpr window;
            for (int k = d; k < d + 4; ++k) window += x[e][k][0] + x[e][k][1];
            m.addConstr(window <= 3, st.id + "_streak_d" + std::to_string(d + 1));
        }
        m.addConstr(days >= st.minDays, st.id + "_mindays");  // 规则 5
        m.addConstr(days <= st.maxDays, st.id + "_maxdays");
        if (st.fullTime && !st.manager) m.addConstr(weekend <= 1, st.id + "_weekend");  // 规则 7
    }
    // 规则 9：新人（小刘=4、小孙=7）上班时必须有师傅（小李=1 或小陈=3）在同一班
    for (int rookie : {4, 7})
        for (int d = 0; d < D; ++d)
            for (int s = 0; s < S; ++s)
                m.addConstr(x[rookie][d][s] <= x[1][d][s] + x[3][d][s],
                            staff[rookie].id + "_mentor_d" + std::to_string(d + 1) + (s ? "_pm" : "_am"));
    // 规则 10：小王（0）和小张（2）不排同一个班
    for (int d = 0; d < D; ++d)
        for (int s = 0; s < S; ++s)
            m.addConstr(x[0][d][s] + x[2][d][s] <= 1, "apart_d" + std::to_string(d + 1) + (s ? "_pm" : "_am"));

    m.setObjective(cost, ObjSense::Minimize);

    {
        std::ofstream out("hard_staff_schedule.lp");
        m.writeLP(out);
    }
    std::printf("模型：%d 个变量（%d 个 0-1），%d 条约束\n\n", m.numVars(), m.numIntegers(), m.numConstrs());

    Params prm;
    prm.verbose = true;
    prm.logEvery = 200;
    Result r = solve(m, prm);
    if (!r.hasSolution) {
        std::printf("没有找到可行解：%s\n", toString(r.status));
        return 1;
    }
    auto on = [&](int e, int d, int s) { return r.x[x[e][d][s].id] > 0.5; };

    std::printf("\n状态：%s   总成本：%.0f 元   节点：%ld   用时：%.2f 秒\n\n", toString(r.status),
                r.objective, r.nodes, r.seconds);
    std::printf("排班表（早 / 晚 / 休）\n");
    std::printf("员工     ");
    for (int d = 0; d < D; ++d) std::printf("%s  ", dayName[d]);
    std::printf("天数   工资\n");
    double wages = 0;
    for (int e = 0; e < E; ++e) {
        std::printf("%s%s  ", staff[e].name.c_str(), staff[e].senior ? "★" : "  ");
        int days = 0;
        for (int d = 0; d < D; ++d) {
            const char* c = "休";
            for (int s = 0; s < S; ++s)
                if (on(e, d, s)) { c = shiftName[s]; ++days; }
            std::printf("  %s  ", c);
        }
        const double w = days * hoursPerShift * staff[e].wage;
        wages += w;
        std::printf("%4d %6.0f\n", days, w);
    }
    std::printf("\n每班人数（实际/需求）\n");
    for (int s = 0; s < S; ++s) {
        std::printf("%s班      ", shiftName[s]);
        for (int d = 0; d < D; ++d) {
            int k = 0;
            for (int e = 0; e < E; ++e) k += on(e, d, s);
            std::printf(" %d/%d  ", k, need[d][s]);
        }
        std::printf("\n");
    }
    std::printf("\n工资 %.0f 元 + 偏好惩罚 %.0f = 目标值 %.0f\n", wages, r.objective - wages, r.objective);
    std::printf("★ = 老员工    可行性自检：%s\n", checkFeasible(m, r.x) ? "通过" : "失败");
}
