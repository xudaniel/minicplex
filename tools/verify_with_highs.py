# 用 scipy 自带的 HiGHS 求解器独立验算 minicplex 导出的 .lp 文件。
# 用法：python3 tools/verify_with_highs.py model.lp
# 只支持 minicplex 自己写出的 LP 格式（Model::writeLP）。
import re, sys
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

text = open(sys.argv[1]).read()
lines = [l.split('\\')[0] for l in text.splitlines()]
sec, obj, cons, cur = None, '', [], ''
bounds, gen, binv, sense = [], [], [], 1
for l in lines:
    s = l.strip(); low = s.lower()
    if low in ('minimize', 'maximize'): sec = 'obj'; sense = -1 if low == 'maximize' else 1; continue
    if low == 'subject to': sec = 'con'; continue
    if low == 'bounds': sec = 'bnd'; continue
    if low == 'general': sec = 'gen'; continue
    if low == 'binary': sec = 'bin'; continue
    if low == 'end': break
    if not s: continue
    if sec == 'obj': obj += ' ' + s
    elif sec == 'con':
        cur += ' ' + s
        if re.search(r'(<=|>=|=)\s*-?[\d.e+-]+\s*$', cur): cons.append(cur); cur = ''
    elif sec == 'bnd': bounds.append(s)
    elif sec == 'gen': gen += s.split()
    elif sec == 'bin': binv += s.split()

names = {}
def terms(expr):
    out = {}; const = 0.0
    for sign, coef, var in re.findall(r'([+-])\s*([\d.e+-]+\s+)?([A-Za-z_][\w.]*)?', expr):
        if not coef and not var: continue
        c = float(coef) if coef else 1.0
        c = -c if sign == '-' else c
        if var: names.setdefault(var, len(names)); out[var] = out.get(var, 0) + c
        else: const += c
    return out, const

o, oc = terms(obj.split(':', 1)[1])
rows = []
for c in cons:
    body = c.split(':', 1)[1]
    m = re.match(r'(.*?)(<=|>=|=)\s*(-?[\d.e+-]+)\s*$', body)
    t, _ = terms(m.group(1)); rows.append((t, m.group(2), float(m.group(3))))
for v in gen + binv: names.setdefault(v, len(names))
bounds_parsed = []
for b in bounds:
    p = b.split()
    for v in [p[0], p[2] if len(p) > 2 else None]:
        if v and not v.lstrip('-').replace('.', '').replace('e', '').isdigit() and v not in ('inf', '-inf'):
            names.setdefault(v, len(names))
    bounds_parsed.append(p)
n = len(names)
lb = np.zeros(n); ub = np.full(n, np.inf)
for p in bounds_parsed:
    if len(p) == 5: lb[names[p[2]]] = float(p[0]); ub[names[p[2]]] = float(p[4])
    elif p[1] == 'free': lb[names[p[0]]] = -np.inf; ub[names[p[0]]] = np.inf
    elif p[1] == '=': lb[names[p[0]]] = ub[names[p[0]]] = float(p[2])
    elif p[1] == '>=': lb[names[p[0]]] = float(p[2])
    elif p[1] == '<=': ub[names[p[0]]] = float(p[2])
for v in binv: lb[names[v]] = 0; ub[names[v]] = 1
cvec = np.zeros(n)
for v, c in o.items(): cvec[names[v]] = c * sense
A = np.zeros((len(rows), n)); lo = np.full(len(rows), -np.inf); hi = np.full(len(rows), np.inf)
for i, (t, s, r) in enumerate(rows):
    for v, c in t.items(): A[i, names[v]] = c
    if s in ('<=', '='): hi[i] = r
    if s in ('>=', '='): lo[i] = r
integ = np.zeros(n)
for v in gen + binv: integ[names[v]] = 1
res = milp(cvec, constraints=LinearConstraint(A, lo, hi), bounds=Bounds(lb, ub),
           integrality=integ, options={'mip_rel_gap': 1e-9})
print('HiGHS status:', res.message)
print('HiGHS objective:', sense * res.fun + oc, f'({n} vars, {len(rows)} rows)')
