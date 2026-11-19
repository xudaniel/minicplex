// Branch and bound on top of the bounded simplex engine (LPEngine).
//   * plunging: after branching, one child is solved immediately from the
//     parent's tableau (warm start, dual simplex, usually a few pivots);
//     the sibling is stored with the parent's basis and restored later
//   * node selection when a plunge ends: smallest LP bound first
//   * branching variable: most fractional integer variable; the plunge
//     follows the rounding direction of the fractional value
//   * pruning inside the LP: the dual simplex stops as soon as the node's
//     bound reaches the incumbent (cutoff)
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
    detail::Basis basis;  // parent's optimal basis (warm start)
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

    detail::LPEngine E(M, sgn);
    E.setAllColBounds(lb, ub);

    // ---------------- pure LP ----------------
    if (ints.empty()) {
        const auto st = E.solve(maxIt);
        R.lpIterations = E.iterations();
        R.seconds = elapsed();
        switch (st) {
            case detail::LPStatus::Optimal:
                R.status = Status::Optimal;
                R.hasSolution = true;
                R.x = E.colValues();
                R.objective = R.bestBound = sgn * E.objective();
                R.gap = 0.0;
                break;
            case detail::LPStatus::Infeasible: R.status = Status::Infeasible; break;
            case detail::LPStatus::Unbounded: R.status = Status::Unbounded; break;
            default: R.status = Status::IterationLimit; break;
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

    auto cutoff = [&]() {
        if (incX.empty()) return INF;
        double c = inc - P.mipGap * std::max(1.0, std::abs(inc));
        if (objIntegral) c = std::min(c, inc - 1.0 + 1e-6);
        return c;
    };
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
    Node cur{lb, ub, -INF, 0, {}};
    bool haveCur = true;  // root: engine already holds bounds and the slack basis

    auto bestBound = [&]() {
        double b = inc;
        if (!open.empty()) b = std::min(b, open.top().bound);
        if (haveCur) b = std::min(b, cur.bound);
        return b;
    };

    if (P.verbose)
        std::printf("%9s %7s %15s %15s %15s %8s\n", "Node", "Left", "Objective", "Best Integer", "Best Bound",
                    "Gap");
    auto logLine = [&](const char* mark, double nodeObj) {
        const double bnd = bestBound();
        const double gap =
            std::isfinite(inc) ? std::abs(inc - bnd) / std::max(1e-10, std::abs(inc)) : INF;
        std::printf("%1s%8ld %7zu %15.6g %15.6g %15.6g %7.2f%%\n", mark, R.nodes, open.size(), sgn * nodeObj,
                    std::isfinite(inc) ? sgn * inc : NAN, sgn * bnd, 100 * gap);
    };

    for (;;) {
        if (!haveCur) {
            if (open.empty()) break;
            if (!incX.empty() && closeEnough(open.top().bound, inc)) break;
            cur = open.top();
            open.pop();
            haveCur = true;
            E.setAllColBounds(cur.lb, cur.ub);
            E.loadBasis(cur.basis);
        }
        if (R.nodes >= P.nodeLimit) { stop = Status::NodeLimit; break; }
        if (elapsed() > P.timeLimit) { stop = Status::TimeLimit; break; }

        ++R.nodes;
        const auto st = E.solve(maxIt, cutoff());

        if (st == detail::LPStatus::Infeasible || st == detail::LPStatus::Cutoff) {
            haveCur = false;
            continue;
        }
        if (st == detail::LPStatus::Unbounded) {
            if (R.nodes == 1) {
                R.status = Status::InfeasibleOrUnbounded;
                R.lpIterations = E.iterations();
                R.seconds = elapsed();
                return R;
            }
            incomplete = true;  // should not happen: children are restrictions
            haveCur = false;
            continue;
        }
        if (st == detail::LPStatus::IterationLimit) {
            incomplete = true;
            haveCur = false;
            continue;
        }

        const std::vector<double> x = E.colValues();
        const double lpObj = E.objective();
        const double nodeBound = strengthen(lpObj);
        cur.bound = nodeBound;
        if (!incX.empty() && closeEnough(nodeBound, inc)) {
            haveCur = false;
            continue;
        }

        int bj = -1;
        double bestFrac = 0.0;
        for (int j : ints) {
            const double f = x[j] - std::floor(x[j]);
            const double frac = std::min(f, 1.0 - f);
            if (frac > P.intTol && frac > bestFrac) {
                bestFrac = frac;
                bj = j;
            }
        }
        if (bj < 0) {  // LP solution is integral
            if (tryIncumbent(x) && P.verbose) logLine("*", lpObj);
            haveCur = false;
            continue;
        }
        if (tryIncumbent(x)) {
            if (P.verbose) logLine("H", lpObj);
            if (closeEnough(nodeBound, inc)) {
                haveCur = false;
                continue;
            }
        }

        // Branch: plunge into the child on the rounding side, store the sibling.
        const double v = x[bj];
        const double fl = std::floor(v), ce = std::ceil(v);
        const bool goUp = (v - fl) >= 0.5;
        Node sib{cur.lb, cur.ub, nodeBound, cur.depth + 1, E.basis()};
        if (goUp) sib.ub[bj] = fl; else sib.lb[bj] = ce;
        open.push(std::move(sib));

        if (goUp) cur.lb[bj] = ce; else cur.ub[bj] = fl;
        cur.depth += 1;
        E.setColBounds(bj, cur.lb[bj], cur.ub[bj]);  // warm start: same tableau

        if (P.verbose && R.nodes % P.logEvery == 0) logLine("", lpObj);
    }

    R.seconds = elapsed();
    R.lpIterations = E.iterations();
    const double bound = bestBound();
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
        std::printf("B&B done: %s, %ld nodes, %ld simplex iterations, %.3f s\n", toString(R.status), R.nodes,
                    R.lpIterations, R.seconds);
    return R;
}

}  // namespace mcplex
