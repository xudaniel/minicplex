// 进阶例子 09：绝对值——选址让总距离最短
//
// 一条路上有 5 户人家，位置分别是 1、3、8、10、20（公里）。
// 要在路上建一个快递点，让它到所有人家的距离之和最小。建在哪里？
//
// 技巧：距离是绝对值 |x − 位置|，不能直接写成线性限制。为每户人家新建一个变量 d，
// 要求  d ≥ x − 位置  并且  d ≥ 位置 − x，然后最小化所有 d 的和。
// 求最小时，d 会自动被压到两者中较大的那个，也就是绝对值。
#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

#include "solver.hpp"

using namespace mcplex;

int main() {
    const std::vector<double> home = {1, 3, 8, 10, 20};

    Model m;
    Var x = m.addVar(-INF, INF, VarType::Continuous, "x");  // 快递点位置
    LinExpr total;
    std::vector<Var> d;
    for (size_t i = 0; i < home.size(); ++i) {
        d.push_back(m.addVar(0, INF, VarType::Continuous, "d" + std::to_string(i)));  // 到第 i 户的距离
        m.addConstr(d[i] >= x - home[i], "right" + std::to_string(i));
        m.addConstr(d[i] >= home[i] - x, "left" + std::to_string(i));
        total += d[i];
    }
    m.setObjective(total, ObjSense::Minimize);

    Result r = solve(m);
    std::printf("快递点建在 %.0f 公里处，总距离 %.0f 公里\n", r.x[x.id], r.objective);
    for (size_t i = 0; i < home.size(); ++i)
        std::printf("  到位置 %2.0f 的人家：%.0f 公里\n", home[i], r.x[d[i].id]);
    // 对比：如果建在平均位置（很多人的第一反应），总距离是多少？
    double mean = 0, distMean = 0;
    for (double h : home) mean += h / home.size();
    for (double h : home) distMean += std::abs(h - mean);
    std::printf("对比：建在平均位置 %.1f，总距离 %.1f 公里，反而更远。最优位置是中位数，不是平均数。\n", mean,
                distMean);
}
