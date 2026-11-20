# Lesson 18: Command-line programs, modules and packaging

> **You learn:** `sys.argv` and `argparse`; `if __name__ == "__main__"`; `python -m` and `__main__.py`; `pyproject.toml`; `pip install`; virtual environments
> **Code used:** [`__main__.py`](../../../minicplex/__main__.py), [`bench.py`](../../../minicplex/bench.py), [`pyproject.toml`](../../../pyproject.toml), the `argparse` in [`make_web.py`](../../make_web.py)
> **Exercise:** `python3 python/tutorial/en/run.py 18`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l18)

[← Files and data](17-files-data.md) · [Contents](../README.md) · Next: [How do we know it's optimal? →](19-optimality.md)

## 1. Command-line arguments

When you run `python3 -m minicplex model.lp --gap 0.01 --quiet`, the program finds these arguments in `sys.argv`:
`["…/__main__.py", "model.lp", "--gap", "0.01", "--quiet"]`. To match the C++ version line by line, minicplex's command line parses them one at a time in a hand-written `while` loop ([`__main__.py`](../../../minicplex/__main__.py)).
For a new program of your own, the standard library's `argparse` is far less work ([`make_web.py`](../../make_web.py) uses it):

```python
p = argparse.ArgumentParser(prog="mini", description="a mini minicplex command line")
p.add_argument("model", help="LP file")                              # positional: required
p.add_argument("--gap", type=float, default=1e-6, help="relative gap")    # converted to float for you
p.add_argument("--quiet", action="store_true")                       # a switch: True if given
p.add_argument("--branch", choices=["pc", "frac"], default="pc")    # only these values allowed
args = p.parse_args()            # with no argument it reads sys.argv[1:]
args.gap, args.quiet
```

`argparse` also gives you for free: an automatically generated `--help`; and on a bad argument, it prints the usage and exits with code 2 (which is why the exercise checks for `SystemExit`).

Keep "parsing arguments" separate from "doing the work" (`build_parser` / `to_params` / `main(argv)` in the exercise), and have `main` take a list of arguments rather than read `sys.argv` itself; then tests can call `main(["m.lp", "--quiet"])` directly.

## 2. if __name__ == "__main__"

```python
def main(argv=None): ...

if __name__ == "__main__":
    main()
```

When a file is run directly, `__name__` is `"__main__"`; when someone `import`s it, `__name__` is the module name.
This line lets one file work both as a program and as a module that other code can import without it running by itself.

## 3. python -m and __main__.py

`python3 -m minicplex` means: find the package `minicplex` on the search path and run its `__main__.py`.
`python3 -m minicplex.bench` runs `minicplex/bench.py`. The benefit: you don't need to know where the file is; if the package can be imported, it can be run. The standard library works the same way: `python3 -m http.server`, `python3 -m unittest`.

## 4. Packaging: pyproject.toml

For others to `pip install` your code, you need a [`pyproject.toml`](../../../pyproject.toml). minicplex's is only a dozen lines or so:

```toml
[project]
name = "minicplex"
version = "1.0"
requires-python = ">=3.9"
dependencies = []

[project.scripts]
minicplex-py = "minicplex.__main__:main"     # installing adds a command called minicplex-py
```

`pip install ./python` installs the `minicplex` package into the current Python environment; after that `import minicplex` works from any folder, and `minicplex-py model.lp` runs directly.

## 5. Virtual environments: a clean Python for each project

Different projects may need different versions of the same library. Installing everything into the system Python leads to conflicts sooner or later. The usual habit is a **virtual environment** per project:

```bash
python3 -m venv .venv            # create a separate Python environment in the project
source .venv/bin/activate        # turn it on on macOS / Linux (Windows: .venv\Scripts\activate)
pip install ./python             # installs into this environment only
deactivate                       # turn it off when done
```

Don't commit the `.venv` folder to Git (put it in `.gitignore`). This course and minicplex use only the standard library, so it was never needed; but the moment you start using third-party libraries (`numpy`, `pandas`, ...), creating a virtual environment comes first.

## 6. Your turn

Open [`exercises/l18_cli_packaging.py`](../exercises/l18_cli_packaging.py): parse arguments with `argparse`, turn them into `Params`, and write a `main(argv)` that tests can call. Run `python3 python/tutorial/en/run.py 18`.

## 7. What next

The engineering skills are now complete: reading errors, debugging, writing tests, handling files, building command-line tools, packaging. One lesson is left ([lesson 19](19-optimality.md)): why a solver is entitled to say "this is optimal". After that, a few ways to keep going:

- Turn lesson 12's course planner into a real command-line tool: `python3 -m planner courses.csv --max-hours 20`, writing the result as JSON.
- Read the minicplex source. Suggested order: [`model.py`](../../../minicplex/model.py) → [`lp_reader.py`](../../../minicplex/lp_reader.py) → [`solver.py`](../../../minicplex/solver.py) → [`lp_engine.py`](../../../minicplex/lp_engine.py).
  The main README's [Code tour](../../../../README.en.md#code-tour) walks through the algorithms section by section.
- Send minicplex a pull request: for example, a new piece of syntax for the LP reader, with tests to go with it (the process is in [CONTRIBUTING.md](../../../../CONTRIBUTING.md)).
- Want a second language? The same solver also has a [Java version with a 20-lesson Java course](../../../../java/tutorial/README.md) (in Chinese).

[← Files and data](17-files-data.md) · [Contents](../README.md) · Next: [How do we know it's optimal? →](19-optimality.md)
