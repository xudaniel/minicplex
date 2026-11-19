package minicplex;

import java.io.FileDescriptor;
import java.io.FileOutputStream;
import java.io.PrintStream;
import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;

/** Number formatting that matches C's printf("%.Ng") exactly, so the Java and C++ versions print the same text. */
public final class Fmt {
    private Fmt() {}

    /** Equivalent of C printf("%.{precision}g", v). */
    public static String g(double v, int precision) {
        if (Double.isNaN(v)) return "nan";
        if (Double.isInfinite(v)) return v > 0 ? "inf" : "-inf";
        if (v == 0.0) return (1 / v < 0) ? "-0" : "0";
        if (precision == 0) precision = 1;
        BigDecimal bd = new BigDecimal(v).round(new MathContext(precision, RoundingMode.HALF_EVEN));
        int exp = bd.precision() - bd.scale() - 1;  // decimal exponent of the rounded value
        if (exp < -4 || exp >= precision) {
            String mant = bd.movePointLeft(exp).stripTrailingZeros().toPlainString();
            String es = (exp < 0 ? "-" : "+") + (Math.abs(exp) < 10 ? "0" : "") + Math.abs(exp);
            return mant + "e" + es;
        }
        String s = bd.stripTrailingZeros().toPlainString();
        return s;
    }

    /** Make System.out / System.err print UTF-8 (Chinese text) regardless of the platform locale. */
    public static void useUtf8Output() {
        System.setOut(new PrintStream(new FileOutputStream(FileDescriptor.out), true, java.nio.charset.StandardCharsets.UTF_8));
        System.setErr(new PrintStream(new FileOutputStream(FileDescriptor.err), true, java.nio.charset.StandardCharsets.UTF_8));
    }

    /** printf("%g") (precision 6). */
    public static String g(double v) { return g(v, 6); }
}
