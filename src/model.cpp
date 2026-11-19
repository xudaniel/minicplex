#include <cmath>
#include <iomanip>
#include <ostream>
#include <sstream>

#include "model.hpp"

namespace mcplex {
namespace {

std::string num(double v) {
    if (v == INF) return "inf";
    if (v == -INF) return "-inf";
    std::ostringstream o;
    o << std::setprecision(15) << v;
    return o.str();
}

void writeTerms(std::ostream& os, const Model& m, const std::map<int, double>& terms,
                double constant) {
    int k = 0;
    for (const auto& [j, v] : terms) {
        if (v == 0.0) continue;
        if (k > 0 && k % 6 == 0) os << "\n  ";
        os << (v < 0 ? " - " : " + ");
        double a = std::abs(v);
        if (a != 1.0) os << num(a) << ' ';
        os << m.vars[j].name;
        ++k;
    }
    if (constant != 0.0 || k == 0) os << (constant < 0 ? " - " : " + ") << num(std::abs(constant));
}

const char* senseStr(Sense s) {
    switch (s) {
        case Sense::LE: return "<=";
        case Sense::GE: return ">=";
        default: return "=";
    }
}

}  // namespace

void Model::writeLP(std::ostream& os) const {
    os << "\\ Written by minicplex\n";
    os << (objSense == ObjSense::Maximize ? "Maximize\n" : "Minimize\n");
    os << ' ' << objName << ':';
    writeTerms(os, *this, objective.terms, objective.constant);
    os << "\nSubject To\n";
    for (const auto& c : constraints) {
        os << ' ' << c.name << ':';
        writeTerms(os, *this, c.coefs, 0.0);
        os << ' ' << senseStr(c.sense) << ' ' << num(c.rhs) << '\n';
    }
    os << "Bounds\n";
    for (const auto& v : vars) {
        if (v.type == VarType::Binary) continue;
        if (v.lb == 0.0 && v.ub == INF) continue;
        if (v.lb == -INF && v.ub == INF)
            os << ' ' << v.name << " free\n";
        else if (v.lb == v.ub)
            os << ' ' << v.name << " = " << num(v.lb) << '\n';
        else if (v.ub == INF)
            os << ' ' << v.name << " >= " << num(v.lb) << '\n';
        else
            os << ' ' << num(v.lb) << " <= " << v.name << " <= " << num(v.ub) << '\n';
    }
    bool any = false;
    for (const auto& v : vars)
        if (v.type == VarType::Integer) {
            if (!any) os << "General\n";
            any = true;
            os << ' ' << v.name << '\n';
        }
    any = false;
    for (const auto& v : vars)
        if (v.type == VarType::Binary) {
            if (!any) os << "Binary\n";
            any = true;
            os << ' ' << v.name << '\n';
        }
    os << "End\n";
}

}  // namespace mcplex
