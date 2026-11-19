// 入门例子 05：求最小（花最少的钱）
//
// 问题：每天要喝牛奶、吃鸡蛋来补充营养，至少需要：
//   - 蛋白质 30 克
//   - 钙 600 毫克
//            价格   蛋白质   钙
//   一杯牛奶  3 元    8 克   300 毫克
//   一个鸡蛋  1 元    6 克    30 毫克
// 牛奶按杯、鸡蛋按个，都必须是整数。怎么搭配最省钱？
#include <iostream>

#include "solver.hpp"

using namespace mcplex;

int main() {
    Model m;
    Var milk = m.addVar(0, INF, VarType::Integer, "milk");
    Var egg = m.addVar(0, INF, VarType::Integer, "egg");

    // “至少”用 >=
    m.addConstr(8 * milk + 6 * egg >= 30, "protein");
    m.addConstr(300 * milk + 30 * egg >= 600, "calcium");

    // 目标是花钱最少：Minimize
    m.setObjective(3 * milk + 1 * egg, ObjSense::Minimize);

    Result r = solve(m);
    const double mk = r.x[milk.id], eg = r.x[egg.id];
    std::cout << "牛奶 " << mk << " 杯，鸡蛋 " << eg << " 个，花 " << r.objective << " 元\n";
    std::cout << "蛋白质 " << 8 * mk + 6 * eg << " 克（至少 30），钙 " << 300 * mk + 30 * eg << " 毫克（至少 600）\n";
}
