# Basics A1: Make the program talk

> **You learn:** what a Python program looks like; printing a line; strings, `+` joining and f-strings; comments
> **Time:** about 10 minutes · **Exercise:** `python3 python/tutorial/en/run.py A01`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#a01)

[Contents](../README.md) · Next: [Variables and arithmetic →](a2-variables.md)

## 1. The smallest Python program

Create a file `hello.py` with a single line:

```python
print("Hello, Python!")
```

Run `python3 hello.py` on the command line (on Windows it may be `python hello.py` or `py hello.py`) and `Hello, Python!` appears on the screen.

Three things are enough to remember:

- A program starts at the first line of the file and runs downwards, line by line.
- `print(...)` prints a line.
- Python needs no semicolons and no curly braces: one line is one statement.

## 2. Strings: text inside quotes

```python
print("Hello")                    # Hello
print("Hello, " + "Ming")         # Hello, Ming     ← + joins two pieces of text
print("apple: $" + 2)             # ✗ error: TypeError, text and numbers can't be added with +
print(f"apple: ${2}")             # apple: $2       ← f-string: put f before the quotes, any value goes in {}
```

Everything after `#` is a **comment**: it is written for people, and Python skips it.

The last form is an **f-string**, the most common way to build text in Python: in `f"{name} is {age} years old"` each pair of braces is replaced by its value.

## 3. Returning a value

The exercises don't print their answers; they hand them back with `return`, so that the checker can compare your answer:

```python
def greet(name):
    return "Hello, " + name + "!"
```

A line starting with `def` defines a **function** (more in A5). Notice the 4 spaces in front of the second line: Python uses **indentation** to know which lines belong to the function.
Calling `greet("Ming")` gives `"Hello, Ming!"`. `name` is the name passed in from outside.

## 4. Common mistakes

- **Wrong indentation**: `IndentationError`. Every line inside a function must be indented 4 spaces more than `def`, and the lines must line up.
- **Curly quotes**: word processors turn `"` into `“ ”`, which Python doesn't accept. Type code in a code editor, not in a word processor.
- **Capitals**: `Print("hi")` is wrong; it has to be `print`.

## 5. Your turn

Open [`exercises/a01_hello.py`](../exercises/a01_hello.py). Each function contains a line:

```python
raise NotImplementedError("TODO")  # ← write your code here
```

It means "not written yet". **Delete** that line and put your code in its place (keep the indentation), then run:

```bash
python3 python/tutorial/en/run.py A01
```

✅ means right, ❌ means wrong (it shows what was expected and what you got), ⏳ means not written yet.

## 6. Think about it

What are `"1" + "2"` and `1 + 2`? And `"1" + 2`?

<details><summary>Answer</summary>

`"1" + "2"` is the string `"12"` (two pieces of text joined); `1 + 2` is the number `3`; `"1" + 2` raises `TypeError`: Python won't turn a number into text by itself, so write `"1" + str(2)` or `f"1{2}"`.

</details>

[Contents](../README.md) · Next: [Variables and arithmetic →](a2-variables.md)
