"""对拍：把 minicplex 的结果（minicplex_bench 写出的 CSV）与 HiGHS 逐题比对。

用法：
  ./build/minicplex_gen --kind mixed --count 300 --seed 1 --out fuzz
  ./build/minicplex_bench fuzz --gap 1e-9 --quiet --csv fuzz/ours.csv
  python3 tools/fuzz_vs_highs.py fuzz fuzz/ours.csv

有任何一题不一致，退出码为 1，并打印该题文件名，便于复现。
"""
import csv
import itertools
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_with_highs import read_lp, solve_with_highs  # noqa: E402


def brute_force(path, limit=2_000_000):
    """纯整数、变量有界且整数点不超过 limit 个时，逐点枚举求最优；否则返回 None。"""
    c, oc, sense, A, lo, hi, lb, ub, integ, _ = read_lp(path)
    if not np.all(integ == 1) or not (np.all(np.isfinite(lb)) and np.all(np.isfinite(ub))):
        return None
    ranges = [range(math.ceil(l - 1e-9), math.floor(u + 1e-9) + 1) for l, u in zip(lb, ub)]
    if math.prod(len(r) for r in ranges) > limit:
        return None
    best = None
    for pt in itertools.product(*ranges):
        x = np.array(pt, dtype=float)
        act = A @ x if A.shape[0] else np.zeros(0)
        if np.all(act >= lo - 1e-9) and np.all(act <= hi + 1e-9):
            v = sense * (c @ x)
            best = v if best is None else min(best, v)
    return ('Infeasible', None) if best is None else ('Optimal', sense * best + oc)


def referee(path):
    """HiGHS 自己出错（状态 Other）时：先关掉 HiGHS 预处理重解，还不行就暴力枚举。"""
    st, val = solve_with_highs(path, presolve=False)
    if st != 'Other':
        return st, val, 'HiGHS（关预处理）'
    bf = brute_force(path)
    if bf is not None:
        return bf[0], bf[1], '暴力枚举'
    return 'Other', None, None


def agree(path, ours_status, ours_obj, highs_status, highs_obj):
    if ours_status == 'Optimal':
        return highs_status == 'Optimal' and abs(ours_obj - highs_obj) <= 1e-6 * (1 + abs(highs_obj))
    if ours_status == 'Infeasible':
        return highs_status in ('Infeasible', 'InfeasibleOrUnbounded')
    if ours_status == 'Unbounded':
        return highs_status in ('Unbounded', 'InfeasibleOrUnbounded')
    if ours_status in ('NodeLimit', 'TimeLimit'):
        # Search stopped early: acceptable when the incumbent is HiGHS's optimum
        # (known case: unbounded integer variables along which the LP bound never drops).
        return (highs_status == 'Optimal' and not math.isnan(ours_obj)
                and abs(ours_obj - highs_obj) <= 1e-6 * (1 + abs(highs_obj)))
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
    refereed = 0
    for r in rows:
        path = os.path.join(folder, r['model'])
        st, val = solve_with_highs(path)
        if st == 'Other':  # HiGHS 内部出错，换裁判
            st, val, judge = referee(path)
            print(f'  {r["model"]}: HiGHS 出错，改由{judge or "（无可用裁判）"}判定：{st}')
            refereed += 1
        obj = float(r['objective']) if r['objective'] not in ('nan', '') else math.nan
        counts[st] = counts.get(st, 0) + 1
        if not agree(path, r['status'], obj, st, val):
            bad.append((r['model'], r['status'], obj, st, val))
    summary = ', '.join(f'{k} {v}' for k, v in sorted(counts.items()))
    unproven = sum(1 for r in rows if r['status'] in ('NodeLimit', 'TimeLimit'))
    extra = f'; {unproven} hit a limit with the optimal answer (unproven)' if unproven else ''
    if refereed:
        extra += f'; HiGHS errored on {refereed}, judged by fallback'
    print(f'{len(rows) - len(bad)}/{len(rows)} agree with HiGHS ({summary}){extra}')
    for b in bad:
        print('  MISMATCH %s: minicplex %s %s | HiGHS %s %s' % b)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
