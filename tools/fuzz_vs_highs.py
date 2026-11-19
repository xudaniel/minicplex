"""对拍：把 minicplex 的结果（minicplex_bench 写出的 CSV）与 HiGHS 逐题比对。

用法：
  ./build/minicplex_gen --kind mixed --count 300 --seed 1 --out fuzz
  ./build/minicplex_bench fuzz --gap 1e-9 --quiet --csv fuzz/ours.csv
  python3 tools/fuzz_vs_highs.py fuzz fuzz/ours.csv

有任何一题不一致，退出码为 1，并打印该题文件名，便于复现。
"""
import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_with_highs import solve_with_highs  # noqa: E402


def agree(path, ours_status, ours_obj, highs_status, highs_obj):
    if ours_status == 'Optimal':
        return highs_status == 'Optimal' and abs(ours_obj - highs_obj) <= 1e-6 * (1 + abs(highs_obj))
    if ours_status == 'Infeasible':
        return highs_status in ('Infeasible', 'InfeasibleOrUnbounded')
    if ours_status == 'Unbounded':
        return highs_status in ('Unbounded', 'InfeasibleOrUnbounded')
    if ours_status == 'InfeasibleOrUnbounded':
        if highs_status in ('Infeasible', 'Unbounded', 'InfeasibleOrUnbounded'):
            return True
        # HiGHS 的 MIP 求解器在 LP 松弛无界时偶尔会报“最优”。按 Meyer 定理（有理数据），
        # 整数规划可行且 LP 松弛无界 ⇒ 整数规划无界，所以此时以 LP 松弛的结论为准。
        relax_status, _ = solve_with_highs(path, relax=True)
        return relax_status in ('Unbounded', 'InfeasibleOrUnbounded')
    return False


def main():
    folder, ours_csv = sys.argv[1], sys.argv[2]
    rows = list(csv.DictReader(open(ours_csv)))
    bad, counts = [], {}
    for r in rows:
        path = os.path.join(folder, r['model'])
        st, val = solve_with_highs(path)
        obj = float(r['objective']) if r['objective'] not in ('nan', '') else math.nan
        counts[st] = counts.get(st, 0) + 1
        if not agree(path, r['status'], obj, st, val):
            bad.append((r['model'], r['status'], obj, st, val))
    summary = ', '.join(f'{k} {v}' for k, v in sorted(counts.items()))
    print(f'{len(rows) - len(bad)}/{len(rows)} agree with HiGHS ({summary})')
    for b in bad:
        print('  MISMATCH %s: minicplex %s %s | HiGHS %s %s' % b)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
