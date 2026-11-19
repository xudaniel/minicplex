\ 面包店（整数版）：蛋糕、面包都必须做整数个
\ 去掉 General 段就是允许做半个的线性规划版本
Maximize
 profit: 5 cake + 4 bread
Subject To
 flour: 6 cake + 4 bread <= 24
 labor: cake + 2 bread <= 6
General
 cake bread
End
