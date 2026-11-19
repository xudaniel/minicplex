package minicplex.tools;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

import minicplex.Branching;
import minicplex.LpReader;
import minicplex.Model;
import minicplex.Params;
import minicplex.Result;
import minicplex.Solver;

/**
 * Batch solver: solves every .lp model in a directory (or a list of files), prints a table and can
 * write a CSV in exactly the same format as the C++ minicplex_bench, so tools/fuzz_vs_highs.py and
 * tools/bench_compare.py work unchanged.
 */
public final class Bench {
    private Bench() {}

    public static void main(String[] args) throws IOException {
        minicplex.Fmt.useUtf8Output();
        List<String> files = new ArrayList<>();
        String csv = "";
        boolean quiet = false;
        Params P = new Params();
        for (int i = 0; i < args.length; ++i) {
            String a = args[i];
            if (a.equals("--csv") && i + 1 < args.length) csv = args[++i];
            else if (a.equals("--gap") && i + 1 < args.length) P.mipGap = Double.parseDouble(args[++i]);
            else if (a.equals("--absgap") && i + 1 < args.length) P.mipAbsGap = Double.parseDouble(args[++i]);
            else if (a.equals("--time") && i + 1 < args.length) P.timeLimit = Double.parseDouble(args[++i]);
            else if (a.equals("--nodes") && i + 1 < args.length) P.nodeLimit = Long.parseLong(args[++i]);
            else if (a.equals("--quiet")) quiet = true;
            else if (a.equals("--branch") && i + 1 < args.length)
                P.branching = args[++i].equals("frac") ? Branching.MOST_FRACTIONAL : Branching.PSEUDO_COST;
            else if (a.equals("--cuts") && i + 1 < args.length) P.cutRounds = Integer.parseInt(args[++i]);
            else if (a.equals("--no-presolve")) P.presolve = false;
            else if (new File(a).isDirectory()) {
                File[] fs = new File(a).listFiles((d, name) -> name.endsWith(".lp"));
                if (fs != null) for (File f : fs) files.add(f.getPath());
            } else files.add(a);
        }
        Collections.sort(files);
        if (files.isEmpty()) {
            System.err.println("usage: Bench DIR|FILES... [--csv out.csv] [--gap G] [--time T] [--nodes N] [--quiet]");
            System.exit(2);
        }

        PrintWriter out = csv.isEmpty() ? null : new PrintWriter(csv);
        if (out != null) out.println("model,status,objective,nodes,iterations,seconds");
        if (!quiet)
            System.out.println(String.format(Locale.ROOT, "%-36s %-22s %16s %9s %11s %9s", "model", "status", "objective",
                    "nodes", "iterations", "seconds"));

        double totalSec = 0;
        long totalNodes = 0, totalIters = 0;
        int failures = 0;
        for (String f : files) {
            String name = new File(f).getName();
            try {
                Model M = LpReader.readFile(f);
                Result R = Solver.solve(M, P);
                if (R.hasSolution && !Solver.checkFeasible(M, R.x, 1e-5)) {
                    System.err.println(name + ": returned solution is NOT feasible");
                    ++failures;
                }
                totalSec += R.seconds;
                totalNodes += R.nodes;
                totalIters += R.lpIterations;
                if (!quiet)
                    System.out.println(String.format(Locale.ROOT, "%-36s %-22s %16s %9d %11d %9.3f", name, R.status,
                            R.hasSolution ? g(R.objective, 10) : "nan", R.nodes, R.lpIterations, R.seconds));
                if (out != null)
                    out.println(String.format(Locale.ROOT, "%s,%s,%s,%d,%d,%.6f", name, R.status,
                            R.hasSolution ? g(R.objective, 12) : "nan", R.nodes, R.lpIterations, R.seconds));
            } catch (RuntimeException e) {
                System.err.println(name + ": error: " + e.getMessage());
                ++failures;
                if (out != null) out.println(name + ",Error,nan,0,0,0");
            }
        }
        if (out != null) out.close();
        System.out.println(String.format(Locale.ROOT, "%d models, %d nodes, %d simplex iterations, %.3f s total%s", files.size(),
                totalNodes, totalIters, totalSec, failures > 0 ? " — FAILURES!" : ""));
        System.exit(failures > 0 ? 1 : 0);
    }

    private static String g(double v, int p) { return minicplex.Fmt.g(v, p); }
}
