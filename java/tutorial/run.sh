#!/usr/bin/env bash
# 运行教程练习。
#
#   java/tutorial/run.sh A01             运行入门第 A1 课的练习（零基础，A01～A08）
#   java/tutorial/run.sh 03              运行第 3 课的练习（你写的代码）
#   java/tutorial/run.sh 03 --solution   运行第 3 课的参考答案
#   java/tutorial/run.sh all --solution  运行全部参考答案（CI 用：必须全部通过）
#   java/tutorial/run.sh all             看看你一共完成了多少
set -uo pipefail
cd "$(dirname "$0")"
LESSON="${1:-}"
DIR=exercises
[[ "${2:-}" == "--solution" ]] && DIR=solutions
if [[ -z "$LESSON" ]]; then sed -n '2,9p' "$0"; exit 2; fi

JAR=../build/minicplex.jar
if [[ ! -f "$JAR" ]]; then ../build.sh --no-test > /dev/null || exit 1; fi

OUT=build/$DIR
rm -rf "$OUT" && mkdir -p "$OUT"
javac -encoding UTF-8 --release 17 -Xlint:all -cp "$JAR" -d "$OUT" $DIR/minicplex/tutorial/*.java || exit 1

if [[ "$LESSON" == "all" ]]; then
    failed=0
    for f in $DIR/minicplex/tutorial/A*.java $DIR/minicplex/tutorial/L*.java; do
        cls=$(basename "$f" .java)
        java -cp "$JAR:$OUT" "minicplex.tutorial.$cls"
        code=$?
        if [[ $code -eq 1 || ( $code -ne 0 && "$DIR" == "solutions" ) ]]; then failed=1; fi
        echo
    done
    exit $failed
fi

case "$LESSON" in
    [Aa]*) f=$(ls $DIR/minicplex/tutorial/A$(printf '%02d' "$((10#${LESSON:1}))")*.java 2>/dev/null | head -1) ;;
    *) f=$(ls $DIR/minicplex/tutorial/L$(printf '%02d' "$((10#$LESSON))")*.java 2>/dev/null | head -1) ;;
esac
if [[ -z "$f" ]]; then echo "找不到第 $LESSON 课（例如 A01、A1、03 或 3）"; exit 2; fi
java -cp "$JAR:$OUT" "minicplex.tutorial.$(basename "$f" .java)"
