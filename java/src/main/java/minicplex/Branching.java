package minicplex;

/** Branching variable selection rule. */
public enum Branching {
    /** Branch on the variable closest to .5. */
    MOST_FRACTIONAL,
    /** Branch on the largest estimated bound improvement (reliability branching). */
    PSEUDO_COST
}
