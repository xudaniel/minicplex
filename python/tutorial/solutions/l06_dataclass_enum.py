"""第 6 课：dataclass 和 enum。

minicplex 的 Params、Result 是 dataclass（自动生成 __init__、__repr__、__eq__），Status 是 enum。
这一课各写一个，顺便踩一下“可变默认值”那个著名的坑。
运行：python3 python/tutorial/run.py 06
"""
import dataclasses
import math
from dataclasses import dataclass, field
from enum import Enum

from check import lesson, eq, near, raises, that, done


class Weather(Enum):
    """天气。每个成员的值是中文名。"""
    SUNNY = "晴"
    CLOUDY = "多云"
    RAINY = "雨"

    def __str__(self):
        """str(Weather.RAINY) 返回 "雨"（就像 str(Status.OPTIMAL) 返回 "Optimal"）。"""
        # >>>
        return self.value
        # <<<

    def need_umbrella(self):
        """下雨才要带伞。enum 成员用 is 比较。"""
        # >>>
        return self is Weather.RAINY
        # <<<


@dataclass(frozen=True)
class Point:
    """平面上的点。frozen=True：造出来以后不能改，所以能放进 set、当 dict 的键。"""
    x: float
    y: float

    def distance_to(self, other):
        """两点之间的直线距离。math.hypot(dx, dy) = √(dx² + dy²)。"""
        # >>>
        return math.hypot(self.x - other.x, self.y - other.y)
        # <<<


@dataclass
class Cart:
    """购物车。items 是 [(商品名, 价格), ...]。"""
    owner: str
    # 注意：下一行如果写成 items: list = []，dataclass 会直接报错——那样所有购物车会共用同一个列表。
    #       field(default_factory=list) 的意思是：每造一个购物车，就调用 list() 新建一个空列表。
    items: list = field(default_factory=list)

    def add(self, name, price):
        # >>>
        self.items.append((name, price))
        # <<<

    def total(self):
        # >>>
        return sum(price for _, price in self.items)
        # <<<


def two_carts():
    a, b = Cart("小明"), Cart("小红")
    a.add("书", 30)
    return len(a.items), len(b.items)


def change_frozen_point():
    p = Point(1, 2)
    p.x = 5


lesson("第 6 课：dataclass 和 enum")
eq('str(Weather.RAINY) 是 "雨"', "雨", lambda: str(Weather.RAINY))
eq("下雨要带伞", True, lambda: Weather.RAINY.need_umbrella())
eq("晴天不用", False, lambda: Weather.SUNNY.need_umbrella())
eq('按值找成员：Weather("多云")', Weather.CLOUDY, lambda: Weather("多云"))
near("(0,0) 到 (3,4) 的距离是 5", 5, lambda: Point(0, 0).distance_to(Point(3, 4)))
that("dataclass 自动生成 ==：Point(1, 2) == Point(1, 2)", lambda: Point(1, 2) == Point(1, 2))
eq("frozen 的点能放进 set（重复的只算一个）", 2, lambda: len({Point(1, 2), Point(1, 2), Point(0, 0)}))
raises("frozen 的点不能改", dataclasses.FrozenInstanceError, change_frozen_point)
eq("两个购物车不共用列表", (1, 0), two_carts)
eq("总价", 42, lambda: (lambda c: (c.add("笔", 12), c.add("书", 30), c.total())[-1])(Cart("小明")))
done()
