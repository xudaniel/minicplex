package minicplex;

/** Result of {@link Solver#solve}. */
public final class Result {
    public Status status = Status.INFEASIBLE;
    public boolean hasSolution = false;
    public double objective = Double.NaN;
    public double bestBound = Double.NaN;
    public double gap = Double.NaN;          // relative gap of incumbent vs bound
    public double[] x = new double[0];       // values, indexed like Model.vars
    /** LP only: shadow price of each constraint (change of optimum per unit rhs increase). */
    public double[] duals = new double[0];
    /** LP only: reduced cost of each variable (0 for basic variables). */
    public double[] reducedCosts = new double[0];
    public long nodes = 0;
    public long lpIterations = 0;
    public int cuts = 0;                     // Gomory cuts kept after the root cut loop
    public double seconds = 0.0;

    /** Value of variable v in the solution. */
    public double value(Var v) { return x[v.id()]; }
}
