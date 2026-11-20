# 入门 A1：让程序说话

> **这一课学：** 一个 Python 程序长什么样；打印一行字；字符串、`+` 拼接和 f-string；注释
> **大约：** 10 分钟 · **练习：** `python3 python/tutorial/run.py A01`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#a01)

[目录](../README.md) · 下一课：[变量和计算 →](a2-variables.md)

## 1. 最小的 Python 程序

新建一个文件 `hello.py`，只写一行：

```python
print("Hello, Python!")
```

在命令行运行 `python3 hello.py`（Windows 上可能是 `python hello.py` 或 `py hello.py`），屏幕上就出现 `Hello, Python!`。

记住三件事就够了：

- 程序从文件第一行开始，一行一行往下执行。
- `print(...)` 打印一行字。
- Python 不用分号，也不用大括号；一行就是一句话。

## 2. 字符串：用引号包起来的文字

```python
print("你好")                  # 你好
print("你好，" + "小明")        # 你好，小明     ← + 把两段文字接起来
print("苹果：" + 2 + " 元")     # ✗ 报错：TypeError，文字和数字不能直接 +
print(f"苹果：{2} 元")          # 苹果：2 元     ← f-string：在引号前加 f，{} 里放任何值
```

`#` 后面是**注释**，写给人看的，程序会跳过它。

最后一种写法叫 **f-string**，是 Python 里最常用的拼接方式：`f"{名字}今年{年龄}岁"`，大括号里的东西会被换成它的值。

## 3. 返回一个值

练习里的代码不是直接打印，而是把结果“交回去”（`return`），这样检查程序才能比对你的答案：

```python
def greet(name):
    return "你好，" + name + "！"
```

`def` 开头的是**函数**（A5 再细讲）。注意第二行前面的 4 个空格：Python 靠**缩进**知道哪几行属于这个函数。
调用 `greet("小明")`，得到的就是 `"你好，小明！"`。`name` 是从外面传进来的名字。

## 4. 常见错误

- **缩进不对**：`IndentationError`。函数里面的每一行都要比 `def` 多缩进 4 个空格，而且要对齐。
- **中文标点**：`（` `“` `：` 是中文符号，Python 不认。代码里的符号都要用英文输入法打，引号里面的文字可以是中文。
- **大小写**：`Print("hi")` 不对，必须是 `print`。

## 5. 动手

打开 [`exercises/a01_hello.py`](../exercises/a01_hello.py)。每个函数里有一行：

```python
raise NotImplementedError("TODO")  # ← 在这里写你的代码
```

它的意思是“这里还没写”。把这一行**删掉**，换成你的代码（注意保持缩进），然后运行：

```bash
python3 python/tutorial/run.py A01
```

✅ 是对了，❌ 是不对（会告诉你期望什么、实际得到什么），⏳ 是还没写。

## 6. 想一想

`"1" + "2"` 和 `1 + 2` 分别是什么？`"1" + 2` 呢？

<details><summary>答案</summary>

`"1" + "2"` 是字符串 `"12"`（两段文字接起来）；`1 + 2` 是数字 `3`；`"1" + 2` 会报 `TypeError`：Python 不会自动把数字变成文字，要写成 `"1" + str(2)` 或 `f"1{2}"`。

</details>

[目录](../README.md) · 下一课：[变量和计算 →](a2-variables.md)
