#!/usr/bin/env python3
"""对比 C++ 版和 Java / Python 版在同一批模型上的结果（两份 minicplex_bench 格式的 CSV）。

    python3 tools/compare_java_cpp.py cpp.csv java.csv [--strict]
    python3 tools/compare_java_cpp.py cpp.csv py.csv --strict --label Python

状态和目标值必须一致；加 --strict 时，节点数和单纯形迭代次数也必须一模一样
（Java、Python 版都是逐行移植，同一台机器上应当走完全相同的计算路径）。
"""
import csv
import math
import sys


def main():
    argv = sys.argv[1:]
    label = "Java"
    if "--label" in argv:
        k = argv.index("--label")
        label = argv[k + 1]
        del argv[k:k + 2]
    args = [a for a in argv if not a.startswith("--")]
    strict = "--strict" in argv
    if len(args) != 2:
        sys.exit(__doc__)
    a = {r["model"]: r for r in csv.DictReader(open(args[0], encoding="utf-8"))}
    b = {r["model"]: r for r in csv.DictReader(open(args[1], encoding="utf-8"))}
    if a.keys() != b.keys():
        sys.exit(f"模型列表不同：只在 C++ 里 {sorted(a.keys() - b.keys())[:5]}，只在 {label} 里 {sorted(b.keys() - a.keys())[:5]}")
    same_res = same_path = 0
    bad = []
    for k in sorted(a):
        x, y = a[k], b[k]
        ox, oy = float(x["objective"]), float(y["objective"])
        ok = x["status"] == y["status"] and (
            (math.isnan(ox) and math.isnan(oy)) or abs(ox - oy) <= 1e-6 * (1 + abs(ox)))
        path = x["nodes"] == y["nodes"] and x["iterations"] == y["iterations"]
        same_res += ok
        same_path += path
        if not ok or (strict and not path):
            bad.append(f"  {k}: C++ {x['status']} {ox:g} ({x['nodes']} 节点, {x['iterations']} 迭代)"
                       f"  {label} {y['status']} {oy:g} ({y['nodes']} 节点, {y['iterations']} 迭代)")
    n = len(a)
    print(f"{n} 个模型：状态+目标值一致 {same_res}/{n}，节点数+迭代次数一致 {same_path}/{n}")
    tc = sum(float(r["seconds"]) for r in a.values())
    tj = sum(float(r["seconds"]) for r in b.values())
    print(f"总用时：C++ {tc:.3f}s，{label} {tj:.3f}s")
    if bad:
        print("不一致的模型：")
        print("\n".join(bad[:20]))
        sys.exit(1)


if __name__ == "__main__":
    main()
