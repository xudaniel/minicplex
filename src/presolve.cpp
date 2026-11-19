// MIP presolve: bound propagation, coefficient tightening, redundant rows.
//
// Only reductions that keep every variable are used, so a solution of the
// presolved model is directly a solution of the original one (no postsolve).
//
//  * Bound propagation.  For a row  sum a_j x_j <= b  the other variables
//    contribute at least minRest, so  a_k x_k <= b - minRest  bounds x_k
//    (similarly for >= rows with maxRest). Integer bounds are rounded.
//  * Coefficient tightening (binary x_k in a <= row with finite maximum
//    activity U).  If the row cannot be tight when x_k sits on its "loose"
//    value, the coefficient can be reduced by the slack d without removing
//    any integer point, which strengthens the LP relaxation ("big-M"):
//      a_k > 0, d = b - (U - a_k) > 0:   a_k -= d, b -= d
//      a_k < 0, d = b - (U + a_k) > 0:   a_k += d
//  * A row whose activity can never violate it is removed; a row that can
//    never be satisfied proves infeasibility.

#include <cmath>

#include "solver.hpp"

namespace mcplex::detail {
namespace {

struct Activity {
    double fin = 0.0;  // finite part
    int inf = 0;       // number of infinite contributions
    double asMin() const { return inf ? -INF : fin; }  // as a minimum activity
    double asMax() const { return inf ? INF : fin; }   // as a maximum activity
};

Activity minActivity(const std::map<int, double>& row, const std::vector<double>& lb,
                     const std::vector<double>& ub) {
    Activity a;
    for (const auto& [k, c] : row) {
        const double t = c > 0 ? c * lb[k] : c * ub[k];
        if (std::isfinite(t)) a.fin += t; else ++a.inf;
    }
    return a;
}
Activity maxActivity(const std::map<int, double>& row, const std::vector<double>& lb,
                     const std::vector<double>& ub) {
    Activity a;
    for (const auto& [k, c] : row) {
        const double t = c > 0 ? c * ub[k] : c * lb[k];
        if (std::isfinite(t)) a.fin += t; else ++a.inf;
    }
    return a;
}

// Activity of the row without variable k (term = k's own contribution).
double rest(const Activity& a, double term) {
    if (!std::isfinite(term)) return a.inf == 1 ? a.fin : NAN;
    return a.inf == 0 ? a.fin - term : NAN;
}

}  // namespace

bool presolve(Model& W, std::vector<double>& lb, std::vector<double>& ub, const std::vector<char>& isInt,
              PresolveStats& st) {
    const double feasTol = 1e-6;
    auto tightenLb = [&](int k, double v) {
        if (isInt[k]) v = std::ceil(v - 1e-6);
        else v -= 1e-9 * (1.0 + std::abs(v));  // stay safely outside round-off
        const double range = std::isfinite(ub[k]) && std::isfinite(lb[k]) ? ub[k] - lb[k] : INF;
        if (v > lb[k] + 1e-6 * (1.0 + std::abs(v)) &&
            (isInt[k] || !std::isfinite(lb[k]) || v - lb[k] > 1e-3 * std::max(1.0, range))) {
            lb[k] = v;
            ++st.boundsTightened;
            return true;
        }
        return false;
    };
    auto tightenUb = [&](int k, double v) {
        if (isInt[k]) v = std::floor(v + 1e-6);
        else v += 1e-9 * (1.0 + std::abs(v));
        const double range = std::isfinite(ub[k]) && std::isfinite(lb[k]) ? ub[k] - lb[k] : INF;
        if (v < ub[k] - 1e-6 * (1.0 + std::abs(v)) &&
            (isInt[k] || !std::isfinite(ub[k]) || ub[k] - v > 1e-3 * std::max(1.0, range))) {
            ub[k] = v;
            ++st.boundsTightened;
            return true;
        }
        return false;
    };

    for (int pass = 0; pass < 20; ++pass) {
        bool changed = false;
        std::vector<Constraint> kept;
        kept.reserve(W.constraints.size());
        for (Constraint& c : W.constraints) {
            if (c.coefs.empty()) {
                const bool ok = (c.sense == Sense::LE && 0 <= c.rhs + feasTol) ||
                                (c.sense == Sense::GE && 0 >= c.rhs - feasTol) ||
                                (c.sense == Sense::EQ && std::abs(c.rhs) <= feasTol);
                if (!ok) return false;
                ++st.rowsRemoved;
                changed = true;
                continue;
            }
            const double tol = feasTol * (1.0 + std::abs(c.rhs));
            Activity mn = minActivity(c.coefs, lb, ub), mx = maxActivity(c.coefs, lb, ub);
            const bool le = c.sense != Sense::GE, ge = c.sense != Sense::LE;
            if (le && mn.asMin() > c.rhs + tol) return false;
            if (ge && mx.asMax() < c.rhs - tol) return false;
            // Redundant row?
            if (c.sense == Sense::LE && mx.asMax() <= c.rhs + 1e-9) { ++st.rowsRemoved; changed = true; continue; }
            if (c.sense == Sense::GE && mn.asMin() >= c.rhs - 1e-9) { ++st.rowsRemoved; changed = true; continue; }

            // Bound propagation.
            for (const auto& [k, a] : c.coefs) {
                if (std::abs(a) < 1e-9) continue;
                if (le) {
                    const double r = rest(mn, a > 0 ? a * lb[k] : a * ub[k]);
                    if (std::isfinite(r)) {
                        const double v = (c.rhs - r) / a;
                        changed |= a > 0 ? tightenUb(k, v) : tightenLb(k, v);
                    }
                }
                if (ge) {
                    const double r = rest(mx, a > 0 ? a * ub[k] : a * lb[k]);
                    if (std::isfinite(r)) {
                        const double v = (c.rhs - r) / a;
                        changed |= a > 0 ? tightenLb(k, v) : tightenUb(k, v);
                    }
                }
                if (lb[k] > ub[k] + 1e-6) return false;
                mn = minActivity(c.coefs, lb, ub);
                mx = maxActivity(c.coefs, lb, ub);
            }

            // Coefficient tightening on binaries (written as  s * row <= s * rhs).
            if (c.sense != Sense::EQ) {
                const double s = (c.sense == Sense::LE) ? 1.0 : -1.0;
                for (auto& [k, a] : c.coefs) {
                    if (!isInt[k] || lb[k] != 0.0 || ub[k] != 1.0) continue;
                    // maximum of s*row
                    const Activity U = s > 0 ? maxActivity(c.coefs, lb, ub) : [&] {
                        Activity t = minActivity(c.coefs, lb, ub);
                        t.fin = -t.fin;
                        return t;
                    }();
                    if (U.inf) break;
                    const double ck = s * a, b = s * c.rhs;
                    const double d = ck > 0 ? b - (U.fin - ck) : b - (U.fin + ck);
                    if (d <= 1e-6 * (1.0 + std::abs(b))) continue;
                    if (ck > 0) {
                        a = s * (ck - d);
                        c.rhs = s * (b - d);
                    } else {
                        a = s * (ck + d);
                    }
                    ++st.coefsTightened;
                    changed = true;
                }
            }
            kept.push_back(std::move(c));
        }
        W.constraints = std::move(kept);
        if (!changed) break;
    }
    return true;
}

}  // namespace mcplex::detail
