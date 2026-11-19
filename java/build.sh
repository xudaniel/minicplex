#!/usr/bin/env bash
# 不需要 Maven、不需要联网：只用 JDK 自带的 javac / jar 构建 minicplex 的 Java 版。
#
#   ./build.sh            编译 + 打包 build/minicplex.jar + 跑测试
#   ./build.sh --no-test  只编译打包
#
# 产物：
#   build/minicplex.jar   求解器 + 命令行（java -jar build/minicplex.jar model.lp）+ 工具 + 例子
set -euo pipefail
cd "$(dirname "$0")"

rm -rf build
mkdir -p build/classes build/test-classes

echo "== 编译求解器、命令行和工具"
javac --release 17 -Xlint:all -Werror -encoding UTF-8 -d build/classes $(find src/main/java -name '*.java')

echo "== 编译例子"
javac --release 17 -Xlint:all -Werror -encoding UTF-8 -cp build/classes -d build/classes examples/minicplex/examples/*.java

echo "== 打包 build/minicplex.jar"
jar --create --file build/minicplex.jar --main-class minicplex.Main -C build/classes .

if [[ "${1:-}" != "--no-test" ]]; then
    echo "== 编译并运行测试"
    javac --release 17 -Xlint:all -Werror -encoding UTF-8 -cp build/classes -d build/test-classes \
        $(find src/test/java -name '*.java')
    java -cp build/classes:build/test-classes minicplex.SolverTest
fi
echo "== 完成：build/minicplex.jar"
