// 用 Java API 建模的完整演示（对应 C++ 的 api_demo.cpp）。
// 家具店做椅子和桌子（只能整件）。
package minicplex.examples;

import minicplex.*;

public class ApiDemo {
    public static void main(String[] args) {
        Fmt.useUtf8Output();
        Model m = new Model();
        Var chairs = m.addVar(0, Model.INF, VarType.INTEGER, "chairs");
        Var tables = m.addVar(0, Model.INF, VarType.INTEGER, "tables");

        m.addConstr(LinExpr.of(2, chairs).plus(5, tables).le(40), "wood");
        m.addConstr(LinExpr.of(3, chairs).plus(2, tables).le(30), "labor");
        m.addConstr(LinExpr.of(chairs).ge(tables), "mix");
        m.setObjective(LinExpr.of(30, chairs).plus(70, tables), ObjSense.MAXIMIZE);

        System.out.println("Model in CPLEX LP format:");
        System.out.print(m.toLP());
        System.out.println();

        Params p = new Params();
        p.verbose = true;
        Result r = Solver.solve(m, p);

        System.out.println();
        System.out.println("status = " + r.status + ", profit = " + Fmt.g(r.objective));
        for (int j = 0; j < m.numVars(); ++j)
            System.out.println("  " + m.vars.get(j).name + " = " + Fmt.g(r.x[j]));
    }
}
