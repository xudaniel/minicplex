"""第 15 课：装饰器。

@property、@staticmethod、@dataclass 都是装饰器：一个“接收函数（或类）、返回新函数（或类）”的函数。
这一课自己写几个，最后用标准库的 functools.lru_cache 体会一下“加一行就快一万倍”。
运行：python3 python/tutorial/run.py 15
"""
import functools

from check import lesson, eq, raises, that, done


def count_calls(func):
    """装饰器：记录函数被调用了几次，次数存在 wrapper.calls 里。
    用 @functools.wraps(func) 保留原函数的名字和说明。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def retry(times):
    """带参数的装饰器：函数抛出 ValueError 时自动重试，最多一共试 times 次；还是失败就把最后那个异常抛出去。
    结构是三层：retry(times) 返回装饰器 deco(func)，deco 返回 wrapper(*args, **kwargs)。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def memoize(func):
    """自己写一个缓存装饰器：同样的参数只算一次，结果存在字典 cache 里（键是 args 元组）。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def make_greet():
    """用 @count_calls 装饰一个函数（放在函数里，是为了你还没写完 count_calls 时，这个文件也能运行）。"""
    @count_calls
    def greet(name):
        """打招呼。"""
        return f"你好，{name}"
    return greet


def call_three_times():
    greet = make_greet()
    greet("a"), greet("b"), greet("c")
    return greet.calls


def make_flaky(fail_times):
    """造一个前 fail_times 次都失败的函数，用来测试 retry。"""
    state = {"n": 0}

    def flaky():
        state["n"] += 1
        if state["n"] <= fail_times:
            raise ValueError("网络抖了一下")
        return "成功"
    return flaky


def fib_calls(decorator):
    """用给定的装饰器包装递归的斐波那契，算 fib(25)，返回 (结果, 真正执行函数体的次数)。"""
    body_runs = [0]

    @decorator
    def fib(n):
        body_runs[0] += 1
        return n if n < 2 else fib(n - 1) + fib(n - 2)
    return fib(25), body_runs[0]


lesson("第 15 课：装饰器")
eq("被装饰的函数照常工作", "你好，小明", lambda: make_greet()("小明"))
eq("调用了 3 次，calls 就是 3", 3, call_three_times)
eq("functools.wraps 保留了名字", "greet", lambda: make_greet().__name__)
eq("functools.wraps 保留了说明", "打招呼。", lambda: make_greet().__doc__)
eq("失败 2 次、最多试 3 次：成功", "成功", lambda: retry(3)(make_flaky(2))())
raises("失败 3 次、最多试 3 次：把异常抛出去", ValueError, lambda: retry(3)(make_flaky(3))())
eq("不加缓存：fib(25) 的函数体执行了 242785 次", (75025, 242785), lambda: fib_calls(lambda f: f))
eq("加上自己写的 memoize：只执行 26 次", (75025, 26), lambda: fib_calls(memoize))
eq("标准库的 functools.lru_cache 也是 26 次", (75025, 26), lambda: fib_calls(functools.lru_cache(maxsize=None)))
done()
