// 进阶例子 06：影子价格——多一份资源值多少钱？
//
// 还是面包店（允许做半个）：蛋糕赚 5 元，面包赚 4 元；面粉 24 公斤，人工 6 小时。
// 老板想知道：如果能多买 1 公斤面粉，或者多请 1 小时人工，最多值得花多少钱？
//
// 答案就是每条限制的“影子价格”（对偶值）：右边多 1 个单位，最优利润能多多少。
#include <cstdio>

#include "solver.hpp"

using namespace mcplex;

static double bestProfit(double flour, double labor) {
    Model m;
    Var cake = m.addVar(0, INF, VarType::Continuous, "cake");
    Var bread = m.addVar(0, INF, VarType::Continuous, "bread");
    m.addConstr(6 * cake + 4 * bread <= flour, "flour");
    m.addConstr(1 * cake + 2 * bread <= labor, "labor");
    m.setObjective(5 * cake + 4 * bread, ObjSense::Maximize);
    return solve(m).objective;
}

int main() {
    Model m;
    Var cake = m.addVar(0, INF, VarType::Continuous, "cake");
    Var bread = m.addVar(0, INF, VarType::Continuous, "bread");
    m.addConstr(6 * cake + 4 * bread <= 24, "flour");
    m.addConstr(1 * cake + 2 * bread <= 6, "labor");
    m.setObjective(5 * cake + 4 * bread, ObjSense::Maximize);
    Result r = solve(m);

    // r.duals[i] 就是第 i 条限制的影子价格（只有线性规划才有）
    std::printf("最大利润 %.2f 元\n", r.objective);
    std::printf("面粉的影子价格：%.2f 元/公斤\n", r.duals[0]);
    std::printf("人工的影子价格：%.2f 元/小时\n\n", r.duals[1]);

    // 验证：真的多给 1 份资源，重新算一遍
    std::printf("面粉 25 公斤：利润 %.2f 元（多了 %.2f）\n", bestProfit(25, 6), bestProfit(25, 6) - r.objective);
    std::printf("人工 7 小时： 利润 %.2f 元（多了 %.2f）\n\n", bestProfit(24, 7), bestProfit(24, 7) - r.objective);

    // 注意：影子价格只在一定范围内有效。多 20 公斤面粉，并不能多赚 20 × 0.75 = 15 元，
    // 因为人工很快变成瓶颈了。
    std::printf("面粉 44 公斤：利润 %.2f 元（按影子价格估算是 %.2f）\n", bestProfit(44, 6),
                r.objective + 20 * r.duals[0]);
}
