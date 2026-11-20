# 简单例子 1：线性规划（LP）—— 面包店生产计划
#
# 面包店每天做蛋糕和面包：
#   蛋糕：每个利润 5 元，用面粉 6 kg、人工 1 小时
#   面包：每个利润 4 元，用面粉 4 kg、人工 2 小时
#   每天最多 24 kg 面粉、6 小时人工
# 问：各做多少，利润最大？（这里允许做半个，所以是连续变量）
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()
m = Model()

# 1. 决策变量：做多少个（>= 0，连续）
cake = m.add_var(0, INF, VarType.CONTINUOUS, "cake")
bread = m.add_var(0, INF, VarType.CONTINUOUS, "bread")

# 2. 约束
m.add_constr(6 * cake + 4 * bread <= 24, "flour")  # 面粉
m.add_constr(1 * cake + 2 * bread <= 6, "labor")   # 人工

# 3. 目标：利润最大
m.set_objective(5 * cake + 4 * bread, ObjSense.MAXIMIZE)

# 4. 求解
r = solve(m)
print(f"状态：{r.status}")
print(f"最大利润：{g(r.objective)} 元")
print(f"蛋糕：{g(r.value(cake))} 个")
print(f"面包：{g(r.value(bread))} 个")
