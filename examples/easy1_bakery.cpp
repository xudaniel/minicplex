// 简单例子 1：线性规划（LP）—— 面包店生产计划
//
// 面包店每天做蛋糕和面包：
//   蛋糕：每个利润 5 元，用面粉 6 kg、人工 1 小时
//   面包：每个利润 4 元，用面粉 4 kg、人工 2 小时
//   每天最多 24 kg 面粉、6 小时人工
// 问：各做多少，利润最大？（这里允许做半个，所以是连续变量）
#include <iostream>

#include "solver.hpp"

using namespace mcplex;

int main() {
    Model m;

    // 1. 决策变量：做多少个（>= 0，连续）
    Var cake = m.addVar(0, INF, VarType::Continuous, "cake");
    Var bread = m.addVar(0, INF, VarType::Continuous, "bread");

    // 2. 约束
    m.addConstr(6 * cake + 4 * bread <= 24, "flour");  // 面粉
    m.addConstr(1 * cake + 2 * bread <= 6, "labor");   // 人工

    // 3. 目标：利润最大
    m.setObjective(5 * cake + 4 * bread, ObjSense::Maximize);

    // 4. 求解
    Result r = solve(m);

    std::cout << "状态：" << toString(r.status) << '\n'
              << "最大利润：" << r.objective << " 元\n"
              << "蛋糕：" << r.x[cake.id] << " 个\n"
              << "面包：" << r.x[bread.id] << " 个\n";
}
