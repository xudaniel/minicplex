"""命令行求解器：python -m minicplex [选项] model.lp（选项和 C++ 版一样）。"""
import sys
from typing import List, Optional

from . import solver
from .fmt import g, use_utf8_output
from .lp_reader import read_file
from .model import ObjSense

USAGE = """usage: minicplex [options] model.lp
  --relax         solve the LP relaxation only
  --gap G         relative MIP gap (default 1e-6)
  --absgap G      absolute MIP gap (default 1e-6)
  --nodes N       node limit
  --time T        time limit in seconds
  --quiet         no node log
  --all           print zero-valued variables too
  --duals         LP: print shadow prices of constraints and reduced costs
  --write FILE    write the parsed model back out in LP format
  --branch R      branching rule: pc (pseudo-cost, default) | frac (most fractional)
  --cuts K        rounds of root Gomory cuts (default 2, 0 = off)
  --no-presolve   skip presolve
  --trace         print every simplex pivot and branching decision (for learning)"""

NEEDS_VALUE = {"--gap", "--absgap", "--nodes", "--time", "--branch", "--cuts", "--write"}


def run(args: List[str]) -> int:
    P = solver.Params(verbose=True)
    path = write_path = ""
    print_all = print_duals = False
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("-h", "--help"):
            print(USAGE)
            return 0
        if a in NEEDS_VALUE and i + 1 >= len(args):
            print(USAGE)
            return 2
        val = args[i + 1] if a in NEEDS_VALUE else ""
        if a in NEEDS_VALUE:
            i += 1
        if a == "--relax":
            P.relax_integrality = True
        elif a == "--gap":
            P.mip_gap = float(val)
        elif a == "--absgap":
            P.mip_abs_gap = float(val)
        elif a == "--nodes":
            P.node_limit = int(val)
        elif a == "--time":
            P.time_limit = float(val)
        elif a == "--quiet":
            P.verbose = False
        elif a == "--all":
            print_all = True
        elif a == "--duals":
            print_duals = True
        elif a == "--branch":
            P.branching = solver.Branching.MOST_FRACTIONAL if val == "frac" else solver.Branching.PSEUDO_COST
        elif a == "--cuts":
            P.cut_rounds = int(val)
        elif a == "--no-presolve":
            P.presolve = False
        elif a == "--trace":
            P.trace, P.verbose = True, False
        elif a == "--write":
            write_path = val
        elif a.startswith("-"):
            print(USAGE)
            return 2
        else:
            path = a
        i += 1
    if not path:
        print(USAGE)
        return 2

    try:
        M = read_file(path)
        print(f"minicplex 1.0 (Python) | {path}")
        print(f"  {M.num_vars} variables ({M.num_integers} integer), {M.num_constrs} constraints, "
              f"{'maximize' if M.obj_sense == ObjSense.MAXIMIZE else 'minimize'}\n")
        if write_path:
            M.write_lp(write_path)

        R = solver.solve(M, P)

        print(f"\nStatus:       {R.status}")
        if R.has_solution:
            print(f"Objective:    {g(R.objective, 10)}")
            if M.num_integers > 0 and not P.relax_integrality:
                print(f"Best bound:   {g(R.best_bound, 10)}   (gap {100.0 * R.gap:.4f}%)")
        print("Nodes:        %d\nIterations:   %d\nTime:         %.3f s" % (R.nodes, R.lp_iterations, R.seconds))
        if R.has_solution:
            print("\n%-20s %16s" % ("Variable", "Value"))
            for j, vi in enumerate(M.vars):
                v = R.x[j]
                if abs(v) < 1e-9:
                    v = 0.0
                if v != 0.0 or print_all:
                    print("%-20s %16s" % (vi.name, g(v, 10)))
        if print_duals and R.duals:
            print("\n%-20s %14s %14s %16s" % ("Constraint", "Activity", "RHS", "Shadow price"))
            for i, c in enumerate(M.constraints):
                act = 0.0
                for k, a in c.coefs.items():
                    act += a * R.x[k]
                print("%-20s %14s %14s %16s" % (c.name, g(act, 8), g(c.rhs, 8), g(R.duals[i], 8)))
            print("\n%-20s %14s %16s" % ("Variable", "Value", "Reduced cost"))
            for j, vi in enumerate(M.vars):
                print("%-20s %14s %16s" % (vi.name, g(R.x[j], 8), g(R.reduced_costs[j], 8)))
        elif print_duals:
            print("\n(shadow prices are only defined for LPs; use --relax for the LP relaxation)")
        return 0 if R.has_solution else 1
    except (ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def main(argv: Optional[List[str]] = None) -> None:
    use_utf8_output()
    sys.exit(run(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
    main()
