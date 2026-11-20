"""A tiny test framework for the exercises: each check prints ✅ (pass), ❌ (wrong) or ⏳ (not written yet).

You don't need to change this file, but it is worth reading: it uses lambdas (lesson 8) and exceptions (lesson 9).

    from check import lesson, eq, near, that, raises, done

    lesson("Basics A1: Make the program talk")
    eq("greet('Ming')", "Hello, Ming!", lambda: greet("Ming"))
    done()
"""
import pathlib
import sys

# Import minicplex without installing it: add the repository's python/ folder to the search path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from minicplex import use_utf8_output  # noqa: E402

use_utf8_output()  # emoji and accents print correctly on every system

_pass = _fail = _todo = 0


def lesson(title):
    """Print the lesson title."""
    print(f"== {title} ==")


def _is_todo(e):
    return isinstance(e, NotImplementedError) and e.args == ("TODO",)


_ERROR_HINTS = {
    "TypeError": "Wrong type: for example adding text and a number with +, doing arithmetic on None, or calling a function with the wrong number of arguments.",
    "NameError": "A name that was never defined: a typo, or missing quotes around some text?",
    "IndexError": "Index out of range: a list with n items ends at [n - 1].",
    "KeyError": "That key is not in the dictionary: check with `in` first, or use .get().",
    "ZeroDivisionError": "Division by zero: did you average an empty list?",
    "AttributeError": "This object has no such attribute or method: a typo? If the object is None, some function probably forgot to return.",
    "UnboundLocalError": "A variable was used before it got a value: did you forget a starting value such as total = 0?",
    "RecursionError": "The function keeps calling itself forever: recursion needs a case that stops.",
}


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _why(expected, actual):
    """Guess the common reason for a wrong answer (None if there is no good guess)."""
    if actual is None and expected is not None:
        return "The function returned None: did you forget `return`, or use print instead of return?"
    if isinstance(expected, bool) and not isinstance(actual, bool):
        return "This needs True or False. A comparison already is True/False, so you can write return a >= b."
    if _num(expected) and _num(actual):
        if isinstance(expected, int) and isinstance(actual, float) and actual != int(actual):
            return "Expected a whole number but got a decimal: use // (floor division), not /."
        if abs(expected - actual) == 1:
            return "Off by one: check where range stops (range(1, n) excludes n), < versus <=, or the counter's starting value."
        if actual == -expected:
            return "The sign is flipped: check the order of a subtraction."
        if expected != 0 and abs(actual / expected - 1) < 1e-6:
            return "Very close but not equal: decimals carry rounding error (lesson 2); compare them with a tolerance."
    if isinstance(expected, str) and isinstance(actual, str):
        if actual.strip() == expected.strip():
            return "Only the spaces or newlines at the start or end differ."
        if actual.lower() == expected.lower():
            return "Only upper/lower case differs."
        if actual.replace(" ", "") == expected.replace(" ", ""):
            return "Only the spaces in the middle differ."
    lists = isinstance(expected, (list, tuple)) and isinstance(actual, (list, tuple))
    if lists and type(expected) is not type(actual) and list(expected) == list(actual):
        return f"Right items, wrong type: expected a {type(expected).__name__}, got a {type(actual).__name__}."
    if lists and len(expected) == len(actual) and sorted(map(repr, expected)) == sorted(map(repr, actual)):
        return "All the items are right but the order is not."
    if lists and abs(len(expected) - len(actual)) == 1:
        return "One item too many or too few: check where your loop starts and stops."
    return None


def _explain(err, expected, actual):
    hint = _why(expected, actual)
    return err + (f"\n   💡 {hint}" if hint else "")


def _run(what, check):
    global _pass, _fail, _todo
    try:
        err = check()
    except NotImplementedError as e:
        if not _is_todo(e):
            err = f"raised {type(e).__name__}: {e}"
        else:
            _todo += 1
            print(f"⏳ {what} (not written yet: look for TODO)")
            return
    except (Exception, SystemExit) as e:  # noqa: BLE001  catch whatever the student's code raises
        err = f"raised {type(e).__name__}: {e}"
        if type(e).__name__ in _ERROR_HINTS:
            err += f"\n   💡 {_ERROR_HINTS[type(e).__name__]}"
    if err is None:
        _pass += 1
        print(f"✅ {what}")
    else:
        _fail += 1
        print(f"❌ {what}: {err}")


def that(what, cond):
    """Check that a condition holds. cond is a function with no arguments (usually lambda: ...)."""
    _run(what, lambda: None if cond() else "the condition is false")


def eq(what, expected, actual):
    """Check that actual() == expected."""
    def check():
        a = actual()
        if isinstance(expected, bool) or isinstance(a, bool):
            ok = a is expected  # True and 1 are not the same answer
        else:
            ok = a == expected
        return None if ok else _explain(f"expected {expected!r}, got {a!r}", expected, a)
    _run(what, check)


def near(what, expected, actual):
    """Check that two numbers are close enough (relative error 1e-6)."""
    def check():
        a = actual()
        ok = isinstance(a, (int, float)) and abs(a - expected) <= 1e-6 * (1 + abs(expected))
        return None if ok else _explain(f"expected about {expected!r}, got {a!r}", expected, a)
    _run(what, check)


def raises(what, error_type, code):
    """Check that running code() raises error_type."""
    def check():
        try:
            code()
        except NotImplementedError as e:
            if _is_todo(e):
                raise
            return None if issubclass(NotImplementedError, error_type) else f"raised {type(e).__name__}"
        except (Exception, SystemExit) as e:  # noqa: BLE001  argparse exits with SystemExit on errors
            return None if isinstance(e, error_type) else f"raised {type(e).__name__}: {e}"
        return f"did not raise {error_type.__name__}"
    _run(what, check)


def done():
    """Print the summary and exit: 1 if anything is wrong, 3 if something is not written yet, 0 if all pass."""
    print(f"-- passed {_pass}, wrong {_fail}, todo {_todo}" + (". All done 🎉" if _fail == 0 and _todo == 0 else ""))
    sys.exit(1 if _fail else 3 if _todo else 0)


__all__ = ["lesson", "that", "eq", "near", "raises", "done"]
