"""对拍：把 minicplex 的结果与 Google OR-Tools（GLOP／SCIP）逐题比对；不一致时再请 HiGHS 当裁判。

用法：
  ./build/minicplex_gen --kind mixed --count 300 --seed 1 --out fuzz
  ./build/minicplex_bench fuzz --gap 1e-9 --quiet --csv fuzz/ours.csv
  python3 tools/fuzz_vs_ortools.py fuzz fuzz/ours.csv

纯 LP 题（--kind lp）还会对比单纯形迭代次数，方便和 GLOP 比效率。
有任何一题不一致，退出码为 1，并打印文件名和三方结果，便于复现。
"""
import csv
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fuzz_vs_highs import agree  # noqa: E402
from verify_with_highs import solve_with_highs  # noqa: E402
from verify_with_ortools import solve_with_ortools  # noqa: E402


def _same(st, val, ref_st, ref_val):
    if st != ref_st:
        return False
    return st != 'Optimal' or abs(val - ref_val) <= 1e-6 * (1 + abs(ref_val))


def main():
    folder, ours_csv = sys.argv[1], sys.argv[2]
    rows = list(csv.DictReader(open(ours_csv)))
    bad, counts, ratios = [], {}, []
    for r in rows:
        path = os.path.join(folder, r['model'])
        st, val, name, it = solve_with_ortools(path)
        obj = float(r['objective']) if r['objective'] not in ('nan', '') else math.nan
        counts[f'{name} {st}'] = counts.get(f'{name} {st}', 0) + 1
        # 判定规则与 HiGHS 对拍完全相同（含 NodeLimit、InfeasibleOrUnbounded 的处理）
        if not agree(path, r['status'], obj, st, val):
            h_st, h_val = solve_with_highs(path)
            judge = ('OR-Tools 与 HiGHS 一致 → 多半是 minicplex 的问题'
                     if val is not None and h_val is not None and _same(st, val, h_st, h_val)
                     or (val is None and st == h_st)
                     else 'OR-Tools 与 HiGHS 也不一致 → 需要人工判断')
            bad.append((r['model'], r['status'], obj, f'{name} {st}', val, h_st, h_val, judge))
        elif name == 'GLOP' and r['status'] == 'Optimal' and it > 0:
            ratios.append(int(r['iterations']) / it)
    summary = ', '.join(f'{k} {v}' for k, v in sorted(counts.items()))
    print(f'{len(rows) - len(bad)}/{len(rows)} agree with OR-Tools ({summary})')
    if ratios:
        print(f'pure LP: minicplex / GLOP simplex iterations, median {statistics.median(ratios):.2f}x '
              f'over {len(ratios)} models (GLOP 含预处理，迭代次数仅作参考)')
    for b in bad:
        print('  MISMATCH %s: minicplex %s %s | OR-Tools %s %s | HiGHS %s %s\n    %s' % b)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
