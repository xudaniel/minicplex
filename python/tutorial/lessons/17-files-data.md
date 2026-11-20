# 第 17 课：文件和数据——pathlib、CSV、JSON

> **这一课学：** `pathlib.Path`；读写文本文件和编码；`csv` 模块；`json` 模块；临时文件和目录；一个“读数据 → 建模 → 写结果”的完整流程
> **用到的代码：** [`model.py`](../../minicplex/model.py) 的 `write_lp`、[`lp_reader.py`](../../minicplex/lp_reader.py) 的 `read_file`、[`tools/compare_java_cpp.py`](../../../tools/compare_java_cpp.py) 读 CSV、[`make_web.py`](../make_web.py) 写 JSON
> **练习：** `python3 python/tutorial/run.py 17`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l17)

[← 生成器和迭代器](16-generators.md) · [目录](../README.md) · 下一课：[命令行程序和打包 →](18-cli-packaging.md)

## 1. pathlib：用对象表示路径

```python
from pathlib import Path

folder = Path("data")
f = folder / "products.csv"          # 用 / 拼路径，Windows、macOS、Linux 都对
f.exists(), f.name, f.suffix         # True, 'products.csv', '.csv'
text = f.read_text(encoding="utf-8")
f.with_suffix(".json").write_text("{}", encoding="utf-8")
for p in folder.glob("*.lp"): ...    # 找出所有 .lp 文件
```

比起拼字符串 `"data" + "/" + name`，`Path` 不会把斜杠搞错，读写文件也只要一行。

## 2. 编码：永远写 encoding="utf-8"

```python
with open(path, encoding="utf-8") as f:     # lp_reader.py 的 read_file 就是这么写的
    text = f.read()
```

不写的话，Python 用操作系统的默认编码：macOS、Linux 上一般是 UTF-8，Windows 上常常不是，同一个程序换台电脑读中文就乱码或者报 `UnicodeDecodeError`。

## 3. CSV：表格数据

minicplex 的批量求解工具把结果写成 CSV，对比脚本再读回来：

```python
a = {r["model"]: r for r in csv.DictReader(open(args[0], encoding="utf-8"))}   # tools/compare_java_cpp.py
```

`csv.DictReader` 把每一行变成一个字典，键是表头。两个要点：

- 读出来的**全是字符串**，数字要自己 `int()` / `float()`。
- 打开文件时加 `newline=""`，否则 Windows 上会多出空行。

写的时候用 `csv.DictWriter(f, fieldnames=[...])`，先 `writeheader()` 再 `writerows(rows)`。为什么不自己用 `","` 拼？因为字段里本身可能有逗号、引号、换行，`csv` 模块会自动处理。

## 4. JSON：结构化数据

```python
json.dumps(course, ensure_ascii=False)          # make_web.py：网页版课程就是一个大 JSON
data = json.loads(text)
```

JSON 能存字典、列表、字符串、数字、`true`/`false`/`null`，几乎所有语言、所有网页都能读。
`ensure_ascii=False` 让中文原样写出来；不加的话会变成 `\u4fdd\u6e29\u676f` 这样的转义（也能读回来，只是人看不懂）。
`indent=2` 让输出有缩进，方便人看。

## 5. 临时文件

测试里经常需要“写个文件试试，用完删掉”：

```python
with tempfile.TemporaryDirectory() as d:
    folder = Path(d)
    ...                    # 在 folder 里随便写
# 离开 with，整个目录自动删掉
```

第 9 课手动用 `try / finally` 删临时文件；`TemporaryDirectory` 把这件事包好了。

## 6. 完整的流程

练习里要串起来：

```text
products.csv ──读──▶ [字典, …] ──plan()──▶ 选哪些货 ──写──▶ result.json ──读──▶ 核对
```

结果里有个小惊喜：容量 6 公斤时，直觉是“挑轻的，多拿几样”（保温杯、茶叶、书，利润 75），
求解器却选了保温杯和台灯（利润 80）。这正是优化模型的用处：直觉在组合问题上常常不对。

## 7. 动手

打开 [`exercises/l17_files_data.py`](../exercises/l17_files_data.py)，写 CSV 读写和 JSON 读写，运行 `python3 python/tutorial/run.py 17`。

## 8. 想一想

为什么 `read_products` 要在函数里把 `weight`、`profit` 转成 `int`，而不是让用它的人自己转？

<details><summary>答案</summary>

“数据从文件里来”是读取这一层的细节，用的人不该操心。在边界上一次转换好，后面的代码拿到的就是干净、类型正确的数据。
否则每个用到的地方都要记得转，忘一次就是第 13 课那种“不报错但答案错”的 bug（`"2" * 3` 是 `"222"`）。

</details>

[← 生成器和迭代器](16-generators.md) · [目录](../README.md) · 下一课：[命令行程序和打包 →](18-cli-packaging.md)
