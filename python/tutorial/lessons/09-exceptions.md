# 第 9 课：异常

> **这一课学：** `raise`；自定义异常类；`try / except / else / finally`；`raise … from None`；`with` 自动关文件；什么时候该抛、什么时候该接
> **用到的代码：** [`lp_reader.py`](../../minicplex/lp_reader.py) 的 `LpParseError` 和 `read_file`、[`__main__.py`](../../minicplex/__main__.py) 的 `run`、[`model.py`](../../minicplex/model.py) 的 `add_var`
> **练习：** `python3 python/tutorial/run.py 09`

[← 排序、lambda 和堆](08-sorting-heaps.md) · [目录](../README.md) · 下一课：[字符串和文本处理 →](10-text.md)

## 1. 出错了就 raise

```python
if name in self._index:
    raise ValueError(f"duplicate variable name: {name}")   # model.py：变量名重复
```

函数发现自己没法正确完成任务时，就**抛出异常**：立即停下，把错误一层层往上交，直到有人接住；没人接住，程序就停下来打印 Traceback。
这比返回一个“特殊值”（比如 `-1`）好：调用的人不可能忘了检查。

## 2. 自己定义异常类

```python
class LpParseError(ValueError):
    """LP 文件格式错误。"""
```

继承 `ValueError` 有两个好处：想精确处理的人可以 `except LpParseError`；只想“输入有问题就算了”的人 `except ValueError` 也能接住。
错误信息要带上**行号**，用户才找得到错在哪：

```python
def fail(self, msg):
    raise LpParseError(f"LP parse error (line {self.peek().line}): {msg}")
```

## 3. 接住它：try / except

命令行程序在最外层接住所有“预料之中”的错误，打印一行人能看懂的话（[`__main__.py`](../../minicplex/__main__.py)）：

```python
try:
    M = read_file(path)
    ...
except (ValueError, OSError) as e:
    print(f"error: {e}", file=sys.stderr)
    return 2
```

完整的形式：

```python
try:
    x = float(text)          # 可能出错的代码
except ValueError:
    ...                      # 出错时
else:
    ...                      # 没出错时
finally:
    ...                      # 不管怎样都执行：关文件、删临时文件
```

**只接你知道怎么处理的异常。** `except Exception:` 一把全接，会把真正的 bug 也藏起来。

## 4. raise … from None

```python
def read_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        raise LpParseError(f"cannot open file: {path}") from None
    return read_string(text)
```

在 `except` 里再 `raise` 一个新异常，Python 默认会把两个都打印出来（“During handling of the above exception, another exception occurred”）。
`from None` 的意思是：原来那个是内部细节，用户只需要看新的这个。

## 5. with：用完自动收拾

`with open(...) as f:` 保证离开这一段时文件一定被关上，哪怕中间出了异常。它等于一个写好的 `try / finally`。
读写文件时总是带上 `encoding="utf-8"`：不写的话，Windows 上默认编码不是 UTF-8，中文会乱码。

## 6. 动手

打开 [`exercises/l09_exceptions.py`](../exercises/l09_exceptions.py)：解析金额（错了抛 `ValueError`）、安全除法、用 minicplex 读 LP 文件并分出三种结果、`try / finally` 删临时文件。运行 `python3 python/tutorial/run.py 09`。

## 7. 想一想

`parse_amount` 失败时，应该返回 `None` 还是抛异常？

<details><summary>答案</summary>

看调用的人能不能、该不该处理。“用户输入的金额格式不对”是调用的人必须知道的事，抛异常不会被忽略；
返回 `None` 的话，后面的 `None * 2` 会在离真正错误很远的地方报一个莫名其妙的 `TypeError`。
`safe_ratio` 返回 `None` 是因为它的名字和说明已经约定了“除以 0 时给 None”——这是调用的人主动选择的。

</details>

[← 排序、lambda 和堆](08-sorting-heaps.md) · [目录](../README.md) · 下一课：[字符串和文本处理 →](10-text.md)
