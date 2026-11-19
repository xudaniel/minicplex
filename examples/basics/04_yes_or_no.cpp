// 入门例子 04：选或不选（0-1 变量）
//
// 问题：周末有 8 小时空闲，有 4 件想做的事：
//   事情      用时    开心值
//   看电影    3 小时    6
//   爬山      5 小时    9
//   吃大餐    2 小时    4
//   读书      4 小时    5
// 规则：爬山和读书不能都选（太累）。选哪几件最开心？
#include <iostream>
#include <string>
#include <vector>

#include "solver.hpp"

using namespace mcplex;

int main() {
    const std::vector<std::string> name = {"看电影", "爬山", "吃大餐", "读书"};
    const std::vector<double> hours = {3, 5, 2, 4};
    const std::vector<double> happy = {6, 9, 4, 5};

    Model m;
    std::vector<Var> pick;
    LinExpr time, fun;
    for (size_t i = 0; i < name.size(); ++i) {
        // VarType::Binary：只能取 0（不选）或 1（选）
        pick.push_back(m.addVar(0, 1, VarType::Binary, "pick" + std::to_string(i)));
        time += hours[i] * pick[i];  // 总用时 = Σ 用时 × 选没选
        fun += happy[i] * pick[i];   // 总开心值
    }
    m.addConstr(time <= 8, "hours");                 // 时间不超过 8 小时
    m.addConstr(pick[1] + pick[3] <= 1, "not_both");  // 爬山 + 读书 ≤ 1：最多选其中一个
    m.setObjective(fun, ObjSense::Maximize);

    Result r = solve(m);
    std::cout << "选：";
    for (size_t i = 0; i < name.size(); ++i)
        if (r.x[pick[i].id] > 0.5) std::cout << name[i] << " ";
    std::cout << "\n开心值 " << r.objective << "\n";
}
