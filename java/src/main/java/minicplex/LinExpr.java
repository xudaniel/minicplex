package minicplex;

import java.util.Collections;
import java.util.Map;
import java.util.TreeMap;

/**
 * Linear expression: sum(coef * var) + constant.
 *
 * <p>Java has no operator overloading, so expressions are built fluently:
 * <pre>{@code
 * LinExpr e = LinExpr.of(2, x).plus(3, y).plus(-5);   // 2x + 3y - 5
 * Constraint c = e.le(12);                            // 2x + 3y - 5 <= 12
 * }</pre>
 * Every method returns a new expression; expressions are never modified in place.
 */
public final class LinExpr {
    final TreeMap<Integer, Double> terms = new TreeMap<>();
    double constant = 0.0;

    public LinExpr() {}

    public static LinExpr of(Var v) { return new LinExpr().plus(1.0, v); }
    public static LinExpr of(double coef, Var v) { return new LinExpr().plus(coef, v); }
    public static LinExpr constant(double c) { LinExpr e = new LinExpr(); e.constant = c; return e; }

    private LinExpr copy() {
        LinExpr e = new LinExpr();
        e.terms.putAll(terms);
        e.constant = constant;
        return e;
    }

    public LinExpr plus(double coef, Var v) {
        LinExpr e = copy();
        e.terms.merge(v.id(), coef, Double::sum);
        return e;
    }
    public LinExpr plus(Var v) { return plus(1.0, v); }
    public LinExpr minus(double coef, Var v) { return plus(-coef, v); }
    public LinExpr minus(Var v) { return plus(-1.0, v); }
    public LinExpr plus(double c) { LinExpr e = copy(); e.constant += c; return e; }
    public LinExpr minus(double c) { return plus(-c); }
    public LinExpr plus(LinExpr o) {
        LinExpr e = copy();
        for (Map.Entry<Integer, Double> t : o.terms.entrySet()) e.terms.merge(t.getKey(), t.getValue(), Double::sum);
        e.constant += o.constant;
        return e;
    }
    public LinExpr minus(LinExpr o) { return plus(o.times(-1.0)); }
    public LinExpr times(double s) {
        LinExpr e = copy();
        e.terms.replaceAll((k, v) -> v * s);
        e.constant *= s;
        return e;
    }

    /** this <= rhs */
    public Constraint le(double rhs) { return Constraint.make(this, Sense.LE, constant(rhs)); }
    public Constraint le(LinExpr rhs) { return Constraint.make(this, Sense.LE, rhs); }
    public Constraint le(Var rhs) { return Constraint.make(this, Sense.LE, of(rhs)); }
    /** this >= rhs */
    public Constraint ge(double rhs) { return Constraint.make(this, Sense.GE, constant(rhs)); }
    public Constraint ge(LinExpr rhs) { return Constraint.make(this, Sense.GE, rhs); }
    public Constraint ge(Var rhs) { return Constraint.make(this, Sense.GE, of(rhs)); }
    /** this == rhs */
    public Constraint eq(double rhs) { return Constraint.make(this, Sense.EQ, constant(rhs)); }
    public Constraint eq(LinExpr rhs) { return Constraint.make(this, Sense.EQ, rhs); }
    public Constraint eq(Var rhs) { return Constraint.make(this, Sense.EQ, of(rhs)); }

    /** Read-only view of the terms (variable id → coefficient); modifying it throws. */
    public Map<Integer, Double> terms() { return Collections.unmodifiableMap(terms); }
    public double constant() { return constant; }
}
