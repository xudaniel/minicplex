"""Lesson 12: Project, a course planner.

Read a course catalog (plain text) and, within limits on hours, credits, courses per day and prerequisites, pick the set of
courses with the highest total interest, then print it as a table. It ties lessons 1-11 together: parsing text,
dataclasses, sets, modelling, exceptions and formatted output.
Run: python3 python/tutorial/en/run.py 12
"""
import unicodedata
from dataclasses import dataclass

from check import lesson, eq, raises, that, done
from minicplex import LinExpr, Model, ObjSense, Status, VarType, solve

CATALOG = """
# course      credits  hours/week  day  interest
Python        4        6           Mon  9
Algorithms    4        8           Tue  10
Databases     3        5           Mon  7
OpsResearch   3        6           Wed  10
English       2        3           Tue  4
PE            1        2           Wed  3
Writing       2        4           Mon  5
"""
DAYS = ["Mon", "Tue", "Wed"]


@dataclass(frozen=True)
class Course:
    name: str
    credits: int
    hours: int
    day: str
    interest: int


def parse(text):
    """Parse the catalog: skip blank lines and # comments; split each line on whitespace into 5 fields. Raise ValueError on a bad line."""
    # TODO text.splitlines() gives the lines; line.strip(); line.split() splits the fields; int() converts numbers
    raise NotImplementedError("TODO")  # ← write your code here


def choose(courses, max_hours, min_credits):
    """Choose courses: one 0-1 variable per course. Limits:
    total hours per week <= max_hours; total credits >= min_credits; at most 2 courses a day; Algorithms requires Python.
    Objective: maximise total interest. Return the chosen names in catalog order; an empty list if there is no solution."""
    # TODO take = [m.add_var(0, 1, VarType.BINARY, ...) for c in courses];
    #      sum((c.hours * t for c, t in zip(courses, take)), LinExpr()) adds up a column of terms;
    #      one constraint per day; prerequisite: take[Algorithms] <= take[Python]
    raise NotImplementedError("TODO")  # ← write your code here


def _pad(s, width):
    """Pad by display width (pad from lesson 10), so tables stay aligned even with wide characters."""
    w = sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in s)
    return s + " " * max(0, width - w)


def report(courses, chosen):
    """Print the chosen courses as a table (nothing to write: see how lesson 10's formatting and pad are used)."""
    rows = [c for c in courses if c.name in chosen]
    lines = [f"  {_pad(c.name, 12)} {c.day}  {c.credits} credits  {c.hours} h  interest {c.interest}" for c in rows]
    lines.append(f"  total: {sum(c.credits for c in rows)} credits, {sum(c.hours for c in rows)} h, "
                 f"interest {sum(c.interest for c in rows)}")
    return "\n".join(lines)


def prereq_always_holds():
    for h in range(41):
        c = choose(parse(CATALOG), h, 0)
        if "Algorithms" in c and "Python" not in c:
            return False
    return True


def at_most_two_per_day():
    courses = parse(CATALOG)
    for h in range(41):
        c = set(choose(courses, h, 0))
        for day in DAYS:
            if sum(1 for x in courses if x.day == day and x.name in c) > 2:
                return False
    return True


lesson("Lesson 12: Course planner")
eq("the catalog has 7 courses", 7, lambda: len(parse(CATALOG)))
eq("the first is Python, 4 credits", Course("Python", 4, 6, "Mon", 9), lambda: parse(CATALOG)[0])
raises("a line with a missing field is rejected", ValueError, lambda: parse("Python 4 6 Mon"))
raises("a bad number is rejected too", ValueError, lambda: parse("Python four 6 Mon 9"))
eq("20 hours a week, at least 10 credits: Python, Databases, OpsResearch, English", ["Python", "Databases", "OpsResearch", "English"],
   lambda: choose(parse(CATALOG), 20, 10))
eq("28 hours a week: add Algorithms", ["Python", "Algorithms", "Databases", "OpsResearch", "English"], lambda: choose(parse(CATALOG), 28, 10))
eq("only 12 hours a week: Python and OpsResearch", ["Python", "OpsResearch"], lambda: choose(parse(CATALOG), 12, 6))
eq("5 hours a week but 10 credits: no solution", [], lambda: choose(parse(CATALOG), 5, 10))
that("whatever the hours, choosing Algorithms means choosing Python", prereq_always_holds)
that("whatever the hours, at most 2 courses a day", at_most_two_per_day)
try:
    all_courses = parse(CATALOG)
    print("\nYour plan (<= 20 hours a week, >= 10 credits):")
    print(report(all_courses, choose(all_courses, 20, 10)) + "\n")
except NotImplementedError:
    print("\n(Once parse and choose are written, the plan is printed here)\n")
done()
