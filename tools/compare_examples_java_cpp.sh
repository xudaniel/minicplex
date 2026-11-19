#!/usr/bin/env bash
# 逐个运行 C++ 和 Java 的例子，比较输出（忽略用时）。两边应当一字不差。
#   tools/compare_examples_java_cpp.sh build java/build/minicplex.jar
set -uo pipefail
CPP_BUILD=$(realpath "${1:-build}")
JAR=$(realpath "${2:-java/build/minicplex.jar}")
WORK=$(mktemp -d)
mkdir -p "$WORK/cpp" "$WORK/java"
pairs="basics_01_one_variable:Basics01OneVariable basics_02_two_variables:Basics02TwoVariables
basics_03_must_be_whole:Basics03MustBeWhole basics_04_yes_or_no:Basics04YesOrNo basics_05_minimize:Basics05Minimize
basics_06_shadow_price:Basics06ShadowPrice basics_07_fixed_cost:Basics07FixedCost basics_08_min_max:Basics08MinMax
basics_09_absolute_value:Basics09AbsoluteValue basics_10_infeasible:Basics10Infeasible easy1_bakery:Easy1Bakery
easy2_projects:Easy2Projects api_demo:ApiDemo hard_production_plan:HardProductionPlan hard_staff_schedule:HardStaffSchedule"
mask() { grep -v '^Picked up' "$1" | sed -E 's/[0-9]+\.[0-9]+ ?(s|秒)//g; s/ +[0-9.]+s$//'; }
total=0; same=0
for p in $pairs; do
    c=${p%%:*}; j=${p##*:}; total=$((total + 1))
    (cd "$WORK/cpp" && "$CPP_BUILD/$c" > "$c.out" 2>&1)
    (cd "$WORK/java" && java -cp "$JAR" "minicplex.examples.$j" > "$c.out" 2>&1)
    if diff <(mask "$WORK/cpp/$c.out") <(mask "$WORK/java/$c.out") > "$WORK/$c.diff"; then
        same=$((same + 1)); echo "一致    $c"
    else
        echo "不一致  $c"; head -20 "$WORK/$c.diff"
    fi
done
# 写出的 .lp 文件也要一样
for f in hard_production_plan.lp hard_staff_schedule.lp; do
    total=$((total + 1))
    if cmp -s "$WORK/cpp/$f" "$WORK/java/$f"; then same=$((same + 1)); echo "一致    $f"; else echo "不一致  $f"; fi
done
echo "$same/$total 一致"
[[ $same == "$total" ]]
