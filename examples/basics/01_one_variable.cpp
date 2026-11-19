// 入门例子 01：只有一个变量
//
// 问题：你有 10 元，苹果 2 元一个。最多能买几个苹果？
// 答案一眼就能看出是 5 个。这个例子只为了认识最基本的四个步骤。
//
// 运行：./build/basics_01_one_variable            （加 --trace 可以看到求解过程）
#include <iostream>
#include <string>

#include "solver.hpp"  // minicplex 的全部功能都在这个头文件里

using namespace mcplex;

int main(int argc, char** argv) {
    // 第 1 步：建一个空模型
    Model m;

    // 第 2 步：建变量。apples = 买几个苹果，最少 0 个，没有上限
    Var apples = m.addVar(0, INF, VarType::Continuous, "apples");

    // 第 3 步：加限制。花的钱不能超过 10 元：2 × 苹果数 ≤ 10
    m.addConstr(2 * apples <= 10, "money");

    // 第 4 步：定目标。苹果越多越好：最大化 苹果数
    m.setObjective(apples, ObjSense::Maximize);

    // 求解
    Params p;
    p.trace = argc > 1 && std::string(argv[1]) == "--trace";
    Result r = solve(m, p);

    std::cout << "状态：" << toString(r.status) << "\n";  // Optimal = 找到了最优解
    std::cout << "最多买 " << r.x[apples.id] << " 个苹果\n";
}
