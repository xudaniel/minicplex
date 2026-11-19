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
#include <iostream>
#include <vector>

#include "solver.hpp"

using namespace mcplex;

int main() {
    const std::vector<std::string> name = {"A", "B", "C", "D"};
    const std::vector<double> cost = {5, 4, 3, 2};
    const std::vector<double> gain = {8, 7, 4, 4};

    Model m;
    std::vector<Var> pick;
    LinExpr totalCost, totalGain;
    for (size_t i = 0; i < name.size(); ++i) {
        // 0-1 变量：1 = 投，0 = 不投
        Var v = m.addVar(0, 1, VarType::Binary, name[i]);
        pick.push_back(v);
        totalCost += cost[i] * v;
        totalGain += gain[i] * v;
    }

    m.addConstr(totalCost <= 10, "budget");    // 预算
    m.addConstr(pick[2] <= pick[3], "C_needs_D");  // 投 C 必须投 D
    m.setObjective(totalGain, ObjSense::Maximize);

    Result r = solve(m);

    std::cout << "状态：" << toString(r.status) << '\n'
              << "最大收益：" << r.objective << " 万\n"
              << "投资项目：";
    for (size_t i = 0; i < name.size(); ++i)
        if (r.x[pick[i].id] > 0.5) std::cout << name[i] << ' ';
    std::cout << "\n分支定界节点数：" << r.nodes << '\n';
}
