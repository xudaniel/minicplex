"""Lesson 10: Strings and text processing.

An LP file is plain text. minicplex first cuts it into tokens (numbers, names, operators), then assembles the model from them;
when it reports results it lines numbers up in tables. You build a mini version of both.
Run: python3 python/tutorial/en/run.py 10
"""
import unicodedata

from check import lesson, eq, raises, done


def tokenize(text):
    """Cut "2 x + 3.5 y <= 12" into ["2", "x", "+", "3.5", "y", "<=", "12"].
    Rules: skip spaces; numbers are 0-9 and .; names are letters, digits and _ (starting with a letter);
    "<=" and ">=" are two-character operators, "+" "-" "=" one-character ones. Anything else: raise ValueError.
    Hint: walk an index i forward, while i < len(text); ch.isdigit(), ch.isalpha(), ch.isalnum()."""
    # >>>
    out, i = [], 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == ".":
            j = i
            while j < len(text) and (text[j].isdigit() or text[j] == "."):
                j += 1
            out.append(text[i:j])
            i = j
        elif ch.isalpha() or ch == "_":
            j = i
            while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                j += 1
            out.append(text[i:j])
            i = j
        elif text[i:i + 2] in ("<=", ">="):
            out.append(text[i:i + 2])
            i += 2
        elif ch in "+-=":
            out.append(ch)
            i += 1
        else:
            raise ValueError(f"unknown character: {ch!r}")
    return out
    # <<<


def parse_bound(line):
    """Parse a bound line: "x <= 5" -> ("x", "<=", 5.0). Use tokenize and check there are exactly 3 tokens; otherwise raise ValueError."""
    # >>>
    toks = tokenize(line)
    if len(toks) != 3 or toks[1] not in ("<=", ">=", "="):
        raise ValueError(f"cannot read this line: {line}")
    return (toks[0], toks[1], float(toks[2]))
    # <<<


def format_row(name, value):
    """One table row: the name left-aligned in 10 columns, the value right-aligned in 8 with 2 decimals.
    The f-string format: f"{name:<10}{value:>8.2f}"."""
    # >>>
    return f"{name:<10}{value:>8.2f}"
    # <<<


def display_width(s):
    """How many columns a string takes on screen: Chinese, Japanese and Korean characters (and full-width symbols) take 2, Latin letters and digits 1.
    Hint: unicodedata.east_asian_width(ch) returns "W" or "F" for wide characters (2 columns)."""
    # >>>
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in s)
    # <<<


def pad(s, width):
    """Pad s on the right so it takes exactly width columns on screen (return it unchanged if it is already that wide). f"{s:<10}" pads by character count, which goes crooked with wide characters; this pads by display width."""
    # >>>
    return s + " " * max(0, width - display_width(s))
    # <<<


def report(values):
    """values is {name: value}. One row per value (format_row), sorted by name, then a "total" row, joined with "\\n".join."""
    # >>>
    lines = [format_row(k, values[k]) for k in sorted(values)]
    lines.append(format_row("total", sum(values.values())))
    return "\n".join(lines)
    # <<<


lesson("Lesson 10: Strings and text processing")
eq("tokenize a constraint", ["2", "x", "+", "3.5", "y", "<=", "12"], lambda: tokenize("2 x + 3.5 y <= 12"))
eq("works without spaces", ["x1", ">=", "0.5"], lambda: tokenize("x1>=0.5"))
eq("names may contain underscores and digits", ["make_drill_w1", "=", "30"], lambda: tokenize("make_drill_w1 = 30"))
raises("an unknown character raises an error", ValueError, lambda: tokenize("x * 2"))
eq('parse_bound("y >= 2.5")', ("y", ">=", 2.5), lambda: parse_bound("y >= 2.5"))
raises("parse_bound rejects an incomplete line", ValueError, lambda: parse_bound("x <="))
eq("format_row", "cake          3.00", lambda: format_row("cake", 3))
eq("report", "bread         1.50\ncake          3.00\ntotal         4.50", lambda: report({"cake": 3, "bread": 1.5}))
eq('display_width("abc")', 3, lambda: display_width("abc"))
eq('display_width("数据库") (Chinese for "database"): each character takes 2 columns', 6, lambda: display_width("数据库"))
eq('display_width("Python课")', 8, lambda: display_width("Python课"))
eq('pad("运筹学", 8) pads to 8 columns', "运筹学  ", lambda: pad("运筹学", 8))
eq('pad("Python", 8)', "Python  ", lambda: pad("Python", 8))
done()
