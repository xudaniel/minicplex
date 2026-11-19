package minicplex;

/** Name, bounds and type of a variable. */
public final class VarInfo {
    public String name;
    public double lb;
    public double ub;
    public VarType type;

    public VarInfo(String name, double lb, double ub, VarType type) {
        this.name = name;
        this.lb = lb;
        this.ub = ub;
        this.type = type;
    }

    public VarInfo(VarInfo o) { this(o.name, o.lb, o.ub, o.type); }
}
