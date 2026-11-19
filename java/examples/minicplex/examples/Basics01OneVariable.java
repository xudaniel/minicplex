// 入门例子 01：只有一个变量
//
// 问题：你有 10 元，苹果 2 元一个。最多能买几个苹果？
// 答案一眼就能看出是 5 个。这个例子只为了认识最基本的四个步骤。
//
// 运行：java -cp java/build/minicplex.jar minicplex.examples.Basics01OneVariable   （加 --trace 可以看到求解过程）
package minicplex.examples;

import minicplex.*;  // minicplex 的全部功能都在这个包里

public class Basics01OneVariable {
    public static void main(String[] args) {
        Fmt.useUtf8Output();  // 让中文在任何系统上都能正常显示

        // 第 1 步：建一个空模型
        Model m = new Model();

        // 第 2 步：建变量。apples = 买几个苹果，最少 0 个，没有上限
        Var apples = m.addVar(0, Model.INF, VarType.CONTINUOUS, "apples");

        // 第 3 步：加限制。花的钱不能超过 10 元：2 × 苹果数 ≤ 10
        //（Java 没有运算符重载，所以写成 LinExpr.of(2, apples).le(10)）
        m.addConstr(LinExpr.of(2, apples).le(10), "money");

        // 第 4 步：定目标。苹果越多越好：最大化 苹果数
        m.setObjective(LinExpr.of(apples), ObjSense.MAXIMIZE);

        // 求解
        Params p = new Params();
        p.trace = args.length > 0 && args[0].equals("--trace");
        Result r = Solver.solve(m, p);

        System.out.println("状态：" + r.status);  // Optimal = 找到了最优解
        System.out.println("最多买 " + Fmt.g(r.value(apples)) + " 个苹果");
    }
}
