// minicplex — a small CPLEX-style LP/MIP solver.
// Model building API (in the spirit of CPLEX Concert / IloModel).
#pragma once

#include <algorithm>
#include <iosfwd>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

namespace mcplex {

constexpr double INF = std::numeric_limits<double>::infinity();

enum class VarType { Continuous, Integer, Binary };
enum class Sense { LE, GE, EQ };
enum class ObjSense { Minimize, Maximize };

// Lightweight handle to a variable inside a Model.
struct Var {
    int id = -1;
};

// Linear expression: sum(coef * var) + constant.
class LinExpr {
public:
    std::map<int, double> terms;
    double constant = 0.0;

    LinExpr() = default;
    LinExpr(double c) : constant(c) {}           // NOLINT: implicit on purpose
    LinExpr(Var v) { terms[v.id] = 1.0; }        // NOLINT: implicit on purpose

    LinExpr& operator+=(const LinExpr& o) {
        for (const auto& [k, v] : o.terms) terms[k] += v;
        constant += o.constant;
        return *this;
    }
    LinExpr& operator-=(const LinExpr& o) {
        for (const auto& [k, v] : o.terms) terms[k] -= v;
        constant -= o.constant;
        return *this;
    }
    LinExpr& operator*=(double s) {
        for (auto& kv : terms) kv.second *= s;
        constant *= s;
        return *this;
    }
};

inline LinExpr operator+(LinExpr a, const LinExpr& b) { return a += b; }
inline LinExpr operator-(LinExpr a, const LinExpr& b) { return a -= b; }
inline LinExpr operator-(LinExpr a) { return a *= -1.0; }
inline LinExpr operator*(LinExpr a, double s) { return a *= s; }
inline LinExpr operator*(double s, LinExpr a) { return a *= s; }

// A linear constraint: sum(coefs) <sense> rhs
struct Constraint {
    std::string name;
    std::map<int, double> coefs;
    Sense sense = Sense::LE;
    double rhs = 0.0;
};

inline Constraint makeConstraint(const LinExpr& lhs, Sense s, const LinExpr& rhs) {
    LinExpr d = lhs - rhs;
    Constraint c;
    for (const auto& [k, v] : d.terms)
        if (v != 0.0) c.coefs[k] = v;
    c.sense = s;
    c.rhs = -d.constant;
    return c;
}
inline Constraint operator<=(const LinExpr& l, const LinExpr& r) { return makeConstraint(l, Sense::LE, r); }
inline Constraint operator>=(const LinExpr& l, const LinExpr& r) { return makeConstraint(l, Sense::GE, r); }
inline Constraint operator==(const LinExpr& l, const LinExpr& r) { return makeConstraint(l, Sense::EQ, r); }

struct VarInfo {
    std::string name;
    double lb = 0.0;
    double ub = INF;
    VarType type = VarType::Continuous;
};

class Model {
public:
    std::vector<VarInfo> vars;
    std::vector<Constraint> constraints;
    LinExpr objective;
    ObjSense objSense = ObjSense::Minimize;
    std::string objName = "obj";

    Var addVar(double lb = 0.0, double ub = INF, VarType type = VarType::Continuous,
               std::string name = "") {
        if (type == VarType::Binary) {
            lb = std::max(lb, 0.0);
            ub = std::min(ub, 1.0);
        }
        if (name.empty()) name = "x" + std::to_string(vars.size() + 1);
        if (index_.count(name)) throw std::invalid_argument("duplicate variable name: " + name);
        index_[name] = static_cast<int>(vars.size());
        vars.push_back({name, lb, ub, type});
        return Var{static_cast<int>(vars.size()) - 1};
    }

    int addConstr(Constraint c, std::string name = "") {
        for (const auto& kv : c.coefs)
            if (kv.first < 0 || kv.first >= numVars())
                throw std::invalid_argument("constraint references unknown variable");
        if (!name.empty()) c.name = std::move(name);
        if (c.name.empty()) c.name = "c" + std::to_string(constraints.size() + 1);
        constraints.push_back(std::move(c));
        return static_cast<int>(constraints.size()) - 1;
    }

    void setObjective(const LinExpr& e, ObjSense s = ObjSense::Minimize) {
        objective = e;
        objSense = s;
    }

    int findVar(const std::string& name) const {
        auto it = index_.find(name);
        return it == index_.end() ? -1 : it->second;
    }
    Var var(const std::string& name) const {
        int j = findVar(name);
        if (j < 0) throw std::out_of_range("unknown variable: " + name);
        return Var{j};
    }

    int numVars() const { return static_cast<int>(vars.size()); }
    int numConstrs() const { return static_cast<int>(constraints.size()); }
    bool isInteger(int j) const { return vars[j].type != VarType::Continuous; }
    int numIntegers() const {
        int k = 0;
        for (int j = 0; j < numVars(); ++j) k += isInteger(j);
        return k;
    }

    // Write the model in CPLEX LP format.
    void writeLP(std::ostream& os) const;

private:
    std::unordered_map<std::string, int> index_;
};

}  // namespace mcplex
