// minicplex — solver interface: primal simplex + branch and bound.
#pragma once

#include <cmath>
#include <string>
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

enum class Branching {
    MostFractional,  // branch on the variable closest to .5
    PseudoCost,      // branch on the largest estimated bound improvement
};

struct Params {
    bool relaxIntegrality = false;  // solve the LP relaxation only
    Branching branching = Branching::PseudoCost;
    int cutRounds = 2;              // rounds of root Gomory cuts (0 = off)
    bool presolve = true;           // bound propagation + coefficient tightening
    double intTol = 1e-6;           // integrality tolerance (CPLEX EpInt)
    double mipGap = 1e-6;           // relative MIP gap (CPLEX EpGap)
    double mipAbsGap = 1e-6;        // absolute MIP gap (CPLEX EpAGap)
    long nodeLimit = 10'000'000;
    double timeLimit = 1e30;        // seconds
    bool verbose = false;           // print a CPLEX-style node log
    bool trace = false;             // print every simplex pivot and branching decision (teaching aid)
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
    int cuts = 0;                   // Gomory cuts kept after the root cut loop
    double seconds = 0.0;
};

// Solve an LP or MIP.
Result solve(const Model& model, const Params& params = Params());

// Helpers.
double evalObjective(const Model& model, const std::vector<double>& x);
bool checkFeasible(const Model& model, const std::vector<double>& x, double tol = 1e-6,
                   bool checkIntegrality = true);

namespace detail {

enum class LPStatus { Optimal, Infeasible, Unbounded, IterationLimit, Cutoff };

struct LPResult {
    LPStatus status = LPStatus::Infeasible;
    double objective = 0.0;  // value of objSign * (c'x + c0)
    std::vector<double> x;
    long iterations = 0;
};

// A simplex basis that can be saved and restored (warm start).
struct Basis {
    std::vector<int> head;          // basic variable of each row
    std::vector<signed char> stat;  // status of every variable (structural + slack)
};

// Bounded-variable simplex engine on a dense tableau.
//
// Computational form:  A x - s = 0,  l <= x <= u,  rlo <= s <= rhi.
// Every row has a slack s_i (its row activity), so the all-slack basis is
// always a valid starting basis, and variable bounds never become rows.
//   * primal simplex: composite phase 1 (minimise the sum of infeasibilities)
//     followed by phase 2, with bound flips;
//   * dual simplex: used whenever the basis is dual feasible, e.g. after a
//     branching bound change, so a child node re-optimises in a few pivots;
//   * basis save / restore for branch and bound (warm start).
class LPEngine {
public:
    LPEngine(const Model& model, double objSign);

    void setColBounds(int j, double lb, double ub);
    void setAllColBounds(const std::vector<double>& lb, const std::vector<double>& ub);

    // Minimise objSign * objective. Stops early with Cutoff once the (dual)
    // objective provably reaches `cutoff`.
    LPStatus solve(long maxIters, double cutoff = INF);

    double objective() const;               // objSign * (c'x + c0)
    void setTrace(bool on) { trace_ = on; }
    std::vector<double> colValues() const;  // structural variables only
    long iterations() const { return iters_; }

    Basis basis() const { return {head_, stat_}; }
    int numRows() const { return m_; }

    // Gomory mixed-integer cuts read off the current optimal tableau.
    // isIntCol[j] says whether structural j is integer. Returns at most
    // maxCuts cuts of the form sum(coefs) >= rhs in structural variables,
    // sorted by efficacy and filtered for parallelism and dynamism.
    std::vector<Constraint> gomoryCuts(const std::vector<char>& isIntCol, int maxCuts) const;
    // Move to basis b. By default this pivots from the current tableau and
    // only swaps the columns that differ; fromScratch rebuilds T from A.
    void loadBasis(const Basis& b, bool fromScratch = false);

private:
    enum : signed char { kBasic = 0, kLower = 1, kUpper = 2, kFree = 3, kFixed = 4 };

    int n_, m_, N_;
    std::vector<double> A_;  // original constraint matrix, m x n (row major)
    std::vector<double> c_, lb_, ub_;
    double objConst_;
    double objSign_;
    std::vector<std::string> names_;  // variable and slack names (for tracing)
    bool trace_ = false;
    std::vector<double> T_;  // B^-1 [A | -I], m x N
    std::vector<double> d_;  // reduced costs
    std::vector<double> x_;  // values of all variables
    std::vector<int> head_;
    std::vector<signed char> stat_;
    long iters_ = 0;
    std::string name(int j) const { return names_[j]; }
    double realObjective() const { return objSign_ * objective(); }
    long pivotsSinceRefactor_ = 0;
    long pivotsSinceRecompute_ = 0;
    bool valuesDirty_ = true;
    std::vector<int> nz_;

    double& T(int i, int j) { return T_[static_cast<size_t>(i) * N_ + j]; }
    double T(int i, int j) const { return T_[static_cast<size_t>(i) * N_ + j]; }
    signed char defaultStatus(int j) const;
    double nonbasicValue(int j) const;
    void pivot(int r, int q);
    void recomputeValues();
    void recomputeReducedCosts();
    double infeasibility(int v) const;
    bool makeDualFeasible();
    LPStatus primal(long maxIters);
    LPStatus dual(long maxIters, double cutoff);
};

struct PresolveStats {
    int boundsTightened = 0;
    int coefsTightened = 0;
    int rowsRemoved = 0;
};

// MIP presolve on a copy of the model: tightens lb/ub (indexed like
// Model::vars), tightens big-M coefficients of binaries, removes redundant
// rows. Variables are never removed. Returns false if infeasibility is proven.
bool presolve(Model& model, std::vector<double>& lb, std::vector<double>& ub, const std::vector<char>& isInt,
              PresolveStats& stats);

// Convenience wrapper: solve one LP from scratch.
LPResult lpMin(const Model& model, const std::vector<double>& lb, const std::vector<double>& ub,
               double objSign, long maxIters);

}  // namespace detail
}  // namespace mcplex
