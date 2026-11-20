# 参与贡献

谢谢你愿意改进 minicplex！这是一个以**学习**为目的的项目，所以“好读”和“算得对”比“更快”更重要。

## 提 issue

- **算错了 / 崩溃了**：请附上能复现的 `.lp` 文件和完整命令，最好再附上 HiGHS 或其他求解器的结果
  （`python3 tools/verify_with_highs.py model.lp`）。
- **看不懂某段代码**：也欢迎提问。看不懂通常说明注释或 README 的代码解析写得不够清楚。

## 提 pull request

1. C++ 版改完先跑：
   ```bash
   cmake -S . -B build && cmake --build build -j && ctest --test-dir build
   ```
2. 求解逻辑有改动时，**Java 版和 Python 版都要同步改**，并确认三边仍然逐步一致：
   ```bash
   java/build.sh
   tools/compare_examples_java_cpp.sh build java/build/minicplex.jar
   ./build/minicplex_bench bench/models --quiet --csv cpp.csv
   java -cp java/build/minicplex.jar minicplex.tools.Bench bench/models --quiet --csv java.csv
   python3 tools/compare_java_cpp.py cpp.csv java.csv --strict

   python3 -m unittest discover -s python/tests
   tools/compare_examples_py_cpp.sh build
   (cd python && python3 -m minicplex.bench ../bench/models --quiet --csv ../py.csv)
   python3 tools/compare_java_cpp.py cpp.csv py.csv --strict --label Python
   ```
   改了公开 API 时，记得同步两门课的参考答案（`java/tutorial/run.sh all --solution`、`python3 python/tutorial/run.py all --solution`，Python 课的英文版是 `python3 python/tutorial/en/run.py all --solution`）。改 Python 课的答案时，中英文两份一起改，再分别运行 `make_exercises.py` 和 `make_exercises.py --lang en`。
3. 改动求解逻辑时，跑一轮对拍：
   ```bash
   ./build/minicplex_gen --kind mixed --count 400 --seed 1 --out fuzz
   ./build/minicplex_bench fuzz --gap 1e-9 --nodes 200000 --quiet --csv fuzz/ours.csv
   python3 tools/fuzz_vs_highs.py fuzz fuzz/ours.csv
   ```
4. 新功能请附测试；行为变化请写进 `CHANGELOG.md` 的“未发布”一节。

## 代码风格

- C++17，不引入第三方依赖；Java 17、Python 3.9+，同样零依赖（Python 只用标准库）。
- 代码注释用英文，文档和例子注释用中文。
- 宁可多写一行注释解释“为什么”，也不要写聪明但难懂的代码。
