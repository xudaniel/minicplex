// 批量求解器：求解目录（或文件列表）里的所有 .lp 模型，打印结果表并可写 CSV。
// 既用于基准测试，也为对拍脚本（fuzz_vs_highs.py）提供 minicplex 的结果。
//
// 用法：
//   minicplex_bench bench/models --csv new.csv
//   minicplex_bench fuzz/ --gap 1e-9 --csv fuzz/ours.csv --quiet
#include <algorithm>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

#include "lp_reader.hpp"
#include "solver.hpp"

using namespace mcplex;
namespace fs = std::filesystem;

int main(int argc, char** argv) {
    std::vector<std::string> files;
    std::string csv;
    bool quiet = false;
    Params P;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--csv" && i + 1 < argc) csv = argv[++i];
        else if (a == "--gap" && i + 1 < argc) P.mipGap = std::stod(argv[++i]);
        else if (a == "--time" && i + 1 < argc) P.timeLimit = std::stod(argv[++i]);
        else if (a == "--quiet") quiet = true;
        else if (fs::is_directory(a)) {
            for (const auto& e : fs::directory_iterator(a))
                if (e.path().extension() == ".lp") files.push_back(e.path().string());
        } else files.push_back(a);
    }
    std::sort(files.begin(), files.end());
    if (files.empty()) {
        std::fprintf(stderr, "usage: minicplex_bench DIR|FILES... [--csv out.csv] [--gap G] [--time T] [--quiet]\n");
        return 2;
    }

    std::FILE* out = csv.empty() ? nullptr : std::fopen(csv.c_str(), "w");
    if (out) std::fprintf(out, "model,status,objective,nodes,iterations,seconds\n");
    if (!quiet)
        std::printf("%-36s %-22s %16s %9s %11s %9s\n", "model", "status", "objective", "nodes", "iterations", "seconds");

    double totalSec = 0;
    long totalNodes = 0, totalIters = 0;
    int failures = 0;
    for (const auto& f : files) {
        const std::string name = fs::path(f).filename().string();
        try {
            Model M = readLPFile(f);
            Result R = solve(M, P);
            if (R.hasSolution && !checkFeasible(M, R.x, 1e-5)) {
                std::fprintf(stderr, "%s: returned solution is NOT feasible\n", name.c_str());
                ++failures;
            }
            totalSec += R.seconds;
            totalNodes += R.nodes;
            totalIters += R.lpIterations;
            if (!quiet)
                std::printf("%-36s %-22s %16.10g %9ld %11ld %9.3f\n", name.c_str(), toString(R.status),
                            R.hasSolution ? R.objective : NAN, R.nodes, R.lpIterations, R.seconds);
            if (out)
                std::fprintf(out, "%s,%s,%.12g,%ld,%ld,%.6f\n", name.c_str(), toString(R.status),
                             R.hasSolution ? R.objective : NAN, R.nodes, R.lpIterations, R.seconds);
        } catch (const std::exception& e) {
            std::fprintf(stderr, "%s: error: %s\n", name.c_str(), e.what());
            ++failures;
            if (out) std::fprintf(out, "%s,Error,nan,0,0,0\n", name.c_str());
        }
    }
    if (out) std::fclose(out);
    std::printf("%zu models, %ld nodes, %ld simplex iterations, %.3f s total%s\n", files.size(), totalNodes,
                totalIters, totalSec, failures ? " — FAILURES!" : "");
    return failures ? 1 : 0;
}
