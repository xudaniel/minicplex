// minicplex — solver interface: primal simplex + branch and bound.
#pragma once

#include <cmath>
#include <vector>

#include "model.hpp"

namespace mcplex {

enum class Status {
    Optimal,
    Infeasible,
    Unbounded,
    InfeasibleOrUnbounded,
    NodeLimit,
    TimeLimit,
    IterationLimit,
};

const char* toString(Status s);

struct Params {
    bool relaxIntegrality = false;  // solve the LP relaxation only
    double intTol = 1e-6;           // integrality tolerance (CPLEX EpInt)
    double mipGap = 1e-6;           // relative MIP gap (CPLEX EpGap)
    long nodeLimit = 10'000'000;
    double timeLimit = 1e30;        // seconds
    bool verbose = false;           // print a CPLEX-style node log
    long logEvery = 100;            // log every N nodes
};

struct Result {
    Status status = Status::Infeasible;
    bool hasSolution = false;
    double objective = std::nan("");
    double bestBound = std::nan("");
    double gap = std::nan("");      // relative gap of incumbent vs bound
    std::vector<double> x;          // values, indexed like Model::vars
    long nodes = 0;
    long lpIterations = 0;
    double seconds = 0.0;
};

// Solve an LP or MIP.
Result solve(const Model& model, const Params& params = Params());

// Helpers.
double evalObjective(const Model& model, const std::vector<double>& x);
bool checkFeasible(const Model& model, const std::vector<double>& x, double tol = 1e-6,
                   bool checkIntegrality = true);

namespace detail {

enum class LPStatus { Optimal, Infeasible, Unbounded, IterationLimit };

struct LPResult {
    LPStatus status = LPStatus::Infeasible;
    double objective = 0.0;  // value of objSign * (c'x + c0)
    std::vector<double> x;
    long iterations = 0;
};

// Minimise objSign * objective over the constraints of `model`, using the
// given variable bounds (integrality ignored). Two-phase tableau simplex.
LPResult lpMin(const Model& model, const std::vector<double>& lb, const std::vector<double>& ub,
               double objSign, long maxIters);

}  // namespace detail
}  // namespace mcplex
