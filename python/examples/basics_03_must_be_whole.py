# 入门例子 03：必须是整数
#
# 问题（面包店）：蛋糕每个赚 5 元，面包每个赚 4 元。
#   - 面粉只有 24 公斤：蛋糕用 6 公斤，面包用 4 公斤
#   - 人工只有 6 小时：蛋糕用 1 小时，面包用 2 小时
# 不能卖半个，怎么做最赚钱？
#
# 这个例子会算两遍：先允许做半个，再要求整数，看看有什么不同。
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()
m = Model()
# VarType.INTEGER 表示“必须是整数”
cake = m.add_var(0, INF, VarType.INTEGER, "cake")
bread = m.add_var(0, INF, VarType.INTEGER, "bread")
m.add_constr(6 * cake + 4 * bread <= 24, "flour")
m.add_constr(1 * cake + 2 * bread <= 6, "labor")
m.set_objective(5 * cake + 4 * bread, ObjSense.MAXIMIZE)

# 第一遍：暂时忽略“必须是整数”（relax_integrality = 放松整数要求）
a = solve(m, Params(relax_integrality=True))
print(f"允许做半个：蛋糕 {g(a.value(cake))}，面包 {g(a.value(bread))}，赚 {g(a.objective)} 元")

# 很多人会想：把小数部分去掉不就行了？
c, b = float(int(a.value(cake))), float(int(a.value(bread)))
print(f"直接去掉小数：蛋糕 {g(c)}，面包 {g(b)}，赚 {g(5 * c + 4 * b)} 元")

# 第二遍：真正的整数规划
r = solve(m)
print(f"整数最优解：  蛋糕 {g(r.value(cake))}，面包 {g(r.value(bread))}，赚 {g(r.objective)} 元")
print("结论：整数最优解不是“去掉小数”那么简单，需要分支定界来找。")
