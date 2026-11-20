#!/usr/bin/env bash
# 逐个运行 C++ 和 Python 的例子，比较输出（忽略用时）。两边应当一字不差。
#   tools/compare_examples_py_cpp.sh build
set -uo pipefail
CPP_BUILD=$(realpath "${1:-build}")
PYEX=$(realpath "$(dirname "$0")/../python/examples")
WORK=$(mktemp -d)
mkdir -p "$WORK/cpp" "$WORK/py"
names="basics_01_one_variable basics_02_two_variables basics_03_must_be_whole basics_04_yes_or_no basics_05_minimize
basics_06_shadow_price basics_07_fixed_cost basics_08_min_max basics_09_absolute_value basics_10_infeasible
easy1_bakery easy2_projects api_demo hard_production_plan hard_staff_schedule"
mask() { sed -E 's/[0-9]+\.[0-9]+ ?(s|秒)//g; s/ +[0-9.]+s$//' "$1"; }
total=0; same=0
for c in $names; do
    total=$((total + 1))
    (cd "$WORK/cpp" && "$CPP_BUILD/$c" > "$c.out" 2>&1)
    (cd "$WORK/py" && python3 "$PYEX/$c.py" > "$c.out" 2>&1)
    if diff <(mask "$WORK/cpp/$c.out") <(mask "$WORK/py/$c.out") > "$WORK/$c.diff"; then
        same=$((same + 1)); echo "一致    $c"
    else
        echo "不一致  $c"; head -20 "$WORK/$c.diff"
    fi
done
# 写出的 .lp 文件也要一样
for f in hard_production_plan.lp hard_staff_schedule.lp; do
    total=$((total + 1))
    if cmp -s "$WORK/cpp/$f" "$WORK/py/$f"; then same=$((same + 1)); echo "一致    $f"; else echo "不一致  $f"; fi
done
echo "$same/$total 一致"
[[ $same == "$total" ]]
