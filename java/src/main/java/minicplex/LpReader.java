package minicplex;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Reader for (a practical subset of) the CPLEX LP file format.
 *
 * <p>Supported sections: Minimize/Maximize, Subject To, Bounds, General(s)/Integer(s),
 * Binary/Binaries, End. Comments start with '\'.
 */
public final class LpReader {
    private LpReader() {}

    public static Model readString(String text) { return new Parser(tokenize(text)).parse(); }

    public static Model readFile(String path) {
        try {
            return readString(Files.readString(Path.of(path), StandardCharsets.UTF_8));
        } catch (IOException e) {
            throw new RuntimeException("cannot open file: " + path);
        }
    }

    // ------------------------------------------------------------ tokens

    private enum Kind { NUM, ID, OP, END }

    private static final class Tok {
        Kind kind = Kind.END;
        String s = "";
        double num = 0.0;
        int line = 0;
        boolean lineStart = false;
    }

    private static boolean isIdChar(char c) {
        if (c == 0) return false;
        return Character.isLetterOrDigit(c) || "_.!\"#$%&()/,;?@`'{}|~".indexOf(c) >= 0 || c > 127;
    }

    private static List<Tok> tokenize(String src) {
        List<Tok> out = new ArrayList<>();
        int line = 1;
        boolean ls = true;
        int i = 0;
        final int n = src.length();
        while (i < n) {
            final char c = src.charAt(i);
            if (c == '\n') { ++line; ls = true; ++i; continue; }
            if (Character.isWhitespace(c)) { ++i; continue; }
            if (c == '\\') { while (i < n && src.charAt(i) != '\n') ++i; continue; }

            Tok t = new Tok();
            t.line = line;
            t.lineStart = ls;
            ls = false;
            if (isDigit(src, i) || (c == '.' && isDigit(src, i + 1))) {
                // Scan digits manually (a library parse would accept hex such as 0x1).
                int j = i;
                while (isDigit(src, j)) ++j;
                if (j < n && src.charAt(j) == '.') { ++j; while (isDigit(src, j)) ++j; }
                if (j < n && (src.charAt(j) == 'e' || src.charAt(j) == 'E')) {
                    int k = j + 1;
                    if (k < n && (src.charAt(k) == '+' || src.charAt(k) == '-')) ++k;
                    if (isDigit(src, k)) { j = k; while (isDigit(src, j)) ++j; }
                }
                t.kind = Kind.NUM;
                t.s = src.substring(i, j);
                t.num = Double.parseDouble(t.s);
                i = j;
            } else if (c == '<' || c == '>' || c == '=') {
                StringBuilder op = new StringBuilder().append(c);
                if (i + 1 < n && "<>=".indexOf(src.charAt(i + 1)) >= 0) op.append(src.charAt(++i));
                ++i;
                t.kind = Kind.OP;
                String o = op.toString();
                t.s = o.indexOf('<') >= 0 ? "<=" : o.indexOf('>') >= 0 ? ">=" : "=";
            } else if (c == '+' || c == '-' || c == ':') {
                t.kind = Kind.OP;
                t.s = String.valueOf(c);
                ++i;
            } else if (isIdChar(c)) {
                int j = i;
                while (j < n && isIdChar(src.charAt(j))) ++j;
                t.kind = Kind.ID;
                t.s = src.substring(i, j);
                i = j;
            } else {
                throw new RuntimeException("LP parse error (line " + line + "): unexpected character '" + c + "'");
            }
            out.add(t);
        }
        Tok end = new Tok();
        end.line = line;
        out.add(end);
        return out;
    }

    private static boolean isDigit(String s, int k) { return k < s.length() && Character.isDigit(s.charAt(k)) && s.charAt(k) < 128; }

    private static String lower(String s) { return s.toLowerCase(Locale.ROOT); }

    // ------------------------------------------------------------ parser

    private enum Sec { OBJ, CONS, BNDS, GEN, BIN, FIN }

    private static final class Parser {
        private final List<Tok> t;
        private int p = 0;
        private final Model M = new Model();
        // results of keyword()
        private Sec kwSec;
        private int kwLen;
        private boolean kwMax;

        Parser(List<Tok> toks) { t = toks; }

        Model parse() {
            if (!keyword() || kwSec != Sec.OBJ) fail("file must start with Minimize or Maximize");
            while (peek(0).kind != Kind.END) {
                if (!keyword()) fail("unexpected token '" + peek(0).s + "'");
                p += kwLen;
                switch (kwSec) {
                    case OBJ -> {
                        M.objSense = kwMax ? ObjSense.MAXIMIZE : ObjSense.MINIMIZE;
                        parseObjective();
                    }
                    case CONS -> parseConstraints();
                    case BNDS -> parseBounds();
                    case GEN -> parseNames(false);
                    case BIN -> parseNames(true);
                    case FIN -> { return M; }
                }
            }
            return M;
        }

        private Tok peek(int k) { return t.get(Math.min(p + k, t.size() - 1)); }

        private RuntimeException fail(String msg) {
            throw new RuntimeException("LP parse error (line " + peek(0).line + "): " + msg);
        }

        /** Is the current token a section keyword (first token on its line)? Sets kwSec/kwLen/kwMax. */
        private boolean keyword() {
            Tok a = peek(0);
            if (a.kind != Kind.ID || !a.lineStart) return false;
            String w = lower(a.s);
            kwLen = 1;
            kwMax = false;
            switch (w) {
                case "maximize", "maximise", "maximum", "max" -> { kwSec = Sec.OBJ; kwMax = true; return true; }
                case "minimize", "minimise", "minimum", "min" -> { kwSec = Sec.OBJ; return true; }
                default -> {}
            }
            if ((w.equals("subject") || w.equals("such")) && peek(1).kind == Kind.ID) {
                String w2 = lower(peek(1).s);
                if ((w.equals("subject") && w2.equals("to")) || (w.equals("such") && w2.equals("that"))) {
                    kwSec = Sec.CONS;
                    kwLen = 2;
                    return true;
                }
            }
            switch (w) {
                case "st", "s.t.", "st." -> { kwSec = Sec.CONS; return true; }
                case "bounds", "bound" -> { kwSec = Sec.BNDS; return true; }
                case "general", "generals", "gen", "integer", "integers" -> { kwSec = Sec.GEN; return true; }
                case "binary", "binaries", "bin" -> { kwSec = Sec.BIN; return true; }
                case "end" -> { kwSec = Sec.FIN; return true; }
                case "semi", "semis", "sos" -> throw fail("section '" + a.s + "' is not supported by minicplex");
                default -> { return false; }
            }
        }

        private boolean atStop() {
            if (peek(0).kind == Kind.END) return true;
            Sec s = kwSec; int l = kwLen; boolean mx = kwMax;
            boolean k = keyword();
            kwSec = s; kwLen = l; kwMax = mx;
            return k;
        }
        private boolean isOp(String op, int k) { return peek(k).kind == Kind.OP && peek(k).s.equals(op); }
        private boolean isOp(String op) { return isOp(op, 0); }
        private boolean isSense() { return isOp("<=") || isOp(">=") || isOp("="); }
        private boolean isLabel() { return peek(0).kind == Kind.ID && isOp(":", 1); }
        private static boolean isInfWord(String s) {
            String w = lower(s);
            return w.equals("inf") || w.equals("infinity");
        }

        private int var(String name) {
            int j = M.findVar(name);
            return j >= 0 ? j : M.addVar(0.0, Model.INF, VarType.CONTINUOUS, name).id();
        }

        private LinExpr parseExpr() {
            LinExpr e = new LinExpr();
            while (!atStop() && !isSense() && !isLabel()) {
                double sign = 1.0;
                boolean anySign = false;
                while (isOp("+") || isOp("-")) {
                    if (isOp("-")) sign = -sign;
                    ++p;
                    anySign = true;
                }
                double coef = 1.0;
                boolean hasNum = false;
                if (peek(0).kind == Kind.NUM) {
                    coef = peek(0).num;
                    ++p;
                    hasNum = true;
                }
                if (peek(0).kind == Kind.ID && !atStop() && !isLabel()) {
                    e.terms.merge(var(peek(0).s), sign * coef, Double::sum);
                    ++p;
                } else if (hasNum) {
                    e.constant += sign * coef;
                } else if (anySign) {
                    throw fail("dangling sign");
                } else {
                    throw fail("unexpected token '" + peek(0).s + "'");
                }
            }
            return e;
        }

        private double parseValue() {
            double sign = 1.0;
            while (isOp("+") || isOp("-")) {
                if (isOp("-")) sign = -sign;
                ++p;
            }
            if (peek(0).kind == Kind.NUM) { double v = peek(0).num; ++p; return sign * v; }
            if (peek(0).kind == Kind.ID && isInfWord(peek(0).s)) { ++p; return sign * Model.INF; }
            throw fail("expected a number");
        }

        private Sense parseSense() {
            if (!isSense()) throw fail("expected <=, >= or =");
            Sense s = isOp("<=") ? Sense.LE : isOp(">=") ? Sense.GE : Sense.EQ;
            ++p;
            return s;
        }

        private void parseObjective() {
            if (isLabel()) {
                M.objName = peek(0).s;
                p += 2;
            }
            M.objective = parseExpr();
            if (!atStop()) throw fail("unexpected token '" + peek(0).s + "' in objective");
        }

        private void parseConstraints() {
            while (!atStop()) {
                String name = "";
                if (isLabel()) {
                    name = peek(0).s;
                    p += 2;
                }
                LinExpr lhs = parseExpr();
                Sense s = parseSense();
                double rhs = parseValue();
                M.addConstr(Constraint.make(lhs, s, LinExpr.constant(rhs)), name);
            }
        }

        private void setBound(int j, Sense s, double v) {
            VarInfo vi = M.vars.get(j);
            if (s == Sense.LE) vi.ub = v;
            else if (s == Sense.GE) vi.lb = v;
            else { vi.lb = v; vi.ub = v; }
        }

        private void parseBounds() {
            while (!atStop()) {
                Tok a = peek(0);
                boolean valueFirst = a.kind == Kind.NUM || isOp("+") || isOp("-") || (a.kind == Kind.ID && isInfWord(a.s));
                if (valueFirst) {  // v <= x [<= w]
                    double v = parseValue();
                    Sense s = parseSense();
                    if (peek(0).kind != Kind.ID) throw fail("expected a variable name");
                    int j = var(peek(0).s);
                    ++p;
                    // "v <= x" means x >= v, and vice versa
                    setBound(j, s == Sense.LE ? Sense.GE : s == Sense.GE ? Sense.LE : Sense.EQ, v);
                    if (isSense()) {
                        Sense s2 = parseSense();
                        setBound(j, s2, parseValue());
                    }
                } else if (a.kind == Kind.ID) {  // x free | x <= v | x >= v | x = v
                    int j = var(a.s);
                    ++p;
                    if (peek(0).kind == Kind.ID && lower(peek(0).s).equals("free")) {
                        ++p;
                        M.vars.get(j).lb = -Model.INF;
                        M.vars.get(j).ub = Model.INF;
                    } else {
                        Sense s = parseSense();
                        setBound(j, s, parseValue());
                    }
                } else {
                    throw fail("unexpected token '" + a.s + "' in Bounds");
                }
            }
        }

        private void parseNames(boolean binary) {
            while (!atStop()) {
                if (peek(0).kind != Kind.ID) throw fail("expected a variable name");
                VarInfo v = M.vars.get(var(peek(0).s));
                ++p;
                if (binary) {
                    v.type = VarType.BINARY;
                    v.lb = 0.0;
                    v.ub = 1.0;
                } else {
                    v.type = VarType.INTEGER;
                }
            }
        }
    }
}
