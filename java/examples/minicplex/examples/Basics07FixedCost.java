// 进阶例子 07：固定费用（大 M）——要生产，先付开工费
//
// 面包店（必须整数）：蛋糕赚 5 元，面包赚 4 元；面粉 24 公斤，人工 6 小时。
// 新情况：做蛋糕要先买模具（12 元），做面包要先开烤箱（2 元）。只要做了，不管做多少，
// 这笔钱都要付；一个都不做就不用付。
//
// 技巧：给每种产品加一个 0-1 变量 open（做不做），再加一条“开关”限制：
//      数量 ≤ M × open
// open = 0 时数量只能是 0；open = 1 时数量最多是 M，相当于没有限制。
// M 要取“这种产品最多可能做多少”：太小会切掉合法方案，太大会让计算变慢。
package minicplex.examples;

import minicplex.*;

public class Basics07FixedCost {
    /** 求解结果加上蛋糕、面包的数量。 */
    record Plan(Result r, double cake, double bread) {}

    static Plan solveWithM(double mCake, double mBread, boolean relax) {
        Model m = new Model();
        Var c = m.addVar(0, Model.INF, VarType.INTEGER, "cake");
        Var b = m.addVar(0, Model.INF, VarType.INTEGER, "bread");
        Var openCake = m.addVar(0, 1, VarType.BINARY, "open_cake");
        Var openBread = m.addVar(0, 1, VarType.BINARY, "open_bread");
        m.addConstr(LinExpr.of(6, c).plus(4, b).le(24), "flour");
        m.addConstr(LinExpr.of(1, c).plus(2, b).le(6), "labor");
        m.addConstr(LinExpr.of(c).le(LinExpr.of(mCake, openCake)), "cake_switch");     // 不开工就不能做蛋糕
        m.addConstr(LinExpr.of(b).le(LinExpr.of(mBread, openBread)), "bread_switch");  // 不开工就不能做面包
        m.setObjective(LinExpr.of(5, c).plus(4, b).minus(12, openCake).minus(2, openBread), ObjSense.MAXIMIZE);
        Params p = new Params();
        p.relaxIntegrality = relax;
        p.presolve = false;  // 关掉预处理，才能看清 M 取值本身的影响
        p.cutRounds = 0;
        Result r = Solver.solve(m, p);
        return new Plan(r, r.value(c), r.value(b));
    }

    public static void main(String[] args) {
        Fmt.useUtf8Output();
        Plan best = solveWithM(4, 3, false);  // M：面粉最多够做 4 个蛋糕，人工最多够做 3 个面包
        Result r = best.r();
        System.out.printf("最优方案：蛋糕 %.0f 个，面包 %.0f 个，净赚 %.0f 元%n", best.cake(), best.bread(), r.objective);
        System.out.printf("（没有开工费时最优是只做 4 个蛋糕赚 20 元；现在模具太贵，改成只做面包更划算）%n%n");

        // 同样的模型，M 取得很大：答案不变，但“先允许小数”时的估算（界）宽松得多。
        // 这道小题两种取法搜索的节点数一样；题目一大，宽松的界会让分支定界多搜很多节点。
        Result tight = solveWithM(4, 3, true).r();
        Result loose = solveWithM(1000, 1000, true).r();
        Result looseInt = solveWithM(1000, 1000, false).r();
        System.out.printf("M 取 4 和 3：  允许小数时估算最多赚 %.2f 元，整数最优 %.0f 元，搜索 %d 个节点%n",
                          tight.objective, r.objective, r.nodes);
        System.out.printf("M 取 1000：    允许小数时估算最多赚 %.2f 元，整数最优 %.0f 元，搜索 %d 个节点%n",
                          loose.objective, looseInt.objective, looseInt.nodes);
        System.out.printf("（估算越接近真实答案 10 元越好：M 取得准，估算是 11；M 取得大，估算是 20.96）%n");
    }
}
