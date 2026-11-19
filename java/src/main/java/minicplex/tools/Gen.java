package minicplex.tools;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Random;

import minicplex.LinExpr;
import minicplex.Model;
import minicplex.ObjSense;
import minicplex.Var;
import minicplex.VarType;

/**
 * Random model generator (Java port of tools/gen_random.cpp; uses java.util.Random, so the models
 * differ from the C++ generator's for the same seed).
 *
 * <pre>
 *   Gen --kind mixed --count 300 --seed 1 --out fuzz/
 *   Gen --kind mkp   --count 3   --seed 7 --vars 35 --cons 5 --out bench/
 *   Gen --kind lp    --count 2   --seed 9 --vars 120 --cons 100 --out bench/
 * </pre>
 */
public final class Gen {
    private Gen() {}

    private static Random rng;
    private static int ri(int a, int b) { return a + rng.nextInt(b - a + 1); }
    private static double rr(double a, double b) { return a + (b - a) * rng.nextDouble(); }
    private static boolean coin(double p) { return rng.nextDouble() < p; }
    private static final double INF = Model.INF;
    private static double cround(double v) { return Math.signum(v) * Math.floor(Math.abs(v) + 0.5); }

    static Model genMixed(int nMax, int mMax) {
        Model M = new Model();
        int n = ri(2, nMax), m = ri(1, mMax);
        double[] x0 = new double[n];
        for (int j = 0; j < n; ++j) {
            double t = rr(0, 1);
            VarType type = t < 0.40 ? VarType.INTEGER : t < 0.55 ? VarType.BINARY : VarType.CONTINUOUS;
            double lb = coin(0.6) ? 0.0 : coin(0.75) ? -ri(1, 5) : -INF;
            double ub = coin(0.8) ? (Double.isFinite(lb) ? lb : 0.0) + ri(1, 10) : INF;
            if (type == VarType.BINARY) { lb = 0; ub = 1; }
            M.addVar(lb, ub, type, "x" + (j + 1));
            double lo = Double.isFinite(lb) ? lb : (Double.isFinite(ub) ? ub - 5 : -3);
            double hi = Double.isFinite(ub) ? ub : lo + 5;
            x0[j] = rr(lo, hi);
            if (type != VarType.CONTINUOUS) x0[j] = cround(x0[j]);
            x0[j] = Math.min(Math.max(x0[j], lb), ub);
        }
        for (int i = 0; i < m; ++i) {
            LinExpr e = new LinExpr();
            double act = 0;
            for (int j = 0; j < n; ++j) {
                if (!coin(0.6)) continue;
                double a = ri(-6, 6);
                if (coin(0.3)) a += 0.5;
                if (a == 0) continue;
                e = e.plus(a, new Var(j));
                act += a * x0[j];
            }
            int s = ri(0, 2);
            double rhs = cround(act);
            if (coin(0.1)) rhs = ri(-10, 10);  // may be infeasible
            if (s == 0) M.addConstr(e.le(coin(0.9) ? Math.ceil(act) + ri(0, 4) : rhs));
            else if (s == 1) M.addConstr(e.ge(coin(0.9) ? Math.floor(act) - ri(0, 4) : rhs));
            else M.addConstr(e.eq(coin(0.9) ? act : rhs));
        }
        LinExpr obj = new LinExpr();
        for (int j = 0; j < n; ++j) obj = obj.plus(ri(-5, 5), new Var(j));
        if (coin(0.2)) obj = obj.plus((double) ri(-20, 20));
        M.setObjective(obj, coin(0.5) ? ObjSense.MAXIMIZE : ObjSense.MINIMIZE);
        return M;
    }

    static Model genMkp(int n, int m) {
        Model M = new Model();
        Var[] x = new Var[n];
        for (int j = 0; j < n; ++j) x[j] = M.addVar(0, 1, VarType.BINARY, "x" + (j + 1));
        double[] avgW = new double[n];
        for (int i = 0; i < m; ++i) {
            LinExpr e = new LinExpr();
            double total = 0;
            for (int j = 0; j < n; ++j) {
                double w = ri(5, 40);
                e = e.plus(w, x[j]);
                total += w;
                avgW[j] += w / m;
            }
            M.addConstr(e.le(Math.floor(0.5 * total)), "cap" + (i + 1));
        }
        LinExpr obj = new LinExpr();
        for (int j = 0; j < n; ++j) obj = obj.plus(cround(avgW[j] + ri(0, 10)), x[j]);
        M.setObjective(obj, ObjSense.MAXIMIZE);
        return M;
    }

    static Model genLp(int n, int m) {
        Model M = new Model();
        double[] x0 = new double[n];
        for (int j = 0; j < n; ++j) {
            double lb = coin(0.8) ? 0.0 : -ri(1, 20);
            double ub = lb + ri(5, 50);
            M.addVar(lb, ub, VarType.CONTINUOUS, "x" + (j + 1));
            x0[j] = rr(lb, ub);
        }
        for (int i = 0; i < m; ++i) {
            LinExpr e = new LinExpr();
            double act = 0;
            for (int j = 0; j < n; ++j) {
                if (!coin(0.3)) continue;
                double a = ri(-10, 10);
                e = e.plus(a, new Var(j));
                act += a * x0[j];
            }
            int s = ri(0, 9);
            if (s < 5) M.addConstr(e.le(cround(act + ri(0, 20))));
            else if (s < 9) M.addConstr(e.ge(cround(act - ri(0, 20))));
            else M.addConstr(e.eq(cround(act)));
        }
        LinExpr obj = new LinExpr();
        for (int j = 0; j < n; ++j) obj = obj.plus(ri(-10, 10), new Var(j));
        M.setObjective(obj, coin(0.5) ? ObjSense.MAXIMIZE : ObjSense.MINIMIZE);
        return M;
    }

    public static void main(String[] args) throws IOException {
        minicplex.Fmt.useUtf8Output();
        String kind = "mixed", out = ".";
        int count = 100, seed = 1, vars = -1, cons = -1;
        for (int i = 0; i + 1 < args.length; i += 2) {
            switch (args[i]) {
                case "--kind" -> kind = args[i + 1];
                case "--count" -> count = Integer.parseInt(args[i + 1]);
                case "--seed" -> seed = Integer.parseInt(args[i + 1]);
                case "--vars" -> vars = Integer.parseInt(args[i + 1]);
                case "--cons" -> cons = Integer.parseInt(args[i + 1]);
                case "--out" -> out = args[i + 1];
                default -> { System.err.println("unknown option " + args[i]); System.exit(2); }
            }
        }
        rng = new Random(seed);
        new File(out).mkdirs();
        for (int k = 0; k < count; ++k) {
            Model M;
            switch (kind) {
                case "mixed" -> M = genMixed(vars > 0 ? vars : 12, cons > 0 ? cons : 10);
                case "mkp" -> M = genMkp(vars > 0 ? vars : 35, cons > 0 ? cons : 5);
                case "lp" -> M = genLp(vars > 0 ? vars : 120, cons > 0 ? cons : 100);
                default -> { System.err.println("unknown kind " + kind); System.exit(2); return; }
            }
            String name = String.format("%s/%s_j%d_%04d.lp", out, kind, seed, k);
            try (FileWriter w = new FileWriter(name)) { M.writeLP(w); }
        }
        System.out.println("generated " + count + " " + kind + " models in " + out);
    }
}
