# 入门 A7：字符串

> **这一课学：** 下标和切片；`split`、`upper`、`isdigit`；`in`；字符串不能改
> **大约：** 20 分钟 · **练习：** `python3 python/tutorial/run.py A07`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#a07)

[← 列表](a6-lists.md) · [目录](../README.md) · 下一课：[小项目：挑水果 →](a8-project.md)

## 1. 字符串也能用下标

```python
s = "minicplex"
s[0]       # 'm'
s[-1]      # 'x'
len(s)     # 9
for ch in s:      # 一个个字符
    ...
```

Python 没有单独的“字符”类型，一个字符就是长度为 1 的字符串。中文也一样：`"你好"[0]` 是 `"你"`。

## 2. 切片：取一段

```python
phone = "13812345678"
phone[:3]      # '138'        前 3 个
phone[-4:]     # '5678'       后 4 个
phone[3:7]     # '1234'       从下标 3 到 6（不含 7）
phone[::-1]    # '87654321831' 步长 -1：倒过来
```

## 3. 常用的方法

```python
"ada lovelace".split()      # ['ada', 'lovelace']   按空白切开
"a".upper()                 # 'A'
"7".isdigit()               # True
"lp" in "minicplex"         # False                 有没有这一段
" x <= 5 ".strip()          # 'x <= 5'              去掉两边空白
"-".join(["a", "b", "c"])   # 'a-b-c'               用 - 连起来
```

字符串**不能改**：`s[0] = "M"` 会报错。所有方法都是返回一个新字符串，原来的不变。

> **minicplex 里的例子：** 读 LP 文件时，[`lp_reader.py`](../../minicplex/lp_reader.py) 就是这样一个字符一个字符地看：
> 是数字就一直读到不是数字为止，是字母就一直读到名字结束，`"<="` 这样的两个字符合起来算一个运算符。第 10 课会写一个迷你版。

## 4. 常见错误

- `s.upper` 忘了括号：得到的是“方法本身”，不是结果。
- 以为方法会改原字符串：`name.upper()` 之后 `name` 还是小写，要写 `name = name.upper()`。

## 5. 动手

打开 [`exercises/a07_strings.py`](../exercises/a07_strings.py)，运行 `python3 python/tutorial/run.py A07`。

## 6. 想一想

`"3" < "10"` 是 `True` 还是 `False`？

<details><summary>答案</summary>

`False`！字符串按字符一个个比：`"3"` 和 `"1"` 比，`"3"` 大，所以 `"3" > "10"`。要按数字比，先 `int("3") < int("10")`。
文件里读出来的都是字符串，忘了转换是很常见的 bug。

</details>

[← 列表](a6-lists.md) · [目录](../README.md) · 下一课：[小项目：挑水果 →](a8-project.md)
