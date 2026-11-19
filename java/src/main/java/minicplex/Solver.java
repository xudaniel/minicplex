package minicplex;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.PriorityQueue;

/**
 * Solves an LP or MIP: presolve, root Gomory cuts, then branch and bound on top of {@link LPEngine}.
 *
 * <ul>
 *   <li>plunging: after branching, one child is solved immediately from the parent's tableau
 *       (warm start, dual simplex); the sibling is stored with the parent's basis</li>
 *   <li>node selection when a plunge ends: smallest LP bound first</li>
 *   <li>reliability branching: pseudo-costs, initialised by strong branching</li>
 *   <li>pruning inside the LP: the dual simplex stops once the bound reaches the incumbent</li>
 *   <li>primal heuristic: round the LP solution, polish, verify</li>
 * </ul>
 *
 * <p>Line-by-line port of {@code src/branch_and_bound.cpp}.
 */
public final class Solver {
    private Solver() {}

    private static final double INF = Double.POSITIVE_INFINITY;

    public static Result solve(Model M) { return solve(M, new Params()); }

    public static Result solve(Model M, Params P) { return new Run(M, P).solve(); }

    /** Value of the objective (model sense) at x. */
    public static double evalObjective(Model M, double[] x) {
        double v = M.objective.constant;
        for (Map.Entry<Integer, Double> t : M.objective.terms.entrySet()) v += t.getValue() * x[t.getKey()];
        return v;
    }

    public static boolean checkFeasible(Model M, double[] x) { return checkFeasible(M, x, 1e-6, true); }

    public static boolean checkFeasible(Model M, double[] x, double tol) { return checkFeasible(M, x, tol, true); }

    /** Bounds, integrality and every constraint, with tolerance tol * (1 + |rhs|). */
    public static boolean checkFeasible(Model M, double[] x, double tol, boolean checkInt) {
        for (int j = 0; j < M.numVars(); ++j) {
            VarInfo v = M.vars.get(j);
            if (x[j] < v.lb - tol || x[j] > v.ub + tol) return false;
            if (checkInt && M.isInteger(j) && Math.abs(x[j] - cround(x[j])) > tol) return false;
        }
        for (Constraint c : M.constraints) {
            double lhs = 0.0;
            for (Map.Entry<Integer, Double> t : c.coefs.entrySet()) lhs += t.getValue() * x[t.getKey()];
            double t = tol * (1.0 + Math.abs(c.rhs));
            if (c.sense == Sense.LE && lhs > c.rhs + t) return false;
            if (c.sense == Sense.GE && lhs < c.rhs - t) return false;
            if (c.sense == Sense.EQ && Math.abs(lhs - c.rhs) > t) return false;
        }
        return true;
    }

    /** C++ std::round: halfway cases away from zero (Math.round/rint behave differently). */
    static double cround(double v) { return Math.signum(v) * Math.floor(Math.abs(v) + 0.5); }

    private static boolean finite(double v) { return !Double.isInfinite(v) && !Double.isNaN(v); }

    // ------------------------------------------------------------ search state

    private static final class Node {
        double[] lb, ub;
        double bound;          // lower bound (internal min sense) inherited from the parent
        int depth;
        LPEngine.Basis basis;  // parent's optimal basis (warm start)
        int branchVar = -1;    // how this node was created (for pseudo-cost learning)
        int dir = 0;           // 0 = down branch, 1 = up branch
        double dist = 0.0;     // distance the variable was moved
        double parentObj = 0.0;
        long seq = 0;          // insertion order: final tie-break, so the search order is fully defined

        Node(double[] lb, double[] ub, double bound, int depth, LPEngine.Basis basis) {
            this.lb = lb;
            this.ub = ub;
            this.bound = bound;
            this.depth = depth;
            this.basis = basis;
        }
    }

    /** Average objective increase per unit change, learned separately for down and up branches. */
    private static final class PseudoCosts {
        final double[][] sum = new double[2][];
        final int[][] cnt = new int[2][];
        final double[] totSum = {0, 0};
        final int[] totCnt = {0, 0};

        PseudoCosts(int n) {
            for (int d = 0; d < 2; ++d) { sum[d] = new double[n]; cnt[d] = new int[n]; }
        }
        void update(int j, int d, double gainPerUnit) {
            sum[d][j] += gainPerUnit;
            ++cnt[d][j];
            totSum[d] += gainPerUnit;
            ++totCnt[d];
        }
        double get(int j, int d) {
            if (cnt[d][j] > 0) return sum[d][j] / cnt[d][j];
            return totCnt[d] > 0 ? totSum[d] / totCnt[d] : 1.0;  // uninitialised: global average
        }
    }

    private static final class Run {
        final Model M;
        final Params P;
        final long t0 = System.nanoTime();
        final Result R = new Result();
        final int nv;
        final double sgn;
        final long maxIt;
        final List<Integer> ints = new ArrayList<>();
        double[] lb, ub;
        Model LM;                   // model given to the LP engine
        LPEngine E;
        boolean objIntegral = true;
        double objConst;
        double inc = INF;           // incumbent, internal min sense
        double[] incX = null;
        boolean hasContinuous = false;
        final PriorityQueue<Node> open = new PriorityQueue<>((a, b) ->
                a.bound != b.bound ? Double.compare(a.bound, b.bound)
                : a.depth != b.depth ? Integer.compare(b.depth, a.depth)
                : Long.compare(b.seq, a.seq));  // newest first
        long nodeSeq = 0;
        Node cur;
        boolean haveCur;

        Run(Model M, Params P) {
            this.M = M;
            this.P = P;
            nv = M.numVars();
            sgn = M.objSense == ObjSense.MAXIMIZE ? -1.0 : 1.0;
            maxIt = 200000 + 50L * (nv + M.numConstrs());
        }

        double elapsed() { return (System.nanoTime() - t0) / 1e9; }

        double strengthen(double b) {
            if (!objIntegral || !finite(b)) return b;
            return Math.ceil(b - objConst - 1e-6) + objConst;
        }
        boolean closeEnough(double bound, double incumbent) {
            return incumbent - bound <= Math.max(P.mipAbsGap, P.mipGap * Math.max(1.0, Math.abs(incumbent)));
        }
        double cutoff() {
            if (incX == null) return INF;
            double c = inc - Math.max(P.mipAbsGap, P.mipGap * Math.max(1.0, Math.abs(inc)));
            if (objIntegral) c = Math.min(c, inc - 1.0 + 1e-6);
            return c;
        }

        /**
         * Accept a candidate only after "polishing": fix the integer variables at their rounded
         * values and re-solve the continuous part with a fresh LP. Returns 1 if accepted, 0 if not
         * better than the incumbent, -1 if rejected as infeasible.
         */
        int tryIncumbent(double[] xIn) {
            double[] x = xIn.clone();
            for (int j : ints) x[j] = cround(x[j]);
            // Cheap filter; with continuous variables the polishing LP decides feasibility.
            if (!checkFeasible(M, x, hasContinuous ? 1e-4 : 1e-6)) return -1;
            if (sgn * evalObjective(M, x) >= inc + 1e-6 * (1.0 + Math.abs(inc))) return 0;
            if (hasContinuous) {
                double[] plb = new double[nv], pub = new double[nv];
                for (int j = 0; j < nv; ++j) { plb[j] = M.vars.get(j).lb; pub[j] = M.vars.get(j).ub; }
                for (int j : ints) { plb[j] = x[j]; pub[j] = x[j]; }
                LPEngine.LPResult pol = LPEngine.lpMin(M, plb, pub, sgn, maxIt);
                if (pol.status != LPEngine.LPStatus.OPTIMAL) return -1;
                x = pol.x;
                for (int j : ints) x[j] = plb[j];
            }
            if (!checkFeasible(M, x, 1e-7)) return -1;
            double v = sgn * evalObjective(M, x);
            if (v < inc - 1e-12) {
                inc = v;
                incX = x;
                return 1;
            }
            return 0;
        }

        double bestBound() {
            double b = inc;
            if (!open.isEmpty()) b = Math.min(b, open.peek().bound);
            if (haveCur) b = Math.min(b, cur.bound);
            return b;
        }

        void logLine(String mark, double nodeObj) {
            double bnd = bestBound();
            double gap = finite(inc) ? Math.abs(inc - bnd) / Math.max(1e-10, Math.abs(inc)) : INF;
            System.out.println(String.format(Locale.ROOT, "%1s%8d %7d %15s %15s %15s %7.2f%%", mark, R.nodes, open.size(),
                    Fmt.g(sgn * nodeObj), finite(inc) ? Fmt.g(sgn * inc) : "nan", Fmt.g(sgn * bnd), 100 * gap));
        }

        void newEngine(Model model) {
            E = new LPEngine(model, sgn);
            E.setAllColBounds(lb, ub);
            E.setTrace(P.trace);
        }

        Result solve() {
            lb = new double[nv];
            ub = new double[nv];
            for (int j = 0; j < nv; ++j) {
                lb[j] = M.vars.get(j).lb;
                ub[j] = M.vars.get(j).ub;
                if (!P.relaxIntegrality && M.isInteger(j)) {
                    ints.add(j);
                    if (finite(lb[j])) lb[j] = Math.ceil(lb[j] - P.intTol);
                    if (finite(ub[j])) ub[j] = Math.floor(ub[j] + P.intTol);
                }
            }

            // ---------------- presolve (MIP only) ----------------
            LM = M;
            if (P.presolve && !ints.isEmpty()) {
                boolean[] isIntCol = new boolean[nv];
                for (int j : ints) isIntCol[j] = true;
                Model PM = new Model(M);
                Presolve.Stats ps = new Presolve.Stats();
                boolean feasible = Presolve.run(PM, lb, ub, isIntCol, ps);
                if (P.verbose || P.trace)
                    System.out.println("Presolve: " + ps.boundsTightened + " bounds tightened, " + ps.coefsTightened
                            + " coefficients tightened, " + ps.rowsRemoved + " rows removed" + (feasible ? "" : ", INFEASIBLE"));
                if (!feasible) {
                    R.status = Status.INFEASIBLE;
                    R.seconds = elapsed();
                    return R;
                }
                LM = PM;
            }
            newEngine(LM);

            // ---------------- pure LP ----------------
            if (ints.isEmpty()) {
                LPEngine.LPStatus st = E.solve(maxIt);
                R.lpIterations = E.iterations();
                R.seconds = elapsed();
                switch (st) {
                    case OPTIMAL -> {
                        R.status = Status.OPTIMAL;
                        R.hasSolution = true;
                        R.x = E.colValues();
                        R.duals = E.rowDuals();
                        R.reducedCosts = E.colReducedCosts();
                        R.objective = R.bestBound = sgn * E.objective();
                        R.gap = 0.0;
                    }
                    case INFEASIBLE -> R.status = Status.INFEASIBLE;
                    case UNBOUNDED -> R.status = Status.UNBOUNDED;
                    default -> R.status = Status.ITERATION_LIMIT;
                }
                if (P.verbose)
                    System.out.println(String.format(Locale.ROOT, "LP solved: %s, %d simplex iterations, %.3f s",
                            R.status, R.lpIterations, R.seconds));
                return R;
            }

            // ---------------- MIP: branch and bound ----------------
            for (Map.Entry<Integer, Double> t : M.objective.terms.entrySet()) {
                double c = t.getValue();
                if (c != 0.0 && (!M.isInteger(t.getKey()) || c != cround(c))) objIntegral = false;
            }
            objConst = sgn * M.objective.constant;
            for (int j = 0; j < nv; ++j) hasContinuous |= !M.isInteger(j) || P.relaxIntegrality;

            long cutIters = rootCuts();

            PseudoCosts pc = new PseudoCosts(nv);
            cur = new Node(lb.clone(), ub.clone(), -INF, 0, null);
            haveCur = true;  // root: engine already holds bounds and the slack basis
            boolean incomplete = false;
            Status stop = Status.OPTIMAL;

            if (P.verbose)
                System.out.println(String.format(Locale.ROOT, "%9s %7s %15s %15s %15s %8s", "Node", "Left", "Objective",
                        "Best Integer", "Best Bound", "Gap"));

            for (;;) {
                if (!haveCur) {
                    if (open.isEmpty()) break;
                    if (incX != null && closeEnough(open.peek().bound, inc)) break;
                    cur = open.poll();
                    haveCur = true;
                    if (P.trace) System.out.println("\n（下潜结束，从队列取出界最好的节点，恢复它保存的基）");
                    E.setAllColBounds(cur.lb, cur.ub);
                    E.loadBasis(cur.basis);
                }
                if (R.nodes >= P.nodeLimit) { stop = Status.NODE_LIMIT; break; }
                if (elapsed() > P.timeLimit) { stop = Status.TIME_LIMIT; break; }

                ++R.nodes;
                if (P.trace) {
                    StringBuilder sb = new StringBuilder("\n[节点 " + R.nodes + "] 深度 " + cur.depth);
                    if (cur.branchVar >= 0)
                        sb.append("，由 ").append(M.vars.get(cur.branchVar).name).append(' ')
                          .append(cur.dir == 1 ? "≥ " + (long) cur.lb[cur.branchVar] : "≤ " + (long) cur.ub[cur.branchVar])
                          .append(" 分出来");
                    System.out.println(sb);
                }
                LPEngine.LPStatus st = E.solve(maxIt, cutoff());

                if (st == LPEngine.LPStatus.INFEASIBLE || st == LPEngine.LPStatus.CUTOFF) {
                    if (P.trace)
                        System.out.println("  剪枝：" + (st == LPEngine.LPStatus.INFEASIBLE ? "这种情况不可行" : "这种情况最好也比已有整数解差"));
                    haveCur = false;
                    continue;
                }
                if (st == LPEngine.LPStatus.UNBOUNDED) {
                    if (R.nodes == 1) {
                        R.status = Status.INFEASIBLE_OR_UNBOUNDED;
                        R.lpIterations = E.iterations();
                        R.seconds = elapsed();
                        return R;
                    }
                    incomplete = true;  // should not happen: children are restrictions
                    haveCur = false;
                    continue;
                }
                if (st == LPEngine.LPStatus.ITERATION_LIMIT) {
                    incomplete = true;
                    haveCur = false;
                    continue;
                }

                final double[] x = E.colValues();
                final double lpObj = E.objective();
                if (cur.branchVar >= 0 && cur.dist > 1e-9)
                    pc.update(cur.branchVar, cur.dir, Math.max(0.0, lpObj - cur.parentObj) / cur.dist);
                final double nodeBound = strengthen(lpObj);
                cur.bound = nodeBound;
                if (incX != null && closeEnough(nodeBound, inc)) {
                    if (P.trace) System.out.println("  剪枝：界 " + Fmt.g(sgn * nodeBound) + " 不比已有整数解 " + Fmt.g(sgn * inc) + " 好");
                    haveCur = false;
                    continue;
                }

                // Reliability branching: unobserved candidates are evaluated by strong branching.
                final double HUGE = 1e12;
                List<double[]> sbGain = new ArrayList<>();
                List<Integer> sbVar = new ArrayList<>();
                boolean pruneNode = false;
                if (P.branching == Branching.PSEUDO_COST) {
                    List<double[]> unrel = new ArrayList<>();  // {frac, j}
                    for (int j : ints) {
                        double f = x[j] - Math.floor(x[j]);
                        double frac = Math.min(f, 1.0 - f);
                        if (frac > P.intTol && (pc.cnt[0][j] < 1 || pc.cnt[1][j] < 1)) unrel.add(new double[] {frac, j});
                    }
                    unrel.sort((a, b) -> Double.compare(b[0], a[0]));
                    if (unrel.size() > 8) unrel = new ArrayList<>(unrel.subList(0, 8));
                    if (!unrel.isEmpty()) {
                        LPEngine.Basis B = E.basis();
                        E.setTrace(false);
                        for (double[] u : unrel) {
                            int j = (int) u[1];
                            double v = x[j], fl = Math.floor(v), ce = Math.ceil(v);
                            double[] g = new double[2];
                            for (int d = 0; d < 2; ++d) {
                                double olb = cur.lb[j], oub = cur.ub[j];
                                if (d == 0) E.setColBounds(j, olb, fl); else E.setColBounds(j, ce, oub);
                                LPEngine.LPStatus s2 = E.solve(40, cutoff());
                                double dist = d == 0 ? v - fl : ce - v;
                                if (s2 == LPEngine.LPStatus.INFEASIBLE) {
                                    g[d] = HUGE;
                                } else if (s2 == LPEngine.LPStatus.CUTOFF) {
                                    g[d] = Math.max(cutoff() - lpObj, 1e-6);
                                    pc.update(j, d, g[d] / dist);
                                    g[d] = HUGE;  // this side would be pruned immediately
                                } else {
                                    g[d] = Math.max(0.0, E.objective() - lpObj);
                                    if (s2 == LPEngine.LPStatus.OPTIMAL) pc.update(j, d, g[d] / dist);
                                }
                                E.setColBounds(j, olb, oub);
                                E.loadBasis(B);
                            }
                            sbVar.add(j);
                            sbGain.add(g);
                            if (P.trace) {
                                System.out.println("  强分支试算 " + M.vars.get(j).name + " = " + Fmt.g(x[j], 4) + "：向下目标变差 "
                                        + sbFmt(g[0], HUGE) + "，向上变差 " + sbFmt(g[1], HUGE));
                            }
                            if (g[0] >= HUGE && g[1] >= HUGE) { pruneNode = true; break; }
                        }
                    }
                }
                E.setTrace(P.trace);
                if (pruneNode) {  // both children are infeasible or cut off
                    if (P.trace) System.out.println("  剪枝：强分支发现某个变量两侧都不可行或被截断");
                    haveCur = false;
                    continue;
                }

                // Branching variable: pseudo-cost product score, or most fractional.
                int bj = -1;
                double bestScore = -1.0, bestFrac = 0.0;
                for (int j : ints) {
                    double f = x[j] - Math.floor(x[j]);
                    double frac = Math.min(f, 1.0 - f);
                    if (frac <= P.intTol) continue;
                    double score = frac;
                    if (P.branching == Branching.PSEUDO_COST) {
                        double down = pc.get(j, 0) * f, up = pc.get(j, 1) * (1.0 - f);
                        for (int k = 0; k < sbVar.size(); ++k)
                            if (sbVar.get(k) == j) { down = sbGain.get(k)[0]; up = sbGain.get(k)[1]; }
                        score = Math.max(down, 1e-6) * Math.max(up, 1e-6);
                    }
                    if (score > bestScore * (1 + 1e-9) || (score >= bestScore * (1 - 1e-9) && frac > bestFrac)) {
                        bestScore = score;
                        bestFrac = frac;
                        bj = j;
                    }
                }
                if (bj < 0) {  // LP solution is integral
                    int res = tryIncumbent(x);
                    if (P.trace) {
                        if (res == 1) System.out.println("  LP 解全是整数，成为新的最优整数解：" + Fmt.g(sgn * inc));
                        else if (res == 0) System.out.println("  LP 解全是整数，但不比已有整数解好");
                        else System.out.println("  LP 解全是整数，但严格检查不可行（只在数值误差范围内成立），放弃");
                    }
                    if (res == 1 && P.verbose) logLine("*", lpObj);
                    haveCur = false;
                    continue;
                }
                if (tryIncumbent(x) == 1) {
                    if (P.trace) {
                        StringBuilder sb = new StringBuilder("  取整启发式：把 LP 解四舍五入后得到可行的整数解（");
                        for (int j = 0, k = 0; j < nv; ++j)
                            if (M.isInteger(j)) sb.append(k++ > 0 ? "，" : "").append(M.vars.get(j).name).append(" = ").append(Fmt.g(incX[j]));
                        sb.append("），新的最优整数解：").append(Fmt.g(sgn * inc));
                        System.out.println(sb);
                    }
                    if (P.verbose) logLine("H", lpObj);
                    if (closeEnough(nodeBound, inc)) {
                        haveCur = false;
                        continue;
                    }
                }

                // Branch: plunge into the child on the rounding side, store the sibling.
                double v = x[bj];
                double fl = Math.floor(v), ce = Math.ceil(v);
                boolean goUp = (v - fl) >= 0.5;
                Node sib = new Node(cur.lb.clone(), cur.ub.clone(), nodeBound, cur.depth + 1, E.basis());
                if (goUp) sib.ub[bj] = fl; else sib.lb[bj] = ce;
                sib.branchVar = bj;
                sib.dir = goUp ? 0 : 1;
                sib.dist = goUp ? v - fl : ce - v;
                sib.parentObj = lpObj;
                sib.seq = ++nodeSeq;
                open.add(sib);

                if (goUp) cur.lb[bj] = ce; else cur.ub[bj] = fl;
                cur.depth += 1;
                cur.branchVar = bj;
                cur.dir = goUp ? 1 : 0;
                cur.dist = goUp ? ce - v : v - fl;
                cur.parentObj = lpObj;
                E.setColBounds(bj, cur.lb[bj], cur.ub[bj]);  // warm start: same tableau

                if (P.trace) {
                    String name = M.vars.get(bj).name;
                    System.out.println("  分支：" + name + " = " + Fmt.g(v, 4) + " 不是整数 → 先走 " + name + (goUp ? " ≥ " : " ≤ ")
                            + String.format(Locale.ROOT, "%.0f", goUp ? ce : fl) + "（下潜，接着用当前单纯形表），" + name
                            + (goUp ? " ≤ " : " ≥ ") + String.format(Locale.ROOT, "%.0f", goUp ? fl : ce) + " 放进队列");
                }
                if (P.verbose && R.nodes % P.logEvery == 0) logLine("", lpObj);
            }

            R.seconds = elapsed();
            R.lpIterations = E.iterations() + cutIters;
            double bound = bestBound();
            if (incX == null) {
                R.status = stop != Status.OPTIMAL ? stop : incomplete ? Status.ITERATION_LIMIT : Status.INFEASIBLE;
            } else {
                R.status = stop;
                if (stop == Status.OPTIMAL && incomplete) R.status = Status.ITERATION_LIMIT;
                R.hasSolution = true;
                R.x = incX;
                R.objective = sgn * inc;
                R.bestBound = sgn * bound;
                R.gap = Math.abs(inc - bound) / Math.max(1e-10, Math.abs(inc));
            }
            if (P.verbose)
                System.out.println(String.format(Locale.ROOT, "B&B done: %s, %d nodes, %d simplex iterations, %.3f s",
                        R.status, R.nodes, R.lpIterations, R.seconds));
            return R;
        }

        private static String sbFmt(double v, double huge) {
            if (v >= huge) return "剪掉";
            String s = String.format(Locale.ROOT, "%f", v);
            return s.substring(0, Math.min(6, s.length()));
        }

        /**
         * Rounds of Gomory mixed-integer cuts at the root. Each round's cuts become new rows; the LP
         * is re-optimised from the previous basis (new slacks basic) with the dual simplex. Cuts that
         * are not tight at the end are dropped again. Returns the iterations spent.
         */
        private long rootCuts() {
            long cutIters = 0;
            if (P.cutRounds <= 0 || E.solve(maxIt) != LPEngine.LPStatus.OPTIMAL) return 0;
            boolean[] isIntCol = new boolean[nv];
            for (int j : ints) isIntCol[j] = true;
            Model W = new Model(LM);
            final int m0 = W.numConstrs();
            double obj = E.objective();
            for (int round = 0; round < P.cutRounds; ++round) {
                double[] x = E.colValues();
                boolean fractional = false;
                for (int j : ints) fractional |= Math.abs(x[j] - cround(x[j])) > P.intTol;
                if (!fractional) break;
                List<Constraint> cuts = E.gomoryCuts(isIntCol, Math.max(5, Math.min(20, W.numConstrs())));
                if (cuts.isEmpty()) break;
                int nCuts = cuts.size();
                LPEngine.Basis B = E.basis();
                int[] head = Arrays.copyOf(B.head, B.head.length + nCuts);
                byte[] stat = Arrays.copyOf(B.stat, B.stat.length + nCuts);
                int k = 0;
                for (Constraint c : cuts) {
                    if (P.trace) {
                        StringBuilder sb = new StringBuilder("[割平面] 新割 gmi" + (W.numConstrs() - m0 + 1) + "：");
                        boolean first = true;
                        for (Map.Entry<Integer, Double> t : c.coefs.entrySet()) {
                            double a = t.getValue();
                            sb.append(first ? "" : (a < 0 ? " - " : " + ")).append(Fmt.g(first ? a : Math.abs(a)))
                              .append(' ').append(M.vars.get(t.getKey()).name);
                            first = false;
                        }
                        sb.append(" ≥ ").append(Fmt.g(c.rhs));
                        System.out.println(sb);
                    }
                    head[B.head.length + k] = nv + W.numConstrs();  // new slack starts basic
                    stat[B.stat.length + k] = LPEngine.BASIC;
                    ++k;
                    W.addConstr(c, "gmi" + (W.numConstrs() - m0 + 1));
                }
                cutIters += E.iterations();
                newEngine(W);
                E.loadBasis(new LPEngine.Basis(head, stat), true);
                if (P.trace) System.out.println("[割平面] 第 " + (round + 1) + " 轮：加入 " + nCuts + " 个 Gomory 割，重新求解根节点");
                if (E.solve(maxIt) != LPEngine.LPStatus.OPTIMAL) break;
                double nobj = E.objective();
                if (P.trace) System.out.println("[割平面] 根节点的界：" + Fmt.g(sgn * obj) + " → " + Fmt.g(sgn * nobj));
                boolean stalled = nobj - obj < 1e-4 * (1.0 + Math.abs(obj));
                obj = nobj;
                if (stalled) break;
            }
            // Keep only the cuts that are tight at the final root LP.
            if (W.numConstrs() > m0) {
                double[] x = E.colValues();
                Model K = new Model(LM);
                for (int i = m0; i < W.numConstrs(); ++i) {
                    Constraint c = W.constraints.get(i);
                    double act = 0.0;
                    for (Map.Entry<Integer, Double> t : c.coefs.entrySet()) act += t.getValue() * x[t.getKey()];
                    if (act <= c.rhs + 1e-6 * (1.0 + Math.abs(c.rhs))) K.addConstr(new Constraint(c));
                }
                R.cuts = K.numConstrs() - m0;
                cutIters += E.iterations();
                newEngine(K);
            }
            if (P.verbose && R.cuts > 0)
                System.out.println("Root cuts: " + R.cuts + " Gomory cuts kept, root bound " + Fmt.g(sgn * obj));
            return cutIters;
        }
    }
}
