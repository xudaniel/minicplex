\ Written by minicplex
Minimize
 obj: + 20 make_drill_w1 + 2 inv_drill_w1 + 800 setup_drill_w1 + 30 make_grinder_w1 + 3 inv_grinder_w1 + 1000 setup_grinder_w1
   + 45 make_saw_w1 + 5 inv_saw_w1 + 1500 setup_saw_w1 + 1200 overtime_w1 + 20 make_drill_w2 + 2 inv_drill_w2
   + 800 setup_drill_w2 + 30 make_grinder_w2 + 3 inv_grinder_w2 + 1000 setup_grinder_w2 + 45 make_saw_w2 + 5 inv_saw_w2
   + 1500 setup_saw_w2 + 1200 overtime_w2 + 20 make_drill_w3 + 2 inv_drill_w3 + 800 setup_drill_w3 + 30 make_grinder_w3
   + 3 inv_grinder_w3 + 1000 setup_grinder_w3 + 45 make_saw_w3 + 5 inv_saw_w3 + 1500 setup_saw_w3 + 1200 overtime_w3
   + 20 make_drill_w4 + 2 inv_drill_w4 + 800 setup_drill_w4 + 30 make_grinder_w4 + 3 inv_grinder_w4 + 1000 setup_grinder_w4
   + 45 make_saw_w4 + 5 inv_saw_w4 + 1500 setup_saw_w4 + 1200 overtime_w4 + 20 make_drill_w5 + 2 inv_drill_w5
   + 800 setup_drill_w5 + 30 make_grinder_w5 + 3 inv_grinder_w5 + 1000 setup_grinder_w5 + 45 make_saw_w5 + 5 inv_saw_w5
   + 1500 setup_saw_w5 + 1200 overtime_w5 + 20 make_drill_w6 + 2 inv_drill_w6 + 800 setup_drill_w6 + 30 make_grinder_w6
   + 3 inv_grinder_w6 + 1000 setup_grinder_w6 + 45 make_saw_w6 + 5 inv_saw_w6 + 1500 setup_saw_w6 + 1200 overtime_w6
Subject To
 balance_drill_w1: + make_drill_w1 - inv_drill_w1 = -20
 link_drill_w1: + make_drill_w1 - 280 setup_drill_w1 <= -0
 minlot_drill_w1: + make_drill_w1 - 30 setup_drill_w1 >= -0
 balance_grinder_w1: + make_grinder_w1 - inv_grinder_w1 = 30
 link_grinder_w1: + make_grinder_w1 - 186.666666666667 setup_grinder_w1 <= -0
 minlot_grinder_w1: + make_grinder_w1 - 20 setup_grinder_w1 >= -0
 balance_saw_w1: + make_saw_w1 - inv_saw_w1 = 20
 link_saw_w1: + make_saw_w1 - 140 setup_saw_w1 <= -0
 minlot_saw_w1: + make_saw_w1 - 15 setup_saw_w1 >= -0
 hours_w1: + 2 make_drill_w1 + 3 make_grinder_w1 + 4 make_saw_w1 - 80 overtime_w1 <= 400
 setups_w1: + setup_drill_w1 + setup_grinder_w1 + setup_saw_w1 <= 2
 warehouse_w1: + inv_drill_w1 + inv_grinder_w1 + inv_saw_w1 <= 250
 balance_drill_w2: + inv_drill_w1 + make_drill_w2 - inv_drill_w2 = 70
 link_drill_w2: + make_drill_w2 - 280 setup_drill_w2 <= -0
 minlot_drill_w2: + make_drill_w2 - 30 setup_drill_w2 >= -0
 balance_grinder_w2: + inv_grinder_w1 + make_grinder_w2 - inv_grinder_w2 = 30
 link_grinder_w2: + make_grinder_w2 - 186.666666666667 setup_grinder_w2 <= -0
 minlot_grinder_w2: + make_grinder_w2 - 20 setup_grinder_w2 >= -0
 balance_saw_w2: + inv_saw_w1 + make_saw_w2 - inv_saw_w2 = 30
 link_saw_w2: + make_saw_w2 - 140 setup_saw_w2 <= -0
 minlot_saw_w2: + make_saw_w2 - 15 setup_saw_w2 >= -0
 hours_w2: + 2 make_drill_w2 + 3 make_grinder_w2 + 4 make_saw_w2 - 80 overtime_w2 <= 400
 setups_w2: + setup_drill_w2 + setup_grinder_w2 + setup_saw_w2 <= 2
 warehouse_w2: + inv_drill_w2 + inv_grinder_w2 + inv_saw_w2 <= 250
 balance_drill_w3: + inv_drill_w2 + make_drill_w3 - inv_drill_w3 = 50
 link_drill_w3: + make_drill_w3 - 280 setup_drill_w3 <= -0
 minlot_drill_w3: + make_drill_w3 - 30 setup_drill_w3 >= -0
 balance_grinder_w3: + inv_grinder_w2 + make_grinder_w3 - inv_grinder_w3 = 50
 link_grinder_w3: + make_grinder_w3 - 186.666666666667 setup_grinder_w3 <= -0
 minlot_grinder_w3: + make_grinder_w3 - 20 setup_grinder_w3 >= -0
 balance_saw_w3: + inv_saw_w2 + make_saw_w3 - inv_saw_w3 = 25
 link_saw_w3: + make_saw_w3 - 140 setup_saw_w3 <= -0
 minlot_saw_w3: + make_saw_w3 - 15 setup_saw_w3 >= -0
 hours_w3: + 2 make_drill_w3 + 3 make_grinder_w3 + 4 make_saw_w3 - 80 overtime_w3 <= 400
 setups_w3: + setup_drill_w3 + setup_grinder_w3 + setup_saw_w3 <= 2
 warehouse_w3: + inv_drill_w3 + inv_grinder_w3 + inv_saw_w3 <= 250
 balance_drill_w4: + inv_drill_w3 + make_drill_w4 - inv_drill_w4 = 80
 link_drill_w4: + make_drill_w4 - 280 setup_drill_w4 <= -0
 minlot_drill_w4: + make_drill_w4 - 30 setup_drill_w4 >= -0
 balance_grinder_w4: + inv_grinder_w3 + make_grinder_w4 - inv_grinder_w4 = 40
 link_grinder_w4: + make_grinder_w4 - 186.666666666667 setup_grinder_w4 <= -0
 minlot_grinder_w4: + make_grinder_w4 - 20 setup_grinder_w4 >= -0
 balance_saw_w4: + inv_saw_w3 + make_saw_w4 - inv_saw_w4 = 35
 link_saw_w4: + make_saw_w4 - 140 setup_saw_w4 <= -0
 minlot_saw_w4: + make_saw_w4 - 15 setup_saw_w4 >= -0
 hours_w4: + 2 make_drill_w4 + 3 make_grinder_w4 + 4 make_saw_w4 - 80 overtime_w4 <= 400
 setups_w4: + setup_drill_w4 + setup_grinder_w4 + setup_saw_w4 <= 2
 warehouse_w4: + inv_drill_w4 + inv_grinder_w4 + inv_saw_w4 <= 250
 balance_drill_w5: + inv_drill_w4 + make_drill_w5 - inv_drill_w5 = 90
 link_drill_w5: + make_drill_w5 - 280 setup_drill_w5 <= -0
 minlot_drill_w5: + make_drill_w5 - 30 setup_drill_w5 >= -0
 balance_grinder_w5: + inv_grinder_w4 + make_grinder_w5 - inv_grinder_w5 = 60
 link_grinder_w5: + make_grinder_w5 - 186.666666666667 setup_grinder_w5 <= -0
 minlot_grinder_w5: + make_grinder_w5 - 20 setup_grinder_w5 >= -0
 balance_saw_w5: + inv_saw_w4 + make_saw_w5 - inv_saw_w5 = 20
 link_saw_w5: + make_saw_w5 - 140 setup_saw_w5 <= -0
 minlot_saw_w5: + make_saw_w5 - 15 setup_saw_w5 >= -0
 hours_w5: + 2 make_drill_w5 + 3 make_grinder_w5 + 4 make_saw_w5 - 80 overtime_w5 <= 400
 setups_w5: + setup_drill_w5 + setup_grinder_w5 + setup_saw_w5 <= 2
 warehouse_w5: + inv_drill_w5 + inv_grinder_w5 + inv_saw_w5 <= 250
 balance_drill_w6: + inv_drill_w5 + make_drill_w6 - inv_drill_w6 = 60
 link_drill_w6: + make_drill_w6 - 280 setup_drill_w6 <= -0
 minlot_drill_w6: + make_drill_w6 - 30 setup_drill_w6 >= -0
 balance_grinder_w6: + inv_grinder_w5 + make_grinder_w6 - inv_grinder_w6 = 50
 link_grinder_w6: + make_grinder_w6 - 186.666666666667 setup_grinder_w6 <= -0
 minlot_grinder_w6: + make_grinder_w6 - 20 setup_grinder_w6 >= -0
 balance_saw_w6: + inv_saw_w5 + make_saw_w6 - inv_saw_w6 = 40
 link_saw_w6: + make_saw_w6 - 140 setup_saw_w6 <= -0
 minlot_saw_w6: + make_saw_w6 - 15 setup_saw_w6 >= -0
 hours_w6: + 2 make_drill_w6 + 3 make_grinder_w6 + 4 make_saw_w6 - 80 overtime_w6 <= 400
 setups_w6: + setup_drill_w6 + setup_grinder_w6 + setup_saw_w6 <= 2
 warehouse_w6: + inv_drill_w6 + inv_grinder_w6 + inv_saw_w6 <= 250
Bounds
 0 <= overtime_w1 <= 2
 0 <= overtime_w2 <= 2
 0 <= overtime_w3 <= 2
 0 <= overtime_w4 <= 2
 0 <= overtime_w5 <= 2
 inv_drill_w6 >= 20
 inv_grinder_w6 >= 15
 inv_saw_w6 >= 10
 0 <= overtime_w6 <= 2
General
 overtime_w1
 overtime_w2
 overtime_w3
 overtime_w4
 overtime_w5
 overtime_w6
Binary
 setup_drill_w1
 setup_grinder_w1
 setup_saw_w1
 setup_drill_w2
 setup_grinder_w2
 setup_saw_w2
 setup_drill_w3
 setup_grinder_w3
 setup_saw_w3
 setup_drill_w4
 setup_grinder_w4
 setup_saw_w4
 setup_drill_w5
 setup_grinder_w5
 setup_saw_w5
 setup_drill_w6
 setup_grinder_w6
 setup_saw_w6
End
