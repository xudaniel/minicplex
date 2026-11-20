"""第 12 课：综合项目——选课助手。

读一张课程表（纯文本），在时间、学分、每天课数和先修课的限制下，选出“兴趣分”最高的一组课，
再把结果排成表格。把前 11 课学到的东西串起来：字符串解析、dataclass、集合、建模、异常、格式化输出。
运行：python3 python/tutorial/run.py 12
"""
import unicodedata
from dataclasses import dataclass

from check import lesson, eq, raises, that, done
from minicplex import LinExpr, Model, ObjSense, Status, VarType, solve

CATALOG = """
# 课程     学分  每周小时  上课日  兴趣
Python     4     6        Mon     9
算法       4     8        Tue     10
数据库     3     5        Mon     7
运筹学     3     6        Wed     10
英语       2     3        Tue     4
体育       1     2        Wed     3
写作       2     4        Mon     5
"""
DAYS = ["Mon", "Tue", "Wed"]


@dataclass(frozen=True)
class Course:
    name: str
    credits: int
    hours: int
    day: str
    interest: int


def parse(text):
    """解析课程表：跳过空行和 # 开头的注释行；每行按空白切成 5 段。格式不对时 raise ValueError。"""
    # TODO text.splitlines() 拿到每一行；line.strip()；line.split() 切成几段；int() 转数字
    # >>>
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        f = line.split()
        if len(f) != 5:
            raise ValueError(f"这一行应该有 5 段：{line}")
        try:
            out.append(Course(f[0], int(f[1]), int(f[2]), f[3], int(f[4])))
        except ValueError:
            raise ValueError(f"数字写错了：{line}") from None
    return out
    # <<<


def choose(courses, max_hours, min_credits):
    """选课：每门课一个 0-1 变量。限制：
    每周总小时 ≤ max_hours；总学分 ≥ min_credits；每天最多 2 门；选“算法”就必须选“Python”（先修课）。
    目标：总兴趣分最大。返回选中的课名（按课程表顺序）；无解时返回空列表。"""
    # TODO take = [m.add_var(0, 1, VarType.BINARY, ...) for c in courses]；
    #      sum((c.hours * t for c, t in zip(courses, take)), LinExpr()) 这样把一列项加起来；
    #      每天一条约束；先修课：take[算法] <= take[Python]
    # >>>
    m = Model()
    take = [m.add_var(0, 1, VarType.BINARY, f"take_{k}") for k in range(len(courses))]
    pairs = list(zip(courses, take))
    m.add_constr(sum((c.hours * t for c, t in pairs), LinExpr()) <= max_hours, "hours")
    m.add_constr(sum((c.credits * t for c, t in pairs), LinExpr()) >= min_credits, "credits")
    for day in DAYS:
        m.add_constr(sum((t for c, t in pairs if c.day == day), LinExpr()) <= 2, f"day_{day}")
    index = {c.name: t for c, t in pairs}
    if "Python" in index and "算法" in index:
        m.add_constr(index["算法"] <= index["Python"], "prereq")
    m.set_objective(sum((c.interest * t for c, t in pairs), LinExpr()), ObjSense.MAXIMIZE)
    r = solve(m)
    if r.status != Status.OPTIMAL:
        return []
    return [c.name for c, t in pairs if r.value(t) > 0.5]
    # <<<


def _pad(s, width):
    """按屏幕显示宽度补空格（第 10 课的 pad）：一个汉字占 2 格，这样中英文混排的表格也是齐的。"""
    w = sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in s)
    return s + " " * max(0, width - w)


def report(courses, chosen):
    """把选中的课排成表格（这段不用写，看看第 10 课的格式化和 pad 在这里怎么用）。"""
    rows = [c for c in courses if c.name in chosen]
    lines = [f"  {_pad(c.name, 8)} {c.day}  {c.credits} 学分  {c.hours} 小时  兴趣 {c.interest}" for c in rows]
    lines.append(f"  合计：{sum(c.credits for c in rows)} 学分，{sum(c.hours for c in rows)} 小时，"
                 f"兴趣 {sum(c.interest for c in rows)}")
    return "\n".join(lines)


def prereq_always_holds():
    for h in range(41):
        c = choose(parse(CATALOG), h, 0)
        if "算法" in c and "Python" not in c:
            return False
    return True


def at_most_two_per_day():
    courses = parse(CATALOG)
    for h in range(41):
        c = set(choose(courses, h, 0))
        for day in DAYS:
            if sum(1 for x in courses if x.day == day and x.name in c) > 2:
                return False
    return True


lesson("第 12 课：选课助手")
eq("课程表里有 7 门课", 7, lambda: len(parse(CATALOG)))
eq("第一门是 Python，4 学分", Course("Python", 4, 6, "Mon", 9), lambda: parse(CATALOG)[0])
raises("少一段的行会报错", ValueError, lambda: parse("Python 4 6 Mon"))
raises("数字写错也会报错", ValueError, lambda: parse("Python 四 6 Mon 9"))
eq("每周 20 小时、至少 10 学分：选 Python、数据库、运筹学、英语", ["Python", "数据库", "运筹学", "英语"],
   lambda: choose(parse(CATALOG), 20, 10))
eq("每周 28 小时：加上算法", ["Python", "算法", "数据库", "运筹学", "英语"], lambda: choose(parse(CATALOG), 28, 10))
eq("每周只有 12 小时：选 Python、运筹学", ["Python", "运筹学"], lambda: choose(parse(CATALOG), 12, 6))
eq("每周 5 小时却要 10 学分：无解", [], lambda: choose(parse(CATALOG), 5, 10))
that("不管时间多少，选了算法就一定选了 Python", prereq_always_holds)
that("不管时间多少，每天最多 2 门课", at_most_two_per_day)
try:
    all_courses = parse(CATALOG)
    print("\n选课结果（每周 ≤ 20 小时，≥ 10 学分）：")
    print(report(all_courses, choose(all_courses, 20, 10)) + "\n")
except NotImplementedError:
    print("\n（写完 parse 和 choose 后，这里会打印选课表）\n")
done()
