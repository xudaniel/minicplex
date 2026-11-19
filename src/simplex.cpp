// Bounded-variable simplex engine (primal + dual) on a dense tableau.
//
// Computational form
//     A x - s = 0,    l <= x <= u,    rlo <= s <= rhi
// Each constraint row i gets a slack s_i equal to its activity a_i x, with
// bounds taken from the row sense (<=: (-inf, b], >=: [b, inf), =: [b, b]).
// Variable bounds are handled implicitly: a nonbasic variable sits at its
// lower bound, its upper bound, or at zero if it is free.  So, unlike a
// textbook standard form, bounds never add rows and no artificial columns
// are needed: the all-slack basis is always a valid start.
//
// The tableau T = B^-1 [A | -I] (m x (n+m)) is kept explicitly together with
// the reduced costs d and the values x of all variables, so that
//     x_B = - sum_{j nonbasic} T[:, j] x_j.
//
//   * Primal simplex.  Phase 1 minimises the sum of bound violations of the
//     basic variables (a "composite" phase 1: the cost vector is rebuilt every
//     iteration), phase 2 minimises c'x.  Entering variables may simply jump
//     to their other bound ("bound flip") without a basis change.
//   * Dual simplex.  Used whenever the basis is dual feasible.  This is the
//     case after branch and bound tightens a bound of a basic variable, so a
//     child node is re-optimised from its parent's basis in a few pivots.
//   * Anti-cycling: after a run of degenerate pivots, Bland's smallest-index
//     rule is used.  The tableau is periodically rebuilt from the original
//     matrix to stop round-off from accumulating.

#include <algorithm>
#include <cmath>
#include <cstdio>

#include "solver.hpp"

namespace mcplex::detail {
namespace {
constexpr double kPrimalTol = 1e-7;  // bound violation allowed (scaled)
constexpr double kDualTol = 1e-9;    // reduced-cost tolerance
constexpr double kPivotTol = 1e-9;   // smallest acceptable pivot element
constexpr int kBlandAfter = 50;      // degenerate pivots before Bland's rule
}  // namespace

LPEngine::LPEngine(const Model& M, double objSign)
    : n_(M.numVars()), m_(M.numConstrs()), N_(n_ + m_) {
    A_.assign(static_cast<size_t>(m_) * n_, 0.0);
    c_.assign(N_, 0.0);
    lb_.assign(N_, 0.0);
    ub_.assign(N_, INF);
    for (int i = 0; i < m_; ++i) {
        const Constraint& con = M.constraints[i];
        for (const auto& [k, v] : con.coefs) A_[static_cast<size_t>(i) * n_ + k] += v;
        const int s = n_ + i;
        lb_[s] = (con.sense == Sense::LE) ? -INF : con.rhs;
        ub_[s] = (con.sense == Sense::GE) ? INF : con.rhs;
    }
    for (int j = 0; j < n_; ++j) {
        lb_[j] = M.vars[j].lb;
        ub_[j] = M.vars[j].ub;
    }
    for (const auto& [k, v] : M.objective.terms) c_[k] += objSign * v;
    objConst_ = objSign * M.objective.constant;
    objSign_ = objSign;
    names_.resize(N_);
    for (int j = 0; j < n_; ++j) names_[j] = M.vars[j].name;
    for (int i = 0; i < m_; ++i) names_[n_ + i] = "s(" + M.constraints[i].name + ")";

    // All-slack starting basis.
    Basis b;
    b.head.resize(m_);
    for (int i = 0; i < m_; ++i) b.head[i] = n_ + i;
    b.stat.assign(N_, -1);  // -1: choose default status
    loadBasis(b);
}

signed char LPEngine::defaultStatus(int j) const {
    const bool lf = std::isfinite(lb_[j]), uf = std::isfinite(ub_[j]);
    if (lf && uf && lb_[j] == ub_[j]) return kFixed;
    if (lf && uf) return c_[j] < 0 ? kUpper : kLower;  // pick the dual-feasible side
    if (lf) return kLower;
    if (uf) return kUpper;
    return kFree;
}

double LPEngine::nonbasicValue(int j) const {
    switch (stat_[j]) {
        case kLower: case kFixed: return lb_[j];
        case kUpper: return ub_[j];
        default: return 0.0;
    }
}

// Move to basis b and recompute x and d.
//  * incremental (default): pivot the missing columns into the current
//    tableau, replacing rows whose basic variable is not wanted. After a
//    plunge the stored sibling basis usually differs in only a few columns.
//  * fromScratch: rebuild T from the original matrix (removes round-off).
void LPEngine::loadBasis(const Basis& b, bool fromScratch) {
    if (!fromScratch && static_cast<int>(head_.size()) == m_ && !T_.empty() &&
        pivotsSinceRefactor_ < std::max(200, 2 * m_)) {
        std::vector<char> wanted(N_, 0);
        for (int v : b.head) wanted[v] = 1;
        bool ok = true;
        for (int q : b.head) {
            if (stat_[q] == kBasic) continue;
            int r = -1;
            double best = 1e-7;
            for (int i = 0; i < m_; ++i) {
                if (wanted[head_[i]]) continue;
                if (std::abs(T(i, q)) > best) {
                    best = std::abs(T(i, q));
                    r = i;
                }
            }
            if (r < 0) { ok = false; break; }
            stat_[head_[r]] = kLower;  // fixed below
            pivot(r, q);
            stat_[q] = kBasic;
        }
        if (ok) {
            for (int j = 0; j < N_; ++j) {
                if (stat_[j] == kBasic) continue;
                signed char s = (static_cast<size_t>(j) < b.stat.size()) ? b.stat[j] : -1;
                const bool valid = (s == kLower && std::isfinite(lb_[j])) ||
                                   (s == kUpper && std::isfinite(ub_[j])) ||
                                   (s == kFree && !std::isfinite(lb_[j]) && !std::isfinite(ub_[j])) ||
                                   (s == kFixed && lb_[j] == ub_[j]);
                stat_[j] = valid ? s : defaultStatus(j);
            }
            recomputeValues();
            recomputeReducedCosts();
            return;
        }
    }
    T_.assign(static_cast<size_t>(m_) * N_, 0.0);
    for (int i = 0; i < m_; ++i) {
        for (int j = 0; j < n_; ++j) T(i, j) = -A_[static_cast<size_t>(i) * n_ + j];
        T(i, n_ + i) = 1.0;
    }
    head_.resize(m_);
    for (int i = 0; i < m_; ++i) head_[i] = n_ + i;
    stat_.assign(N_, kLower);
    for (int i = 0; i < m_; ++i) stat_[n_ + i] = kBasic;

    std::vector<char> wanted(N_, 0);
    for (int v : b.head) wanted[v] = 1;
    d_.assign(N_, 0.0);  // pivot() updates d_, keep it defined
    for (int q : b.head) {
        if (q >= n_) continue;  // slacks are basic already
        int r = -1;
        double best = kPivotTol;
        for (int i = 0; i < m_; ++i) {
            const int h = head_[i];
            if (h < n_ || wanted[h]) continue;  // row already holds a wanted variable
            if (std::abs(T(i, q)) > best) {
                best = std::abs(T(i, q));
                r = i;
            }
        }
        if (r >= 0) {
            stat_[head_[r]] = kLower;  // placeholder, fixed below
            pivot(r, q);
            stat_[q] = kBasic;
        }
    }
    // Nonbasic statuses: keep the saved one when it is still valid.
    for (int j = 0; j < N_; ++j) {
        if (stat_[j] == kBasic) continue;
        signed char s = (static_cast<size_t>(j) < b.stat.size()) ? b.stat[j] : -1;
        const bool ok = (s == kLower && std::isfinite(lb_[j])) || (s == kUpper && std::isfinite(ub_[j])) ||
                        (s == kFree && !std::isfinite(lb_[j]) && !std::isfinite(ub_[j])) ||
                        (s == kFixed && lb_[j] == ub_[j]);
        stat_[j] = ok ? s : defaultStatus(j);
    }
    x_.assign(N_, 0.0);
    recomputeValues();
    recomputeReducedCosts();
    pivotsSinceRefactor_ = 0;
}

void LPEngine::recomputeValues() {
    valuesDirty_ = false;
    pivotsSinceRecompute_ = 0;
    for (int j = 0; j < N_; ++j)
        if (stat_[j] != kBasic) x_[j] = nonbasicValue(j);
    for (int i = 0; i < m_; ++i) {
        double v = 0.0;
        const double* row = &T_[static_cast<size_t>(i) * N_];
        for (int j = 0; j < N_; ++j)
            if (stat_[j] != kBasic && x_[j] != 0.0) v -= row[j] * x_[j];
        x_[head_[i]] = v;
    }
}

void LPEngine::recomputeReducedCosts() {
    d_ = c_;
    for (int i = 0; i < m_; ++i) {
        const double cb = c_[head_[i]];
        if (cb == 0.0) continue;
        const double* row = &T_[static_cast<size_t>(i) * N_];
        for (int j = 0; j < N_; ++j) d_[j] -= cb * row[j];
    }
    for (int i = 0; i < m_; ++i) d_[head_[i]] = 0.0;
}

void LPEngine::pivot(int r, int q) {
    double* pr = &T_[static_cast<size_t>(r) * N_];
    const double inv = 1.0 / pr[q];
    nz_.clear();
    for (int j = 0; j < N_; ++j) {
        if (pr[j] == 0.0) continue;
        pr[j] *= inv;
        nz_.push_back(j);
    }
    pr[q] = 1.0;
    for (int i = 0; i < m_; ++i) {
        if (i == r) continue;
        double* pi = &T_[static_cast<size_t>(i) * N_];
        const double f = pi[q];
        if (f == 0.0) continue;
        for (int j : nz_) pi[j] -= f * pr[j];
        pi[q] = 0.0;
    }
    const double f = d_[q];
    if (f != 0.0) {
        for (int j : nz_) d_[j] -= f * pr[j];
        d_[q] = 0.0;
    }
    head_[r] = q;
    ++pivotsSinceRefactor_;
    ++pivotsSinceRecompute_;
}

void LPEngine::setColBounds(int j, double lb, double ub) {
    lb_[j] = lb;
    ub_[j] = ub;
    if (stat_[j] == kBasic) return;  // may become primal infeasible: dual simplex fixes it
    const double old = x_[j];
    const signed char s = stat_[j];
    const bool ok = (s == kLower && std::isfinite(lb)) || (s == kUpper && std::isfinite(ub)) ||
                    (s == kFree && !std::isfinite(lb) && !std::isfinite(ub)) || (s == kFixed && lb == ub);
    if (!ok) stat_[j] = defaultStatus(j);
    if (lb == ub) stat_[j] = kFixed;
    x_[j] = nonbasicValue(j);
    const double delta = x_[j] - old;
    if (delta != 0.0)
        for (int i = 0; i < m_; ++i) x_[head_[i]] -= T(i, j) * delta;
}

void LPEngine::setAllColBounds(const std::vector<double>& lb, const std::vector<double>& ub) {
    for (int j = 0; j < n_; ++j) {
        lb_[j] = lb[j];
        ub_[j] = ub[j];
    }
    valuesDirty_ = true;
}

double LPEngine::objective() const {
    double v = objConst_;
    for (int j = 0; j < n_; ++j) v += c_[j] * x_[j];
    return v;
}

// Sensitivity information from the current (optimal) basis, recomputed from T
// so it does not depend on the incrementally updated d_.
//   reduced cost  d_j = c_j - sum_i c_B(i) T[i][j]
//   shadow price of row i = reduced cost of its slack s_i: the slack's column
//   in [A | -I] is -e_i, so d_{s_i} = y_i, the dual value of the row.
// Both are converted to the model's objective sense (objSign_).
std::vector<double> LPEngine::rowDuals() const {
    std::vector<double> y(m_, 0.0);
    for (int k = 0; k < m_; ++k) {
        const int j = n_ + k;
        if (stat_[j] == kBasic) continue;  // non-binding row: price 0
        double d = c_[j];
        for (int i = 0; i < m_; ++i) d -= c_[head_[i]] * T(i, j);
        y[k] = std::abs(d) < 1e-12 ? 0.0 : objSign_ * d;
    }
    return y;
}

std::vector<double> LPEngine::colReducedCosts() const {
    std::vector<double> r(n_, 0.0);
    for (int j = 0; j < n_; ++j) {
        if (stat_[j] == kBasic) continue;
        double d = c_[j];
        for (int i = 0; i < m_; ++i) d -= c_[head_[i]] * T(i, j);
        r[j] = std::abs(d) < 1e-12 ? 0.0 : objSign_ * d;
    }
    return r;
}

std::vector<double> LPEngine::colValues() const { return std::vector<double>(x_.begin(), x_.begin() + n_); }

// > 0: amount by which variable v violates its bounds.
double LPEngine::infeasibility(int v) const {
    const double tl = kPrimalTol * (1.0 + std::abs(lb_[v]));
    const double tu = kPrimalTol * (1.0 + std::abs(ub_[v]));
    if (x_[v] < lb_[v] - tl) return lb_[v] - x_[v];
    if (x_[v] > ub_[v] + tu) return x_[v] - ub_[v];
    return 0.0;
}

// Put boxed nonbasic variables on the bound that matches the sign of their
// reduced cost. Returns false if some variable cannot be made dual feasible
// (e.g. a negative reduced cost on a variable without an upper bound).
bool LPEngine::makeDualFeasible() {
    bool ok = true;
    for (int j = 0; j < N_; ++j) {
        const signed char s = stat_[j];
        if (s == kBasic || s == kFixed) continue;
        const double dj = d_[j];
        signed char want = s;
        if (s == kLower && dj < -kDualTol) want = kUpper;
        else if (s == kUpper && dj > kDualTol) want = kLower;
        else if (s == kFree && std::abs(dj) > kDualTol) { ok = false; continue; }
        if (want == s) continue;
        if ((want == kUpper && !std::isfinite(ub_[j])) || (want == kLower && !std::isfinite(lb_[j]))) {
            ok = false;
            continue;
        }
        const double old = x_[j];
        stat_[j] = want;
        x_[j] = nonbasicValue(j);
        const double delta = x_[j] - old;
        for (int i = 0; i < m_; ++i) x_[head_[i]] -= T(i, j) * delta;
    }
    return ok;
}

LPStatus LPEngine::primal(long maxIters) {
    int degenerate = 0;
    std::vector<double> dd(N_);
    std::vector<double> rowCost(m_);
    for (;;) {
        if (iters_ >= maxIters) return LPStatus::IterationLimit;
        if (pivotsSinceRefactor_ > std::max(200, 2 * m_)) loadBasis(basis(), true);

        // Phase-1 cost: -1 for basics below their lower bound, +1 above the upper.
        bool phase1 = false;
        for (int i = 0; i < m_; ++i) {
            const int v = head_[i];
            rowCost[i] = 0.0;
            if (infeasibility(v) > 0.0) {
                rowCost[i] = x_[v] < lb_[v] ? -1.0 : 1.0;
                phase1 = true;
            }
        }
        if (phase1) {
            std::fill(dd.begin(), dd.end(), 0.0);
            for (int i = 0; i < m_; ++i) {
                if (rowCost[i] == 0.0) continue;
                const double* row = &T_[static_cast<size_t>(i) * N_];
                for (int j = 0; j < N_; ++j) dd[j] -= rowCost[i] * row[j];
            }
        }
        const std::vector<double>& price = phase1 ? dd : d_;

        // Pricing.
        const bool bland = degenerate > kBlandAfter;
        int q = -1, dir = 0;
        double best = 0.0;
        for (int j = 0; j < N_; ++j) {
            const signed char s = stat_[j];
            if (s == kBasic || s == kFixed) continue;
            const double dj = price[j];
            int dj_dir = 0;
            if ((s == kLower || s == kFree) && dj < -kDualTol) dj_dir = +1;
            else if ((s == kUpper || s == kFree) && dj > kDualTol) dj_dir = -1;
            if (!dj_dir) continue;
            if (std::abs(dj) > best) {
                best = std::abs(dj);
                q = j;
                dir = dj_dir;
                if (bland) break;
            }
        }
        if (q < 0) return phase1 ? LPStatus::Infeasible : LPStatus::Optimal;

        // Ratio test. alpha_i = change of basic i per unit step of x_q.
        double tMax = (std::isfinite(lb_[q]) && std::isfinite(ub_[q])) ? ub_[q] - lb_[q] : INF;
        int r = -1;
        double tBest = INF, aBest = 0.0, target = 0.0;
        for (int i = 0; i < m_; ++i) {
            const double alpha = -T(i, q) * dir;
            if (std::abs(alpha) < kPivotTol) continue;
            const int v = head_[i];
            const double xv = x_[v];
            double t, tg;
            const double inf = phase1 ? infeasibility(v) : 0.0;
            if (inf > 0.0 && xv < lb_[v]) {         // below: stops when it reaches lb
                if (alpha <= 0) continue;
                t = (lb_[v] - xv) / alpha;
                tg = lb_[v];
            } else if (inf > 0.0) {                 // above: stops when it reaches ub
                if (alpha >= 0) continue;
                t = (ub_[v] - xv) / alpha;
                tg = ub_[v];
            } else if (alpha > 0) {
                if (!std::isfinite(ub_[v])) continue;
                t = (ub_[v] - xv) / alpha;
                tg = ub_[v];
            } else {
                if (!std::isfinite(lb_[v])) continue;
                t = (lb_[v] - xv) / alpha;
                tg = lb_[v];
            }
            if (t < 0) t = 0;
            bool take = r < 0 || t < tBest - 1e-12;
            if (!take && t <= tBest + 1e-12)
                take = bland ? v < head_[r] : std::abs(alpha) > aBest;
            if (take) {
                r = i;
                tBest = t;
                aBest = std::abs(alpha);
                target = tg;
            }
        }
        if (r < 0 && !std::isfinite(tMax))
            return phase1 ? LPStatus::IterationLimit : LPStatus::Unbounded;  // phase 1 cannot be unbounded

        const bool flip = tMax <= tBest;
        const double t = flip ? tMax : tBest;
        if (trace_) {
            std::printf("    第 %ld 步（%s）：%s 进基（从%s%s，既约成本 %.4g）", iters_ + 1,
                        phase1 ? "原始单纯形·第一阶段" : "原始单纯形·第二阶段", name(q).c_str(),
                        stat_[q] == kUpper ? "上界" : stat_[q] == kFree ? "0" : "下界", dir > 0 ? "增大" : "减小", price[q]);
            if (flip)
                std::printf("，走到另一侧边界（bound flip），步长 %.4g\n", t);
            else
                std::printf("，%s 离基停在%s %.4g，步长 %.4g\n", name(head_[r]).c_str(),
                            target == lb_[head_[r]] ? "下界" : "上界", target, t);
        }
        if (t != 0.0) {
            x_[q] += dir * t;
            for (int i = 0; i < m_; ++i) {
                const double a = T(i, q);
                if (a != 0.0) x_[head_[i]] -= a * dir * t;
            }
        }
        ++iters_;
        degenerate = (t <= 1e-12) ? degenerate + 1 : 0;
        if (flip) {
            stat_[q] = (dir > 0) ? kUpper : kLower;
            x_[q] = nonbasicValue(q);
            continue;
        }
        const int leave = head_[r];
        x_[leave] = target;
        stat_[leave] = (lb_[leave] == ub_[leave]) ? kFixed : (target == lb_[leave] ? kLower : kUpper);
        pivot(r, q);
        stat_[q] = kBasic;
    }
}

LPStatus LPEngine::dual(long maxIters, double cutoff) {
    int degenerate = 0;
    for (;;) {
        if (iters_ >= maxIters) return LPStatus::IterationLimit;
        if (pivotsSinceRefactor_ > std::max(200, 2 * m_)) {
            loadBasis(basis(), true);
            if (!makeDualFeasible()) return primal(maxIters);
        }
        if (std::isfinite(cutoff) && objective() >= cutoff) return LPStatus::Cutoff;

        // Leaving row: the most infeasible basic variable.
        const bool bland = degenerate > kBlandAfter;
        int r = -1;
        double worst = 0.0;
        for (int i = 0; i < m_; ++i) {
            const double inf = infeasibility(head_[i]);
            if (inf <= 0.0) continue;
            if (bland ? (r < 0 || head_[i] < head_[r]) : inf > worst) {
                worst = inf;
                r = i;
            }
        }
        if (r < 0) return LPStatus::Optimal;

        const int v = head_[r];
        const bool below = x_[v] < lb_[v];
        const double target = below ? lb_[v] : ub_[v];

        // Entering column: keep reduced costs dual feasible (min |d_j / a_rj|).
        int q = -1;
        double bestRatio = INF, bestA = 0.0;
        for (int j = 0; j < N_; ++j) {
            const signed char s = stat_[j];
            if (s == kBasic || s == kFixed) continue;
            const double a = T(r, j);
            if (std::abs(a) < kPivotTol) continue;
            // x_v changes by -a per unit increase of x_j.
            const int dirNeeded = below ? (a < 0 ? +1 : -1) : (a > 0 ? +1 : -1);
            if (dirNeeded > 0 && s == kUpper) continue;
            if (dirNeeded < 0 && s == kLower) continue;
            const double ratio = std::abs(d_[j]) / std::abs(a);
            bool take = q < 0 || ratio < bestRatio - 1e-12;
            if (!take && ratio <= bestRatio + 1e-12) take = bland ? j < q : std::abs(a) > bestA;
            if (take) {
                q = j;
                bestRatio = ratio;
                bestA = std::abs(a);
            }
        }
        if (q < 0) return LPStatus::Infeasible;

        if (trace_)
            std::printf("    第 %ld 步（对偶单纯形）：%s = %.4g 越过%s %.4g，离基；%s 进基（比值 %.4g）\n", iters_ + 1,
                        name(v).c_str(), x_[v], below ? "下界" : "上界", target, name(q).c_str(), bestRatio);
        const double delta = (x_[v] - target) / T(r, q);
        x_[q] += delta;
        for (int i = 0; i < m_; ++i) {
            const double a = T(i, q);
            if (a != 0.0) x_[head_[i]] -= a * delta;
        }
        x_[v] = target;
        stat_[v] = (lb_[v] == ub_[v]) ? kFixed : (below ? kLower : kUpper);
        pivot(r, q);
        stat_[q] = kBasic;
        ++iters_;
        degenerate = (bestRatio <= 1e-12) ? degenerate + 1 : 0;
    }
}

LPStatus LPEngine::solve(long maxIters, double cutoff) {
    const long limit = iters_ + maxIters;
    // Bounds of structurals may have changed wholesale: refresh nonbasic values.
    for (int j = 0; j < n_; ++j) {
        if (stat_[j] == kBasic) continue;
        const signed char s = stat_[j];
        const bool ok = (s == kLower && std::isfinite(lb_[j])) || (s == kUpper && std::isfinite(ub_[j])) ||
                        (s == kFree && !std::isfinite(lb_[j]) && !std::isfinite(ub_[j])) ||
                        (s == kFixed && lb_[j] == ub_[j]);
        const signed char ns = (!ok || lb_[j] == ub_[j]) ? defaultStatus(j) : s;
        if (ns != s || x_[j] != nonbasicValue(j)) valuesDirty_ = true;
        stat_[j] = ns;
    }
    for (int j = 0; j < n_; ++j)
        if (lb_[j] > ub_[j] + 1e-9) return LPStatus::Infeasible;
    if (valuesDirty_) recomputeValues();

    for (int round = 0; round < 4; ++round) {
        const bool dualOk = makeDualFeasible();
        if (trace_)
            std::printf("  [LP] 当前基%s → 用%s\n", dualOk ? "对偶可行" : "不是对偶可行",
                        dualOk ? "对偶单纯形" : "原始单纯形");
        LPStatus st = dualOk ? dual(limit, cutoff) : primal(limit);
        if (trace_) {
            const char* names[] = {"最优", "不可行", "无界", "达到迭代上限", "被截断（不可能比已有整数解更好）"};
            std::printf("  [LP] 结果：%s", names[static_cast<int>(st)]);
            if (st == LPStatus::Optimal || st == LPStatus::Cutoff) std::printf("，目标值 %.6g", realObjective());
            std::printf("\n");
        }
        if (st != LPStatus::Optimal) {
            if (st == LPStatus::Infeasible && round < 3) {
                // confirm with fresh values before declaring infeasibility
                recomputeValues();
                recomputeReducedCosts();
                if (makeDualFeasible() ? dual(limit, INF) == LPStatus::Infeasible
                                       : primal(limit) == LPStatus::Infeasible)
                    return LPStatus::Infeasible;
                continue;
            }
            return st;
        }
        // Verify optimality on freshly computed values (and, every so often,
        // freshly computed reduced costs) to catch accumulated round-off.
        const bool refreshD = pivotsSinceRefactor_ > 50;
        if (pivotsSinceRecompute_ > 0) recomputeValues();
        if (refreshD) recomputeReducedCosts();
        bool clean = true;
        for (int i = 0; i < m_ && clean; ++i) clean = infeasibility(head_[i]) == 0.0;
        // Guard against round-off in T: the slack values must agree with the
        // row activities computed from the original matrix.
        for (int i = 0; i < m_ && clean; ++i) {
            double act = 0.0;
            const double* a = &A_[static_cast<size_t>(i) * n_];
            for (int k = 0; k < n_; ++k)
                if (a[k] != 0.0) act += a[k] * x_[k];
            if (std::abs(act - x_[n_ + i]) > 1e-9 * (1.0 + std::abs(act))) clean = false;
        }
        for (int j = 0; j < N_ && clean; ++j) {
            const signed char s = stat_[j];
            if (s == kBasic || s == kFixed) continue;
            if ((s == kLower || s == kFree) && d_[j] < -1e-7) clean = false;
            if ((s == kUpper || s == kFree) && d_[j] > 1e-7) clean = false;
        }
        if (clean) {
            if (std::isfinite(cutoff) && objective() >= cutoff) return LPStatus::Cutoff;
            return LPStatus::Optimal;
        }
        loadBasis(basis(), true);  // numerical trouble: refactor and continue
    }
    return LPStatus::IterationLimit;
}

// Gomory mixed-integer (GMI) cuts.
//
// Row r of the tableau reads  x_B + sum_j T[r][j] x_j = 0.  Writing every
// nonbasic variable as its distance y_j >= 0 from the bound it sits on
// (x_j = l_j + y_j, or x_j = u_j - y_j) gives
//     x_B + sum_j a_j y_j = b,      b = current value of x_B,
// with a_j = T[r][j] (at lower) or -T[r][j] (at upper).  If x_B must be
// integer and f0 = frac(b) > 0, every integer-feasible point satisfies
//     sum_j g_j y_j >= 1,
//     g_j = f_j / f0              if y_j integer and f_j = frac(a_j) <= f0
//         = (1 - f_j) / (1 - f0)  if y_j integer and f_j > f0
//         = a_j / f0              if y_j continuous and a_j >= 0
//         = -a_j / (1 - f0)       if y_j continuous and a_j < 0,
// which the current vertex (all y_j = 0) violates.  Slack variables are
// integer when their row has integer coefficients on integer variables;
// they are finally substituted by their definition s_i = a_i x.
std::vector<Constraint> LPEngine::gomoryCuts(const std::vector<char>& isIntCol, int maxCuts) const {
    auto isIntegral = [](double v) { return std::isfinite(v) && std::abs(v - std::round(v)) < 1e-9; };
    std::vector<char> isInt(N_, 0);
    for (int j = 0; j < n_; ++j) isInt[j] = isIntCol[j];
    for (int i = 0; i < m_; ++i) {
        bool ok = true;
        for (int j = 0; j < n_ && ok; ++j) {
            const double a = A_[static_cast<size_t>(i) * n_ + j];
            if (a != 0.0 && (!isIntCol[j] || !isIntegral(a))) ok = false;
        }
        isInt[n_ + i] = ok;
    }

    struct Cand { std::vector<double> pi; double rhs, eff; };
    std::vector<Cand> cands;
    for (int r = 0; r < m_; ++r) {
        const int v = head_[r];
        if (!isInt[v]) continue;
        const double b = x_[v];
        const double f0 = b - std::floor(b);
        if (f0 < 0.01 || f0 > 0.99) continue;  // nearly integral: numerically unsafe

        std::vector<double> pi(n_, 0.0);  // cut in structural space: pi x >= rhs
        double rhs = 1.0;
        bool ok = true;
        for (int j = 0; j < N_ && ok; ++j) {
            const signed char s = stat_[j];
            if (s == kBasic || s == kFixed) continue;
            const double t = T(r, j);
            if (std::abs(t) < 1e-11) continue;
            if (s == kFree) { ok = false; break; }
            const bool atLower = (s == kLower);
            const double a = atLower ? t : -t;
            const double bnd = atLower ? lb_[j] : ub_[j];
            double g;
            if (isInt[j] && isIntegral(bnd)) {
                const double fj = a - std::floor(a);
                g = (fj <= f0) ? fj / f0 : (1.0 - fj) / (1.0 - f0);
            } else {
                g = (a >= 0) ? a / f0 : -a / (1.0 - f0);
            }
            if (g == 0.0) continue;
            // g * y_j  with  y_j = x_j - l_j  or  u_j - x_j
            const double coef = atLower ? g : -g;
            rhs += atLower ? g * bnd : -g * bnd;
            if (j < n_) {
                pi[j] += coef;
            } else {  // slack: s_i = a_i x
                const int i = j - n_;
                for (int k = 0; k < n_; ++k) {
                    const double aik = A_[static_cast<size_t>(i) * n_ + k];
                    if (aik != 0.0) pi[k] += coef * aik;
                }
            }
        }
        if (!ok) continue;

        // Clean up: drop tiny coefficients (relaxing the rhs safely), check dynamism.
        double maxAbs = 0.0;
        for (double p : pi) maxAbs = std::max(maxAbs, std::abs(p));
        if (maxAbs < 1e-9) continue;
        double minAbs = INF;
        for (int k = 0; k < n_ && ok; ++k) {
            const double p = pi[k];
            if (p == 0.0) continue;
            if (std::abs(p) < 1e-9 * maxAbs) {
                // remove p x_k from a ">=" cut: subtract its largest possible value
                const double hi = p > 0 ? ub_[k] : lb_[k];
                if (!std::isfinite(hi)) { ok = false; break; }
                rhs -= p * hi;
                pi[k] = 0.0;
                continue;
            }
            minAbs = std::min(minAbs, std::abs(p));
        }
        if (!ok || maxAbs / minAbs > 1e6) continue;

        double act = 0.0, norm2 = 0.0;
        for (int k = 0; k < n_; ++k) {
            act += pi[k] * x_[k];
            norm2 += pi[k] * pi[k];
        }
        const double viol = rhs - act;
        const double eff = viol / std::sqrt(norm2);
        if (viol <= 1e-6 * (1.0 + std::abs(rhs)) || eff < 1e-5) continue;
        cands.push_back({std::move(pi), rhs, eff});
    }

    // stable_sort: ties keep row order, so results do not depend on the standard library (and match Java).
    std::stable_sort(cands.begin(), cands.end(), [](const Cand& a, const Cand& b) { return a.eff > b.eff; });
    std::vector<Constraint> out;
    std::vector<const Cand*> kept;
    for (const Cand& c : cands) {
        if (static_cast<int>(out.size()) >= maxCuts) break;
        bool parallel = false;
        for (const Cand* k : kept) {
            double dot = 0, na = 0, nb = 0;
            for (int j = 0; j < n_; ++j) {
                dot += c.pi[j] * k->pi[j];
                na += c.pi[j] * c.pi[j];
                nb += k->pi[j] * k->pi[j];
            }
            if (dot / std::sqrt(na * nb) > 0.98) { parallel = true; break; }
        }
        if (parallel) continue;
        kept.push_back(&c);
        Constraint con;
        for (int j = 0; j < n_; ++j)
            if (c.pi[j] != 0.0) con.coefs[j] = c.pi[j];
        con.sense = Sense::GE;
        con.rhs = c.rhs;
        out.push_back(std::move(con));
    }
    return out;
}

LPResult lpMin(const Model& M, const std::vector<double>& lb, const std::vector<double>& ub, double objSign,
               long maxIters) {
    LPEngine E(M, objSign);
    E.setAllColBounds(lb, ub);
    LPResult res;
    res.status = E.solve(maxIters);
    res.iterations = E.iterations();
    if (res.status == LPStatus::Optimal) {
        res.x = E.colValues();
        res.objective = E.objective();
    }
    return res;
}

}  // namespace mcplex::detail
