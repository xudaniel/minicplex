// 入门例子 05：求最小（花最少的钱）
//
// 问题：每天要喝牛奶、吃鸡蛋来补充营养，至少需要：
//   - 蛋白质 30 克
//   - 钙 600 毫克
//            价格   蛋白质   钙
//   一杯牛奶  3 元    8 克   300 毫克
//   一个鸡蛋  1 元    6 克    30 毫克
// 牛奶按杯、鸡蛋按个，都必须是整数。怎么搭配最省钱？
package minicplex.examples;

import minicplex.*;

public class Basics05Minimize {
    public static void main(String[] args) {
        Fmt.useUtf8Output();
        Model m = new Model();
        Var milk = m.addVar(0, Model.INF, VarType.INTEGER, "milk");
        Var egg = m.addVar(0, Model.INF, VarType.INTEGER, "egg");

        // “至少”用 ge（≥）
        m.addConstr(LinExpr.of(8, milk).plus(6, egg).ge(30), "protein");
        m.addConstr(LinExpr.of(300, milk).plus(30, egg).ge(600), "calcium");

        // 目标是花钱最少：MINIMIZE
        m.setObjective(LinExpr.of(3, milk).plus(1, egg), ObjSense.MINIMIZE);

        Result r = Solver.solve(m);
        double mk = r.value(milk), eg = r.value(egg);
        System.out.println("牛奶 " + Fmt.g(mk) + " 杯，鸡蛋 " + Fmt.g(eg) + " 个，花 " + Fmt.g(r.objective) + " 元");
        System.out.println("蛋白质 " + Fmt.g(8 * mk + 6 * eg) + " 克（至少 30），钙 " + Fmt.g(300 * mk + 30 * eg)
                           + " 毫克（至少 600）");
    }
}
