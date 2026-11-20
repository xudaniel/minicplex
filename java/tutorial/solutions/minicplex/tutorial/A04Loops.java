package minicplex.tutorial;

/**
 * 入门 A4：重复做事（for 和 while）。
 *
 * <p>运行：java/tutorial/run.sh A04
 */
public class A04Loops {

    /** 1 + 2 + … + n。 */
    static int sumTo(int n) {
        // TODO int sum = 0;  for (int i = 1; i <= n; i++) { sum = sum + i; }  return sum;
        // >>>
        int sum = 0;
        for (int i = 1; i <= n; i++) {
            sum = sum + i;
        }
        return sum;
        // <<<
    }

    /** 1 到 n 里有几个偶数？（偶数：除以 2 余数是 0，也就是 i % 2 == 0） */
    static int countEven(int n) {
        // >>>
        int count = 0;
        for (int i = 1; i <= n; i++) {
            if (i % 2 == 0) count++;
        }
        return count;
        // <<<
    }

    /** 倒数：countdown(3) 返回 "3 2 1 发射！" */
    static String countdown(int n) {
        // TODO 从 n 数到 1：for (int i = n; i >= 1; i--)，每次把 i + " " 接到结果后面
        // >>>
        String s = "";
        for (int i = n; i >= 1; i--) {
            s = s + i + " ";
        }
        return s + "发射！";
        // <<<
    }

    /** 每天存 perDay 元，至少要存几天才能攒够 target 元？用 while：钱不够就再存一天。 */
    static int daysToSave(int target, int perDay) {
        // >>>
        int saved = 0, days = 0;
        while (saved < target) {
            saved = saved + perDay;
            days++;
        }
        return days;
        // <<<
    }

    public static void main(String[] args) {
        Check.lesson("入门 A4：重复做事");
        Check.eq("1 + 2 + … + 10 = 55", 55, () -> sumTo(10));
        Check.eq("1 + 2 + … + 100 = 5050", 5050, () -> sumTo(100));
        Check.eq("1 到 10 有 5 个偶数", 5, () -> countEven(10));
        Check.eq("1 到 7 有 3 个偶数", 3, () -> countEven(7));
        Check.eq("倒数 3", "3 2 1 发射！", () -> countdown(3));
        Check.eq("每天 15 元攒 100 元：7 天", 7, () -> daysToSave(100, 15));
        Check.eq("每天 20 元攒 100 元：正好 5 天", 5, () -> daysToSave(100, 20));
        Check.done();
    }
}
