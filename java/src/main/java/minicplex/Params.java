package minicplex;

/** Solver parameters (defaults match the C++ version). */
public final class Params {
    public boolean relaxIntegrality = false;  // solve the LP relaxation only
    public Branching branching = Branching.PSEUDO_COST;
    public int cutRounds = 2;                 // rounds of root Gomory cuts (0 = off)
    public boolean presolve = true;           // bound propagation + coefficient tightening
    public double intTol = 1e-6;              // integrality tolerance (CPLEX EpInt)
    public double mipGap = 1e-6;              // relative MIP gap (CPLEX EpGap)
    public double mipAbsGap = 1e-6;           // absolute MIP gap (CPLEX EpAGap)
    public long nodeLimit = 10_000_000L;
    public double timeLimit = 1e30;           // seconds
    public boolean verbose = false;           // print a CPLEX-style node log
    public boolean trace = false;             // print every simplex pivot and branching decision
    public long logEvery = 100;               // log every N nodes
}
