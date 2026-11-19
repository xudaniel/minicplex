#include <cctype>
#include <cstring>
#include <fstream>
#include <sstream>
#include <stdexcept>

#include "lp_reader.hpp"

namespace mcplex {
namespace {

struct Tok {
    enum Kind { Num, Id, Op, End } kind = End;
    std::string s;
    double num = 0.0;
    int line = 0;
    bool lineStart = false;
};

bool isIdChar(char c) {
    if (c == 0) return false;
    return std::isalnum(static_cast<unsigned char>(c)) || std::strchr("_.!\"#$%&()/,;?@`'{}|~", c);
}

std::string lower(std::string s) {
    for (char& c : s) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return s;
}

std::vector<Tok> tokenize(const std::string& src) {
    std::vector<Tok> out;
    int line = 1;
    bool ls = true;
    size_t i = 0;
    const size_t n = src.size();
    auto isDigit = [&](size_t k) { return k < n && std::isdigit(static_cast<unsigned char>(src[k])); };
    while (i < n) {
        const char c = src[i];
        if (c == '\n') { ++line; ls = true; ++i; continue; }
        if (std::isspace(static_cast<unsigned char>(c))) { ++i; continue; }
        if (c == '\\') { while (i < n && src[i] != '\n') ++i; continue; }

        Tok t;
        t.line = line;
        t.lineStart = ls;
        ls = false;
        if (isDigit(i) || (c == '.' && isDigit(i + 1))) {
            size_t j = i;
            while (isDigit(j)) ++j;
            if (j < n && src[j] == '.') { ++j; while (isDigit(j)) ++j; }
            if (j < n && (src[j] == 'e' || src[j] == 'E')) {
                size_t k = j + 1;
                if (k < n && (src[k] == '+' || src[k] == '-')) ++k;
                if (isDigit(k)) { j = k; while (isDigit(j)) ++j; }
            }
            t.kind = Tok::Num;
            t.s = src.substr(i, j - i);
            t.num = std::stod(t.s);
            i = j;
        } else if (c == '<' || c == '>' || c == '=') {
            std::string op(1, c);
            if (i + 1 < n && std::strchr("<>=", src[i + 1])) op += src[++i];
            ++i;
            t.kind = Tok::Op;
            t.s = op.find('<') != std::string::npos ? "<="
                : op.find('>') != std::string::npos ? ">=" : "=";
        } else if (c == '+' || c == '-' || c == ':') {
            t.kind = Tok::Op;
            t.s = std::string(1, c);
            ++i;
        } else if (isIdChar(c)) {
            size_t j = i;
            while (j < n && isIdChar(src[j])) ++j;
            t.kind = Tok::Id;
            t.s = src.substr(i, j - i);
            i = j;
        } else {
            throw std::runtime_error("LP parse error (line " + std::to_string(line) +
                                     "): unexpected character '" + std::string(1, c) + "'");
        }
        out.push_back(std::move(t));
    }
    Tok end;
    end.line = line;
    out.push_back(end);
    return out;
}

class Parser {
public:
    explicit Parser(std::vector<Tok> toks) : t_(std::move(toks)) {}

    Model parse() {
        Sec s;
        int len;
        bool mx;
        if (!keyword(s, len, mx) || s != Sec::Obj) fail("file must start with Minimize or Maximize");
        while (peek().kind != Tok::End) {
            if (!keyword(s, len, mx)) fail("unexpected token '" + peek().s + "'");
            p_ += len;
            switch (s) {
                case Sec::Obj:
                    M_.objSense = mx ? ObjSense::Maximize : ObjSense::Minimize;
                    parseObjective();
                    break;
                case Sec::Cons: parseConstraints(); break;
                case Sec::Bnds: parseBounds(); break;
                case Sec::Gen: parseNames(false); break;
                case Sec::Bin: parseNames(true); break;
                case Sec::Fin: return std::move(M_);
            }
        }
        return std::move(M_);
    }

private:
    enum class Sec { Obj, Cons, Bnds, Gen, Bin, Fin };
    std::vector<Tok> t_;
    size_t p_ = 0;
    Model M_;

    const Tok& peek(size_t k = 0) const { return t_[std::min(p_ + k, t_.size() - 1)]; }

    [[noreturn]] void fail(const std::string& msg) const {
        throw std::runtime_error("LP parse error (line " + std::to_string(peek().line) + "): " + msg);
    }

    bool keyword(Sec& s, int& len, bool& mx) const {
        const Tok& a = peek();
        if (a.kind != Tok::Id || !a.lineStart) return false;
        const std::string w = lower(a.s);
        len = 1;
        mx = false;
        if (w == "maximize" || w == "maximise" || w == "maximum" || w == "max") { s = Sec::Obj; mx = true; return true; }
        if (w == "minimize" || w == "minimise" || w == "minimum" || w == "min") { s = Sec::Obj; return true; }
        if ((w == "subject" || w == "such") && peek(1).kind == Tok::Id) {
            const std::string w2 = lower(peek(1).s);
            if ((w == "subject" && w2 == "to") || (w == "such" && w2 == "that")) { s = Sec::Cons; len = 2; return true; }
        }
        if (w == "st" || w == "s.t." || w == "st.") { s = Sec::Cons; return true; }
        if (w == "bounds" || w == "bound") { s = Sec::Bnds; return true; }
        if (w == "general" || w == "generals" || w == "gen" || w == "integer" || w == "integers") { s = Sec::Gen; return true; }
        if (w == "binary" || w == "binaries" || w == "bin") { s = Sec::Bin; return true; }
        if (w == "end") { s = Sec::Fin; return true; }
        if (w == "semi" || w == "semis" || w == "sos")
            fail("section '" + a.s + "' is not supported by minicplex");
        return false;
    }
    bool atStop() const {
        Sec s; int len; bool mx;
        return peek().kind == Tok::End || keyword(s, len, mx);
    }
    bool isOp(const char* op, size_t k = 0) const { return peek(k).kind == Tok::Op && peek(k).s == op; }
    bool isSense() const { return isOp("<=") || isOp(">=") || isOp("="); }
    bool isLabel() const { return peek().kind == Tok::Id && isOp(":", 1); }
    static bool isInfWord(const std::string& s) {
        const std::string w = lower(s);
        return w == "inf" || w == "infinity";
    }

    int var(const std::string& name) {
        int j = M_.findVar(name);
        return j >= 0 ? j : M_.addVar(0.0, INF, VarType::Continuous, name).id;
    }

    LinExpr parseExpr() {
        LinExpr e;
        while (!atStop() && !isSense() && !isLabel()) {
            double sign = 1.0;
            bool anySign = false;
            while (isOp("+") || isOp("-")) {
                if (isOp("-")) sign = -sign;
                ++p_;
                anySign = true;
            }
            double coef = 1.0;
            bool hasNum = false;
            if (peek().kind == Tok::Num) {
                coef = peek().num;
                ++p_;
                hasNum = true;
            }
            if (peek().kind == Tok::Id && !atStop() && !isLabel()) {
                e.terms[var(peek().s)] += sign * coef;
                ++p_;
            } else if (hasNum) {
                e.constant += sign * coef;
            } else if (anySign) {
                fail("dangling sign");
            } else {
                fail("unexpected token '" + peek().s + "'");
            }
        }
        return e;
    }

    double parseValue() {
        double sign = 1.0;
        while (isOp("+") || isOp("-")) {
            if (isOp("-")) sign = -sign;
            ++p_;
        }
        if (peek().kind == Tok::Num) { double v = peek().num; ++p_; return sign * v; }
        if (peek().kind == Tok::Id && isInfWord(peek().s)) { ++p_; return sign * INF; }
        fail("expected a number");
    }

    Sense parseSense() {
        if (!isSense()) fail("expected <=, >= or =");
        Sense s = isOp("<=") ? Sense::LE : isOp(">=") ? Sense::GE : Sense::EQ;
        ++p_;
        return s;
    }

    void parseObjective() {
        if (isLabel()) {
            M_.objName = peek().s;
            p_ += 2;
        }
        M_.objective = parseExpr();
        if (!atStop()) fail("unexpected token '" + peek().s + "' in objective");
    }

    void parseConstraints() {
        while (!atStop()) {
            std::string name;
            if (isLabel()) {
                name = peek().s;
                p_ += 2;
            }
            LinExpr lhs = parseExpr();
            Sense s = parseSense();
            double rhs = parseValue();
            M_.addConstr(makeConstraint(lhs, s, LinExpr(rhs)), name);
        }
    }

    void setBound(int j, Sense s, double v) {
        auto& vi = M_.vars[j];
        if (s == Sense::LE) vi.ub = v;
        else if (s == Sense::GE) vi.lb = v;
        else vi.lb = vi.ub = v;
    }

    void parseBounds() {
        while (!atStop()) {
            const Tok& a = peek();
            const bool valueFirst = a.kind == Tok::Num || isOp("+") || isOp("-") ||
                                    (a.kind == Tok::Id && isInfWord(a.s));
            if (valueFirst) {  // v <= x [<= w]
                double v = parseValue();
                Sense s = parseSense();
                if (peek().kind != Tok::Id) fail("expected a variable name");
                int j = var(peek().s);
                ++p_;
                // "v <= x" means x >= v, and vice versa
                setBound(j, s == Sense::LE ? Sense::GE : s == Sense::GE ? Sense::LE : Sense::EQ, v);
                if (isSense()) {
                    Sense s2 = parseSense();
                    setBound(j, s2, parseValue());
                }
            } else if (a.kind == Tok::Id) {  // x free | x <= v | x >= v | x = v
                int j = var(a.s);
                ++p_;
                if (peek().kind == Tok::Id && lower(peek().s) == "free") {
                    ++p_;
                    M_.vars[j].lb = -INF;
                    M_.vars[j].ub = INF;
                } else {
                    Sense s = parseSense();
                    setBound(j, s, parseValue());
                }
            } else {
                fail("unexpected token '" + a.s + "' in Bounds");
            }
        }
    }

    void parseNames(bool binary) {
        while (!atStop()) {
            if (peek().kind != Tok::Id) fail("expected a variable name");
            auto& v = M_.vars[var(peek().s)];
            ++p_;
            if (binary) {
                v.type = VarType::Binary;
                v.lb = 0.0;
                v.ub = 1.0;
            } else {
                v.type = VarType::Integer;
            }
        }
    }
};

}  // namespace

Model readLPString(const std::string& text) { return Parser(tokenize(text)).parse(); }

Model readLPFile(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("cannot open file: " + path);
    std::stringstream ss;
    ss << in.rdbuf();
    return readLPString(ss.str());
}

}  // namespace mcplex
