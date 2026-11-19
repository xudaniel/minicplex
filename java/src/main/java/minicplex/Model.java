package minicplex;

import java.io.IOException;
import java.io.Writer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * An LP / MIP model (in the spirit of CPLEX Concert's IloModel).
 *
 * <pre>{@code
 * Model m = new Model();
 * Var x = m.addVar(0, Model.INF, VarType.INTEGER, "x");
 * m.addConstr(LinExpr.of(2, x).le(10), "budget");
 * m.setObjective(LinExpr.of(x), ObjSense.MAXIMIZE);
 * Result r = Solver.solve(m);
 * }</pre>
 */
public final class Model {
    public static final double INF = Double.POSITIVE_INFINITY;

    public final List<VarInfo> vars = new ArrayList<>();
    public final List<Constraint> constraints = new ArrayList<>();
    public LinExpr objective = new LinExpr();
    public ObjSense objSense = ObjSense.MINIMIZE;
    public String objName = "obj";
    private final Map<String, Integer> index = new HashMap<>();

    public Model() {}

    /** Deep copy. */
    public Model(Model o) {
        for (VarInfo v : o.vars) vars.add(new VarInfo(v));
        for (Constraint c : o.constraints) constraints.add(new Constraint(c));
        objective = o.objective.plus(0.0);
        objSense = o.objSense;
        objName = o.objName;
        index.putAll(o.index);
    }

    public Var addVar(double lb, double ub, VarType type, String name) {
        if (type == VarType.BINARY) {
            lb = Math.max(lb, 0.0);
            ub = Math.min(ub, 1.0);
        }
        if (name == null || name.isEmpty()) name = "x" + (vars.size() + 1);
        if (index.containsKey(name)) throw new IllegalArgumentException("duplicate variable name: " + name);
        index.put(name, vars.size());
        vars.add(new VarInfo(name, lb, ub, type));
        return new Var(vars.size() - 1);
    }
    /** Continuous variable in [lb, ub]. */
    public Var addVar(double lb, double ub, VarType type) { return addVar(lb, ub, type, ""); }

    public Var addVar(double lb, double ub) { return addVar(lb, ub, VarType.CONTINUOUS, ""); }
    /** Continuous variable in [0, +inf). */
    public Var addVar() { return addVar(0.0, INF, VarType.CONTINUOUS, ""); }

    public int addConstr(Constraint c, String name) {
        for (int k : c.coefs.keySet())
            if (k < 0 || k >= numVars()) throw new IllegalArgumentException("constraint references unknown variable");
        if (name != null && !name.isEmpty()) c.name = name;
        if (c.name == null || c.name.isEmpty()) c.name = "c" + (constraints.size() + 1);
        constraints.add(c);
        return constraints.size() - 1;
    }
    public int addConstr(Constraint c) { return addConstr(c, ""); }

    public void setObjective(LinExpr e, ObjSense s) {
        objective = e;
        objSense = s;
    }
    public void setObjective(LinExpr e) { setObjective(e, ObjSense.MINIMIZE); }

    public int findVar(String name) {
        Integer j = index.get(name);
        return j == null ? -1 : j;
    }
    public Var var(String name) {
        int j = findVar(name);
        if (j < 0) throw new IllegalArgumentException("unknown variable: " + name);
        return new Var(j);
    }

    public int numVars() { return vars.size(); }
    public int numConstrs() { return constraints.size(); }
    public boolean isInteger(int j) { return vars.get(j).type != VarType.CONTINUOUS; }
    public int numIntegers() {
        int k = 0;
        for (int j = 0; j < numVars(); ++j) if (isInteger(j)) ++k;
        return k;
    }

    // ------------------------------------------------------------ LP writer

    private static String num(double v) {
        if (v == INF) return "inf";
        if (v == -INF) return "-inf";
        return Fmt.g(v, 15);
    }

    private void writeTerms(StringBuilder os, Map<Integer, Double> terms, double constant) {
        int k = 0;
        for (Map.Entry<Integer, Double> t : terms.entrySet()) {
            double v = t.getValue();
            if (v == 0.0) continue;
            if (k > 0 && k % 6 == 0) os.append("\n  ");
            os.append(v < 0 ? " - " : " + ");
            double a = Math.abs(v);
            if (a != 1.0) os.append(num(a)).append(' ');
            os.append(vars.get(t.getKey()).name);
            ++k;
        }
        if (constant != 0.0 || k == 0) os.append(constant < 0 ? " - " : " + ").append(num(Math.abs(constant)));
    }

    private static boolean plainBinary(VarInfo v) {
        return v.type == VarType.BINARY && v.lb == 0.0 && v.ub == 1.0;
    }

    /** The model in CPLEX LP format. */
    public String toLP() {
        StringBuilder os = new StringBuilder();
        os.append("\\ Written by minicplex\n");
        os.append(objSense == ObjSense.MAXIMIZE ? "Maximize\n" : "Minimize\n");
        os.append(' ').append(objName).append(':');
        writeTerms(os, objective.terms, objective.constant);
        os.append("\nSubject To\n");
        for (Constraint c : constraints) {
            os.append(' ').append(c.name).append(':');
            writeTerms(os, c.coefs, 0.0);
            os.append(' ').append(c.sense == Sense.LE ? "<=" : c.sense == Sense.GE ? ">=" : "=")
              .append(' ').append(num(c.rhs)).append('\n');
        }
        os.append("Bounds\n");
        for (VarInfo v : vars) {
            if (plainBinary(v)) continue;
            if (v.lb == 0.0 && v.ub == INF) continue;
            if (v.lb == -INF && v.ub == INF) os.append(' ').append(v.name).append(" free\n");
            else if (v.lb == v.ub) os.append(' ').append(v.name).append(" = ").append(num(v.lb)).append('\n');
            else if (v.ub == INF) os.append(' ').append(v.name).append(" >= ").append(num(v.lb)).append('\n');
            else os.append(' ').append(num(v.lb)).append(" <= ").append(v.name).append(" <= ").append(num(v.ub)).append('\n');
        }
        boolean any = false;
        for (VarInfo v : vars)
            if (v.type == VarType.INTEGER || (v.type == VarType.BINARY && !plainBinary(v))) {
                if (!any) os.append("General\n");
                any = true;
                os.append(' ').append(v.name).append('\n');
            }
        any = false;
        for (VarInfo v : vars)
            if (plainBinary(v)) {
                if (!any) os.append("Binary\n");
                any = true;
                os.append(' ').append(v.name).append('\n');
            }
        os.append("End\n");
        return os.toString();
    }

    public void writeLP(Writer w) throws IOException { w.write(toLP()); }
}
