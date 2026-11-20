# 第 13 课：读懂报错、调试和 assert

> **这一课学：** 从下往上读 Traceback；常见的几种异常各说明什么；用 print 和 breakpoint() 找 bug；用 assert 给代码加“自检”
> **用到的代码：** [`solver.py`](../../minicplex/solver.py) 里的 `assert` 和 `check_feasible`、[`__main__.py`](../../minicplex/__main__.py) 的报错方式
> **练习：** `python3 python/tutorial/run.py 13`（这一课的练习是“找 bug”：代码已经写好了，但有错）
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l13)

[← 综合项目：选课助手](12-project.md) · [目录](../README.md) · 下一课：[函数进阶 →](14-functions.md)

## 1. Traceback：从下往上读

程序出错时，Python 打印一段 **Traceback**（调用栈）。新手常被吓到，其实它是最好的线索：

```text
Traceback (most recent call last):
  File "plan.py", line 12, in <module>
    print(report(load("menu.txt")))
  File "plan.py", line 8, in report
    return "合计：" + total
TypeError: can only concatenate str (not "float") to str
```

- **最后一行**最重要：错误的类型（`TypeError`）和原因（字符串不能和小数直接 `+`）。
- 往上一行是**出错的位置**：`plan.py` 第 8 行，在 `report` 函数里，原文是 `return "合计：" + total`。
- 再往上是“谁调用了它”：第 12 行调用了 `report`。一直往上，就是程序是怎么一步步走到这里的。

所以读 Traceback 的顺序是：**先看最后一行知道是什么错，再看它上面一行知道错在哪**。

## 2. 常见的几种错误

| 错误 | 通常是因为 |
|---|---|
| `SyntaxError` / `IndentationError` | 括号没配对、漏了冒号、缩进不齐、用了中文标点。程序一行都还没运行 |
| `NameError` | 名字拼错了，或者用之前没定义 |
| `TypeError` | 类型不对：文字 + 数字、参数个数不对、对 `None` 调用方法 |
| `AttributeError: 'NoneType' object has no attribute ...` | 某个函数忘了 `return`，拿到的是 `None` |
| `IndexError` / `KeyError` | 下标越界 / 字典里没有这个键 |
| `ValueError` | 类型对但值不对：`int("abc")`、`math.sqrt(-1)` |

网页版的练习出错时，会自动用中文告诉你是第几行、什么错、通常是什么原因。

## 3. 最难的 bug 不报错

上面那些至少会报错。最麻烦的是**程序正常跑完，答案却是错的**：少加了一个数、条件写反了、两个变量共用了一个列表……这一课的练习全是这种。

找这种 bug 的办法：

1. **先找一个最小的、你知道答案的例子**。`average([2, 4, 6])` 应该是 4，结果是 3.33——好，问题就在这几行里。
2. **把中间结果打印出来**：在循环里 `print(i, total)`，看看每一步的值是不是你以为的那样。
3. **用调试器一步步走**：在代码里写一行 `breakpoint()`，在自己电脑上运行时程序会停在那里，输入 `p total` 看变量、`n` 走一步、`c` 继续。VS Code、PyCharm 里点行号左边设断点也是一样的。（网页版里用不了调试器，用 print。）

## 4. 可变默认值：一个“不报错”的经典 bug

```python
def add_item(item, cart=[]):
    cart.append(item)
    return cart

add_item("书")    # ['书']
add_item("笔")    # ['书', '笔']   ← 咦？
```

默认值 `[]` 只在定义函数时创建**一次**，以后每次调用都是同一个列表。第 6 课在 dataclass 里见过它的另一个面孔。正确写法：

```python
def add_item(item, cart=None):
    if cart is None:
        cart = []
```

## 5. assert：让错误尽早暴露

```python
assert x >= 0, "x 不能是负数"
```

条件不成立时立刻抛出 `AssertionError`，带着你写的信息。它的作用是**把“我以为一定成立的事”写下来，让程序替你检查**。
错误越早暴露越好找：`math.sqrt(-1)` 报错还好，要是悄悄算出个 `nan`，可能要过很久才在别处冒出一个莫名其妙的结果。

minicplex 里也有：分支定界的主循环里有一句 `assert cur is not None`。更大的“自检”是 `check_feasible`：
求解器每找到一个整数解，都要用原始模型重新检查一遍每条约束（[`solver.py`](../../minicplex/solver.py) 的 `try_incumbent`），
不满足就扔掉。正是这道自检，曾经抓到过一个单纯形表舍入误差导致的“伪解”。

注意：`assert` 是给**程序员**看的检查，用 `python -O` 运行时会被跳过。检查用户输入（比如文件格式）要用 `if ...: raise ValueError(...)`（第 9 课）。

## 6. 动手

打开 [`exercises/l13_debugging.py`](../exercises/l13_debugging.py)。前五个函数都标着 🐞：代码能跑，但有 bug。运行一下，从 ❌ 那几行入手，一个个修好；最后一个函数用 `assert` 写。运行 `python3 python/tutorial/run.py 13`。

## 7. 想一想

`best_price` 的 bug（`min(prices)`）为什么没有报错，却返回了“梨”？

<details><summary>答案</summary>

`min` 遍历字典时拿到的是**键**（商品名），所以它比的是字符串的大小，返回了“编码最小”的名字，和价格毫无关系。
要按价格比，就告诉 `min` 用什么当比较依据：`min(prices, key=prices.get)`（第 8 课的 `key=`）。

</details>

[← 综合项目：选课助手](12-project.md) · [目录](../README.md) · 下一课：[函数进阶 →](14-functions.md)
