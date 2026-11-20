package minicplex.tutorial;

/**
 * 入门 A7：字符串。
 *
 * <p>运行：java/tutorial/run.sh A07
 */
public class A07Strings {

    /** 变成大写再加感叹号：shout("hi") 返回 "HI!" */
    static String shout(String s) {
        // >>>
        return s.toUpperCase() + "!";
        // <<<
    }

    /** 名字缩写：initials("Daniel", "Xu") 返回 "D.X." 。charAt(0) 是第一个字符。 */
    static String initials(String first, String last) {
        // >>>
        return first.charAt(0) + "." + last.charAt(0) + ".";
        // <<<
    }

    /** 字符 c 在 s 里出现几次？ */
    static int countChar(String s, char c) {
        // TODO for (int i = 0; i < s.length(); i++) { if (s.charAt(i) == c) ... }
        // >>>
        int n = 0;
        for (int i = 0; i < s.length(); i++) if (s.charAt(i) == c) n++;
        return n;
        // <<<
    }

    /** 密码里有没有数字？Character.isDigit(ch) 判断一个字符是不是数字。 */
    static boolean hasDigit(String s) {
        // >>>
        for (int i = 0; i < s.length(); i++) if (Character.isDigit(s.charAt(i))) return true;
        return false;
        // <<<
    }

    /** 两次输入的密码一样吗？比较文字内容要用 equals。 */
    static boolean samePassword(String a, String b) {
        // >>>
        return a.equals(b);
        // <<<
    }

    public static void main(String[] args) {
        Check.lesson("入门 A7：字符串");
        Check.eq("shout(\"hi\")", "HI!", () -> shout("hi"));
        Check.eq("initials(\"Daniel\", \"Xu\")", "D.X.", () -> initials("Daniel", "Xu"));
        Check.eq("banana 里有 3 个 a", 3, () -> countChar("banana", 'a'));
        Check.eq("hello 里没有 z", 0, () -> countChar("hello", 'z'));
        Check.that("abc123 里有数字", () -> hasDigit("abc123"));
        Check.that("password 里没有数字", () -> !hasDigit("password"));
        Check.that("两次都输入 abc：一样", () -> samePassword("abc", new String("abc")));
        Check.that("abc 和 abd：不一样", () -> !samePassword("abc", "abd"));
        Check.done();
    }
}
