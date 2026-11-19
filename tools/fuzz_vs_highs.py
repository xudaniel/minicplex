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


def agree(ours_status, ours_obj, highs_status, highs_obj):
    if ours_status == 'Optimal':
        return highs_status == 'Optimal' and abs(ours_obj - highs_obj) <= 1e-6 * (1 + abs(highs_obj))
    if ours_status == 'Infeasible':
        return highs_status == 'Infeasible'
    if ours_status == 'Unbounded':
        return highs_status == 'Unbounded'
    if ours_status == 'InfeasibleOrUnbounded':
        return highs_status in ('Infeasible', 'Unbounded')
    return False


def main():
    folder, ours_csv = sys.argv[1], sys.argv[2]
    rows = list(csv.DictReader(open(ours_csv)))
    bad, counts = [], {}
    for r in rows:
        st, val = solve_with_highs(os.path.join(folder, r['model']))
        obj = float(r['objective']) if r['objective'] not in ('nan', '') else math.nan
        counts[st] = counts.get(st, 0) + 1
        if not agree(r['status'], obj, st, val):
            bad.append((r['model'], r['status'], obj, st, val))
    summary = ', '.join(f'{k} {v}' for k, v in sorted(counts.items()))
    print(f'{len(rows) - len(bad)}/{len(rows)} agree with HiGHS ({summary})')
    for b in bad:
        print('  MISMATCH %s: minicplex %s %s | HiGHS %s %s' % b)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
