"""入门 A1：让程序说话。

只需要改每个函数里 TODO 下面的那一行。“函数”是什么，A5 再讲。
运行：python3 python/tutorial/run.py A01
"""
from check import lesson, eq, done


def hello():
    """返回一句固定的话：Hello, Python!"""
    # TODO 把下面这一行换成：return "Hello, Python!"
    # >>>
    return "Hello, Python!"
    # <<<


def greet(name):
    """跟人打招呼：greet("小明") 返回 "你好，小明！" """
    # TODO 用 + 把三段拼起来："你好，" + name + "！"
    # >>>
    return "你好，" + name + "！"
    # <<<


def price(item, yuan):
    """报价：price("苹果", 2) 返回 "苹果：2 元"。数字要先放进 f-string 里才能和文字拼在一起。"""
    # TODO 用 f-string：f"{item}：{yuan} 元"
    # >>>
    return f"{item}：{yuan} 元"
    # <<<


lesson("入门 A1：让程序说话")
print("（这一行是程序自己打印的：Python 从上往下一行一行执行）")
eq("hello() 返回 Hello, Python!", "Hello, Python!", lambda: hello())
eq('greet("小明")', "你好，小明！", lambda: greet("小明"))
eq('greet("Mia")', "你好，Mia！", lambda: greet("Mia"))
eq('price("苹果", 2)', "苹果：2 元", lambda: price("苹果", 2))
eq('price("香蕉", 1)', "香蕉：1 元", lambda: price("香蕉", 1))
done()
