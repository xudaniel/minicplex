# 用 Python API 建模的完整演示（对应 C++ 的 api_demo.cpp）。
# 家具店做椅子和桌子（只能整件）。
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()

m = Model()
chairs = m.add_var(0, INF, VarType.INTEGER, "chairs")
tables = m.add_var(0, INF, VarType.INTEGER, "tables")

m.add_constr(2 * chairs + 5 * tables <= 40, "wood")
m.add_constr(3 * chairs + 2 * tables <= 30, "labor")
m.add_constr(chairs >= tables, "mix")
m.set_objective(30 * chairs + 70 * tables, ObjSense.MAXIMIZE)

print("Model in CPLEX LP format:")
print(m.to_lp())

r = solve(m, Params(verbose=True))

print()
print(f"status = {r.status}, profit = {g(r.objective)}")
for j, v in enumerate(m.vars):
    print(f"  {v.name} = {g(r.x[j])}")
