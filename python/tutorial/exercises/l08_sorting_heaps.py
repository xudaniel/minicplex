"""第 8 课：排序、lambda 和堆。

分支定界要不停地从一大堆节点里取出“最好的”一个。minicplex 用 heapq（堆）存节点，
排序规则写成一个元组：(界, -深度, -序号)——界小的先出，界一样时深的先出，再一样时新的先出。
运行：python3 python/tutorial/run.py 08
"""
import heapq
from dataclasses import dataclass

from check import lesson, eq, done


@dataclass
class Node:
    name: str
    bound: float  # 界：越小越好
    depth: int    # 深度：越深越好（更快找到整数解）
    seq: int      # 第几个放进来的：越新越好


def node_key(node):
    """返回排序用的元组，让“最好的”节点排在最前面。元组按第一项比，一样再比第二项……"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def pop_order(nodes):
    """把节点都放进堆，再一个个弹出来，返回弹出的名字列表。
    heapq.heappush(heap, (node_key(n), n.name))；heapq.heappop(heap) 弹出最小的。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def rank(students):
    """students 是 [(名字, 分数), ...]。分数高的在前；分数一样时按名字排。
    sorted(..., key=lambda s: ...)：分数取负号就能从高到低。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def top_k(words, k):
    """出现次数最多的 k 个词（次数一样时按词排）。可以先用字典数次数，再排序取前 k 个。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


NODES = [Node("A", 5.0, 1, 1), Node("B", 3.0, 1, 2), Node("C", 3.0, 4, 3), Node("D", 3.0, 4, 4), Node("E", 9.0, 9, 5)]

lesson("第 8 课：排序、lambda 和堆")
eq("界小的先出", True, lambda: node_key(NODES[1]) < node_key(NODES[0]))
eq("界一样时，深的先出", True, lambda: node_key(NODES[2]) < node_key(NODES[1]))
eq("界和深度都一样时，新的先出", True, lambda: node_key(NODES[3]) < node_key(NODES[2]))
eq("堆的弹出顺序", ["D", "C", "B", "A", "E"], lambda: pop_order(NODES))
eq("成绩排名：分高的在前，同分按名字", ["Amy", "Bob", "Cara"], lambda: rank([("Bob", 90), ("Cara", 85), ("Amy", 90)]))
eq("出现最多的 2 个词", ["the", "a"], lambda: top_k("the cat and the dog and a the a".split(), 2))
done()
