"""Lesson 9: Exceptions.

When an LP file is malformed, minicplex raises LpParseError (a subclass of ValueError); the command line catches it with
try / except and prints "error: ..." instead of a long traceback. This lesson practises raising and catching exceptions.
Run: python3 python/tutorial/en/run.py 09
"""
import os
import tempfile

from check import lesson, eq, raises, that, done
from minicplex import LpParseError, read_file


def parse_amount(text):
    """Turn text such as "$12.5" or " 7 " into a number: strip the spaces and a leading "$", then float().
    If that fails, raise ValueError with the original text in the message, for example "not an amount: abc"."""
    # TODO text.strip(); s.startswith("$") / s[1:]; try: float(s) except ValueError: raise ValueError(...) from None
    # >>>
    s = text.strip()
    if s.startswith("$"):
        s = s[1:]
    try:
        return float(s)
    except ValueError:
        raise ValueError(f"not an amount: {text}") from None
    # <<<


def safe_ratio(a, b):
    """a / b; return None when b is 0 (catch ZeroDivisionError)."""
    # >>>
    try:
        return a / b
    except ZeroDivisionError:
        return None
    # <<<


def try_read(path):
    """Read an LP file with minicplex. Success returns ("ok", number of variables); a malformed file returns ("bad", message);
    a missing file returns ("missing", message).
    Hint: read_file also raises LpParseError ("cannot open file ...") for a missing file, so check os.path.exists first."""
    # >>>
    if not os.path.exists(path):
        return ("missing", f"file not found: {path}")
    try:
        return ("ok", read_file(path).num_vars)
    except LpParseError as e:
        return ("bad", str(e))
    # <<<


def write_and_read(text):
    """Write text to a temporary file, read it with try_read, and delete the file afterwards whatever happens. Use try / finally."""
    fd, path = tempfile.mkstemp(suffix=".lp")
    # >>>
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        return try_read(path)
    finally:
        os.remove(path)
    # <<<


def message_of(code):
    """Run code() and return the message of the exception it raises."""
    try:
        code()
    except ValueError as e:
        return str(e)
    return "(no exception)"


GOOD = "Maximize\n obj: x + y\nSubject To\n c: x + 2 y <= 4\nEnd\n"
BAD = "Maximize\n obj: x +\nSubject To\n c: x >= 1\nEnd\n"

lesson("Lesson 9: Exceptions")
eq('parse_amount("$12.5")', 12.5, lambda: parse_amount("$12.5"))
eq('parse_amount(" 7 ")', 7.0, lambda: parse_amount(" 7 "))
raises('parse_amount("abc") raises ValueError', ValueError, lambda: parse_amount("abc"))
eq("the message includes the original text", "not an amount: abc", lambda: message_of(lambda: parse_amount("abc")))
eq("safe_ratio(6, 3)", 2.0, lambda: safe_ratio(6, 3))
eq("safe_ratio(1, 0) is None", None, lambda: safe_ratio(1, 0))
eq("read a valid model: 2 variables", ("ok", 2), lambda: write_and_read(GOOD))
eq("read a broken model: bad", "bad", lambda: write_and_read(BAD)[0])
that("the message has a line number (LP parse error (line 3): ...)", lambda: "line 3" in write_and_read(BAD)[1])
eq("missing file: missing", "missing", lambda: try_read("no-such-file.lp")[0])
done()
