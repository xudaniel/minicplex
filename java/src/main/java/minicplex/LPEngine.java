package minicplex;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

/**
 * Bounded-variable simplex engine (primal + dual) on a dense tableau.
 *
 * <p>Computational form
 * <pre>
 *     A x - s = 0,    l &lt;= x &lt;= u,    rlo &lt;= s &lt;= rhi
 * </pre>
 * Each constraint row i gets a slack s_i equal to its activity a_i x, with bounds taken from the
 * row sense (&lt;=: (-inf, b], &gt;=: [b, inf), =: [b, b]). Variable bounds are handled implicitly: a
 * nonbasic variable sits at its lower bound, its upper bound, or at zero if it is free. So bounds
 * never add rows and no artificial columns are needed: the all-slack basis is always a valid start.
 *
 * <p>The tableau T = B^-1 [A | -I] (m x (n+m)) is kept explicitly together with the reduced costs
 * d and the values x of all variables, so that x_B = - sum_{j nonbasic} T[:, j] x_j.
 *
 * <ul>
 *   <li>Primal simplex: composite phase 1 (minimise the sum of bound violations), then phase 2,
 *       with bound flips.</li>
 *   <li>Dual simplex: used whenever the basis is dual feasible, e.g. after branch and bound
 *       tightens a bound of a basic variable.</li>
 *   <li>Anti-cycling via Bland's rule after a run of degenerate pivots; the tableau is periodically
 *       rebuilt from the original matrix to stop round-off from accumulating.</li>
 * </ul>
 *
 * <p>This is a line-by-line port of {@code src/simplex.cpp}.
 */
final class LPEngine {
    enum LPStatus { OPTIMAL, INFEASIBLE, UNBOUNDED, ITERATION_LIMIT, CUTOFF }

    /** A simplex basis that can be saved and restored (warm start). */
    static final class Basis {
        int[] head;   // basic variable of each row
        byte[] stat;  // status of every variable (structural + slack)

        Basis(int[] head, byte[] stat) {
            this.head = head;
            this.stat = stat;
        }

        Basis copy() { return new Basis(head.clone(), stat.clone()); }
    }

    private static final double INF = Double.POSITIVE_INFINITY;
    private static final double PRIMAL_TOL = 1e-7;  // bound violation allowed (scaled)
    private static final double DUAL_TOL = 1e-9;    // reduced-cost tolerance
    private static final double PIVOT_TOL = 1e-9;   // smallest acceptable pivot element
    private static final int BLAND_AFTER = 50;      // degenerate pivots before Bland's rule

    static final byte BASIC = 0, LOWER = 1, UPPER = 2, FREE = 3, FIXED = 4, UNSET = -1;

    private final int n, m, N;
    private final double[] A;  // original constraint matrix, m x n (row major)
    private final double[] c, lb, ub;
    private final double objConst, objSign;
    private final String[] names;
    private double[] T;  // B^-1 [A | -I], m x N
    private double[] d;  // reduced costs
    private double[] x;  // values of all variables
    private int[] head;
    private byte[] stat;
    private long iters = 0;
    private long pivotsSinceRefactor = 0;
    private long pivotsSinceRecompute = 0;
    private boolean valuesDirty = true;
    private boolean trace = false;
    private final int[] nz;
    private int nzCount;

    LPEngine(Model M, double objSign) {
        n = M.numVars();
        m = M.numConstrs();
        N = n + m;
        A = new double[m * n];
        c = new double[N];
        lb = new double[N];
        ub = new double[N];
        Arrays.fill(ub, INF);
        for (int i = 0; i < m; ++i) {
            Constraint con = M.constraints.get(i);
            for (Map.Entry<Integer, Double> t : con.coefs.entrySet()) A[i * n + t.getKey()] += t.getValue();
            int s = n + i;
            lb[s] = (con.sense == Sense.LE) ? -INF : con.rhs;
            ub[s] = (con.sense == Sense.GE) ? INF : con.rhs;
        }
        for (int j = 0; j < n; ++j) {
            lb[j] = M.vars.get(j).lb;
            ub[j] = M.vars.get(j).ub;
        }
        for (Map.Entry<Integer, Double> t : M.objective.terms.entrySet()) c[t.getKey()] += objSign * t.getValue();
        objConst = objSign * M.objective.constant;
        this.objSign = objSign;
        names = new String[N];
        for (int j = 0; j < n; ++j) names[j] = M.vars.get(j).name;
        for (int i = 0; i < m; ++i) names[n + i] = "s(" + M.constraints.get(i).name + ")";
        nz = new int[N];

        // All-slack starting basis.
        int[] h = new int[m];
        for (int i = 0; i < m; ++i) h[i] = n + i;
        byte[] st = new byte[N];
        Arrays.fill(st, UNSET);  // choose default status
        loadBasis(new Basis(h, st), true);
    }

    void setTrace(boolean on) { trace = on; }
    long iterations() { return iters; }
    int numRows() { return m; }
    Basis basis() { return new Basis(head.clone(), stat.clone()); }

    private double T(int i, int j) { return T[i * N + j]; }
    private static boolean finite(double v) { return !Double.isInfinite(v) && !Double.isNaN(v); }

    private byte defaultStatus(int j) {
        boolean lf = finite(lb[j]), uf = finite(ub[j]);
        if (lf && uf && lb[j] == ub[j]) return FIXED;
        if (lf && uf) return c[j] < 0 ? UPPER : LOWER;  // pick the dual-feasible side
        if (lf) return LOWER;
        if (uf) return UPPER;
        return FREE;
    }

    private double nonbasicValue(int j) {
        switch (stat[j]) {
            case LOWER: case FIXED: return lb[j];
            case UPPER: return ub[j];
            default: return 0.0;
        }
    }

    private boolean validStatus(byte s, int j) {
        return (s == LOWER && finite(lb[j])) || (s == UPPER && finite(ub[j]))
                || (s == FREE && !finite(lb[j]) && !finite(ub[j])) || (s == FIXED && lb[j] == ub[j]);
    }

    void loadBasis(Basis b) { loadBasis(b, false); }

    /**
     * Move to basis b and recompute x and d. Incremental (default): pivot the missing columns into
     * the current tableau. fromScratch: rebuild T from the original matrix (removes round-off).
     */
    void loadBasis(Basis b, boolean fromScratch) {
        if (!fromScratch && head != null && head.length == m && T != null
                && pivotsSinceRefactor < Math.max(200, 2 * m)) {
            boolean[] wanted = new boolean[N];
            for (int v : b.head) wanted[v] = true;
            boolean ok = true;
            for (int q : b.head) {
                if (stat[q] == BASIC) continue;
                int r = -1;
                double best = 1e-7;
                for (int i = 0; i < m; ++i) {
                    if (wanted[head[i]]) continue;
                    if (Math.abs(T(i, q)) > best) {
                        best = Math.abs(T(i, q));
                        r = i;
                    }
                }
                if (r < 0) { ok = false; break; }
                stat[head[r]] = LOWER;  // fixed below
                pivot(r, q);
                stat[q] = BASIC;
            }
            if (ok) {
                for (int j = 0; j < N; ++j) {
                    if (stat[j] == BASIC) continue;
                    byte s = j < b.stat.length ? b.stat[j] : UNSET;
                    stat[j] = validStatus(s, j) ? s : defaultStatus(j);
                }
                recomputeValues();
                recomputeReducedCosts();
                return;
            }
        }
        T = new double[m * N];
        for (int i = 0; i < m; ++i) {
            for (int j = 0; j < n; ++j) T[i * N + j] = -A[i * n + j];
            T[i * N + n + i] = 1.0;
        }
        head = new int[m];
        for (int i = 0; i < m; ++i) head[i] = n + i;
        stat = new byte[N];
        Arrays.fill(stat, LOWER);
        for (int i = 0; i < m; ++i) stat[n + i] = BASIC;

        boolean[] wanted = new boolean[N];
        for (int v : b.head) wanted[v] = true;
        d = new double[N];  // pivot() updates d, keep it defined
        for (int q : b.head) {
            if (q >= n) continue;  // slacks are basic already
            int r = -1;
            double best = PIVOT_TOL;
            for (int i = 0; i < m; ++i) {
                int h = head[i];
                if (h < n || wanted[h]) continue;  // row already holds a wanted variable
                if (Math.abs(T(i, q)) > best) {
                    best = Math.abs(T(i, q));
                    r = i;
                }
            }
            if (r >= 0) {
                stat[head[r]] = LOWER;  // placeholder, fixed below
                pivot(r, q);
                stat[q] = BASIC;
            }
        }
        // Nonbasic statuses: keep the saved one when it is still valid.
        for (int j = 0; j < N; ++j) {
            if (stat[j] == BASIC) continue;
            byte s = j < b.stat.length ? b.stat[j] : UNSET;
            stat[j] = validStatus(s, j) ? s : defaultStatus(j);
        }
        x = new double[N];
        recomputeValues();
        recomputeReducedCosts();
        pivotsSinceRefactor = 0;
    }

    private void recomputeValues() {
        valuesDirty = false;
        pivotsSinceRecompute = 0;
        for (int j = 0; j < N; ++j)
            if (stat[j] != BASIC) x[j] = nonbasicValue(j);
        for (int i = 0; i < m; ++i) {
            double v = 0.0;
            int row = i * N;
            for (int j = 0; j < N; ++j)
                if (stat[j] != BASIC && x[j] != 0.0) v -= T[row + j] * x[j];
            x[head[i]] = v;
        }
    }

    private void recomputeReducedCosts() {
        d = c.clone();
        for (int i = 0; i < m; ++i) {
            double cb = c[head[i]];
            if (cb == 0.0) continue;
            int row = i * N;
            for (int j = 0; j < N; ++j) d[j] -= cb * T[row + j];
        }
        for (int i = 0; i < m; ++i) d[head[i]] = 0.0;
    }

    private void pivot(int r, int q) {
        final int pr = r * N;
        final double inv = 1.0 / T[pr + q];
        nzCount = 0;
        for (int j = 0; j < N; ++j) {
            if (T[pr + j] == 0.0) continue;
            T[pr + j] *= inv;
            nz[nzCount++] = j;
        }
        T[pr + q] = 1.0;
        for (int i = 0; i < m; ++i) {
            if (i == r) continue;
            final int pi = i * N;
            final double f = T[pi + q];
            if (f == 0.0) continue;
            for (int k = 0; k < nzCount; ++k) {
                int j = nz[k];
                T[pi + j] -= f * T[pr + j];
            }
            T[pi + q] = 0.0;
        }
        final double f = d[q];
        if (f != 0.0) {
            for (int k = 0; k < nzCount; ++k) {
                int j = nz[k];
                d[j] -= f * T[pr + j];
            }
            d[q] = 0.0;
        }
        head[r] = q;
        ++pivotsSinceRefactor;
        ++pivotsSinceRecompute;
    }

    void setColBounds(int j, double l, double u) {
        lb[j] = l;
        ub[j] = u;
        if (stat[j] == BASIC) return;  // may become primal infeasible: dual simplex fixes it
        double old = x[j];
        if (!validStatus(stat[j], j)) stat[j] = defaultStatus(j);
        if (l == u) stat[j] = FIXED;
        x[j] = nonbasicValue(j);
        double delta = x[j] - old;
        if (delta != 0.0)
            for (int i = 0; i < m; ++i) x[head[i]] -= T(i, j) * delta;
    }

    void setAllColBounds(double[] l, double[] u) {
        for (int j = 0; j < n; ++j) {
            lb[j] = l[j];
            ub[j] = u[j];
        }
        valuesDirty = true;
    }

    /** objSign * (c'x + c0), i.e. the internal (minimisation) objective. */
    double objective() {
        double v = objConst;
        for (int j = 0; j < n; ++j) v += c[j] * x[j];
        return v;
    }

    private double realObjective() { return objSign * objective(); }

    double[] colValues() { return Arrays.copyOf(x, n); }

    /** Shadow prices in the model's objective sense (reduced costs of the slacks, recomputed from T). */
    double[] rowDuals() {
        double[] y = new double[m];
        for (int k = 0; k < m; ++k) {
            int j = n + k;
            if (stat[j] == BASIC) continue;  // non-binding row: price 0
            double dj = c[j];
            for (int i = 0; i < m; ++i) dj -= c[head[i]] * T(i, j);
            y[k] = Math.abs(dj) < 1e-12 ? 0.0 : objSign * dj;
        }
        return y;
    }

    /** Reduced costs of the structural variables in the model's objective sense. */
    double[] colReducedCosts() {
        double[] r = new double[n];
        for (int j = 0; j < n; ++j) {
            if (stat[j] == BASIC) continue;
            double dj = c[j];
            for (int i = 0; i < m; ++i) dj -= c[head[i]] * T(i, j);
            r[j] = Math.abs(dj) < 1e-12 ? 0.0 : objSign * dj;
        }
        return r;
    }

    /** &gt; 0: amount by which variable v violates its bounds. */
    private double infeasibility(int v) {
        double tl = PRIMAL_TOL * (1.0 + Math.abs(lb[v]));
        double tu = PRIMAL_TOL * (1.0 + Math.abs(ub[v]));
        if (x[v] < lb[v] - tl) return lb[v] - x[v];
        if (x[v] > ub[v] + tu) return x[v] - ub[v];
        return 0.0;
    }

    /**
     * Put boxed nonbasic variables on the bound that matches the sign of their reduced cost.
     * Returns false if some variable cannot be made dual feasible.
     */
    private boolean makeDualFeasible() {
        boolean ok = true;
        for (int j = 0; j < N; ++j) {
            byte s = stat[j];
            if (s == BASIC || s == FIXED) continue;
            double dj = d[j];
            byte want = s;
            if (s == LOWER && dj < -DUAL_TOL) want = UPPER;
            else if (s == UPPER && dj > DUAL_TOL) want = LOWER;
            else if (s == FREE && Math.abs(dj) > DUAL_TOL) { ok = false; continue; }
            if (want == s) continue;
            if ((want == UPPER && !finite(ub[j])) || (want == LOWER && !finite(lb[j]))) {
                ok = false;
                continue;
            }
            double old = x[j];
            stat[j] = want;
            x[j] = nonbasicValue(j);
            double delta = x[j] - old;
            for (int i = 0; i < m; ++i) x[head[i]] -= T(i, j) * delta;
        }
        return ok;
    }

    private LPStatus primal(long maxIters) {
        int degenerate = 0;
        double[] dd = new double[N];
        double[] rowCost = new double[m];
        for (;;) {
            if (iters >= maxIters) return LPStatus.ITERATION_LIMIT;
            if (pivotsSinceRefactor > Math.max(200, 2 * m)) loadBasis(basis(), true);

            // Phase-1 cost: -1 for basics below their lower bound, +1 above the upper.
            boolean phase1 = false;
            for (int i = 0; i < m; ++i) {
                int v = head[i];
                rowCost[i] = 0.0;
                if (infeasibility(v) > 0.0) {
                    rowCost[i] = x[v] < lb[v] ? -1.0 : 1.0;
                    phase1 = true;
                }
            }
            if (phase1) {
                Arrays.fill(dd, 0.0);
                for (int i = 0; i < m; ++i) {
                    if (rowCost[i] == 0.0) continue;
                    int row = i * N;
                    for (int j = 0; j < N; ++j) dd[j] -= rowCost[i] * T[row + j];
                }
            }
            final double[] price = phase1 ? dd : d;

            // Pricing.
            boolean bland = degenerate > BLAND_AFTER;
            int q = -1, dir = 0;
            double best = 0.0;
            for (int j = 0; j < N; ++j) {
                byte s = stat[j];
                if (s == BASIC || s == FIXED) continue;
                double dj = price[j];
                int djDir = 0;
                if ((s == LOWER || s == FREE) && dj < -DUAL_TOL) djDir = +1;
                else if ((s == UPPER || s == FREE) && dj > DUAL_TOL) djDir = -1;
                if (djDir == 0) continue;
                if (Math.abs(dj) > best) {
                    best = Math.abs(dj);
                    q = j;
                    dir = djDir;
                    if (bland) break;
                }
            }
            if (q < 0) return phase1 ? LPStatus.INFEASIBLE : LPStatus.OPTIMAL;

            // Ratio test. alpha_i = change of basic i per unit step of x_q.
            double tMax = (finite(lb[q]) && finite(ub[q])) ? ub[q] - lb[q] : INF;
            int r = -1;
            double tBest = INF, aBest = 0.0, target = 0.0;
            for (int i = 0; i < m; ++i) {
                double alpha = -T(i, q) * dir;
                if (Math.abs(alpha) < PIVOT_TOL) continue;
                int v = head[i];
                double xv = x[v];
                double t, tg;
                double inf = phase1 ? infeasibility(v) : 0.0;
                if (inf > 0.0 && xv < lb[v]) {          // below: stops when it reaches lb
                    if (alpha <= 0) continue;
                    t = (lb[v] - xv) / alpha;
                    tg = lb[v];
                } else if (inf > 0.0) {                 // above: stops when it reaches ub
                    if (alpha >= 0) continue;
                    t = (ub[v] - xv) / alpha;
                    tg = ub[v];
                } else if (alpha > 0) {
                    if (!finite(ub[v])) continue;
                    t = (ub[v] - xv) / alpha;
                    tg = ub[v];
                } else {
                    if (!finite(lb[v])) continue;
                    t = (lb[v] - xv) / alpha;
                    tg = lb[v];
                }
                if (t < 0) t = 0;
                boolean take = r < 0 || t < tBest - 1e-12;
                if (!take && t <= tBest + 1e-12) take = bland ? v < head[r] : Math.abs(alpha) > aBest;
                if (take) {
                    r = i;
                    tBest = t;
                    aBest = Math.abs(alpha);
                    target = tg;
                }
            }
            if (r < 0 && !finite(tMax))
                return phase1 ? LPStatus.ITERATION_LIMIT : LPStatus.UNBOUNDED;  // phase 1 cannot be unbounded

            boolean flip = tMax <= tBest;
            double t = flip ? tMax : tBest;
            if (trace) {
                System.out.print("    第 " + (iters + 1) + " 步（" + (phase1 ? "原始单纯形·第一阶段" : "原始单纯形·第二阶段") + "）："
                        + names[q] + " 进基（从" + (stat[q] == UPPER ? "上界" : stat[q] == FREE ? "0" : "下界")
                        + (dir > 0 ? "增大" : "减小") + "，既约成本 " + Fmt.g(price[q], 4) + "）");
                if (flip) System.out.println("，走到另一侧边界（bound flip），步长 " + Fmt.g(t, 4));
                else System.out.println("，" + names[head[r]] + " 离基停在" + (target == lb[head[r]] ? "下界" : "上界") + " "
                        + Fmt.g(target, 4) + "，步长 " + Fmt.g(t, 4));
            }
            if (t != 0.0) {
                x[q] += dir * t;
                for (int i = 0; i < m; ++i) {
                    double a = T(i, q);
                    if (a != 0.0) x[head[i]] -= a * dir * t;
                }
            }
            ++iters;
            degenerate = (t <= 1e-12) ? degenerate + 1 : 0;
            if (flip) {
                stat[q] = (dir > 0) ? UPPER : LOWER;
                x[q] = nonbasicValue(q);
                continue;
            }
            int leave = head[r];
            x[leave] = target;
            stat[leave] = (lb[leave] == ub[leave]) ? FIXED : (target == lb[leave] ? LOWER : UPPER);
            pivot(r, q);
            stat[q] = BASIC;
        }
    }

    private LPStatus dual(long maxIters, double cutoff) {
        int degenerate = 0;
        for (;;) {
            if (iters >= maxIters) return LPStatus.ITERATION_LIMIT;
            if (pivotsSinceRefactor > Math.max(200, 2 * m)) {
                loadBasis(basis(), true);
                if (!makeDualFeasible()) return primal(maxIters);
            }
            if (finite(cutoff) && objective() >= cutoff) return LPStatus.CUTOFF;

            // Leaving row: the most infeasible basic variable.
            boolean bland = degenerate > BLAND_AFTER;
            int r = -1;
            double worst = 0.0;
            for (int i = 0; i < m; ++i) {
                double inf = infeasibility(head[i]);
                if (inf <= 0.0) continue;
                if (bland ? (r < 0 || head[i] < head[r]) : inf > worst) {
                    worst = inf;
                    r = i;
                }
            }
            if (r < 0) return LPStatus.OPTIMAL;

            int v = head[r];
            boolean below = x[v] < lb[v];
            double target = below ? lb[v] : ub[v];

            // Entering column: keep reduced costs dual feasible (min |d_j / a_rj|).
            int q = -1;
            double bestRatio = INF, bestA = 0.0;
            for (int j = 0; j < N; ++j) {
                byte s = stat[j];
                if (s == BASIC || s == FIXED) continue;
                double a = T(r, j);
                if (Math.abs(a) < PIVOT_TOL) continue;
                // x_v changes by -a per unit increase of x_j.
                int dirNeeded = below ? (a < 0 ? +1 : -1) : (a > 0 ? +1 : -1);
                if (dirNeeded > 0 && s == UPPER) continue;
                if (dirNeeded < 0 && s == LOWER) continue;
                double ratio = Math.abs(d[j]) / Math.abs(a);
                boolean take = q < 0 || ratio < bestRatio - 1e-12;
                if (!take && ratio <= bestRatio + 1e-12) take = bland ? j < q : Math.abs(a) > bestA;
                if (take) {
                    q = j;
                    bestRatio = ratio;
                    bestA = Math.abs(a);
                }
            }
            if (q < 0) return LPStatus.INFEASIBLE;

            if (trace)
                System.out.println("    第 " + (iters + 1) + " 步（对偶单纯形）：" + names[v] + " = " + Fmt.g(x[v], 4) + " 越过"
                        + (below ? "下界" : "上界") + " " + Fmt.g(target, 4) + "，离基；" + names[q] + " 进基（比值 "
                        + Fmt.g(bestRatio, 4) + "）");
            double delta = (x[v] - target) / T(r, q);
            x[q] += delta;
            for (int i = 0; i < m; ++i) {
                double a = T(i, q);
                if (a != 0.0) x[head[i]] -= a * delta;
            }
            x[v] = target;
            stat[v] = (lb[v] == ub[v]) ? FIXED : (below ? LOWER : UPPER);
            pivot(r, q);
            stat[q] = BASIC;
            ++iters;
            degenerate = (bestRatio <= 1e-12) ? degenerate + 1 : 0;
        }
    }

    LPStatus solve(long maxIters) { return solve(maxIters, INF); }

    /** Minimise objSign * objective. Stops early with CUTOFF once the (dual) objective reaches cutoff. */
    LPStatus solve(long maxIters, double cutoff) {
        long limit = iters + maxIters;
        // Bounds of structurals may have changed wholesale: refresh nonbasic statuses.
        for (int j = 0; j < n; ++j) {
            if (stat[j] == BASIC) continue;
            byte s = stat[j];
            byte ns = (!validStatus(s, j) || lb[j] == ub[j]) ? defaultStatus(j) : s;
            if (ns != s || x[j] != valueFor(ns, j)) valuesDirty = true;
            stat[j] = ns;
        }
        for (int j = 0; j < n; ++j)
            if (lb[j] > ub[j] + 1e-9) return LPStatus.INFEASIBLE;
        if (valuesDirty) recomputeValues();

        for (int round = 0; round < 4; ++round) {
            boolean dualOk = makeDualFeasible();
            if (trace)
                System.out.println("  [LP] 当前基" + (dualOk ? "对偶可行" : "不是对偶可行") + " → 用" + (dualOk ? "对偶单纯形" : "原始单纯形"));
            LPStatus st = dualOk ? dual(limit, cutoff) : primal(limit);
            if (trace) {
                String[] label = {"最优", "不可行", "无界", "达到迭代上限", "被截断（不可能比已有整数解更好）"};
                StringBuilder sb = new StringBuilder("  [LP] 结果：").append(label[st.ordinal()]);
                if (st == LPStatus.OPTIMAL || st == LPStatus.CUTOFF) sb.append("，目标值 ").append(Fmt.g(realObjective(), 6));
                System.out.println(sb);
            }
            if (st != LPStatus.OPTIMAL) {
                if (st == LPStatus.INFEASIBLE && round < 3) {
                    // confirm with fresh values before declaring infeasibility
                    recomputeValues();
                    recomputeReducedCosts();
                    LPStatus again = makeDualFeasible() ? dual(limit, INF) : primal(limit);
                    if (again == LPStatus.INFEASIBLE) return LPStatus.INFEASIBLE;
                    continue;
                }
                return st;
            }
            // Verify optimality on freshly computed values (and, every so often, reduced costs).
            boolean refreshD = pivotsSinceRefactor > 50;
            if (pivotsSinceRecompute > 0) recomputeValues();
            if (refreshD) recomputeReducedCosts();
            boolean clean = true;
            for (int i = 0; i < m && clean; ++i) clean = infeasibility(head[i]) == 0.0;
            // Guard against round-off in T: slack values must agree with the original rows.
            for (int i = 0; i < m && clean; ++i) {
                double act = 0.0;
                int row = i * n;
                for (int k = 0; k < n; ++k)
                    if (A[row + k] != 0.0) act += A[row + k] * x[k];
                if (Math.abs(act - x[n + i]) > 1e-9 * (1.0 + Math.abs(act))) clean = false;
            }
            for (int j = 0; j < N && clean; ++j) {
                byte s = stat[j];
                if (s == BASIC || s == FIXED) continue;
                if ((s == LOWER || s == FREE) && d[j] < -1e-7) clean = false;
                if ((s == UPPER || s == FREE) && d[j] > 1e-7) clean = false;
            }
            if (clean) {
                if (finite(cutoff) && objective() >= cutoff) return LPStatus.CUTOFF;
                return LPStatus.OPTIMAL;
            }
            loadBasis(basis(), true);  // numerical trouble: refactor and continue
        }
        return LPStatus.ITERATION_LIMIT;
    }

    private double valueFor(byte s, int j) {
        switch (s) {
            case LOWER: case FIXED: return lb[j];
            case UPPER: return ub[j];
            default: return 0.0;
        }
    }

    // ------------------------------------------------------------ Gomory cuts

    private static boolean isIntegral(double v) { return finite(v) && Math.abs(v - Math.rint(v)) < 1e-9; }

    /**
     * Gomory mixed-integer cuts read off the current optimal tableau (see src/simplex.cpp for the
     * derivation). Returns at most maxCuts cuts of the form sum(coefs) &gt;= rhs, sorted by efficacy
     * and filtered for parallelism and dynamism.
     */
    List<Constraint> gomoryCuts(boolean[] isIntCol, int maxCuts) {
        boolean[] isInt = new boolean[N];
        for (int j = 0; j < n; ++j) isInt[j] = isIntCol[j];
        for (int i = 0; i < m; ++i) {
            boolean ok = true;
            for (int j = 0; j < n && ok; ++j) {
                double a = A[i * n + j];
                if (a != 0.0 && (!isIntCol[j] || !isIntegral(a))) ok = false;
            }
            isInt[n + i] = ok;
        }

        record Cand(double[] pi, double rhs, double eff) {}
        List<Cand> cands = new ArrayList<>();
        for (int r = 0; r < m; ++r) {
            int v = head[r];
            if (!isInt[v]) continue;
            double b = x[v];
            double f0 = b - Math.floor(b);
            if (f0 < 0.01 || f0 > 0.99) continue;  // nearly integral: numerically unsafe

            double[] pi = new double[n];  // cut in structural space: pi x >= rhs
            double rhs = 1.0;
            boolean ok = true;
            for (int j = 0; j < N && ok; ++j) {
                byte s = stat[j];
                if (s == BASIC || s == FIXED) continue;
                double t = T(r, j);
                if (Math.abs(t) < 1e-11) continue;
                if (s == FREE) { ok = false; break; }
                boolean atLower = (s == LOWER);
                double a = atLower ? t : -t;
                double bnd = atLower ? lb[j] : ub[j];
                double g;
                if (isInt[j] && isIntegral(bnd)) {
                    double fj = a - Math.floor(a);
                    g = (fj <= f0) ? fj / f0 : (1.0 - fj) / (1.0 - f0);
                } else {
                    g = (a >= 0) ? a / f0 : -a / (1.0 - f0);
                }
                if (g == 0.0) continue;
                // g * y_j  with  y_j = x_j - l_j  or  u_j - x_j
                double coef = atLower ? g : -g;
                rhs += atLower ? g * bnd : -g * bnd;
                if (j < n) {
                    pi[j] += coef;
                } else {  // slack: s_i = a_i x
                    int i = j - n;
                    for (int k = 0; k < n; ++k) {
                        double aik = A[i * n + k];
                        if (aik != 0.0) pi[k] += coef * aik;
                    }
                }
            }
            if (!ok) continue;

            // Clean up: drop tiny coefficients (relaxing the rhs safely), check dynamism.
            double maxAbs = 0.0;
            for (double p : pi) maxAbs = Math.max(maxAbs, Math.abs(p));
            if (maxAbs < 1e-9) continue;
            double minAbs = INF;
            for (int k = 0; k < n && ok; ++k) {
                double p = pi[k];
                if (p == 0.0) continue;
                if (Math.abs(p) < 1e-9 * maxAbs) {
                    double hi = p > 0 ? ub[k] : lb[k];  // remove p x_k from a ">=" cut
                    if (!finite(hi)) { ok = false; break; }
                    rhs -= p * hi;
                    pi[k] = 0.0;
                    continue;
                }
                minAbs = Math.min(minAbs, Math.abs(p));
            }
            if (!ok || maxAbs / minAbs > 1e6) continue;

            double act = 0.0, norm2 = 0.0;
            for (int k = 0; k < n; ++k) {
                act += pi[k] * x[k];
                norm2 += pi[k] * pi[k];
            }
            double viol = rhs - act;
            double eff = viol / Math.sqrt(norm2);
            if (viol <= 1e-6 * (1.0 + Math.abs(rhs)) || eff < 1e-5) continue;
            cands.add(new Cand(pi, rhs, eff));
        }

        cands.sort((a, b) -> Double.compare(b.eff(), a.eff()));
        List<Constraint> out = new ArrayList<>();
        List<Cand> kept = new ArrayList<>();
        for (Cand cd : cands) {
            if (out.size() >= maxCuts) break;
            boolean parallel = false;
            for (Cand k : kept) {
                double dot = 0, na = 0, nb = 0;
                for (int j = 0; j < n; ++j) {
                    dot += cd.pi()[j] * k.pi()[j];
                    na += cd.pi()[j] * cd.pi()[j];
                    nb += k.pi()[j] * k.pi()[j];
                }
                if (dot / Math.sqrt(na * nb) > 0.98) { parallel = true; break; }
            }
            if (parallel) continue;
            kept.add(cd);
            Constraint con = new Constraint();
            for (int j = 0; j < n; ++j)
                if (cd.pi()[j] != 0.0) con.coefs.put(j, cd.pi()[j]);
            con.sense = Sense.GE;
            con.rhs = cd.rhs();
            out.add(con);
        }
        return out;
    }

    // ------------------------------------------------------------ one-shot LP

    static final class LPResult {
        LPStatus status = LPStatus.INFEASIBLE;
        double objective = 0.0;  // objSign * (c'x + c0)
        double[] x;
        long iterations = 0;
    }

    /** Solve one LP from scratch with the given bounds (integrality ignored). */
    static LPResult lpMin(Model M, double[] l, double[] u, double objSign, long maxIters) {
        LPEngine E = new LPEngine(M, objSign);
        E.setAllColBounds(l, u);
        LPResult res = new LPResult();
        res.status = E.solve(maxIters);
        res.iterations = E.iterations();
        if (res.status == LPStatus.OPTIMAL) {
            res.x = E.colValues();
            res.objective = E.objective();
        }
        return res;
    }
}
