// 入门例子 02：两个变量、两条限制
//
// 问题：去水果店，苹果 2 元一个，香蕉 1 元一个。
//   - 你有 10 元
//   - 袋子最多装 7 个水果
//   - 你给每个苹果打 3 分（好吃），每根香蕉打 2 分
// 怎么买，总分最高？
#include <iostream>

#include "solver.hpp"

using namespace mcplex;

int main() {
    Model m;
    Var apple = m.addVar(0, INF, VarType::Continuous, "apple");
    Var banana = m.addVar(0, INF, VarType::Continuous, "banana");

    m.addConstr(2 * apple + 1 * banana <= 10, "money");  // 钱：2×苹果 + 1×香蕉 ≤ 10
    m.addConstr(apple + banana <= 7, "bag");              // 袋子：苹果 + 香蕉 ≤ 7

    m.setObjective(3 * apple + 2 * banana, ObjSense::Maximize);  // 总分 = 3×苹果 + 2×香蕉

    Result r = solve(m);
    std::cout << "苹果 " << r.x[apple.id] << " 个，香蕉 " << r.x[banana.id] << " 根，总分 " << r.objective << "\n";

    // 两条限制都刚好用满吗？算一算：
    std::cout << "花钱 " << 2 * r.x[apple.id] + r.x[banana.id] << " 元（上限 10），"
              << "装了 " << r.x[apple.id] + r.x[banana.id] << " 个（上限 7）\n";
}
