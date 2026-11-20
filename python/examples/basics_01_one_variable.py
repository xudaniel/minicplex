# 入门例子 01：只有一个变量
#
# 问题：你有 10 元，苹果 2 元一个。最多能买几个苹果？
# 答案一眼就能看出是 5 个。这个例子只为了认识最基本的四个步骤。
#
# 运行：python3 python/examples/basics_01_one_variable.py   （加 --trace 可以看到求解过程）
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *  # minicplex 的全部功能都在这个包里

use_utf8_output()  # 让中文在任何系统上都能正常显示

# 第 1 步：建一个空模型
m = Model()

# 第 2 步：建变量。apples = 买几个苹果，最少 0 个，没有上限
apples = m.add_var(0, INF, VarType.CONTINUOUS, "apples")

# 第 3 步：加限制。花的钱不能超过 10 元：2 × 苹果数 ≤ 10
m.add_constr(2 * apples <= 10, "money")

# 第 4 步：定目标。苹果越多越好：最大化 苹果数
m.set_objective(apples, ObjSense.MAXIMIZE)

# 求解
p = Params(trace="--trace" in sys.argv[1:])
r = solve(m, p)

print(f"状态：{r.status}")  # Optimal = 找到了最优解
print(f"最多买 {g(r.value(apples))} 个苹果")
