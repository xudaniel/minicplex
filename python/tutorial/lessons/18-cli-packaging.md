# 第 18 课：命令行程序、模块和打包

> **这一课学：** `sys.argv` 和 `argparse`；`if __name__ == "__main__"`；`python -m` 和 `__main__.py`；`pyproject.toml`；`pip install`；虚拟环境
> **用到的代码：** [`__main__.py`](../../minicplex/__main__.py)、[`bench.py`](../../minicplex/bench.py)、[`pyproject.toml`](../../pyproject.toml)、[`make_web.py`](../make_web.py) 的 `argparse`
> **练习：** `python3 python/tutorial/run.py 18`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l18)

[← 文件和数据](17-files-data.md) · [目录](../README.md) · 下一课：[为什么知道这是最优解 →](19-optimality.md)

## 1. 命令行参数

`python3 -m minicplex model.lp --gap 0.01 --quiet` 运行时，程序能在 `sys.argv` 里拿到这串参数：
`["…/__main__.py", "model.lp", "--gap", "0.01", "--quiet"]`。minicplex 的命令行为了和 C++ 版一行行对应，是手写的 `while` 循环逐个解析（[`__main__.py`](../../minicplex/__main__.py)）。
自己写新程序时，用标准库的 `argparse` 省事得多（[`make_web.py`](../make_web.py) 就是）：

```python
p = argparse.ArgumentParser(prog="mini", description="minicplex 的迷你命令行")
p.add_argument("model", help="LP 文件")                              # 位置参数：必须给
p.add_argument("--gap", type=float, default=1e-6, help="相对间隙")    # 自动转成 float
p.add_argument("--quiet", action="store_true")                       # 开关：写了就是 True
p.add_argument("--branch", choices=["pc", "frac"], default="pc")    # 只允许这几个值
args = p.parse_args()            # 不传参数就读 sys.argv[1:]
args.gap, args.quiet
```

`argparse` 还免费送你：`--help` 自动生成的说明；参数写错时打印用法并以退出码 2 结束（所以练习里要检查 `SystemExit`）。

把“解析参数”和“干活”分开写（练习里的 `build_parser` / `to_params` / `main(argv)`），`main` 接收参数列表而不是自己去读 `sys.argv`，就能在测试里直接调用 `main(["m.lp", "--quiet"])`。

## 2. if __name__ == "__main__"

```python
def main(argv=None): ...

if __name__ == "__main__":
    main()
```

一个文件被直接运行时，`__name__` 是 `"__main__"`；被别人 `import` 时，`__name__` 是模块名。
这一句让同一个文件既能当程序跑，又能被别的代码 import 而不会自动运行。

## 3. python -m 和 __main__.py

`python3 -m minicplex` 的意思是：在搜索路径里找到 `minicplex` 这个包，运行它的 `__main__.py`。
`python3 -m minicplex.bench` 则是运行 `minicplex/bench.py`。好处是不用关心文件在哪，只要包能 import 就能运行；标准库也这么用：`python3 -m http.server`、`python3 -m unittest`。

## 4. 打包：pyproject.toml

想让别人 `pip install` 你的代码，需要一个 [`pyproject.toml`](../../pyproject.toml)。minicplex 的只有十几行：

```toml
[project]
name = "minicplex"
version = "1.0"
requires-python = ">=3.9"
dependencies = []

[project.scripts]
minicplex-py = "minicplex.__main__:main"     # 安装后多出一个命令 minicplex-py
```

`pip install ./python` 会把 `minicplex` 包装进当前的 Python 环境，以后在任何目录都能 `import minicplex`，也能直接运行 `minicplex-py model.lp`。

## 5. 虚拟环境：每个项目一个干净的 Python

不同项目可能要不同版本的同一个库。往系统的 Python 里乱装，迟早会冲突。习惯做法是每个项目建一个**虚拟环境**：

```bash
python3 -m venv .venv            # 在项目里建一个独立的 Python 环境
source .venv/bin/activate        # macOS / Linux 启用它（Windows：.venv\Scripts\activate）
pip install ./python             # 装到这个环境里，不影响别处
deactivate                       # 用完退出
```

`.venv` 目录不要提交到 Git（写进 `.gitignore`）。这门课和 minicplex 都只用标准库，所以一直没需要它；一旦开始用第三方库（`numpy`、`pandas`……），第一件事就是建虚拟环境。

## 6. 动手

打开 [`exercises/l18_cli_packaging.py`](../exercises/l18_cli_packaging.py)：用 `argparse` 写参数解析、转成 `Params`、写一个能在测试里调用的 `main(argv)`。运行 `python3 python/tutorial/run.py 18`。

## 7. 接下来

到这里，工程上的本事已经齐了：读报错、调试、写测试、处理文件、做命令行工具、打包发布。还剩最后一课（[第 19 课](19-optimality.md)）：求解器凭什么说“这就是最优解”。之后几个继续的方向：

- 把第 12 课的选课助手改成一个真正的命令行工具：`python3 -m planner courses.csv --max-hours 20`，结果写成 JSON。
- 读 minicplex 的源代码。推荐顺序：[`model.py`](../../minicplex/model.py) → [`lp_reader.py`](../../minicplex/lp_reader.py) → [`solver.py`](../../minicplex/solver.py) → [`lp_engine.py`](../../minicplex/lp_engine.py)。
  主 README 的[代码解析](../../../README.md#代码解析)一节逐段讲了算法。
- 给 minicplex 提一个 pull request：比如给 LP 读取器加一种新的语法，记得同时加测试（流程见 [CONTRIBUTING.md](../../../CONTRIBUTING.md)）。
- 想学第二门语言？同一个求解器还有 [Java 版和 20 节 Java 课](../../../java/tutorial/README.md)。

[← 文件和数据](17-files-data.md) · [目录](../README.md) · 下一课：[为什么知道这是最优解 →](19-optimality.md)
