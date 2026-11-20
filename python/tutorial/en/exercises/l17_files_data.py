"""Lesson 17: Files and data: pathlib, CSV, JSON.

Real data usually lives in files: a CSV table, a JSON config. This lesson runs a small complete pipeline:
read a CSV (products) -> pick goods with a model -> write the result as JSON -> read it back. Everything goes in a temporary folder
that is deleted afterwards.
Run: python3 python/tutorial/en/run.py 17
"""
import csv
import json
import pathlib
import tempfile

from check import lesson, eq, near, raises, that, done
from minicplex import LinExpr, Model, ObjSense, VarType, solve

PRODUCTS = [
    {"name": "thermos ☕", "weight": 2, "profit": 30},
    {"name": "tea", "weight": 1, "profit": 25},
    {"name": "lamp", "weight": 4, "profit": 50},
    {"name": "book", "weight": 3, "profit": 20},
]


def write_csv(path, rows):
    """Write a list of dicts as CSV; the first row is the header (the first dict's keys).
    Hint: open(path, "w", encoding="utf-8", newline=""); csv.DictWriter(f, fieldnames=...); writeheader(); writerows(rows)."""
    raise NotImplementedError("TODO")  # ← write your code here


def read_products(path):
    """Read the CSV back. csv gives you strings only, so convert weight and profit to int. Return a list of dicts."""
    raise NotImplementedError("TODO")  # ← write your code here


def plan(products, capacity):
    """Pick goods: one 0-1 variable per product, total weight <= capacity, maximum profit. Return {"chosen": [names...], "profit": profit}."""
    m = Model()
    take = [m.add_var(0, 1, VarType.BINARY, f"take{k}") for k in range(len(products))]
    m.add_constr(sum((p["weight"] * t for p, t in zip(products, take)), LinExpr()) <= capacity, "capacity")
    m.set_objective(sum((p["profit"] * t for p, t in zip(products, take)), LinExpr()), ObjSense.MAXIMIZE)
    r = solve(m)
    return {"chosen": [p["name"] for p, t in zip(products, take) if r.value(t) > 0.5], "profit": r.objective}


def save_json(path, data):
    """Write JSON keeping non-ASCII text as is (ensure_ascii=False), indented by 2. Use pathlib: pathlib.Path(path).write_text(..., encoding="utf-8")."""
    raise NotImplementedError("TODO")  # ← write your code here


def load_json(path):
    """Read JSON. Return None if the file does not exist (do not crash)."""
    raise NotImplementedError("TODO")  # ← write your code here


def round_trip():
    with tempfile.TemporaryDirectory() as d:
        folder = pathlib.Path(d)
        write_csv(folder / "products.csv", PRODUCTS)
        products = read_products(folder / "products.csv")
        result = plan(products, capacity=6)
        save_json(folder / "result.json", result)
        text = (folder / "result.json").read_text(encoding="utf-8")
        return products, result, load_json(folder / "result.json"), text, sorted(p.name for p in folder.iterdir())


lesson("Lesson 17: Files and data")
eq("write the CSV and read it back unchanged (numbers back as int)", PRODUCTS, lambda: round_trip()[0])
eq("capacity 6: thermos and lamp (profit 80) beat taking the light things (thermos, tea, book: 75)", ["thermos ☕", "lamp"], lambda: round_trip()[1]["chosen"])
near("profit 80", 80, lambda: round_trip()[1]["profit"])
eq("the JSON reads back as written", True, lambda: (lambda r: r[1] == r[2])(round_trip()))
that("non-ASCII text is kept as is in the JSON (not escaped like \\u2615)", lambda: "☕" in round_trip()[3])
eq("exactly two files in the folder", ["products.csv", "result.json"], lambda: round_trip()[4])
eq("reading a missing JSON returns None", None, lambda: load_json("no-such-file.json"))
raises("reading a missing CSV raises FileNotFoundError", FileNotFoundError, lambda: read_products("no-such-file.csv"))
done()
