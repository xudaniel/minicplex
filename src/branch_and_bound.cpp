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

#include <algorithm>
#include <array>
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
    // How this node was created (for pseudo-cost learning).
    int branchVar = -1;
    int dir = 0;          // 0 = down branch, 1 = up branch
    double dist = 0.0;    // distance the variable was moved (fractional part)
    double parentObj = 0.0;
};

// Pseudo-costs: average objective increase per unit change of a variable,
// learned separately for down and up branches.
struct PseudoCosts {
    std::vector<double> sum[2];
    std::vector<int> cnt[2];
    double totSum[2] = {0, 0};
    int totCnt[2] = {0, 0};

    explicit PseudoCosts(int n) {
        for (int d = 0; d < 2; ++d) { sum[d].assign(n, 0.0); cnt[d].assign(n, 0); }
    }
    void update(int j, int d, double gainPerUnit) {
        sum[d][j] += gainPerUnit;
        ++cnt[d][j];
        totSum[d] += gainPerUnit;
        ++totCnt[d];
    }
    double get(int j, int d) const {
        if (cnt[d][j] > 0) return sum[d][j] / cnt[d][j];
        return totCnt[d] > 0 ? totSum[d] / totCnt[d] : 1.0;  // uninitialised: global average
    }
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

    // ---------------- presolve (MIP only) ----------------
    Model PM;
    const Model* LM = &M;  // model given to the LP engine
    if (P.presolve && !ints.empty()) {
        std::vector<char> isIntCol(nv, 0);
        for (int j : ints) isIntCol[j] = 1;
        PM = M;
        detail::PresolveStats ps;
        const bool feasible = detail::presolve(PM, lb, ub, isIntCol, ps);
        if (P.verbose || P.trace)
            std::printf("Presolve: %d bounds tightened, %d coefficients tightened, %d rows removed%s\n",
                        ps.boundsTightened, ps.coefsTightened, ps.rowsRemoved, feasible ? "" : ", INFEASIBLE");
        if (!feasible) {
            R.status = Status::Infeasible;
            R.seconds = elapsed();
            return R;
        }
        LM = &PM;
    }

    detail::LPEngine E(*LM, sgn);
    E.setAllColBounds(lb, ub);
    E.setTrace(P.trace);

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
        return inc - bound <= std::max(P.mipAbsGap, P.mipGap * std::max(1.0, std::abs(inc)));
    };

    double inc = INF;  // incumbent, internal min sense
    std::vector<double> incX;
    bool incomplete = false;
    Status stop = Status::Optimal;

    auto cutoff = [&]() {
        if (incX.empty()) return INF;
        double c = inc - std::max(P.mipAbsGap, P.mipGap * std::max(1.0, std::abs(inc)));
        if (objIntegral) c = std::min(c, inc - 1.0 + 1e-6);
        return c;
    };
    // Accept a candidate only after "polishing": fix the integer variables at
    // their rounded values and re-solve the continuous part with a fresh LP,
    // so a point that is only feasible thanks to round-off is never accepted.
    bool hasContinuous = false;
    for (int j = 0; j < nv; ++j) hasContinuous |= !M.isInteger(j) || P.relaxIntegrality;
    // Returns 1 if accepted as the new incumbent, 0 if not better than the
    // incumbent, -1 if rejected as infeasible.
    auto tryIncumbent = [&](std::vector<double> x) -> int {
        for (int j : ints) x[j] = std::round(x[j]);
        // Cheap filter. With continuous variables the polishing LP below
        // decides feasibility, so the filter only removes hopeless roundings.
        if (!checkFeasible(M, x, hasContinuous ? 1e-4 : 1e-6)) return -1;
        if (sgn * evalObjective(M, x) >= inc + 1e-6 * (1.0 + std::abs(inc))) return 0;
        if (hasContinuous) {
            std::vector<double> plb(nv), pub(nv);
            for (int j = 0; j < nv; ++j) { plb[j] = M.vars[j].lb; pub[j] = M.vars[j].ub; }
            for (int j : ints) plb[j] = pub[j] = x[j];
            const auto pol = detail::lpMin(M, plb, pub, sgn, maxIt);
            if (pol.status != detail::LPStatus::Optimal) return -1;
            x = pol.x;
            for (int j : ints) x[j] = plb[j];
        }
        if (!checkFeasible(M, x, 1e-7)) return -1;
        const double v = sgn * evalObjective(M, x);
        if (v < inc - 1e-12) {
            inc = v;
            incX = std::move(x);
            return 1;
        }
        return 0;
    };

    // ---------------- root cutting planes ----------------
    // Rounds of Gomory mixed-integer cuts. Each round's cuts become new rows;
    // the LP is re-optimised from the previous basis (new slacks basic) with
    // the dual simplex. Cuts that are not tight at the end are dropped again.
    long cutIters = 0;
    if (P.cutRounds > 0 && E.solve(maxIt) == detail::LPStatus::Optimal) {
        std::vector<char> isIntCol(nv, 0);
        for (int j : ints) isIntCol[j] = 1;
        Model W = *LM;
        const int m0 = W.numConstrs();
        double obj = E.objective();
        for (int round = 0; round < P.cutRounds; ++round) {
            const std::vector<double> x = E.colValues();
            bool fractional = false;
            for (int j : ints) fractional |= std::abs(x[j] - std::round(x[j])) > P.intTol;
            if (!fractional) break;
            auto cuts = E.gomoryCuts(isIntCol, std::max(5, std::min(20, W.numConstrs())));
            if (cuts.empty()) break;
            const size_t nCuts = cuts.size();
            detail::Basis B = E.basis();
            for (auto& c : cuts) {
                if (P.trace) {
                    std::printf("[割平面] 新割 gmi%d：", W.numConstrs() - m0 + 1);
                    bool first = true;
                    for (const auto& [k, a] : c.coefs) {
                        std::printf("%s%g %s", first ? "" : (a < 0 ? " - " : " + "), first ? a : std::abs(a),
                                    M.vars[k].name.c_str());
                        first = false;
                    }
                    std::printf(" ≥ %g\n", c.rhs);
                }
                B.head.push_back(nv + W.numConstrs());  // new slack starts basic
                B.stat.push_back(0);
                W.addConstr(std::move(c), "gmi" + std::to_string(W.numConstrs() - m0 + 1));
            }
            cutIters += E.iterations();
            E = detail::LPEngine(W, sgn);
            E.setAllColBounds(lb, ub);
            E.setTrace(P.trace);
            E.loadBasis(B, true);
            if (P.trace)
                std::printf("[割平面] 第 %d 轮：加入 %zu 个 Gomory 割，重新求解根节点\n", round + 1, nCuts);
            if (E.solve(maxIt) != detail::LPStatus::Optimal) break;
            const double nobj = E.objective();
            if (P.trace) std::printf("[割平面] 根节点的界：%.6g → %.6g\n", sgn * obj, sgn * nobj);
            const bool stalled = nobj - obj < 1e-4 * (1.0 + std::abs(obj));
            obj = nobj;
            if (stalled) break;
        }
        // Keep only the cuts that are tight at the final root LP.
        if (W.numConstrs() > m0) {
            const std::vector<double> x = E.colValues();
            Model K = *LM;
            for (int i = m0; i < W.numConstrs(); ++i) {
                const Constraint& c = W.constraints[i];
                double act = 0.0;
                for (const auto& [k, a] : c.coefs) act += a * x[k];
                if (act <= c.rhs + 1e-6 * (1.0 + std::abs(c.rhs))) K.addConstr(c);
            }
            R.cuts = K.numConstrs() - m0;
            cutIters += E.iterations();
            E = detail::LPEngine(K, sgn);
            E.setAllColBounds(lb, ub);
            E.setTrace(P.trace);
        }
        if (P.verbose && R.cuts > 0)
            std::printf("Root cuts: %d Gomory cuts kept, root bound %.6g\n", R.cuts, sgn * obj);
    }

    PseudoCosts pc(nv);
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
            if (P.trace) std::printf("\n（下潜结束，从队列取出界最好的节点，恢复它保存的基）\n");
            E.setAllColBounds(cur.lb, cur.ub);
            E.loadBasis(cur.basis);
        }
        if (R.nodes >= P.nodeLimit) { stop = Status::NodeLimit; break; }
        if (elapsed() > P.timeLimit) { stop = Status::TimeLimit; break; }

        ++R.nodes;
        if (P.trace) {
            std::printf("\n[节点 %ld] 深度 %d", R.nodes, cur.depth);
            if (cur.branchVar >= 0)
                std::printf("，由 %s %s 分出来", M.vars[cur.branchVar].name.c_str(),
                            cur.dir ? ("≥ " + std::to_string(static_cast<long>(cur.lb[cur.branchVar]))).c_str()
                                    : ("≤ " + std::to_string(static_cast<long>(cur.ub[cur.branchVar]))).c_str());
            std::printf("\n");
        }
        const auto st = E.solve(maxIt, cutoff());

        if (st == detail::LPStatus::Infeasible || st == detail::LPStatus::Cutoff) {
            if (P.trace)
                std::printf("  剪枝：%s\n", st == detail::LPStatus::Infeasible ? "这种情况不可行"
                                                                       : "这种情况最好也比已有整数解差");
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
        if (cur.branchVar >= 0 && cur.dist > 1e-9)
            pc.update(cur.branchVar, cur.dir, std::max(0.0, lpObj - cur.parentObj) / cur.dist);
        const double nodeBound = strengthen(lpObj);
        cur.bound = nodeBound;
        if (!incX.empty() && closeEnough(nodeBound, inc)) {
            if (P.trace) std::printf("  剪枝：界 %.6g 不比已有整数解 %.6g 好\n", sgn * nodeBound, sgn * inc);
            haveCur = false;
            continue;
        }

        // Reliability branching: candidates whose pseudo-costs have not been
        // observed yet are evaluated by strong branching (a few dual simplex
        // iterations on each side), which also initialises their pseudo-costs.
        constexpr double kHuge = 1e12;
        std::vector<std::array<double, 2>> sbGain(0);
        std::vector<int> sbVar;
        bool pruneNode = false;
        if (P.branching == Branching::PseudoCost) {
            std::vector<std::pair<double, int>> unrel;
            for (int j : ints) {
                const double f = x[j] - std::floor(x[j]);
                const double frac = std::min(f, 1.0 - f);
                if (frac > P.intTol && (pc.cnt[0][j] < 1 || pc.cnt[1][j] < 1)) unrel.push_back({frac, j});
            }
            std::sort(unrel.begin(), unrel.end(), [](auto& a, auto& b) { return a.first > b.first; });
            if (unrel.size() > 8) unrel.resize(8);
            if (!unrel.empty()) {
                const detail::Basis B = E.basis();
                E.setTrace(false);
                for (const auto& [fr, j] : unrel) {
                    (void)fr;
                    const double v = x[j], fl = std::floor(v), ce = std::ceil(v);
                    std::array<double, 2> g{};
                    for (int d = 0; d < 2; ++d) {
                        const double olb = cur.lb[j], oub = cur.ub[j];
                        if (d == 0) E.setColBounds(j, olb, fl); else E.setColBounds(j, ce, oub);
                        const auto st = E.solve(40, cutoff());
                        const double dist = d == 0 ? v - fl : ce - v;
                        if (st == detail::LPStatus::Infeasible) {
                            g[d] = kHuge;
                        } else if (st == detail::LPStatus::Cutoff) {
                            g[d] = std::max(cutoff() - lpObj, 1e-6);
                            pc.update(j, d, g[d] / dist);
                            g[d] = kHuge;  // this side would be pruned immediately
                        } else {
                            g[d] = std::max(0.0, E.objective() - lpObj);
                            if (st == detail::LPStatus::Optimal) pc.update(j, d, g[d] / dist);
                        }
                        E.setColBounds(j, olb, oub);
                        E.loadBasis(B);
                    }
                    sbVar.push_back(j);
                    sbGain.push_back(g);
                    if (P.trace) {
                        auto fmt = [&](double v) { return v >= kHuge ? std::string("剪掉") : std::to_string(v).substr(0, 6); };
                        std::printf("  强分支试算 %s = %.4g：向下目标变差 %s，向上变差 %s\n", M.vars[j].name.c_str(), x[j],
                                    fmt(g[0]).c_str(), fmt(g[1]).c_str());
                    }
                    if (g[0] >= kHuge && g[1] >= kHuge) { pruneNode = true; break; }
                }
            }
        }
        E.setTrace(P.trace);
        if (pruneNode) {  // both children are infeasible or cut off
            if (P.trace) std::printf("  剪枝：强分支发现某个变量两侧都不可行或被截断\n");
            haveCur = false;
            continue;
        }

        // Branching variable: pseudo-cost product score, or most fractional.
        int bj = -1;
        double bestScore = -1.0, bestFrac = 0.0;
        for (int j : ints) {
            const double f = x[j] - std::floor(x[j]);
            const double frac = std::min(f, 1.0 - f);
            if (frac <= P.intTol) continue;
            double score = frac;
            if (P.branching == Branching::PseudoCost) {
                double down = pc.get(j, 0) * f, up = pc.get(j, 1) * (1.0 - f);
                for (size_t k = 0; k < sbVar.size(); ++k)
                    if (sbVar[k] == j) { down = sbGain[k][0]; up = sbGain[k][1]; }
                score = std::max(down, 1e-6) * std::max(up, 1e-6);
            }
            if (score > bestScore * (1 + 1e-9) || (score >= bestScore * (1 - 1e-9) && frac > bestFrac)) {
                bestScore = score;
                bestFrac = frac;
                bj = j;
            }
        }
        if (bj < 0) {  // LP solution is integral
            const int res = tryIncumbent(x);
            const bool better = res == 1;
            if (P.trace) {
                if (res == 1) std::printf("  LP 解全是整数，成为新的最优整数解：%g\n", sgn * inc);
                else if (res == 0) std::printf("  LP 解全是整数，但不比已有整数解好\n");
                else std::printf("  LP 解全是整数，但严格检查不可行（只在数值误差范围内成立），放弃\n");
            }
            if (better && P.verbose) logLine("*", lpObj);
            haveCur = false;
            continue;
        }
        if (tryIncumbent(x) == 1) {
            if (P.trace) {
                std::printf("  取整启发式：把 LP 解四舍五入后得到可行的整数解（");
                for (int j = 0, k = 0; j < nv; ++j)
                    if (M.isInteger(j)) std::printf("%s%s = %g", k++ ? "，" : "", M.vars[j].name.c_str(), incX[j]);
                std::printf("），新的最优整数解：%g\n", sgn * inc);
            }
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
        sib.branchVar = bj;
        sib.dir = goUp ? 0 : 1;
        sib.dist = goUp ? v - fl : ce - v;
        sib.parentObj = lpObj;
        open.push(std::move(sib));

        if (goUp) cur.lb[bj] = ce; else cur.ub[bj] = fl;
        cur.depth += 1;
        cur.branchVar = bj;
        cur.dir = goUp ? 1 : 0;
        cur.dist = goUp ? ce - v : v - fl;
        cur.parentObj = lpObj;
        E.setColBounds(bj, cur.lb[bj], cur.ub[bj]);  // warm start: same tableau

        if (P.trace)
            std::printf("  分支：%s = %.4g 不是整数 → 先走 %s %s %.0f（下潜，接着用当前单纯形表），%s %s %.0f 放进队列\n",
                        M.vars[bj].name.c_str(), v, M.vars[bj].name.c_str(), goUp ? "≥" : "≤", goUp ? ce : fl,
                        M.vars[bj].name.c_str(), goUp ? "≤" : "≥", goUp ? fl : ce);
        if (P.verbose && R.nodes % P.logEvery == 0) logLine("", lpObj);
    }

    R.seconds = elapsed();
    R.lpIterations = E.iterations() + cutIters;
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
