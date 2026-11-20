"""Lesson 1: Your first model.

Ice cream costs $3 a cone and you have $25. How many can you buy? (Whole cones only.)
Run: python3 python/tutorial/en/run.py 01
"""
from check import lesson, eq, near, done
from minicplex import INF, Model, ObjSense, Status, VarType, solve


def ice_cream_model():
    """Return the ice-cream model: one integer variable ice_cream, one constraint money, maximise the number of cones."""
    # TODO 1. m = Model()  2. add_var an integer variable "ice_cream" (lower bound 0, upper bound INF)
    #      3. add the constraint 3 * ice_cream <= 25 named "money"  4. objective: maximise ice_cream  5. return m
    raise NotImplementedError("TODO")  # ← write your code here


lesson("Lesson 1: Your first model")
eq("the model has 1 variable", 1, lambda: ice_cream_model().num_vars)
eq("the model has 1 constraint", 1, lambda: ice_cream_model().num_constrs)
eq("the variable is called ice_cream", 0, lambda: ice_cream_model().find_var("ice_cream"))
eq("the status is Optimal", Status.OPTIMAL, lambda: solve(ice_cream_model()).status)
near("at most 8 cones", 8, lambda: solve(ice_cream_model()).objective)
done()
