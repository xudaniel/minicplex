package minicplex;

import java.io.FileWriter;
import java.io.IOException;
import java.util.Locale;
import java.util.Map;

/** Command-line solver: {@code java -jar minicplex.jar [options] model.lp} (same options as the C++ CLI). */
public final class Main {
    private Main() {}

    private static void usage() {
        System.out.println("usage: minicplex [options] model.lp\n"
                + "  --relax         solve the LP relaxation only\n"
                + "  --gap G         relative MIP gap (default 1e-6)\n"
                + "  --absgap G      absolute MIP gap (default 1e-6)\n"
                + "  --nodes N       node limit\n"
                + "  --time T        time limit in seconds\n"
                + "  --quiet         no node log\n"
                + "  --all           print zero-valued variables too\n"
                + "  --duals         LP: print shadow prices of constraints and reduced costs\n"
                + "  --write FILE    write the parsed model back out in LP format\n"
                + "  --branch R      branching rule: pc (pseudo-cost, default) | frac (most fractional)\n"
                + "  --cuts K        rounds of root Gomory cuts (default 2, 0 = off)\n"
                + "  --no-presolve   skip presolve\n"
                + "  --trace         print every simplex pivot and branching decision (for learning)");
    }

    public static void main(String[] args) {
        Fmt.useUtf8Output();
        System.exit(run(args));
    }

    static int run(String[] args) {
        Params P = new Params();
        P.verbose = true;
        String path = "", writePath = "";
        boolean printAll = false, printDuals = false;
        for (int i = 0; i < args.length; ++i) {
            String a = args[i];
            if (a.equals("-h") || a.equals("--help")) { usage(); return 0; }
            boolean needsValue = a.equals("--gap") || a.equals("--absgap") || a.equals("--nodes") || a.equals("--time")
                    || a.equals("--branch") || a.equals("--cuts") || a.equals("--write");
            if (needsValue && i + 1 >= args.length) { usage(); return 2; }
            switch (a) {
                case "--relax" -> P.relaxIntegrality = true;
                case "--gap" -> P.mipGap = Double.parseDouble(args[++i]);
                case "--absgap" -> P.mipAbsGap = Double.parseDouble(args[++i]);
                case "--nodes" -> P.nodeLimit = Long.parseLong(args[++i]);
                case "--time" -> P.timeLimit = Double.parseDouble(args[++i]);
                case "--quiet" -> P.verbose = false;
                case "--all" -> printAll = true;
                case "--duals" -> printDuals = true;
                case "--branch" -> P.branching = args[++i].equals("frac") ? Branching.MOST_FRACTIONAL : Branching.PSEUDO_COST;
                case "--cuts" -> P.cutRounds = Integer.parseInt(args[++i]);
                case "--no-presolve" -> P.presolve = false;
                case "--trace" -> { P.trace = true; P.verbose = false; }
                case "--write" -> writePath = args[++i];
                default -> {
                    if (!a.isEmpty() && a.charAt(0) == '-') { usage(); return 2; }
                    path = a;
                }
            }
        }
        if (path.isEmpty()) { usage(); return 2; }

        try {
            Model M = LpReader.readFile(path);
            System.out.println("minicplex 1.0 (Java) | " + path);
            System.out.println("  " + M.numVars() + " variables (" + M.numIntegers() + " integer), " + M.numConstrs()
                    + " constraints, " + (M.objSense == ObjSense.MAXIMIZE ? "maximize" : "minimize") + "\n");
            if (!writePath.isEmpty()) {
                try (FileWriter w = new FileWriter(writePath)) { M.writeLP(w); }
            }

            Result R = Solver.solve(M, P);

            System.out.println("\nStatus:       " + R.status);
            if (R.hasSolution) {
                System.out.println("Objective:    " + Fmt.g(R.objective, 10));
                if (M.numIntegers() > 0 && !P.relaxIntegrality)
                    System.out.println("Best bound:   " + Fmt.g(R.bestBound, 10) + String.format(Locale.ROOT, "   (gap %.4f%%)", 100.0 * R.gap));
            }
            System.out.println(String.format(Locale.ROOT, "Nodes:        %d\nIterations:   %d\nTime:         %.3f s", R.nodes,
                    R.lpIterations, R.seconds));
            if (R.hasSolution) {
                System.out.println(String.format(Locale.ROOT, "\n%-20s %16s", "Variable", "Value"));
                for (int j = 0; j < M.numVars(); ++j) {
                    double v = R.x[j];
                    if (Math.abs(v) < 1e-9) v = 0.0;
                    if (v != 0.0 || printAll)
                        System.out.println(String.format(Locale.ROOT, "%-20s %16s", M.vars.get(j).name, Fmt.g(v, 10)));
                }
            }
            if (printDuals && R.duals.length > 0) {
                System.out.println(String.format(Locale.ROOT, "\n%-20s %14s %14s %16s", "Constraint", "Activity", "RHS", "Shadow price"));
                for (int i = 0; i < M.numConstrs(); ++i) {
                    Constraint c = M.constraints.get(i);
                    double act = 0.0;
                    for (Map.Entry<Integer, Double> t : c.coefs.entrySet()) act += t.getValue() * R.x[t.getKey()];
                    System.out.println(String.format(Locale.ROOT, "%-20s %14s %14s %16s", c.name, Fmt.g(act, 8), Fmt.g(c.rhs, 8),
                            Fmt.g(R.duals[i], 8)));
                }
                System.out.println(String.format(Locale.ROOT, "\n%-20s %14s %16s", "Variable", "Value", "Reduced cost"));
                for (int j = 0; j < M.numVars(); ++j)
                    System.out.println(String.format(Locale.ROOT, "%-20s %14s %16s", M.vars.get(j).name, Fmt.g(R.x[j], 8),
                            Fmt.g(R.reducedCosts[j], 8)));
            } else if (printDuals) {
                System.out.println("\n(shadow prices are only defined for LPs; use --relax for the LP relaxation)");
            }
            return R.hasSolution ? 0 : 1;
        } catch (RuntimeException | IOException e) {
            System.err.println("error: " + e.getMessage());
            return 2;
        }
    }
}
