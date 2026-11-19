package minicplex;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * MIP presolve: bound propagation, coefficient tightening, redundant rows. Variables are never
 * removed, so a solution of the presolved model is directly a solution of the original one.
 * Line-by-line port of {@code src/presolve.cpp}.
 */
final class Presolve {
    private Presolve() {}

    private static final double INF = Double.POSITIVE_INFINITY;

    static final class Stats {
        int boundsTightened = 0;
        int coefsTightened = 0;
        int rowsRemoved = 0;
    }

    private static final class Activity {
        double fin = 0.0;  // finite part
        int inf = 0;       // number of infinite contributions
        double asMin() { return inf > 0 ? -INF : fin; }
        double asMax() { return inf > 0 ? INF : fin; }
    }

    private static boolean finite(double v) { return !Double.isInfinite(v) && !Double.isNaN(v); }

    private static Activity minActivity(Map<Integer, Double> row, double[] lb, double[] ub) {
        Activity a = new Activity();
        for (Map.Entry<Integer, Double> e : row.entrySet()) {
            double c = e.getValue();
            double t = c > 0 ? c * lb[e.getKey()] : c * ub[e.getKey()];
            if (finite(t)) a.fin += t; else ++a.inf;
        }
        return a;
    }

    private static Activity maxActivity(Map<Integer, Double> row, double[] lb, double[] ub) {
        Activity a = new Activity();
        for (Map.Entry<Integer, Double> e : row.entrySet()) {
            double c = e.getValue();
            double t = c > 0 ? c * ub[e.getKey()] : c * lb[e.getKey()];
            if (finite(t)) a.fin += t; else ++a.inf;
        }
        return a;
    }

    /** Activity of the row without the variable whose own contribution is term. */
    private static double rest(Activity a, double term) {
        if (!finite(term)) return a.inf == 1 ? a.fin : Double.NaN;
        return a.inf == 0 ? a.fin - term : Double.NaN;
    }

    /** Returns false if infeasibility is proven. Modifies W.constraints, lb and ub. */
    static boolean run(Model W, double[] lb, double[] ub, boolean[] isInt, Stats st) {
        final double feasTol = 1e-6;
        for (int pass = 0; pass < 20; ++pass) {
            boolean changed = false;
            List<Constraint> kept = new ArrayList<>(W.constraints.size());
            for (Constraint c : W.constraints) {
                if (c.coefs.isEmpty()) {
                    boolean ok = (c.sense == Sense.LE && 0 <= c.rhs + feasTol)
                            || (c.sense == Sense.GE && 0 >= c.rhs - feasTol)
                            || (c.sense == Sense.EQ && Math.abs(c.rhs) <= feasTol);
                    if (!ok) return false;
                    ++st.rowsRemoved;
                    changed = true;
                    continue;
                }
                double tol = feasTol * (1.0 + Math.abs(c.rhs));
                Activity mn = minActivity(c.coefs, lb, ub), mx = maxActivity(c.coefs, lb, ub);
                boolean le = c.sense != Sense.GE, ge = c.sense != Sense.LE;
                if (le && mn.asMin() > c.rhs + tol) return false;
                if (ge && mx.asMax() < c.rhs - tol) return false;
                // Redundant row?
                if (c.sense == Sense.LE && mx.asMax() <= c.rhs + 1e-9) { ++st.rowsRemoved; changed = true; continue; }
                if (c.sense == Sense.GE && mn.asMin() >= c.rhs - 1e-9) { ++st.rowsRemoved; changed = true; continue; }

                // Bound propagation.
                for (Map.Entry<Integer, Double> e : c.coefs.entrySet()) {
                    int k = e.getKey();
                    double a = e.getValue();
                    if (Math.abs(a) < 1e-9) continue;
                    if (le) {
                        double r = rest(mn, a > 0 ? a * lb[k] : a * ub[k]);
                        if (finite(r)) {
                            double v = (c.rhs - r) / a;
                            changed |= a > 0 ? tightenUb(k, v, lb, ub, isInt, st) : tightenLb(k, v, lb, ub, isInt, st);
                        }
                    }
                    if (ge) {
                        double r = rest(mx, a > 0 ? a * ub[k] : a * lb[k]);
                        if (finite(r)) {
                            double v = (c.rhs - r) / a;
                            changed |= a > 0 ? tightenLb(k, v, lb, ub, isInt, st) : tightenUb(k, v, lb, ub, isInt, st);
                        }
                    }
                    if (lb[k] > ub[k] + 1e-6) return false;
                    mn = minActivity(c.coefs, lb, ub);
                    mx = maxActivity(c.coefs, lb, ub);
                }

                // Coefficient tightening on binaries (written as  s * row <= s * rhs).
                if (c.sense != Sense.EQ) {
                    double s = (c.sense == Sense.LE) ? 1.0 : -1.0;
                    for (Map.Entry<Integer, Double> e : c.coefs.entrySet()) {
                        int k = e.getKey();
                        if (!isInt[k] || lb[k] != 0.0 || ub[k] != 1.0) continue;
                        Activity U;  // maximum of s*row
                        if (s > 0) U = maxActivity(c.coefs, lb, ub);
                        else { U = minActivity(c.coefs, lb, ub); U.fin = -U.fin; }
                        if (U.inf > 0) break;
                        double ck = s * e.getValue(), b = s * c.rhs;
                        double d = ck > 0 ? b - (U.fin - ck) : b - (U.fin + ck);
                        if (d <= 1e-6 * (1.0 + Math.abs(b))) continue;
                        if (ck > 0) {
                            e.setValue(s * (ck - d));
                            c.rhs = s * (b - d);
                        } else {
                            e.setValue(s * (ck + d));
                        }
                        ++st.coefsTightened;
                        changed = true;
                    }
                }
                kept.add(c);
            }
            W.constraints.clear();
            W.constraints.addAll(kept);
            if (!changed) break;
        }
        return true;
    }

    private static boolean tightenLb(int k, double v, double[] lb, double[] ub, boolean[] isInt, Stats st) {
        if (isInt[k]) v = Math.ceil(v - 1e-6);
        else v -= 1e-9 * (1.0 + Math.abs(v));  // stay safely outside round-off
        double range = finite(ub[k]) && finite(lb[k]) ? ub[k] - lb[k] : INF;
        if (v > lb[k] + 1e-6 * (1.0 + Math.abs(v))
                && (isInt[k] || !finite(lb[k]) || v - lb[k] > 1e-3 * Math.max(1.0, range))) {
            lb[k] = v;
            ++st.boundsTightened;
            return true;
        }
        return false;
    }

    private static boolean tightenUb(int k, double v, double[] lb, double[] ub, boolean[] isInt, Stats st) {
        if (isInt[k]) v = Math.floor(v + 1e-6);
        else v += 1e-9 * (1.0 + Math.abs(v));
        double range = finite(ub[k]) && finite(lb[k]) ? ub[k] - lb[k] : INF;
        if (v < ub[k] - 1e-6 * (1.0 + Math.abs(v))
                && (isInt[k] || !finite(ub[k]) || ub[k] - v > 1e-3 * Math.max(1.0, range))) {
            ub[k] = v;
            ++st.boundsTightened;
            return true;
        }
        return false;
    }
}
