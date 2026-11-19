// Self-contained tests: known LP/MIP answers, the LP reader/writer, and
// random integer programs checked against brute-force enumeration.
#include <cmath>
#include <iostream>
#include <random>
#include <sstream>

#include "lp_reader.hpp"
#include "solver.hpp"

using namespace mcplex;

static int passes = 0, fails = 0;
#define CHECK(cond)                                                                 \
    do {                                                                            \
        if (cond) ++passes;                                                         \
        else { ++fails; std::cerr << "FAIL " << __LINE__ << ": " #cond "\n"; }      \
    } while (0)

static bool near(double a, double b, double t = 1e-6) { return std::abs(a - b) <= t * (1 + std::abs(b)); }

static void testClassicLP() {
    Model m;
    Var x = m.addVar(), y = m.addVar();
    m.addConstr(x <= 4);
    m.addConstr(2 * y <= 12);
    m.addConstr(3 * x + 2 * y <= 18);
    m.setObjective(3 * x + 5 * y, ObjSense::Maximize);
    Result r = solve(m);
    CHECK(r.status == Status::Optimal);
    CHECK(near(r.objective, 36));
    CHECK(near(r.x[0], 2) && near(r.x[1], 6));
}

static void testInfeasibleUnbounded() {
    Model a;
    Var x = a.addVar(), y = a.addVar();
    a.addConstr(x + y <= 1);
    a.addConstr(x + y >= 3);
    a.setObjective(x + y);
    CHECK(solve(a).status == Status::Infeasible);

    Model b;
    Var u = b.addVar(), v = b.addVar();
    b.addConstr(u - v <= 1);
    b.setObjective(u + v, ObjSense::Maximize);
    CHECK(solve(b).status == Status::Unbounded);
}

static void testFreeAndEquality() {
    Model m;
    Var x = m.addVar(-INF, INF), y = m.addVar(-INF, INF);
    m.addConstr(x + y == 10);
    m.addConstr(x - y >= -2);
    m.setObjective(2 * x + y);
    Result r = solve(m);
    CHECK(r.status == Status::Optimal && near(r.objective, 14) && near(r.x[0], 4));

    Model n;
    Var z = n.addVar(-3, 7);
    n.addConstr(z >= -10);
    n.setObjective(z);
    CHECK(near(solve(n).objective, -3));
    Model k;
    Var w = k.addVar(-INF, 5);
    k.setObjective(w, ObjSense::Maximize);
    CHECK(near(solve(k).objective, 5));
}

static void testBealeCycling() {  // cycles under naive Dantzig without anti-cycling
    Model m;
    Var x4 = m.addVar(), x5 = m.addVar(), x6 = m.addVar(), x7 = m.addVar();
    m.addConstr(0.25 * x4 - 8 * x5 - x6 + 9 * x7 <= 0);
    m.addConstr(0.5 * x4 - 12 * x5 - 0.5 * x6 + 3 * x7 <= 0);
    m.addConstr(x6 <= 1);
    m.setObjective(-0.75 * x4 + 20 * x5 - 0.5 * x6 + 6 * x7);
    Result r = solve(m);
    CHECK(r.status == Status::Optimal && near(r.objective, -1.25));
}

static void testEngineEdgeCases() {
    // no constraints at all: optimum at the bounds
    Model a;
    Var x = a.addVar(-2, 5), y = a.addVar(1, 3, VarType::Integer);
    a.setObjective(x - 2 * y + 1);
    Result r = solve(a);
    CHECK(r.status == Status::Optimal && near(r.objective, -2 - 6 + 1));

    // no constraints, unbounded direction
    Model b;
    Var u = b.addVar(0, INF);
    b.setObjective(u, ObjSense::Maximize);
    CHECK(solve(b).status == Status::Unbounded);

    // every variable fixed
    Model c;
    Var p = c.addVar(3, 3), q = c.addVar(-1, -1);
    c.addConstr(p + q >= 2);
    c.setObjective(p - q);
    r = solve(c);
    CHECK(r.status == Status::Optimal && near(r.objective, 4));
    Model c2;
    Var p2 = c2.addVar(3, 3);
    c2.addConstr(p2 >= 4);
    c2.setObjective(p2);
    CHECK(solve(c2).status == Status::Infeasible);

    // boxed variables with negative costs (start on the upper bound), equality rows
    Model d;
    Var d1 = d.addVar(0, 4), d2 = d.addVar(0, 4), d3 = d.addVar(-INF, INF);
    d.addConstr(d1 + d2 + d3 == 5);
    d.addConstr(d3 >= -1);
    d.setObjective(-d1 - d2 + 0.5 * d3);
    r = solve(d);
    CHECK(r.status == Status::Optimal && near(r.objective, -6.5));  // d1 = d2 = 4, d3 = -1

    // inverted bounds after integer rounding: 0.2 <= x <= 0.8, x integer
    Model e;
    Var ei = e.addVar(0.2, 0.8, VarType::Integer);
    e.setObjective(ei);
    CHECK(solve(e).status == Status::Infeasible);
}

static void testPresolve() {
    // Loose big-M: x <= 1000 y with x <= 20  ->  coefficient becomes -20.
    {
        Model m;
        Var x = m.addVar(0, 20), y = m.addVar(0, 1, VarType::Binary);
        m.addConstr(x - 1000 * y <= 0, "link");
        m.setObjective(2 * x - 30 * y, ObjSense::Maximize);
        std::vector<double> lb = {0, 0}, ub = {20, 1};
        std::vector<char> isInt = {0, 1};
        Model W = m;
        detail::PresolveStats st;
        CHECK(detail::presolve(W, lb, ub, isInt, st));
        bool tight = false;
        for (const auto& c : W.constraints)
            if (c.name == "link") tight = std::abs(c.coefs.at(y.id) + 20) < 1e-9;
        CHECK(st.coefsTightened >= 1 && tight);
        Params off;
        off.presolve = false;
        off.cutRounds = 0;
        Result r1 = solve(m), r2 = solve(m, off);
        CHECK(r1.status == Status::Optimal && near(r1.objective, 10) && near(r2.objective, 10));
    }
    // Bound propagation: x >= 7 forces y = 1 through the link row.
    {
        Model m;
        Var x = m.addVar(0, 20), y = m.addVar(0, 1, VarType::Binary);
        m.addConstr(x - 1000 * y <= 0, "link");
        m.addConstr(x >= 7, "need");
        m.setObjective(x + 50 * y);
        std::vector<double> lb = {0, 0}, ub = {20, 1};
        std::vector<char> isInt = {0, 1};
        Model W = m;
        detail::PresolveStats st;
        CHECK(detail::presolve(W, lb, ub, isInt, st));
        CHECK(lb[1] == 1.0 && lb[0] >= 7.0 - 1e-6);
        Result r = solve(m);
        CHECK(r.status == Status::Optimal && near(r.objective, 57));
    }

    // Infeasibility proven by presolve alone.
    Model q;
    Var a = q.addVar(0, 10, VarType::Integer), b = q.addVar(0, 10, VarType::Integer);
    q.addConstr(a + b <= 1);
    q.addConstr(a >= 2);
    q.setObjective(a + b);
    CHECK(solve(q).status == Status::Infeasible);
}

static void testGomoryCutsAreValid() {
    // Cuts from the root tableau must never cut off an integer-feasible point.
    std::mt19937 rng(777);
    auto ri = [&](int a, int b) { return std::uniform_int_distribution<int>(a, b)(rng); };
    int checked = 0, cutsSeen = 0;
    bool allValid = true;
    for (int t = 0; t < 200; ++t) {
        Model M;
        const int n = 4;
        for (int j = 0; j < n; ++j) M.addVar(0, 4, VarType::Integer);
        for (int i = 0; i < 3; ++i) {
            LinExpr e;
            for (int j = 0; j < n; ++j) e += ri(-4, 6) * Var{j};
            M.addConstr(e <= ri(3, 15));
        }
        LinExpr obj;
        for (int j = 0; j < n; ++j) obj += ri(1, 9) * Var{j};
        M.setObjective(obj, ObjSense::Maximize);
        detail::LPEngine E(M, -1.0);
        if (E.solve(10000) != detail::LPStatus::Optimal) continue;
        auto cuts = E.gomoryCuts(std::vector<char>(n, 1), 20);
        cutsSeen += static_cast<int>(cuts.size());
        std::vector<double> p(n);
        for (int a = 0; a < 625; ++a) {  // every integer point of [0,4]^4
            int k = a;
            for (int j = 0; j < n; ++j) { p[j] = k % 5; k /= 5; }
            if (!checkFeasible(M, p)) continue;
            ++checked;
            for (const auto& c : cuts) {
                double act = 0;
                for (const auto& [j, v] : c.coefs) act += v * p[j];
                if (act < c.rhs - 1e-7) allValid = false;
            }
        }
    }
    std::cout << "  gomory: " << cutsSeen << " cuts checked against " << checked << " integer points\n";
    CHECK(cutsSeen > 50);
    CHECK(allValid);
}

static void testShadowPrices() {
    // Bakery LP: by hand, flour is worth 0.75 per kg and labour 0.5 per hour.
    Model m;
    Var cake = m.addVar(), bread = m.addVar();
    m.addConstr(6 * cake + 4 * bread <= 24, "flour");
    m.addConstr(cake + 2 * bread <= 6, "labor");
    m.setObjective(5 * cake + 4 * bread, ObjSense::Maximize);
    Result r = solve(m);
    CHECK(r.duals.size() == 2 && near(r.duals[0], 0.75) && near(r.duals[1], 0.5));
    CHECK(r.reducedCosts.size() == 2 && near(r.reducedCosts[0], 0) && near(r.reducedCosts[1], 0));

    // Finite differences: moving a right-hand side by +-delta must change the
    // optimum by dual * delta (checked where the LP is locally non-degenerate).
    std::mt19937 rng(4242);
    auto ri = [&](int a, int b) { return std::uniform_int_distribution<int>(a, b)(rng); };
    int compared = 0;
    bool allOk = true;
    for (int t = 0; t < 60; ++t) {
        Model M;
        const int n = 6;
        for (int j = 0; j < n; ++j) M.addVar(ri(-3, 0), ri(4, 12));
        for (int i = 0; i < 5; ++i) {
            LinExpr e;
            for (int j = 0; j < n; ++j) e += ri(-5, 5) * Var{j};
            const int s = ri(0, 2), b = ri(-6, 10);
            M.addConstr(s == 0 ? (e <= b) : s == 1 ? (e >= b) : (e == b));
        }
        LinExpr obj;
        for (int j = 0; j < n; ++j) obj += ri(-6, 6) * Var{j};
        M.setObjective(obj, ri(0, 1) ? ObjSense::Maximize : ObjSense::Minimize);
        Result base = solve(M);
        if (base.status != Status::Optimal) continue;
        for (int i = 0; i < M.numConstrs(); ++i) {
            const double delta = 1e-4;
            Model up = M, dn = M;
            up.constraints[i].rhs += delta;
            dn.constraints[i].rhs -= delta;
            Result ru = solve(up), rd = solve(dn);
            if (ru.status != Status::Optimal || rd.status != Status::Optimal) continue;
            const double gu = (ru.objective - base.objective) / delta;
            const double gd = (base.objective - rd.objective) / delta;
            if (std::abs(gu - gd) > 1e-6 * (1 + std::abs(gu))) continue;  // kink: dual not unique
            ++compared;
            if (std::abs(gu - base.duals[i]) > 1e-5 * (1 + std::abs(gu))) allOk = false;
        }
    }
    std::cout << "  shadow prices: " << compared << " rows checked by finite differences\n";
    CHECK(compared > 50);
    CHECK(allOk);

    // MIPs have no duals.
    Model q;
    Var z = q.addVar(0, 5, VarType::Integer);
    q.addConstr(2 * z <= 7);
    q.setObjective(z, ObjSense::Maximize);
    CHECK(solve(q).duals.empty());
}

static void testKnapsack() {
    Model m;
    double val[] = {10, 13, 7, 8}, wt[] = {5, 6, 4, 3};
    LinExpr obj, w;
    for (int i = 0; i < 4; ++i) {
        Var v = m.addVar(0, 1, VarType::Binary);
        obj += val[i] * v;
        w += wt[i] * v;
    }
    m.addConstr(w <= 10);
    m.setObjective(obj, ObjSense::Maximize);
    Result r = solve(m);
    CHECK(r.status == Status::Optimal && near(r.objective, 21));
    CHECK(checkFeasible(m, r.x));
}

static void testReaderRoundTrip() {
    const char* text = R"(\ test model
Maximize
 obj: 3 x + 2 y - z + 0.5
Subject To
 c1: x + y + z <= 7.5
 c2: x - y >= -2
 c3: - z + 2 x = 1
Bounds
 -1 <= z <= 4
 y <= 3
General
 x
Binary
 b
End
)";
    Model m = readLPString(text);
    CHECK(m.numVars() == 4 && m.numConstrs() == 3);
    CHECK(m.objSense == ObjSense::Maximize);
    CHECK(m.vars[m.findVar("z")].lb == -1 && m.vars[m.findVar("z")].ub == 4);
    CHECK(m.vars[m.findVar("x")].type == VarType::Integer);
    CHECK(m.vars[m.findVar("b")].type == VarType::Binary);
    Result r1 = solve(m);
    CHECK(r1.status == Status::Optimal);

    std::ostringstream os;
    m.writeLP(os);
    Model m2 = readLPString(os.str());
    Result r2 = solve(m2);
    CHECK(r2.status == Status::Optimal && near(r1.objective, r2.objective));

    bool threw = false;
    try { readLPString("Minimize\n obj: x +\nSubject To\n c: x >= 1\nEnd\n"); } catch (...) { threw = true; }
    CHECK(threw);
}

// Random pure-integer programs, verified by enumerating every point.
static void testRandomVsBruteForce(int instances) {
    std::mt19937 rng(12345);
    auto ri = [&](int a, int b) { return std::uniform_int_distribution<int>(a, b)(rng); };
    int agree = 0;
    for (int t = 0; t < instances; ++t) {
        const int n = ri(2, 4), m = ri(1, 4), U = 4;
        Model M;
        std::vector<Var> x;
        for (int j = 0; j < n; ++j) x.push_back(M.addVar(ri(-2, 0), U, VarType::Integer));
        for (int i = 0; i < m; ++i) {
            LinExpr e;
            for (int j = 0; j < n; ++j) e += ri(-5, 5) * x[j];
            int s = ri(0, 2), rhs = ri(-6, 10);
            M.addConstr(s == 0 ? (e <= rhs) : s == 1 ? (e >= rhs) : (e == rhs));
        }
        LinExpr obj;
        for (int j = 0; j < n; ++j) obj += ri(-6, 6) * x[j];
        M.setObjective(obj, ri(0, 1) ? ObjSense::Maximize : ObjSense::Minimize);

        // brute force
        double best = std::nan("");
        std::vector<double> pt(n);
        std::vector<int> idx(n);
        for (int j = 0; j < n; ++j) idx[j] = static_cast<int>(M.vars[j].lb);
        for (;;) {
            for (int j = 0; j < n; ++j) pt[j] = idx[j];
            if (checkFeasible(M, pt)) {
                double v = evalObjective(M, pt);
                if (std::isnan(best) || (M.objSense == ObjSense::Maximize ? v > best : v < best)) best = v;
            }
            int j = 0;
            while (j < n && ++idx[j] > U) { idx[j] = static_cast<int>(M.vars[j].lb); ++j; }
            if (j == n) break;
        }

        bool ok = true;
        for (int cfg = 0; cfg < 3; ++cfg) {  // default, no MIP features, aggressive cuts
            Params P;
            P.mipGap = 1e-9;
            if (cfg == 1) { P.presolve = false; P.cutRounds = 0; P.branching = Branching::MostFractional; }
            if (cfg == 2) P.cutRounds = 10;
            Result r = solve(M, P);
            ok = ok && (std::isnan(best) ? r.status == Status::Infeasible
                                         : (r.status == Status::Optimal && near(r.objective, best) &&
                                            checkFeasible(M, r.x)));
        }
        if (ok) ++agree;
        else std::cerr << "  random instance " << t << " mismatch: brute=" << best << "\n";
    }
    std::cout << "  random IPs: " << agree << "/" << instances << " match brute force\n";
    CHECK(agree == instances);
}

int main() {
    testClassicLP();
    testInfeasibleUnbounded();
    testFreeAndEquality();
    testBealeCycling();
    testEngineEdgeCases();
    testShadowPrices();
    testPresolve();
    testGomoryCutsAreValid();
    testKnapsack();
    testReaderRoundTrip();
    testRandomVsBruteForce(500);
    std::cout << passes << " checks passed, " << fails << " failed\n";
    return fails == 0 ? 0 : 1;
}
