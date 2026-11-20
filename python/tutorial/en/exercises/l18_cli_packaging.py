"""Lesson 18: Command-line programs, modules and packaging.

How does python -m minicplex model.lp --gap 0.01 --quiet work? You build a mini command line with the standard argparse:
parse the arguments, read the model, solve, report. The lesson text also covers __main__, pyproject.toml, pip and virtual environments.
Run: python3 python/tutorial/en/run.py 18
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
    """The command-line arguments:
    - model: positional, the path of the LP file
    - --gap: a float, default 1e-6
    - --quiet: a switch (True when given)
    - --branch: only "pc" or "frac", default "pc"
    - --nodes: an int, default 10000000
    Hint: p = argparse.ArgumentParser(prog="mini"); p.add_argument("--gap", type=float, default=1e-6);
          a switch uses action="store_true"; allowed values use choices=[...]."""
    raise NotImplementedError("TODO")  # ← write your code here


def to_params(args):
    """Turn the parsed arguments into minicplex Params: mip_gap, verbose (True unless quiet), branching, node_limit."""
    raise NotImplementedError("TODO")  # ← write your code here


def main(argv):
    """The whole program: parse argv (the arguments without the program name), read the model, solve, return one line:
    "Optimal 20" (status and objective, as f"{r.status} {r.objective:g}")."""
    raise NotImplementedError("TODO")  # ← write your code here


BAKERY = "Maximize\n profit: 5 cake + 4 bread\nSubject To\n flour: 6 cake + 4 bread <= 24\n labor: cake + 2 bread <= 6\nGeneral\n cake bread\nEnd\n"


def parse_quietly(argv):
    """Parse the arguments but swallow the usage text argparse prints to stderr (it would clutter the grading output)."""
    with contextlib.redirect_stderr(io.StringIO()):
        return build_parser().parse_args(argv)


def run_main(*argv):
    with tempfile.TemporaryDirectory() as d:
        path = pathlib.Path(d) / "bakery.lp"
        path.write_text(BAKERY, encoding="utf-8")
        return main([str(path), *argv])


lesson("Lesson 18: Command-line programs, modules and packaging")
eq("defaults", (1e-6, False, "pc"), lambda: (lambda a: (a.gap, a.quiet, a.branch))(build_parser().parse_args(["m.lp"])))
eq("with --quiet --gap 0.01 --branch frac", (0.01, True, "frac"),
   lambda: (lambda a: (a.gap, a.quiet, a.branch))(build_parser().parse_args(["m.lp", "--quiet", "--gap", "0.01", "--branch", "frac"])))
eq("--nodes became an int", 500, lambda: build_parser().parse_args(["m.lp", "--nodes", "500"]).nodes)
raises("an unknown --branch value: argparse exits with an error (SystemExit)", SystemExit, lambda: parse_quietly(["m.lp", "--branch", "xyz"]))
raises("no model file: also exits with an error", SystemExit, lambda: parse_quietly([]))
that("to_params: quiet turns off the log, frac means most-fractional branching", lambda: (lambda p: p.verbose is False and
     p.branching is Branching.MOST_FRACTIONAL and p.mip_gap == 0.01)(to_params(build_parser().parse_args(["m.lp", "--quiet", "--gap", "0.01", "--branch", "frac"]))))
eq("full run: the bakery model", "Optimal 20", lambda: run_main("--quiet"))
eq("another branching rule, same answer", "Optimal 20", lambda: run_main("--quiet", "--branch", "frac"))
done()
