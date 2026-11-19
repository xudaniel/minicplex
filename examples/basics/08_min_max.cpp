// 进阶例子 08：最小化最大值——公平分配
//
// 6 件任务分给 3 个人，用时分别是 5、4、3、3、2、1 小时。每件任务只给一个人。
// 目标：让最忙的那个人尽量不忙（所有人尽早一起下班）。
//
// 技巧：“最大值”不能直接写进目标。新建一个变量 T 表示“最忙的人的工作量”，
// 要求每个人的工作量都 ≤ T，然后最小化 T。最优时 T 就等于真正的最大值。
#include <cstdio>
#include <string>
#include <vector>

#include "solver.hpp"

using namespace mcplex;

int main() {
    const std::vector<double> hours = {5, 4, 3, 3, 2, 1};
    const int tasks = static_cast<int>(hours.size()), people = 3;

    Model m;
    // give[t][p] = 1 表示任务 t 交给第 p 个人
    std::vector<std::vector<Var>> give(tasks, std::vector<Var>(people));
    for (int t = 0; t < tasks; ++t)
        for (int p = 0; p < people; ++p)
            give[t][p] = m.addVar(0, 1, VarType::Binary, "give_" + std::to_string(t) + "_" + std::to_string(p));
    Var T = m.addVar(0, INF, VarType::Continuous, "T");  // 最忙的人的工作量

    for (int t = 0; t < tasks; ++t) {  // 每件任务正好给一个人
        LinExpr once;
        for (int p = 0; p < people; ++p) once += give[t][p];
        m.addConstr(once == 1, "task" + std::to_string(t));
    }
    for (int p = 0; p < people; ++p) {  // 每个人的工作量 ≤ T
        LinExpr load;
        for (int t = 0; t < tasks; ++t) load += hours[t] * give[t][p];
        m.addConstr(load <= T, "load" + std::to_string(p));
    }
    m.setObjective(T, ObjSense::Minimize);

    Result r = solve(m);
    std::printf("最忙的人工作 %.0f 小时\n", r.objective);
    for (int p = 0; p < people; ++p) {
        double load = 0;
        std::printf("第 %d 个人：", p + 1);
        for (int t = 0; t < tasks; ++t)
            if (r.x[give[t][p].id] > 0.5) {
                std::printf("%.0f 小时任务 ", hours[t]);
                load += hours[t];
            }
        std::printf("→ 共 %.0f 小时\n", load);
    }
}
