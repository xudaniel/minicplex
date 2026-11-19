// Best-first branch and bound on top of the simplex LP solver.
//   * branching variable: most fractional integer variable
//   * node selection: smallest LP bound first (ties: deepest first)
//   * primal heuristic: round the LP solution and test feasibility
//   * if the objective only involves integer variables with integer
//     coefficients, node bounds are rounded up (stronger pruning)

#include <chrono>
#include <cmath>
#include <cstdio>
#include <queue>

#include "solver.hpp"

namespace mcplex {

const char* toString(Status s) {
    switch (s) {
        case Status::Optimal: return "Optimal";
        case Status::Infeasible: return "Infeasible";
        case Status::Unbounded: return "Unbounded";
        case Status::InfeasibleOrUnbounded: return "InfeasibleOrUnbounded";
        case Status::NodeLimit: return "NodeLimit";
        case Status::TimeLimit: return "TimeLimit";
        case Status::IterationLimit: return "IterationLimit";
    }
    return "?";
}

double evalObjective(const Model& M, const std::vector<double>& x) {
    double v = M.objective.constant;
    for (const auto& [k, c] : M.objective.terms) v += c * x[k];
    return v;
}

bool checkFeasible(const Model& M, const std::vector<double>& x, double tol, bool checkInt) {
    for (int j = 0; j < M.numVars(); ++j) {
        const auto& v = M.vars[j];
        if (x[j] < v.lb - tol || x[j] > v.ub + tol) return false;
        if (checkInt && M.isInteger(j) && std::abs(x[j] - std::round(x[j])) > tol) return false;
    }
    for (const auto& c : M.constraints) {
        double lhs = 0.0;
        for (const auto& [k, a] : c.coefs) lhs += a * x[k];
        const double t = tol * (1.0 + std::abs(c.rhs));
        if (c.sense == Sense::LE && lhs > c.rhs + t) return false;
        if (c.sense == Sense::GE && lhs < c.rhs - t) return false;
        if (c.sense == Sense::EQ && std::abs(lhs - c.rhs) > t) return false;
    }
    return true;
}

namespace {

struct Node {
    std::vector<double> lb, ub;
    double bound;  // lower bound (internal min sense) inherited from the parent
    int depth;
};

struct NodeCmp {
    bool operator()(const Node& a, const Node& b) const {
        if (a.bound != b.bound) return a.bound > b.bound;
        return a.depth < b.depth;
    }
};

}  // namespace

Result solve(const Model& M, const Params& P) {
    using clock = std::chrono::steady_clock;
    const auto t0 = clock::now();
    auto elapsed = [&] { return std::chrono::duration<double>(clock::now() - t0).count(); };

    Result R;
    const int nv = M.numVars();
    const double sgn = (M.objSense == ObjSense::Maximize) ? -1.0 : 1.0;
    const long maxIt = 200000 + 50L * (nv + M.numConstrs());

    std::vector<double> lb(nv), ub(nv);
    std::vector<int> ints;
    for (int j = 0; j < nv; ++j) {
        lb[j] = M.vars[j].lb;
        ub[j] = M.vars[j].ub;
        if (!P.relaxIntegrality && M.isInteger(j)) {
            ints.push_back(j);
            if (std::isfinite(lb[j])) lb[j] = std::ceil(lb[j] - P.intTol);
            if (std::isfinite(ub[j])) ub[j] = std::floor(ub[j] + P.intTol);
        }
    }

    // ---------------- pure LP ----------------
    if (ints.empty()) {
        auto lp = detail::lpMin(M, lb, ub, sgn, maxIt);
        R.lpIterations = lp.iterations;
        R.seconds = elapsed();
        switch (lp.status) {
            case detail::LPStatus::Optimal:
                R.status = Status::Optimal;
                R.hasSolution = true;
                R.x = lp.x;
                R.objective = R.bestBound = sgn * lp.objective;
                R.gap = 0.0;
                break;
            case detail::LPStatus::Infeasible: R.status = Status::Infeasible; break;
            case detail::LPStatus::Unbounded: R.status = Status::Unbounded; break;
            case detail::LPStatus::IterationLimit: R.status = Status::IterationLimit; break;
        }
        if (P.verbose)
            std::printf("LP solved: %s, %ld simplex iterations, %.3f s\n", toString(R.status),
                        R.lpIterations, R.seconds);
        return R;
    }

    // ---------------- MIP: branch and bound ----------------
    bool objIntegral = true;
    for (const auto& [k, c] : M.objective.terms)
        if (c != 0.0 && (!M.isInteger(k) || c != std::round(c))) objIntegral = false;
    const double objConst = sgn * M.objective.constant;
    auto strengthen = [&](double b) {
        if (!objIntegral || !std::isfinite(b)) return b;
        return std::ceil(b - objConst - 1e-6) + objConst;
    };
    auto closeEnough = [&](double bound, double inc) {
        return inc - bound <= P.mipGap * std::max(1.0, std::abs(inc));
    };

    double inc = INF;  // incumbent, internal min sense
    std::vector<double> incX;
    bool incomplete = false;
    Status stop = Status::Optimal;

    auto tryIncumbent = [&](std::vector<double> x) {
        for (int j : ints) x[j] = std::round(x[j]);
        if (!checkFeasible(M, x, 1e-6)) return false;
        const double v = sgn * evalObjective(M, x);
        if (v < inc - 1e-12) {
            inc = v;
            incX = std::move(x);
            return true;
        }
        return false;
    };

    std::priority_queue<Node, std::vector<Node>, NodeCmp> open;
    open.push({lb, ub, -INF, 0});

    if (P.verbose)
        std::printf("%9s %7s %15s %15s %15s %8s\n", "Node", "Left", "Objective", "Best Integer",
                    "Best Bound", "Gap");
    auto logLine = [&](const char* mark, double nodeObj) {
        const double bnd = open.empty() ? inc : std::min(open.top().bound, inc);
        const double gap = std::isfinite(inc) ? std::abs(inc - bnd) / std::max(1e-10, std::abs(inc)) : INF;
        std::printf("%1s%8ld %7zu %15.6g %15.6g %15.6g %7.2f%%\n", mark, R.nodes, open.size(),
                    sgn * nodeObj, std::isfinite(inc) ? sgn * inc : NAN, sgn * bnd, 100 * gap);
    };

    while (!open.empty()) {
        if (!incX.empty() && closeEnough(open.top().bound, inc)) break;
        if (R.nodes >= P.nodeLimit) { stop = Status::NodeLimit; break; }
        if (elapsed() > P.timeLimit) { stop = Status::TimeLimit; break; }

        Node nd = open.top();
        open.pop();
        if (!incX.empty() && closeEnough(nd.bound, inc)) continue;

        ++R.nodes;
        auto lp = detail::lpMin(M, nd.lb, nd.ub, sgn, maxIt);
        R.lpIterations += lp.iterations;

        if (lp.status == detail::LPStatus::Infeasible) continue;
        if (lp.status == detail::LPStatus::Unbounded) {
            if (R.nodes == 1) {
                R.status = Status::InfeasibleOrUnbounded;
                R.seconds = elapsed();
                return R;
            }
            incomplete = true;  // should not happen: children are restrictions
            continue;
        }
        if (lp.status == detail::LPStatus::IterationLimit) {
            incomplete = true;
            continue;
        }

        const double nodeBound = strengthen(lp.objective);
        if (!incX.empty() && closeEnough(nodeBound, inc)) continue;

        int bj = -1;
        double bestFrac = 0.0;
        for (int j : ints) {
            const double f = lp.x[j] - std::floor(lp.x[j]);
            const double frac = std::min(f, 1.0 - f);
            if (frac > P.intTol && frac > bestFrac) {
                bestFrac = frac;
                bj = j;
            }
        }

        if (bj < 0) {  // LP solution is integral
            if (tryIncumbent(lp.x) && P.verbose) logLine("*", lp.objective);
            continue;
        }
        if (tryIncumbent(lp.x) && P.verbose) logLine("H", lp.objective);

        const double v = lp.x[bj];
        Node down{nd.lb, nd.ub, nodeBound, nd.depth + 1};
        down.ub[bj] = std::floor(v);
        Node up{std::move(nd.lb), std::move(nd.ub), nodeBound, nd.depth + 1};
        up.lb[bj] = std::ceil(v);
        open.push(std::move(down));
        open.push(std::move(up));

        if (P.verbose && R.nodes % P.logEvery == 0) logLine("", lp.objective);
    }

    R.seconds = elapsed();
    double bound = open.empty() ? inc : std::min(open.top().bound, inc);
    if (incX.empty()) {
        R.status = (stop != Status::Optimal) ? stop
                   : incomplete              ? Status::IterationLimit
                                             : Status::Infeasible;
    } else {
        R.status = stop;
        if (stop == Status::Optimal && incomplete) R.status = Status::IterationLimit;
        R.hasSolution = true;
        R.x = incX;
        R.objective = sgn * inc;
        R.bestBound = sgn * bound;
        R.gap = std::abs(inc - bound) / std::max(1e-10, std::abs(inc));
    }
    if (P.verbose)
        std::printf("B&B done: %s, %ld nodes, %ld simplex iterations, %.3f s\n",
                    toString(R.status), R.nodes, R.lpIterations, R.seconds);
    return R;
}

}  // namespace mcplex
