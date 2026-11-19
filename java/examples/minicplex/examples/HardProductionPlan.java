// 复杂例子：多产品、多周期生产排程（带换线、批量、加班、仓储限制）
//
// 一家电动工具厂，未来 6 周生产 3 种产品：电钻、角磨机、电锯。
// 每周要决定：
//   * 每种产品生产多少（连续）
//   * 每种产品这周开不开线（0-1）：开线要付换线费，且每周最多开 2 条
//   * 加几个班（整数 0~2）：每个加班多 80 工时，每个班 1,200 元
// 规则：
//   1. 库存平衡：上周库存 + 本周生产 − 本周需求 = 本周库存（不允许缺货）
//   2. 工时：Σ 单位工时 × 产量 ≤ 400 + 80 × 加班数
//   3. 开线才能生产，开线就至少生产一个最小批量
//   4. 每周最多换线 2 次（三种产品不能每周都做 → 必须提前囤货）
//   5. 仓库最多放 250 件
//   6. 第 6 周末要留安全库存
// 目标：总成本（换线 + 库存 + 加班 + 生产）最小。
//
// 规模：60 个变量（18 个 0-1、6 个整数）、约 80 条约束。
// 运行时会把模型写到 hard_production_plan.lp，可用 CPLEX / HiGHS 对照验证。
package minicplex.examples;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import minicplex.*;

public class HardProductionPlan {
    public static void main(String[] args) throws IOException {
        Fmt.useUtf8Output();
        final int P = 3, T = 6;
        String[] pid = {"drill", "grinder", "saw"};  // 电钻、角磨机、电锯

        double[] hours = {2, 3, 4};             // 单位工时
        double[] setupCost = {800, 1000, 1500};  // 换线费
        double[] holdCost = {2, 3, 5};          // 每件每周库存费
        double[] unitCost = {20, 30, 45};       // 单位生产成本
        double[] minLot = {30, 20, 15};         // 最小批量
        double[] initInv = {80, 10, 0};         // 期初库存
        double[] endInv = {20, 15, 10};         // 期末安全库存
        double[][] demand = {
            {60, 70, 50, 80, 90, 60},  // 电钻
            {40, 30, 50, 40, 60, 50},  // 角磨机
            {20, 30, 25, 35, 20, 40},  // 电锯
        };
        final double baseHours = 400, otHours = 80, otCost = 1200;
        final int maxOT = 2, maxSetups = 2;
        final double warehouse = 250;

        Model m = new Model();
        Var[][] make = new Var[P][T], inv = new Var[P][T], setup = new Var[P][T];
        Var[] ot = new Var[T];
        for (int t = 0; t < T; ++t) {
            String w = "_w" + (t + 1);
            for (int p = 0; p < P; ++p) {
                make[p][t] = m.addVar(0, Model.INF, VarType.CONTINUOUS, "make_" + pid[p] + w);
                inv[p][t] = m.addVar(t == T - 1 ? endInv[p] : 0, Model.INF, VarType.CONTINUOUS, "inv_" + pid[p] + w);
                setup[p][t] = m.addVar(0, 1, VarType.BINARY, "setup_" + pid[p] + w);
            }
            ot[t] = m.addVar(0, maxOT, VarType.INTEGER, "overtime" + w);
        }

        LinExpr cost = new LinExpr();
        for (int t = 0; t < T; ++t) {
            String w = "_w" + (t + 1);
            LinExpr hoursUsed = new LinExpr(), setupsUsed = new LinExpr(), stock = new LinExpr();
            for (int p = 0; p < P; ++p) {
                // 1. 库存平衡
                LinExpr prev = (t == 0) ? LinExpr.constant(initInv[p]) : LinExpr.of(inv[p][t - 1]);
                m.addConstr(prev.plus(make[p][t]).minus(inv[p][t]).eq(demand[p][t]), "balance_" + pid[p] + w);
                // 3. 开线才能生产 / 最小批量（大 M = 本周最多能做多少）
                double bigM = (baseHours + maxOT * otHours) / hours[p];
                m.addConstr(LinExpr.of(make[p][t]).le(LinExpr.of(bigM, setup[p][t])), "link_" + pid[p] + w);
                m.addConstr(LinExpr.of(make[p][t]).ge(LinExpr.of(minLot[p], setup[p][t])), "minlot_" + pid[p] + w);

                hoursUsed = hoursUsed.plus(hours[p], make[p][t]);
                setupsUsed = setupsUsed.plus(setup[p][t]);
                stock = stock.plus(inv[p][t]);
                cost = cost.plus(setupCost[p], setup[p][t]).plus(holdCost[p], inv[p][t]).plus(unitCost[p], make[p][t]);
            }
            m.addConstr(hoursUsed.le(LinExpr.of(otHours, ot[t]).plus(baseHours)), "hours" + w);  // 2. 工时
            m.addConstr(setupsUsed.le(maxSetups), "setups" + w);                                 // 4. 换线次数
            m.addConstr(stock.le(warehouse), "warehouse" + w);                                   // 5. 仓库
            cost = cost.plus(otCost, ot[t]);
        }
        m.setObjective(cost, ObjSense.MINIMIZE);

        Files.writeString(Path.of("hard_production_plan.lp"), m.toLP(), StandardCharsets.UTF_8);

        System.out.printf("模型：%d 个变量（%d 个整数/0-1），%d 条约束%n%n", m.numVars(), m.numIntegers(), m.numConstrs());

        Params prm = new Params();
        prm.verbose = true;
        prm.logEvery = 500;
        Result r = Solver.solve(m, prm);
        if (!r.hasSolution) {
            System.out.printf("没有找到可行解：%s%n", r.status);
            System.exit(1);
        }

        System.out.printf("%n状态：%s   总成本：%.0f 元   节点：%d   用时：%.2f 秒%n%n", r.status, r.objective, r.nodes,
                          r.seconds);
        System.out.printf("生产计划（* = 本周开线）%n");
        // 中文字符显示宽度为 2，这里手工对齐表头
        System.out.printf("周          电钻   角磨机       电锯   加班        工时   库存%n");
        for (int t = 0; t < T; ++t) {
            System.out.printf("第%d周  ", t + 1);
            double h = 0, s = 0;
            for (int p = 0; p < P; ++p) {
                boolean on = r.value(setup[p][t]) > 0.5;
                System.out.printf("%7.0f%s  ", r.value(make[p][t]), on ? "*" : " ");
                h += hours[p] * r.value(make[p][t]);
                s += r.value(inv[p][t]);
            }
            System.out.printf("%3.0f班  %5.0f/%-4.0f %6.0f%n", r.value(ot[t]), h, baseHours + otHours * r.value(ot[t]), s);
        }

        double cSetup = 0, cHold = 0, cMake = 0, cOT = 0;
        for (int t = 0; t < T; ++t) {
            for (int p = 0; p < P; ++p) {
                cSetup += setupCost[p] * r.value(setup[p][t]);
                cHold += holdCost[p] * r.value(inv[p][t]);
                cMake += unitCost[p] * r.value(make[p][t]);
            }
            cOT += otCost * r.value(ot[t]);
        }
        System.out.printf("%n成本构成：换线 %.0f + 库存 %.0f + 加班 %.0f + 生产 %.0f = %.0f 元%n", cSetup, cHold, cOT, cMake,
                          cSetup + cHold + cOT + cMake);
        System.out.printf("可行性自检：%s%n", Solver.checkFeasible(m, r.x) ? "通过" : "失败");
    }
}
