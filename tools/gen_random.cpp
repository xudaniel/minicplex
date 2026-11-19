// 随机模型生成器：批量生成 .lp 文件，用于对拍（与 HiGHS 比对）和基准测试。
//
// 用法：
//   minicplex_gen --kind mixed --count 300 --seed 1 --out fuzz/
//   minicplex_gen --kind mkp   --count 3   --seed 7 --vars 35 --cons 5   --out bench/models/
//   minicplex_gen --kind lp    --count 2   --seed 9 --vars 120 --cons 100 --out bench/models/
//
// 模型种类：
//   mixed  小型混合整数题：连续 / 整数 / 0-1 变量，负边界、自由变量，<=、>=、= 约束，
//          最小化或最大化；大多可行，也会刻意生成一些不可行或无界的题。
//   mkp    多维 0-1 背包（分支定界压力测试）
//   lp     较大的纯线性规划（单纯形速度测试）
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <random>
#include <string>

#include "model.hpp"

using namespace mcplex;

namespace {

std::mt19937 rng;
int ri(int a, int b) { return std::uniform_int_distribution<int>(a, b)(rng); }
double rr(double a, double b) { return std::uniform_real_distribution<double>(a, b)(rng); }
bool coin(double p) { return rr(0, 1) < p; }

Model genMixed(int nMax, int mMax) {
    Model M;
    const int n = ri(2, nMax), m = ri(1, mMax);
    std::vector<double> x0(n);
    for (int j = 0; j < n; ++j) {
        const double t = rr(0, 1);
        VarType type = t < 0.40 ? VarType::Integer : t < 0.55 ? VarType::Binary : VarType::Continuous;
        double lb = coin(0.6) ? 0.0 : coin(0.75) ? -ri(1, 5) : -INF;
        double ub = coin(0.8) ? (std::isfinite(lb) ? lb : 0.0) + ri(1, 10) : INF;
        if (type == VarType::Binary) { lb = 0; ub = 1; }
        M.addVar(lb, ub, type, "x" + std::to_string(j + 1));
        const double lo = std::isfinite(lb) ? lb : (std::isfinite(ub) ? ub - 5 : -3);
        const double hi = std::isfinite(ub) ? ub : lo + 5;
        x0[j] = rr(lo, hi);
        if (type != VarType::Continuous) x0[j] = std::round(x0[j]);
        x0[j] = std::min(std::max(x0[j], lb), ub);
    }
    for (int i = 0; i < m; ++i) {
        LinExpr e;
        double act = 0;
        for (int j = 0; j < n; ++j) {
            if (!coin(0.6)) continue;
            double a = ri(-6, 6);
            if (coin(0.3)) a += 0.5;
            if (a == 0) continue;
            e += a * Var{j};
            act += a * x0[j];
        }
        const int s = ri(0, 2);
        double rhs = std::round(act);
        if (coin(0.1)) rhs = ri(-10, 10);  // 可能不可行
        if (s == 0) M.addConstr(e <= (coin(0.9) ? std::ceil(act) + ri(0, 4) : rhs));
        else if (s == 1) M.addConstr(e >= (coin(0.9) ? std::floor(act) - ri(0, 4) : rhs));
        else M.addConstr(e == (coin(0.9) ? act : rhs));
    }
    LinExpr obj;
    for (int j = 0; j < n; ++j) obj += ri(-5, 5) * Var{j};
    if (coin(0.2)) obj += ri(-20, 20);
    M.setObjective(obj, coin(0.5) ? ObjSense::Maximize : ObjSense::Minimize);
    return M;
}

Model genMkp(int n, int m) {
    Model M;
    std::vector<Var> x;
    for (int j = 0; j < n; ++j) x.push_back(M.addVar(0, 1, VarType::Binary, "x" + std::to_string(j + 1)));
    std::vector<double> avgW(n, 0);
    for (int i = 0; i < m; ++i) {
        LinExpr e;
        double total = 0;
        for (int j = 0; j < n; ++j) {
            const double w = ri(5, 40);
            e += w * x[j];
            total += w;
            avgW[j] += w / m;
        }
        M.addConstr(e <= std::floor(0.5 * total), "cap" + std::to_string(i + 1));
    }
    LinExpr obj;
    for (int j = 0; j < n; ++j) obj += std::round(avgW[j] + ri(0, 10)) * x[j];
    M.setObjective(obj, ObjSense::Maximize);
    return M;
}

Model genLp(int n, int m) {
    Model M;
    std::vector<double> x0(n);
    for (int j = 0; j < n; ++j) {
        const double lb = coin(0.8) ? 0.0 : -ri(1, 20);
        const double ub = lb + ri(5, 50);
        M.addVar(lb, ub, VarType::Continuous, "x" + std::to_string(j + 1));
        x0[j] = rr(lb, ub);
    }
    for (int i = 0; i < m; ++i) {
        LinExpr e;
        double act = 0;
        for (int j = 0; j < n; ++j) {
            if (!coin(0.3)) continue;
            const double a = ri(-10, 10);
            e += a * Var{j};
            act += a * x0[j];
        }
        const int s = ri(0, 9);
        if (s < 5) M.addConstr(e <= std::round(act + ri(0, 20)));
        else if (s < 9) M.addConstr(e >= std::round(act - ri(0, 20)));
        else M.addConstr(e == std::round(act));
    }
    LinExpr obj;
    for (int j = 0; j < n; ++j) obj += ri(-10, 10) * Var{j};
    M.setObjective(obj, coin(0.5) ? ObjSense::Maximize : ObjSense::Minimize);
    return M;
}

}  // namespace

int main(int argc, char** argv) {
    std::string kind = "mixed", out = ".";
    int count = 100, seed = 1, vars = -1, cons = -1;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        auto next = [&]() -> std::string {
            if (i + 1 >= argc) { std::fprintf(stderr, "missing value for %s\n", a.c_str()); std::exit(2); }
            return argv[++i];
        };
        if (a == "--kind") kind = next();
        else if (a == "--count") count = std::stoi(next());
        else if (a == "--seed") seed = std::stoi(next());
        else if (a == "--vars") vars = std::stoi(next());
        else if (a == "--cons") cons = std::stoi(next());
        else if (a == "--out") out = next();
        else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); return 2; }
    }
    rng.seed(seed);
    std::filesystem::create_directories(out);
    for (int k = 0; k < count; ++k) {
        Model M;
        if (kind == "mixed") M = genMixed(vars > 0 ? vars : 12, cons > 0 ? cons : 10);
        else if (kind == "mkp") M = genMkp(vars > 0 ? vars : 35, cons > 0 ? cons : 5);
        else if (kind == "lp") M = genLp(vars > 0 ? vars : 120, cons > 0 ? cons : 100);
        else { std::fprintf(stderr, "unknown kind %s\n", kind.c_str()); return 2; }
        char name[256];
        std::snprintf(name, sizeof name, "%s/%s_s%d_%04d.lp", out.c_str(), kind.c_str(), seed, k);
        std::ofstream f(name);
        M.writeLP(f);
    }
    std::printf("generated %d %s models in %s\n", count, kind.c_str(), out.c_str());
}
