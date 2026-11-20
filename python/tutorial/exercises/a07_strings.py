"""入门 A7：字符串。

运行：python3 python/tutorial/run.py A07
"""
from check import lesson, eq, done


def initials(full_name):
    """英文名缩写：initials("ada lovelace") 返回 "AL"。
    full_name.split() 按空格切成几个词；word[0] 是第一个字母；.upper() 变大写。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def has_digit(password):
    """密码里有没有数字？一个个字符看，ch.isdigit() 判断是不是数字。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def reverse(s):
    """把字符串倒过来。切片 s[::-1] 一步就能做到。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def mask_phone(phone):
    """手机号打码：mask_phone("13812345678") 返回 "138****5678"。
    用切片：phone[:3] 是前 3 位，phone[-4:] 是后 4 位。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


lesson("入门 A7：字符串")
eq('initials("ada lovelace") 是 "AL"', "AL", lambda: initials("ada lovelace"))
eq('initials("Guido van Rossum") 是 "GVR"', "GVR", lambda: initials("Guido van Rossum"))
eq('"abc123" 里有数字', True, lambda: has_digit("abc123"))
eq('"password" 里没有数字', False, lambda: has_digit("password"))
eq('reverse("上海自来水") 是 "水来自海上"', "水来自海上", lambda: reverse("上海自来水"))
eq('mask_phone("13812345678")', "138****5678", lambda: mask_phone("13812345678"))
done()
