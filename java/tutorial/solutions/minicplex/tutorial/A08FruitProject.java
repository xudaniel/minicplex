package minicplex.tutorial;

import minicplex.*;

/**
 * 入门 A8：小项目——挑水果。
 *
 * <p>苹果 2 元一个、3 分；香蕉 1 元一根、2 分。你有 10 元，袋子最多装 7 个。怎么买，分数最高？
 * 先用前面学的循环把所有买法都试一遍；最后看看 minicplex 求解器是不是也得到同一个答案。
 *
 * <p>运行：java/tutorial/run.sh A08
 */
public class A08FruitProject {

    /** 这样买钱够不够、袋子装不装得下？钱：2 × 苹果 + 1 × 香蕉 ≤ 10；袋子：苹果 + 香蕉 ≤ 7。 */
    static boolean fits(int apples, int bananas) {
        // TODO 两个条件都要满足，用 &&
        // >>>
        return 2 * apples + bananas <= 10 && apples + bananas <= 7;
        // <<<
    }

    /** 这样买得几分？3 × 苹果 + 2 × 香蕉。 */
    static int score(int apples, int bananas) {
        // >>>
        return 3 * apples + 2 * bananas;
        // <<<
    }

    /**
     * 试遍所有买法，返回最好的一种：new int[] {苹果数, 香蕉数, 分数}。
     * 苹果最多 5 个（10 元 ÷ 2 元），香蕉最多 10 根，用两层 for 循环。
     */
    static int[] best() {
        // TODO int[] best = {0, 0, 0};
        //      for (int a = 0; a <= 5; a++) for (int b = 0; b <= 10; b++)
        //          如果 fits(a, b) 并且 score(a, b) > best[2]，就记下 {a, b, score(a, b)}
        // >>>
        int[] best = {0, 0, 0};
        for (int a = 0; a <= 5; a++)
            for (int b = 0; b <= 10; b++)
                if (fits(a, b) && score(a, b) > best[2]) best = new int[] {a, b, score(a, b)};
        return best;
        // <<<
    }

    /** 同一道题交给 minicplex（这段不用你写，看看就好；第 1 课会详细讲）。 */
    static double solverScore() {
        Model m = new Model();
        Var apple = m.addVar(0, Model.INF, VarType.INTEGER, "apple");
        Var banana = m.addVar(0, Model.INF, VarType.INTEGER, "banana");
        m.addConstr(LinExpr.of(2, apple).plus(1, banana).le(10), "money");
        m.addConstr(LinExpr.of(apple).plus(banana).le(7), "bag");
        m.setObjective(LinExpr.of(3, apple).plus(2, banana), ObjSense.MAXIMIZE);
        return Solver.solve(m).objective;
    }

    public static void main(String[] args) {
        Check.lesson("入门 A8：挑水果");
        Check.that("3 苹果 + 4 香蕉：钱和袋子都够", () -> fits(3, 4));
        Check.that("5 苹果 + 1 香蕉：钱不够（11 元）", () -> !fits(5, 1));
        Check.that("0 苹果 + 8 香蕉：袋子装不下", () -> !fits(0, 8));
        Check.eq("3 苹果 + 4 香蕉得 17 分", 17, () -> score(3, 4));
        Check.eq("最好的买法：3 个苹果、4 根香蕉、17 分", "[3, 4, 17]", () -> java.util.Arrays.toString(best()));
        Check.near("minicplex 求解器也得到 17 分", 17, () -> solverScore());
        System.out.println();
        System.out.println("你用两层循环试了 6 × 11 = 66 种买法。变量一多，试遍所有组合就太慢了，");
        System.out.println("这时就轮到求解器出场。下一步：第 1 课，自己用 minicplex 建模型。");
        Check.done();
    }
}
