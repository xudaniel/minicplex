package minicplex;

/** Final status of {@link Solver#solve}. Names match the C++ version (used in CSV output). */
public enum Status {
    OPTIMAL("Optimal"),
    INFEASIBLE("Infeasible"),
    UNBOUNDED("Unbounded"),
    INFEASIBLE_OR_UNBOUNDED("InfeasibleOrUnbounded"),
    NODE_LIMIT("NodeLimit"),
    TIME_LIMIT("TimeLimit"),
    ITERATION_LIMIT("IterationLimit");

    private final String label;
    Status(String label) { this.label = label; }
    @Override public String toString() { return label; }
}
