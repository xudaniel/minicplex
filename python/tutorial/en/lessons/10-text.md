# Lesson 10: Strings and text processing

> **You learn:** scanning text with an index (a hand-written tokenizer); `split`, `strip`, `join`; f-string format specs; `%` formatting; the right way to build a lot of text; display width of East Asian characters
> **Code used:** `_tokenize` in [`lp_reader.py`](../../../minicplex/lp_reader.py), [`fmt.py`](../../../minicplex/fmt.py), `to_lp` in [`model.py`](../../../minicplex/model.py)
> **Exercise:** `python3 python/tutorial/en/run.py 10`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l10)

[← Exceptions](09-exceptions.md) · [Contents](../README.md) · Next: [Testing →](11-testing.md)

## 1. Cut it into tokens first

`c1: 2 x + 3.5 y <= 12` is obvious to a person, but to a program it's just a string of characters. The first step in reading an LP file is cutting it into **tokens**:
`c1` `:` `2` `x` `+` `3.5` `y` `<=` `12`. `_tokenize` in [`lp_reader.py`](../../../minicplex/lp_reader.py) walks forward with an index `i`:

```python
while i < n:
    c = src[i]
    if _is_ws(c):                 # whitespace: skip
        i += 1
        continue
    if _is_digit(src, i) or (c == "." and _is_digit(src, i + 1)):
        j = i
        while _is_digit(src, j):  # a number: read until the digits stop
            j += 1
        ...
        t.kind, t.s = NUM, src[i:j]
        i = j
    elif c in "<>=":              # <= and >= are two-character operators
        ...
```

This "look at one character to decide how to read what follows" style is used by the compiler of almost every programming language. Once the tokens are cut, parsing is easy:
"a name followed by `:` is a constraint name", "a number followed by a name is a term".

## 2. Why not just split?

`"2 x + 3.5 y <= 12".split()` seems to work, but `x1>=0.5` has no spaces, and `split` is stuck. The LP format allows missing spaces, so you have to scan one character at a time.

## 3. Format specs

Inside an f-string's braces, a format can follow a colon:

```python
f"{name:<10}"        # left-aligned, 10 columns wide
f"{value:>8.2f}"     # right-aligned, 8 wide, 2 decimals
f"{n:5d}"            # an integer, 5 wide
f"{x:.6g}"           # 6 significant digits, decimal or scientific as needed: 1e-07, 21, 3.33333
f"{ratio:.1%}"       # a percentage: 0.256 → 25.6%
```

minicplex always prints numbers in `%g` style ([`fmt.py`](../../../minicplex/fmt.py)):

```python
def g(v, precision=6):
    """The same as C's printf("%.{precision}g", v)."""
    return "%.*g" % (precision, v)
```

This uses old-style `%` formatting (just like C's `printf`) because its rules are identical to the C++ version's, so the three versions print exactly the same output.
In new code an f-string is usually fine.

## 4. Lots of pieces of text: collect in a list, join at the end

`to_lp` in [`model.py`](../../../minicplex/model.py) produces hundreds of lines:

```python
out = ["\\ Written by minicplex\n"]
...
out.append(f" {c.name}:")
...
return "".join(out)
```

Don't do `s += "..."` in a loop: strings can't be changed, so every `+=` copies the whole string and it gets slower and slower. `append` to a list, then `"".join(...)` once at the end: fast and clear.

## 5. Chinese, Japanese, Korean and alignment

`f"{name:<6}"` pads by **number of characters**, but a Chinese character takes up the width of two English letters on screen, so tables with mixed text go crooked:

```text
Python 4 credits       ← the result of f"{name:<6}"
数据库    3 credits    ← three characters got 3 spaces of padding, but take 6 columns
```

(数据库 is Chinese for "database".) The fix is to pad by **display width**. The standard library's `unicodedata.east_asian_width(ch)` tells you whether a character is "wide" (it returns `"W"` or `"F"`);
wide characters count 2 columns, everything else 1. The exercise asks you to write `display_width` and `pad`; the course table in lesson 12 uses them for alignment.

## 6. Your turn

Open [`exercises/l10_text.py`](../exercises/l10_text.py): write a mini tokenizer, parse a bound line, lay out a small report, and write `pad`, which aligns by display width. Run `python3 python/tutorial/en/run.py 10`.

## 7. Think about it

Should `tokenize("x2")` give `["x2"]` or `["x", "2"]`? And `tokenize("2x")`?

<details><summary>Answer</summary>

`"x2"` is one name (starts with a letter, may contain digits after); `"2x"` is `["2", "x"]`: a number is read first, and only when it ends does a name start.
That's exactly what the LP format specifies, so `2x + 3y` can be read without spaces. Settle the rules first, then write the code; that's also why tests are a must (next lesson).

</details>

[← Exceptions](09-exceptions.md) · [Contents](../README.md) · Next: [Testing →](11-testing.md)
