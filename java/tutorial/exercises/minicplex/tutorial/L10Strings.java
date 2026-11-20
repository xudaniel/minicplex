package minicplex.tutorial;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * 第 10 课练习：字符串和文本处理。
 *
 * <p>运行：java/tutorial/run.sh 10
 */
public class L10Strings {

    /**
     * 迷你词法分析器：把 "3x+2.5y<=10" 切成 [3, x, +, 2.5, y, <=, 10]。
     * 规则：空格跳过；数字由数字和小数点组成；名字由字母、数字、下划线组成（以字母开头）；
     * 运算符有 &lt;=、&gt;=、=、+、-。遇到别的字符抛 IllegalArgumentException。
     * 这是 LpReader.tokenize 的简化版。
     */
    static List<String> tokenize(String s) {
        // TODO 用下标 i 从左往右扫；s.charAt(i) 取字符；Character.isDigit / isLetter 判断类型；
        //      substring(i, j) 截取一段
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 用 String.format 排成一行表格：名字左对齐占 8 格，数值右对齐占 10 格、保留 2 位小数。 */
    static String row(String name, double value) {
        // TODO 格式串 "%-8s%10.2f"；加 Locale.ROOT，保证小数点永远是“.”（有的语言环境用“,”）
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /**
     * 把一条约束写成 LP 格式的一行，例如 " c1: 3 x - y <= 10"。
     * coefs 按顺序给出 变量名 → 系数；系数 1 不写出来，−1 写成 "- y"。用 StringBuilder 拼接。
     */
    static String lpLine(String name, Map<String, Double> coefs, String sense, double rhs) {
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /** 整数就不带小数点：3.0 → "3"，2.5 → "2.5"。 */
    static String num(double v) {
        return v == Math.rint(v) ? String.valueOf((long) v) : String.valueOf(v);
    }

    /** 按给出的顺序建一个 Map：ordered("x", 3.0, "y", -1.0)。LinkedHashMap 记得插入顺序。 */
    static Map<String, Double> ordered(Object... kv) {
        Map<String, Double> m = new LinkedHashMap<>();
        for (int i = 0; i < kv.length; i += 2) m.put((String) kv[i], (Double) kv[i + 1]);
        return m;
    }

    public static void main(String[] args) {
        Check.lesson("第 10 课：字符串和文本处理");
        Check.eq("切分 3x+2.5y<=10", List.of("3", "x", "+", "2.5", "y", "<=", "10"), () -> tokenize("3x+2.5y<=10"));
        Check.eq("空格不影响结果", List.of("cake", "+", "2", "bread", ">=", "6"), () -> tokenize("  cake + 2 bread >= 6 "));
        Check.eq("名字里可以有数字和下划线", List.of("x_1", "-", "y2", "=", "0"), () -> tokenize("x_1 - y2 = 0"));
        Check.throwsA("不认识的字符会报错", IllegalArgumentException.class, () -> tokenize("3x * 2"));
        Check.eq("表格行", "flour        24.00", () -> row("flour", 24));
        Check.eq("写出一条约束", " c1: 3 x - y + 2.5 z <= 10",
                () -> lpLine("c1", ordered("x", 3.0, "y", -1.0, "z", 2.5), "<=", 10));
        Check.eq("第一项是负数", " c2: - a + b >= -4",
                () -> lpLine("c2", ordered("a", -1.0, "b", 1.0), ">=", -4));
        Check.done();
    }
}
