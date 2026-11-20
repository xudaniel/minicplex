"""第 4 课：类和对象。

minicplex 的 VarInfo、Model 都是类。这一课自己写一个商品类：属性、方法、默认参数、@property、__repr__。
运行：python3 python/tutorial/run.py 04
"""
from check import lesson, eq, near, that, done


class Product:
    """一种商品：名字、单价、库存。"""

    def __init__(self, name, price, stock=0):
        """stock 不写时默认 0。把三个参数存成同名属性：self.name、self.price、self.stock。"""
        raise NotImplementedError("TODO")  # ← 在这里写你的代码

    def total_value(self):
        """库存总价值 = 单价 × 库存。"""
        raise NotImplementedError("TODO")  # ← 在这里写你的代码

    def sell(self, n):
        """卖出 n 件：库存够就减掉并返回 True；不够就什么都不改，返回 False。"""
        raise NotImplementedError("TODO")  # ← 在这里写你的代码

    @property
    def in_stock(self):
        """有没有货。@property 让它用起来像属性：p.in_stock（不加括号）。"""
        raise NotImplementedError("TODO")  # ← 在这里写你的代码

    def __repr__(self):
        """打印对象时显示的样子：Product('苹果', 2.5, stock=10)。提示：{self.name!r} 会带上引号。"""
        raise NotImplementedError("TODO")  # ← 在这里写你的代码


def sold_out_after():
    p = Product("酸奶", 6, 3)
    ok1, ok2, ok3 = p.sell(2), p.sell(2), p.sell(1)
    return (ok1, ok2, ok3, p.stock, p.in_stock)


lesson("第 4 课：类和对象")
eq("名字", "苹果", lambda: Product("苹果", 2.5, 10).name)
eq("不写库存时默认 0", 0, lambda: Product("梨", 3).stock)
near("库存总价值 2.5 × 10 = 25", 25, lambda: Product("苹果", 2.5, 10).total_value())
eq("卖 2、再卖 2（不够了）、再卖 1：(True, False, True, 0, False)", (True, False, True, 0, False), sold_out_after)
that("有货时 in_stock 是 True", lambda: Product("苹果", 2.5, 1).in_stock is True)
eq("repr", "Product('苹果', 2.5, stock=10)", lambda: repr(Product("苹果", 2.5, 10)))
that("两个对象各有各的库存", lambda: (lambda a, b: (a.sell(1), a.stock, b.stock))(Product("a", 1, 5), Product("b", 1, 5))[1:] == (4, 5))
done()
