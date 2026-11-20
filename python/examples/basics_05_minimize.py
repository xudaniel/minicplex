# 入门例子 05：求最小（花最少的钱）
#
# 问题：每天要喝牛奶、吃鸡蛋来补充营养，至少需要：
#   - 蛋白质 30 克
#   - 钙 600 毫克
#            价格   蛋白质   钙
#   一杯牛奶  3 元    8 克   300 毫克
#   一个鸡蛋  1 元    6 克    30 毫克
# 牛奶按杯、鸡蛋按个，都必须是整数。怎么搭配最省钱？
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()
m = Model()
milk = m.add_var(0, INF, VarType.INTEGER, "milk")
egg = m.add_var(0, INF, VarType.INTEGER, "egg")

# “至少”用 >=
m.add_constr(8 * milk + 6 * egg >= 30, "protein")
m.add_constr(300 * milk + 30 * egg >= 600, "calcium")

# 目标是花钱最少：MINIMIZE
m.set_objective(3 * milk + 1 * egg, ObjSense.MINIMIZE)

r = solve(m)
mk, eg = r.value(milk), r.value(egg)
print(f"牛奶 {g(mk)} 杯，鸡蛋 {g(eg)} 个，花 {g(r.objective)} 元")
print(f"蛋白质 {g(8 * mk + 6 * eg)} 克（至少 30），钙 {g(300 * mk + 30 * eg)} 毫克（至少 600）")
