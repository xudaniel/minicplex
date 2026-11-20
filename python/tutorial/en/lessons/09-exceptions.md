# Lesson 9: Exceptions

> **You learn:** `raise`; your own exception classes; `try / except / else / finally`; `raise … from None`; `with` closing files for you; when to raise and when to catch
> **Code used:** `LpParseError` and `read_file` in [`lp_reader.py`](../../../minicplex/lp_reader.py), `run` in [`__main__.py`](../../../minicplex/__main__.py), `add_var` in [`model.py`](../../../minicplex/model.py)
> **Exercise:** `python3 python/tutorial/en/run.py 09`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l09)

[← Sorting, lambda and heaps](08-sorting-heaps.md) · [Contents](../README.md) · Next: [Strings and text processing →](10-text.md)

## 1. When something's wrong, raise

```python
if name in self._index:
    raise ValueError(f"duplicate variable name: {name}")   # model.py: a repeated variable name
```

When a function finds it can't do its job correctly, it **raises an exception**: it stops at once and passes the error up, level by level, until someone catches it; if nobody does, the program stops and prints a traceback.
That's better than returning a "special value" (such as `-1`): the caller can't forget to check.

## 2. Defining your own exception class

```python
class LpParseError(ValueError):
    """The LP file is malformed."""
```

Inheriting from `ValueError` has two benefits: anyone who wants precise handling can write `except LpParseError`, and anyone who just wants "bad input, never mind" catches it with `except ValueError`.
The message should include the **line number**, so the user can find the mistake:

```python
def fail(self, msg):
    raise LpParseError(f"LP parse error (line {self.peek().line}): {msg}")
```

## 3. Catching it: try / except

The command-line program catches every "expected" error at the outermost level and prints one line a person can understand ([`__main__.py`](../../../minicplex/__main__.py)):

```python
try:
    M = read_file(path)
    ...
except (ValueError, OSError) as e:
    print(f"error: {e}", file=sys.stderr)
    return 2
```

The full form:

```python
try:
    x = float(text)          # code that may fail
except ValueError:
    ...                      # when it fails
else:
    ...                      # when it doesn't
finally:
    ...                      # runs no matter what: close files, delete temporary files
```

**Only catch exceptions you know how to handle.** A blanket `except Exception:` hides real bugs too.

## 4. raise … from None

```python
def read_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        raise LpParseError(f"cannot open file: {path}") from None
    return read_string(text)
```

Raising a new exception inside `except` makes Python print both by default ("During handling of the above exception, another exception occurred").
`from None` says: the original was an internal detail; the user only needs to see the new one.

## 5. with: tidies up when you're done

`with open(...) as f:` guarantees the file is closed when the block ends, even if an exception happens in the middle. It's a ready-made `try / finally`.
Always pass `encoding="utf-8"` when reading or writing text files: otherwise Windows uses a different default encoding, and non-English text gets garbled.

## 6. Your turn

Open [`exercises/l09_exceptions.py`](../exercises/l09_exceptions.py): parse an amount (raise `ValueError` if it's wrong), safe division, read an LP file with minicplex and sort the outcome into three kinds, and delete a temporary file with `try / finally`. Run `python3 python/tutorial/en/run.py 09`.

## 7. Think about it

When `parse_amount` fails, should it return `None` or raise?

<details><summary>Answer</summary>

It depends on whether the caller can, and should, deal with it. "The amount the user typed is malformed" is something the caller must know about, and an exception can't be ignored.
Return `None` instead, and a later `None * 2` raises a baffling `TypeError` far away from the real mistake.
`safe_ratio` returns `None` because its name and docstring already promise "None when dividing by 0": the caller chose that on purpose.

</details>

[← Sorting, lambda and heaps](08-sorting-heaps.md) · [Contents](../README.md) · Next: [Strings and text processing →](10-text.md)
