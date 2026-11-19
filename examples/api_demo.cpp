// Building a model in C++ with the Concert-style API.
#include <iostream>

#include "solver.hpp"

using namespace mcplex;

int main() {
    Model m;
    // A furniture shop makes chairs and tables (whole units only).
    Var chairs = m.addVar(0, INF, VarType::Integer, "chairs");
    Var tables = m.addVar(0, INF, VarType::Integer, "tables");

    m.addConstr(2 * chairs + 5 * tables <= 40, "wood");
    m.addConstr(3 * chairs + 2 * tables <= 30, "labor");
    m.addConstr(chairs >= tables, "mix");
    m.setObjective(30 * chairs + 70 * tables, ObjSense::Maximize);

    std::cout << "Model in CPLEX LP format:\n";
    m.writeLP(std::cout);
    std::cout << '\n';

    Params p;
    p.verbose = true;
    Result r = solve(m, p);

    std::cout << "\nstatus = " << toString(r.status) << ", profit = " << r.objective << '\n';
    for (int j = 0; j < m.numVars(); ++j)
        std::cout << "  " << m.vars[j].name << " = " << r.x[j] << '\n';
}
