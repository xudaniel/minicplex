# Basics A7: Strings

> **You learn:** indexes and slices; `split`, `upper`, `isdigit`; `in`; strings can't be changed
> **Time:** about 20 minutes · **Exercise:** `python3 python/tutorial/en/run.py A07`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#a07)

[← Lists](a6-lists.md) · [Contents](../README.md) · Next: [A small project: buying fruit →](a8-project.md)

## 1. Strings have indexes too

```python
s = "minicplex"
s[0]       # 'm'
s[-1]      # 'x'
len(s)     # 9
for ch in s:      # one character at a time
    ...
```

Python has no separate "character" type: a character is just a string of length 1. That holds for any language: `"你好"[0]` is `"你"`.

## 2. Slices: taking a piece

```python
phone = "5551234567"
phone[:3]      # '555'          the first 3
phone[-4:]     # '4567'         the last 4
phone[3:7]     # '1234'         index 3 to 6 (7 not included)
phone[::-1]    # '7654321555'   step -1: backwards
```

## 3. Handy methods

```python
"ada lovelace".split()      # ['ada', 'lovelace']   split on whitespace
"a".upper()                 # 'A'
"7".isdigit()               # True
"lp" in "minicplex"         # False                 does this piece appear?
" x <= 5 ".strip()          # 'x <= 5'              trim spaces at both ends
"-".join(["a", "b", "c"])   # 'a-b-c'               join with -
```

Strings **can't be changed**: `s[0] = "M"` is an error. Every method returns a new string and leaves the original alone.

> **In minicplex:** when reading an LP file, [`lp_reader.py`](../../../minicplex/lp_reader.py) looks at one character at a time just like this:
> a digit means keep reading until the digits stop, a letter means read to the end of the name, and two characters such as `"<="` count as one operator. Lesson 10 writes a mini version.

## 4. Common mistakes

- `s.upper` without parentheses: you get the method itself, not its result.
- Expecting a method to change the original: after `name.upper()`, `name` is still lower case; write `name = name.upper()`.

## 5. Your turn

Open [`exercises/a07_strings.py`](../exercises/a07_strings.py) and run `python3 python/tutorial/en/run.py A07`.

The last one is a **🤔 guess, then run**: don't run anything yet. Read the few lines of code in the task, write your guess after `return`, then run and see whether you were right. A wrong guess is fine; working out why is the point.

## 6. Think about it

Is `"3" < "10"` `True` or `False`?

<details><summary>Answer</summary>

`False`! Strings compare character by character: `"3"` against `"1"`, and `"3"` is larger, so `"3" > "10"`. To compare as numbers, convert first: `int("3") < int("10")`.
Everything read from a file is a string, and forgetting to convert is a very common bug.

</details>

[← Lists](a6-lists.md) · [Contents](../README.md) · Next: [A small project: buying fruit →](a8-project.md)
