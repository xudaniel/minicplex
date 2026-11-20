package minicplex.tutorial;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import minicplex.*;

/**
 * 第 12 课：综合项目——选课助手。
 *
 * <p>读一张课程表（纯文本），在时间、学分、每天课数和先修课的限制下，选出“兴趣分”最高的一组课，
 * 再把结果排成表格。把前 11 课学到的东西串起来：字符串解析、record、集合、建模、异常、格式化输出。
 *
 * <p>运行：java/tutorial/run.sh 12
 */
public class L12Project {

    static final String CATALOG = """
            # 课程     学分  每周小时  上课日  兴趣
            Java       4     6        Mon     9
            算法       4     8        Tue     10
            数据库     3     5        Mon     7
            运筹学     3     6        Wed     10
            英语       2     3        Tue     4
            体育       1     2        Wed     3
            写作       2     4        Mon     5
            """;

    /** 一门课。 */
    record Course(String name, int credits, int hours, String day, int interest) {}

    /** 解析课程表：跳过空行和 # 开头的注释行；每行按空白切成 5 段。格式不对时抛 IllegalArgumentException。 */
    static List<Course> parse(String text) {
        // TODO text.split("\n") 拿到每一行；line.strip()；line.split("\\s+") 切成几段；Integer.parseInt 转数字
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    /**
     * 选课：每门课一个 0-1 变量。限制：
     * 每周总小时 ≤ maxHours；总学分 ≥ minCredits；每天最多 2 门；选“算法”就必须选“Java”（先修课）。
     * 目标：总兴趣分最大。返回选中的课名（按课程表顺序）；无解时返回空列表。
     */
    static List<String> choose(List<Course> courses, int maxHours, int minCredits) {
        // TODO 变量数组 Var[] take；用 LinExpr 累加小时、学分、兴趣；
        //      每天一条约束：遍历 List.of("Mon", "Tue", "Wed")；先修课：take[算法] ≤ take[Java]
        throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
    }

    public static void main(String[] args) {
        Check.lesson("第 12 课：选课助手");
        Check.eq("课程表里有 7 门课", 7, () -> parse(CATALOG).size());
        Check.eq("第一门是 Java，4 学分", new Course("Java", 4, 6, "Mon", 9), () -> parse(CATALOG).get(0));
        Check.throwsA("少一段的行会报错", IllegalArgumentException.class, () -> parse("Java 4 6 Mon"));
        Check.throwsA("数字写错也会报错", IllegalArgumentException.class, () -> parse("Java 四 6 Mon 9"));
        Check.eq("每周 20 小时、至少 10 学分：选 Java、数据库、运筹学、英语", List.of("Java", "数据库", "运筹学", "英语"),
                () -> choose(parse(CATALOG), 20, 10));
        Check.eq("每周 28 小时：加上算法", List.of("Java", "算法", "数据库", "运筹学", "英语"),
                () -> choose(parse(CATALOG), 28, 10));
        Check.eq("每周只有 12 小时：选 Java、运筹学", List.of("Java", "运筹学"), () -> choose(parse(CATALOG), 12, 6));
        Check.eq("每周 5 小时却要 10 学分：无解", List.of(), () -> choose(parse(CATALOG), 5, 10));
        Check.that("不管时间多少，选了算法就一定选了 Java", () -> {
            for (int h = 0; h <= 40; ++h) {
                List<String> c = choose(parse(CATALOG), h, 0);
                if (c.contains("算法") && !c.contains("Java")) return false;
            }
            return true;
        });
        Check.that("不管时间多少，每天最多 2 门课", () -> {
            List<Course> all = parse(CATALOG);
            for (int h = 0; h <= 40; ++h) {
                List<String> c = choose(all, h, 0);
                for (String day : List.of("Mon", "Tue", "Wed"))
                    if (all.stream().filter(x -> x.day().equals(day) && c.contains(x.name())).count() > 2) return false;
            }
            return true;
        });

        // 把结果排成表格（第 10 课的 String.format）
        try {
            List<Course> all = parse(CATALOG);
            List<String> chosen = choose(all, 20, 10);
            System.out.println();
            System.out.println("选课结果（每周 ≤ 20 小时，≥ 10 学分）：");
            int h = 0, cr = 0, in = 0;
            for (Course c : all)
                if (chosen.contains(c.name())) {
                    System.out.println(String.format(Locale.ROOT, "  %-6s %s  %d 学分  %d 小时  兴趣 %d",
                            c.name(), c.day(), c.credits(), c.hours(), c.interest()));
                    h += c.hours(); cr += c.credits(); in += c.interest();
                }
            System.out.println(String.format(Locale.ROOT, "  合计：%d 学分，%d 小时，兴趣 %d", cr, h, in));
            System.out.println();
        } catch (UnsupportedOperationException e) {
            System.out.println("（写完 parse 和 choose 后，这里会打印选课表）");
        }
        Check.done();
    }
}
