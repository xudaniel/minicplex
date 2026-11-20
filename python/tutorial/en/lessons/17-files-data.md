# Lesson 17: Files and data: pathlib, CSV, JSON

> **You learn:** `pathlib.Path`; reading and writing text files and encodings; the `csv` module; the `json` module; temporary files and folders; a complete "read data → model → write results" pipeline
> **Code used:** `write_lp` in [`model.py`](../../../minicplex/model.py), `read_file` in [`lp_reader.py`](../../../minicplex/lp_reader.py), CSV reading in [`tools/compare_java_cpp.py`](../../../../tools/compare_java_cpp.py), JSON writing in [`make_web.py`](../../make_web.py)
> **Exercise:** `python3 python/tutorial/en/run.py 17`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l17)

[← Generators and iterators](16-generators.md) · [Contents](../README.md) · Next: [Command-line programs and packaging →](18-cli-packaging.md)

## 1. pathlib: paths as objects

```python
from pathlib import Path

folder = Path("data")
f = folder / "products.csv"          # join paths with /, right on Windows, macOS and Linux
f.exists(), f.name, f.suffix         # True, 'products.csv', '.csv'
text = f.read_text(encoding="utf-8")
f.with_suffix(".json").write_text("{}", encoding="utf-8")
for p in folder.glob("*.lp"): ...    # find every .lp file
```

Compared with gluing strings like `"data" + "/" + name`, `Path` never gets the slashes wrong, and reading or writing a file takes one line.

## 2. Encoding: always write encoding="utf-8"

```python
with open(path, encoding="utf-8") as f:     # exactly how read_file in lp_reader.py does it
    text = f.read()
```

Leave it out and Python uses the operating system's default encoding: usually UTF-8 on macOS and Linux, often not on Windows. The same program on another computer then garbles non-English text or raises `UnicodeDecodeError`.

## 3. CSV: tables of data

minicplex's batch-solving tool writes its results as CSV, and the comparison script reads them back:

```python
a = {r["model"]: r for r in csv.DictReader(open(args[0], encoding="utf-8"))}   # tools/compare_java_cpp.py
```

`csv.DictReader` turns each row into a dict keyed by the header. Two points:

- What you read is **all strings**; convert numbers yourself with `int()` / `float()`.
- Open the file with `newline=""`, or Windows gets extra blank lines.

To write, use `csv.DictWriter(f, fieldnames=[...])`: `writeheader()` first, then `writerows(rows)`. Why not join with `","` yourself? Because fields may contain commas, quotes or newlines, and the `csv` module handles them for you.

## 4. JSON: structured data

```python
json.dumps(course, ensure_ascii=False)          # make_web.py: the web course is one big JSON file
data = json.loads(text)
```

JSON stores dicts, lists, strings, numbers and `true`/`false`/`null`, and almost every language and every web page can read it.
`ensure_ascii=False` writes non-ASCII text such as `☕` or `保温杯` as it is; without it you get escapes like `☕` (which still read back fine, but people can't read them).
`indent=2` indents the output for human readers.

## 5. Temporary files

Tests often need "write a file to try something, then delete it":

```python
with tempfile.TemporaryDirectory() as d:
    folder = Path(d)
    ...                    # write whatever you like in folder
# leaving the with block deletes the whole folder
```

Lesson 9 deleted a temporary file by hand with `try / finally`; `TemporaryDirectory` wraps that up for you.

## 6. The whole pipeline

The exercise ties it together:

```text
products.csv ──read──▶ [dict, …] ──plan()──▶ what to take ──write──▶ result.json ──read──▶ check
```

There's a small surprise in the result: with 6 kg of room, intuition says "take the light things, more of them" (thermos, tea and book, profit 75),
but the solver picks the thermos and the lamp (profit 80). That's exactly what optimisation models are for: intuition is often wrong on combination problems.

## 7. Your turn

Open [`exercises/l17_files_data.py`](../exercises/l17_files_data.py), write the CSV and JSON reading and writing, and run `python3 python/tutorial/en/run.py 17`.

## 8. Think about it

Why does `read_products` convert `weight` and `profit` to `int` itself, instead of leaving it to whoever uses the data?

<details><summary>Answer</summary>

"The data came from a file" is a detail of the reading layer, and users shouldn't have to care. Convert once at the boundary, and everything after it gets clean data of the right type.
Otherwise every place that uses it must remember to convert, and forgetting once gives lesson 13's "no error, wrong answer" kind of bug (`"2" * 3` is `"222"`).

</details>

[← Generators and iterators](16-generators.md) · [Contents](../README.md) · Next: [Command-line programs and packaging →](18-cli-packaging.md)
