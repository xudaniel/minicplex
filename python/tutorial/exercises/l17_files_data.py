"""第 17 课：文件和数据——pathlib、CSV、JSON。

真实的数据往往在文件里：一张 CSV 表、一个 JSON 配置。这一课做一个完整的小流程：
读 CSV（商品）→ 建模型选货 → 把结果写成 JSON → 再读回来。所有文件都写在一个临时目录里，跑完就删。
运行：python3 python/tutorial/run.py 17
"""
import csv
import json
import pathlib
import tempfile

from check import lesson, eq, near, raises, that, done
from minicplex import LinExpr, Model, ObjSense, VarType, solve

PRODUCTS = [
    {"name": "保温杯", "weight": 2, "profit": 30},
    {"name": "茶叶", "weight": 1, "profit": 25},
    {"name": "台灯", "weight": 4, "profit": 50},
    {"name": "书", "weight": 3, "profit": 20},
]


def write_csv(path, rows):
    """把一串字典写成 CSV：第一行是表头（用第一个字典的键）。
    提示：open(path, "w", encoding="utf-8", newline="") 打开；csv.DictWriter(f, fieldnames=...)；writeheader()；writerows(rows)。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def read_products(path):
    """读回 CSV。csv 读出来的都是字符串，要把 weight、profit 转成 int。返回字典列表。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def plan(products, capacity):
    """选货：每种商品一个 0-1 变量，总重量 ≤ capacity，利润最大。返回 {"chosen": [名字...], "profit": 利润}。"""
    m = Model()
    take = [m.add_var(0, 1, VarType.BINARY, f"take{k}") for k in range(len(products))]
    m.add_constr(sum((p["weight"] * t for p, t in zip(products, take)), LinExpr()) <= capacity, "capacity")
    m.set_objective(sum((p["profit"] * t for p, t in zip(products, take)), LinExpr()), ObjSense.MAXIMIZE)
    r = solve(m)
    return {"chosen": [p["name"] for p, t in zip(products, take) if r.value(t) > 0.5], "profit": r.objective}


def save_json(path, data):
    """写 JSON：中文要原样写出来（ensure_ascii=False），缩进 2 格。用 pathlib：pathlib.Path(path).write_text(..., encoding="utf-8")。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def load_json(path):
    """读 JSON。文件不存在时返回 None（不要让程序崩掉）。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def round_trip():
    with tempfile.TemporaryDirectory() as d:
        folder = pathlib.Path(d)
        write_csv(folder / "products.csv", PRODUCTS)
        products = read_products(folder / "products.csv")
        result = plan(products, capacity=6)
        save_json(folder / "result.json", result)
        text = (folder / "result.json").read_text(encoding="utf-8")
        return products, result, load_json(folder / "result.json"), text, sorted(p.name for p in folder.iterdir())


lesson("第 17 课：文件和数据")
eq("CSV 写了再读回来，内容不变（数字也转回了 int）", PRODUCTS, lambda: round_trip()[0])
eq("容量 6：选保温杯和台灯（利润 80）——比“挑轻的多拿几样”（保温杯、茶叶、书，75）更好", ["保温杯", "台灯"], lambda: round_trip()[1]["chosen"])
near("利润 80", 80, lambda: round_trip()[1]["profit"])
eq("JSON 读回来和写进去的一样", True, lambda: (lambda r: r[1] == r[2])(round_trip()))
that("JSON 里的中文原样保存（不是 \\u4fdd 这种转义）", lambda: "保温杯" in round_trip()[3])
eq("目录里正好有两个文件", ["products.csv", "result.json"], lambda: round_trip()[4])
eq("读不存在的 JSON 返回 None", None, lambda: load_json("no-such-file.json"))
raises("读不存在的 CSV 会报 FileNotFoundError", FileNotFoundError, lambda: read_products("no-such-file.csv"))
done()
