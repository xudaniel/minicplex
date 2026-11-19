\ Written by minicplex
Minimize
 obj: + 256 wang_d1_am + 256 wang_d1_pm + 256 wang_d2_am + 256 wang_d2_pm + 256 wang_d3_am + 256 wang_d3_pm
   + 256 wang_d4_am + 256 wang_d4_pm + 256 wang_d5_am + 256 wang_d5_pm + 296 wang_d6_am + 296 wang_d6_pm
   + 296 wang_d7_am + 296 wang_d7_pm + 224 li_d1_am + 224 li_d1_pm + 224 li_d2_am + 224 li_d2_pm
   + 224 li_d3_am + 224 li_d3_pm + 224 li_d4_am + 224 li_d4_pm + 224 li_d5_am + 224 li_d5_pm
   + 224 li_d6_am + 224 li_d6_pm + 224 li_d7_am + 224 li_d7_pm + 208 zhang_d1_am + 238 zhang_d1_pm
   + 208 zhang_d2_am + 238 zhang_d2_pm + 208 zhang_d3_am + 238 zhang_d3_pm + 208 zhang_d4_am + 238 zhang_d4_pm
   + 208 zhang_d5_am + 238 zhang_d5_pm + 208 zhang_d6_am + 238 zhang_d6_pm + 208 zhang_d7_am + 238 zhang_d7_pm
   + 208 chen_d1_am + 208 chen_d1_pm + 208 chen_d2_am + 208 chen_d2_pm + 208 chen_d3_am + 208 chen_d3_pm
   + 208 chen_d4_am + 208 chen_d4_pm + 208 chen_d5_am + 208 chen_d5_pm + 228 chen_d6_am + 228 chen_d6_pm
   + 228 chen_d7_am + 228 chen_d7_pm + 160 liu_d1_am + 160 liu_d1_pm + 160 liu_d2_am + 160 liu_d2_pm
   + 160 liu_d3_am + 160 liu_d3_pm + 160 liu_d4_am + 160 liu_d4_pm + 160 liu_d5_am + 160 liu_d5_pm
   + 160 liu_d6_am + 160 liu_d6_pm + 160 liu_d7_am + 160 liu_d7_pm + 160 zhao_d1_am + 160 zhao_d1_pm
   + 160 zhao_d2_am + 160 zhao_d2_pm + 160 zhao_d3_am + 160 zhao_d3_pm + 160 zhao_d4_am + 160 zhao_d4_pm
   + 160 zhao_d5_am + 160 zhao_d5_pm + 160 zhao_d6_am + 160 zhao_d6_pm + 160 zhao_d7_am + 160 zhao_d7_pm
   + 168 zhou_d1_am + 183 zhou_d1_pm + 168 zhou_d2_am + 183 zhou_d2_pm + 168 zhou_d3_am + 183 zhou_d3_pm
   + 168 zhou_d4_am + 183 zhou_d4_pm + 168 zhou_d5_am + 183 zhou_d5_pm + 168 zhou_d6_am + 183 zhou_d6_pm
   + 168 zhou_d7_am + 183 zhou_d7_pm + 152 sun_d1_am + 152 sun_d1_pm + 152 sun_d2_am + 152 sun_d2_pm
   + 152 sun_d3_am + 152 sun_d3_pm + 152 sun_d4_am + 152 sun_d4_pm + 152 sun_d5_am + 152 sun_d5_pm
   + 177 sun_d6_am + 177 sun_d6_pm + 177 sun_d7_am + 177 sun_d7_pm
Subject To
 cover_d1_am: + wang_d1_am + li_d1_am + zhang_d1_am + chen_d1_am + liu_d1_am + zhao_d1_am
   + zhou_d1_am + sun_d1_am >= 2
 senior_d1_am: + wang_d1_am + li_d1_am + zhang_d1_am + chen_d1_am >= 1
 cover_d1_pm: + wang_d1_pm + li_d1_pm + zhang_d1_pm + chen_d1_pm + liu_d1_pm + zhao_d1_pm
   + zhou_d1_pm + sun_d1_pm >= 2
 senior_d1_pm: + wang_d1_pm + li_d1_pm + zhang_d1_pm + chen_d1_pm >= 1
 cover_d2_am: + wang_d2_am + li_d2_am + zhang_d2_am + chen_d2_am + liu_d2_am + zhao_d2_am
   + zhou_d2_am + sun_d2_am >= 2
 senior_d2_am: + wang_d2_am + li_d2_am + zhang_d2_am + chen_d2_am >= 1
 cover_d2_pm: + wang_d2_pm + li_d2_pm + zhang_d2_pm + chen_d2_pm + liu_d2_pm + zhao_d2_pm
   + zhou_d2_pm + sun_d2_pm >= 2
 senior_d2_pm: + wang_d2_pm + li_d2_pm + zhang_d2_pm + chen_d2_pm >= 1
 cover_d3_am: + wang_d3_am + li_d3_am + zhang_d3_am + chen_d3_am + liu_d3_am + zhao_d3_am
   + zhou_d3_am + sun_d3_am >= 2
 senior_d3_am: + wang_d3_am + li_d3_am + zhang_d3_am + chen_d3_am >= 1
 cover_d3_pm: + wang_d3_pm + li_d3_pm + zhang_d3_pm + chen_d3_pm + liu_d3_pm + zhao_d3_pm
   + zhou_d3_pm + sun_d3_pm >= 2
 senior_d3_pm: + wang_d3_pm + li_d3_pm + zhang_d3_pm + chen_d3_pm >= 1
 cover_d4_am: + wang_d4_am + li_d4_am + zhang_d4_am + chen_d4_am + liu_d4_am + zhao_d4_am
   + zhou_d4_am + sun_d4_am >= 2
 senior_d4_am: + wang_d4_am + li_d4_am + zhang_d4_am + chen_d4_am >= 1
 cover_d4_pm: + wang_d4_pm + li_d4_pm + zhang_d4_pm + chen_d4_pm + liu_d4_pm + zhao_d4_pm
   + zhou_d4_pm + sun_d4_pm >= 2
 senior_d4_pm: + wang_d4_pm + li_d4_pm + zhang_d4_pm + chen_d4_pm >= 1
 cover_d5_am: + wang_d5_am + li_d5_am + zhang_d5_am + chen_d5_am + liu_d5_am + zhao_d5_am
   + zhou_d5_am + sun_d5_am >= 2
 senior_d5_am: + wang_d5_am + li_d5_am + zhang_d5_am + chen_d5_am >= 1
 cover_d5_pm: + wang_d5_pm + li_d5_pm + zhang_d5_pm + chen_d5_pm + liu_d5_pm + zhao_d5_pm
   + zhou_d5_pm + sun_d5_pm >= 3
 senior_d5_pm: + wang_d5_pm + li_d5_pm + zhang_d5_pm + chen_d5_pm >= 1
 cover_d6_am: + wang_d6_am + li_d6_am + zhang_d6_am + chen_d6_am + liu_d6_am + zhao_d6_am
   + zhou_d6_am + sun_d6_am >= 3
 senior_d6_am: + wang_d6_am + li_d6_am + zhang_d6_am + chen_d6_am >= 1
 cover_d6_pm: + wang_d6_pm + li_d6_pm + zhang_d6_pm + chen_d6_pm + liu_d6_pm + zhao_d6_pm
   + zhou_d6_pm + sun_d6_pm >= 3
 senior_d6_pm: + wang_d6_pm + li_d6_pm + zhang_d6_pm + chen_d6_pm >= 1
 cover_d7_am: + wang_d7_am + li_d7_am + zhang_d7_am + chen_d7_am + liu_d7_am + zhao_d7_am
   + zhou_d7_am + sun_d7_am >= 3
 senior_d7_am: + wang_d7_am + li_d7_am + zhang_d7_am + chen_d7_am >= 1
 cover_d7_pm: + wang_d7_pm + li_d7_pm + zhang_d7_pm + chen_d7_pm + liu_d7_pm + zhao_d7_pm
   + zhou_d7_pm + sun_d7_pm >= 3
 senior_d7_pm: + wang_d7_pm + li_d7_pm + zhang_d7_pm + chen_d7_pm >= 1
 wang_one_d1: + wang_d1_am + wang_d1_pm <= 1
 wang_rest_d1: + wang_d1_pm + wang_d2_am <= 1
 wang_one_d2: + wang_d2_am + wang_d2_pm <= 1
 wang_rest_d2: + wang_d2_pm + wang_d3_am <= 1
 wang_one_d3: + wang_d3_am + wang_d3_pm <= 1
 wang_rest_d3: + wang_d3_pm + wang_d4_am <= 1
 wang_one_d4: + wang_d4_am + wang_d4_pm <= 1
 wang_rest_d4: + wang_d4_pm + wang_d5_am <= 1
 wang_one_d5: + wang_d5_am + wang_d5_pm <= 1
 wang_rest_d5: + wang_d5_pm + wang_d6_am <= 1
 wang_one_d6: + wang_d6_am + wang_d6_pm <= 1
 wang_rest_d6: + wang_d6_pm + wang_d7_am <= 1
 wang_one_d7: + wang_d7_am + wang_d7_pm <= 1
 wang_streak_d1: + wang_d1_am + wang_d1_pm + wang_d2_am + wang_d2_pm + wang_d3_am + wang_d3_pm
   + wang_d4_am + wang_d4_pm <= 3
 wang_streak_d2: + wang_d2_am + wang_d2_pm + wang_d3_am + wang_d3_pm + wang_d4_am + wang_d4_pm
   + wang_d5_am + wang_d5_pm <= 3
 wang_streak_d3: + wang_d3_am + wang_d3_pm + wang_d4_am + wang_d4_pm + wang_d5_am + wang_d5_pm
   + wang_d6_am + wang_d6_pm <= 3
 wang_streak_d4: + wang_d4_am + wang_d4_pm + wang_d5_am + wang_d5_pm + wang_d6_am + wang_d6_pm
   + wang_d7_am + wang_d7_pm <= 3
 wang_mindays: + wang_d1_am + wang_d1_pm + wang_d2_am + wang_d2_pm + wang_d3_am + wang_d3_pm
   + wang_d4_am + wang_d4_pm + wang_d5_am + wang_d5_pm + wang_d6_am + wang_d6_pm
   + wang_d7_am + wang_d7_pm >= 4
 wang_maxdays: + wang_d1_am + wang_d1_pm + wang_d2_am + wang_d2_pm + wang_d3_am + wang_d3_pm
   + wang_d4_am + wang_d4_pm + wang_d5_am + wang_d5_pm + wang_d6_am + wang_d6_pm
   + wang_d7_am + wang_d7_pm <= 5
 li_one_d1: + li_d1_am + li_d1_pm <= 1
 li_rest_d1: + li_d1_pm + li_d2_am <= 1
 li_one_d2: + li_d2_am + li_d2_pm <= 1
 li_rest_d2: + li_d2_pm + li_d3_am <= 1
 li_one_d3: + li_d3_am + li_d3_pm <= 1
 li_rest_d3: + li_d3_pm + li_d4_am <= 1
 li_one_d4: + li_d4_am + li_d4_pm <= 1
 li_rest_d4: + li_d4_pm + li_d5_am <= 1
 li_one_d5: + li_d5_am + li_d5_pm <= 1
 li_rest_d5: + li_d5_pm + li_d6_am <= 1
 li_one_d6: + li_d6_am + li_d6_pm <= 1
 li_rest_d6: + li_d6_pm + li_d7_am <= 1
 li_one_d7: + li_d7_am + li_d7_pm <= 1
 li_streak_d1: + li_d1_am + li_d1_pm + li_d2_am + li_d2_pm + li_d3_am + li_d3_pm
   + li_d4_am + li_d4_pm <= 3
 li_streak_d2: + li_d2_am + li_d2_pm + li_d3_am + li_d3_pm + li_d4_am + li_d4_pm
   + li_d5_am + li_d5_pm <= 3
 li_streak_d3: + li_d3_am + li_d3_pm + li_d4_am + li_d4_pm + li_d5_am + li_d5_pm
   + li_d6_am + li_d6_pm <= 3
 li_streak_d4: + li_d4_am + li_d4_pm + li_d5_am + li_d5_pm + li_d6_am + li_d6_pm
   + li_d7_am + li_d7_pm <= 3
 li_mindays: + li_d1_am + li_d1_pm + li_d2_am + li_d2_pm + li_d3_am + li_d3_pm
   + li_d4_am + li_d4_pm + li_d5_am + li_d5_pm + li_d6_am + li_d6_pm
   + li_d7_am + li_d7_pm >= 4
 li_maxdays: + li_d1_am + li_d1_pm + li_d2_am + li_d2_pm + li_d3_am + li_d3_pm
   + li_d4_am + li_d4_pm + li_d5_am + li_d5_pm + li_d6_am + li_d6_pm
   + li_d7_am + li_d7_pm <= 5
 li_weekend: + li_d6_am + li_d6_pm + li_d7_am + li_d7_pm <= 1
 zhang_one_d1: + zhang_d1_am + zhang_d1_pm <= 1
 zhang_rest_d1: + zhang_d1_pm + zhang_d2_am <= 1
 zhang_one_d2: + zhang_d2_am + zhang_d2_pm <= 1
 zhang_rest_d2: + zhang_d2_pm + zhang_d3_am <= 1
 zhang_one_d3: + zhang_d3_am + zhang_d3_pm <= 1
 zhang_rest_d3: + zhang_d3_pm + zhang_d4_am <= 1
 zhang_one_d4: + zhang_d4_am + zhang_d4_pm <= 1
 zhang_rest_d4: + zhang_d4_pm + zhang_d5_am <= 1
 zhang_one_d5: + zhang_d5_am + zhang_d5_pm <= 1
 zhang_rest_d5: + zhang_d5_pm + zhang_d6_am <= 1
 zhang_one_d6: + zhang_d6_am + zhang_d6_pm <= 1
 zhang_rest_d6: + zhang_d6_pm + zhang_d7_am <= 1
 zhang_one_d7: + zhang_d7_am + zhang_d7_pm <= 1
 zhang_streak_d1: + zhang_d1_am + zhang_d1_pm + zhang_d2_am + zhang_d2_pm + zhang_d3_am + zhang_d3_pm
   + zhang_d4_am + zhang_d4_pm <= 3
 zhang_streak_d2: + zhang_d2_am + zhang_d2_pm + zhang_d3_am + zhang_d3_pm + zhang_d4_am + zhang_d4_pm
   + zhang_d5_am + zhang_d5_pm <= 3
 zhang_streak_d3: + zhang_d3_am + zhang_d3_pm + zhang_d4_am + zhang_d4_pm + zhang_d5_am + zhang_d5_pm
   + zhang_d6_am + zhang_d6_pm <= 3
 zhang_streak_d4: + zhang_d4_am + zhang_d4_pm + zhang_d5_am + zhang_d5_pm + zhang_d6_am + zhang_d6_pm
   + zhang_d7_am + zhang_d7_pm <= 3
 zhang_mindays: + zhang_d1_am + zhang_d1_pm + zhang_d2_am + zhang_d2_pm + zhang_d3_am + zhang_d3_pm
   + zhang_d4_am + zhang_d4_pm + zhang_d5_am + zhang_d5_pm + zhang_d6_am + zhang_d6_pm
   + zhang_d7_am + zhang_d7_pm >= 4
 zhang_maxdays: + zhang_d1_am + zhang_d1_pm + zhang_d2_am + zhang_d2_pm + zhang_d3_am + zhang_d3_pm
   + zhang_d4_am + zhang_d4_pm + zhang_d5_am + zhang_d5_pm + zhang_d6_am + zhang_d6_pm
   + zhang_d7_am + zhang_d7_pm <= 5
 zhang_weekend: + zhang_d6_am + zhang_d6_pm + zhang_d7_am + zhang_d7_pm <= 1
 chen_one_d1: + chen_d1_am + chen_d1_pm <= 1
 chen_rest_d1: + chen_d1_pm + chen_d2_am <= 1
 chen_one_d2: + chen_d2_am + chen_d2_pm <= 1
 chen_rest_d2: + chen_d2_pm + chen_d3_am <= 1
 chen_one_d3: + chen_d3_am + chen_d3_pm <= 1
 chen_rest_d3: + chen_d3_pm + chen_d4_am <= 1
 chen_one_d4: + chen_d4_am + chen_d4_pm <= 1
 chen_rest_d4: + chen_d4_pm + chen_d5_am <= 1
 chen_one_d5: + chen_d5_am + chen_d5_pm <= 1
 chen_rest_d5: + chen_d5_pm + chen_d6_am <= 1
 chen_one_d6: + chen_d6_am + chen_d6_pm <= 1
 chen_rest_d6: + chen_d6_pm + chen_d7_am <= 1
 chen_one_d7: + chen_d7_am + chen_d7_pm <= 1
 chen_streak_d1: + chen_d1_am + chen_d1_pm + chen_d2_am + chen_d2_pm + chen_d3_am + chen_d3_pm
   + chen_d4_am + chen_d4_pm <= 3
 chen_streak_d2: + chen_d2_am + chen_d2_pm + chen_d3_am + chen_d3_pm + chen_d4_am + chen_d4_pm
   + chen_d5_am + chen_d5_pm <= 3
 chen_streak_d3: + chen_d3_am + chen_d3_pm + chen_d4_am + chen_d4_pm + chen_d5_am + chen_d5_pm
   + chen_d6_am + chen_d6_pm <= 3
 chen_streak_d4: + chen_d4_am + chen_d4_pm + chen_d5_am + chen_d5_pm + chen_d6_am + chen_d6_pm
   + chen_d7_am + chen_d7_pm <= 3
 chen_mindays: + chen_d1_am + chen_d1_pm + chen_d2_am + chen_d2_pm + chen_d3_am + chen_d3_pm
   + chen_d4_am + chen_d4_pm + chen_d5_am + chen_d5_pm + chen_d6_am + chen_d6_pm
   + chen_d7_am + chen_d7_pm >= 4
 chen_maxdays: + chen_d1_am + chen_d1_pm + chen_d2_am + chen_d2_pm + chen_d3_am + chen_d3_pm
   + chen_d4_am + chen_d4_pm + chen_d5_am + chen_d5_pm + chen_d6_am + chen_d6_pm
   + chen_d7_am + chen_d7_pm <= 5
 chen_weekend: + chen_d6_am + chen_d6_pm + chen_d7_am + chen_d7_pm <= 1
 liu_one_d1: + liu_d1_am + liu_d1_pm <= 1
 liu_rest_d1: + liu_d1_pm + liu_d2_am <= 1
 liu_one_d2: + liu_d2_am + liu_d2_pm <= 1
 liu_rest_d2: + liu_d2_pm + liu_d3_am <= 1
 liu_one_d3: + liu_d3_am + liu_d3_pm <= 1
 liu_rest_d3: + liu_d3_pm + liu_d4_am <= 1
 liu_one_d4: + liu_d4_am + liu_d4_pm <= 1
 liu_rest_d4: + liu_d4_pm + liu_d5_am <= 1
 liu_one_d5: + liu_d5_am + liu_d5_pm <= 1
 liu_rest_d5: + liu_d5_pm + liu_d6_am <= 1
 liu_one_d6: + liu_d6_am + liu_d6_pm <= 1
 liu_rest_d6: + liu_d6_pm + liu_d7_am <= 1
 liu_one_d7: + liu_d7_am + liu_d7_pm <= 1
 liu_streak_d1: + liu_d1_am + liu_d1_pm + liu_d2_am + liu_d2_pm + liu_d3_am + liu_d3_pm
   + liu_d4_am + liu_d4_pm <= 3
 liu_streak_d2: + liu_d2_am + liu_d2_pm + liu_d3_am + liu_d3_pm + liu_d4_am + liu_d4_pm
   + liu_d5_am + liu_d5_pm <= 3
 liu_streak_d3: + liu_d3_am + liu_d3_pm + liu_d4_am + liu_d4_pm + liu_d5_am + liu_d5_pm
   + liu_d6_am + liu_d6_pm <= 3
 liu_streak_d4: + liu_d4_am + liu_d4_pm + liu_d5_am + liu_d5_pm + liu_d6_am + liu_d6_pm
   + liu_d7_am + liu_d7_pm <= 3
 liu_mindays: + liu_d1_am + liu_d1_pm + liu_d2_am + liu_d2_pm + liu_d3_am + liu_d3_pm
   + liu_d4_am + liu_d4_pm + liu_d5_am + liu_d5_pm + liu_d6_am + liu_d6_pm
   + liu_d7_am + liu_d7_pm >= 2
 liu_maxdays: + liu_d1_am + liu_d1_pm + liu_d2_am + liu_d2_pm + liu_d3_am + liu_d3_pm
   + liu_d4_am + liu_d4_pm + liu_d5_am + liu_d5_pm + liu_d6_am + liu_d6_pm
   + liu_d7_am + liu_d7_pm <= 4
 zhao_one_d1: + zhao_d1_am + zhao_d1_pm <= 1
 zhao_rest_d1: + zhao_d1_pm + zhao_d2_am <= 1
 zhao_one_d2: + zhao_d2_am + zhao_d2_pm <= 1
 zhao_rest_d2: + zhao_d2_pm + zhao_d3_am <= 1
 zhao_one_d3: + zhao_d3_am + zhao_d3_pm <= 1
 zhao_rest_d3: + zhao_d3_pm + zhao_d4_am <= 1
 zhao_one_d4: + zhao_d4_am + zhao_d4_pm <= 1
 zhao_rest_d4: + zhao_d4_pm + zhao_d5_am <= 1
 zhao_one_d5: + zhao_d5_am + zhao_d5_pm <= 1
 zhao_rest_d5: + zhao_d5_pm + zhao_d6_am <= 1
 zhao_one_d6: + zhao_d6_am + zhao_d6_pm <= 1
 zhao_rest_d6: + zhao_d6_pm + zhao_d7_am <= 1
 zhao_one_d7: + zhao_d7_am + zhao_d7_pm <= 1
 zhao_streak_d1: + zhao_d1_am + zhao_d1_pm + zhao_d2_am + zhao_d2_pm + zhao_d3_am + zhao_d3_pm
   + zhao_d4_am + zhao_d4_pm <= 3
 zhao_streak_d2: + zhao_d2_am + zhao_d2_pm + zhao_d3_am + zhao_d3_pm + zhao_d4_am + zhao_d4_pm
   + zhao_d5_am + zhao_d5_pm <= 3
 zhao_streak_d3: + zhao_d3_am + zhao_d3_pm + zhao_d4_am + zhao_d4_pm + zhao_d5_am + zhao_d5_pm
   + zhao_d6_am + zhao_d6_pm <= 3
 zhao_streak_d4: + zhao_d4_am + zhao_d4_pm + zhao_d5_am + zhao_d5_pm + zhao_d6_am + zhao_d6_pm
   + zhao_d7_am + zhao_d7_pm <= 3
 zhao_mindays: + zhao_d1_am + zhao_d1_pm + zhao_d2_am + zhao_d2_pm + zhao_d3_am + zhao_d3_pm
   + zhao_d4_am + zhao_d4_pm + zhao_d5_am + zhao_d5_pm + zhao_d6_am + zhao_d6_pm
   + zhao_d7_am + zhao_d7_pm >= 2
 zhao_maxdays: + zhao_d1_am + zhao_d1_pm + zhao_d2_am + zhao_d2_pm + zhao_d3_am + zhao_d3_pm
   + zhao_d4_am + zhao_d4_pm + zhao_d5_am + zhao_d5_pm + zhao_d6_am + zhao_d6_pm
   + zhao_d7_am + zhao_d7_pm <= 4
 zhou_one_d1: + zhou_d1_am + zhou_d1_pm <= 1
 zhou_rest_d1: + zhou_d1_pm + zhou_d2_am <= 1
 zhou_one_d2: + zhou_d2_am + zhou_d2_pm <= 1
 zhou_rest_d2: + zhou_d2_pm + zhou_d3_am <= 1
 zhou_one_d3: + zhou_d3_am + zhou_d3_pm <= 1
 zhou_rest_d3: + zhou_d3_pm + zhou_d4_am <= 1
 zhou_one_d4: + zhou_d4_am + zhou_d4_pm <= 1
 zhou_rest_d4: + zhou_d4_pm + zhou_d5_am <= 1
 zhou_one_d5: + zhou_d5_am + zhou_d5_pm <= 1
 zhou_rest_d5: + zhou_d5_pm + zhou_d6_am <= 1
 zhou_one_d6: + zhou_d6_am + zhou_d6_pm <= 1
 zhou_rest_d6: + zhou_d6_pm + zhou_d7_am <= 1
 zhou_one_d7: + zhou_d7_am + zhou_d7_pm <= 1
 zhou_streak_d1: + zhou_d1_am + zhou_d1_pm + zhou_d2_am + zhou_d2_pm + zhou_d3_am + zhou_d3_pm
   + zhou_d4_am + zhou_d4_pm <= 3
 zhou_streak_d2: + zhou_d2_am + zhou_d2_pm + zhou_d3_am + zhou_d3_pm + zhou_d4_am + zhou_d4_pm
   + zhou_d5_am + zhou_d5_pm <= 3
 zhou_streak_d3: + zhou_d3_am + zhou_d3_pm + zhou_d4_am + zhou_d4_pm + zhou_d5_am + zhou_d5_pm
   + zhou_d6_am + zhou_d6_pm <= 3
 zhou_streak_d4: + zhou_d4_am + zhou_d4_pm + zhou_d5_am + zhou_d5_pm + zhou_d6_am + zhou_d6_pm
   + zhou_d7_am + zhou_d7_pm <= 3
 zhou_mindays: + zhou_d1_am + zhou_d1_pm + zhou_d2_am + zhou_d2_pm + zhou_d3_am + zhou_d3_pm
   + zhou_d4_am + zhou_d4_pm + zhou_d5_am + zhou_d5_pm + zhou_d6_am + zhou_d6_pm
   + zhou_d7_am + zhou_d7_pm >= 2
 zhou_maxdays: + zhou_d1_am + zhou_d1_pm + zhou_d2_am + zhou_d2_pm + zhou_d3_am + zhou_d3_pm
   + zhou_d4_am + zhou_d4_pm + zhou_d5_am + zhou_d5_pm + zhou_d6_am + zhou_d6_pm
   + zhou_d7_am + zhou_d7_pm <= 4
 sun_one_d1: + sun_d1_am + sun_d1_pm <= 1
 sun_rest_d1: + sun_d1_pm + sun_d2_am <= 1
 sun_one_d2: + sun_d2_am + sun_d2_pm <= 1
 sun_rest_d2: + sun_d2_pm + sun_d3_am <= 1
 sun_one_d3: + sun_d3_am + sun_d3_pm <= 1
 sun_rest_d3: + sun_d3_pm + sun_d4_am <= 1
 sun_one_d4: + sun_d4_am + sun_d4_pm <= 1
 sun_rest_d4: + sun_d4_pm + sun_d5_am <= 1
 sun_one_d5: + sun_d5_am + sun_d5_pm <= 1
 sun_rest_d5: + sun_d5_pm + sun_d6_am <= 1
 sun_one_d6: + sun_d6_am + sun_d6_pm <= 1
 sun_rest_d6: + sun_d6_pm + sun_d7_am <= 1
 sun_one_d7: + sun_d7_am + sun_d7_pm <= 1
 sun_streak_d1: + sun_d1_am + sun_d1_pm + sun_d2_am + sun_d2_pm + sun_d3_am + sun_d3_pm
   + sun_d4_am + sun_d4_pm <= 3
 sun_streak_d2: + sun_d2_am + sun_d2_pm + sun_d3_am + sun_d3_pm + sun_d4_am + sun_d4_pm
   + sun_d5_am + sun_d5_pm <= 3
 sun_streak_d3: + sun_d3_am + sun_d3_pm + sun_d4_am + sun_d4_pm + sun_d5_am + sun_d5_pm
   + sun_d6_am + sun_d6_pm <= 3
 sun_streak_d4: + sun_d4_am + sun_d4_pm + sun_d5_am + sun_d5_pm + sun_d6_am + sun_d6_pm
   + sun_d7_am + sun_d7_pm <= 3
 sun_mindays: + sun_d1_am + sun_d1_pm + sun_d2_am + sun_d2_pm + sun_d3_am + sun_d3_pm
   + sun_d4_am + sun_d4_pm + sun_d5_am + sun_d5_pm + sun_d6_am + sun_d6_pm
   + sun_d7_am + sun_d7_pm >= 2
 sun_maxdays: + sun_d1_am + sun_d1_pm + sun_d2_am + sun_d2_pm + sun_d3_am + sun_d3_pm
   + sun_d4_am + sun_d4_pm + sun_d5_am + sun_d5_pm + sun_d6_am + sun_d6_pm
   + sun_d7_am + sun_d7_pm <= 4
 liu_mentor_d1_am: - li_d1_am - chen_d1_am + liu_d1_am <= -0
 liu_mentor_d1_pm: - li_d1_pm - chen_d1_pm + liu_d1_pm <= -0
 liu_mentor_d2_am: - li_d2_am - chen_d2_am + liu_d2_am <= -0
 liu_mentor_d2_pm: - li_d2_pm - chen_d2_pm + liu_d2_pm <= -0
 liu_mentor_d3_am: - li_d3_am - chen_d3_am + liu_d3_am <= -0
 liu_mentor_d3_pm: - li_d3_pm - chen_d3_pm + liu_d3_pm <= -0
 liu_mentor_d4_am: - li_d4_am - chen_d4_am + liu_d4_am <= -0
 liu_mentor_d4_pm: - li_d4_pm - chen_d4_pm + liu_d4_pm <= -0
 liu_mentor_d5_am: - li_d5_am - chen_d5_am + liu_d5_am <= -0
 liu_mentor_d5_pm: - li_d5_pm - chen_d5_pm + liu_d5_pm <= -0
 liu_mentor_d6_am: - li_d6_am - chen_d6_am + liu_d6_am <= -0
 liu_mentor_d6_pm: - li_d6_pm - chen_d6_pm + liu_d6_pm <= -0
 liu_mentor_d7_am: - li_d7_am - chen_d7_am + liu_d7_am <= -0
 liu_mentor_d7_pm: - li_d7_pm - chen_d7_pm + liu_d7_pm <= -0
 sun_mentor_d1_am: - li_d1_am - chen_d1_am + sun_d1_am <= -0
 sun_mentor_d1_pm: - li_d1_pm - chen_d1_pm + sun_d1_pm <= -0
 sun_mentor_d2_am: - li_d2_am - chen_d2_am + sun_d2_am <= -0
 sun_mentor_d2_pm: - li_d2_pm - chen_d2_pm + sun_d2_pm <= -0
 sun_mentor_d3_am: - li_d3_am - chen_d3_am + sun_d3_am <= -0
 sun_mentor_d3_pm: - li_d3_pm - chen_d3_pm + sun_d3_pm <= -0
 sun_mentor_d4_am: - li_d4_am - chen_d4_am + sun_d4_am <= -0
 sun_mentor_d4_pm: - li_d4_pm - chen_d4_pm + sun_d4_pm <= -0
 sun_mentor_d5_am: - li_d5_am - chen_d5_am + sun_d5_am <= -0
 sun_mentor_d5_pm: - li_d5_pm - chen_d5_pm + sun_d5_pm <= -0
 sun_mentor_d6_am: - li_d6_am - chen_d6_am + sun_d6_am <= -0
 sun_mentor_d6_pm: - li_d6_pm - chen_d6_pm + sun_d6_pm <= -0
 sun_mentor_d7_am: - li_d7_am - chen_d7_am + sun_d7_am <= -0
 sun_mentor_d7_pm: - li_d7_pm - chen_d7_pm + sun_d7_pm <= -0
 apart_d1_am: + wang_d1_am + zhang_d1_am <= 1
 apart_d1_pm: + wang_d1_pm + zhang_d1_pm <= 1
 apart_d2_am: + wang_d2_am + zhang_d2_am <= 1
 apart_d2_pm: + wang_d2_pm + zhang_d2_pm <= 1
 apart_d3_am: + wang_d3_am + zhang_d3_am <= 1
 apart_d3_pm: + wang_d3_pm + zhang_d3_pm <= 1
 apart_d4_am: + wang_d4_am + zhang_d4_am <= 1
 apart_d4_pm: + wang_d4_pm + zhang_d4_pm <= 1
 apart_d5_am: + wang_d5_am + zhang_d5_am <= 1
 apart_d5_pm: + wang_d5_pm + zhang_d5_pm <= 1
 apart_d6_am: + wang_d6_am + zhang_d6_am <= 1
 apart_d6_pm: + wang_d6_pm + zhang_d6_pm <= 1
 apart_d7_am: + wang_d7_am + zhang_d7_am <= 1
 apart_d7_pm: + wang_d7_pm + zhang_d7_pm <= 1
Bounds
 zhang_d3_am = 0
 zhang_d3_pm = 0
 liu_d1_am = 0
 liu_d1_pm = 0
 liu_d2_am = 0
 liu_d2_pm = 0
 liu_d3_am = 0
 liu_d3_pm = 0
 liu_d4_am = 0
 liu_d4_pm = 0
 zhao_d1_am = 0
 zhao_d2_am = 0
 zhao_d3_am = 0
 zhao_d4_am = 0
 zhao_d5_am = 0
 zhao_d6_am = 0
 zhao_d7_am = 0
 zhou_d3_am = 0
 zhou_d3_pm = 0
 zhou_d4_am = 0
 zhou_d4_pm = 0
 sun_d1_am = 0
 sun_d1_pm = 0
General
 zhang_d3_am
 zhang_d3_pm
 liu_d1_am
 liu_d1_pm
 liu_d2_am
 liu_d2_pm
 liu_d3_am
 liu_d3_pm
 liu_d4_am
 liu_d4_pm
 zhao_d1_am
 zhao_d2_am
 zhao_d3_am
 zhao_d4_am
 zhao_d5_am
 zhao_d6_am
 zhao_d7_am
 zhou_d3_am
 zhou_d3_pm
 zhou_d4_am
 zhou_d4_pm
 sun_d1_am
 sun_d1_pm
Binary
 wang_d1_am
 wang_d1_pm
 wang_d2_am
 wang_d2_pm
 wang_d3_am
 wang_d3_pm
 wang_d4_am
 wang_d4_pm
 wang_d5_am
 wang_d5_pm
 wang_d6_am
 wang_d6_pm
 wang_d7_am
 wang_d7_pm
 li_d1_am
 li_d1_pm
 li_d2_am
 li_d2_pm
 li_d3_am
 li_d3_pm
 li_d4_am
 li_d4_pm
 li_d5_am
 li_d5_pm
 li_d6_am
 li_d6_pm
 li_d7_am
 li_d7_pm
 zhang_d1_am
 zhang_d1_pm
 zhang_d2_am
 zhang_d2_pm
 zhang_d4_am
 zhang_d4_pm
 zhang_d5_am
 zhang_d5_pm
 zhang_d6_am
 zhang_d6_pm
 zhang_d7_am
 zhang_d7_pm
 chen_d1_am
 chen_d1_pm
 chen_d2_am
 chen_d2_pm
 chen_d3_am
 chen_d3_pm
 chen_d4_am
 chen_d4_pm
 chen_d5_am
 chen_d5_pm
 chen_d6_am
 chen_d6_pm
 chen_d7_am
 chen_d7_pm
 liu_d5_am
 liu_d5_pm
 liu_d6_am
 liu_d6_pm
 liu_d7_am
 liu_d7_pm
 zhao_d1_pm
 zhao_d2_pm
 zhao_d3_pm
 zhao_d4_pm
 zhao_d5_pm
 zhao_d6_pm
 zhao_d7_pm
 zhou_d1_am
 zhou_d1_pm
 zhou_d2_am
 zhou_d2_pm
 zhou_d5_am
 zhou_d5_pm
 zhou_d6_am
 zhou_d6_pm
 zhou_d7_am
 zhou_d7_pm
 sun_d2_am
 sun_d2_pm
 sun_d3_am
 sun_d3_pm
 sun_d4_am
 sun_d4_pm
 sun_d5_am
 sun_d5_pm
 sun_d6_am
 sun_d6_pm
 sun_d7_am
 sun_d7_pm
End
