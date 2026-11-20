# 入门 A8：小项目——挑水果

> **这一课学：** 把前 7 节串起来：函数、判断、两层循环、元组；第一次用 minicplex 求解器
> **大约：** 20 分钟 · **练习：** `python3 python/tutorial/run.py A08`

[← 字符串](a7-strings.md) · [目录](../README.md) · 下一课：[第 1 课：第一个模型 →](01-first-model.md)

## 1. 题目

苹果 2 元一个、3 分；香蕉 1 元一根、2 分。你有 10 元，袋子最多装 7 个。怎么买，总分最高？

## 2. 拆成小函数

- `fits(a, b)`：这样买，钱够不够、袋子装不装得下？
- `score(a, b)`：这样买得几分？
- `best()`：试遍所有买法，留下最好的。

每个函数只做一件事，写完一个就能单独检查一个。这是写任何程序的好习惯。

## 3. 两层循环：试遍所有组合

```python
for a in range(6):          # 苹果 0～5 个
    for b in range(11):     # 香蕉 0～10 根
        ...                 # 一共 6 × 11 = 66 种
```

找到更好的就记下来。要同时记三个数，可以用**元组** `(a, b, 分数)`：和列表很像，但用圆括号，造出来就不能改。
`best[2]` 是元组里的第 3 个数（分数）。

## 4. 交给求解器

练习文件最后一个函数 `solver_score()` 已经写好了，把同一道题交给 minicplex：

```python
m = Model()
apple = m.add_var(0, INF, VarType.INTEGER, "apple")
banana = m.add_var(0, INF, VarType.INTEGER, "banana")
m.add_constr(2 * apple + 1 * banana <= 10, "money")
m.add_constr(apple + banana <= 7, "bag")
m.set_objective(3 * apple + 2 * banana, ObjSense.MAXIMIZE)
solve(m).objective          # 17.0
```

看，几乎就是把题目原样抄了一遍：变量、限制、目标。怎么找到答案，交给求解器。

## 5. 为什么需要求解器

66 种组合，循环一下就完了。可是如果有 30 种水果、每种最多买 10 个，组合数是 11³⁰（约 1.7 × 10³¹）——每秒试一亿种，也要试几千万亿年。
求解器不会一个个试，它用“单纯形法”和“分支定界”聪明地跳过绝大多数组合（主 README 的
[用大白话讲 minicplex](../../../README.md#用大白话讲-minicplex先看这里) 有 5 分钟的通俗解释）。

## 6. 动手

打开 [`exercises/a08_fruit_project.py`](../exercises/a08_fruit_project.py)，运行 `python3 python/tutorial/run.py A08`。

全部 ✅ 之后，恭喜：你已经会写真正的程序了。下一步进入正式课程，第 1 课就从你刚才看到的这段建模代码讲起。

## 7. 想一想

如果袋子能装无数个，钱还是 10 元，最优买法是什么？为什么？

<details><summary>答案</summary>

全买香蕉，10 根，20 分。香蕉每元钱得 2 分，苹果每元钱只得 1.5 分；袋子不限时，“每元钱的分数”才是关键。
把 `fits` 里袋子的条件去掉验证一下。

</details>

[← 字符串](a7-strings.md) · [目录](../README.md) · 下一课：[第 1 课：第一个模型 →](01-first-model.md)
