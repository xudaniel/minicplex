// 入门例子 03：必须是整数
//
// 问题（面包店）：蛋糕每个赚 5 元，面包每个赚 4 元。
//   - 面粉只有 24 公斤：蛋糕用 6 公斤，面包用 4 公斤
//   - 人工只有 6 小时：蛋糕用 1 小时，面包用 2 小时
// 不能卖半个，怎么做最赚钱？
//
// 这个例子会算两遍：先允许做半个，再要求整数，看看有什么不同。
#include <cmath>
#include <iostream>

#include "solver.hpp"

using namespace mcplex;

int main() {
    Model m;
    // VarType::Integer 表示“必须是整数”
    Var cake = m.addVar(0, INF, VarType::Integer, "cake");
    Var bread = m.addVar(0, INF, VarType::Integer, "bread");
    m.addConstr(6 * cake + 4 * bread <= 24, "flour");
    m.addConstr(1 * cake + 2 * bread <= 6, "labor");
    m.setObjective(5 * cake + 4 * bread, ObjSense::Maximize);

    // 第一遍：暂时忽略“必须是整数”（relaxIntegrality = 放松整数要求）
    Params relaxed;
    relaxed.relaxIntegrality = true;
    Result a = solve(m, relaxed);
    std::cout << "允许做半个：蛋糕 " << a.x[cake.id] << "，面包 " << a.x[bread.id] << "，赚 " << a.objective << " 元\n";

    // 很多人会想：把小数部分去掉不就行了？
    const double c = std::floor(a.x[cake.id]), b = std::floor(a.x[bread.id]);
    std::cout << "直接去掉小数：蛋糕 " << c << "，面包 " << b << "，赚 " << 5 * c + 4 * b << " 元\n";

    // 第二遍：真正的整数规划
    Result r = solve(m);
    std::cout << "整数最优解：  蛋糕 " << r.x[cake.id] << "，面包 " << r.x[bread.id] << "，赚 " << r.objective << " 元\n";
    std::cout << "结论：整数最优解不是“去掉小数”那么简单，需要分支定界来找。\n";
}
