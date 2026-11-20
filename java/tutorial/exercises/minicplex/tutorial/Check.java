package minicplex.tutorial;

import java.util.Objects;
import java.util.function.BooleanSupplier;
import java.util.function.DoubleSupplier;
import java.util.function.Supplier;

import minicplex.Fmt;

/**
 * 练习用的小小测试框架：每一项检查打印 ✅（通过）、❌（不对）或 ⏳（还没写）。
 *
 * <p>你不需要修改这个文件，但值得读一读：它用到了 lambda（第 8 课）和异常（第 9 课）。
 */
public final class Check {
    private Check() {}

    private static int pass = 0, fail = 0, todo = 0;

    static {
        Fmt.useUtf8Output();  // 中文在任何系统上都能正常显示
    }

    /** 打印本课标题。 */
    public static void lesson(String title) {
        System.out.println("== " + title + " ==");
    }

    /** 检查一个条件为真。 */
    public static void that(String what, BooleanSupplier cond) {
        run(what, () -> cond.getAsBoolean() ? null : "条件不成立");
    }

    /** 检查两个对象相等（用 equals 比较）。 */
    public static void eq(String what, Object expected, Supplier<?> actual) {
        run(what, () -> {
            Object a = actual.get();
            return Objects.equals(expected, a) ? null : "期望 " + expected + "，实际 " + a;
        });
    }

    /** 检查两个小数足够接近（相对误差 1e-6）。 */
    public static void near(String what, double expected, DoubleSupplier actual) {
        run(what, () -> {
            double a = actual.getAsDouble();
            boolean ok = Math.abs(a - expected) <= 1e-6 * (1 + Math.abs(expected));
            return ok ? null : "期望 " + expected + "，实际 " + a;
        });
    }

    /** 检查一段代码会抛出指定类型的异常。 */
    public static void throwsA(String what, Class<? extends Throwable> type, Runnable code) {
        run(what, () -> {
            try {
                code.run();
            } catch (UnsupportedOperationException e) {
                if ("TODO".equals(e.getMessage())) throw e;
                return type.isInstance(e) ? null : "抛出了 " + e.getClass().getSimpleName();
            } catch (Throwable e) {
                return type.isInstance(e) ? null : "抛出了 " + e.getClass().getSimpleName() + "：" + e.getMessage();
            }
            return "没有抛出 " + type.getSimpleName();
        });
    }

    private static void run(String what, Supplier<String> check) {
        String err;
        try {
            err = check.get();
        } catch (UnsupportedOperationException e) {
            if ("TODO".equals(e.getMessage())) {
                ++todo;
                System.out.println("⏳ " + what + "（还没写，找 TODO）");
                return;
            }
            err = "抛出了异常 " + e;
        } catch (RuntimeException | AssertionError e) {
            err = "抛出了异常 " + e;
        }
        if (err == null) {
            ++pass;
            System.out.println("✅ " + what);
        } else {
            ++fail;
            System.out.println("❌ " + what + "：" + err);
        }
    }

    /** 打印汇总。有错误时退出码 1，有没写完的退出码 3，全对是 0。 */
    public static void done() {
        System.out.println("-- 通过 " + pass + "，不对 " + fail + "，没写 " + todo
                + (fail == 0 && todo == 0 ? "。全部完成 🎉" : ""));
        System.exit(fail > 0 ? 1 : todo > 0 ? 3 : 0);
    }
}
