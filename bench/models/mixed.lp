\ Mixed-integer example with free, negative and general-integer variables
Minimize
 obj: 2 x + 3 y - z + w
Subject To
 c1: x + y + z >= 4.5
 c2: x - y + 2 w = -1
 c3: z <= 3.7
 c4: - x + 3 w >= -6
Bounds
 -10 <= x <= 10
 y >= -2
 w free
General
 x y
End
