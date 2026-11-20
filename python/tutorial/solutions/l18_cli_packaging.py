"""第 18 课：命令行程序、模块和打包。

python -m minicplex model.lp --gap 0.01 --quiet 是怎么工作的？这一课用标准库的 argparse 写一个迷你版的命令行：
解析参数、读模型、求解、打印结果。课文里还会讲 __main__、pyproject.toml、pip 和虚拟环境。
运行：python3 python/tutorial/run.py 18
"""
import argparse
import contextlib
import io
import pathlib
import tempfile

from check import lesson, eq, near, raises, that, done
from minicplex import Params, read_file, solve
from minicplex.solver import Branching


def build_parser():
    """命令行参数：
    - model：位置参数，LP 文件路径
    - --gap：浮点数，默认 1e-6
    - --quiet：开关（写了就是 True）
    - --branch：只能是 "pc" 或 "frac"，默认 "pc"
    - --nodes：整数，默认 10000000
    提示：p = argparse.ArgumentParser(prog="mini")；p.add_argument("--gap", type=float, default=1e-6)；
         开关用 action="store_true"；限定取值用 choices=[...]。"""
    # >>>
    p = argparse.ArgumentParser(prog="mini", description="minicplex 的迷你命令行")
    p.add_argument("model", help="LP 文件")
    p.add_argument("--gap", type=float, default=1e-6, help="相对间隙")
    p.add_argument("--quiet", action="store_true", help="不打印节点日志")
    p.add_argument("--branch", choices=["pc", "frac"], default="pc", help="分支规则")
    p.add_argument("--nodes", type=int, default=10_000_000, help="节点上限")
    return p
    # <<<


def to_params(args):
    """把解析结果变成 minicplex 的 Params：mip_gap、verbose（不 quiet 就是 True）、branching、node_limit。"""
    # >>>
    return Params(mip_gap=args.gap, verbose=not args.quiet,
                  branching=Branching.MOST_FRACTIONAL if args.branch == "frac" else Branching.PSEUDO_COST,
                  node_limit=args.nodes)
    # <<<


def main(argv):
    """完整的程序：解析 argv（不含程序名的那串参数），读模型、求解，返回一行结果：
    "Optimal 20"（状态 + 目标值，用 f"{r.status} {r.objective:g}"）。"""
    # >>>
    args = build_parser().parse_args(argv)
    r = solve(read_file(args.model), to_params(args))
    return f"{r.status} {r.objective:g}"
    # <<<


BAKERY = "Maximize\n profit: 5 cake + 4 bread\nSubject To\n flour: 6 cake + 4 bread <= 24\n labor: cake + 2 bread <= 6\nGeneral\n cake bread\nEnd\n"


def parse_quietly(argv):
    """解析参数，但把 argparse 打印到 stderr 的用法说明收起来（不然判分输出里会多几行）。"""
    with contextlib.redirect_stderr(io.StringIO()):
        return build_parser().parse_args(argv)


def run_main(*argv):
    with tempfile.TemporaryDirectory() as d:
        path = pathlib.Path(d) / "bakery.lp"
        path.write_text(BAKERY, encoding="utf-8")
        return main([str(path), *argv])


lesson("第 18 课：命令行程序、模块和打包")
eq("默认值", (1e-6, False, "pc"), lambda: (lambda a: (a.gap, a.quiet, a.branch))(build_parser().parse_args(["m.lp"])))
eq("写了 --quiet --gap 0.01 --branch frac", (0.01, True, "frac"),
   lambda: (lambda a: (a.gap, a.quiet, a.branch))(build_parser().parse_args(["m.lp", "--quiet", "--gap", "0.01", "--branch", "frac"])))
eq("--nodes 转成了整数", 500, lambda: build_parser().parse_args(["m.lp", "--nodes", "500"]).nodes)
raises("--branch 写了不认识的值：argparse 报错退出（SystemExit）", SystemExit, lambda: parse_quietly(["m.lp", "--branch", "xyz"]))
raises("少了模型文件：也报错退出", SystemExit, lambda: parse_quietly([]))
that("to_params：quiet 时不打印日志，frac 对应最接近 .5 的分支规则", lambda: (lambda p: p.verbose is False and
     p.branching is Branching.MOST_FRACTIONAL and p.mip_gap == 0.01)(to_params(build_parser().parse_args(["m.lp", "--quiet", "--gap", "0.01", "--branch", "frac"]))))
eq("完整运行：面包店模型", "Optimal 20", lambda: run_main("--quiet"))
eq("换一种分支规则，答案一样", "Optimal 20", lambda: run_main("--quiet", "--branch", "frac"))
done()
