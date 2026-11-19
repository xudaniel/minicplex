package minicplex;

import java.util.Map;
import java.util.TreeMap;

/** A linear constraint: sum(coefs) (sense) rhs. */
public final class Constraint {
    public String name = "";
    public final TreeMap<Integer, Double> coefs = new TreeMap<>();
    public Sense sense = Sense.LE;
    public double rhs = 0.0;

    public Constraint() {}

    /** Copy constructor. */
    public Constraint(Constraint o) {
        name = o.name;
        coefs.putAll(o.coefs);
        sense = o.sense;
        rhs = o.rhs;
    }

    /** Moves everything to the left: lhs - rhs (sense) 0, then the constant to the right. */
    static Constraint make(LinExpr lhs, Sense s, LinExpr rhs) {
        LinExpr d = lhs.minus(rhs);
        Constraint c = new Constraint();
        for (Map.Entry<Integer, Double> t : d.terms.entrySet())
            if (t.getValue() != 0.0) c.coefs.put(t.getKey(), t.getValue());
        c.sense = s;
        c.rhs = -d.constant;
        return c;
    }
}
