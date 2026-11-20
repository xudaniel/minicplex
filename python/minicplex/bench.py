"""批量求解：解一个目录里（或列出的）全部 .lp 模型，打印表格，可以写出和 C++ 版
minicplex_bench 完全同格式的 CSV（tools/compare_java_cpp.py 等工具直接能用）。

    python -m minicplex.bench bench/models --quiet --csv py.csv
"""
import os
import sys

from . import solver
from .fmt import g, use_utf8_output
from .lp_reader import read_file


def main() -> None:
    use_utf8_output()
    args = sys.argv[1:]
    files, csv, quiet = [], "", False
    P = solver.Params()
    i = 0
    while i < len(args):
        a = args[i]
        nxt = args[i + 1] if i + 1 < len(args) else None
        if a == "--csv" and nxt is not None:
            csv, i = nxt, i + 1
        elif a == "--gap" and nxt is not None:
            P.mip_gap, i = float(nxt), i + 1
        elif a == "--absgap" and nxt is not None:
            P.mip_abs_gap, i = float(nxt), i + 1
        elif a == "--time" and nxt is not None:
            P.time_limit, i = float(nxt), i + 1
        elif a == "--nodes" and nxt is not None:
            P.node_limit, i = int(nxt), i + 1
        elif a == "--quiet":
            quiet = True
        elif a == "--branch" and nxt is not None:
            P.branching, i = (solver.Branching.MOST_FRACTIONAL if nxt == "frac" else solver.Branching.PSEUDO_COST), i + 1
        elif a == "--cuts" and nxt is not None:
            P.cut_rounds, i = int(nxt), i + 1
        elif a == "--no-presolve":
            P.presolve = False
        elif os.path.isdir(a):
            files += [os.path.join(a, f) for f in os.listdir(a) if f.endswith(".lp")]
        else:
            files.append(a)
        i += 1
    files.sort()
    if not files:
        print("usage: python -m minicplex.bench DIR|FILES... [--csv out.csv] [--gap G] [--time T] [--nodes N] [--quiet]",
              file=sys.stderr)
        sys.exit(2)

    out = open(csv, "w", encoding="utf-8", newline="\n") if csv else None
    if out:
        out.write("model,status,objective,nodes,iterations,seconds\n")
    if not quiet:
        print("%-36s %-22s %16s %9s %11s %9s" % ("model", "status", "objective", "nodes", "iterations", "seconds"))
    total_sec, total_nodes, total_iters, failures = 0.0, 0, 0, 0
    for f in files:
        name = os.path.basename(f)
        try:
            M = read_file(f)
            R = solver.solve(M, P)
            if R.has_solution and not solver.check_feasible(M, R.x, 1e-5):
                print(f"{name}: returned solution is NOT feasible", file=sys.stderr)
                failures += 1
            total_sec += R.seconds
            total_nodes += R.nodes
            total_iters += R.lp_iterations
            if not quiet:
                print("%-36s %-22s %16s %9d %11d %9.3f" % (name, R.status, g(R.objective, 10) if R.has_solution else "nan",
                                                         R.nodes, R.lp_iterations, R.seconds))
            if out:
                out.write("%s,%s,%s,%d,%d,%.6f\n" % (name, R.status, g(R.objective, 12) if R.has_solution else "nan",
                                                    R.nodes, R.lp_iterations, R.seconds))
        except ValueError as e:
            print(f"{name}: error: {e}", file=sys.stderr)
            failures += 1
            if out:
                out.write(f"{name},Error,nan,0,0,0\n")
    if out:
        out.close()
    print("%d models, %d nodes, %d simplex iterations, %.3f s total%s" % (len(files), total_nodes, total_iters, total_sec,
                                                                          " — FAILURES!" if failures else ""))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
