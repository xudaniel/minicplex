"""基准对比：比较两次 minicplex_bench 的 CSV（例如基线 vs 新版本）。

用法：python3 tools/bench_compare.py bench/baseline.csv new.csv

状态或目标值不一致 → 退出码 1（说明改坏了）；节点数、迭代次数、用时的变化只打印，不判失败
（CI 机器的计时有波动）。
"""
import csv
import math
import sys


def load(p):
    return {r['model']: r for r in csv.DictReader(open(p))}


def main():
    base, new = load(sys.argv[1]), load(sys.argv[2])
    print(f"{'model':34} {'status':>9} {'nodes old→new':>18} {'iters old→new':>20} {'time old→new (s)':>22} {'speedup':>8}")
    broken = 0
    tb = tn = 0.0
    for name in sorted(base):
        if name not in new:
            continue
        a, b = base[name], new[name]
        oa, ob = float(a['objective']), float(b['objective'])
        same = a['status'] == b['status'] and (
            (math.isnan(oa) and math.isnan(ob)) or abs(oa - ob) <= 1e-6 * (1 + abs(oa)))
        broken += not same
        ta, tnew = float(a['seconds']), float(b['seconds'])
        tb += ta
        tn += tnew
        speed = f'{ta / tnew:.1f}x' if tnew > 0 else '-'
        print(f"{name:34} {'ok' if same else 'CHANGED':>9} {a['nodes'] + '→' + b['nodes']:>18} "
              f"{a['iterations'] + '→' + b['iterations']:>20} {f'{ta:.3f}→{tnew:.3f}':>22} {speed:>8}")
    print(f'total time {tb:.3f}s → {tn:.3f}s' + (f'  ({tb / tn:.1f}x)' if tn > 0 else ''))
    if broken:
        print(f'{broken} model(s) changed status/objective!')
    sys.exit(1 if broken else 0)


if __name__ == '__main__':
    main()
