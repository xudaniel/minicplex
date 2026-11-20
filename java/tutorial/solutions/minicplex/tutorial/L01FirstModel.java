package minicplex.tutorial;

import minicplex.*;

/**
 * 第 1 课练习：第一个模型。
 *
 * <p>你有 25 元，冰淇淋 3 元一个，只能买整数个。最多买几个？
 * 按“建模型 → 建变量 → 加限制 → 定目标”四步，把模型建出来。
 *
 * <p>运行：java/tutorial/run.sh 01
 */
public class L01FirstModel {

    /** 返回冰淇淋问题的模型：一个整数变量 iceCream，一条限制 money，目标是最大化个数。 */
    static Model iceCreamModel() {
        // TODO 1. new 一个 Model  2. addVar 一个整数变量 "iceCream"（下限 0，上限 Model.INF）
        //      3. 加限制 3 × iceCream ≤ 25，名字叫 "money"  4. 目标：最大化 iceCream
        // >>>
        Model m = new Model();
        Var ice = m.addVar(0, Model.INF, VarType.INTEGER, "iceCream");
        m.addConstr(LinExpr.of(3, ice).le(25), "money");
        m.setObjective(LinExpr.of(ice), ObjSense.MAXIMIZE);
        return m;
        // <<<
    }

    public static void main(String[] args) {
        Check.lesson("第 1 课：第一个模型");
        Check.eq("模型里有 1 个变量", 1, () -> iceCreamModel().numVars());
        Check.eq("模型里有 1 条限制", 1, () -> iceCreamModel().numConstrs());
        Check.eq("变量名叫 iceCream", 0, () -> iceCreamModel().findVar("iceCream"));
        Check.eq("求解状态是 Optimal", Status.OPTIMAL, () -> Solver.solve(iceCreamModel()).status);
        Check.near("最多买 8 个", 8, () -> Solver.solve(iceCreamModel()).objective);
        Check.done();
    }
}
