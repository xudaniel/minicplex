// minicplex command-line solver:  minicplex [options] model.lp
#include <cmath>
#include <cstdio>
#include <fstream>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>

#include "lp_reader.hpp"
#include "solver.hpp"

using namespace mcplex;

static void usage() {
    std::puts(
        "usage: minicplex [options] model.lp\n"
        "  --relax         solve the LP relaxation only\n"
        "  --gap G         relative MIP gap (default 1e-6)\n"
        "  --nodes N       node limit\n"
        "  --time T        time limit in seconds\n"
        "  --quiet         no node log\n"
        "  --all           print zero-valued variables too\n"
        "  --write FILE    write the parsed model back out in LP format");
}

int main(int argc, char** argv) {
    Params P;
    P.verbose = true;
    std::string path, writePath;
    bool printAll = false;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        auto next = [&]() -> const char* {
            if (i + 1 >= argc) { usage(); std::exit(2); }
            return argv[++i];
        };
        if (a == "-h" || a == "--help") { usage(); return 0; }
        else if (a == "--relax") P.relaxIntegrality = true;
        else if (a == "--gap") P.mipGap = std::atof(next());
        else if (a == "--nodes") P.nodeLimit = std::atol(next());
        else if (a == "--time") P.timeLimit = std::atof(next());
        else if (a == "--quiet") P.verbose = false;
        else if (a == "--all") printAll = true;
        else if (a == "--write") writePath = next();
        else if (!a.empty() && a[0] == '-') { usage(); return 2; }
        else path = a;
    }
    if (path.empty()) { usage(); return 2; }

    try {
        Model M = readLPFile(path);
        std::printf("minicplex 0.2 | %s\n", path.c_str());
        std::printf("  %d variables (%d integer), %d constraints, %s\n\n", M.numVars(),
                    M.numIntegers(), M.numConstrs(),
                    M.objSense == ObjSense::Maximize ? "maximize" : "minimize");
        if (!writePath.empty()) {
            std::ofstream out(writePath);
            M.writeLP(out);
        }

        Result R = solve(M, P);

        std::printf("\nStatus:       %s\n", toString(R.status));
        if (R.hasSolution) {
            std::printf("Objective:    %.10g\n", R.objective);
            if (M.numIntegers() > 0 && !P.relaxIntegrality)
                std::printf("Best bound:   %.10g   (gap %.4f%%)\n", R.bestBound, 100.0 * R.gap);
        }
        std::printf("Nodes:        %ld\nIterations:   %ld\nTime:         %.3f s\n", R.nodes,
                    R.lpIterations, R.seconds);
        if (R.hasSolution) {
            std::printf("\n%-20s %16s\n", "Variable", "Value");
            for (int j = 0; j < M.numVars(); ++j) {
                double v = R.x[j];
                if (std::abs(v) < 1e-9) v = 0.0;
                if (v != 0.0 || printAll) std::printf("%-20s %16.10g\n", M.vars[j].name.c_str(), v);
            }
        }
        return R.hasSolution ? 0 : 1;
    } catch (const std::exception& e) {
        std::fprintf(stderr, "error: %s\n", e.what());
        return 2;
    }
}
