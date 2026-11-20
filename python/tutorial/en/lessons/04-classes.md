# Lesson 4: Classes and objects

> **You learn:** `class`, `__init__`, `self`; attributes and methods; default arguments instead of "overloading"; `@property`; `__repr__`; `__slots__`
> **Code used:** `VarInfo`, `Model.add_var` and `Model.num_vars` in [`model.py`](../../../minicplex/model.py)
> **Exercise:** `python3 python/tutorial/en/run.py 04`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l04)

[← Lists and comprehensions](03-lists.md) · [Contents](../README.md) · Next: [Operator overloading and immutable objects →](05-operators.md)

## 1. A class keeps data and operations together

A variable has a name, bounds and a type. minicplex packs them into one class ([`model.py`](../../../minicplex/model.py)):

```python
class VarInfo:
    """A variable's name, bounds and type."""
    __slots__ = ("name", "lb", "ub", "type")

    def __init__(self, name, lb, ub, type):
        self.name = name
        self.lb = lb
        self.ub = ub
        self.type = type

    def copy(self):
        return VarInfo(self.name, self.lb, self.ub, self.type)
```

- `class VarInfo:` defines a new type; `VarInfo("x", 0, 10, VarType.INTEGER)` creates an **object**.
- `__init__` runs automatically when an object is created and stores the attributes.
- `self` is "this object itself". It is the first parameter of every method, and you don't pass it when calling: `v.copy()`.
- `__slots__` (optional) declares up front that only these attributes exist: it saves memory, and a misspelt attribute (`v.nmae = ...`) raises an error straight away.

## 2. Methods: what an object can do

```python
class Model:
    def add_var(self, lb=0.0, ub=INF, type=VarType.CONTINUOUS, name=""):
        lb, ub = float(lb), float(ub)
        if type == VarType.BINARY:
            lb = max(lb, 0.0)
            ub = min(ub, 1.0)
        if not name:
            name = f"x{len(self.vars) + 1}"
        if name in self._index:
            raise ValueError(f"duplicate variable name: {name}")
        self._index[name] = len(self.vars)
        self.vars.append(VarInfo(name, lb, ub, type))
        return Var(len(self.vars) - 1)
```

The method reads and changes the object's state (`self.vars`), then hands back a small `Var` handle.
The underscore in `_index` is a convention: "internal, don't touch from outside". Python doesn't enforce it, but everyone respects it.

## 3. @property: a method used like an attribute

```python
@property
def num_vars(self):
    return len(self.vars)

m.num_vars      # no parentheses
```

The value is computed, but it's used like a plain attribute. The benefit: if the internal storage changes later, outside code doesn't change at all.

## 4. __repr__: what it looks like when printed

```python
>>> VarInfo("x", 0.0, 10.0, VarType.INTEGER)
VarInfo('x', 0, 10, INTEGER)
```

Without `__repr__` you'd only see `<minicplex.model.VarInfo object at 0x7f…>`, which is useless when debugging.
By convention, `__repr__` looks like "the code that would create this object".

## 5. Each object has its own data

```python
a, b = Product("apple", 2.5, 5), Product("pear", 3, 5)
a.sell(1)
a.stock, b.stock     # (4, 5)
```

`self.stock` lives in each object separately, so they don't affect each other. But writing `stock = []` in the class body (not in `__init__`) makes a "class attribute" shared by every object; lesson 6 meets this trap again.

## 6. Your turn

Open [`exercises/l04_classes.py`](../exercises/l04_classes.py) and write a `Product` class: stock defaults to 0, total stock value, selling, an `in_stock` property, and `__repr__`. Run `python3 python/tutorial/en/run.py 04`.

## 7. Think about it

Is there any difference between `m.add_var(0, 1, VarType.BINARY)` and `m.add_var(type=VarType.BINARY, ub=1)`?

<details><summary>Answer</summary>

None. Positional arguments need you to remember the order; named arguments can come in any order and read better. With many parameters, most of them defaulted, passing by name is a good habit.
`Params(relax_integrality=True, cut_rounds=0)` is used exactly like that (lesson 6).

</details>

[← Lists and comprehensions](03-lists.md) · [Contents](../README.md) · Next: [Operator overloading and immutable objects →](05-operators.md)
