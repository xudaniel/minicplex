\ Capacitated facility location: 3 sites, 4 customers.
\ open_i = 1 if site i is opened, x_ij = 1 if customer j is served by site i.
Minimize
 cost: 100 open1 + 120 open2 + 90 open3
     + 40 x11 + 60 x12 + 90 x13 + 50 x14
     + 70 x21 + 30 x22 + 40 x23 + 80 x24
     + 60 x31 + 80 x32 + 30 x33 + 40 x34
Subject To
 serve1: x11 + x21 + x31 = 1
 serve2: x12 + x22 + x32 = 1
 serve3: x13 + x23 + x33 = 1
 serve4: x14 + x24 + x34 = 1
 cap1: 20 x11 + 30 x12 + 25 x13 + 15 x14 - 50 open1 <= 0
 cap2: 20 x21 + 30 x22 + 25 x23 + 15 x24 - 60 open2 <= 0
 cap3: 20 x31 + 30 x32 + 25 x33 + 15 x34 - 45 open3 <= 0
Binary
 open1 open2 open3
 x11 x12 x13 x14 x21 x22 x23 x24 x31 x32 x33 x34
End
