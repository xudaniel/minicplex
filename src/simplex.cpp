// Two-phase primal simplex on a dense tableau.
//
// The model  min c'x  s.t.  A x (<=,>=,=) b,  l <= x <= u  is converted to
// standard form  min c'y  s.t.  A' y = b',  y >= 0,  b' >= 0  by
//   * shifting variables by their finite bound (x = l + y  or  x = u - y),
//   * splitting free variables (x = y+ - y-),
//   * turning finite ranges into extra rows (y <= u - l),
//   * adding slack / surplus columns and, where needed, artificials.
// Phase 1 minimises the sum of artificials; phase 2 the real objective.
// Pricing is Dantzig's rule, switching to Bland's rule after a run of
// degenerate pivots so that the method cannot cycle.

#include <algorithm>
#include <cmath>

#include "solver.hpp"

namespace mcplex::detail {
namespace {

constexpr double kPivTol = 1e-9;
constexpr double kOptTol = 1e-9;

class Tableau {
public:
    int m, n;  // constraint rows, columns (rhs is column n, objective is row m)
    std::vector<double> a;
    std::vector<int> basis;

    Tableau(int rows, int cols)
        : m(rows), n(cols), a(static_cast<size_t>(rows + 1) * (cols + 1), 0.0), basis(rows, -1) {}

    double& at(int i, int j) { return a[static_cast<size_t>(i) * (n + 1) + j]; }
    double rhs(int i) { return at(i, n); }

    void pivot(int r, int c) {
        double* pr = &at(r, 0);
        const double inv = 1.0 / pr[c];
        for (int j = 0; j <= n; ++j) pr[j] *= inv;
        pr[c] = 1.0;
        for (int i = 0; i <= m; ++i) {
            if (i == r) continue;
            double* pi = &at(i, 0);
            const double f = pi[c];
            if (f == 0.0) continue;
            for (int j = 0; j <= n; ++j) pi[j] -= f * pr[j];
            pi[c] = 0.0;
            if (i < m && pi[n] < 0.0 && pi[n] > -1e-11) pi[n] = 0.0;  // numerical noise
        }
        basis[r] = c;
    }
};

LPStatus iterate(Tableau& T, const std::vector<char>& allowed, long& iters, long maxIters) {
    int degenerate = 0;
    for (;;) {
        if (iters >= maxIters) return LPStatus::IterationLimit;
        const bool bland = degenerate > 30;

        int enter = -1;
        double best = -kOptTol;
        for (int j = 0; j < T.n; ++j) {
            if (!allowed[j]) continue;
            const double d = T.at(T.m, j);
            if (d < best) {
                enter = j;
                if (bland) break;
                best = d;
            }
        }
        if (enter < 0) return LPStatus::Optimal;

        int leave = -1;
        double minRatio = INF;
        for (int i = 0; i < T.m; ++i) {
            const double aij = T.at(i, enter);
            if (aij <= kPivTol) continue;
            const double r = T.rhs(i) / aij;
            bool take = leave < 0 || r < minRatio - 1e-12;
            if (!take && r <= minRatio + 1e-12)
                take = bland ? T.basis[i] < T.basis[leave] : aij > T.at(leave, enter);
            if (take) {
                minRatio = r;
                leave = i;
            }
        }
        if (leave < 0) return LPStatus::Unbounded;

        degenerate = (minRatio <= 1e-12) ? degenerate + 1 : 0;
        T.pivot(leave, enter);
        ++iters;
    }
}

}  // namespace

LPResult lpMin(const Model& M, const std::vector<double>& lb, const std::vector<double>& ub,
               double objSign, long maxIters) {
    LPResult res;
    const int nv = M.numVars();

    // ---- 1. map model variables to non-negative columns -------------------
    std::vector<double> offset(nv, 0.0);
    std::vector<int> colP(nv, -1), colN(nv, -1);
    struct BoundRow { int col; double ub; };
    std::vector<BoundRow> boundRows;
    int ncol = 0;
    for (int j = 0; j < nv; ++j) {
        const double l = lb[j], u = ub[j];
        if (l > u + 1e-9 || l == INF || u == -INF) {
            res.status = LPStatus::Infeasible;
            return res;
        }
        const bool lf = std::isfinite(l), uf = std::isfinite(u);
        if (lf && uf && u - l <= 1e-12) {
            offset[j] = l;  // fixed variable: no column needed
        } else if (lf) {
            offset[j] = l;
            colP[j] = ncol++;
            if (uf) boundRows.push_back({colP[j], u - l});
        } else if (uf) {
            offset[j] = u;
            colN[j] = ncol++;
        } else {
            colP[j] = ncol++;
            colN[j] = ncol++;
        }
    }

    // ---- 2. build rows -----------------------------------------------------
    const int nc0 = M.numConstrs();
    const int m = nc0 + static_cast<int>(boundRows.size());
    std::vector<std::vector<double>> A(m, std::vector<double>(ncol, 0.0));
    std::vector<double> b(m, 0.0);
    std::vector<Sense> sense(m, Sense::LE);
    for (int i = 0; i < nc0; ++i) {
        const Constraint& c = M.constraints[i];
        double r = c.rhs;
        for (const auto& [k, v] : c.coefs) {
            r -= v * offset[k];
            if (colP[k] >= 0) A[i][colP[k]] += v;
            if (colN[k] >= 0) A[i][colN[k]] -= v;
        }
        b[i] = r;
        sense[i] = c.sense;
    }
    for (size_t t = 0; t < boundRows.size(); ++t) {
        const int i = nc0 + static_cast<int>(t);
        A[i][boundRows[t].col] = 1.0;
        b[i] = boundRows[t].ub;
    }

    // ---- 3. slacks, sign normalisation, artificials ------------------------
    int nc = ncol;
    std::vector<int> slackCol(m, -1);
    std::vector<double> slackCoef(m, 0.0);
    for (int i = 0; i < m; ++i) {
        if (sense[i] == Sense::EQ) continue;
        slackCol[i] = nc++;
        slackCoef[i] = (sense[i] == Sense::LE) ? 1.0 : -1.0;
    }
    for (int i = 0; i < m; ++i) {
        if (b[i] < 0) {
            for (double& v : A[i]) v = -v;
            b[i] = -b[i];
            slackCoef[i] = -slackCoef[i];
        }
    }
    const int firstArt = nc;
    std::vector<int> artCol(m, -1);
    for (int i = 0; i < m; ++i)
        if (slackCoef[i] != 1.0) artCol[i] = nc++;
    const int nArt = nc - firstArt;

    Tableau T(m, nc);
    double maxB = 0.0;
    for (int i = 0; i < m; ++i) {
        for (int j = 0; j < ncol; ++j) T.at(i, j) = A[i][j];
        if (slackCol[i] >= 0) T.at(i, slackCol[i]) = slackCoef[i];
        if (artCol[i] >= 0) T.at(i, artCol[i]) = 1.0;
        T.at(i, nc) = b[i];
        T.basis[i] = (artCol[i] >= 0) ? artCol[i] : slackCol[i];
        maxB = std::max(maxB, b[i]);
    }
    std::vector<char> allowed(nc, 1);
    long iters = 0;

    // ---- 4. phase 1 ---------------------------------------------------------
    if (nArt > 0) {
        for (int j = firstArt; j < nc; ++j) T.at(m, j) = 1.0;
        for (int i = 0; i < m; ++i)
            if (artCol[i] >= 0)
                for (int j = 0; j <= nc; ++j) T.at(m, j) -= T.at(i, j);
        LPStatus st = iterate(T, allowed, iters, maxIters);
        res.iterations = iters;
        if (st == LPStatus::IterationLimit) {
            res.status = st;
            return res;
        }
        const double infeas = -T.at(m, nc);
        if (infeas > 1e-7 * (1.0 + maxB)) {
            res.status = LPStatus::Infeasible;
            return res;
        }
        // Drive remaining (zero-valued) artificials out of the basis.
        for (int i = 0; i < m; ++i) {
            if (T.basis[i] < firstArt) continue;
            int best = -1;
            double bestAbs = 1e-9;
            for (int j = 0; j < firstArt; ++j)
                if (std::abs(T.at(i, j)) > bestAbs) {
                    bestAbs = std::abs(T.at(i, j));
                    best = j;
                }
            if (best >= 0) T.pivot(i, best);  // else: redundant row, harmless
        }
        for (int j = firstArt; j < nc; ++j) allowed[j] = 0;
    }

    // ---- 5. phase 2 ---------------------------------------------------------
    std::vector<double> cost(nc, 0.0);
    for (const auto& [k, v] : M.objective.terms) {
        const double c = objSign * v;
        if (colP[k] >= 0) cost[colP[k]] += c;
        if (colN[k] >= 0) cost[colN[k]] -= c;
    }
    for (int j = 0; j < nc; ++j) T.at(m, j) = cost[j];
    T.at(m, nc) = 0.0;
    for (int i = 0; i < m; ++i) {
        const double cb = cost[T.basis[i]];
        if (cb != 0.0)
            for (int j = 0; j <= nc; ++j) T.at(m, j) -= cb * T.at(i, j);
    }
    LPStatus st = iterate(T, allowed, iters, maxIters);
    res.iterations = iters;
    if (st != LPStatus::Optimal) {
        res.status = st;
        return res;
    }

    // ---- 6. recover x -------------------------------------------------------
    std::vector<double> colVal(nc, 0.0);
    for (int i = 0; i < m; ++i) colVal[T.basis[i]] = T.rhs(i);
    res.x.assign(nv, 0.0);
    for (int j = 0; j < nv; ++j) {
        double v = offset[j];
        if (colP[j] >= 0) v += colVal[colP[j]];
        if (colN[j] >= 0) v -= colVal[colN[j]];
        res.x[j] = v;
    }
    res.objective = objSign * evalObjective(M, res.x);
    res.status = LPStatus::Optimal;
    return res;
}

}  // namespace mcplex::detail
